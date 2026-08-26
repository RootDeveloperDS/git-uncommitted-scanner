# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.

## Performance Optimization: Isolated TUI Dependencies

- 💡 **Optimization**: Isolated TUI dependencies (`textual`) by extracting `GitScannerTUI` and its related logic from `git_scanner/main.py` into `git_scanner/tui.py` and implementing a dynamic import in CLI mode.
- 🎯 **Bottleneck**: CLI Startup Latency and Import Overhead. Import of `textual` (and `rich`, etc.) modules takes significant time when the user just wants to run the non-interactive CLI version of `git-uncommitted-scanner`.
- 📊 **Impact**: CLI startup time improved dramatically. Import of `git_scanner.main` reduced from ~0.51s to ~0.14s on benchmark script.
- 🧪 **Verification**: Ran `python -c "import time; t0 = time.time(); import git_scanner.main; print(time.time() - t0)"` before and after. Verified TUI mode functions using `pytest-asyncio` headless test.
