from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class StepType(str, Enum):
    planner = "planner"
    search = "search"
    reflection = "reflection"
    synthesis = "synthesis"


class StepBase(BaseModel):
    step_type: StepType
    step_order: int
    input_data: dict[str, Any] | None = None


class StepCreate(StepBase):
    run_id: int


class Step(StepBase):
    id: int
    run_id: int
    output_data: dict[str, Any] | None
    created_at: datetime
    duration_ms: int | None
    triggered_loop: bool

    model_config = ConfigDict(from_attributes=True)
