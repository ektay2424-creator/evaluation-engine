import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "patterns"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "classifier"))

from trace_parser import load_trace
from pattern_matcher import match_patterns
from classifier import classify


def load_test_data():
    return load_trace("mock_trace/real_traces.json")


def test_classify_fails_on_known_regression():
    data = load_test_data()
    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]

    result = match_patterns(trace_a10, trace_b7)
    verdict = classify(result["findings"])

    assert verdict["verdict"] == "fail"
    assert verdict["gate_result"]["gate_failed"] is True


def test_classify_passes_on_clean_pair():
    data = load_test_data()
    trace_a1 = data["dataset"]["version_a"][0]
    trace_b1 = data["dataset"]["version_b"][0]

    result = match_patterns(trace_a1, trace_b1)
    verdict = classify(result["findings"])

    assert verdict["verdict"] == "pass"
    assert verdict["gate_result"]["gate_failed"] is False
    assert verdict["score_result"]["total_score"] == 0


def test_classify_warns_on_single_argument_diff():
    fake_findings = [
        {"pattern": "argument_diff", "position": 0, "tool": "lookup_order",
         "argument": "order_id", "change": "modified",
         "version_a_value": "ORD-1001", "version_b_value": "ORD-1002"}
    ]
    verdict = classify(fake_findings)

    assert verdict["verdict"] == "warn"
    assert verdict["gate_result"]["gate_failed"] is False
    assert verdict["score_result"]["total_score"] == 5


def test_classify_all_known_regressions_fail():
    data = load_test_data()
    version_a = data["dataset"]["version_a"]
    version_b = data["dataset"]["version_b"]

    regression_pairs = [
        (version_a[9], version_b[6]),
        (version_a[1], version_b[7]),
        (version_a[5], version_b[8]),
    ]

    for trace_a, trace_b in regression_pairs:
        result = match_patterns(trace_a, trace_b)
        verdict = classify(result["findings"])
        assert verdict["verdict"] == "fail", (
            f"Expected fail for {trace_a['run_id']} vs {trace_b['run_id']}, got {verdict['verdict']}"
        )