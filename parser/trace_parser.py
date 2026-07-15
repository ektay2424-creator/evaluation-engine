import json


def load_trace(filepath):
    with open(filepath, "r") as f:
        trace = json.load(f)
    return trace


if __name__ == "__main__":
    trace = load_trace("schemas/trace_schema.json")
    print(trace)
