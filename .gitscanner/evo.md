# GitScanner Evo 🚀 - Learnings

- Evaluated practical product capability to include Git stashes in directory scans.
- Implemented `git rev-list -g refs/stash` logic to accurately count stashes, even when the rest of the working tree is clean.
- Displayed the stash count in TUI and CLI tables and exports, increasing overall tool observability.