import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))

from trace_parser import load_trace, get_latencies, check_consistency

def load_test_data():
    return load_trace("mock_trace/real_traces.json")

def test_check_consistency_normal_case():
    data = load_test_data()
    all_latencies = []
    for run in data["dataset"]["version_a"]:
        all_latencies.extend(get_latencies(run))

    result = check_consistency(all_latencies, threshold_std=200)
    assert result["mean_latency"] == 636.7777777777778
    assert round(result["std_latency"], 2) == 199.87
    assert result["is_consistent"] is True

def test_check_consistency_flags_high_variance():
    data = load_test_data()
    all_latencies = []
    for run in data["dataset"]["version_a"]:
        all_latencies.extend(get_latencies(run))

    result = check_consistency(all_latencies, threshold_std=50)
    assert result["is_consistent"] is False

def test_check_consistency_single_value():
    result = check_consistency([431])
    assert result["mean_latency"] == 431
    assert result["std_latency"] is None
    assert result["is_consistent"] is True

def test_check_consistency_empty_list():
    result = check_consistency([])
    assert result["mean_latency"] is None
    assert result["std_latency"] is None
    assert result["is_consistent"] is True