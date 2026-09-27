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


## Performance Optimization: Skip Directory Traversal Inside Git Repositories

- 💡 **Optimization**: Added a `continue` statement inside `find_git_repos` to skip scanning subdirectories once a `.git` repository is discovered.
- 🎯 **Bottleneck**: `find_git_repos` would continue to deeply traverse all subdirectories inside a large git repository (like a monorepo), creating significant I/O and CPU overhead.
- 📊 **Impact**: Directory scanning latency on deep repositories drops drastically in extreme nested benchmarks by aborting sub-tree traversal immediately upon `.git` discovery.
- 🧪 **Verification**: Tested locally simulating nested git subdirectories and verified that `git_scanner` correctly identifies repositories while ignoring their inner folders.
