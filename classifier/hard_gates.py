HARD_GATE_PATTERNS = {
    "response_diverges_from_output",
    "error_not_acknowledged",
    "missing_tool_call",
}


def check_hard_gates(findings):
    triggered = [f for f in findings if f["pattern"] in HARD_GATE_PATTERNS]
    return {
        "gate_failed": len(triggered) > 0,
        "triggered_gates": triggered
    }

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "patterns"))
    from trace_parser import load_trace
    from pattern_matcher import match_patterns

    data = load_trace("mock_trace/real_traces.json")
    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]

    result = match_patterns(trace_a10, trace_b7)
    print(check_hard_gates(result["findings"]))