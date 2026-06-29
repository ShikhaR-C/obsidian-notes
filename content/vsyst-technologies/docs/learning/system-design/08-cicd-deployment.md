# Session 8: CI/CD & Deployment

> Phase 4 — Operations | 2 hours | Review: 15 min

## What You'll Learn

- Why manual SSH-and-pull deploys are a ticking time bomb and what the 12-Factor App says about build/release/run
- Three deployment options ranked by implementation effort, from a shell script you can ship today to a full CodeDeploy pipeline
- How to manage secrets without copying .env files by hand
- How to write a deploy script and an emergency runbook so that someone besides you can keep the system running
- How to add a GitHub Actions workflow that runs tests on every push to master

## Why This Matters for DZZLO-OMS

Your current deploy process: SSH into each EC2 instance, `git pull`, `pm2 restart dzzlo-oms`. You do this for each server individually. The `.env.production` file was copied to each server by hand. There is no CI/CD pipeline, no automated testing before deploy, no automated rollback. AMI snapshots are taken manually after significant updates, and the ASG launch template uses those AMIs to spin up new instances.

Here is the real problem: **bus factor = 1**. You are the only person who has SSH keys, `.env` files, AWS Console access, and the knowledge of how to deploy. If you are on a flight, asleep, or unavailable for any reason and the system goes down, nobody can fix it. There is no runbook. There is no script. There is nothing documented.

This session does not aim to build a perfect pipeline. It aims to get you from "only one person can deploy" to "anyone with the right access can deploy by running one command" — today, in under two hours.

---

## Hour 1 — Concepts (60 min)

### Step 1: CI/CD Principles and Why Manual Deploys Fail (20 min)

