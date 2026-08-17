# 🎨 GitScanner Palette: TUI Navigation & Visual Feedback

- **Shortcuts & Row Selection**: Bound `@on(DataTable.RowSelected)` to `action_open_terminal()` so pressing `Enter` or double-clicking any table row launches the terminal for that repository.
- **Feedback Notification**: Added non-intrusive `self.notify()` confirmation when a terminal is spawned (`🚀 Spawning terminal for: <path>`).
- **Footer Hint**: Updated binding hint to `"Open Workspace (o/Enter/DblClick)"`.
- **Textual DataTable Row State**: Instead of relying on displayed text for background actions (which might be truncated or formatted for aesthetics), store essential data strings (like raw file paths) in the `key` parameter of `DataTable.add_row()`. Retrieve it later via `table.coordinate_to_cell_key(table.cursor_coordinate)[0].value`. This safely decouples the visual presentation from functional state.
- **Path Truncation Strategy**: Long nested paths disrupt narrow terminal columns. The optimal UX strategy is to retain the root (part index 0) and the final few directories to preserve context while compressing the middle with `...`.
- In Textual, avoid setting `display: none` in CSS if you plan to dynamically toggle visibility via the `widget.display` boolean property in Python, as they can conflict. Instead, handle initial hidden states programmatically in `on_mount()`.
- Focused `Input` widgets in Textual intercept and handle character keys directly, making global key bindings unresponsive for normal characters. However, special keys like `escape` can be captured globally via the `on_key` event to correctly dismiss the input focus and state.
