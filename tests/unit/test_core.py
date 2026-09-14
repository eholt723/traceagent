import pytest
from sqlalchemy import inspect
from unittest.mock import patch

from app.agent import planner, reflector, synthesizer
from app.agent.llm import chat_json


def test_tables_exist(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "runs" in tables
    assert "steps" in tables


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_planner_returns_sub_questions():
    with patch("app.agent.planner.chat_json", return_value={"sub_questions": ["q1", "q2"]}):
        result = planner.run("what is quantum computing?")
    assert "sub_questions" in result
    assert len(result["sub_questions"]) == 2


def test_planner_fallback_on_bad_llm_response():
    with patch("app.agent.planner.chat_json", return_value={"unexpected": "key"}):
        result = planner.run("what is quantum computing?")
    assert result == {"sub_questions": ["what is quantum computing?"]}


def test_reflector_adequate():
    with patch("app.agent.reflector.chat_json", return_value={
        "adequate": True,
        "reason": "sufficient coverage",
        "refined_queries": [],
    }):
        result = reflector.run("test query", [{"title": "t", "content": "c", "url": "u"}])
    assert result["adequate"] is True


def test_reflector_inadequate_provides_refined_queries():
    with patch("app.agent.reflector.chat_json", return_value={
        "adequate": False,
        "reason": "needs more sources",
        "refined_queries": ["better query"],
    }):
        result = reflector.run("test query", [])
    assert result["adequate"] is False
    assert len(result["refined_queries"]) > 0


def test_reflector_fallback_on_missing_adequate_key():
    with patch("app.agent.reflector.chat_json", return_value={"reason": "no adequate key"}):
        result = reflector.run("test query", [])
    assert result["adequate"] is True  # defaults to adequate per reflector fallback logic


@pytest.mark.parametrize("bad_response", [
    {},
    {"unexpected": "key"},
    {"sub_questions": None},
    {"sub_questions": "not a list"},
])
def test_planner_fallback_on_various_bad_responses(bad_response):
    with patch("app.agent.planner.chat_json", return_value=bad_response):
        result = planner.run("what is quantum computing?")
    assert result == {"sub_questions": ["what is quantum computing?"]}


def test_synthesizer_run_returns_report():
    with patch("app.agent.synthesizer.chat", return_value="A report with no citations."):
        result = synthesizer.run("test query", [{"title": "t", "url": "u", "content": "c"}])
    assert result == {"report": "A report with no citations."}


def test_fix_bracket_citations_converts_exact_title_match():
    results = [{"title": "Beneficial effects of intermittent fasting: a narrative review - PMC",
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9946909"}]
    report = "Weight loss is well documented 【Beneficial effects of intermittent fasting: a narrative review - PMC】."
    fixed = synthesizer._fix_bracket_citations(report, results)
    assert fixed == (
        "Weight loss is well documented "
        "[Beneficial effects of intermittent fasting: a narrative review - PMC]"
        "(https://pmc.ncbi.nlm.nih.gov/articles/PMC9946909)."
    )


def test_fix_bracket_citations_matches_truncated_title():
    results = [{"title": "Intermittent fasting strategies and their effects on body weight and metabolism",
                "url": "https://example.com/ifs"}]
    report = "Adherence varies 【Intermittent fasting strategies and their effects on body weight and ...】."
    fixed = synthesizer._fix_bracket_citations(report, results)
    assert "[Intermittent fasting strategies and their effects on body weight and metabolism](https://example.com/ifs)" in fixed
    assert "【" not in fixed and "】" not in fixed


def test_fix_bracket_citations_strips_unmatched_bracket():
    report = "Something claimed 【a citation with no matching source at all】."
    fixed = synthesizer._fix_bracket_citations(report, [{"title": "Unrelated source", "url": "https://example.com"}])
    assert fixed == "Something claimed a citation with no matching source at all."


def test_fix_bracket_citations_noop_when_no_brackets_present():
    report = "A clean report with a real [markdown link](https://example.com) and no brackets."
    fixed = synthesizer._fix_bracket_citations(report, [{"title": "x", "url": "https://example.com"}])
    assert fixed == report


def test_dedupe_by_url_removes_repeats_across_search_rounds():
    results = [
        {"title": "A", "url": "https://a.com"},
        {"title": "A dup", "url": "https://a.com"},
        {"title": "B", "url": "https://b.com"},
        {"title": "No url"},
    ]
    deduped = synthesizer._dedupe_by_url(results)
    assert [r["url"] for r in deduped] == ["https://a.com", "https://b.com"]


def test_format_sources_numbers_sequentially():
    results = [{"title": "First", "url": "https://a.com", "content": "x"},
               {"title": "Second", "url": "https://b.com", "content": "y"}]
    formatted, numbered = synthesizer._format_sources(results)
    assert "[1] Title: First" in formatted
    assert "[2] Title: Second" in formatted
    assert numbered == results


def test_resolve_numbered_citations_converts_known_index():
    numbered = [{"title": "First Source", "url": "https://a.com"},
                {"title": "Second Source", "url": "https://b.com"}]
    report = "A claim [1] and another claim [2]."
    resolved = synthesizer._resolve_numbered_citations(report, numbered)
    assert resolved == "A claim [First Source](https://a.com) and another claim [Second Source](https://b.com)."


def test_resolve_numbered_citations_leaves_out_of_range_index_untouched():
    numbered = [{"title": "Only Source", "url": "https://a.com"}]
    report = "A claim [1] and a bogus one [99]."
    resolved = synthesizer._resolve_numbered_citations(report, numbered)
    assert resolved == "A claim [Only Source](https://a.com) and a bogus one [99]."


def test_chat_json_returns_empty_dict_on_malformed_output():
    with patch("app.agent.llm.chat", return_value="Sorry, I cannot produce JSON for that."):
        result = chat_json([{"role": "user", "content": "x"}])
    assert result == {}


def test_chat_json_strips_markdown_fences():
    with patch("app.agent.llm.chat", return_value='```json\n{"adequate": true}\n```'):
        result = chat_json([{"role": "user", "content": "x"}])
    assert result == {"adequate": True}


def test_planner_falls_back_when_chat_json_returns_empty_dict():
    with patch("app.agent.planner.chat_json", return_value={}):
        result = planner.run("what is quantum computing?")
    assert result == {"sub_questions": ["what is quantum computing?"]}


def test_reflector_falls_back_when_chat_json_returns_empty_dict():
    with patch("app.agent.reflector.chat_json", return_value={}):
        result = reflector.run("test query", [])
    assert result["adequate"] is True
