from app.agent.llm import chat_json

_SYSTEM = (
    "You are a research planner. Given a research query, decompose it into "
    "2 to 4 focused sub-questions that together will fully answer the main query. "
    "Return JSON with a single key: {\"sub_questions\": [\"...\", ...]}"
)


def run(query: str) -> dict:
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": query},
    ]
    result = chat_json(messages)
    if "sub_questions" not in result or not isinstance(result["sub_questions"], list):
        result = {"sub_questions": [query]}
    return result
