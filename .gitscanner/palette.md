# 🎨 GitScanner Palette: TUI Navigation & Visual Feedback

- **Shortcuts & Row Selection**: Bound `@on(DataTable.RowSelected)` to `action_open_terminal()` so pressing `Enter` or double-clicking any table row launches the terminal for that repository.
- **Feedback Notification**: Added non-intrusive `self.notify()` confirmation when a terminal is spawned (`🚀 Spawning terminal for: <path>`).
- **Footer Hint**: Updated binding hint to `"Open Workspace (o/Enter/DblClick)"`.
- **Textual DataTable Row State**: Instead of relying on displayed text for background actions (which might be truncated or formatted for aesthetics), store essential data strings (like raw file paths) in the `key` parameter of `DataTable.add_row()`. Retrieve it later via `table.coordinate_to_cell_key(table.cursor_coordinate)[0].value`. This safely decouples the visual presentation from functional state.
- **Path Truncation Strategy**: Long nested paths disrupt narrow terminal columns. The optimal UX strategy is to retain the root (part index 0) and the final few directories to preserve context while compressing the middle with `...`.
- **TUI Sorting with ColumnKey**: In `Textual` versions >= 0.28, `table.sort()` requires `ColumnKey` objects returned by `table.add_columns()`. Added logic to store these keys in `self.col_keys` during `on_mount` and use them in a custom `_apply_sort()` method.
- **Sorting Numeric Data**: When sorting textual rows with string representations of numeric data (like Modified/Untracked file counts), use `key=lambda x: int(x)` in `table.sort()` to ensure proper numerical sorting order rather than lexicographical order.
- **Preserving Sort State on Re-render**: Added logic to call `self._apply_sort()` at the end of `_render_table_rows()` to ensure the table retains the active sort state even when the rows are fully rebuilt (e.g., during search filtering or background data refreshing).
