# Hotfix Runbook

A repeatable checklist for shipping a quick hotfix with Claude. Claude **asks for
permission at every step** — confirm or redirect before each action.

> Reference run: PR #26 → release `v1.5.2 (2026-05-19)`.
>
> The whole workflow (issues, branch names, PRs, review, releases) is in
> [GitHub workflow](../github_workflow/00-github-workflow.md). Its §9 covers the case
> where `slave` holds unreleased work, in which case the hotfix goes into `master` instead.

## Inputs to confirm up front

- **Fix branch** — the branch holding the fix commits (e.g. `fix/so-backdate-reprice`).
- **Base branch** — where the PR merges. This repo ships hotfixes into **`slave`**,
  not `master`. Always confirm the base branch explicitly.
- **Version**: **no bump** unless the user asks for one (decided 2026-09-23). If they
  ask, ask which number (X, Y or Z) too; never assume.
- **Tag and release title**: with no bump, tag `hotfix-<short-name>` and title
  `hotfix(<scope>): <short-name> (YYYY-MM-DD)` (e.g. `hotfix-ist-dates` /
  `hotfix(ledger): ist-dates (2026-09-10)`). With a bump, tag `vX.Y.Z` and title
  `vX.Y.Z (YYYY-MM-DD)`. Check the list with `gh release list`.

## Steps

### 1. Commit (test first), bumping the version only if asked

- The regression test goes in first as its own commit (`test(<scope>): … — red`), then
  the fix (`fix(<scope>): … — green`). TDD applies in every repo.
- Only if a bump was asked for: edit `package.json` `"version"` and commit it with the fix:
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
  --title "<type>(<scope>): <summary>" \
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
# no bump (the default)
gh release create hotfix-<short-name> --target slave \
  --title "hotfix(<scope>): <short-name> (YYYY-MM-DD)" \
  --notes "## What's Changed
- ...
Hotfix shipped without a \`package.json\` version bump (stays at X.Y.Z).
Merged via PR #<PR#> into \`slave\`."

# bump asked for
gh release create vX.Y.Z --target slave \
  --title "vX.Y.Z (YYYY-MM-DD)" \
  --notes "## What's Changed
- ...
Merged via PR #<PR#> into \`slave\`."
```

Then fast-forward `master` to `slave` and deploy
([GitHub workflow §8.2 step 7](../github_workflow/00-github-workflow.md)).

If the title needs fixing afterward:

```bash
gh release edit vX.Y.Z --title "vX.Y.Z (YYYY-MM-DD)"
```

## Notes / gotchas

- **Base branch is `slave`, not `master`** for hotfixes — easy to get wrong.
- Release title **must include the date** in `(YYYY-MM-DD)` form to match the
  existing release list; the bare tag (`hotfix-<short-name>` or `vX.Y.Z`) stays without the date.
- When a bump _is_ asked for, put `package.json` in the **same commit** as the fix
  so the version and the release tag stay in sync.
- Run `gh release list` first to copy the exact title convention.
