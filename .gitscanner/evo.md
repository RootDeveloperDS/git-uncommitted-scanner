# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

## Evolution Upgrade: Configuration Support

Added configuration support to `git-uncommitted-scanner`. The scanner can now read fallbacks for `exclude`, `max_depth`, and `export` from:
1. `~/.gitscannerrc` (JSON)
2. `.gitscannerrc` in the scanned directory (JSON)
3. `pyproject.toml` (`[tool.gitscanner]`)

**Architectural Learnings:**
- When parsing `pyproject.toml`, simple manual string extraction was preferred to avoid introducing an additional dependency like `toml` or `tomli`, adhering to the "No Unnecessary Dependencies" project guideline.
