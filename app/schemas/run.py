from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.schemas.step import Step


class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    complete = "complete"
    failed = "failed"


class RunBase(BaseModel):
    query: str
    is_public: bool = True


class RunCreate(RunBase):
    user_id: int | None = None
    forked_from_id: int | None = None


class Run(RunBase):
    id: int
    user_id: int | None
    status: RunStatus
    started_at: datetime
    ended_at: datetime | None
    step_count: int
    forked_from_id: int | None

    model_config = ConfigDict(from_attributes=True)


class RunWithSteps(Run):
    steps: list[Step] = []
