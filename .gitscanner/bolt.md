# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.
## GitScanner Bolt Optimization: Parallelizing Git Status Execution
- **Date**: $(date)
- **Bottleneck**: Sequential `subprocess.run` calls for `git status --porcelain` were causing significant delay, especially when scanning hundreds of repositories.
- **Optimization**: Implemented `concurrent.futures.ThreadPoolExecutor` in both CLI and TUI worker modes to execute `git status` subprocesses in parallel.
- **Impact**:
  - Subprocess mapping over 200 repos (pure map): Decreased from 0.632s to 0.272s.
  - Overall CLI application time (200 repos): Decreased from 1.671s to 1.095s.
- **Notes**: In TUI mode, `ThreadPoolExecutor` was manually instantiated and managed with a `finally: executor.shutdown(wait=False, cancel_futures=True)` block, rather than as a context manager (`with`), to prevent the worker cancellation from blocking during exit.
