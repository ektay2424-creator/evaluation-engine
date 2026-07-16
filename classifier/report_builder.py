import sys
import os

sys.path.append(os.path.dirname(__file__))
from hard_gates import HARD_GATE_PATTERNS
from weighted_scoring import PATTERN_WEIGHTS

REASON_TEXT = {
    "missing_tool_call": "Agent skipped a required tool call",
    "wrong_tool_called": "Agent called the wrong tool",
    "extra_tool_call": "Agent called an unexpected extra tool",
    "argument_diff": "Agent's tool call used different arguments than expected",
    "response_diverges_from_output": "Agent gave a factual response with no tool call to back it up",
    "error_not_acknowledged": "Tool returned an error, but agent's response didn't acknowledge it",
    "blind_tool_call": "Agent called a tool without required input (e.g. missing order_id)",
}


def _pick_matched_pattern(findings, gate_result):
    if gate_result["triggered_gates"]:
        return gate_result["triggered_gates"][0]["pattern"]

    scored = [f for f in findings if f["pattern"] in PATTERN_WEIGHTS]
    if not scored:
        return None

    scored.sort(key=lambda f: PATTERN_WEIGHTS[f["pattern"]], reverse=True)
    return scored[0]["pattern"]


def _build_metrics(trace_a, trace_b):
    from trace_parser import get_latencies

    latencies_a = get_latencies(trace_a)
    latencies_b = get_latencies(trace_b)

    total_latency_a = sum(latencies_a) if latencies_a else None
    total_latency_b = sum(latencies_b) if latencies_b else None

    latency_change_pct = None
    if total_latency_a and total_latency_b is not None:
        latency_change_pct = round(
            ((total_latency_b - total_latency_a) / total_latency_a) * 100, 2
        )

    return {
        "latency_ms_a": total_latency_a,
        "latency_ms_b": total_latency_b,
        "latency_change_pct": latency_change_pct,
        "task_completed_a": trace_a.get("task_completed"),
        "task_completed_b": trace_b.get("task_completed"),
        "cost": None
    }


def build_report(trace_a, trace_b, findings, classification):
    gate_result = classification["gate_result"]
    verdict = classification["verdict"]

    risk_map = {"fail": "high", "warn": "medium", "pass": "low"}

    reasons = []
    seen_patterns = set()
    for f in findings:
        if f["pattern"] not in seen_patterns:
            seen_patterns.add(f["pattern"])
            reasons.append(REASON_TEXT.get(f["pattern"], f["pattern"]))

    return {
        "comparison_id": f"{trace_a.get('run_id')}_vs_{trace_b.get('run_id')}",
        "task_id": None,
        "version_a": trace_a.get("run_id"),
        "version_b": trace_b.get("run_id"),
        "regression_detected": len(findings) > 0,
        "confidence_score": None,
        "risk_level": risk_map[verdict],
        "changes": findings,
        "metrics": _build_metrics(trace_a, trace_b),
        "matched_pattern": _pick_matched_pattern(findings, gate_result),
        "hard_gate_triggered": gate_result["gate_failed"],
        "reasons": reasons,
    }

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "patterns"))
    from trace_parser import load_trace
    from pattern_matcher import match_patterns
    from classifier import classify
    import json

    data = load_trace("mock_trace/real_traces.json")
    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]

    result = match_patterns(trace_a10, trace_b7)
    classification = classify(result["findings"])
    report = build_report(trace_a10, trace_b7, result["findings"], classification)

    print(json.dumps(report, indent=2))

    trace_a1 = data["dataset"]["version_a"][0]
    trace_b1 = data["dataset"]["version_b"][0]

    result_clean = match_patterns(trace_a1, trace_b1)
    classification_clean = classify(result_clean["findings"])
    report_clean = build_report(trace_a1, trace_b1, result_clean["findings"], classification_clean)

    print(json.dumps(report_clean, indent=2))