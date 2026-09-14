import json
import re

from groq import Groq

from app.config import settings

_client = Groq(api_key=settings.groq_api_key)


def chat(messages: list[dict], json_mode: bool = False, reasoning_effort: str = "low") -> str:
    kwargs = {
        "model": settings.groq_model,
        "messages": messages,
        "reasoning_effort": reasoning_effort,
        "include_reasoning": False,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = _client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def chat_json(messages: list[dict]) -> dict:
    """Callers (planner, reflector) already fall back gracefully when the returned
    dict is missing expected keys, so on malformed output we return {} rather than
    raising and killing the whole pipeline run. gpt-oss occasionally wraps JSON mode
    output in markdown fences or leaks stray text despite include_reasoning=False."""
    raw = chat(messages, json_mode=True)
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}
