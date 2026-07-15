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
            continue  # skip non-tool-call steps (user_message, assistant_message, etc.)

        if step_a["tool"] != step_b["tool"]:
            continue  # different tools entirely — exact_diff already flags this

        args_a = step_a["arguments"]
        args_b = step_b["arguments"]

        for key in args_a:
            if key in args_b and args_a[key] != args_b[key]:
                differences.append({
                    "position": i,
                    "tool": step_a["tool"],
                    "argument": key,
                    "version_a_value": args_a[key],
                    "version_b_value": args_b[key]
                })

    return differences

import statistics


def check_consistency(latencies, threshold_std=1.0):
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

    print(trace_a1["steps"][0])   # <-- add this line to inspect the real structure

    print(get_tool_sequence(trace_a1))

print(get_args(trace_a1, 1))   
print(get_args(trace_a1, 0))   
print(semantic_diff(trace_a1["steps"], data["dataset"]["version_b"][0]["steps"]))
trace_a10 = data["dataset"]["version_a"][9]   # A-010
trace_b7 = data["dataset"]["version_b"][6]    # B-007

print(get_tool_sequence(trace_a10))
print(get_tool_sequence(trace_b7))

seq_a10 = get_tool_sequence(trace_a10)
seq_b7 = get_tool_sequence(trace_b7)

print(exact_diff(seq_a10, seq_b7))