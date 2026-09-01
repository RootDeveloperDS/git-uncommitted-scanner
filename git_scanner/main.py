import sys
import re
import os
import json
import csv
import subprocess
import configparser
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List, Any

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, LoadingIndicator, Input
from textual.binding import Binding
from textual.worker import get_current_worker

# ---------------------------------------------------------
# CORE LOGIC & CONFIGURATION
# ---------------------------------------------------------
def load_config(base_path: Path) -> Dict[str, Any]:
    """Loads configuration options from .gitscannerrc or pyproject.toml."""
    config: Dict[str, Any] = {"exclude": [], "max_depth": None}

    def parse_rc(file_path: Path):
        try:
            parser = configparser.ConfigParser()
            parser.read(file_path, encoding="utf-8")
            section = "gitscanner" if parser.has_section("gitscanner") else (
                "tool.gitscanner" if parser.has_section("tool.gitscanner") else None
            )
            if section:
                if parser.has_option(section, "exclude"):
                    val = parser.get(section, "exclude")
                    config["exclude"].extend([v.strip() for v in val.split(",") if v.strip()])
                if parser.has_option(section, "max_depth"):
                    config["max_depth"] = parser.getint(section, "max_depth")
        except Exception:
            pass

    def parse_pyproject(file_path: Path):
        try:
            content = file_path.read_text(encoding="utf-8")
            in_section = False
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    in_section = (line == "[tool.gitscanner]")
                    continue
                if in_section and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'").strip('"')
                    if key == "exclude":
                        cleaned = val.strip("[]")
                        config["exclude"].extend([v.strip().strip("'").strip('"') for v in cleaned.split(",") if v.strip()])
                    elif key == "max_depth":
                        try:
                            config["max_depth"] = int(val)
                        except ValueError:
                            pass
        except Exception:
            pass

    home_rc = Path.home() / ".gitscannerrc"
    if home_rc.exists():
        parse_rc(home_rc)

    local_pyproject = base_path / "pyproject.toml"
    if local_pyproject.exists():
        parse_pyproject(local_pyproject)

    local_rc = base_path / ".gitscannerrc"
    if local_rc.exists():
        parse_rc(local_rc)

    if config["exclude"]:
        config["exclude"] = list(dict.fromkeys(config["exclude"]))

    return config


def truncate_path(path_obj: Path, max_length: int = 85, min_length: int = 20) -> str:
    """Helper to truncate very long repository paths with ellipses while enforcing a minimum visibility limit."""
    path_str = str(path_obj)
    
    # Ensure max_length never drops below min_length so the path column is never hidden
    effective_max = max(max_length, min_length)

    if len(path_str) <= effective_max:
        return path_str

    parts = path_obj.parts
    if len(parts) > 3:
        # Format as: C:\...\last_folder or /.../last_folder
        truncated = str(Path(parts[0], "...", *parts[-2:]))
        if len(truncated) <= effective_max:
            return truncated

    if len(parts) > 1:
        # Show first part + "..." + end of path
        suffix_len = max(5, effective_max - len(parts[0]) - 4)
        return f"{parts[0]}...\\{path_str[-suffix_len:]}"

    return "..." + path_str[-(effective_max - 3):]


def find_git_repos(
    base_path: Path,
    exclude: Optional[List[str]] = None,
    max_depth: Optional[int] = None
):
    """Optimized directory traversal to find git repositories."""
    ignore_dirs = {
        'node_modules', '.venv', 'venv', 'env', '.env',
        '.tox', 'build', 'dist', 'target', '.idea', '.vscode'
    }
    if exclude:
        ignore_dirs.update(d.strip() for d in exclude if d.strip())

    stack = [(str(base_path), 0)]
    while stack:
        current_path, depth = stack.pop()
        try:
            with os.scandir(current_path) as it:
                subdirs = []
                has_git = False
                for entry in it:
                    if entry.name == '.git':
                        # Explicitly handles both .git directories and .git files (submodules)
                        has_git = True
                    elif entry.is_dir(follow_symlinks=False) and entry.name not in ignore_dirs:
                        subdirs.append(entry.path)

                if has_git:
                    yield Path(current_path)

                if max_depth is None or depth < max_depth:
                    stack.extend((subdir, depth + 1) for subdir in subdirs)
        except (PermissionError, FileNotFoundError):
            continue


