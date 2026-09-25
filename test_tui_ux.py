import pytest
from git_scanner.main import GitScannerTUI
from pathlib import Path

@pytest.mark.asyncio
async def test_zero_repos_ux():
    app = GitScannerTUI(target_dir=Path("."), exclude=["*"])
    async with app.run_test() as pilot:
        await pilot.pause()
        app.update_table([]) # trigger zero state

        status = app.query_one("#status-bar")
        assert "ALL REPOSITORIES SECURED AND COMMITTED" in str(status.render())
        # We want to add a class to status bar
