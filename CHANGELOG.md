# 📜 Changelog

All notable changes to the `git-uncommitted-scanner` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.6] - 2026-08-18

### 🚀 Features (Evo 🚀)
- **Last Commit Age Metric**: Added relative last commit timestamp (`git log -1 --format=%cr`) to CLI output, interactive TUI table, and JSON export to help developers instantly prioritize stale vs recently touched dirty repos.
- **Enhanced Terminal Launcher**: Extended `open_external_terminal()` with `shutil.which` detection supporting Windows Terminal (`wt`), PowerShell 7 (`pwsh`), macOS `iTerm2`, and modern Linux terminals (`alacritty`, `kitty`, `konsole`, `xfce4-terminal`, etc.).

### 🎨 User Experience (Palette 🎨)
- **Search Escape & Keybinding Ergonomics**: Added <kbd>Escape</kbd> key handler to instantly cancel/dismiss search and return table focus. Supported both <kbd>/</kbd> and <kbd>s</kbd> search shortcuts.
- **Native DataTable Sorting**: Stored column keys to utilize Textual's native `DataTable.sort()` ensuring consistent sort direction chevrons (▲/▼).

---

## [0.1.5] - 2026-08-15

### ⚡ Performance (Bolt ⚡)
- **Parallel Git Status Execution**: Integrated `ThreadPoolExecutor` in both CLI and TUI worker threads, executing `git status` subprocesses in parallel (2x–4x scan speedup on multi-repository projects).

### 🚀 Features (Evo 🚀)
- **Configuration File Support**: Added automatic configuration parsing from `~/.gitscannerrc`, `.gitscannerrc`, and `pyproject.toml` (`[tool.gitscanner]`) to define default `exclude` folders and `max_depth`.

### 🎨 User Experience (Palette 🎨)
- **Interactive Column Sorting**: Implemented `@on(DataTable.HeaderSelected)` to allow clicking any column header (ID, Path, Branch, Modified, Untracked) in the TUI to toggle ascending (▲) and descending (▼) sort order with instant feedback.

---

## [0.1.4] - 2026-08-12

### ⚡ Performance (Bolt ⚡)
- **Single Subprocess Status Parsing**: Refactored status check to use `git status --porcelain -b`. Retrieves branch name, modified file count, and untracked file count in a single subprocess call, cutting git execution overhead by 50%.
- **`os.scandir` Traversal Pruning**: High-speed directory scanner automatically skips heavy folders (`node_modules`, `.venv`, `build`, `dist`, `.tox`, etc.) without entering `.git` directories.

### 🚀 Features (Evo 🚀)
- **Advanced Path Filtering**: Added `--max-depth` (`-d`) to limit search depth and `--exclude` (`-e`) for custom folder exclusions across CLI and TUI modes.
- **Git Submodule Support**: Added detection for `.git` files (submodules) alongside `.git` directories.
- **JSON Data Export**: Added `--export <path.json>` flag to save scan results to structured JSON format.

### 🎨 User Experience (Palette 🎨)
- **TUI Ergonomics**: Added <kbd>Enter</kbd> key and double-click row selection (`@on(DataTable.RowSelected)`) to launch native terminals directly from the TUI.
- **Visual Feedback**: Added non-intrusive toast notifications when spawning terminals and automatic path truncation for long workspace directories.
- **Cross-Platform Fixes**: Reconfigured UTF-8 console output to prevent legacy Windows `cmd.exe` codepage encoding crashes.

---

## [0.1.3] - 2026-08-07

### 🚀 Added
- **AI Agent Operating Rules & Guidelines**: Created [`AGENTS.md`](AGENTS.md) defining strict contribution standards, performance policies, empirical verification rules, and mandatory PR structures (Executive Summary, Impact & Safety Matrix, Verification).
- **Scheduled Agent Prompt Suite**: Tailored three dedicated autonomous agent personas for the project:
  - ⚡ **GitScanner Bolt**: Performance, directory scan, and thread optimizer ([`prompt-bolt.md`](prompt-bolt.md)).
  - 🚀 **GitScanner Evo**: Feature evolution, CLI options, and cross-platform capability engineer ([`prompt-evo.md`](prompt-evo.md)).
  - 🎨 **GitScanner Palette**: Textual TUI & CLI UX evolution engineer ([`prompt-pallete.md`](prompt-pallete.md)).
- **Automated PR Review Integration**: Created [`.coderabbit.yaml`](.coderabbit.yaml) for assertive CodeRabbit AI code reviews.
- **Dedicated Agent Branching**: Established the `Dev2Auto` branch as the target branch for automated agent PRs and feature submissions.

### ⚡ Changed
- **Packaging & CI/CD Docs**: Updated package setup references and GitHub Actions PyPI deployment documentation for automated OIDC publishing on GitHub releases.

---

## [0.1.0] - Initial Release

### 🚀 Added
- Asynchronous deep directory scanner using Python standard `subprocess` and `pathlib.Path`.
- Standard CLI table output powered by `Typer` and `Rich`.
- Interactive Neon-Cyan Terminal User Interface (TUI) powered by `Textual`.
- Cross-platform native terminal spawning (`cmd`, `osascript`, `gnome-terminal`, `konsole`, `alacritty`, `xterm`).
- Registered global CLI command `scanrepos`.
