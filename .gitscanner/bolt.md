# GitScanner Bolt - Performance Learnings Journal

## Performance Optimization: Optimized Directory Traversal via `os.scandir`

- 💡 **Optimization**: Replaced `os.walk` with an iterative DFS implementation using `os.scandir` in `git_scanner/main.py`.
- 🎯 **Bottleneck**: `os.walk` was aggressively allocating lists and extracting metadata for deeply nested directories which was unnecessary for just finding `.git` paths.
- 📊 **Impact**: Directory scanning latency improved by ~41% (walk: ~0.222s vs scandir: ~0.129s on generated benchmark). `scandir` reduces memory allocations and only fetches names iteratively rather than all folder info at once.
- 🧪 **Verification**: Tested CLI output by mocking up mock git repositories in `test_env/` (both regular folders and submodules). TUI functionally checked via `pytest-asyncio` with Textual pilot. Script runs successfully.

# Optimization: Subprocess overhead and CLI Startup latency
* Modified `get_repo_details` to use `git status --porcelain -b`. This merges branch retrieval into the single status command, avoiding the secondary subprocess `git branch --show-current`, dropping execution time.
* Deferred imports of `textual` and `rich` from module-level scope to function-level/lazy scope. This avoids executing massive UI frameworks initialization during CLI instantiation and reduced Python module import and startup latency significantly.
