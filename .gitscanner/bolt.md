# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.

## Lazy Initialization for TUI
- **Bottleneck**: Top-level textual imports and TUI class definition slow down CLI start time.
- **Identification**: Profiling `time python git_scanner/main.py --help` showed ~1.04s latency.
- **Metric**: CLI start time decreased significantly from ~1.04s to ~0.54s.
- **Practical Value**: Faster CLI execution for users not requiring the interactive TUI.
- **Verification**: Ran CLI and headless TUI tests locally, both passed without issue.
