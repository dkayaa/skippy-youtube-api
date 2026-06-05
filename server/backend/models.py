from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Video(Base):
    __tablename__ = "videos"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    intervals: Mapped[list["Interval"]] = relationship(
        "Interval",
        back_populates="video",
        cascade="all, delete-orphan",
    )


class Interval(Base):
    __tablename__ = "intervals"

    pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    orgs: Mapped[str] = mapped_column(String(1000), server_default="")
    video_fk: Mapped[int] = mapped_column(Integer, ForeignKey("videos.pk"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    video: Mapped["Video"] = relationship("Video", back_populates="intervals")
