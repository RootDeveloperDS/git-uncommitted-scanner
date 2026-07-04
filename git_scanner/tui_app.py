import sys
import subprocess
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label
from textual.binding import Binding
from textual.worker import Worker, get_current_worker

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
    """Cross-platform function to open a new terminal window at the specified path."""
    if sys.platform == "win32":
        # Opens a new CMD window and changes directory
        subprocess.Popen(['start', 'cmd', '/K', f'cd /d "{path}"'], shell=True)
    elif sys.platform == "darwin":
        # Opens macOS Terminal at path
        subprocess.Popen(['open', '-a', 'Terminal', path])
    else:
        # Linux: Attempts to find and launch standard terminal emulators
        terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'alacritty', 'xterm']
        for term in terminals:
            if subprocess.run(['which', term], capture_output=True).returncode == 0:
                if term == 'gnome-terminal':
                    subprocess.Popen([term, '--working-directory', path])
                else:
                    subprocess.Popen([term, '-e', f'bash -c "cd \\"{path}\\" && exec bash"'])
                break

class GitScannerTUI(App):
    """A Textual TUI to scan and navigate uncommitted Git repositories."""
    
    CSS = """
    DataTable {
        height: 100%;
        margin: 1;
        border: solid cyan;
    }
    #status {
        content-align: center middle;
        width: 100%;
        color: yellow;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("o", "open_terminal", "Open in Terminal (Requires selection)"),
        Binding("r", "refresh_scan", "Refresh Scan")
    ]

    def __init__(self, target_dir: str):
        super().__init__()
        self.target_dir = Path(target_dir).expanduser().resolve()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Press 'r' to scan. Use Arrow Keys to navigate. Press 'o' to open repo.", id="status")
        yield DataTable(id="repo_table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("No.", "Uncommitted Repository Path")
        self.action_refresh_scan()

    def action_refresh_scan(self) -> None:
        """Triggers the async scanning worker."""
        table = self.query_one(DataTable)
        table.clear()
        status = self.query_one("#status", Label)
        status.update(f"⏳ Scanning {self.target_dir} for repositories...")
        self.run_worker(self.scan_directories(), exclusive=True)

    async def scan_directories(self) -> None:
        """Runs the I/O blocking scan in a background thread to keep UI responsive."""
        worker = get_current_worker()
        dirty_repos = []
        
        # Scan filesystem
        for git_dir in self.target_dir.rglob('.git'):
            if worker.is_cancelled:
                return
            repo_path = git_dir.parent
            if is_repo_dirty(repo_path):
                dirty_repos.append(repo_path)
                
        # Update UI thread safely
        self.call_from_thread(self.update_table, dirty_repos)

    def update_table(self, repos: list[Path]) -> None:
        """Populates the DataTable with found repositories."""
        table = self.query_one(DataTable)
        status = self.query_one("#status", Label)
        
        if not repos:
            status.update("✅ All repositories are clean and committed!")
            return
            
        status.update(f"⚠️ Found {len(repos)} repositories with uncommitted changes.")
        for idx, repo in enumerate(repos, 1):
            table.add_row(str(idx), str(repo), key=str(repo))

    def action_open_terminal(self) -> None:
        """Opens the selected repository in a new OS terminal window."""
        table = self.query_one(DataTable)
        try:
            # Get the path from the currently highlighted row's key
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            repo_path = row_key.value
            open_external_terminal(repo_path)
        except Exception:
            self.notify("Error: Ensure a repository is selected.", severity="error")

if __name__ == "__main__":
    # Update this to your target 'MY' directory
    TARGET = "~/Documents/MY"
    app = GitScannerTUI(TARGET)
    app.run()
