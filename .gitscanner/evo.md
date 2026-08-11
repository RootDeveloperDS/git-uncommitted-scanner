# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

# 🚀 GitScanner Evo: Export Uncommitted Repositories to JSON

- **JSON Export CLI Flag**: Added `--export-json` option to the main CLI. This allows users to dump the scanning results (which uncommitted repos exist and their metrics) directly to a valid JSON file for integration into developer scripts and reports.
- **Pathlib Serialization Fix**: Ensured the Pathlib file objects are stringified natively so they serialize perfectly to `json.dump()`.
