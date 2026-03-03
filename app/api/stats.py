from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.stats import Stats

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=Stats)
def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)
