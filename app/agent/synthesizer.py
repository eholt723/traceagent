from app.agent.llm import chat

_SYSTEM = (
    "You are a research analyst. Given a query and search results, write a comprehensive, "
    "well-structured markdown report. Include an executive summary, key findings, "
    "relevant comparisons, and conclusions. Cite sources by title where relevant. "
    "Be specific and factual — base your report only on the provided results."
)


def _format_results(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results[:30], 1):
        lines.append(f"[{i}] Title: {r.get('title', '')}\nURL: {r.get('url', '')}\n{r.get('content', '')[:400]}\n")
    return "\n".join(lines)


def run(query: str, results: list[dict]) -> dict:
    formatted = _format_results(results)
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": f"Research query: {query}\n\nSources:\n{formatted}"},
    ]
    report = chat(messages)
    return {"report": report}
