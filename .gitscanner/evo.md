# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.
## Added Last Commit Age Display
- Extracted relative last commit age and timestamp using 'git log -1' in get_repo_details.
- Updated TUI components and CLI output to display this practical information for evaluating staleness of uncommitted branches.
