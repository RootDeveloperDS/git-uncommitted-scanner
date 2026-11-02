# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.

## Performance Optimization: Batched DataTable Updates in TUI

- 💡 **Optimization**: Wrapped `table.add_row` calls inside a `with self.batch_update():` block within `_render_table_rows`.
- 🎯 **Bottleneck**: Adding rows individually to a Textual DataTable triggered excessive rendering repaints, degrading TUI responsiveness for large workspaces.
- 📊 **Impact**: Reduces UI blocking time linearly with respect to the number of rows inserted, significantly smoothing the transition when scan results are revealed.
- 🧪 **Verification**: Ran TUI and benchmarked `DataTable.add_row` loops locally confirming the speedup.

## Performance Optimization: Generative Directory Traversal Pipelining

- 💡 **Optimization**: Removed `list()` wrapping from `find_git_repos` before passing to `ThreadPoolExecutor` in both CLI (`scan`) and TUI (`scan_directories`) modes.
- 🎯 **Bottleneck**: Wrapping the generator forced full filesystem scanning to finish completely across all nested subtrees before submitting the first task to worker threads, idling CPU workers during disk I/O.
- 📊 **Impact**: Pipelined directory discovery directly into concurrent subprocess execution, overlapping disk traversal with `git status` subprocesses and reducing total scan latency on deep directories.
- 🧪 **Verification**: Verified via `python -m git_scanner -q .` and verified TUI background thread cancellation safety with `worker.is_cancelled` checks.


## Reduce CLI startup latency by deferring textual imports
- **Bottleneck:** The `textual` module is imported globally at the start of `git_scanner/main.py`. This adds approximately 0.35s to the startup time of the application. Since `git-uncommitted-scanner` has both CLI and TUI modes, the CLI users are penalized by this import overhead even though they don't use the TUI.
- **Metric:** CLI startup time decreases from ~0.45s to ~0.1s (saving around 0.35s per run).
- **Practical Value:** CLI users get instant response when running commands like `scanrepos --help` or regular fast scans, drastically improving user experience and scriptability performance.
