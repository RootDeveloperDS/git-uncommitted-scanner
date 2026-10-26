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

### UX Upgrade - TUI DataTable Auto-Focus
- Discovered that dynamically revealing a DataTable by toggling `display = True` does not automatically grant it keyboard focus, which breaks immediate keyboard navigation (like arrow keys).
- Added explicit `self.call_later(table.focus)` inside `update_table` after a background scan finishes, ensuring to check that the search `Input` is not actively focused first to avoid stealing its focus.

## UX Upgrade: Right-justified numerical columns in TUI DataTable
- **Date**: 2026-10-26
- **Improvement**: Right-justified the "Modified" and "Untracked" columns and cell data in the TUI DataTable.
- **Learning**: Textual's DataTable supports rich formatting natively. To right-justify column headers or cell data, pass a `rich.text.Text` object directly to `add_columns()` or `add_row()`: e.g. `Text('Value', justify='right')`. This improves readability for numerical counts by aligning the digits.
