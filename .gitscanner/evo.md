# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

# 🚀 GitScanner Evo: Add Export Options and Submodule Support

- **Export Options**: Added `--export-json` and `--export-csv` options to the CLI to facilitate integration into CI/CD pipelines and developer scripts.
- **Submodule Detection**: Updated `find_git_repos` traversal logic to handle Git submodules, where `.git` is represented as a file containing a reference to the actual gitdir, rather than a standard directory.
