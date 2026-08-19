# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.

## 2026-08-19 - Added CSV Export Capability
Added support for exporting scan results to CSV format based on the file extension. This provides practical utility for users who want to integrate scan results into spreadsheets or other reporting tools. Implemented using standard library `csv` to maintain zero dependencies bloat.
