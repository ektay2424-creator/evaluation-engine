import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "patterns"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "classifier"))

from trace_parser import load_trace
from pattern_matcher import match_patterns
from classifier import classify
from report_builder import build_report


def load_test_data():
    return load_trace("mock_trace/real_traces.json")


def test_report_on_known_regression():
    data = load_test_data()
    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]

    result = match_patterns(trace_a10, trace_b7)
    classification = classify(result["findings"])
    report = build_report(trace_a10, trace_b7, result["findings"], classification)

    assert report["regression_detected"] is True
    assert report["risk_level"] == "high"
    assert report["hard_gate_triggered"] is True
    assert report["matched_pattern"] == "missing_tool_call"
    assert len(report["reasons"]) == 2


def test_report_on_clean_pair():
    data = load_test_data()
    trace_a1 = data["dataset"]["version_a"][0]
    trace_b1 = data["dataset"]["version_b"][0]

    result = match_patterns(trace_a1, trace_b1)
    classification = classify(result["findings"])
    report = build_report(trace_a1, trace_b1, result["findings"], classification)

    assert report["regression_detected"] is False
    assert report["risk_level"] == "low"
    assert report["hard_gate_triggered"] is False
    assert report["matched_pattern"] is None
    assert report["reasons"] == []
    assert report["metrics"]["latency_ms_a"] is not None
    assert report["metrics"]["latency_ms_b"] is not None

def test_report_confidence_score_hard_gate():
    data = load_test_data()
    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]

    result = match_patterns(trace_a10, trace_b7)
    classification = classify(result["findings"])
    report = build_report(trace_a10, trace_b7, result["findings"], classification)

    assert report["confidence_score"] == 0.0


def test_report_confidence_score_clean():
    data = load_test_data()
    trace_a1 = data["dataset"]["version_a"][0]
    trace_b1 = data["dataset"]["version_b"][0]

    result = match_patterns(trace_a1, trace_b1)
    classification = classify(result["findings"])
    report = build_report(trace_a1, trace_b1, result["findings"], classification)

    assert report["confidence_score"] == 1.0