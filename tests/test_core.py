from sqlalchemy import inspect
from unittest.mock import patch

from app.agent import planner, reflector


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
