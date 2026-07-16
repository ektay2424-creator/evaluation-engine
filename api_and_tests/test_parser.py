import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))

from trace_parser import load_trace, get_tool_sequence, get_args

def load_test_data():
    return load_trace("mock_trace/real_traces.json")

def test_get_tool_sequence():
    data = load_test_data()
    trace_a1 = data["dataset"]["version_a"][0]
    result = get_tool_sequence(trace_a1)
    assert result == ["lookup_order"]

def test_get_tool_sequence_multi_call():
    data = load_test_data()
    trace_a8 = data["dataset"]["version_a"][7]  # A-008 has two tool calls
    result = get_tool_sequence(trace_a8)
    assert result == ["lookup_order", "lookup_order"]

def test_get_args_on_tool_call():
    data = load_test_data()
    trace_a1 = data["dataset"]["version_a"][0]
    result = get_args(trace_a1, 1)
    assert result == {"order_id": "ORD-1001"}

def test_get_args_on_non_tool_call():
    data = load_test_data()
    trace_a1 = data["dataset"]["version_a"][0]
    result = get_args(trace_a1, 0)
    assert result is None

