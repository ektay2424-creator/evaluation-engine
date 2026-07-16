import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "parser"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "patterns"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "classifier"))

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

from pattern_matcher import match_patterns
from classifier import classify
from report_builder import build_report

app = FastAPI(title="Evaluation Engine API")


class CompareRequest(BaseModel):
    trace_a: Dict[str, Any]
    trace_b: Dict[str, Any]


@app.post("/compare")
def compare_traces(request: CompareRequest):
    result = match_patterns(request.trace_a, request.trace_b)
    classification = classify(result["findings"])
    report = build_report(request.trace_a, request.trace_b, result["findings"], classification)
    return report


@app.get("/health")
def health_check():
    return {"status": "ok"}