import re

from app.agent.llm import chat

_SYSTEM = (
    "You are a research analyst. Given a query and a numbered list of sources, write a "
    "comprehensive, well-structured markdown report. Include an executive summary, key "
    "findings, relevant comparisons, and conclusions. "
    "Cite sources with ONLY a bracketed number matching the source list, like [1] or [3], "
    "placed immediately after the claim it supports. Do not write out the source title or "
    "URL yourself, do not invent markdown links, and do not use any other citation style. "
    "Only cite numbers that appear in the provided source list — do not invent citations. "
    "Be specific and factual — base your report only on the provided results."
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
    numbered = _dedupe_by_url(results)[:30]
    lines = []
    for i, r in enumerate(numbered, start=1):
        lines.append(f"[{i}] Title: {r.get('title', '')}\nURL: {r.get('url', '')}\n{r.get('content', '')[:400]}\n")
    return "\n".join(lines), numbered


def _resolve_numbered_citations(report: str, numbered_sources: list[dict]) -> str:
    """Turn the model's [n] citation markers into real [Title](URL) links using the
    exact index it was given — deterministic, no fuzzy title matching needed."""

    def replace(match: re.Match) -> str:
        idx = int(match.group(1))
        if 1 <= idx <= len(numbered_sources):
            source = numbered_sources[idx - 1]
            title, url = source.get("title") or "", source.get("url") or ""
            if title and url:
                return f"[{title}]({url})"
        return match.group(0)

    return re.sub(r"\[(\d{1,3})\]", replace, report)


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
    formatted, numbered_sources = _format_sources(results)
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": f"Research query: {query}\n\nSources:\n{formatted}"},
    ]
    report = chat(messages, reasoning_effort="medium")
    report = _resolve_numbered_citations(report, numbered_sources)
    report = _fix_bracket_citations(report, results)  # safety net if old habits slip through
    return {"report": report}
