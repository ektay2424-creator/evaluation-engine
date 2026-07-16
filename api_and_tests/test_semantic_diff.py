import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))

from trace_parser import semantic_diff, load_trace

def load_test_data():
    return load_trace("mock_trace/real_traces.json")

def test_semantic_diff_identical_args():
    data = load_test_data()
    steps_a1 = data["dataset"]["version_a"][0]["steps"]
    steps_b1 = data["dataset"]["version_b"][0]["steps"]
    result = semantic_diff(steps_a1, steps_b1)
    assert result == []

def test_semantic_diff_different_order_id():
    data = load_test_data()
    steps_a1 = data["dataset"]["version_a"][0]["steps"]   # A-001, looks up ORD-1001
    steps_a4 = data["dataset"]["version_a"][3]["steps"]   # A-004, looks up ORD-1003
    result = semantic_diff(steps_a1, steps_a4)
    assert len(result) == 1
    assert result[0]["argument"] == "order_id"
    assert result[0]["change"] == "modified"
    assert result[0]["version_a_value"] == "ORD-1001"
    assert result[0]["version_b_value"] == "ORD-1003"