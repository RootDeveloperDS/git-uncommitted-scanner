# GitScanner Evo Journal

## Upgrade: Enhanced Status Details
**Date:** $(date)

### Learnings & Architectural Decisions:
- **CLI Table Enhancement:** The standard view was simply outputting paths of dirty repositories, which gave zero context on *why* they were dirty. By incorporating `git status --porcelain` and parsing the untracked/modified files count along with fetching the branch via `git rev-parse --abbrev-ref HEAD`, the user can instantly gauge the severity or context of the dirty repo without needing to enter it immediately.
- **TUI Synchronization:** The text user interface logic (`DataTable`) strictly required adjusting column numbers from ID and Path, to include Branch, Modified, and Untracked count. Ensuring the asynchronous background worker parsed this extra data beforehand ensured the UI didn't block during rendering.
- **Design Alignment:** Kept the aesthetic of the TUI untouched while integrating the newly formed string-based counts for rows.
