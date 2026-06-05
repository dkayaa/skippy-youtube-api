from collections.abc import Callable
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Video
from backend.pipeline import (
    PIPELINE_VERSION,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_READY,
    get_model_version,
)


class IntervalStore:
    def __init__(self, session: Session):
        self._session = session

    def get_or_create_intervals(
        self,
        video_id: str,
        compute_analysis: Callable[[], dict],
    ) -> list[dict]:
        current_model = get_model_version()
        video = self._session.scalar(select(Video).where(Video.video_id == video_id))

        if video is not None and self._has_cached_intervals(video):
            if self._needs_recompute(video, current_model):
                pass
            else:
                if video.model_version in (None, "migrated"):
                    self._backfill_metadata(video, current_model)
                    self._session.commit()
                return self._to_response(video.intervals_json)

        if video is None:
            video = Video(video_id=video_id, status=STATUS_PENDING)
            self._session.add(video)
        else:
            video.status = STATUS_PENDING
            video.error_message = None

        self._session.commit()

        try:
            result = compute_analysis()
            video.intervals_json = self._serialize_intervals(result["intervals"])
            video.model_version = current_model
            video.pipeline_version = PIPELINE_VERSION
            video.transcript_hash = result.get("transcript_hash")
            video.computed_at = datetime.now(timezone.utc)
            video.status = STATUS_READY
            video.error_message = None
        except Exception as exc:
            video.status = STATUS_FAILED
            video.error_message = str(exc)
            self._session.commit()
            raise

        self._session.commit()
        return self._to_response(video.intervals_json)

    @staticmethod
    def _has_cached_intervals(video: Video) -> bool:
        return video.status == STATUS_READY and video.intervals_json is not None

    @staticmethod
    def _needs_recompute(video: Video, current_model: str) -> bool:
        if video.pipeline_version != PIPELINE_VERSION:
            return True
        if video.model_version in (None, "migrated"):
            return False
        return video.model_version != current_model

    def _backfill_metadata(self, video: Video, current_model: str) -> None:
        video.model_version = current_model
        video.pipeline_version = PIPELINE_VERSION
        if video.computed_at is None:
            video.computed_at = datetime.now(timezone.utc)

    @staticmethod
    def _serialize_intervals(intervals: list[dict]) -> list[dict]:
        return [
            {
                "start_time": item["start_time"],
                "end_time": item["end_time"],
                "orgs": item["orgs"],
            }
            for item in intervals
        ]

    @staticmethod
    def _to_response(intervals_json: list[dict] | None) -> list[dict]:
        if not intervals_json:
            return []

        return [
            {
                "id": index + 1,
                "start_time": int(item["start_time"]),
                "end_time": int(item["end_time"]),
                "orgs": item["orgs"],
            }
            for index, item in enumerate(intervals_json)
        ]
