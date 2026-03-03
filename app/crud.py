from datetime import datetime, timezone

from sqlalchemy import case, distinct, func
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


# --- Stats ---

def get_stats(db: Session) -> dict:
    counts = db.query(
        func.count(Run.id).label("total"),
        func.sum(case((Run.status == "complete", 1), else_=0)).label("completed"),
        func.sum(case((Run.status == "failed", 1), else_=0)).label("failed"),
    ).filter(Run.is_public == True).one()

    total = counts.total or 0
    completed = int(counts.completed or 0)
    failed = int(counts.failed or 0)
    finished = completed + failed
    success_rate = round(completed / finished * 100) if finished > 0 else 0

    avg_dur = db.query(
        func.avg(
            func.extract("epoch", Run.ended_at) -
            func.extract("epoch", Run.started_at)
        )
    ).filter(Run.status == "complete", Run.ended_at.isnot(None)).scalar()

    avg_steps = db.query(func.avg(Run.step_count)).filter(
        Run.status == "complete"
    ).scalar()

    runs_with_loops = db.query(
        func.count(distinct(Step.run_id))
    ).join(Run, Step.run_id == Run.id).filter(
        Step.triggered_loop == True,
        Run.status == "complete",
        Run.is_public == True,
    ).scalar() or 0

    loop_rate = round(runs_with_loops / completed * 100) if completed > 0 else 0

    return {
        "total_runs": total,
        "completed_runs": completed,
        "failed_runs": failed,
        "success_rate": success_rate,
        "avg_duration_ms": round(avg_dur * 1000) if avg_dur else 0,
        "avg_steps_per_run": round(float(avg_steps), 1) if avg_steps else 0.0,
        "reflection_loop_rate": loop_rate,
        "runs_with_loops": runs_with_loops,
    }


def get_steps_for_run(db: Session, run_id: int) -> list[Step]:
    return (
        db.query(Step)
        .filter(Step.run_id == run_id)
        .order_by(Step.step_order)
        .all()
    )
