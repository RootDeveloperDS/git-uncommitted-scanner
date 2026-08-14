# 🎨 GitScanner Palette: TUI Navigation & Visual Feedback

- **Shortcuts & Row Selection**: Bound `@on(DataTable.RowSelected)` to `action_open_terminal()` so pressing `Enter` or double-clicking any table row launches the terminal for that repository.
- **Feedback Notification**: Added non-intrusive `self.notify()` confirmation when a terminal is spawned (`🚀 Spawning terminal for: <path>`).
- **Footer Hint**: Updated binding hint to `"Open Workspace (o/Enter/DblClick)"`.
- **Textual DataTable Row State**: Instead of relying on displayed text for background actions (which might be truncated or formatted for aesthetics), store essential data strings (like raw file paths) in the `key` parameter of `DataTable.add_row()`. Retrieve it later via `table.coordinate_to_cell_key(table.cursor_coordinate)[0].value`. This safely decouples the visual presentation from functional state.
- **Path Truncation Strategy**: Long nested paths disrupt narrow terminal columns. The optimal UX strategy is to retain the root (part index 0) and the final few directories to preserve context while compressing the middle with `...`.

## UX Upgrade: Interactive TUI Sorting
- **Date:** 2026-08-14
- **Feature:** Added keyboard and header-click sorting to the Textual `DataTable` for the `git-uncommitted-scanner`.
- **Learnings:**
  - To implement Textual sorting on versions >= 0.28, `table.add_columns()` returns `ColumnKey` objects which must be used instead of string column names.
  - Adding an integer sort key via `lambda x: int(x)` correctly sorts string representations of integers for columns like 'ID', 'Modified', and 'Untracked'.
  - Added intuitive keybinding `s` to focus the sorting on the 'Modified' column, a highly useful shortcut for discovering repositories requiring immediate attention.
