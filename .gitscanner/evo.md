# GitScanner Evo 🚀 Learnings & Upgrades

## Date: 2025-02-14
- **Upgrade**: Added stash detection and display.
- **Value**: Scanning for uncommitted repositories now detects and surfaces repositories with only stashes, preventing loss of work when a working directory is otherwise clean. The stashes count is now displayed in both TUI and CLI outputs, and included in JSON/CSV exports.
- **Details**: Updated `get_repo_details` to check for `refs/stash` using `git rev-list --walk-reflogs --count refs/stash`. Updated TUI, CLI rendering, and export to support this new field. Added custom sorting by stashes for the TUI data table.

## Date: 2025-02-14
- **Upgrade**: Added stash detection and display.
- **Value**: Scanning for uncommitted repositories now detects and surfaces repositories with only stashes, preventing loss of work when a working directory is otherwise clean. The stashes count is now displayed in both TUI and CLI outputs, and included in JSON/CSV exports.
- **Details**: Updated `get_repo_details` to check for `refs/stash` using `git rev-list --walk-reflogs --count refs/stash`. Updated TUI, CLI rendering, and export to support this new field. Added custom sorting by stashes for the TUI data table.
