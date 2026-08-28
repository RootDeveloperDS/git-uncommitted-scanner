# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.
## Batching DataTable Updates
- **Bottleneck**: Sequential row additions to DataTable in TUI.
- **Identification**: Observed multiple layout repaints triggered per added row in GitScannerTUI._render_table_rows.
- **Metric**: Reduced redundant UI render cycles, avoiding performance chokes when rendering large result sets.
- **Practical Value**: Ensures the TUI remains extremely responsive while population completes, enhancing UX.
- **Verification**: Tested row rendering timing with and without batch_update, confirmed via headless textual testing.
