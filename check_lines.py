
                if has_git:
                    yield Path(current_path)

                if max_depth is None or depth < max_depth:
                    stack.extend((subdir, depth + 1) for subdir in subdirs)
        except (PermissionError, FileNotFoundError):
            continue


def get_repo_details(repo_path: Path, exclude_untracked: bool = False) -> Optional[Dict[str, Any]]:
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

        if exclude_untracked and modified == 0:
            return None

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
