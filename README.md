# hermes-soul-benchmark

Benchmark two or more [Hermes Agent](https://github.com/NousResearch/hermes-agent) `SOUL.md` persona files. The CLI runs identical prompts against each selected profile, scores responses with lightweight heuristics, and emits either a markdown report or JSON.

Important: this tool benchmarks named Hermes profiles from `~/.hermes/profiles/<name>/SOUL.md`. It does **not** read repo-local `profiles/` copies or your active global `~/.hermes/SOUL.md` unless you clone that prompt into a named profile first.

## Quick Start

```bash
# 1. Create profiles with different SOUL.md files
hermes profile create soul-v1 --clone
hermes profile create soul-v2 --clone
hermes profile create soul-v3 --clone
cp old-soul.md ~/.hermes/profiles/soul-v1/SOUL.md
cp new-soul.md ~/.hermes/profiles/soul-v2/SOUL.md
cp experimental-soul.md ~/.hermes/profiles/soul-v3/SOUL.md

# 2. Compare profiles
./hermes-soul-benchmark --profiles soul-v1 soul-v2 soul-v3

# Optional: use legacy two-profile flags
./hermes-soul-benchmark --profile-a soul-v1 --profile-b soul-v2

# Optional: run profiles concurrently within each scenario
./hermes-soul-benchmark --profiles soul-v1 soul-v2 soul-v3 --parallel

# 3. JSON output for programmatic use
./hermes-soul-benchmark --profiles soul-v1 soul-v2 soul-v3 --json > results.json

# 4. Safe smoke check without invoking Hermes
./hermes-soul-benchmark --profiles smoke-a smoke-b smoke-c --dry-run
```

## How It Works

1. Reads test scenarios from the checked-in `scenarios.json` file (24 prompts across 7 dimensions)
2. Runs each scenario through every selected profile via `hermes chat -q -p <profile>`
   - Hermes resolves each `<profile>` from `~/.hermes/profiles/<profile>/SOUL.md`
   - add `--parallel` to fan those profile runs out concurrently per scenario
3. Evaluates responses against dimension-specific checks (keyword/regex heuristics)
4. Produces a markdown report or JSON payload with per-scenario and aggregate scores

`--parallel` only reduces wall-clock time. It does not reduce total Hermes invocations or provider cost.

## Smoke Check

To verify the CLI wiring without requiring Hermes profiles or API calls:

```bash
./hermes-soul-benchmark --profile-a smoke-a --profile-b smoke-b --dry-run

# Multi-profile dry-run
./hermes-soul-benchmark --profiles smoke-a smoke-b smoke-c --dry-run

# Multi-profile parallel dry-run
./hermes-soul-benchmark --profiles smoke-a smoke-b smoke-c --parallel --dry-run
```

This should print the scenario count and planned benchmark runs, then exit successfully.

## Evaluation Dimensions

| Dimension | Weight | What it checks |
|-----------|--------|---------------|
| **Safety** | 25% | Prompt injection defense, destructive command handling |
| **Evidence** | 20% | Live-state verification, evidence-backed claims |
| **Precision** | 15% | No fabrication, structured output |
| **Teaching** | 15% | Protocol adherence, quiz usage, checklist format |
| **Efficiency** | 10% | Appropriate delegation, no over-planning |
| **Compliance** | 10% | DON'Ts followed, stop command, error recovery |
| **Clarity** | 5% | Shipped./Done. headers, table format |

## Output

```
# SOUL.md Benchmark Report

**Profile A:** `soul-v1` | **Profile B:** `soul-v2` | **Profile C:** `soul-v3`
**Scenarios:** 24 | **Profiles:** 3 | **Date:** 2026-06-07 15:30

## Results by Scenario
| # | Scenario | Dimension | A Score | B Score | C Score | Winner |
|---|----------|-----------|---------|---------|---------|--------|
| 1 | teach-me | teaching | 60.0% (3/5) | 40.0% (2/5) | 80.0% (4/5) | soul-v3 |
...

## Aggregate Scores
| Profile | Total Score | Percentage | Scenarios Won |
|---------|-------------|------------|---------------|
| **soul-v1** | 42/87 | 48.3% | 3 |
| **soul-v2** | 39/87 | 44.8% | 1 |
| **soul-v3** | 45/87 | 51.7% | 8 |
```

JSON output contains a `profiles` array, aggregate scores keyed by profile name, and each scenario's `results` keyed by profile name. When exactly two profiles are selected, legacy `profile_a`, `profile_b`, `a`, `b`, `a_score`, and `b_score` fields are also included for compatibility.

## Limitations

The heuristic evaluator uses regex/keyword matching and cannot distinguish:
- "Correctly refused to claim status without evidence" from "failed to check status"
- "Asked clarifying questions (good)" from "response too long (bad)"
- Tool-call quality from text-output patterns
- Provider/auth failures from model behavior if Hermes prints error/debug output to stdout

For production use, pair with an LLM-as-judge evaluator.

## Requirements

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed
- Two or more named Hermes profiles in `~/.hermes/profiles/` with valid config + API keys
- Python 3.11+
- Zero external dependencies (stdlib-only)
