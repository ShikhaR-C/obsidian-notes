# 05 — CI/CD Pipeline with GitHub Actions

> Originally deferred in the learning docs (`docs/learning/system-design/08-cicd-deployment.md` covers the strategy; this file is the execution plan).
> Target: both `dzzlo_oms_api` and `dzzlo_oms_app` have GitHub Actions workflows for test, lint, type-check, build, and deploy — replacing the current "SSH in and `git pull`" process.

---

## TL;DR

Today: the API is deployed by SSH-ing into the EC2 instance, running `git pull && pm2 restart dzzlo-oms`. The app is built manually via `build-release-apk.sh` and uploaded to Google Play by hand. No automated tests run before deploy. Only one person knows the full process. Bus factor = 1. A single typo in a route file can take the whole system down with no safety net.

Target: every push to `master` on either repo triggers a GitHub Actions workflow that runs Jest, ESLint, type-check, and (on pass) deploys automatically. The API uses SSH + PM2 graceful reload. The app uploads an Android AAB to the Google Play internal track and an iOS archive to TestFlight. Secrets live in GitHub Actions secrets, not in `.env` files on servers.

Net effect: ship with confidence, bus factor > 1, tests gate deployment, artifacts are traceable to a commit SHA.

---

## 1. Current State (from code research)

### 1.1 Repository layout

