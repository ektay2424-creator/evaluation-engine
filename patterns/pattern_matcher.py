import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))
sys.path.append(os.path.dirname(__file__))

from pattern_definitions import (
    missing_tool_call,
    wrong_tool_called,
    extra_tool_call,
    argument_diff,
    response_diverges_from_output,
)



def match_patterns(trace_a, trace_b):
    steps_a = trace_a["steps"]
    steps_b = trace_b["steps"]

    findings = []
    findings.extend(missing_tool_call(steps_a, steps_b))
    findings.extend(wrong_tool_called(steps_a, steps_b))
    findings.extend(extra_tool_call(steps_a, steps_b))
    findings.extend(argument_diff(steps_a, steps_b))
    findings.extend(response_diverges_from_output(trace_b))

    return {
        "run_a": trace_a.get("run_id"),
        "run_b": trace_b.get("run_id"),
        "findings": findings,
        "regression_detected": len(findings) > 0
    }

if __name__ == "__main__":
    from trace_parser import load_trace

    data = load_trace("mock_trace/real_traces.json")
    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]

    print(match_patterns(trace_a10, trace_b7))
    trace_a1 = data["dataset"]["version_a"][0]
    trace_b1 = data["dataset"]["version_b"][0]
    print(match_patterns(trace_a1, trace_b1))