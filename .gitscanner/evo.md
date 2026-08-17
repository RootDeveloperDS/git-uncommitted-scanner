# 🚀 GitScanner Evo: Enhanced Repository Status Metrics

- **Detailed Status Metrics**: Replaced basic boolean dirty check with `get_repo_details()` to extract active branch (`git branch --show-current`), modified file count, and untracked file count (`git status --porcelain`).
- **TUI & CLI Table Extensions**: Added "Branch", "Modified", and "Untracked" columns to both the Textual TUI `DataTable` and Rich CLI `Table`.
- **Cross-Platform Robustness**: Improved `open_external_terminal` to add robust terminal detection via `shutil.which` and handle fallbacks for Windows (`wt`, `pwsh`, `powershell`, `cmd`), macOS (`iTerm2`, `Terminal`), and Linux (`alacritty`, `kitty`, `gnome-terminal`, `konsole`, `xfce4-terminal`, `terminator`, `tilix`, `xterm`).
