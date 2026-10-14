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


## CLI Startup Latency Optimization
- **Optimization**: Encapsulated `textual` imports and the `GitScannerTUI` class inside a factory function (`get_tui_app_class()`).
- **Bottleneck**: The `textual` library was imported at the module level in `git_scanner/main.py`. Because `textual` pulls in `rich`, `markdown-it-py`, and other UI dependencies, executing simple CLI commands like `scanrepos --help` or performing standard non-interactive scans took roughly 0.8-0.9 seconds just to parse imports.
- **Impact**: By deferring the `textual` import until interactive TUI mode is explicitly invoked (via the `-i` flag), CLI startup latency improved drastically. Command execution time for `scanrepos --help` dropped from ~0.88s to ~0.61s. Bare module import (`python -c 'import git_scanner.main'`) improved from ~0.81s to ~0.45s.
- **Verification**: Benchmarked with `time python -c 'import git_scanner.main'` and `time python -m git_scanner --help`. Wrote a headless test script using Textual's test pilot pattern to verify that the deferred TUI mode still initializes correctly and handles data rendering.
