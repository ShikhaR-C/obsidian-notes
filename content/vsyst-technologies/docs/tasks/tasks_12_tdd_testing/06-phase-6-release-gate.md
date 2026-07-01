# Phase 6 — Release Gate

**Outcome:** one command proves all three projects pass their suites before a release; the policy when it fails is written and non-negotiable (release blocked, bug becomes a failing regression test first); a CI path is defined that reconciles the existing tasks_02 CI plan.
**Effort:** 1–2 dev-days for the local gate + policy; +1–2 for CI workflows (⏳ Q8).

> **TDD lens:** the gate is the whole point of the safety net — it converts "we think nothing broke" into "the regression contract passed on this exact code." It must be boring, fast enough to run without dread, and impossible to half-run.

---

## 6.1 The command — local gate first (⏳ Q8 for CI timing)

Lives in the reference repo (all four checkouts are siblings in the versioned workspace folder, e.g. `v1_78/`):

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

1. **Green gate or no release.** No "just this once," no partial runs, no local diffs on the release commit after the gate ran. If the gate is red, the release date moves, not the bar.
2. **Every gate failure becomes a regression test.** If the failure is a real bug: write/point-to the failing test **in the owning repo** first, fix, re-run the **entire** gate from scratch. If the failure is a flaky/bad test: fixing the test is the release work — flakes are bugs in the safety net.
3. **Bugs found after release** (by a customer or otherwise) enter the same loop: failing regression test → fix → test stays forever. This is the mandatory-TDD rule from Phase 7.
4. **Contract changes** (API response shapes) require `fixtures:export` → `fixtures:pull` → front-end suites green *within the same release* (Phase 5 drift detector enforces the API side).

## 6.3 The release checklist (copy per release into the release notes/PR)

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

Deliberately *not* specified until Q6 is answered. The reserved design if adopted: a `scripts/e2e/` runner that (a) starts a standalone local mongod via `mongodb-memory-server`'s persistent mode, (b) boots the API against it (`NODE_ENV=development`, overridden `DATABASE_URI`), (c) seeds via the existing factories, then (d) runs Playwright (web, ~5 scenarios) and/or Maestro (app, ~3 flows) against it. Strictly local, ≤ 10 minutes, release-gate-only — never in the inner loop. Until then, the gate above ships without e2e and is still a massive upgrade over manual verification.

## 6.5 CI — reconcile with `tasks_02_major/05-cicd-github-actions.md` (⏳ Q8)

That plan already chose GitHub Actions + Jest; dip-web already runs `lint.yml`. The increment here, per repo, once Q8 confirms:

- `dzzlo_oms_api/.github/workflows/test.yml`: `yarn install` → `yarn test:full` on PR + release branches (memory-server downloads its pinned binary in CI — cache `~/.cache/mongodb-binaries`).
- `dip-web/.github/workflows/test.yml`: `yarn test` (mirror of existing lint.yml structure).
- `dzzlo_oms_app/.github/workflows/test.yml`: `yarn test` (pure JS suites — no emulator needed at this depth).

The **local gate script remains the release ritual** even after CI exists (CI proves PRs; the gate proves the exact release combination of the three repos). Full cross-repo CI orchestration is out of scope until the release-cut mechanics (Q8) are known.

## 6.6 Verification — how we know Phase 6 is done

- `release_gate.sh` run on a healthy workspace → PASS, exit 0; with one deliberately broken test in any repo → BLOCKED, exit 1, and the failing repo is obvious from output.
- The policy text (§6.2) and checklist (§6.3) are copied into `docs/testing.md` (API) and referenced from the other repos' testing docs.
- One real release has used the checklist end-to-end.

## Phase 6 checklist

- [ ] `dzzlo_oms_api/scripts/release_gate.sh` committed + executable
- [ ] Policy §6.2 adopted verbatim in `docs/testing.md` (team ack — ⏳ Q10)
- [ ] Release checklist template placed where releases are cut (pending Q8 answer on mechanics)
- [ ] E2E decision recorded (Q6) — slot implemented or explicitly deferred
- [ ] CI workflows added per repo (pending Q8) with mongod binary cache
- [ ] First gated release completed
