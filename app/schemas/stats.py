from pydantic import BaseModel


class Stats(BaseModel):
    total_runs: int
    completed_runs: int
    failed_runs: int
    success_rate: int        # 0-100 integer percent
    avg_duration_ms: int     # average pipeline wall-clock time in ms
    avg_steps_per_run: float
    reflection_loop_rate: int  # % of completed runs that triggered a loop
    runs_with_loops: int
