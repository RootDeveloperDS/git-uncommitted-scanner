import sys
import subprocess
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label, LoadingIndicator
from textual.binding import Binding
from textual.worker import get_current_worker

# ---------------------------------------------------------
# CORE LOGIC
# ---------------------------------------------------------
def is_repo_dirty(repo_path: Path) -> bool:
    """Checks if a git repo has uncommitted changes."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=repo_path, capture_output=True, text=True, check=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False

def open_external_terminal(path: str) -> None:
    """Cross-platform function to open terminal and execute 'git status'."""
    path_obj = Path(path).resolve()
    
    # ➔ FIX: Using 'cwd=path_obj' forces the terminal to spawn inside the repo natively.
    if sys.platform == "win32":
        subprocess.Popen('start cmd /K "git status"', cwd=path_obj, shell=True)
    elif sys.platform == "darwin":
        # macOS: Use AppleScript to strictly open a new Terminal window with commands
        script = f'''
        osascript -e 'tell application "Terminal" to do script "cd \\"{path_obj}\\" && git status"' -e 'tell application "Terminal" to activate'
        '''
        subprocess.Popen(script, shell=True)
    else:
        terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'alacritty', 'xterm']
        for term in terminals:
            if subprocess.run(['which', term], capture_output=True).returncode == 0:
                if term == 'gnome-terminal':
                    subprocess.Popen([term, '--', 'bash', '-c', 'git status && exec bash'], cwd=path_obj)
                else:
                    subprocess.Popen([term, '-e', 'bash -c "git status && exec bash"'], cwd=path_obj)
                break

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
        Binding("o", "open_terminal", "Open Workspace"),
        Binding("r", "refresh_scan", "Refresh Scan")
    ]

    def __init__(self, target_dir: Path):
        super().__init__()
        self.target_dir = target_dir

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield LoadingIndicator(id="loader")
        yield DataTable(id="repo_table")
        yield Label("INITIALIZING SYSTEM...", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("ID", "Uncommitted Repository Target")
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
        
        for git_dir in self.target_dir.rglob('.git'):
            if worker.is_cancelled: 
                return
            repo_path = git_dir.parent
            if is_repo_dirty(repo_path):
                dirty_repos.append(repo_path)
                
        self.call_from_thread(self.update_table, dirty_repos)

    def update_table(self, repos: list[Path]) -> None:
        table = self.query_one(DataTable)
        loader = self.query_one("#loader", LoadingIndicator)
        status = self.query_one("#status-bar", Label)
        
        table.clear()
        loader.display = False
        table.display = True
        
        if not repos:
            status.update("✅ ALL REPOSITORIES SECURED AND COMMITTED")
            return
            
        status.update(f"⚠️ DETECTED {len(repos)} REPOSITORIES REQUIRING ATTENTION")
        for idx, repo in enumerate(repos, 1):
            table.add_row(str(idx), str(repo))

    def action_open_terminal(self) -> None:
        table = self.query_one(DataTable)
        try:
            # Safely grab the exact string from column index 1 of the highlighted row
            row_index = table.cursor_row
            # ➔ FIX: Ensure the extracted cell is cast to a standard string
            repo_path = str(table.get_row_at(row_index)[1])
            open_external_terminal(repo_path)
        except Exception:
            self.notify("ERROR: TARGET A REPOSITORY FIRST", severity="error")

# ---------------------------------------------------------
# CLI & ROUTING
# ---------------------------------------------------------
app = typer.Typer(help="Scan directories for uncommitted Git repositories.")
console = Console()

@app.command()
def scan(
    # ➔ FIX: Default to "." (current directory) if no argument is provided
    directory: str = typer.Argument(".", help="Target directory to scan (defaults to current directory)"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Launch the interactive TUI")
):
    """Deep scan a directory for uncommitted Git repositories."""
    base_path = Path(directory).expanduser().resolve()
    
    if not base_path.exists() or not base_path.is_dir():
        rprint(f"[bold red]❌ Error:[/bold red] Directory '{base_path}' does not exist.")
        raise typer.Exit(code=1)

    # Route 1: TUI Mode
    if interactive:
        try:
            tui_app = GitScannerTUI(base_path)
            tui_app.run()
            rprint("\n[bold cyan]✅ Workspace Scanner Terminated Successfully.[/bold cyan]\n")
        except Exception as e:
            rprint(f"\n[bold red]❌ CRITICAL TUI ERROR:[/bold red] {e}")
            console.print_exception()
        return

    # Route 2: CLI Mode
    with console.status(f"[bold cyan]Scanning {base_path}...[/bold cyan]", spinner="dots"):
        dirty_repos = [
            git_dir.parent for git_dir in base_path.rglob('.git') 
            if is_repo_dirty(git_dir.parent)
        ]

    if not dirty_repos:
        rprint("[bold green]✅ All repositories are clean and committed![/bold green]")
        return

    table = Table(title="⚠️ Uncommitted Repositories", show_header=True, header_style="bold magenta")
    table.add_column("No.", style="dim", width=4)
    table.add_column("Repository Path", style="cyan")

    for idx, repo in enumerate(dirty_repos, 1):
        table.add_row(str(idx), str(repo))

    console.print(table)

if __name__ == "__main__":
    app()
