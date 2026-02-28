from app.agent.search_client import search as tavily_search


def run(sub_questions: list[str]) -> dict:
    all_results = []
    for question in sub_questions:
        results = tavily_search(question)
        all_results.extend(results)
    return {"queries": sub_questions, "results": all_results}
