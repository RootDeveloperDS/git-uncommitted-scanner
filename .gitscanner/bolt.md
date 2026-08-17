# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.

## Optimization: Lazy Load Textual TUI

- **Bottleneck**: The `textual` package and its rich set of dependencies were being imported globally at the top of `git_scanner/main.py`. This caused CLI startup latency for every invocation, even when simply running `--help` or scanning in CLI-only mode.
- **Identification**: Measured by timing `python git_scanner/main.py --help` which initially took around 0.9s.
- **Metric**: Execution time for `--help` decreased from ~0.9s to ~0.68s.
- **Practical Value**: CLI commands are much snappier and responsive, reducing overhead when scripting or integrating with other tools.
- **Verification**: Tested `python git_scanner/main.py --help` for speed and `python git_scanner/main.py -i` for functional regression testing.
