from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.run import Run
from app.models.step import Step
from app.models.user import User
from app.schemas.run import RunCreate
from app.schemas.step import StepCreate


# --- Users ---

def get_user_by_uuid(db: Session, uuid: str) -> User | None:
    return db.query(User).filter(User.uuid == uuid).first()


def upsert_user(db: Session, uuid: str, name: str) -> User:
    user = get_user_by_uuid(db, uuid)
    if user:
        user.name = name
    else:
        user = User(uuid=uuid, name=name)
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --- Runs ---

def create_run(db: Session, run_in: RunCreate) -> Run:
    run = Run(
        **run_in.model_dump(),
        status="pending",
        started_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_run(db: Session, run_id: int) -> Run | None:
    return (
        db.query(Run)
        .options(joinedload(Run.user))
        .filter(Run.id == run_id)
        .first()
    )


def list_runs(db: Session, limit: int = 20, offset: int = 0) -> list[Run]:
    return (
        db.query(Run)
        .options(joinedload(Run.user))
        .filter(Run.is_public == True)
        .order_by(Run.started_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def update_run_status(
    db: Session,
    run_id: int,
    status: str,
    ended_at: datetime | None = None,
    step_count: int | None = None,
) -> Run | None:
    run = get_run(db, run_id)
    if not run:
        return None
    run.status = status
    if ended_at:
        run.ended_at = ended_at
    if step_count is not None:
        run.step_count = step_count
    db.commit()
    db.refresh(run)
    return run


def fork_run(db: Session, original_run_id: int, new_query: str, user_id: int | None) -> Run:
    run = Run(
        query=new_query,
        user_id=user_id,
        status="pending",
        started_at=datetime.now(timezone.utc),
        forked_from_id=original_run_id,
        is_public=True,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


# --- Steps ---

def create_step(db: Session, step_in: StepCreate) -> Step:
    step = Step(**step_in.model_dump())
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def get_steps_for_run(db: Session, run_id: int) -> list[Step]:
    return (
        db.query(Step)
        .filter(Step.run_id == run_id)
        .order_by(Step.step_order)
        .all()
    )
