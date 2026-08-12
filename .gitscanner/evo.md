# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

# 🚀 GitScanner Evo: Advanced Scanning Filters

- **Directory Filtering**: Implemented `--exclude` flag to pass a comma-separated list of directories (e.g. `node_modules`, `build`) to ignore during traversal, preventing unnecessary I/O on deeply nested junk folders.
- **Scan Depth Limits**: Implemented `--max-depth` flag to constrain directory traversal to a maximum structural depth, drastically speeding up execution on large file systems by limiting recursion.
- **Cross-mode Application**: These parameters correctly map to both CLI execution mode and the background Textual worker in TUI mode.