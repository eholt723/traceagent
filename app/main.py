from fastapi import FastAPI

app = FastAPI(title="TraceAgent", description="Observable Agentic Research Platform")


@app.get("/health")
def health():
    return {"status": "ok"}
