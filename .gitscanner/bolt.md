# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.

## YYYY-MM-DD: Separating TUI dependencies for CLI latency
- **Bottleneck**: The main CLI script (`git_scanner/main.py`) imported `textual` globally, adding substantial overhead to start time in regular CLI mode, even when not invoking the TUI.
- **Identification**: Execution latency measurement (`python -c "import time; t0 = time.time(); import git_scanner.main; print(time.time() - t0)"`) showed ~0.6s import time.
- **Metric**: CLI startup/import latency reduced from ~0.60s to ~0.16s (a ~73% improvement).
- **Practical Value**: CLI commands will feel significantly snappier to launch for standard scans.
- **Verification**: Verified using `py_compile` checks, timing script, and running CLI runner validation script.
