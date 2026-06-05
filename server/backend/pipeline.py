import hashlib
import json
import os

from transcript_labelling import compute_intervals, get_labelled_tscript

PIPELINE_VERSION = "2"
STATUS_PENDING = "pending"
STATUS_READY = "ready"
STATUS_FAILED = "failed"


def get_model_version() -> str:
    return os.getenv("HUGGINGFACE_MODEL", "kayaaaa/ad-classifier")


def hash_segments(segments: list[dict]) -> str | None:
    if not segments:
        return None
    payload = json.dumps([(s["start"], s["text"]) for s in segments], sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def serialize_intervals(intervals: list[dict]) -> list[dict]:
    return [
        {
            "start_time": item["start_time"],
            "end_time": item["end_time"],
            "orgs": item["orgs"],
        }
        for item in intervals
    ]


def compute_video_analysis(video_id: str) -> dict:
    segments = get_labelled_tscript(video_id)
    return {
        "intervals": compute_intervals(segments),
        "transcript_hash": hash_segments(segments),
    }