def get_repo_details(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Checks if a git repo has uncommitted changes and returns status details including branch and last commit age."""
    try:
        status_result = subprocess.run(
            ['git', 'status', '--porcelain', '-b'],
            cwd=repo_path, capture_output=True, text=True, check=True
        )
        output = status_result.stdout.strip()
        lines = [line for line in output.split('\n') if line]
        if not lines:
            return None

        branch = "HEAD"
        if lines and lines[0].startswith('## '):
            branch_line = lines[0][3:]

            ahead = 0
            behind = 0
            ahead_match = re.search(r'ahead (\d+)', branch_line)
            if ahead_match:
                ahead = int(ahead_match.group(1))
            behind_match = re.search(r'behind (\d+)', branch_line)
            if behind_match:
                behind = int(behind_match.group(1))

            branch = branch_line.split('...')[0].strip()
            if branch.startswith('No commits yet on '):
                branch = branch.replace('No commits yet on ', '')

            display_branch = branch
            status = []
            if ahead > 0:
                status.append(f"↑{ahead}")
            if behind > 0:
                status.append(f"↓{behind}")
            if status:
                display_branch = f"{branch} [{' '.join(status)}]"

            lines = lines[1:]

        if not lines:
            return None

        untracked = sum(1 for line in lines if line.startswith('??'))
        modified = len(lines) - untracked

        last_commit = "Unknown"
        last_commit_timestamp = 0
        try:
            log_result = subprocess.run(
                ['git', 'log', '-1', '--format=%cr%x00%ct'],
                cwd=repo_path, capture_output=True, text=True, check=True
            )
            raw_log = log_result.stdout.strip()
            if raw_log:
                parts = raw_log.split('\x00')
                last_commit = parts[0]
                if len(parts) > 1 and parts[1].isdigit():
                    last_commit_timestamp = int(parts[1])
        except subprocess.CalledProcessError:
            last_commit = "No commits"

        return {
            'path': repo_path,
            'branch': branch,
            'display_branch': display_branch if 'display_branch' in locals() else branch,
            'modified': modified,
            'untracked': untracked,
            'last_commit': last_commit,
            'last_commit_timestamp': last_commit_timestamp
        }
    except Exception:
        return None


def is_repo_dirty(repo_path: Path) -> bool:
    """Checks if a git repo has uncommitted changes."""
    return get_repo_details(repo_path) is not None


def open_external_terminal(path: str) -> None:
    """Cross-platform function to open terminal and execute 'git status'."""
    path_obj = Path(path).resolve()
    
    if sys.platform == "win32":
        if shutil.which("wt"):
            subprocess.Popen(f'wt -d "{path_obj}" cmd /k "git status"', shell=True)
        elif shutil.which("pwsh") or shutil.which("powershell"):
            ps = "pwsh" if shutil.which("pwsh") else "powershell"
            subprocess.Popen(f'start {ps} -NoExit -Command "cd \'{path_obj}\'; git status"', shell=True)
        else:
            subprocess.Popen('start cmd /K "git status"', cwd=path_obj, shell=True)
    elif sys.platform == "darwin":
        script = f'''
        tell application "System Events"
            set isRunning to (exists process "iTerm2")
        end tell
        if isRunning then
            tell application "iTerm2"
                create window with default profile
                tell current session of current window
                    write text "cd \\"{path_obj}\\" && git status"
                end tell
                activate
            end tell
        else
            tell application "Terminal"
                do script "cd \\"{path_obj}\\" && git status"
                activate
            end tell
        end if
        '''
        subprocess.Popen(['osascript', '-e', script])
    else:
        terminals = [
            'alacritty', 'kitty', 'gnome-terminal', 'konsole',
            'xfce4-terminal', 'terminator', 'tilix', 'xterm'
        ]
        for term in terminals:
            if shutil.which(term):
                try:
                    if term == 'gnome-terminal':
                        subprocess.Popen([term, '--', 'bash', '-c', 'git status && exec bash'], cwd=path_obj)
                    elif term in ['alacritty', 'kitty']:
                        subprocess.Popen([term, '-e', 'bash', '-c', 'git status && exec bash'], cwd=path_obj)
                    else:
                        subprocess.Popen([term, '-e', 'bash -c "git status && exec bash"'], cwd=path_obj)
                    break
                except Exception:
                    continue

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


        with self.batch_update():
            for idx, repo in enumerate(sorted_repos, 1):
              table.add_row(
                  str(idx),
                  truncate_path(repo['path'], max_length=dynamic_max_len, min_length=20),
                  str(repo.get('display_branch', repo['branch'])),
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

        if not search_input.has_focus or not search_input.display:
            self.call_later(table.focus)

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

# Ensure UTF-8 output encoding for legacy Windows console compatibility
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------
# CLI & ROUTING
# ---------------------------------------------------------
app = typer.Typer(help="Scan directories for uncommitted Git repositories.")
console = Console()

@app.command()
def scan(
    directory: str = typer.Argument(".", help="Target directory to scan (defaults to current directory)"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Launch the interactive TUI"),
    exclude: Optional[str] = typer.Option(None, "--exclude", "-e", help="Comma-separated list of directory names to exclude"),
    max_depth: Optional[int] = typer.Option(None, "--max-depth", "-d", help="Maximum directory depth to traverse"),
    export: Optional[str] = typer.Option(None, "--export", help="Export scan results to specified file path (.json or .csv)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all rich output and print only raw directory paths")
):
    """Deep scan a directory for uncommitted Git repositories."""
    base_path = Path(directory).expanduser().resolve()
    
    if not base_path.exists() or not base_path.is_dir():
        rprint(f"[bold red]❌ Error:[/bold red] Directory '{base_path}' does not exist.")
        raise typer.Exit(code=1)

    config = load_config(base_path)

    exclude_list = list(config.get("exclude", []))
    if exclude:
        exclude_list.extend([item.strip() for item in exclude.split(',') if item.strip()])
    exclude_list = list(dict.fromkeys(exclude_list)) if exclude_list else None

    final_max_depth = max_depth if max_depth is not None else config.get("max_depth")

    # Route 1: TUI Mode
    if interactive:
        try:
            tui_app = GitScannerTUI(base_path, exclude=exclude_list, max_depth=final_max_depth)
            tui_app.run()
            rprint("\n[bold cyan]✅ Workspace Scanner Terminated Successfully.[/bold cyan]\n")
        except Exception as e:
            rprint(f"\n[bold red]❌ CRITICAL TUI ERROR:[/bold red] {e}")
            console.print_exception()
        return

    # Route 2: CLI Mode
    if quiet:
        repos = list(find_git_repos(base_path, exclude=exclude_list, max_depth=final_max_depth))
        with ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 4) * 4)) as executor:
            results = executor.map(get_repo_details, repos)
            dirty_repos = [r for r in results if r is not None]
    else:
        with console.status(f"[bold cyan]Scanning {base_path}...[/bold cyan]", spinner="dots"):
            repos = list(find_git_repos(base_path, exclude=exclude_list, max_depth=final_max_depth))
            with ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 4) * 4)) as executor:
                results = executor.map(get_repo_details, repos)
                dirty_repos = [r for r in results if r is not None]

    if not dirty_repos:
        if not quiet:
            rprint("[bold green]✅ All repositories are clean and committed![/bold green]")
        return

    if export:
        export_data = [
            {
                "path": str(repo['path']),
                "branch": repo['branch'],
                "modified": repo['modified'],
                "untracked": repo['untracked'],
                "last_commit": repo.get('last_commit', 'Unknown'),
                "last_commit_timestamp": repo.get('last_commit_timestamp', 0)
            }
            for repo in dirty_repos
        ]
        export_file = Path(export)

        if export_file.suffix.lower() == ".csv":
            with open(export_file, mode='w', newline='', encoding='utf-8') as f:
                if export_data:
                    fieldnames = ["path", "branch", "modified", "untracked", "last_commit", "last_commit_timestamp"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(export_data)
                else:
                    f.write("path,branch,modified,untracked,last_commit,last_commit_timestamp\n")
        else:
            export_file.write_text(json.dumps(export_data, indent=2), encoding="utf-8")

        if not quiet:
            rprint(f"[bold green]📄 Exported scan results ({len(dirty_repos)} repos) to {export_file.resolve()}[/bold green]")

    if quiet:
        for repo in dirty_repos:
            print(str(repo['path']))
        return

    table = Table(title="Uncommitted Repositories", show_header=True, header_style="bold magenta")
    table.add_column("No.", style="dim", width=4)
    table.add_column("Repository Path", style="cyan")
    table.add_column("Branch", style="green")
    table.add_column("Modified", style="yellow", justify="right")
    table.add_column("Untracked", style="red", justify="right")
    table.add_column("Last Commit", style="blue")

    for idx, repo in enumerate(dirty_repos, 1):
        table.add_row(
            str(idx),
            str(repo['path']),
            str(repo.get('display_branch', repo['branch'])),
            str(repo['modified']),
            str(repo['untracked']),
            str(repo.get('last_commit', 'Unknown'))
        )

    console.print(table)

if __name__ == "__main__":
    app()

