import json

from groq import Groq

from app.config import settings

_client = Groq(api_key=settings.groq_api_key)


def chat(messages: list[dict], json_mode: bool = False) -> str:
    kwargs = {"model": settings.groq_model, "messages": messages}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = _client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def chat_json(messages: list[dict]) -> dict:
    raw = chat(messages, json_mode=True)
    return json.loads(raw)
