# GitScanner Bolt - Learnings Journal

## Performance Learnings

### 1. Directory Traversal

Using `os.scandir` combined with manual sub-directory recursion provides significant improvements over `os.walk`, largely because `os.scandir` caches directory entry attributes (like `is_dir()`). This avoids extra `stat()` calls and results in an approximate 30% speedup in traversal times in nested structures. Additionally, when searching for `.git`, we must check `entry.name == '.git'` to properly catch submodules where `.git` is a file rather than a directory.

### 2. Subprocess Overhead

Running two subprocesses per repository (`git status` and `git branch`) imposes significant execution overhead. By using a single command `git status --porcelain -b`, we fetch both branch info and modified/untracked files count in a single pass. Parsing this single output eliminates the need for the secondary `subprocess.run` and cuts the subprocess time roughly in half (e.g. from ~0.9s to ~0.45s per 100 calls in synthetic benchmarks).