import sys
import os
sys.path.append("parser")
sys.path.append("patterns")
sys.path.append("classifier")

import json
from trace_parser import load_trace
from pattern_matcher import match_patterns
from classifier import classify
from report_builder import build_report

data = load_trace("mock_trace/real_traces.json")
trace_a10 = data["dataset"]["version_a"][9]
trace_b7 = data["dataset"]["version_b"][6]

result = match_patterns(trace_a10, trace_b7)
classification = classify(result["findings"])
report = build_report(trace_a10, trace_b7, result["findings"], classification)

print(json.dumps(report, indent=2))