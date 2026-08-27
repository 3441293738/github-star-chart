from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from star_chart.cli import main as render


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "creatorhub.json"


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, stdout=subprocess.DEVNULL)


class PublishTests(unittest.TestCase):
    def test_publish_creates_data_branch(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            remote, work, charts, checkout = root / "remote.git", root / "work", root / "charts", root / "checkout"
            remote.mkdir()
            git(remote, "init", "--bare")
            subprocess.run(["git", "clone", str(remote), str(work)], check=True, stdout=subprocess.DEVNULL)
            (work / "README.md").write_text("fixture", encoding="utf-8")
            git(work, "config", "user.name", "Test")
            git(work, "config", "user.email", "test@example.com")
            git(work, "add", "README.md")
            git(work, "commit", "-m", "initial")
            git(work, "push", "origin", "HEAD:main")
            render(["--fixture", str(FIXTURE), "--output-dir", str(charts), "--animate", "false"])
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src")
            subprocess.run(
                [sys.executable, "-m", "star_chart.publish", "--source", str(charts), "--branch", "star-history"],
                cwd=work,
                env=env,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(["git", "clone", "--branch", "star-history", str(remote), str(checkout)], check=True, stdout=subprocess.DEVNULL)
            self.assertTrue((checkout / "assets" / "star-history.svg").is_file())
            self.assertTrue((checkout / "assets" / "star-history-dark.svg").is_file())
            self.assertFalse((checkout / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
