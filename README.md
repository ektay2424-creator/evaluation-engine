# Evaluation Engine

An AI reliability co-pilot that evaluates an agent's behavior before and after changes, detecting regressions by comparing execution traces from two versions (Version A vs Version B) of the same agent.

Built and tested against a real order-status agent dataset (LangGraph-based), but designed to generalize to other tool-using agents.

## What it does

Given two traces — one from a baseline agent run, one from a candidate version — the engine:
1. Parses both traces into a common structure
2. Diffs their tool-call sequences and arguments
3. Matches known regression patterns (skipped tool calls, wrong tool, fabricated responses, unacknowledged errors, etc.)
4. Classifies the result as `pass`, `warn`, or `fail`, using hard gates + weighted scoring
5. Returns a structured report explaining exactly what changed and why it matters

## Project structure

evaluation_engine/
├── parser/              # Trace loading + field extraction (tool sequence, args, latency)
├── comparators/         # exact_diff, semantic_diff, check_consistency
├── patterns/            # 7 named regression patterns + pattern_matcher.py
├── classifier/          # hard_gates.py, weighted_scoring.py, classifier.py, report_builder.py
├── config/               # thresholds.json, task_category_weights.json
├── schemas/              # report_schema.json — the output contract
├── api_and_tests/       # FastAPI app (main.py) + all pytest test files
└── mock_trace/           # real_traces.json — sample dataset used for testing

## Setup

```bash
pip install -r requirements.txt
```

## Running tests

```bash
pytest api_and_tests/
```

All patterns, comparators, and the classifier are tested against real trace data (`mock_trace/real_traces.json`), including both known regressions and known clean runs. 25 tests total.

## Running the API

```bash
uvicorn api_and_tests.main:app --reload
```

Server starts at `http://127.0.0.1:8000`.

- `GET /health` — liveness check
- `POST /compare` — send two traces, get back a regression report

### Example request

```bash
curl -X POST http://127.0.0.1:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"trace_a": { ... }, "trace_b": { ... }}'
```

`trace_a` and `trace_b` are full trace objects (see `mock_trace/real_traces.json` for the expected shape — each run under `version_a`/`version_b` is a valid `trace_a`/`trace_b` value).

### Example response

```json
{
  "comparison_id": "A-010_vs_B-007",
  "task_id": null,
  "version_a": "A-010",
  "version_b": "B-007",
  "regression_detected": true,
  "confidence_score": 0.0,
  "risk_level": "high",
  "changes": [
    {"pattern": "missing_tool_call", "position": 0, "tool": "lookup_order"},
    {"pattern": "response_diverges_from_output", "run_id": "B-007", "reason": "No tool_call present, but agent gave a factual-sounding response"}
  ],
  "metrics": {
    "latency_ms_a": 388,
    "latency_ms_b": null,
    "latency_change_pct": null,
    "task_completed_a": true,
    "task_completed_b": true,
    "cost": null
  },
  "matched_pattern": "missing_tool_call",
  "hard_gate_triggered": true,
  "reasons": [
    "Agent skipped a required tool call",
    "Agent gave a factual response with no tool call to back it up"
  ]
}
```

Full field definitions live in `schemas/report_schema.json`.

## Known limitations

- `confidence_score` uses a simple heuristic (hard gate → 0.0, no findings → 1.0, otherwise scaled by weighted score against a fixed ceiling of 20) — not a statistically validated model, and the ceiling value hasn't been tuned against a large dataset
- `metrics.cost` is always `null` — no cost-tracking data exists yet
- `task_id` is always `null` — the current dataset has no task-category concept
- Patterns compare tool-call subsequences positionally; this works well for single-turn tool use but hasn't been tested against traces with parallel or branching tool calls
- `error_not_acknowledged` uses simple keyword matching on the response text, not semantic understanding — it may miss acknowledgments phrased unusually