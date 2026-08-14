# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

## Configuration Support Upgrade
- Added configuration support reading from ~/.gitscannerrc, pyproject.toml, and .gitscannerrc.
- Used a minimal TOML parser to avoid adding 3rd party dependencies.
