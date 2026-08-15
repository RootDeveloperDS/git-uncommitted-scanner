# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

### Configuration Support
- Evaluated and implemented a configuration fallback system that manually parses `.gitscannerrc` and `pyproject.toml` files instead of using heavy external libraries (like `tomli`).
- Ensure fallback hierarchy: `~/.gitscannerrc` -> `pyproject.toml` -> `.gitscannerrc`.
