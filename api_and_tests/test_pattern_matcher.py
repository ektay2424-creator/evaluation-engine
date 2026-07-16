import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "patterns"))

from trace_parser import load_trace
from pattern_matcher import match_patterns


def load_test_data():
    return load_trace("mock_trace/real_traces.json")


def test_match_patterns_detects_real_regression():
    data = load_test_data()
    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]

    result = match_patterns(trace_a10, trace_b7)

    assert result["regression_detected"] is True
    pattern_names = [f["pattern"] for f in result["findings"]]
    assert "missing_tool_call" in pattern_names
    assert "response_diverges_from_output" in pattern_names


def test_match_patterns_no_false_positive_on_clean_pair():
    data = load_test_data()
    trace_a1 = data["dataset"]["version_a"][0]
    trace_b1 = data["dataset"]["version_b"][0]

    result = match_patterns(trace_a1, trace_b1)

    assert result["regression_detected"] is False
    assert result["findings"] == []


def test_match_patterns_all_known_regressions():
    data = load_test_data()
    version_a = data["dataset"]["version_a"]
    version_b = data["dataset"]["version_b"]

    # B-007 through B-010 are all marked regression: true in the dataset,
    # and each corresponds by order-lookup to an earlier version_a run.
    regression_pairs = [
        (version_a[9], version_b[6]),  # A-010 vs B-007 (ORD-1001)
        (version_a[1], version_b[7]),  # A-002 vs B-008 (ORD-1002)
        (version_a[5], version_b[8]),  # A-006 vs B-009 (ORD-1004)
    ]

    for trace_a, trace_b in regression_pairs:
        result = match_patterns(trace_a, trace_b)
        assert result["regression_detected"] is True, (
            f"Expected regression for {trace_a['run_id']} vs {trace_b['run_id']}, found none"
        )

def test_match_patterns_recognizes_good_error_handling():
    data = load_test_data()
    trace_a3 = data["dataset"]["version_a"][2]  # A-003, ORD-9999 not found, handled well

    result = match_patterns(trace_a3, trace_a3)  # comparing against itself: should be totally clean

    pattern_names = [f["pattern"] for f in result["findings"]]
    assert "error_not_acknowledged" not in pattern_names
    assert "blind_tool_call" not in pattern_names

def test_match_patterns_all_known_clean_pairs():
    data = load_test_data()
    version_a = data["dataset"]["version_a"]
    version_b = data["dataset"]["version_b"]

    # B-001 through B-004 are marked regression: false, matched to their
    # corresponding version_a runs by order_id.
    clean_pairs = [
        (version_a[0], version_b[0]),  # A-001 vs B-001 (ORD-1001)
        (version_a[5], version_b[1]),  # A-006 vs B-002 (ORD-1004)
        (version_a[1], version_b[2]),  # A-002 vs B-003 (ORD-1002)
        (version_a[3], version_b[3]),  # A-004 vs B-004 (ORD-1003)
    ]

    for trace_a, trace_b in clean_pairs:
        result = match_patterns(trace_a, trace_b)
        assert result["regression_detected"] is False, (
            f"Expected no regression for {trace_a['run_id']} vs {trace_b['run_id']}, but found: {result['findings']}"
        )
