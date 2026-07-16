import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "thresholds.json")


def _load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


_config = _load_config()
PATTERN_WEIGHTS = _config["pattern_weights"]
WARN_THRESHOLD = _config["warn_threshold"]


def compute_score(findings):
    scored_findings = [f for f in findings if f["pattern"] in PATTERN_WEIGHTS]
    total_score = sum(PATTERN_WEIGHTS[f["pattern"]] for f in scored_findings)

    return {
        "total_score": total_score,
        "scored_findings": scored_findings,
        "exceeds_warn_threshold": total_score >= WARN_THRESHOLD
    }