from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.agent.pipeline import run_pipeline
from app.api.ws import emit
from app.database import get_db
from app.schemas.run import Run, RunCreate, RunWithSteps

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("", response_model=list[Run])
def list_runs(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    return crud.list_runs(db, limit=limit, offset=offset)


@router.get("/{run_id}", response_model=RunWithSteps)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = crud.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("", response_model=Run, status_code=201)
def create_run(payload: RunCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    run = crud.create_run(db, payload)
    background_tasks.add_task(run_pipeline, run.id, run.query, emit)
    return run


@router.post("/{run_id}/fork", response_model=Run, status_code=201)
def fork_run(run_id: int, payload: RunCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    original = crud.get_run(db, run_id)
    if not original:
        raise HTTPException(status_code=404, detail="Run not found")
    run = crud.fork_run(db, original_run_id=run_id, new_query=payload.query, user_id=payload.user_id)
    background_tasks.add_task(run_pipeline, run.id, run.query, emit)
    return run
