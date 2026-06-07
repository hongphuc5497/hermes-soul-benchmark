import json
import runpy
import subprocess
import sys
import threading
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "hermes-soul-benchmark"
SCENARIOS_PATH = REPO_ROOT / "scenarios.json"


def load_scenario_data():
    return json.loads(SCENARIOS_PATH.read_text())


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
        self.assertIn("Benchmark two or more Hermes SOUL.md profiles", result.stdout)
        self.assertIn("--profiles", result.stdout)
        self.assertIn("--parallel", result.stdout)

    def test_dry_run_uses_checked_in_scenarios(self):
        scenario_count = len(load_scenario_data()["scenarios"])
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "--profile-a", "smoke-a", "--profile-b", "smoke-b", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"Would run {scenario_count} scenarios × 2 profiles = {scenario_count * 2} hermes invocations",
            result.stdout,
        )

    def test_multi_profile_dry_run_counts_all_profiles(self):
        scenario_count = len(load_scenario_data()["scenarios"])
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "--profiles", "smoke-a", "smoke-b", "smoke-c", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"Would run {scenario_count} scenarios × 3 profiles = {scenario_count * 3} hermes invocations",
            result.stdout,
        )
        self.assertIn("Profiles: smoke-a, smoke-b, smoke-c", result.stdout)

    def test_parallel_dry_run_reports_mode(self):
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "--profiles", "smoke-a", "smoke-b", "--parallel", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Mode: parallel per scenario", result.stdout)

    def test_multi_profile_json_shape_helper(self):
        namespace = runpy.run_path(str(CLI_PATH))
        build_json_output = namespace["build_json_output"]
        scenarios = [{"id": "quick", "dimension": "precision"}]
        profiles = ["alpha", "beta", "gamma"]
        results = {
            "quick": {
                "alpha": {"score": 1, "total": 2, "pct": 50.0, "elapsed": 1.0},
                "beta": {"score": 2, "total": 2, "pct": 100.0, "elapsed": 2.0},
                "gamma": {"score": 0, "total": 2, "pct": 0.0, "elapsed": 3.0},
            }
        }

        output = build_json_output(profiles, scenarios, results)

        self.assertEqual(output["profiles"], profiles)
        self.assertEqual(output["aggregate"]["beta"]["pct"], 100.0)
        self.assertEqual(output["scenarios"][0]["winner"], "beta")
        self.assertEqual(set(output["scenarios"][0]["results"]), set(profiles))
        self.assertNotIn("profile_a", output)

    def test_run_profile_set_parallel_uses_concurrent_workers(self):
        namespace = runpy.run_path(str(CLI_PATH))
        run_profile_set = namespace["run_profile_set"]
        profiles = ["alpha", "beta", "gamma"]
        barrier = threading.Barrier(len(profiles))
        thread_ids = []

        def fake_run_hermes(profile, prompt, timeout):
            thread_ids.append(threading.get_ident())
            barrier.wait(timeout=0.5)
            return {
                "exit_code": 0,
                "stdout": profile,
                "stderr": "",
                "elapsed": 0.1,
                "truncated": False,
            }

        run_profile_set.__globals__["run_hermes"] = fake_run_hermes
        results = run_profile_set(profiles, "prompt", ["no_fabrication"], 5, parallel=True)

        self.assertEqual(list(results.keys()), profiles)
        self.assertGreater(len(set(thread_ids)), 1)
        self.assertEqual(results["alpha"]["stdout"], "alpha")
        self.assertTrue(results["alpha"]["checks"]["no_fabrication"])


class ScenarioDataTests(unittest.TestCase):
    def test_scenarios_have_required_shape(self):
        data = load_scenario_data()
        dimensions = set(data["dimensions"])
        scenarios = data["scenarios"]
        ids = [scenario.get("id") for scenario in scenarios]

        self.assertGreaterEqual(len(scenarios), 20)
        self.assertEqual(len(ids), len(set(ids)), "scenario ids must be unique")

        for scenario in scenarios:
            with self.subTest(scenario=scenario.get("id")):
                self.assertIsInstance(scenario.get("id"), str)
                self.assertIn(scenario.get("dimension"), dimensions)
                self.assertIsInstance(scenario.get("prompt"), str)
                self.assertGreater(len(scenario["prompt"]), 20)
                self.assertIsInstance(scenario.get("checks"), list)
                self.assertGreater(len(scenario["checks"]), 0)

    def test_every_dimension_has_at_least_one_scenario(self):
        data = load_scenario_data()
        covered = {scenario["dimension"] for scenario in data["scenarios"]}

        self.assertEqual(set(data["dimensions"]), covered)

    def test_all_scenario_checks_are_registered(self):
        registry = runpy.run_path(str(CLI_PATH))["CHECK_REGISTRY"]
        data = load_scenario_data()
        unknown_checks = sorted({
            check
            for scenario in data["scenarios"]
            for check in scenario["checks"]
            if check not in registry
        })

        self.assertEqual(unknown_checks, [])


if __name__ == "__main__":
    unittest.main()