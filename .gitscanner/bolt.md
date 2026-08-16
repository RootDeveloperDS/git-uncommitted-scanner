# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.

## Optimization: Defer Textual Import
- **Optimization:** Wrapped `textual` imports and `GitScannerTUI` class definition inside `run_tui_app` function.
- **Bottleneck:** `textual` imports took ~0.35s to load globally, slowing down CLI invocation when running `git-uncommitted-scanner` without the TUI flag.
- **Impact:** CLI startup time reduced from ~0.85s to ~0.56s. Memory utilization is also slightly reduced when running purely in CLI mode.
- **Verification:** Verified by running `time python git_scanner/main.py --help` which shows marked improvement. Also ran `python -m py_compile git_scanner/main.py` and `pytest`.
