# GitScanner Palette Learnings Journal

## Keyboard Interaction & Visual Feedback (TUI)

- **Intuitive Shortcuts:** Implementing `on_data_table_row_selected` for DataTables in Textual enables natural user behavior, allowing users to trigger default actions using the `Enter` key or a double-click, augmenting single-key shortcuts (like `o`) and significantly improving navigation ergonomics.
- **Visual Feedback:** Utilizing `self.notify()` provides non-disruptive, immediate visual confirmation (e.g., successful terminal launch), reducing user ambiguity without cluttering the main UI components.
