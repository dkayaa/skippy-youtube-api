import logging
import threading
from collections.abc import Callable
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from backend.database import get_engine
from backend.models import Video
from backend.pipeline import (
    PIPELINE_VERSION,
    STATUS_FAILED,
    STATUS_READY,
    get_model_version,
    serialize_intervals,
)

logger = logging.getLogger(__name__)

_active_jobs: set[str] = set()
_lock = threading.Lock()


def is_analysis_active(video_id: str) -> bool:
    with _lock:
        return video_id in _active_jobs


def start_analysis_job(video_id: str, compute_analysis: Callable[[], dict]) -> None:
    with _lock:
        if video_id in _active_jobs:
            logger.info(
                "Analysis job already running; skipping duplicate start video_id=%s",
                video_id,
            )
            return
        _active_jobs.add(video_id)

    logger.info("Starting analysis job video_id=%s", video_id)
    thread = threading.Thread(
        target=_run_analysis,
        args=(video_id, compute_analysis),
        daemon=True,
    )
    thread.start()


def _run_analysis(video_id: str, compute_analysis: Callable[[], dict]) -> None:
    session_factory = sessionmaker(bind=get_engine())
    session = session_factory()
    try:
        current_model = get_model_version()
        logger.info(
            "Running analysis video_id=%s model=%s",
            video_id,
            current_model,
        )
        result = compute_analysis()
        video = session.scalar(select(Video).where(Video.video_id == video_id))
        if video is None:
            logger.warning(
                "Analysis finished but video row missing video_id=%s",
                video_id,
            )
            return

        intervals = serialize_intervals(result["intervals"])
        video.intervals_json = intervals
        video.model_version = current_model
        video.pipeline_version = PIPELINE_VERSION
        video.transcript_hash = result.get("transcript_hash")
        video.computed_at = datetime.now(timezone.utc)
        video.status = STATUS_READY
        video.error_message = None
        session.commit()
        logger.info(
            "Analysis completed video_id=%s interval_count=%d transcript_hash=%s",
            video_id,
            len(intervals),
            result.get("transcript_hash"),
        )
    except Exception as exc:
        logger.exception("Analysis failed video_id=%s", video_id)
        video = session.scalar(select(Video).where(Video.video_id == video_id))
        if video is not None:
            video.status = STATUS_FAILED
            video.error_message = str(exc)
            session.commit()
    finally:
        session.close()
        with _lock:
            _active_jobs.discard(video_id)
