# 🔍 Git Uncommitted Scanner (`scanrepos`)

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Typer](https://img.shields.io/badge/typer-CLI-black.svg)
![Rich](https://img.shields.io/badge/rich-Terminal-magenta.svg)
![Textual](https://img.shields.io/badge/textual-TUI-cyan.svg)
[![PyPI version](https://badge.fury.io/py/git-uncommitted-scanner.svg)](https://badge.fury.io/py/git-uncommitted-scanner)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**A high-speed, cross-platform CLI & TUI utility that recursively deep-scans your filesystem to instantly locate Git repositories with pending uncommitted changes.**

---

## ⚡ Why `git-uncommitted-scanner`?

Tired of discovering forgotten, uncommitted code changes in scattered workspace folders months later? `git-uncommitted-scanner` recursively hunts down pending changes across your entire filesystem with asynchronous speed, presenting them in either a clean CLI table or a high-tech interactive Terminal User Interface (TUI).

---

## 📦 Installation

Install globally via `pip` (or `pipx` for isolated environment management):

```bash
pip install git-uncommitted-scanner
```

---

## 🚀 Usage

The package installs a global executable command `scanrepos` that runs in two distinct modes:

### 1. Standard CLI Mode
Run a rapid background scan that outputs a styled `Rich` table listing all uncommitted repositories.

```bash
# Scan the current directory
scanrepos

# Scan a specific directory path
scanrepos /path/to/your/projects

# Ignore specific directories (e.g. node_modules, build)
scanrepos /path/to/your/projects --exclude node_modules,build

# Limit the directory scanning depth
scanrepos /path/to/your/projects --max-depth 3
```

### 2. Interactive TUI Mode (`-i`)
Launch the Neon-Cyan Terminal User Interface. Navigate repositories with keyboard arrows and spawn a native shell terminal directly inside the highlighted workspace.

```bash
# Launch TUI in the current directory
scanrepos -i

# Launch TUI for a specific path
scanrepos -i /path/to/your/projects

# Launch TUI with filters
scanrepos -i /path/to/your/projects --exclude node_modules --max-depth 2
```

#### TUI Keyboard Controls:
* <kbd>o</kbd> : Spawn native OS terminal (`cmd`, `Terminal.app`, `gnome-terminal`, `alacritty`, etc.) in the selected repository.
* <kbd>r</kbd> : Trigger an asynchronous re-scan of the target folder.
* <kbd>q</kbd> : Quit the application.

---

## ✨ Key Features

* **Asynchronous Deep Scanning**: Traverses nested folder structures in worker threads without freezing the user interface.
* **Dual Interface**: Choice between concise CLI tabular output and full interactive TUI.
* **High-Tech Neon-Cyan Aesthetics**: Built with customized `Textual` components and `Rich` console formatting.
* **OS-Aware Terminal Launcher**: Select an uncommitted repository in the TUI and instantly launch a native shell running `git status` inside that folder (supports Windows, macOS, and Linux).
* **Zero Dependencies Bloat**: Built purely on Python standard libraries alongside `typer`, `rich`, and `textual`.

---

## 🛠️ Technology Stack

* **Core Engine**: Python `>=3.9`, standard `subprocess`, `pathlib.Path`
* **CLI Routing**: [`Typer`](https://typer.tiangolo.com/)
* **Terminal Formatting**: [`Rich`](https://rich.readthedocs.io/)
* **Interactive TUI**: [`Textual`](https://textual.textualize.io/)
* **Build System**: `setuptools` (PEP 621 compliant)

---

## 🤖 Agent Ecosystem & Developer Guidelines

This repository includes a structured multi-agent automation setup for continuous maintenance:

* [`AGENTS.md`](AGENTS.md) — Mandatory developer & autonomous agent guidelines, zero-fake-progress rules, and PR formatting standards.
* [`prompt-bolt.md`](prompt-bolt.md) — **GitScanner Bolt ⚡** (Performance & scan speed optimizer prompt).
* [`prompt-evo.md`](prompt-evo.md) — **GitScanner Evo 🚀** (Product feature evolution prompt).
* [`prompt-pallete.md`](prompt-pallete.md) — **GitScanner Palette 🎨** (TUI & CLI UX evolution prompt).
* [`.coderabbit.yaml`](.coderabbit.yaml) — Assertive automated PR code review rules.
* **Target PR Branch**: `Dev2Auto`

---

## 📜 Version History & Release Notes

For a complete record of all updates, bug fixes, and feature additions across releases, please refer to the **[`CHANGELOG.md`](CHANGELOG.md)**.

---

Built with ❤️ by [RootDeveloperDS](https://github.com/RootDeveloperDS)
