# 📜 Changelog

All notable changes to the `git-uncommitted-scanner` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### 🚀 Added
- **JSON Export CLI Flag**: Added `--export-json` option to the main CLI, allowing users to dump uncommitted repository scan results into a valid JSON file.

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
