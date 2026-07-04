import subprocess
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

app = typer.Typer(help="Scan directories for uncommitted Git repositories.")
console = Console()

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

@app.command()
def scan(
    directory: str = typer.Argument(..., help="The root directory to scan"),
    depth: int = typer.Option(3, help="Max directory depth to scan (Not implemented in rglob, kept for scaling)")
):
    """Deep scan a directory for dirty Git repositories."""
    base_path = Path(directory).expanduser().resolve()
    
    if not base_path.exists() or not base_path.is_dir():
        rprint(f"[bold red]❌ Error:[/bold red] Directory '{base_path}' does not exist.")
        raise typer.Exit(code=1)

    with console.status(f"[bold cyan]Scanning {base_path} for Git repositories...[/bold cyan]", spinner="dots"):
        dirty_repos = []
        for git_dir in base_path.rglob('.git'):
            repo_path = git_dir.parent
            if is_repo_dirty(repo_path):
                dirty_repos.append(repo_path)

    # ➔ Build a beautiful TUI Table
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
