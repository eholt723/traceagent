from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    uuid: str
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
