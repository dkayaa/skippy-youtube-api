from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Interval, Video


class IntervalStore:
    def __init__(self, session: Session):
        self._session = session

    def get_or_create_intervals(
        self,
        video_id: str,
        compute_intervals: Callable[[], list[dict]],
    ) -> list[dict]:
        video = self._session.scalar(select(Video).where(Video.video_id == video_id))

        if video is None:
            computed = compute_intervals()
            video = Video(video_id=video_id)
            self._session.add(video)
            self._session.flush()

            for item in computed:
                self._session.add(
                    Interval(
                        start_time=item["start_time"],
                        end_time=item["end_time"],
                        orgs="|".join(item["orgs"]),
                        video_fk=video.pk,
                    )
                )

            self._session.commit()
            intervals = self._session.scalars(
                select(Interval).where(Interval.video_fk == video.pk)
            ).all()
            return self._to_response(intervals)

        intervals = self._session.scalars(
            select(Interval).where(Interval.video_fk == video.pk)
        ).all()
        return self._to_response(intervals)

    @staticmethod
    def _to_response(intervals: list[Interval]) -> list[dict]:
        return [
            {
                "id": interval.pk,
                "start_time": int(interval.start_time),
                "end_time": int(interval.end_time),
                "orgs": interval.orgs.split("|") if interval.orgs else [],
            }
            for interval in intervals
        ]
