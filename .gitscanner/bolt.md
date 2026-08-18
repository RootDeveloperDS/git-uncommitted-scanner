# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.

## Optimization: Lazy TUI Imports

**Bottleneck:**
`git-uncommitted-scanner` experienced significant startup latency (~0.9s to >1.5s) primarily due to importing `textual` and building the `GitScannerTUI(App)` class globally, even when only the CLI scanner was requested.

**Metric:**
- **Before:** `time python3 -c 'import git_scanner.main'` took ~0.9s (or ~1.5s when textual was initially downloaded).
- **After:** `time python3 -c 'import git_scanner.main'` takes ~0.45s (a ~50% reduction in import time).
- CLI commands like `git_scanner/main.py --help` are now much snappier.

**Practical Value:**
The core directive for standard CLI interaction is fast execution. Loading bulky terminal UI frameworks only when requested via `-i` ensures a significantly faster experience for users executing the tool as a quick one-shot command or in automated bash aliases.

**Verification:**
Verified via `pytest`, `python3 git_scanner/main.py`, and testing interactive module readiness. Functionality remains identical with lower overhead.
