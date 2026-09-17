import time
import tempfile
import subprocess
import os
import concurrent.futures
from pathlib import Path
from git_scanner.main import find_git_repos, get_repo_details

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

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = set()

            for _ in range(max_workers):
                try:
                    repo = next(repos)
                    futures.add(executor.submit(get_repo_details, repo))
                except StopIteration:
                    break

            while futures:
                # wait for at least one future to complete
                done, futures = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)

                for future in done:
                    details = future.result()
                    if details:
                        dirty.append(details)

                # top up
                for _ in range(len(done)):
                    try:
                        repo = next(repos)
                        futures.add(executor.submit(get_repo_details, repo))
                    except StopIteration:
                        break
        t1 = time.time()
        print(f"Bounded concurrency time: {t1 - t0:.4f}s")
        print(f"Found dirty: {len(dirty)}")

if __name__ == "__main__":
    test_bounded()