- **Separate git repos:** `dzzlo_oms_api/.git` and `dzzlo_oms_app/.git` are siblings. Parent is not a git repo. **Each needs its own set of workflows** (there's no monorepo option).
- Neither repo has a `.github/workflows/` directory today.
- No Dockerfile, no other CI config, no Fastlane.

### 1.2 API project state

| Concern         | Details                                                                                                     |
| --------------- | ----------------------------------------------------------------------------------------------------------- |
| Node version    | Not explicitly pinned in `package.json` `engines`. The app project requires `>= 22.11.0`; API should match. |
| Package manager | `yarn.lock` present → yarn 1.x (Classic)                                                                    |
| Test runner     | Jest 30.3.0                                                                                                 |
| Test count      | 239 `.js` test files in `test/` (api_v3 active, others ignored per `jest.config.js`)                        |
| Test DB         | `mongodb-memory-server@11.0.1` in devDependencies — no external DB needed in CI                             |
| Lint            | **None configured.** Add ESLint as part of this initiative.                                                 |
| TypeScript      | None. Pure JS.                                                                                              |
| Deploy target   | EC2 instance(s), PM2 (`ecosystem.config.js`), behind ALB                                                    |
| Env file        | `.env.production` manually placed on each instance (not in AMI)                                             |
| Secrets         | 28 required env vars (MongoDB, JWT, SES, Paytm, OneSignal, 2Factor SMS, etc.)                               |
| Health endpoint | `/health` (exists via `tasks_01/RES-1`)                                                                     |
| Rollback        | None — manual `git reset --hard` under pressure                                                             |

### 1.3 App project state

| Concern          | Details                                                                                  |
| ---------------- | ---------------------------------------------------------------------------------------- |
| Node version     | `engines.node: ">= 22.11.0"`                                                             |
| Package manager  | yarn                                                                                     |
| React Native     | 0.84.1 (new arch enabled: Hermes + TurboModules + Fabric)                                |
| Test runner      | Jest + `react-native` preset, 238 test files                                             |
| Lint             | ESLint 9.0.0 + `@react-native/eslint-config`, `yarn lint`                                |
| Type-check       | TypeScript 6.0.2, `tsconfig.json` extends `@react-native/typescript-config`              |
| Android keystore | `dzzlooms-upload-key.keystore`, creds in `gradle.properties` (passwords masked in git)   |
| Android package  | `in.vsyst.dzzlooms`                                                                      |
| Android version  | versionCode 100, versionName "1.76"                                                      |
| iOS pods         | CocoaPods, OneSignal extension, no Fastlane                                              |
| CodePush         | Keys in env files, RN code commented out. Not wired.                                     |
| Firebase         | config files present (`google-services.json`, `GoogleService-Info.plist`), code disabled |
| Build scripts    | `build-release-apk.sh`, `build-install-apk.sh` — Gradle-based                            |

### 1.4 Documentation that already exists

- `docs/learning/system-design/08-cicd-deployment.md` — strategy doc, discusses three options (deploy.sh, GitHub Actions + SSH, CodeDeploy + ASG). **Option B (GitHub Actions + SSH) is what this initiative implements.**
- `docs/oms_app/FIREBASE_INTEGRATION_PLAN.md` — Firebase re-integration plan (not blocking for CI/CD).

---

## 2. Problem Statement

1. **Bus factor = 1.** Only the project owner knows the SSH keys, the `.env.production` contents, the exact steps to roll out a change. A single person unavailable = nothing can ship.
2. **No tests before deploy.** `pm2 restart` will happily start a broken build. Errors surface as user-facing 500s, not as a red X in a PR checker.
3. **Secrets on the server filesystem.** `.env.production` lives on disk in plaintext. AMI snapshots include it. Any breach of the EC2 instance = full credentials exfiltration.
4. **No audit trail.** "When did this code get deployed?" has to be answered by SSH-ing in and checking `git log`. Commit → running code traceability is manual.
5. **App builds are brittle.** `build-release-apk.sh` depends on a locally configured keystore, Node 22, correct JDK, pods installed. A new laptop takes a day to get building.
6. **No rollback.** If a bad commit goes to production, `git reset --hard HEAD~1 && pm2 restart` under pressure is the procedure. No tested rollback path.
7. **App store releases are tedious.** Upload AAB to Play Console, fill in release notes, promote to production, wait for review. Half an hour minimum per release. Trivial to forget a step.

---

## 3. Research & Technical Deep-Dive

### 3.1 Why GitHub Actions specifically

- The repos live on GitHub (inferred from the `github.com/anthropics` / `.git` structure; confirm before starting).
- GitHub Actions is free for public repos and generous for private (2000 minutes/month on Free, more on Team). At DZZLO's deploy frequency, Free or Team tier is more than enough.
- Native integration with GitHub Secrets, environments, deployment protection rules.
- No new account/vendor required.
- Alternative: CircleCI, GitLab CI, Jenkins. Not chosen because they'd add a new SaaS or a new service to self-host with no corresponding benefit.

### 3.2 API deploy strategy: SSH + PM2 graceful reload

The API is deployed to one or more EC2 instances behind an ALB. The deploy flow should:

1. SSH into the instance.
2. Pull the latest commit to `/home/ubuntu/dzzlo_oms_api` (or wherever).
3. Run `yarn install --frozen-lockfile --production=false` (need dev deps for build steps if any).
4. Actually: since this is JS-only with no build step, just `yarn install --frozen-lockfile`.
5. `pm2 reload dzzlo-oms` — **reload** not `restart`. Reload keeps the old process alive until the new one is healthy (zero-downtime on clustered mode; a ~1s gap on single-process mode, which is acceptable).
6. Wait 5 seconds.
7. Curl `/health` on localhost → expect 200 with `status: ok`.
8. If health fails: automatic rollback — `git reset --hard HEAD~1 && yarn install && pm2 reload`.

**Zero-downtime consideration:** with single-process PM2 mode (current), `pm2 reload` briefly drops connections during restart. After `tasks_01/RES-3` (cluster mode) is done, `pm2 reload` is truly zero-downtime because PM2 restarts workers one at a time. **Recommendation: gate automatic deploys on RES-3 completion** OR accept the ~1s gap initially.

**Alternative considered: CodeDeploy + ASG.** AWS-native, blue-green deploys, easier rollback. Rejected because (a) it's a much bigger infrastructure change, (b) the SSH approach works at current scale, (c) CodeDeploy adds a new vendor lock-in.

### 3.3 SSH from GitHub Actions: security

Two common approaches:

1. **Direct SSH:** store an SSH private key in GitHub Secrets. Actions SSH-es in, runs commands. Requires the EC2 security group to allow GitHub Actions IP ranges (not great — IPs are huge) or allow SSH from 0.0.0.0/0 (bad).
2. **AWS Systems Manager Session Manager:** no open SSH port, uses IAM auth. Requires an AWS IAM role for the GitHub Actions runner (via OIDC federation, not static access keys). More setup, much better security.

**Choice for this phase:** option 1 (direct SSH) for speed, **but** use [Tailscale](https://tailscale.com/) or a [bastion](https://github.com/webfactory/ssh-agent) to avoid opening SSH to the world. Long-term, migrate to option 2.

For the SSH setup inside GitHub Actions:

- Use [`webfactory/ssh-agent@v0.9.0`](https://github.com/webfactory/ssh-agent) — loads a private key into the agent.
- Store `SSH_PRIVATE_KEY`, `SSH_HOST`, `SSH_USER` in GitHub Secrets.
- Scope: a "deploy" IAM / OS user on EC2 with only permissions to (a) pull the repo, (b) restart PM2. No sudo.

### 3.4 Environment files without storing them on disk

The API reads `.env.production` at startup. In CI/CD, we have two options:

1. **Generate `.env` from secrets at deploy time.** The GitHub Actions workflow writes `echo "KEY=VALUE" > .env` on the server during deploy. Slightly better than static `.env.production` but still leaves a file on disk.
2. **Export env vars into PM2 directly via `ecosystem.config.js`.** PM2 supports loading env vars from the process environment. CI writes a single `pm2.env` file that's sourced by `ecosystem.config.js`.
3. **AWS Parameter Store / Secrets Manager.** At startup, the API calls `ssm:GetParametersByPath` with an IAM role attached to the EC2 instance. Most secure; no secrets on disk.

**Recommendation:** option 1 for Phase 2 (immediate win), option 3 (Parameter Store) for Phase 7 as a follow-up.

### 3.5 App CI: what it should cover

For an RN app, the CI pipeline should do, in order:

1. `yarn install --frozen-lockfile`
2. `yarn lint` (ESLint)
3. `tsc --noEmit` (type-check without emitting)
4. `yarn jest --ci` (tests)
5. Android: `cd android && ./gradlew :app:assembleRelease` (or `bundleRelease` for AAB)
6. iOS: `xcodebuild archive` → export IPA (macOS runner required)

Steps 1-4 run on every PR. Steps 5-6 run on pushes to `master`/`release` branches.

### 3.6 App deploys: Google Play + TestFlight

**Android:**

- [`r0adkll/upload-google-play@v1`](https://github.com/r0adkll/upload-google-play) uploads an AAB to the Play Console internal/alpha/beta/production track.
- Requires a Google Play Service Account JSON key with "Release Manager" role on the app.
- Keystore: base64-encode the `.keystore` file, store as a secret, decode during build.

**iOS:**

- [`apple-actions/upload-testflight-build@v1`](https://github.com/apple-actions/upload-testflight-build) uploads an IPA to TestFlight.
- Requires an App Store Connect API key (`.p8`), Key ID, and Issuer ID.
- Code signing: use App Store Connect API with "automatic signing" where possible, or manage certificates via [`apple-actions/import-codesign-certs@v1`](https://github.com/apple-actions/import-codesign-certs).
- macOS runner required for Xcode; GitHub Actions `macos-14` image comes with Xcode 15.

**Fastlane vs. direct Actions:** Fastlane is a battle-tested Ruby toolchain that abstracts app store uploads. For a team of one, direct Actions are simpler. Revisit Fastlane if the iOS signing gets complex.

### 3.7 CodePush for JS-only updates

CodePush lets you ship JS bundle updates without going through the app stores. For bugfixes that don't touch native code, this is hours vs. days.

The infrastructure is partially present (env vars in `.env` files, native plugin commented out in the app). Phase 8 of this initiative enables it:

1. Re-enable `react-native-code-push` in the app.
2. GitHub Actions workflow that calls `appcenter codepush release-react` (or the new [Visual Studio App Center replacement](https://github.com/microsoft/code-push-server) / [CodePush standalone](https://github.com/microsoft/react-native-code-push) since App Center is sunsetting).

**Caveat:** Microsoft App Center is in the process of being deprecated. The replacement path is either (a) self-host CodePush via the OSS server, or (b) switch to [Expo Updates](https://docs.expo.dev/eas-update/introduction/) (requires EAS setup).

**Recommendation:** defer CodePush to a later sub-phase or a separate initiative. Get the main CI/CD wins first. Evaluate Expo Updates vs. self-hosted CodePush when this comes up.

### 3.8 Secrets inventory for both repos

**API secrets (GitHub Actions → Secrets):**

| Secret name             | Maps to env var         | Source                                |
| ----------------------- | ----------------------- | ------------------------------------- |
| `DATABASE_URI`          | `DATABASE_URI`          | MongoDB Atlas connection string       |
| `DIPDB`                 | `DIPDB`                 | DIP database connection               |
| `X_API_KEY`             | `X_API_KEY`             | bcrypt-hashed API key                 |
| `X_API_KEY_3`           | `X_API_KEY_3`           | hex API key variant                   |
| `JWT_SECRET`            | `JWT_SECRET`            | random 32-byte secret                 |
| `JWT_ACCESS_EXPIRE`     | `JWT_ACCESS_EXPIRE`     | `15m` (from `01-token-refresh`)       |
| `JWT_REFRESH_EXPIRE`    | `JWT_REFRESH_EXPIRE`    | `7d`                                  |
| `EMAIL_VERIFY_KEY`      | `EMAIL_VERIFY_KEY`      | WhoisAPI                              |
| `SMTP_HOST`             | `SMTP_HOST`             | SES or provider                       |
| `SMTP_PORT`             | `SMTP_PORT`             |                                       |
| `SMTP_EMAIL`            | `SMTP_EMAIL`            |                                       |
| `SMTP_PASSWORD`         | `SMTP_PASSWORD`         |                                       |
| `FROM_EMAIL`            | `FROM_EMAIL`            |                                       |
| `FROM_NAME`             | `FROM_NAME`             |                                       |
| `ACCESS_KEY`            | `ACCESS_KEY`            | AWS IAM                               |
| `ACCESS_SECRET`         | `ACCESS_SECRET`         | AWS IAM                               |
| `ACCESS_REGION`         | `ACCESS_REGION`         | `ap-south-1`                          |
| `MID`                   | `MID`                   | Paytm                                 |
| `WEBSITE`               | `WEBSITE`               | Paytm                                 |
| `CHANNEL_ID`            | `CHANNEL_ID`            | Paytm                                 |
| `INDUSTRY_TYPE_ID`      | `INDUSTRY_TYPE_ID`      | Paytm                                 |
| `MERCHANT_KEY`          | `MERCHANT_KEY`          | Paytm                                 |
| `ONESIGNAL_APP_ID`      | `ONESIGNAL_APP_ID`      |                                       |
| `ONESIGNAL_REST_API_ID` | `ONESIGNAL_REST_API_ID` |                                       |
| `ONESIGNAL_HOST`        | `ONESIGNAL_HOST`        |                                       |
| `SENDER_ID`             | `SENDER_ID`             | 2Factor                               |
| `API_2F_KEY`            | `API_2F_KEY`            | 2Factor                               |
| `PE_ID`                 | `PE_ID`                 | 2Factor                               |
| **SSH/infra:**          |                         |                                       |
| `SSH_PRIVATE_KEY`       | —                       | deploy user's private key             |
| `SSH_HOST`              | —                       | EC2 IP or DNS                         |
| `SSH_USER`              | —                       | e.g. `deploy`                         |
| `API_HEALTH_URL`        | —                       | full URL for post-deploy health check |

**App secrets (GitHub Actions → Secrets):**

| Secret name                        | Purpose                                                |
| ---------------------------------- | ------------------------------------------------------ |
| `KEYSTORE_BASE64`                  | `cat dzzlooms-upload-key.keystore \| base64`           |
| `KEYSTORE_PASSWORD`                | from `gradle.properties` `MYAPP_UPLOAD_STORE_PASSWORD` |
| `KEY_ALIAS`                        | `dzzlooms-key-alias`                                   |
| `KEY_ALIAS_PASSWORD`               | from `gradle.properties` `MYAPP_UPLOAD_KEY_PASSWORD`   |
| `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` | Play Console service account JSON                      |
| `APPLE_API_KEY_ID`                 | App Store Connect API key id                           |
| `APPLE_API_ISSUER_ID`              | App Store Connect issuer id                            |
| `APPLE_API_KEY_P8`                 | .p8 file contents                                      |
| `APPLE_TEAM_ID`                    | Apple developer team id                                |
| `APP_STORE_CONNECT_APP_ID`         | numeric app id                                         |
| `ONESIGNAL_APP_ID`                 | OneSignal app id for build-time config                 |
| `API_URL`                          | Production API base URL                                |
| `X_API_KEY`                        | API key for build-time config                          |
| `CODEPUSH_STAGING_KEY_ANDROID`     | (if CodePush is used)                                  |
| `CODEPUSH_STAGING_KEY_IOS`         |                                                        |
| `CODEPUSH_PRODUCTION_KEY_ANDROID`  |                                                        |
| `CODEPUSH_PRODUCTION_KEY_IOS`      |                                                        |

### 3.9 GitHub Environments for deploy gates

Use [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) to:

- Separate `staging` and `production` secrets.
- Require **manual approval** before a `production` deploy job runs. A reviewer clicks "approve" in the GitHub UI, then the deploy proceeds.
- Log every deployment with commit SHA, timestamp, approver.

**Recommendation:** require manual approval on production, auto-deploy to staging.

---

## 4. Target Architecture

### 4.1 API pipeline

```
┌─────────────────┐
│ PR to master    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ on: pull_request            │
│ .github/workflows/test.yml  │
│                             │
│   jobs:                     │
│    test                     │
│    ├─ checkout              │
│    ├─ setup-node@v4 (22.x)  │
│    ├─ yarn install          │
│    ├─ yarn lint             │
│    ├─ yarn test --ci        │
│    └─ upload coverage       │
└─────────┬───────────────────┘
          │ status check
          ▼
   required for merge
          │
          ▼
┌─────────────────┐
│ merge to master │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ on: push → master           │
│ .github/workflows/deploy.yml│
│                             │
│   jobs:                     │
│    test (same as PR)        │
│     └─► deploy-staging      │
│          ├─ approval gate   │
│          └─ ssh + reload    │
│            └─ health check  │
│                             │
│    deploy-production        │
│    ├─ manual approval       │
│    ├─ ssh + reload          │
│    ├─ health check          │
│    └─ rollback on failure   │
└─────────────────────────────┘
```

### 4.2 App pipeline

```
┌─────────────────┐
│ PR to master    │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│ .github/workflows/verify.yml │
│   runs-on: ubuntu-latest     │
│                              │
│   jobs:                      │
│    verify                    │
│    ├─ yarn install           │
│    ├─ yarn lint              │
│    ├─ tsc --noEmit           │
│    └─ yarn jest --ci         │
└─────────┬────────────────────┘
          │ gate
          ▼
   required for merge
          │
          ▼
┌─────────────────┐
│ tag v* push     │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│ .github/workflows/release.yml│
│                              │
│   jobs:                      │
│    build-android             │
│    ├─ runs-on: ubuntu-latest │
│    ├─ decode keystore        │
│    ├─ gradle bundleRelease   │
│    └─ upload-google-play     │
│                              │
│    build-ios                 │
│    ├─ runs-on: macos-14      │
│    ├─ import certs           │
│    ├─ xcodebuild archive     │
│    ├─ export IPA             │
│    └─ upload to TestFlight   │
│                              │
│  both gated by manual approval │
└──────────────────────────────┘
```

---

## 5. Phased Rollout

### Phase 1 — API: CI-only (test + lint on PR)

**Goal:** start running tests on every PR. No deploys yet. Lowest-risk entry point.

#### Step 1.1 — Pin Node version

- File: `dzzlo_oms_api/package.json`
- Add `"engines": {"node": ">= 22.11.0"}` to match the app's constraint.
- Add a `.nvmrc` file with `22.11.0` so contributors' local Node matches CI.

#### Step 1.2 — Add ESLint

- `yarn add --dev eslint @eslint/js` (ESLint 9 uses flat config)
- Create `eslint.config.js` with a basic Node config (recommended rules, no style bikeshed for now).
- Add script: `"lint": "eslint ."`
- Run locally, fix glaring issues (expect < 20 warnings on a 239-file project with no prior lint; fix or silence).

#### Step 1.3 — Create `.github/workflows/test.yml`

```yaml
name: API Test

on:
  pull_request:
    branches: [master]
  push:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22.11.0"
          cache: "yarn"
      - run: yarn install --frozen-lockfile
      - run: yarn lint
      - run: yarn test --ci --passWithNoTests --maxWorkers=2
        env:
          NODE_ENV: testing
          # mongodb-memory-server handles the DB, no DATABASE_URI needed
          JWT_SECRET: test-secret-for-ci
          JWT_EXPIRE: 1h
```

#### Step 1.4 — Branch protection

- GitHub repo settings → Branches → Protection rule for `master`:
  - Require status checks to pass before merging
  - Require `test` (the job defined above) to pass
  - Require at least 1 approving review (optional for team-of-one)

#### Step 1.5 — Verify with a test PR

- Open a trivial PR (add a comment to a README).
- Watch the workflow run in GitHub Actions tab.
- Merge when green.

**Definition of Done:**

- Workflow exists and runs on every PR.
- Tests + lint are required to pass before merge.
- A failing test visibly blocks merge.
- No deploy automation yet.

---

### Phase 2 — API: CD (deploy to staging + production, SSH + PM2)

**Goal:** every push to `master` auto-deploys to staging; production requires manual approval.

#### Step 2.1 — Configure GitHub Environments

- Settings → Environments → New environment `staging`, another `production`.
- For `production`, enable "Required reviewers" with yourself (or a teammate).
- Add env-scoped secrets (SSH keys, env vars) to each environment.

#### Step 2.2 — Prepare the EC2 instance(s)

- Create a `deploy` user (or reuse `ubuntu`) with:
  - Own `~/.ssh/authorized_keys` with the GitHub Actions public key
  - Can run `git pull` in `/home/ubuntu/dzzlo_oms_api`
  - Can run `pm2 reload dzzlo-oms` (add to sudoers if PM2 runs as another user)
  - NO other sudo
- Verify: from your laptop, `ssh deploy@<host>` → `pm2 ls` works.

#### Step 2.3 — Create `.github/workflows/deploy.yml`

```yaml
name: API Deploy

on:
  push:
    branches: [master]
  workflow_dispatch: # allow manual runs

jobs:
  test:
    uses: ./.github/workflows/test.yml

  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      - name: Add host to known_hosts
        run: ssh-keyscan -H ${{ secrets.SSH_HOST }} >> ~/.ssh/known_hosts
      - name: Deploy
        run: |
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} <<'EOF'
            set -euo pipefail
            cd /home/ubuntu/dzzlo_oms_api
            git fetch origin master
            git reset --hard origin/master
            yarn install --frozen-lockfile
            pm2 reload dzzlo-oms --update-env
          EOF
      - name: Health check
        run: |
          sleep 5
          for i in 1 2 3 4 5; do
            if curl -fsS ${{ secrets.API_HEALTH_URL }} | grep -q '"status":"ok"'; then
              echo "Healthy"
              exit 0
            fi
            sleep 3
          done
          echo "Health check failed"
          exit 1

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production # ← manual approval gate set in env settings
    steps:
      # same steps as staging, different secrets scope
      - uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      - run: ssh-keyscan -H ${{ secrets.SSH_HOST }} >> ~/.ssh/known_hosts
      - name: Deploy
        run: |
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} <<'EOF'
            set -euo pipefail
            cd /home/ubuntu/dzzlo_oms_api
            PREV_SHA=$(git rev-parse HEAD)
            git fetch origin master
            git reset --hard origin/master
            yarn install --frozen-lockfile
            pm2 reload dzzlo-oms --update-env

            # Rollback on health failure
            sleep 5
            if ! curl -fsS http://localhost:8030/health | grep -q '"status":"ok"'; then
              echo "Health failed — rolling back"
              git reset --hard "$PREV_SHA"
              yarn install --frozen-lockfile
              pm2 reload dzzlo-oms --update-env
              exit 1
            fi
          EOF
```

#### Step 2.4 — Environment variables on the server

- Stop using `.env.production` on disk. Instead:
  - Create `/etc/dzzlo/dzzlo_oms.env` with the 28 secrets, owned by `root`, mode `0600`.
  - `ecosystem.config.js` sets `env` from `process.env` (the environment the PM2 daemon was started with).
  - A systemd-launched PM2 daemon loads `/etc/dzzlo/dzzlo_oms.env` via `EnvironmentFile=` in the unit file.
  - Alternative (simpler): let PM2's `ecosystem.config.js` continue to read `.env.production`, but keep that file owned by root and never commit/update it via the CI — it only changes manually when secrets rotate.

**Recommendation:** defer env file restructuring to Phase 7 (Parameter Store). For Phase 2, keep the current `.env.production` approach and just focus on code deploy automation.

#### Step 2.5 — Test the pipeline

- Push a no-op change to a file to `master`.
- Watch workflow.
- Staging deploys automatically; production waits for your approval.
- Approve → production deploys → health check passes → success.

**Definition of Done:**

- Push to master auto-deploys to staging, auto-runs health check.
- Production deploy blocked on manual approval.
- Failed health check rolls back production automatically.
- No human SSH needed for a normal release.

---

### Phase 3 — API: PR checks and dependency hygiene

**Goal:** harden the PR path so obvious mistakes can't merge.

#### Step 3.1 — Enable Dependabot

- File: `.github/dependabot.yml`
  ```yaml
  version: 2
  updates:
    - package-ecosystem: "npm"
      directory: "/"
      schedule:
        interval: "weekly"
      open-pull-requests-limit: 5
  ```
- Security updates auto-merge if tests pass (separate workflow).

#### Step 3.2 — Add CodeQL (free for public repos, also free for private on Team)

- `.github/workflows/codeql.yml` — standard template from GitHub.
- Finds SQL injection, XSS, path traversal style issues.

#### Step 3.3 — Require CodeQL and Dependabot alerts to pass

- Branch protection rule: add `CodeQL` as required check.

**Definition of Done:**

- Dependabot opens PRs weekly.
- CodeQL runs on every push.
- Branch protection enforces both.

---

### Phase 4 — App: CI-only (lint + type-check + test on PR)

**Goal:** mirror Phase 1 for the app project. No deploys yet.

#### Step 4.1 — Create `.github/workflows/verify.yml` in the app repo

```yaml
name: App Verify

on:
  pull_request:
    branches: [master]
  push:
    branches: [master]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22.11.0"
          cache: "yarn"
      - run: yarn install --frozen-lockfile
      - run: yarn lint
      - run: yarn tsc --noEmit
      - run: yarn test --ci --passWithNoTests --maxWorkers=2
```

#### Step 4.2 — Fix pre-existing issues

- Run `yarn lint` and `yarn tsc --noEmit` locally.
- Resolve errors (may take a few hours on a 238-test codebase that's never had CI).
- If some lint rules are aspirational, down-level them to warnings temporarily.

#### Step 4.3 — Branch protection on `master`

- Require `verify` to pass.

**Definition of Done:**

- Every PR runs lint + TS + Jest.
- Red checks block merge.

---

### Phase 5 — App: Android CD (build AAB, upload to Play Console internal track)

**Goal:** tagging a release (`v1.77.0`) builds an AAB and uploads it to the Play Console internal track. Manual promotion to production is still a human step.

#### Step 5.1 — Encode and store the keystore

Locally:

```bash
base64 -i android/app/dzzlooms-upload-key.keystore | pbcopy
```

Paste into GitHub Secret `KEYSTORE_BASE64`. Also add `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_ALIAS_PASSWORD`.

#### Step 5.2 — Get a Google Play Service Account

- [Play Console → API access → Create service account](https://developers.google.com/android-publisher/getting_started).
- Grant "Release Manager" role (not owner — least privilege).
- Download JSON, store as `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` secret.

#### Step 5.3 — Create `.github/workflows/release-android.yml`

```yaml
name: App Release Android

on:
  push:
    tags: ["v*"]
  workflow_dispatch:

jobs:
  build-android:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22.11.0"
          cache: "yarn"
      - uses: actions/setup-java@v4
        with:
          distribution: "zulu"
          java-version: "17"
      - run: yarn install --frozen-lockfile

      - name: Decode keystore
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > android/app/dzzlooms-upload-key.keystore

      - name: Write gradle.properties overrides
        run: |
          cat >> android/gradle.properties <<EOF
          MYAPP_UPLOAD_STORE_PASSWORD=${{ secrets.KEYSTORE_PASSWORD }}
          MYAPP_UPLOAD_KEY_PASSWORD=${{ secrets.KEY_ALIAS_PASSWORD }}
          EOF

      - name: Write .env
        run: |
          cat > .env.production <<EOF
          PROJ_ENV=production
          API_URL=${{ secrets.API_URL }}
          X_API_KEY=${{ secrets.X_API_KEY }}
          ONESIGNAL_APP_ID=${{ secrets.ONESIGNAL_APP_ID }}
          EOF

      - name: Build AAB
        working-directory: android
        run: |
          ./gradlew clean
          ./gradlew bundleRelease

      - uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON }}
          packageName: in.vsyst.dzzlooms
          releaseFiles: android/app/build/outputs/bundle/release/app-release.aab
          track: internal
          status: completed

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: app-release.aab
          path: android/app/build/outputs/bundle/release/app-release.aab
```

#### Step 5.4 — Versioning

- Tag a release: `git tag v1.77.0 && git push origin v1.77.0`.
- The tag triggers the workflow.
- Increment `versionCode` in `android/app/build.gradle` **as part of the tagged commit** (Play Store rejects duplicates).
- Long-term: auto-derive `versionCode` from the tag or commit count. For now, manual bump.

#### Step 5.5 — First deploy

- Run manually via `workflow_dispatch` first with a canary commit.
- Inspect Play Console internal track → confirm the new AAB.
- Test on a physical device via the Play Store internal link.

**Definition of Done:**

- `git tag v1.77.0 && git push origin v1.77.0` produces an installable AAB on the Play Console internal track.
- Artifact is archived on the workflow run.
- No manual Gradle build needed.

---

### Phase 6 — App: iOS CD (archive, upload to TestFlight)

**Goal:** tagging a release also triggers an iOS TestFlight upload.

#### Step 6.1 — Generate an App Store Connect API key

- https://appstoreconnect.apple.com/access/integrations/api → Generate.
- Store the `.p8` contents, Key ID, Issuer ID in GitHub Secrets.

#### Step 6.2 — Set up code signing

Options:

- **App Store Connect API + automatic signing** (simplest): GH Actions passes the API key to `xcodebuild`, which handles signing automatically via Xcode cloud.
- **Manual certs via [`apple-actions/import-codesign-certs`](https://github.com/apple-actions/import-codesign-certs)**: store a `.p12` certificate + provisioning profile, import on each build.

Recommendation: start with manual certs (option B) — more reliable in CI experience reports.

#### Step 6.3 — Create `.github/workflows/release-ios.yml`

```yaml
name: App Release iOS

on:
  push:
    tags: ["v*"]
  workflow_dispatch:

jobs:
  build-ios:
    runs-on: macos-14
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22.11.0"
          cache: "yarn"
      - run: yarn install --frozen-lockfile

      - name: Install pods
        working-directory: ios
        run: pod install

      - name: Import code signing certificates
        uses: apple-actions/import-codesign-certs@v3
        with:
          p12-file-base64: ${{ secrets.IOS_P12_BASE64 }}
          p12-password: ${{ secrets.IOS_P12_PASSWORD }}

      - name: Download provisioning profile
        uses: apple-actions/download-provisioning-profiles@v3
        with:
          bundle-id: in.vsyst.dzzlooms
          profile-type: IOS_APP_STORE
          issuer-id: ${{ secrets.APPLE_API_ISSUER_ID }}
          api-key-id: ${{ secrets.APPLE_API_KEY_ID }}
          api-private-key: ${{ secrets.APPLE_API_KEY_P8 }}

      - name: Archive
        working-directory: ios
        run: |
          xcodebuild \
            -workspace dzzlo_oms_app.xcworkspace \
            -scheme dzzlo_oms_app \
            -configuration Release \
            -sdk iphoneos \
            -archivePath $PWD/build/dzzlo_oms_app.xcarchive \
            archive

      - name: Export IPA
        working-directory: ios
        run: |
          xcodebuild -exportArchive \
            -archivePath $PWD/build/dzzlo_oms_app.xcarchive \
            -exportOptionsPlist ExportOptions.plist \
            -exportPath $PWD/build

      - uses: apple-actions/upload-testflight-build@v1
        with:
          app-path: ios/build/dzzlo_oms_app.ipa
          issuer-id: ${{ secrets.APPLE_API_ISSUER_ID }}
          api-key-id: ${{ secrets.APPLE_API_KEY_ID }}
          api-private-key: ${{ secrets.APPLE_API_KEY_P8 }}
```

#### Step 6.4 — `ExportOptions.plist`

- Check in a minimal `ios/ExportOptions.plist` with `method=app-store`, team id, etc.
- Signing style = manual (referenced by the imported profile name).

#### Step 6.5 — CFBundleVersion bump

- Before tagging: `agvtool next-version -all` to bump `CURRENT_PROJECT_VERSION`.
- Long-term: auto-bump via script in the workflow; commit back. For now, manual.

**Definition of Done:**

- Tagging `v1.77.0` uploads an IPA to TestFlight.
- Build status visible in App Store Connect.
- Install on a registered test device via TestFlight app.

---

### Phase 7 — API: Secrets to AWS Parameter Store (optional follow-up)

**Goal:** eliminate `.env.production` from disk.

#### Step 7.1 — Create parameters in AWS Systems Manager

- Prefix: `/dzzlo/oms/prod/*`
- One parameter per secret.
- Use `SecureString` type with a KMS key.

#### Step 7.2 — Modify API startup to load from SSM

- File: `dzzlo_oms.js` (or a new `helpers/loadConfig.js`)
- On boot, call `ssm:GetParametersByPath` with the prefix, populate `process.env`.
- Fall back to `.env` files for local development.
- Requires AWS SDK (`@aws-sdk/client-ssm`, already likely in the project via SES SDK).

#### Step 7.3 — Attach IAM role to the EC2 instance

- Instance profile allows `ssm:GetParametersByPath` on `/dzzlo/oms/prod/*`.
- No static AWS keys needed on the instance.

#### Step 7.4 — Delete `.env.production` from the server

- Once verified working, `rm /home/ubuntu/dzzlo_oms_api/.env.production`.
- Update GH Actions workflow to skip any `.env` writing.

**Definition of Done:**

- API starts with no `.env*` files on the server.
- Secrets are only in SSM Parameter Store.
- Rotating a secret: update the parameter, `pm2 reload` — zero downtime, no file touches.

---

### Phase 8 — App: CodePush for JS-only hotfixes (optional follow-up)

**Skipped in favor of deeper evaluation.** App Center is deprecated; Expo Updates and self-hosted CodePush are both viable alternatives. Spin this up as a separate mini-initiative after Phase 5 + Phase 6 are stable.

---

## 6. Benefits

| Benefit                   | Before                              | After                                                            |
| ------------------------- | ----------------------------------- | ---------------------------------------------------------------- |
| API deploy time           | ~5 min (manual SSH + pm2)           | ~3 min (automated, fully hands-off)                              |
| Failed-deploy detection   | User reports + logs                 | Health check auto-rollback                                       |
| Bus factor                | 1                                   | ∞ (anyone with GH write can trigger)                             |
| Tests before deploy       | Never                               | Every PR, every deploy                                           |
| Time to ship a 1-line fix | 10-20 min                           | 3-5 min                                                          |
| App release time          | 30-60 min of manual steps           | 15 min (build time), 1 min human work                            |
| Android AAB traceability  | Local .apk, no link to commit       | Artifact linked to tag + commit SHA                              |
| Secrets exposure          | Plaintext `.env.production` on disk | GitHub Secrets + (Phase 7) SSM                                   |
| Rollback (API)            | Manual `git reset --hard`           | Automatic on failed health check                                 |
| Rollback (App)            | Halt Play Console release           | Rotate back to previous AAB via Play Console                     |
| Cost                      | 0 (manual time)                     | ~$0 on Free tier; ~$4/mo for macOS minutes if iOS builds monthly |

---

## 7. Risks & Rollback

| Risk                                                       | Likelihood         | Impact   | Mitigation                                                                                      |
| ---------------------------------------------------------- | ------------------ | -------- | ----------------------------------------------------------------------------------------------- |
| SSH key leaked                                             | Low                | Critical | Limit deploy user's permissions; rotate keys quarterly; monitor `auth.log`                      |
| Health check passes but app is broken (false positive)     | Medium             | High     | Deepen health check (`tasks_01/RES-1` covers this); add smoke-test endpoint                     |
| Play Console service account compromised                   | Low                | High     | Least privilege (Release Manager only); rotate yearly                                           |
| iOS signing break                                          | Medium             | Medium   | Check in `ExportOptions.plist`; keep certs valid; monitor expiry                                |
| CI flakiness (Jest on CI fails intermittently)             | Medium             | Low      | `--maxWorkers=2` and `testTimeout: 30000`; quarantine flaky tests                               |
| GitHub Actions minute budget overrun                       | Low                | Low      | Watch billing; iOS macOS minutes cost 10× Linux; only build iOS on tag                          |
| Rollback infinite loop (rollback commit also fails health) | Low                | High     | Cap rollback attempts at 1; alert human on failure                                              |
| Keystore lost                                              | Low (if backed up) | Critical | Back up to secure offline storage; losing this = can't ever update the Play Store listing again |

### Rollback plan (meta — how to roll back the CI/CD itself)

- **Disable a workflow:** edit the workflow file and set `on: []`, commit. No future runs.
- **Fall back to manual deploy:** the old SSH + `git pull` process still works. Don't remove the ability to log in manually.
- **Revert a deploy:** re-run the workflow with an earlier commit SHA via `workflow_dispatch`. For emergencies, SSH in and `git reset --hard <SHA>` + `pm2 reload`.

---

## 8. Testing Strategy

### 8.1 Workflow testing

- Use a fork or a throwaway branch to test workflow changes.
- [act](https://github.com/nektos/act) to run Actions locally, but iOS builds can't be tested this way.
- Always have a working rollback command typed out before approving a new workflow.

### 8.2 Deploy smoke tests

After every deploy:

- `GET /health` → 200 with `{status: "ok"}`
- `GET /api/v3/version` → current commit SHA (add this endpoint if not present)
- `POST /api/v3/auth/loginCredentialVerify` with test credentials → 200
- If any fail → rollback.

### 8.3 Secret rotation drill

Quarterly: rotate the SSH deploy key and one other secret. Verify the workflow still passes. Ensures the process isn't just theoretical.

---

## 9. Post-launch Monitoring

- GitHub Actions run history tab: watch for flakes
- Deploy frequency (target: enable "push to master deploys automatically" without fear)
- Deploy lead time (commit → production)
- Change failure rate (deploys that triggered a rollback)
- Mean time to recovery (rollback time)

These are the [DORA metrics](https://dora.dev/). Even tracking them roughly is an improvement.

---

## 10. Open Questions

1. **OIDC federation instead of SSH?** Long-term yes. Phase 9 future work.
2. **Monorepo consolidation?** The two repos are siblings. A single repo with `/api` and `/app` directories would share CI infrastructure and simplify cross-cutting changes (e.g., token refresh rollout from `01`). Big move; defer to a separate initiative.
3. **E2E tests in CI?** Detox for RN is heavy; Maestro is lighter. Not in scope here; consider after unit tests are stable.
4. **Staged rollout on Play Store?** The `upload-google-play` action supports `userFraction: 0.1` for phased rollout. Add once we're confident in the pipeline.
5. **Slack / Discord notifications?** Trivial to add via [`slackapi/slack-github-action`](https://github.com/slackapi/slack-github-action). Nice-to-have.
6. **CodeQL costs?** Free for public repos, included in Team/Enterprise for private. Confirm plan before enabling.
7. **Will the API pass lint cleanly on first try?** Probably not. Expect a few hours to silence or fix existing warnings on 239 files.

---

## Appendix A — Workflow file locations

**API repo (`dzzlo_oms_api/.github/workflows/`):**

- `test.yml` — PR checks (Phase 1)
- `deploy.yml` — staging + production deploy (Phase 2)
- `codeql.yml` — security scanning (Phase 3)
- `.github/dependabot.yml` — dependency updates (Phase 3)

**App repo (`dzzlo_oms_app/.github/workflows/`):**

- `verify.yml` — lint + TS + Jest on PR (Phase 4)
- `release-android.yml` — tag-triggered Android release (Phase 5)
- `release-ios.yml` — tag-triggered iOS release (Phase 6)
- `.github/dependabot.yml` — dependency updates

## Appendix B — Secrets setup checklist

Before starting Phase 2:

- [ ] Generate a new SSH keypair dedicated to GitHub Actions (`ssh-keygen -t ed25519 -f ~/.ssh/dzzlo-deploy`)
- [ ] Add public key to `~/.ssh/authorized_keys` of the `deploy` user on EC2
- [ ] Add private key to GitHub Secret `SSH_PRIVATE_KEY`
- [ ] Add `SSH_HOST`, `SSH_USER`, `API_HEALTH_URL`
- [ ] Create `staging` and `production` GitHub Environments
- [ ] Add production approval reviewers

Before starting Phase 5:

- [ ] Base64-encode the keystore and add as secret
- [ ] Add keystore passwords as secrets
- [ ] Create Play Console service account, add JSON as secret
- [ ] Confirm `in.vsyst.dzzlooms` is registered and published at least once in the Play Console (required for service-account uploads)

Before starting Phase 6:

- [ ] Create App Store Connect API key
- [ ] Export iOS distribution cert as `.p12`, base64-encode
- [ ] Add `IOS_P12_BASE64`, `IOS_P12_PASSWORD`, `APPLE_API_KEY_ID`, `APPLE_API_ISSUER_ID`, `APPLE_API_KEY_P8`
- [ ] Check in `ios/ExportOptions.plist`
