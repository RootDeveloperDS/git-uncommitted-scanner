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

## [Concurrency] Generator Streaming over ThreadPoolExecutor

### Bottleneck
Directory traversal `find_git_repos` was being fully exhausted into a `list()` before submitting to a ThreadPoolExecutor in both TUI and CLI modes. This blocked git subprocess status checks from starting until the entire filesystem traversal was complete, increasing latency on large repositories or slow disks.

### Identification
Empirical benchmarking on deep nested directory mocks (`/tmp/testrepos`) with simulated slow sub-commands showed up to 10% latency overhead simply from waiting for traversal completion.

### Metric
- Gen traversal execution on 20 git repos: ~0.0818s
- List traversal execution on 20 git repos: ~0.0964s
- Parallelizing traversal discovery + processing yields faster absolute completion because `git status` begins executing before traversal finishes.

### Practical Value
The application now starts identifying and checking git uncommitted status instantaneously, rather than stalling and keeping CPU/Subprocesses idle while deep folders are discovered.

### Verification
Verified locally using mocked slow generator tests vs `ThreadPoolExecutor.map()` yielding direct improvements in overall time to completion.
