# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

## GitScanner Evo Upgrade
- Added dynamic CSV export support via the `--export` flag.
- Improved the tool's versatility for pipeline and spreadsheet integrations by inferring output format from the file extension.
