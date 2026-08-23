# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.

## CLI Startup Latency Optimization
- **Bottleneck**: The CLI took ~0.53s to start up because `textual` and its dependencies were imported globally, even when only running the CLI mode.
- **Identification**: Measured using `python -c "import time; t0 = time.time(); import git_scanner.main; print(time.time() - t0)"`.
- **Metric**: Import time dropped from ~0.53s to ~0.23s (a ~56% reduction).
- **Practical Value**: Faster responsiveness when users run `scanrepos` in CLI mode.
- **Verification**: Verified using the benchmark command and running both CLI and TUI modes.
