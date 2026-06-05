import os

import torch
from dotenv import load_dotenv
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
from youtube_transcript_api import YouTubeTranscriptApi

from org_extractor import get_orgs

ytt_api = YouTubeTranscriptApi()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

model_name = os.getenv("HUGGINGFACE_MODEL")
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForSequenceClassification.from_pretrained(model_name)

WINDOW_SIZE = 10
STRIDE = 5
BATCH_SIZE = int(os.getenv("CLASSIFIER_BATCH_SIZE", "32"))


def _get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


DEVICE = _get_device()
model.to(DEVICE)
model.eval()


class TranscriptFetchError(RuntimeError):
    """Raised when the YouTube transcript cannot be fetched."""


def _build_windows(fetched_transcript) -> list[tuple[str, float]]:
    windows = []
    for index in range(0, len(fetched_transcript) - WINDOW_SIZE, STRIDE):
        segment_text = " ".join(
            snippet.text for snippet in fetched_transcript[index : index + WINDOW_SIZE]
        )
        segment_start = fetched_transcript[index].start
        windows.append((segment_text, segment_start))
    return windows


def _classify_windows(texts: list[str]) -> list[int]:
    labels: list[int] = []
    for index in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[index : index + BATCH_SIZE]
        inputs = tokenizer(
            batch_texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
        )
        inputs = {key: value.to(DEVICE) for key, value in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        labels.extend(torch.argmax(outputs.logits, dim=1).tolist())
    return labels


def get_labelled_tscript(video_id: str) -> list[dict]:
    try:
        fetched_transcript = ytt_api.fetch(video_id)
    except Exception as exc:
        raise TranscriptFetchError(
            f"Failed to fetch transcript for video {video_id}"
        ) from exc

    if not fetched_transcript:
        return []

    windows = _build_windows(fetched_transcript)
    if not windows:
        return []

    texts = [window[0] for window in windows]
    labels = _classify_windows(texts)

    segments = []
    for (segment_text, segment_start), predicted_class in zip(windows, labels):
        orgs = get_orgs(segment_text) if predicted_class == 1 else []
        segments.append(
            {
                "text": segment_text,
                "start": segment_start,
                "label": predicted_class,
                "orgs": orgs,
            }
        )

    return segments


def compute_intervals(data, interval_threshold=5, min_duration=45):
    """
    input: list of dicts with keys 'text', 'start', 'label'

    output: list of dicts with keys 'start_time', 'end_time'
    """

    data.sort(key=lambda x: x["start"])

    intervals = []

    for i in range(0, len(data) - 1):
        if data[i]["label"] == 0:
            continue
        intervals.append(
            {
                "start_time": data[i]["start"],
                "end_time": data[i + 1]["start"],
                "orgs": data[i].get("orgs", []),
            }
        )

    intervals_merged = []

    i = 0
    while i < len(intervals):
        intervals_merged.append(intervals[i].copy())
        for j in range(i, len(intervals)):
            if (
                intervals[j]["start_time"] - intervals_merged[-1]["end_time"]
                <= interval_threshold
            ):
                intervals_merged[-1]["end_time"] = intervals[j]["end_time"]
                intervals_merged[-1]["orgs"] = list(
                    set(
                        intervals_merged[-1].get("orgs", [])
                        + intervals[j].get("orgs", [])
                    )
                )
                i += 1
            else:
                i = j
                break

    intervals_merged = [
        x
        for x in intervals_merged
        if x["end_time"] - x["start_time"] > min_duration
    ]

    for interval in intervals_merged:
        if len(interval["orgs"]) == 0:
            interval["orgs"] = ["UNKNOWN"]

    return intervals_merged
