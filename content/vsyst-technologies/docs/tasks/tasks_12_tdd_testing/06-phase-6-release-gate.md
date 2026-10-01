# Phase 6 — Release Gate

**Outcome:** one command proves all three projects pass their suites before a release; the policy when it fails is written and non-negotiable (release blocked, bug becomes a failing regression test first); a CI path is defined that reconciles the existing tasks_02 CI plan.
**Effort:** 1–2 dev-days for the local gate + policy; +1–2 for CI workflows (⏳ Q8).

> **TDD lens:** the gate is the whole point of the safety net — it converts "we think nothing broke" into "the regression contract passed on this exact code." It must be boring, fast enough to run without dread, and impossible to half-run.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). 🟡 The gate, the policy, the checklist template and the CI workflows exist, and the gate now checks two fixture sets; what is missing is proof on a release — no gate run is recorded on the 1.5.5 / 1.79 release commits (the latest recorded PASS is in API PR #39's body, 2026-09-04), `master`'s CI is red (`X-REL-1`), lint is not in the gate and e2e stays deferred. Checklist: 4 ✅, 1 🟡, 1 ⏸. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## 6.1 The command — local gate first (⏳ Q8 for CI timing)

**Status (2026-10-01):** ✅ `scripts/release_gate.sh:22-26` — fixtures-fresh first, then API `test:full`, web, app; the "second iteration" (`yarn lint` per repo) is not in the script yet ⬜.

Lives in the reference repo (all four checkouts are siblings in the versioned workspace folder, e.g. `v1_79/`):

`dzzlo_oms_api/scripts/release_gate.sh` (new):

```bash
#!/usr/bin/env bash
# Release gate: runs every repo's suite against local-only data. Any failure blocks release.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"   # the vN_NN workspace folder
FAIL=0

gate() {
  local name="$1" dir="$2" cmd="$3"
  echo "──────────── ${name}: ${cmd}"
  if (cd "${ROOT}/${dir}" && eval "${cmd}"); then
    echo "✅ ${name}"
  else
    echo "❌ ${name}"
    FAIL=1
  fi
}

gate "api (seed → jest → uproot)" "dzzlo_oms_api"  "yarn test:full"
gate "web (vitest)"               "dip-web"        "yarn test"
gate "app (jest)"                 "dzzlo_oms_app"  "yarn test"

echo "────────────"
[ "${FAIL}" -eq 0 ] && echo "RELEASE GATE: PASS" || echo "RELEASE GATE: BLOCKED"
exit "${FAIL}"
```

Run from anywhere: `bash dzzlo_oms_api/scripts/release_gate.sh`. Deliberately dumb — no parallelism, no skipping, full output. Add `yarn lint` per repo to the gate once the suites are stable (second iteration, noted in the script header when done).

## 6.2 The policy — written, absolute

**Status (2026-10-01):** ✅ adopted verbatim in API `docs/testing.md` §9 ("The policy — written, absolute", `:339`).

1. **Green gate or no release.** No "just this once," no partial runs, no local diffs on the release commit after the gate ran. If the gate is red, the release date moves, not the bar.
2. **Every gate failure becomes a regression test.** If the failure is a real bug: write/point-to the failing test **in the owning repo** first, fix, re-run the **entire** gate from scratch. If the failure is a flaky/bad test: fixing the test is the release work — flakes are bugs in the safety net.
3. **Bugs found after release** (by a customer or otherwise) enter the same loop: failing regression test → fix → test stays forever. This is the mandatory-TDD rule from Phase 7.
4. **Contract changes** (API response shapes) require `fixtures:export` → `fixtures:pull` → front-end suites green _within the same release_ (Phase 5 drift detector enforces the API side).

## 6.3 The release checklist (copy per release into the release notes/PR)

**Status (2026-10-01):** 🟡 template in `docs/testing.md` §9 (`:357`); no filled checklist or gate run is recorded in the repos for the 1.5.5 / 1.79 releases (API PR #39's and app PR #49's bodies record gate PASSes at their 2026-09-04 heads) ❔ — the user can confirm. The Q8 ritual is now visible: each repo cuts a tag plus a GitHub release that names the compatible builds (API `v1.5.5`, 2026-09-30: Android 1.79 (105), iOS 1.79 (4), DIP-Web 1.4.8; app `v1.79`).

```
Release vX.YY gate — run on commit <sha> per repo
- [ ] dzzlo_oms_api  yarn test:full          ✅/❌
- [ ] dip-web        yarn test                ✅/❌
- [ ] dzzlo_oms_app  yarn test                ✅/❌
- [ ] Fixtures fresh: fixtures:export + pull ran if any API contract changed
- [ ] Flow→test map (Phase 2 §2.1) — new flows added this release have rows
- [ ] Legacy: no ignored-suite change slipped in
- [ ] (when adopted) e2e smoke: login + 1 order + 1 payment per role  ✅/❌/n-a
```

**Open question folded in (⏳ Q8):** how a release is actually cut — what copying `v1_77/` → `v1_78/` corresponds to (app release line? all repos tagged together? who does it, when). The checklist attaches to whatever that ritual is; answer determines where the checklist physically lives (release PR template per repo vs a vault note per release).

## 6.4 E2E smoke — decision slot (⏳ Q6)

**Status (2026-10-01):** ⏸ still deferred — no Detox, Maestro or Playwright in either repo (tree and `package.json` searched).

Deliberately _not_ specified until Q6 is answered. The reserved design if adopted: a `scripts/e2e/` runner that (a) starts a standalone local mongod via `mongodb-memory-server`'s persistent mode, (b) boots the API against it (`NODE_ENV=development`, overridden `DATABASE_URI`), (c) seeds via the existing factories, then (d) runs Playwright (web, ~5 scenarios) and/or Maestro (app, ~3 flows) against it. Strictly local, ≤ 10 minutes, release-gate-only — never in the inner loop. Until then, the gate above ships without e2e and is still a massive upgrade over manual verification.

## 6.5 CI — reconcile with `tasks_02_major/05-cicd-github-actions.md` (⏳ Q8)

**Status (2026-10-01):** 🟡 API `.github/workflows/test.yml` (PRs + pushes to `master`, mongod cache keyed `8.2.1`, 15-min timeout) and app `.github/workflows/test.yml` (PRs + pushes to `main`, Jest only); pushes to `slave` get no run, and the app job has no lint, type-check or build step and ran 157.5 s at `ea7e7222` — see `X-CI-1` and `X-CI-2` in tasks_02. dip-web — not assessed.

That plan already chose GitHub Actions + Jest; dip-web already runs `lint.yml`. The increment here, per repo, once Q8 confirms:

- `dzzlo_oms_api/.github/workflows/test.yml`: `yarn install` → `yarn test:full` on PR + release branches (memory-server downloads its pinned binary in CI — cache `~/.cache/mongodb-binaries`).
- `dip-web/.github/workflows/test.yml`: `yarn test` (mirror of existing lint.yml structure).
- `dzzlo_oms_app/.github/workflows/test.yml`: `yarn test` (pure JS suites — no emulator needed at this depth).

The **local gate script remains the release ritual** even after CI exists (CI proves PRs; the gate proves the exact release combination of the three repos). Full cross-repo CI orchestration is out of scope until the release-cut mechanics (Q8) are known.

## 6.6 Verification — how we know Phase 6 is done

**Status (2026-10-01):** 🟡 PASS and BLOCKED both proven on 2026-07-10; "one real release has used the checklist end-to-end" is not evidenced for 1.5.5 / 1.79 ❔.

- `release_gate.sh` run on a healthy workspace → PASS, exit 0; with one deliberately broken test in any repo → BLOCKED, exit 1, and the failing repo is obvious from output.
- The policy text (§6.2) and checklist (§6.3) are copied into `docs/testing.md` (API) and referenced from the other repos' testing docs.
- One real release has used the checklist end-to-end.

## Phase 6 checklist

**Status (2026-10-01):** 4 ✅, 1 🟡, 1 ⏸ — marks at the end of each line.

- [x] `dzzlo_oms_api/scripts/release_gate.sh` executable (+ `scripts/check_fixtures_fresh.js`) — _committing is the user's call_ — **2026-10-01:** ✅ (the freshness check covers v4 since PR #39).
- [x] Policy §6.2 adopted verbatim in `docs/testing.md` §9 (team ack still ⏳ Q10) — **2026-10-01:** ✅.
- [x] Release checklist template in `docs/testing.md` §9 — _physical home per release still pending Q8 release-cut mechanics_ — **2026-10-01:** ✅ template; its home per release is still Q8.
- [x] E2E decision recorded (Q6) — **explicitly deferred**; checklist keeps a marked `e2e smoke … when adopted` slot; Maestro-preferred design in §6.4 — **2026-10-01:** ⏸ still deferred.
- [x] CI workflows added per repo (`.github/workflows/test.yml` ×3) with mongod binary cache — **2026-10-01:** ✅ API and app (dip-web not assessed); gaps are `X-CI-1` / `X-CI-2` in tasks_02.
- [x] First gated release completed — the §6.6 gate run below **is** the demonstration — **2026-10-01:** 🟡 the 2026-07-10 demonstration only; no gate run is recorded on the 1.5.5 / 1.79 release commits ❔.

## Phase 6 — implementation notes (executed 2026-07-10, agent team)

**Result — the gate is GREEN and proven both ways:**

```
✅ fixtures fresh
✅ api (seed → jest → uproot)     668 passed (via yarn test:full = fresh seed)
✅ web (vitest)                   32 passed
✅ app (jest)                     337 passed
RELEASE GATE: PASS   (exit 0)
```

BLOCKED path also proven: a throwaway failing test in one repo → that repo `❌`, `RELEASE GATE: BLOCKED`, exit 1, offending repo obvious (throwaway removed after).

**What Phase 6 delivered:**

- `scripts/release_gate.sh` — the §6.1 design, deliberately dumb (no parallelism/skipping, full output), runnable from any cwd. Gate order: **fixtures-fresh (fast fail) → api `test:full` → web `test` → app `test`**.
- `scripts/check_fixtures_fresh.js` — Phase-5-aware provenance gate: compares each front-end's `generated/fixtures.meta.json` `gitSha`+`seedSnapshot` against the API's `fixtures/api_v3/fixtures.meta.json`; fails with a `run yarn fixtures:pull in <repo>` message if a front-end is behind; tolerant (skip-with-warning) if fixtures/meta absent.
- `docs/testing.md` §9 — the §6.2 policy verbatim + the §6.3 checklist + how-to.
- Per-repo `.github/workflows/test.yml` (CI, §6.5): mirror dip-web's `lint.yml` idiom (`checkout@v4` → `setup-node@v4 cache:yarn` → `yarn install --frozen-lockfile` → run); triggers `pull_request` + `push` to default branch (API `master`, web/app `main`); Node 22 (web 20 to match its lint.yml). **API job caches `~/.cache/mongodb-binaries`** keyed on the pinned `8.2.1`.

**Critical fix Phase 6 forced (see tasks_08… no — see Phase 5 §Correction):** the healthy gate was initially **BLOCKED**, because `test:full` re-seeds and the Phase 5 contract spec had pinned non-deterministic ObjectIds / `inv_no`. That was a _real_ Phase 5 latent bug (green under `yarn test`, red under `test:full`) — fixed in `test/api_v3/features/contract/fixtures.test.js` by scrubbing ObjectIds + `inv_no` and comparing lists order-insensitively; drift teeth re-verified. Only after that fix does the gate reach PASS. **Takeaway now baked into the policy: the gate (`test:full`), not `yarn test`, is what certifies the API.**

**Still open (correctly deferred):** full cross-repo CI orchestration + where the release checklist physically lives both wait on the **release-cut mechanics (Q8)** — how `vN_NN → vN_(NN+1)` is actually cut, who tags, when. The local gate is the release ritual regardless; CI proves PRs.
