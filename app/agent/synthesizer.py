import re

from app.agent.llm import chat

_SYSTEM = (
    "You are a research analyst. Given a query and a set of source materials, write a "
    "comprehensive, well-structured markdown report. Include an executive summary, key "
    "findings, relevant comparisons, and conclusions. "
    "Do not include inline citations, footnotes, or source references of any kind in the "
    "report body — write it as plain narrative prose, tables, and lists. A separate sources "
    "list is appended automatically after your report, so do not write one yourself. "
    "Use only plain markdown syntax — never raw HTML tags such as <br>. Inside a markdown "
    "table cell, separate multiple points with '; ' instead of a line break. "
    "Be specific and factual — base your report only on the provided source materials."
)


def _dedupe_by_url(results: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped = []
    for r in results:
        url = r.get("url") or ""
        if url and url not in seen:
            seen.add(url)
            deduped.append(r)
    return deduped


def _format_sources(results: list[dict]) -> tuple[str, list[dict]]:
    deduped = _dedupe_by_url(results)[:30]
    lines = []
    for r in deduped:
        lines.append(f"Title: {r.get('title', '')}\nURL: {r.get('url', '')}\n{r.get('content', '')[:400]}\n")
    return "\n".join(lines), deduped


def _build_sources_section(deduped_sources: list[dict]) -> str:
    if not deduped_sources:
        return ""
    lines = ["\n\n---\n\n## Sources\n"]
    for r in deduped_sources:
        title = r.get("title") or r.get("url") or "Untitled source"
        url = r.get("url") or ""
        lines.append(f"- [{title}]({url})" if url else f"- {title}")
    return "\n".join(lines)


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _fix_bracket_citations(report: str, results: list[dict]) -> str:
    """gpt-oss-120b sometimes ignores the no-citations instruction and falls back to its
    own 【Title】 citation style out of habit. Turn any that slip through into real links by
    matching the bracketed text against the actual source list; strip to plain text if not."""

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
    formatted, deduped_sources = _format_sources(results)
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": f"Research query: {query}\n\nSource materials:\n{formatted}"},
    ]
    report = chat(messages, reasoning_effort="medium")
    report = _fix_bracket_citations(report, results)  # safety net if old habits slip through
    report += _build_sources_section(deduped_sources)
    return {"report": report}
