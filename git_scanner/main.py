import sys
import os
import json
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
            branch = branch_line.split('...')[0].strip()
            if branch.startswith('No commits yet on '):
                branch = branch.replace('No commits yet on ', '')
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
    export: Optional[str] = typer.Option(None, "--export", help="Export scan results as JSON to specified file path")
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
            from git_scanner.tui import GitScannerTUI
            tui_app = GitScannerTUI(base_path, exclude=exclude_list, max_depth=final_max_depth)
            tui_app.run()
            rprint("\n[bold cyan]✅ Workspace Scanner Terminated Successfully.[/bold cyan]\n")
        except Exception as e:
            rprint(f"\n[bold red]❌ CRITICAL TUI ERROR:[/bold red] {e}")
            console.print_exception()
        return

    # Route 2: CLI Mode
    with console.status(f"[bold cyan]Scanning {base_path}...[/bold cyan]", spinner="dots"):
        repos = list(find_git_repos(base_path, exclude=exclude_list, max_depth=final_max_depth))
        with ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 4) * 4)) as executor:
            results = executor.map(get_repo_details, repos)
            dirty_repos = [r for r in results if r is not None]

    if not dirty_repos:
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
        export_file.write_text(json.dumps(export_data, indent=2), encoding="utf-8")
        rprint(f"[bold green]📄 Exported scan results ({len(dirty_repos)} repos) to {export_file.resolve()}[/bold green]")

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
            str(repo['branch']),
            str(repo['modified']),
            str(repo['untracked']),
            str(repo.get('last_commit', 'Unknown'))
        )

    console.print(table)

if __name__ == "__main__":
    app()

