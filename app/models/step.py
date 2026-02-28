from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Step(Base):
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("runs.id"), nullable=False)
    step_type: Mapped[str] = mapped_column(String(20), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    input_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    triggered_loop: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    run: Mapped["Run"] = relationship("Run", back_populates="steps")
