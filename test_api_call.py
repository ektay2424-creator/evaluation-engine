import json
import requests

with open("mock_trace/real_traces.json", "r") as f:
    data = json.load(f)

trace_a10 = data["dataset"]["version_a"][9]
trace_b7 = data["dataset"]["version_b"][6]

response = requests.post(
    "http://127.0.0.1:8000/compare",
    json={"trace_a": trace_a10, "trace_b": trace_b7}
)

print(response.status_code)
print(json.dumps(response.json(), indent=2))