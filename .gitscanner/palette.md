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

### UX Upgrade - TUI DataTable Auto-Focus and Status Styles
- **Auto-Focus DataTable**: Resolved an issue where the Textual DataTable would not receive keyboard focus when dynamically revealed after background scans. This was accomplished by explicitly setting focus during `on_mount` and using `self.call_later(table.focus)` in `update_table()`.
- **Display Toggle Conflict**: Replaced `display: none;` in the CSS for `#search-input` with a programmatic assignment in `on_mount()` to avoid conflict with `Widget.display = True/False` toggling during Textual renders.
- **Dynamic Status Styling**: Enhanced visual feedback by dynamically adding `.success` (green) and `.warning` (orange) CSS classes to the `#status-bar` to clearly indicate when 0 or multiple uncommitted repositories are found.
