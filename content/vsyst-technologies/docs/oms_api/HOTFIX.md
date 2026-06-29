# Hotfix Runbook

A repeatable checklist for shipping a quick hotfix with Claude. Claude **asks for
permission at every step** — confirm or redirect before each action.

> Reference run: PR #26 → release `v1.5.2 (2026-05-19)`.

## Inputs to confirm up front

- **Fix branch** — the branch holding the fix commits (e.g. `fix/so-backdate-reprice`).
- **Base branch** — where the PR merges. This repo ships hotfixes into **`slave`**,
  not `master`. Always confirm the base branch explicitly.
- **Version** — next semver patch bump (e.g. `1.5.1` → `1.5.2`).
- **Release title format** — `vX.Y.Z (YYYY-MM-DD)` (matches existing releases; check
  with `gh release list`).

## Steps

### 1. Bump version + commit

- Edit `package.json` `"version"` to the new patch version.
- Stage the fix changes (and any new tests) + `package.json`.
- Commit, e.g.:
  ```bash
  git add <changed files> package.json
  git commit -m "<type>(<scope>): <summary>; bump vX.Y.Z"
  ```

### 2. Push the fix branch

```bash
git push origin <fix-branch>
```

### 3. Create the PR into the base branch

Confirm the base branch (**`slave`** for hotfixes) before running:

```bash
gh pr create --base slave --head <fix-branch> \
  --title "<type>(<scope>): <summary> + vX.Y.Z" \
  --body "## Changes
- ...
## Commits
- <sha> <message>"
```

### 4. Merge the PR

Default to a **merge commit** (matches prior PR history):

```bash
gh pr merge <PR#> --merge
```

Verify: `gh pr view <PR#> --json state,mergedAt`.

### 5. Create the GitHub release

Tag on the **base branch** (`slave`), title with date:

```bash
gh release create vX.Y.Z --target slave \
  --title "vX.Y.Z (YYYY-MM-DD)" \
  --notes "## What's Changed
- ...
Merged via PR #<PR#> into \`slave\`."
```

If the title needs fixing afterward:

```bash
gh release edit vX.Y.Z --title "vX.Y.Z (YYYY-MM-DD)"
```

## Notes / gotchas

- **Base branch is `slave`, not `master`** for hotfixes — easy to get wrong.
- Release title **must include the date** in `(YYYY-MM-DD)` form to match the
  existing release list; the bare tag (`vX.Y.Z`) stays without the date.
- Bump `package.json` in the **same commit** as the fix/tests so the version and
  the release tag stay in sync.
- Run `gh release list` first to copy the exact title convention.
