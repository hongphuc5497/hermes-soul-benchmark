# hermes-soul-benchmark

A/B benchmark two [Hermes Agent](https://github.com/NousResearch/hermes-agent) SOUL.md persona files. Runs identical test prompts against two Hermes profiles, evaluates responses across 7 dimensions, and produces a comparison report.

## Quick Start

```bash
# 1. Create two profiles with different SOUL.md files
hermes profile create soul-v1 --clone
hermes profile create soul-v2 --clone
cp old-soul.md ~/.hermes/profiles/soul-v1/SOUL.md
cp new-soul.md ~/.hermes/profiles/soul-v2/SOUL.md

# 2. Run benchmark
./hermes-soul-benchmark --profile-a soul-v1 --profile-b soul-v2

# 3. JSON output for programmatic use
./hermes-soul-benchmark --profile-a soul-v1 --profile-b soul-v2 --json > results.json

# 4. Safe smoke check without invoking Hermes
./hermes-soul-benchmark --profile-a smoke-a --profile-b smoke-b --dry-run
```

## How It Works

1. Reads test scenarios from the checked-in `scenarios.json` file (10 prompts across 7 dimensions)
2. Runs each scenario through both profiles via `hermes chat -q -p <profile>`
3. Evaluates responses against dimension-specific checks (keyword/regex heuristics)
4. Produces a markdown comparison report with per-scenario scores and aggregate

## Smoke Check

To verify the CLI wiring without requiring Hermes profiles or API calls:

```bash
./hermes-soul-benchmark --profile-a smoke-a --profile-b smoke-b --dry-run
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

Profile A: soul-v1 | Profile B: soul-v2

## Results by Scenario
| # | Scenario | Dimension | A Score | B Score | Winner |
|---|----------|-----------|---------|---------|--------|
| 1 | teach-me | teaching | 60% | 40% | A |
...

## Aggregate Scores
| Profile | Total Score | Percentage |
|---------|-------------|------------|
| soul-v1 | 22/36 | 61.1% |
| soul-v2 | 19/36 | 52.8% |
```

## Limitations

The heuristic evaluator uses regex/keyword matching and cannot distinguish:
- "Correctly refused to claim status without evidence" from "failed to check status"
- "Asked clarifying questions (good)" from "response too long (bad)"
- Tool-call quality from text-output patterns

For production use, pair with an LLM-as-judge evaluator.

## Requirements

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed
- Two Hermes profiles with valid config + API keys
- Python 3.11+
- Zero external dependencies (stdlib-only)
