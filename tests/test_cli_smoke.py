import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "hermes-soul-benchmark"


class CliSmokeTests(unittest.TestCase):
    def test_help_exits_successfully(self):
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "--help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("A/B benchmark two Hermes SOUL.md versions", result.stdout)

    def test_dry_run_uses_checked_in_scenarios(self):
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "--profile-a", "smoke-a", "--profile-b", "smoke-b", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Would run 10 scenarios × 2 profiles = 20 hermes invocations", result.stdout)


if __name__ == "__main__":
    unittest.main()