# 🎨 GitScanner Palette: TUI Navigation & Visual Feedback

- **Shortcuts & Row Selection**: Bound `@on(DataTable.RowSelected)` to `action_open_terminal()` so pressing `Enter` or double-clicking any table row launches the terminal for that repository.
- **Feedback Notification**: Added non-intrusive `self.notify()` confirmation when a terminal is spawned (`🚀 Spawning terminal for: <path>`).
- **Footer Hint**: Updated binding hint to `"Open Workspace (o/Enter/DblClick)"`.
- **Textual DataTable Row State**: Instead of relying on displayed text for background actions (which might be truncated or formatted for aesthetics), store essential data strings (like raw file paths) in the `key` parameter of `DataTable.add_row()`. Retrieve it later via `table.coordinate_to_cell_key(table.cursor_coordinate)[0].value`. This safely decouples the visual presentation from functional state.
- **Path Truncation Strategy**: Long nested paths disrupt narrow terminal columns. The optimal UX strategy is to retain the root (part index 0) and the final few directories to preserve context while compressing the middle with `...`.

### UX Upgrade - TUI Search Toggle Input Binding

- Changed the toggle search binding from `slash` to `s` for a more ergonomic UX.
- Implemented `escape` to close the search overlay explicitly instead of requiring toggle with `s` (avoiding issues typing `s` inside the search bar).
- Discovered and accounted for Textual behavior where an `Input` consumes app-level key bindings if focused, enabling users to type "s" within the search input safely.
### UX Upgrade - TUI Dynamic Status Feedback & Default Focus

- **Visual Feedback for States**: Refined the `#status-bar` by defining distinct `.warning` and `.success` CSS classes to clearly differentiate between "repositories found" (warning, orange) and "all clean" (success, green).
- **Class Management vs Display None**: Utilized `widget.add_class()` and `widget.remove_class()` in `update_table` to toggle the stylistic state dynamically without modifying static inline styles. Also avoided using `display: none` in CSS for widgets that might be dynamically toggled via `widget.display` in Python. For instance, `#search-input` is now hidden natively during `on_mount` instead of CSS `display: none`.
- **Keyboard Navigation & Defaults**: Enhanced the focus lifecycle. `DataTable` now explicitly receives focus in `on_mount` so keyboard navigation (arrow keys) works immediately after launch without requiring a mouse click. Focus is also restored back to the `DataTable` dynamically via `update_table` when background refreshes clear and reload rows, provided the search input isn't currently active.
