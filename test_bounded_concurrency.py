import time
import tempfile
import subprocess
import os
from pathlib import Path
from git_scanner.main import find_git_repos, get_repo_details
from concurrent.futures import ThreadPoolExecutor, as_completed

def generate_mock_repos(base_dir, num_repos=10):
    for i in range(num_repos):
        repo_dir = Path(base_dir) / f"repo_{i}"
        repo_dir.mkdir(parents=True)
        subprocess.run(['git', 'init'], cwd=repo_dir, capture_output=True)
        if i % 2 == 0:
            (repo_dir / "dirty.txt").write_text("hello")

def test_bounded():
    with tempfile.TemporaryDirectory() as tempdir:
        generate_mock_repos(tempdir, 20)

        t0 = time.time()
        repos = find_git_repos(Path(tempdir))
        dirty = []
        max_workers = min(32, (os.cpu_count() or 4) * 4)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = set()

            # Initial fill
            for _ in range(max_workers):
                try:
                    repo = next(repos)
                    futures.add(executor.submit(get_repo_details, repo))
                except StopIteration:
                    break

            # Process as they complete, top up from generator
            while futures:
                done, futures = as_completed(futures, return_when="FIRST_COMPLETED")
                # But wait, as_completed doesn't have return_when parameter, concurrent.futures.wait does.
                # However we can just pop from as_completed? No, as_completed returns an iterator.
                pass
