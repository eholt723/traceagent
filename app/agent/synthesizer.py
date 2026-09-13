import re

from app.agent.llm import chat

_SYSTEM = (
    "You are a research analyst. Given a query and search results, write a comprehensive, "
    "well-structured markdown report. Include an executive summary, key findings, "
    "relevant comparisons, and conclusions. "
    "When citing sources, you MUST use inline markdown links in the exact format [Title](URL), "
    "with the real URL from the sources list. "
    "Do NOT use bracketed citation markers like 【Title】 or [1] — every citation must be a clickable "
    "markdown link with a URL, never a bare title in brackets. "
    "Only cite sources that appear in the provided list — do not invent citations. "
    "Be specific and factual — base your report only on the provided results."
)


def _format_results(results: list[dict]) -> str:
    lines = []
    for r in results[:30]:
        lines.append(f"Title: {r.get('title', '')}\nURL: {r.get('url', '')}\n{r.get('content', '')[:400]}\n")
    return "\n".join(lines)


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _fix_bracket_citations(report: str, results: list[dict]) -> str:
    """gpt-oss-120b sometimes ignores the [Title](URL) instruction and falls back to its
    own 【Title】 citation style. Turn any that slip through into real links by matching
    the bracketed text against the actual source list; strip to plain text if no match."""

    def replace(match: re.Match) -> str:
        raw = match.group(1).strip()
        norm_raw = _normalize(raw)
        if norm_raw:
            for r in results:
                title = (r.get("title") or "").strip()
                url = r.get("url") or ""
                norm_title = _normalize(title)
                if title and url and norm_title and (norm_title in norm_raw or norm_raw in norm_title):
                    return f"[{title}]({url})"
        return raw

    return re.sub(r"【([^【】]*)】", replace, report)


def run(query: str, results: list[dict]) -> dict:
    formatted = _format_results(results)
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": f"Research query: {query}\n\nSources:\n{formatted}"},
    ]
    report = chat(messages, reasoning_effort="medium")
    report = _fix_bracket_citations(report, results)
    return {"report": report}
