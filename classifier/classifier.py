import sys
import os

sys.path.append(os.path.dirname(__file__))

from hard_gates import check_hard_gates
from weighted_scoring import compute_score


def classify(findings):
    gate_result = check_hard_gates(findings)
    score_result = compute_score(findings)

    if gate_result["gate_failed"]:
        verdict = "fail"
    elif score_result["exceeds_warn_threshold"]:
        verdict = "warn"
    else:
        verdict = "pass"

    return {
        "verdict": verdict,
        "gate_result": gate_result,
        "score_result": score_result
    }

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "patterns"))
    from trace_parser import load_trace
    from pattern_matcher import match_patterns

    data = load_trace("mock_trace/real_traces.json")

    # Known regression — should be "fail"
    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]
    result = match_patterns(trace_a10, trace_b7)
    print(classify(result["findings"])["verdict"])

    # Known clean pair — should be "pass"
    trace_a1 = data["dataset"]["version_a"][0]
    trace_b1 = data["dataset"]["version_b"][0]
    result_clean = match_patterns(trace_a1, trace_b1)
    print(classify(result_clean["findings"])["verdict"])

    # Synthetic case: argument_diff only, no hard gate — should be "warn"
    fake_findings = [
        {"pattern": "argument_diff", "position": 0, "tool": "lookup_order",
         "argument": "order_id", "change": "modified",
         "version_a_value": "ORD-1001", "version_b_value": "ORD-1002"}
    ]
    print(classify(fake_findings)["verdict"])