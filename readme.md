# 🔍 Git Uncommitted Scanner

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Typer](https://img.shields.io/badge/typer-CLI-black.svg)
![Textual](https://img.shields.io/badge/textual-TUI-cyan.svg)
[![PyPI version](https://badge.fury.io/py/git-uncommitted-scanner.svg)](https://badge.fury.io/py/git-uncommitted-scanner)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**A lightning-fast, cross-platform utility that recursively deep-scans directories to instantly find Git repositories with uncommitted changes.**

---

## ⚡ Why `git-uncommitted-scanner`?

Tired of discovering forgotten, uncommitted work in scattered repositories months later? `git-uncommitted-scanner` hunts down pending changes across your entire filesystem with asynchronous speed, presenting them in either a clean CLI table or a high-tech interactive TUI. 

---

## 📦 Installation

Install globally via `pip` (or `pipx` for isolated environments):

```bash
pip install git-uncommitted-scanner
```

---

## 🚀 Usage

The tool provides a single command `scanrepos` that works in two modes: standard CLI and interactive TUI.

### Standard CLI Mode
Run a blazing-fast background scan that outputs a clean, readable table of repositories needing your attention.

```bash
# Scan the current directory
scanrepos

# Scan a specific path
scanrepos /path/to/your/projects
```

### Interactive TUI Mode
Launch the high-tech Neon-Cyan Terminal User Interface for an interactive experience. Navigate repositories with your keyboard and spawn a native terminal to instantly handle changes.

```bash
# Launch TUI in the current directory
scanrepos -i

# Launch TUI for a specific path
scanrepos -i /path/to/your/projects
```

---

## ✨ Key Features

*   **Asynchronous Deep-Scanning**: Rapidly traverses deep folder structures in the background without blocking the UI.
*   **Lightning-Fast CLI Output**: Instantly summarizes findings in a clean, easily readable terminal table.
*   **High-Tech Neon-Cyan TUI**: A beautiful, interactive textual interface accessible via a simple `-i` flag.
*   **Keyboard Navigation**: Full keyboard support in the TUI for seamless, mouse-free workflow.
*   **OS-Aware Terminal Spawning**: Select a repository in the TUI and instantly spawn a native terminal (Windows, macOS, or Linux) running `git status` right in that directory.
*   **Cross-Platform**: Built to work flawlessly across Windows, macOS, and Linux environments.

*Built with [Python](https://www.python.org/), [Typer](https://typer.tiangolo.com/), and [Textual](https://textual.textualize.io/).*

---

Built with ❤️ by [RootDeveloperDS](https://github.com/RootDeveloperDS)

