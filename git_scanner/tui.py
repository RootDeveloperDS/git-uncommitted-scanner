import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List, Any

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, LoadingIndicator, Input
from textual.binding import Binding
from textual.worker import get_current_worker

from git_scanner.main import find_git_repos, get_repo_details, truncate_path, open_external_terminal

# ---------------------------------------------------------
# TUI IMPLEMENTATION
# ---------------------------------------------------------
class GitScannerTUI(App):
    """High-Tech TUI for navigating repositories."""

    # Premium Neon-Cyan Aesthetic
    CSS = """
    Screen { background: #0a0a0a; }
    Header { background: #002222; color: #00ffff; text-style: bold; }
    Footer { background: #002222; color: #00ffff; }

    DataTable {
        height: 1fr;
        margin: 1 2;
        border: round #00ffff;
        background: #051515;
        color: #e0ffff;
    }
    DataTable > .datatable--header { background: #004444; color: #00ffff; text-style: bold; }
    DataTable > .datatable--cursor { background: #00ffff; color: #000000; text-style: bold; }

    #search-input {
        dock: top;
        margin: 0 2;
        border: round #00ffff;
        background: #051515;
        color: #e0ffff;
        display: none;
    }

    #status-bar {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: #001111;
        color: #00ffff;
        border-top: solid #00ffff;
    }

    LoadingIndicator { color: #00ffff; height: 1fr; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("o", "open_terminal", "Open Workspace (o/Enter/DblClick)"),
        Binding("slash", "toggle_search", "Search/Filter"),
        Binding("s", "toggle_search", "Search/Filter", show=False),
        Binding("escape", "close_search", "Close Search", show=False),
        Binding("r", "refresh_scan", "Refresh Scan")
    ]

    def __init__(
        self,
        target_dir: Path,
        exclude: Optional[List[str]] = None,
        max_depth: Optional[int] = None
    ):
        super().__init__()
        self.target_dir = target_dir
        self.exclude = exclude
        self.max_depth = max_depth
        self.current_repos: List[Dict[str, Any]] = []
        self.sort_column: Optional[int] = None
        self.sort_reverse: bool = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="🔍 Type to filter repositories by path or branch... (Press Esc to close)", id="search-input")
        yield LoadingIndicator(id="loader")
        yield DataTable(id="repo_table")
        yield Label("INITIALIZING SYSTEM...", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.expand = True  # Spreads columns evenly across full screen width
        self.col_keys = table.add_columns("ID", "Uncommitted Repository Target", "Branch", "Modified", "Untracked", "Last Commit")
        self.action_refresh_scan()

    def action_refresh_scan(self) -> None:
        """Triggers the UI loading state and starts the background worker."""
        table = self.query_one(DataTable)
        loader = self.query_one("#loader", LoadingIndicator)

        table.display = False
        loader.display = True
        self.query_one("#status-bar", Label).update(f"⏳ SCANNING DIRECTORY: {self.target_dir}")

        self.run_worker(self.scan_directories, thread=True, exclusive=True)

    def scan_directories(self) -> None:
        worker = get_current_worker()
        dirty_repos = []

        repos = list(find_git_repos(self.target_dir, exclude=self.exclude, max_depth=self.max_depth))
        if worker.is_cancelled:
            return

        executor = ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 4) * 4))
        try:
            futures = [executor.submit(get_repo_details, repo_path) for repo_path in repos]
            for future in as_completed(futures):
                if worker.is_cancelled:
                    return
                details = future.result()
                if details:
                    dirty_repos.append(details)
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        self.call_from_thread(self.update_table, dirty_repos)

    def _render_table_rows(self, repos_to_render: List[Dict[str, Any]]) -> None:
        table = self.query_one(DataTable)
        table.clear()

        # Sort the data model accurately before rendering rows
        sorted_repos = list(repos_to_render)
        if self.sort_column is not None:
            if self.sort_column == 0:  # ID
                pass
            elif self.sort_column == 1:  # Path
                sorted_repos.sort(key=lambda r: str(r['path']).lower(), reverse=self.sort_reverse)
            elif self.sort_column == 2:  # Branch
                sorted_repos.sort(key=lambda r: str(r['branch']).lower(), reverse=self.sort_reverse)
            elif self.sort_column == 3:  # Modified
                sorted_repos.sort(key=lambda r: r.get('modified', 0), reverse=self.sort_reverse)
            elif self.sort_column == 4:  # Untracked
                sorted_repos.sort(key=lambda r: r.get('untracked', 0), reverse=self.sort_reverse)
            elif self.sort_column == 5:  # Last Commit (Chronological by epoch timestamp)
                sorted_repos.sort(key=lambda r: r.get('last_commit_timestamp', 0), reverse=self.sort_reverse)

        # Calculate dynamic max path length based on current screen width with a min floor of 20 chars
        screen_width = self.size.width if self.size and self.size.width > 0 else 100
        dynamic_max_len = max(20, screen_width - 55)

        for idx, repo in enumerate(sorted_repos, 1):
            table.add_row(
                str(idx),
                truncate_path(repo['path'], max_length=dynamic_max_len, min_length=20),
                str(repo['branch']),
                str(repo['modified']),
                str(repo['untracked']),
                str(repo.get('last_commit', 'Unknown')),
                key=str(repo['path'])
            )

    def on_resize(self, event) -> None:
        """Dynamically re-render table rows when window size changes."""
        if hasattr(self, 'current_repos') and self.current_repos:
            search_input = self.query_one("#search-input", Input)
            search_term = search_input.value.lower() if search_input.display else ""
            if search_term:
                filtered = [
                    repo for repo in self.current_repos
                    if search_term in str(repo['path']).lower() or search_term in str(repo['branch']).lower()
                ]
                self._render_table_rows(filtered)
            else:
                self._render_table_rows(self.current_repos)

    def update_table(self, repos: List[Dict[str, Any]]) -> None:
        self.current_repos = repos
        table = self.query_one(DataTable)
        loader = self.query_one("#loader", LoadingIndicator)
        status = self.query_one("#status-bar", Label)

        loader.display = False
        table.display = True

        if not repos:
            table.clear()
            status.update("✅ ALL REPOSITORIES SECURED AND COMMITTED")
            return

        status.update(f"⚠️ DETECTED {len(repos)} REPOSITORIES REQUIRING ATTENTION")

        # Re-apply active search filter if input is visible
        search_input = self.query_one("#search-input", Input)
        search_term = search_input.value.lower() if search_input.display else ""
        if search_term:
            filtered = [
                repo for repo in self.current_repos
                if search_term in str(repo['path']).lower() or search_term in str(repo['branch']).lower()
            ]
            self._render_table_rows(filtered)
        else:
            self._render_table_rows(repos)

    def action_toggle_search(self) -> None:
        search_input = self.query_one("#search-input", Input)
        if search_input.display:
            self.action_close_search()
        else:
            search_input.display = True
            search_input.focus()

    def action_close_search(self) -> None:
        search_input = self.query_one("#search-input", Input)
        if search_input.display:
            search_input.display = False
            search_input.value = ""
            self.query_one(DataTable).focus()
            self._render_table_rows(self.current_repos)

    def on_key(self, event) -> None:
        """Handle escape key to cancel search and restore focus."""
        if event.key == "escape":
            search_input = self.query_one("#search-input", Input)
            if search_input.display:
                self.action_close_search()
                event.prevent_default()
                event.stop()

    @on(Input.Changed, "#search-input")
    def handle_search_changed(self, event: Input.Changed) -> None:
        search_term = event.value.lower()
        if not search_term:
            filtered = self.current_repos
        else:
            filtered = [
                repo for repo in self.current_repos
                if search_term in str(repo['path']).lower() or search_term in str(repo['branch']).lower()
            ]
        self._render_table_rows(filtered)

    @on(DataTable.HeaderSelected)
    def handle_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Handle clicking column header to toggle sorting."""
        column_index = event.column_index
        col_names = ["ID", "Target", "Branch", "Modified", "Untracked", "Last Commit"]
        col_name = col_names[column_index] if column_index < len(col_names) else f"Column {column_index}"

        if self.sort_column == column_index:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column_index
            # Default to descending (newest/highest first) for timestamps and counts, ascending for text
            self.sort_reverse = True if column_index in (3, 4, 5) else False

        direction = "Descending (▼ - Newest/Highest)" if (self.sort_reverse and column_index in (3, 4, 5)) else ("Descending (▼)" if self.sort_reverse else ("Ascending (▲ - Oldest/Lowest)" if column_index in (3, 4, 5) else "Ascending (▲)"))
        self.notify(f"Sorted by {col_name}: {direction}")

        search_input = self.query_one("#search-input", Input)
        search_term = search_input.value.lower() if search_input.display else ""
        if search_term:
            filtered = [
                repo for repo in self.current_repos
                if search_term in str(repo['path']).lower() or search_term in str(repo['branch']).lower()
            ]
            self._render_table_rows(filtered)
        else:
            self._render_table_rows(self.current_repos)

    def action_open_terminal(self) -> None:
        table = self.query_one(DataTable)
        try:
            # Grab the full path from the row key instead of the displayed string
            repo_path = table.coordinate_to_cell_key(table.cursor_coordinate)[0].value
            open_external_terminal(repo_path)
            self.notify(f"🚀 Spawning terminal for: {repo_path}")
        except Exception:
            self.notify("ERROR: TARGET A REPOSITORY FIRST", severity="error")

    @on(DataTable.RowSelected)
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle Enter key or double click on a row to open the terminal."""
        self.action_open_terminal()
