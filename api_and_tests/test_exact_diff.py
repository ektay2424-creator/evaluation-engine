import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))

from trace_parser import exact_diff

def test_exact_diff_identical_sequences():
    result = exact_diff(["lookup_order"], ["lookup_order"])
    assert result == []

def test_exact_diff_length_mismatch():
    result = exact_diff(["lookup_order"], [])
    assert result == [{
        "position": "length_mismatch",
        "version_a_length": 1,
        "version_b_length": 0
    }]