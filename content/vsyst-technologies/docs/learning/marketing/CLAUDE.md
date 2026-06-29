# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

This directory is a working/scratch area, not a conventional code project. It currently contains:

- `VSYST Technologies Pvt. Ltd./` — an **Obsidian vault** (contains `.obsidian/`) with top-level PARA-style folders (`1_Calendar`, `2_Projects`, `3_Areas`, `4_Resources`, `5_Tags`, `7_Templates`, `8_Media`). **Read-only — see rule below.**
- `try1/`, `try2/`, `try3/`, `try4/` — empty scratch folders for experimentation.
- `README.md` — empty.

There is no build system, package manager, or test suite configured in this directory. Do not invent commands; if the user asks to build/test/run, ask what stack they want to use.

## Rule: `VSYST Technologies Pvt. Ltd./` is read-only

**Never edit, create, move, rename, or delete any file under `VSYST Technologies Pvt. Ltd./`** (including every subfolder and `.obsidian/`). This is the user's authoritative Obsidian vault and must not be mutated by the assistant.

- Allowed: `Read`, `Glob`, `Grep` against that path.
- Forbidden: `Edit`, `Write`, `NotebookEdit`, and any `Bash` command that would create, modify, move, or delete a path under that folder (`rm`, `mv`, `cp` into it, `>` redirects, `touch`, `mkdir`, `sed -i`, `git` operations that rewrite files, etc.).
- If a task appears to require modifying files in the vault, stop and ask the user to either confirm explicitly or copy the content out to an editable location (e.g., one of the `tryN/` folders) first.
