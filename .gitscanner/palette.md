# 🎨 GitScanner Palette: TUI Navigation & Visual Feedback

- **Shortcuts & Row Selection**: Bound `@on(DataTable.RowSelected)` to `action_open_terminal()` so pressing `Enter` or double-clicking any table row launches the terminal for that repository.
- **Feedback Notification**: Added non-intrusive `self.notify()` confirmation when a terminal is spawned (`🚀 Spawning terminal for: <path>`).
- **Footer Hint**: Updated binding hint to `"Open Workspace (o/Enter/DblClick)"`.
- **Textual DataTable Row State**: Instead of relying on displayed text for background actions (which might be truncated or formatted for aesthetics), store essential data strings (like raw file paths) in the `key` parameter of `DataTable.add_row()`. Retrieve it later via `table.coordinate_to_cell_key(table.cursor_coordinate)[0].value`. This safely decouples the visual presentation from functional state.
- **Path Truncation Strategy**: Long nested paths disrupt narrow terminal columns. The optimal UX strategy is to retain the root (part index 0) and the final few directories to preserve context while compressing the middle with `...`.

### TUI Table Sorting (Textual >= 0.28)
- Implementing sorting on `DataTable` requires storing the `ColumnKey` objects returned by `table.add_columns()`.
- Added support for interactive header clicking via `@on(DataTable.HeaderSelected)` and a dedicated keybinding (`s`) to cycle through common sort states (Modified -> Untracked -> Default).
- Implemented robust sorting keys that attempt `float()` first, falling back to `str().lower()` to handle numeric counts cleanly in tables.
- Sorting application (`table.sort()`) must be re-applied after clearing and redrawing rows, such as during search filtering.
