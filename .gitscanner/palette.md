# GitScanner Palette Learnings Journal

## Textual TUI Improvements

### Notifications and Feedback
- Added visual feedback when opening a repository in the terminal using `self.notify()`. This gives the user immediate confirmation that their action (pressing `o`, `Enter`, or double-clicking) was registered and is being processed.

### Event Handling for Row Selection
- Learned and applied `DataTable.RowSelected` events via the `@on(DataTable.RowSelected)` decorator.
- This significantly improves TUI ergonomics by allowing users to double-click or press `Enter` on a row to trigger the same action as the dedicated keyboard shortcut (`o`), adhering to expected native application behavior and reducing friction.
