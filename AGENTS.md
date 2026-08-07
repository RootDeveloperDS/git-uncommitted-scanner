# 🤖 AGENTS.md – Project Guidelines & Rules for Autonomous AI Agents

Welcome to **git-uncommitted-scanner**. This document defines the mandatory guidelines, architectural standards, quality controls, and PR rules that **all AI agents** (including GitScanner Bolt ⚡, GitScanner Evo 🚀, GitScanner Palette 🎨, and standard coding assistants) MUST follow when contributing to this codebase.

---

## 1. Project Overview & Technology Stack

**`git-uncommitted-scanner`** is a high-speed, cross-platform CLI & TUI utility that scans directories recursively to detect Git repositories with pending uncommitted changes.

- **Primary Language**: Python >= 3.9
- **CLI Engine**: `Typer`
- **Console Output & Styling**: `Rich`
- **Interactive TUI**: `Textual`
- **Subprocess & OS Logic**: Standard library `subprocess`, `pathlib.Path`
- **Build Backend**: `setuptools` (PEP 621, pinned `<75.0` in `pyproject.toml`)

---

## 2. Core Code Standards

1. **Single Entry Point**: All application logic, CLI routing, and TUI widgets reside cleanly under `git_scanner/main.py`.
2. **Cross-Platform Compatibility**: Every file operation and terminal invocation must work seamlessly across Windows, macOS, and Linux.
3. **No Unnecessary Dependencies**: Prefer standard library solutions or existing dependencies (`typer`, `rich`, `textual`). Do not add external packages without explicit approval.
4. **Preserve Functionality**: Never modify existing working features, public interfaces, or CLI command signatures without explicit instructions.

---

## 3. Strict "No Fake Progress" Policy

- **Zero-Change Execution**: If an agent run uncovers no practical, high-value performance, feature, or UX improvement, the agent **MUST NOT** modify any files or submit commits/PRs.
- **No Pure Aesthetic Churn**: Never refactor code simply to change formatting, variable names, line spacing, or syntax style unless it delivers measurable, practical utility.
- **Empirical Verification**: All changes must be verified locally by running `scanrepos` or test commands.

---

## 4. Performance Guidelines (GitScanner Bolt ⚡)

- Avoid heavy module imports at the top level if they delay CLI invocation.
- Keep directory walking efficient (`Path.rglob` or `os.scandir`) and minimize `git status` subprocess execution overhead.
- Ensure `Textual` worker threads run heavy directory scans in the background without blocking the UI main thread.

---

## 5. Feature & Product Evolution Guidelines (GitScanner Evo 🚀)

- Focus on practical, working CLI and TUI enhancements (e.g. branch info, uncommitted file counts, exclusion filters, JSON export, config files).
- No stub implementations, fake UI elements, TODO placeholders, or broken workflows.

---

## 6. UX & Design Guidelines (GitScanner Palette 🎨)

- Maintain high visual contrast and modern terminal styling using `Rich` tables and `Textual` components.
- Ensure keyboard shortcuts are clean, intuitive, and properly documented in the TUI footer.
- Provide clear error feedback if external terminal execution fails.

---

## 7. Artifact & Cleanup Rules

- Never commit build artifacts (`dist/`, `build/`, `*.egg-info/`, `__pycache__/`).
- Never commit scratch files, `.patch`, `.log`, or `.tmp` files.
- Keep `.gitscanner/` logs focused on long-term learnings.

---

# 8. PR & Code Generation Rules

When creating a Pull Request or submitting code changes, you MUST structure the PR description with the following sections:

1. **Executive Summary**: 2-3 sentences max explaining WHAT was changed and WHY.

2. **Impact & Safety Matrix**:

| File Changed / Removed | Action | Technical Reason | Post-Removal/Update Impact | Risk Level |
| :--- | :--- | :--- | :--- | :--- |
| `path/to/file` | Modified/Deleted | Why it was changed | What improves or changes | 🟢 Low / 🟡 Med / 🔴 High |

3. **Verification**: State tests run or how you verified this won't break existing IPC/UI threads.

4. **Clean Artifacts**: NEVER commit `.patch`, `.log`, or `.tmp` files.
