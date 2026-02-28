from app.agent.llm import chat_json

_SYSTEM = (
    "You are a research quality evaluator. Given a research query and a set of search results, "
    "decide if the results are sufficient to write a comprehensive, well-sourced report. "
    "If not, provide 1 to 3 refined search queries to fill the gaps. "
    'Return JSON: {"adequate": true/false, "reason": "...", "refined_queries": ["..."]}'
)


def _summarize_results(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results[:20], 1):
        lines.append(f"{i}. [{r.get('title', '')}] {r.get('content', '')[:200]}")
    return "\n".join(lines)


def run(query: str, results: list[dict]) -> dict:
    summary = _summarize_results(results)
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": f"Query: {query}\n\nSearch results:\n{summary}"},
    ]
    result = chat_json(messages)
    if "adequate" not in result:
        result = {"adequate": True, "reason": "defaulting to adequate", "refined_queries": []}
    if "refined_queries" not in result:
        result["refined_queries"] = []
    return result
