# GitScanner Evo Journal

## Enhanced Status Details

**Feature Implemented:**
Added enhanced status details to `git_scanner/main.py`. Both the TUI and CLI output now display additional repository metrics, including:
- **Branch**: The currently active branch (or "HEAD" if detached).
- **Modified**: The count of modified, tracked files.
- **Untracked**: The count of untracked files.

**Architectural Decision:**
Replaced `is_repo_dirty` (which just returned a boolean based on string length) with a new `get_repo_details` function.
`get_repo_details` fetches both `git status --porcelain` and `git branch --show-current`, computing file counts and returning them as a dictionary.

**Rationale:**
Providing more context than just "uncommitted" vs "clean" provides substantial, practical value for developers managing multiple Git repositories. Seeing the current branch alongside the number of modified and untracked files allows a user to quickly prioritize which repositories need immediate attention without having to `cd` into them.
