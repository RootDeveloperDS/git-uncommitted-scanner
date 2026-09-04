# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

## CSV Export Implementation
- Upgraded CLI to support exporting scan results directly to CSV in addition to JSON based on file extension. This enables users to easily feed their repo scanning outcomes into developer reporting scripts or spreadsheets.

## Enhanced Upstream Sync Status
- **Ahead/Behind Counts**: Enhanced branch name extraction in `get_repo_details()` to parse ahead and behind upstream commit counts from `git status --porcelain -b`.
- **Visual Indicators**: The branch name now displays visual indicators `[↑X ↓Y]` directly in the TUI and CLI `Table` for repositories that are out of sync with their upstream counterparts, providing immediate actionable insights on push/pull requirements.

## Quiet Mode for Scripting
- **Piping & Automation**: Added a `--quiet` (`-q`) flag to the CLI `scan` command. This suppresses all rich UI elements (spinners, tables, success messages) and outputs only raw repository paths, allowing seamless piping into other tools (e.g., `xargs`).