**Read:** [12-Factor: Build, Release, Run](https://12factor.net/build-release-run) and [12-Factor: Config](https://12factor.net/config)

The 12-Factor App defines three stages that should be strictly separated:


| Stage       | What Happens                                                                        | Your Current State                                                                                                                                                              |
| ----------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Build**   | Convert code into an executable bundle (install deps, run tests, compile if needed) | You run `npm install` on the server itself. No tests run before deploy. If a dependency fails to install, you find out after SSH-ing in.                                        |
| **Release** | Combine the build with the environment config to create a release                   | You have no concept of a "release." The code on the server IS the release. The `.env.production` file was hand-copied months ago and has drifted between servers at least once. |
| **Run**     | Execute the release in the execution environment                                    | `pm2 restart dzzlo-oms`. This is the only step you have.                                                                                                                        |


**Why this breaks down:**

1. **No reproducibility.** If you deploy to Server A and Server B an hour apart, and someone pushes a commit in between, they run different code. You have no way to verify they match.
2. **No testing gate.** A typo in a route handler goes straight to production. Jest is configured (`jest.config.js` exists, `npm test` is in `package.json`) but nothing forces tests to run before deploy.
3. **No audit trail.** You cannot answer "what version is running on Server B right now?" without SSH-ing in and running `git log -1`.
4. **No rollback procedure.** Your current rollback is: detach from ALB, SSH in, `git revert`, `pm2 restart`, reattach. That is 5+ manual steps under pressure, when the system is already down and users are affected.
5. **No delegation.** Nobody else can do any of this. If you hire a second developer tomorrow, you would need to give them a 30-minute walkthrough just to deploy.

**The 12-Factor config principle** is also violated: your config (database URIs, API keys, JWT secrets) lives in `.env` files committed to the server filesystem. The 12-Factor approach says config should be stored in the environment, not in files that can get out of sync. AWS has tools for this (Parameter Store, Secrets Manager) — we cover them in Step 3.

### Step 2: Three Deployment Options, Ranked by Effort (25 min)

You do not need to pick one right now. Read all three, understand the trade-offs, and implement Option A in Hour 2. Options B and C are for when you are ready.

---

#### Option A: `deploy.sh` Script (30 minutes to implement)

**What it does:** A single shell script on your local machine that SSHs into each server, pulls the latest code, installs dependencies, and restarts PM2. You run one command instead of repeating manual steps per server.

**What it solves:**

- Bus factor drops from 1 to "anyone who has the script and SSH key"
- Both servers always get the same commit
- Deploy steps are documented in code, not in your head
- Rollback becomes `./deploy.sh --rollback` instead of remembering 5 steps

**What it does NOT solve:**

- No automated testing before deploy (you still have to remember to run tests)
- Still requires SSH access to each server
- No integration with GitHub — push and deploy are still separate actions

**Effort:** ~30 minutes. You will implement this in Step 4.

---

#### Option B: GitHub Actions + SSH Deploy (2-4 hours to implement)

**What it does:** A GitHub Actions workflow triggers on push to `master`. It runs tests, and if they pass, SSHs into each server and deploys automatically.

**What it solves (beyond Option A):**

- Tests run automatically before every deploy — broken code cannot reach production
- Deploy is triggered by pushing to `master` — no manual SSH required
- GitHub Actions logs provide a full audit trail of every deploy
- Any developer with push access to `master` can deploy

**What it does NOT solve:**

- Still deploys by SSH-ing into running servers (not immutable infrastructure)
- Rolling deploy is manual — you would need to script the ALB deregistration yourself
- If a deploy fails mid-way (Server A updated, Server B failed), you have an inconsistent state

**Architecture:**

```
push to master
    |
    v
GitHub Actions runner
    |
    +--> Step 1: checkout code
    +--> Step 2: npm install
    +--> Step 3: npm test
    +--> Step 4: SSH to Server A → git pull → npm install → pm2 restart
    +--> Step 5: SSH to Server B → git pull → npm install → pm2 restart
```

**Effort:** 2-4 hours. Requires storing SSH private keys as GitHub Secrets and configuring the workflow YAML.

**Read:** [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart)

---

#### Option C: GitHub Actions + CodeDeploy + ASG (1-2 days to implement)

**What it does:** GitHub Actions builds and tests the code, then triggers AWS CodeDeploy to perform a rolling deployment across your Auto Scaling Group. CodeDeploy handles deregistering instances from the ALB, deploying, running health checks, and re-registering — with automatic rollback if health checks fail.

**What it solves (beyond Option B):**

- Rolling deploys: instances are updated one at a time, so the system is never fully down
- Automatic rollback: if the health check fails after deploy, CodeDeploy reverts automatically
- Works with ASG: new instances launched by the ASG automatically get the latest deployment
- No SSH required at all — CodeDeploy agent on each instance pulls the code
- Immutable-ish: combined with a fresh AMI bake, each deploy can be a clean slate

**What it does NOT solve:**

- Significant setup: IAM roles, CodeDeploy application, deployment group, appspec.yml, install scripts
- More AWS surface area to understand and maintain
- Debugging deployment failures requires reading CodeDeploy logs in CloudWatch

**Architecture:**

```
push to master
    |
    v
GitHub Actions runner
    |
    +--> Step 1: checkout + npm install + npm test
    +--> Step 2: zip artifact + upload to S3
    +--> Step 3: trigger CodeDeploy deployment
                    |
                    v
              CodeDeploy
                    |
                    +--> Deregister instance from ALB
                    +--> Pull artifact from S3
                    +--> Run install script (npm install, pm2 restart)
                    +--> Health check (curl /health)
                    +--> Re-register with ALB
                    +--> Repeat for next instance
```

**Effort:** 1-2 days. Requires CodeDeploy agent on each EC2 instance, IAM roles, S3 bucket, `appspec.yml`, and lifecycle hook scripts.

**Read:**

- [AWS CodeDeploy + ASG](https://docs.aws.amazon.com/codedeploy/latest/userguide/integrations-aws-auto-scaling.html)
- [CodeDeploy with ELB](https://aws.amazon.com/blogs/devops/use-aws-codedeploy-to-deploy-to-amazon-ec2-instances-behind-an-elastic-load-balancer-2/)
- [Node.js Deploy on AWS CI/CD](https://rrawat.com/blog/deploy-nodejs-on-aws-cicd)

---

**Recommendation:** Implement Option A today. Plan Option B for next week. Option C is your eventual target, but only after you are comfortable with GitHub Actions.

### Step 3: Secrets Management (15 min)

Your `.env.production` files contain database URIs, JWT secrets, API keys, SMTP passwords, AWS credentials, and payment gateway keys. These files were copied to each server by hand. Here are three approaches to managing them, from simplest to most robust:

#### Manual `.env` Files (current state)

**How it works:** You SCP the file to each server. The app reads it with `dotenv`.

**Problems:**

- Files can drift between servers (you update Server A, forget Server B)
- No audit trail — you cannot see when a secret was changed or by whom
- Secrets sit in plaintext on the filesystem
- New servers (from ASG scale-out) do NOT get the `.env` file automatically — you bake it into the AMI, which means the AMI contains plaintext secrets

#### AWS Systems Manager Parameter Store (recommended next step)

**How it works:** You store each secret as a parameter in AWS SSM Parameter Store (`/dzzlo-oms/production/DATABASE_URI`, etc.). Your app reads them at startup using the AWS SDK, or a boot script fetches them and writes a `.env` file before PM2 starts.

**Read:** [AWS Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)


| Feature        | Parameter Store (Standard)                     |
| -------------- | ---------------------------------------------- |
| Cost           | Free (up to 10,000 parameters)                 |
| Encryption     | Optional (KMS)                                 |
| Versioning     | Yes                                            |
| Audit trail    | CloudTrail logs every read/write               |
| Access control | IAM policies per parameter path                |
| Max size       | 4 KB per parameter (standard), 8 KB (advanced) |


**Migration path (do NOT do this now, just understand it):**

1. Store each secret in Parameter Store under a path like `/dzzlo-oms/prod/DATABASE_URI`
2. Give your EC2 instance role permission to read `/dzzlo-oms/prod/`*
3. Add a boot script to your launch template user data:
  ```bash
   #!/bin/bash
   # Fetch secrets from Parameter Store and write .env
   aws ssm get-parameters-by-path \
     --path "/dzzlo-oms/prod" \
     --with-decryption \
     --query "Parameters[*].[Name,Value]" \
     --output text | while read name value; do
       key=$(basename "$name")
       echo "${key}=${value}" >> /home/ubuntu/dzzlo_oms_api/.env.production
   done

   cd /home/ubuntu/dzzlo_oms_api
   pm2 start ecosystem.config.js --env production
  ```
4. Remove the `.env` file from the AMI — secrets are fetched fresh on every boot
5. New ASG instances automatically get current secrets

**Why this matters for your bus factor:** Anyone with AWS Console access (or CLI with the right IAM role) can update a secret. They do not need SSH access to the server. The change takes effect on next deploy or reboot.

#### AWS Secrets Manager

**How it works:** Similar to Parameter Store but designed specifically for secrets. Adds automatic rotation (e.g., rotate your database password every 90 days automatically) and cross-account sharing.

**When to use it instead of Parameter Store:**

- You need automatic secret rotation
- You are managing secrets across multiple AWS accounts
- Cost is not a concern ($0.40/secret/month)

**For DZZLO-OMS right now:** Parameter Store is sufficient. Secrets Manager is overkill unless you specifically need rotation.

---

## Hour 2 — Hands-On (60 min)

### Step 4: Write a `deploy.sh` Script (25 min)

This is the single highest-impact thing you can do today. The script below is a starting point — adapt the paths, server IPs, and SSH key location to your actual setup.

**Create this file at the root of your repo as `deploy.sh`:**

```bash
#!/bin/bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh — deploy DZZLO-OMS to production servers
#
# Usage:
#   ./deploy.sh              Deploy latest master to all servers
#   ./deploy.sh --rollback   Revert to previous commit on all servers
#   ./deploy.sh --status     Show current commit on each server
#
# Prerequisites:
#   - SSH key at ~/.ssh/dzzlo-prod.pem (or update SSH_KEY below)
#   - SSH access to all servers listed in SERVERS array
#   - Servers have git, node, npm, pm2 installed
# ─────────────────────────────────────────────────────────────────────────────

# ── Configuration ────────────────────────────────────────────────────────────
SSH_KEY="$HOME/.ssh/dzzlo-prod.pem"
SSH_USER="ubuntu"
APP_DIR="/home/ubuntu/dzzlo_oms_api"
PM2_APP="dzzlo-oms"
BRANCH="master"

# Add all your server IPs here
SERVERS=(
  "10.0.1.100"    # Server A (t3.small, 84% traffic)
  "10.0.1.101"    # Server B (t3.micro, 16% traffic)
)

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── Functions ────────────────────────────────────────────────────────────────
log()   { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

ssh_cmd() {
  local server=$1
  shift
  ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$server" "$@"
}

get_current_commit() {
  local server=$1
  ssh_cmd "$server" "cd $APP_DIR && git rev-parse --short HEAD"
}

deploy_to_server() {
  local server=$1
  log "Deploying to $server..."

  # Capture current commit for rollback reference
  local before_commit
  before_commit=$(get_current_commit "$server")
  log "  Current commit on $server: $before_commit"

  # Pull latest, install deps, restart
  ssh_cmd "$server" "cd $APP_DIR && \
    git fetch origin $BRANCH && \
    git reset --hard origin/$BRANCH && \
    npm install --production && \
    pm2 restart $PM2_APP"

  local after_commit
  after_commit=$(get_current_commit "$server")
  log "  Deployed commit on $server: $after_commit"

  # Basic health check
  sleep 3
  local health
  health=$(ssh_cmd "$server" "curl -sf http://localhost:8030/health || echo 'FAILED'")
  if [ "$health" = "FAILED" ]; then
    error "Health check failed on $server!"
    error "Rolling back to $before_commit..."
    ssh_cmd "$server" "cd $APP_DIR && \
      git reset --hard $before_commit && \
      npm install --production && \
      pm2 restart $PM2_APP"
    error "Rolled back $server to $before_commit. Check logs: ssh -i $SSH_KEY $SSH_USER@$server 'pm2 logs $PM2_APP --lines 50'"
    return 1
  fi

  log "  Health check passed on $server"
}

rollback_server() {
  local server=$1
  log "Rolling back $server to previous commit..."
  ssh_cmd "$server" "cd $APP_DIR && \
    git reset --hard HEAD~1 && \
    npm install --production && \
    pm2 restart $PM2_APP"
  local commit
  commit=$(get_current_commit "$server")
  log "  $server now at commit: $commit"
}

show_status() {
  log "Current deployment status:"
  for server in "${SERVERS[@]}"; do
    local commit
    commit=$(get_current_commit "$server")
    local pm2_status
    pm2_status=$(ssh_cmd "$server" "pm2 jlist" 2>/dev/null | \
      python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['pm2_env']['status'])" 2>/dev/null || echo "unknown")
    log "  $server: commit=$commit  pm2=$pm2_status"
  done
}

# ── Main ─────────────────────────────────────────────────────────────────────
case "${1:-deploy}" in
  --status)
    show_status
    ;;
  --rollback)
    warn "Rolling back ALL servers to previous commit."
    read -p "Are you sure? (y/N) " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
      for server in "${SERVERS[@]}"; do
        rollback_server "$server"
      done
      log "Rollback complete."
      show_status
    else
      log "Rollback cancelled."
    fi
    ;;
  deploy|"")
    log "Starting deployment to ${#SERVERS[@]} servers..."
    log "Branch: $BRANCH"
    echo ""

    failed=0
    for server in "${SERVERS[@]}"; do
      if ! deploy_to_server "$server"; then
        error "Deploy failed on $server. Stopping."
        failed=1
        break
      fi
      echo ""
    done

    if [ $failed -eq 0 ]; then
      log "All servers deployed successfully."
      show_status
    else
      error "Deployment failed. Check status:"
      show_status
      exit 1
    fi
    ;;
  *)
    echo "Usage: ./deploy.sh [deploy|--rollback|--status]"
    exit 1
    ;;
esac
```

**After creating the file:**

```bash
chmod +x deploy.sh
```

**Test it immediately:**

```bash
# Check status first (safe, read-only)
./deploy.sh --status

# If that works, try a deploy
./deploy.sh
```

**What to customize:**

- Replace the IP addresses in `SERVERS` with your actual EC2 private IPs
- Update `SSH_KEY` to point to your actual key file
- Update `APP_DIR` if your app lives somewhere else on the server
- Adjust the health check URL if `/health` is not your endpoint
- Add the script to `.gitignore` if you do not want it in the repo (it contains server IPs but no secrets)

**Exercise:** Create the script, customize it, and run `./deploy.sh --status` against your servers. If that works, you have already reduced your bus factor.

### Step 5: Write an Emergency Runbook (20 min)

Create a file at `docs/runbook.md` (or wherever your team can find it). The runbook should be usable by someone who has never seen your system before but has AWS Console access and the SSH key.

**Write a runbook that covers at minimum these scenarios:**

#### Scenario 1: API is returning 502/504 errors

```
1. Check ALB target health:
   AWS Console → EC2 → Target Groups → dzzlo-oms-tg → Targets tab
   - If targets show "unhealthy": SSH into the server, check pm2 status
   - If targets show "draining": ASG might be replacing the instance, wait 5 min

2. SSH into the server:
   ssh -i ~/.ssh/dzzlo-prod.pem ubuntu@<server-ip>

3. Check PM2:
   pm2 status
   pm2 logs dzzlo-oms --lines 100

4. If PM2 shows "errored":
   pm2 restart dzzlo-oms
   Wait 10 seconds, then: curl http://localhost:8030/health

5. If PM2 restart does not fix it, check .env:
   cat /home/ubuntu/dzzlo_oms_api/.env.production | head -5
   (verify NODE_ENV and DATABASE_URI are set)

6. If nothing works, rollback:
   ./deploy.sh --rollback
```

#### Scenario 2: Need to deploy a hotfix

```
1. Push the fix to master on GitHub
2. Run: ./deploy.sh
3. Verify: ./deploy.sh --status
4. Check ALB target health in AWS Console
```

#### Scenario 3: Server is unreachable via SSH

```
1. Check instance status in AWS Console:
   EC2 → Instances → find by IP
   - If "running" but unreachable: check Security Group inbound rules for SSH (port 22)
   - If "stopped": Start it, but note that public IP may change
   - If "terminated": ASG should launch a replacement (check ASG activity)

2. If ASG launched a new instance:
   - It will use the latest AMI from the launch template
   - The .env file is baked into the AMI (current state)
   - PM2 should start automatically via ecosystem.config.js
   - Verify the new instance is registered in the target group

3. If the new instance has old code:
   SSH in and run: ./deploy.sh
   Or manually: cd /home/ubuntu/dzzlo_oms_api && git pull && npm install --production && pm2 restart dzzlo-oms
```

#### Scenario 4: MongoDB Atlas is down

```
1. Check Atlas status: https://status.cloud.mongodb.com/
2. Check Atlas Console: https://cloud.mongodb.com/ → your cluster → Metrics
3. If the cluster is paused (should not happen on dedicated, but check): Resume it
4. If connection limits are hit: Check pm2 process count, restart PM2 to reset connection pools
5. Nothing you can do if Atlas itself is having an outage — it is a managed service.
   Post a status message to your users if downtime exceeds 15 min.
```

**Exercise:** Write the runbook now, customized with your actual server IPs, key paths, and AWS region. Then send it to at least one other person (cofounder, trusted colleague) along with:

- The SSH key file
- AWS Console credentials (IAM user with read-only access at minimum)
- This runbook

That single act — sharing the runbook, key, and credentials — is the most important thing you do today.

### Step 6: GitHub Actions Starter — Run Tests on Push (15 min)

Even if you are not ready for automated deploys (Option B), you can add a GitHub Actions workflow that runs your test suite on every push to `master`. This catches bugs before you deploy, and it takes 15 minutes to set up.

**Create `.github/workflows/test.yml`:**

```yaml
name: Run Tests

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18]    # Match your production Node version

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
        env:
          NODE_ENV: development
          # Add any env vars your tests need.
          # Do NOT put real secrets here — use GitHub Secrets
          # for anything sensitive, or use mongodb-memory-server
          # (which your devDependencies already include).
```

**What this does:**

- Every push to `master` and every pull request targeting `master` triggers a test run
- The workflow checks out your code, installs dependencies with `npm ci` (faster and stricter than `npm install`), and runs `npm test`
- Your `jest.config.js` is already configured; `mongodb-memory-server` is already in your devDependencies — tests should run without needing a real database connection
- If tests fail, GitHub shows a red X on the commit and the PR — you see the failure before deploying

**Read:** [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart)

**To set this up:**

```bash
mkdir -p .github/workflows
# Create the test.yml file above
git add .github/workflows/test.yml
git commit -m "ci: add GitHub Actions workflow to run tests on push"
git push origin master
```

Then go to your GitHub repo → Actions tab. You should see the workflow running.

**Exercise:** Create the workflow file and push it. Watch the first run. If tests fail, that is useful information — it tells you exactly what would break if you deployed right now. Fix the failing tests before moving to Option B.

---

## 15-Minute Review — Bus Factor Reduction Checklist

Go through this checklist. For each item, mark whether it is done, in progress, or not started. The goal is to have at least the first five checked off by the end of this session.

### Deploy Knowledge (can someone else deploy?)

- `deploy.sh` script exists and is tested
- Script is documented (usage, prerequisites, customization)
- At least one other person has the SSH key
- At least one other person has AWS Console access (even read-only)
- Emergency runbook exists with step-by-step instructions

### Automated Safety Nets (do bugs get caught before production?)

- GitHub Actions runs tests on push to `master`
- Tests actually pass in CI (not just locally)
- Deploy script includes a health check after restart
- Rollback procedure is scripted, not manual

### Secrets Management (can secrets be recovered without you?)

- All secrets are documented (what they are, not their values) in `.env.example`
- At least one other person knows where secrets are stored
- Plan exists to move secrets to Parameter Store (even if not implemented yet)

### Disaster Recovery (can the system recover without you?)

- AMI is recent (less than 2 weeks old)
- ASG launch template uses the latest AMI
- New instances launched by ASG can serve traffic without manual intervention
- Someone besides you knows how to check ALB target health
- Someone besides you knows how to read PM2 logs

**Scoring:**

- **0-5 checked:** Critical risk. Prioritize this over feature work.
- **6-10 checked:** Moderate risk. You have the basics, keep going.
- **11-14 checked:** Good. You can go on vacation without your laptop.
- **15 checked:** Excellent. Your system can survive without you.

**Concrete next steps after this session:**

- Share the deploy script, SSH key, and runbook with at least one other person
- Push the GitHub Actions test workflow and fix any failing tests
- Schedule a 2-hour block to implement Option B (GitHub Actions + SSH deploy)
- Investigate Parameter Store migration — start with one non-critical secret to test the flow
- Take a fresh AMI snapshot that includes the deploy script

---

## Resources

**12-Factor App:**

- [Build, Release, Run](https://12factor.net/build-release-run)
- [Config](https://12factor.net/config)

**GitHub Actions:**

- [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart)

**AWS Deployment:**

- [AWS CodeDeploy + ASG](https://docs.aws.amazon.com/codedeploy/latest/userguide/integrations-aws-auto-scaling.html)
- [CodeDeploy with ELB](https://aws.amazon.com/blogs/devops/use-aws-codedeploy-to-deploy-to-amazon-ec2-instances-behind-an-elastic-load-balancer-2/)
- [Node.js Deploy on AWS CI/CD](https://rrawat.com/blog/deploy-nodejs-on-aws-cicd)

**Secrets Management:**

- [AWS Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)

