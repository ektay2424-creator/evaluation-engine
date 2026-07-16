import json


def load_trace(filepath):
    with open(filepath, "r") as f:
        trace = json.load(f)
    return trace

def get_tool_sequence(trace):
    tool_sequence = []
    for step in trace["steps"]:
        if step["type"] == "tool_call":
            tool_sequence.append(step["tool"])
    return tool_sequence

def get_args(trace, step_index):
    step = trace["steps"][step_index]
    if step["type"] != "tool_call":
        return None
    args = step["arguments"]
    return args

def exact_diff(sequence_a, sequence_b):
    differences = []
    min_length = min(len(sequence_a), len(sequence_b))

    for i in range(min_length):
        if sequence_a[i] != sequence_b[i]:
            differences.append({
                "position": i,
                "version_a": sequence_a[i],
                "version_b": sequence_b[i]
            })

    if len(sequence_a) != len(sequence_b):
        differences.append({
            "position": "length_mismatch",
            "version_a_length": len(sequence_a),
            "version_b_length": len(sequence_b)
        })

    return differences

def semantic_diff(steps_a, steps_b):
    differences = []
    min_length = min(len(steps_a), len(steps_b))

    for i in range(min_length):
        step_a = steps_a[i]
        step_b = steps_b[i]

        if step_a["type"] != "tool_call" or step_b["type"] != "tool_call":
            continue

        if step_a["tool"] != step_b["tool"]:
            continue

        args_a = step_a["arguments"]
        args_b = step_b["arguments"]

        all_keys = set(args_a) | set(args_b)

        for key in all_keys:
            if key not in args_a:
                differences.append({
                    "position": i,
                    "tool": step_a["tool"],
                    "argument": key,
                    "change": "added",
                    "version_b_value": args_b[key]
                })
            elif key not in args_b:
                differences.append({
                    "position": i,
                    "tool": step_a["tool"],
                    "argument": key,
                    "change": "removed",
                    "version_a_value": args_a[key]
                })
            elif args_a[key] != args_b[key]:
                differences.append({
                    "position": i,
                    "tool": step_a["tool"],
                    "argument": key,
                    "change": "modified",
                    "version_a_value": args_a[key],
                    "version_b_value": args_b[key]
                })

    return differences

def get_latencies(trace):
    latencies = []
    for step in trace["steps"]:
        if step["type"] == "tool_call":
            latencies.append(step["latency_ms"])
    return latencies

import statistics


def check_consistency(latencies, threshold_std=1.0):
    if len(latencies) < 2:
        return {
            "mean_latency": latencies[0] if latencies else None,
            "std_latency": None,
            "is_consistent": True
        }

    mean_latency = statistics.mean(latencies)
    std_latency = statistics.stdev(latencies)
    is_consistent = std_latency <= threshold_std

    return {
        "mean_latency": mean_latency,
        "std_latency": std_latency,
        "is_consistent": is_consistent
    }


if __name__ == "__main__":
    data = load_trace("mock_trace/real_traces.json")
    trace_a1 = data["dataset"]["version_a"][0]

    print(trace_a1["steps"][0])
    print(get_tool_sequence(trace_a1))
    print(get_args(trace_a1, 1))
    print(get_args(trace_a1, 0))
    print(semantic_diff(trace_a1["steps"], data["dataset"]["version_b"][0]["steps"]))

    trace_a10 = data["dataset"]["version_a"][9]
    trace_b7 = data["dataset"]["version_b"][6]
    print(get_tool_sequence(trace_a10))
    print(get_tool_sequence(trace_b7))
    print(exact_diff(get_tool_sequence(trace_a10), get_tool_sequence(trace_b7)))

    print(get_latencies(trace_a1))
    print(get_latencies(trace_a10))

    all_latencies = []
    for run in data["dataset"]["version_a"]:
        all_latencies.extend(get_latencies(run))
    print(all_latencies)

    print(check_consistency(all_latencies))