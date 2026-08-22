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
## Dynamic Status Bar Styling (2026-08-22)

**UX Improvement:** Added dynamic CSS classes (`status-success` and `status-warning`) to the status bar in the Textual TUI (`GitScannerTUI`).
**Usability Problem Solved:** The status bar now changes its background color and border to provide immediate visual feedback. It turns green when no uncommitted repositories are found, and orange/warning color when there are repositories requiring attention. This greatly enhances visual clarity and improves the overall responsiveness of the terminal app.
**Learnings:** In Textual TUIs, dynamic styling of widgets (like the status bar) should be achieved by defining CSS classes (e.g., `.status-success`, `.status-warning`) and dynamically toggling them using `widget.add_class()` and `widget.remove_class()` in Python, rather than explicitly hardcoding style properties.
