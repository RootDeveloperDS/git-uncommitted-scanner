# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

## CSV Export Implementation
- Upgraded CLI to support exporting scan results directly to CSV in addition to JSON based on file extension. This enables users to easily feed their repo scanning outcomes into developer reporting scripts or spreadsheets.

## Enhanced Upstream Sync Status
- **Ahead/Behind Counts**: Enhanced branch name extraction in `get_repo_details()` to parse ahead and behind upstream commit counts from `git status --porcelain -b`.
- **Visual Indicators**: The branch name now displays visual indicators `[↑X ↓Y]` directly in the TUI and CLI `Table` for repositories that are out of sync with their upstream counterparts, providing immediate actionable insights on push/pull requirements.

## Script Automation & Filtering Upgrades
- **Quiet Mode (`--quiet` / `-q`)**: Added a quiet mode flag that bypasses Rich spinners, tables, and banners using `contextlib.nullcontext()`, outputting only raw repository paths one per line for seamless piping into Unix utilities like `xargs`.
- **Untracked File Exclusion (`--exclude-untracked` / `-u`)**: Added a filtering flag to ignore repositories that contain only untracked files (`modified == 0 and untracked > 0`), reducing noise across workspaces with temporary or generated files.
- **Module Execution (`python -m git_scanner`)**: Added `git_scanner/__main__.py` to provide a robust fallback execution path for users whose system PATH does not include Python's user Scripts directory.


### Add Stash Tracking to GitScanner
- 🚀 **Upgrade**: Added stash tracking to GitScanner. It now extracts stash count using `git rev-list -g refs/stash` and displays it.
- 💡 **Practical Value**: Useful for developers keeping track of uncommitted changes and parked work.
