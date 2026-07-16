
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
    calls_a = _tool_call_steps(steps_a)
    calls_b = _tool_call_steps(steps_b)

    findings = []
    min_length = min(len(calls_a), len(calls_b))
    for i in range(min_length):
        if calls_a[i]["tool"] != calls_b[i]["tool"]:
            findings.append({
                "pattern": "wrong_tool_called",
                "position": i,
                "expected_tool": calls_a[i]["tool"],
                "actual_tool": calls_b[i]["tool"]
            })
    return findings


def extra_tool_call(steps_a, steps_b):
    calls_a = _tool_call_steps(steps_a)
    calls_b = _tool_call_steps(steps_b)

    findings = []
    for i, call_b in enumerate(calls_b):
        if i >= len(calls_a):
            findings.append({
                "pattern": "extra_tool_call",
                "position": i,
                "tool": call_b["tool"]
            })
    return findings

def semantic_diff(steps_a, steps_b):
    calls_a = [s for s in steps_a if s["type"] == "tool_call"]
    calls_b = [s for s in steps_b if s["type"] == "tool_call"]

    differences = []
    min_length = min(len(calls_a), len(calls_b))

    for i in range(min_length):
        step_a = calls_a[i]
        step_b = calls_b[i]

        if step_a["tool"] != step_b["tool"]:
            continue

        args_a = step_a["arguments"]
        args_b = step_b["arguments"]
        all_keys = set(args_a) | set(args_b)

        for key in all_keys:
            if key not in args_a:
                differences.append({
                    "position": i, "tool": step_a["tool"], "argument": key,
                    "change": "added", "version_b_value": args_b[key]
                })
            elif key not in args_b:
                differences.append({
                    "position": i, "tool": step_a["tool"], "argument": key,
                    "change": "removed", "version_a_value": args_a[key]
                })
            elif args_a[key] != args_b[key]:
                differences.append({
                    "position": i, "tool": step_a["tool"], "argument": key,
                    "change": "modified",
                    "version_a_value": args_a[key], "version_b_value": args_b[key]
                })

    return differences

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
def error_not_acknowledged(trace):
    findings = []
    response = trace.get("final_agent_response", "").lower()
    acknowledgment_phrases = [
        "couldn't", "could not", "not found", "unable",
        "please check", "sorry", "can't find", "cannot find"
    ]

    for step in trace["steps"]:
        if step["type"] != "tool_call":
            continue
        output = step.get("output", {})
        if "error" in output:
            if not any(phrase in response for phrase in acknowledgment_phrases):
                findings.append({
                    "pattern": "error_not_acknowledged",
                    "run_id": trace.get("run_id"),
                    "tool_error": output["error"],
                    "final_agent_response": trace.get("final_agent_response"),
                    "reason": "Tool returned an error, but response doesn't acknowledge failure"
                })
    return findings


def blind_tool_call(trace):
    findings = []
    for step in trace["steps"]:
        if step["type"] != "tool_call":
            continue
        args = step.get("arguments", {})
        order_id = args.get("order_id")
        if not order_id:
            findings.append({
                "pattern": "blind_tool_call",
                "run_id": trace.get("run_id"),
                "tool": step["tool"],
                "reason": "Tool called without a valid order_id argument"
            })
    return findings

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
    trace_a3 = data["dataset"]["version_a"][2]  # A-003, the ORD-9999 error case
    print(error_not_acknowledged(trace_a3))   # should be [] — it WAS acknowledged well
    print(blind_tool_call(trace_a3))          # should be [] — order_id was provided