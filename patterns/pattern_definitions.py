
def _tool_call_steps(steps):
    return [step for step in steps if step["type"] == "tool_call"]

def missing_tool_call(steps_a, steps_b):
    calls_a = _tool_call_steps(steps_a)
    calls_b = _tool_call_steps(steps_b)

    findings = []
    for i, call_a in enumerate(calls_a):
        if i >= len(calls_b):
            findings.append({
                "pattern": "missing_tool_call",
                "position": i,
                "tool": call_a["tool"]
            })
    return findings

def wrong_tool_called(steps_a, steps_b):
    findings = []
    for i, step_a in enumerate(steps_a):
        if step_a["type"] != "tool_call":
            continue
        if i >= len(steps_b):
            continue

        step_b = steps_b[i]
        if step_b["type"] != "tool_call":
            continue

        if step_a["tool"] != step_b["tool"]:
            findings.append({
                "pattern": "wrong_tool_called",
                "position": i,
                "expected_tool": step_a["tool"],
                "actual_tool": step_b["tool"]
            })

    return findings


def extra_tool_call(steps_a, steps_b):
    findings = []
    for i, step_b in enumerate(steps_b):
        if step_b["type"] != "tool_call":
            continue

        if i >= len(steps_a):
            findings.append({
                "pattern": "extra_tool_call",
                "position": i,
                "tool": step_b["tool"]
            })
            continue

        step_a = steps_a[i]
        if step_a["type"] != "tool_call":
            findings.append({
                "pattern": "extra_tool_call",
                "position": i,
                "tool": step_b["tool"]
            })

    return findings

def argument_diff(steps_a, steps_b):
    from trace_parser import semantic_diff
    results = semantic_diff(steps_a, steps_b)
    for r in results:
        r["pattern"] = "argument_diff"
    return results

def response_diverges_from_output(trace):
    steps = trace["steps"]
    has_tool_call = any(step["type"] == "tool_call" for step in steps)
    response = trace.get("final_agent_response", "")

    if not has_tool_call and response:
        return [{
            "pattern": "response_diverges_from_output",
            "run_id": trace.get("run_id"),
            "final_agent_response": response,
            "reason": "No tool_call present, but agent gave a factual-sounding response"
        }]
    return []

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))
    from trace_parser import load_trace

    data = load_trace("mock_trace/real_traces.json")
    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]

    print(missing_tool_call(trace_a10["steps"], trace_b7["steps"]))
    print(wrong_tool_called(trace_a10["steps"], trace_b7["steps"]))
    print(extra_tool_call(trace_a10["steps"], trace_b7["steps"]))
    print(argument_diff(trace_a10["steps"], trace_b7["steps"]))
    print(response_diverges_from_output(trace_b7))