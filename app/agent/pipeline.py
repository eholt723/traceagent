import asyncio
from collections.abc import Callable
from datetime import datetime, timezone

from app.agent import planner, searcher, reflector, synthesizer
from app.config import settings
from app.crud import create_step, update_run_status
from app.database import SessionLocal
from app.schemas.step import StepCreate, StepType


def _now_ms(start: datetime) -> int:
    return int((datetime.now(timezone.utc) - start).total_seconds() * 1000)


def _step_payload(step, run_id: int) -> dict:
    return {
        "id": step.id,
        "run_id": run_id,
        "step_type": step.step_type,
        "step_order": step.step_order,
        "input_data": step.input_data,
        "output_data": step.output_data,
        "duration_ms": step.duration_ms,
        "triggered_loop": step.triggered_loop,
    }


async def run_pipeline(run_id: int, query: str, emit: Callable) -> None:
    db = SessionLocal()
    try:
        update_run_status(db, run_id, "running")
        step_order = 0

        # Step 1: Planner
        step_order += 1
        t0 = datetime.now(timezone.utc)
        plan = await asyncio.to_thread(planner.run, query)
        step = create_step(db, StepCreate(
            run_id=run_id,
            step_type=StepType.planner,
            step_order=step_order,
            input_data={"query": query},
            output_data=plan,
            duration_ms=_now_ms(t0),
        ))
        await emit(run_id, "step_complete", _step_payload(step, run_id))

        sub_questions = plan.get("sub_questions", [query])
        all_results: list[dict] = []
        loop_count = 0

        while loop_count <= settings.max_search_loops:
            # Search
            step_order += 1
            t0 = datetime.now(timezone.utc)
            search_out = await asyncio.to_thread(searcher.run, sub_questions)
            all_results.extend(search_out["results"])
            step = create_step(db, StepCreate(
                run_id=run_id,
                step_type=StepType.search,
                step_order=step_order,
                input_data={"queries": sub_questions},
                output_data={"result_count": len(search_out["results"]), "results": search_out["results"]},
                duration_ms=_now_ms(t0),
            ))
            await emit(run_id, "step_complete", _step_payload(step, run_id))

            # Reflection
            step_order += 1
            t0 = datetime.now(timezone.utc)
            reflection = await asyncio.to_thread(reflector.run, query, all_results)
            triggered_loop = not reflection["adequate"]
            step = create_step(db, StepCreate(
                run_id=run_id,
                step_type=StepType.reflection,
                step_order=step_order,
                input_data={"query": query, "result_count": len(all_results)},
                output_data=reflection,
                duration_ms=_now_ms(t0),
                triggered_loop=triggered_loop,
            ))
            await emit(run_id, "step_complete", _step_payload(step, run_id))

            if reflection["adequate"]:
                break
            sub_questions = reflection.get("refined_queries", [query])
            loop_count += 1

        # Synthesis
        step_order += 1
        t0 = datetime.now(timezone.utc)
        synthesis = await asyncio.to_thread(synthesizer.run, query, all_results)
        step = create_step(db, StepCreate(
            run_id=run_id,
            step_type=StepType.synthesis,
            step_order=step_order,
            input_data={"query": query, "result_count": len(all_results)},
            output_data=synthesis,
            duration_ms=_now_ms(t0),
        ))
        await emit(run_id, "step_complete", _step_payload(step, run_id))

        update_run_status(db, run_id, "complete",
                          ended_at=datetime.now(timezone.utc),
                          step_count=step_order)
        await emit(run_id, "run_complete", {"run_id": run_id})

    except Exception as exc:
        update_run_status(db, run_id, "failed", ended_at=datetime.now(timezone.utc))
        await emit(run_id, "run_error", {"run_id": run_id, "error": str(exc)})
    finally:
        await emit(run_id, None, None)  # sentinel — close WebSocket
        db.close()
