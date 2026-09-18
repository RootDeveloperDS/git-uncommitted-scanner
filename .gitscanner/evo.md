# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

## CSV Export Implementation
- Upgraded CLI to support exporting scan results directly to CSV in addition to JSON based on file extension. This enables users to easily feed their repo scanning outcomes into developer reporting scripts or spreadsheets.

## Enhanced Upstream Sync Status
- **Ahead/Behind Counts**: Enhanced branch name extraction in `get_repo_details()` to parse ahead and behind upstream commit counts from `git status --porcelain -b`.
- **Visual Indicators**: The branch name now displays visual indicators `[↑X ↓Y]` directly in the TUI and CLI `Table` for repositories that are out of sync with their upstream counterparts, providing immediate actionable insights on push/pull requirements.

## CLI Automation Support (Quiet Mode)
- **Script Piping Compatibility**: Implemented a `--quiet` (`-q`) flag for the CLI that suppresses all Rich UI visual elements (like progress spinners, status messages, and data tables). When activated, it outputs only the raw directory paths of the uncommitted repositories line by line. This drastically improves scriptability by allowing `git-uncommitted-scanner` to be cleanly piped to commands like `xargs`.
- **Background Integrity**: Ensured that short-circuiting the UI output does not accidentally bypass essential background logic, such as result file generation triggered by the `--export` flag.
