from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.user import User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/upsert", response_model=User)
def upsert_user(payload: UserCreate, db: Session = Depends(get_db)):
    return crud.upsert_user(db, uuid=payload.uuid, name=payload.name)
