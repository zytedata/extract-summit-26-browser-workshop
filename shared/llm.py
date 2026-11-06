"""Ask a model about a page, through OpenRouter.

OpenRouter is one API in front of many models (Claude, Gemini, GPT, Llama,
Mistral, ...). One key, and you switch models by changing a string. The model
comes from --model, or OPENROUTER_MODEL in .env, or DEFAULT_MODEL below.

It's a single HTTP POST, no SDK. What goes in: a system prompt, the
screenshot as a base64 image, the page text. What comes back: JSON that
matches the schema you asked for, plus token counts and the cost.
"""

import base64
import json
import os
import re
import time
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv(".env.local")  # wins if both exist
load_dotenv()

URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-haiku-5.5"


def model_name(override=None):
    return override or os.environ.get("OPENROUTER_MODEL") or DEFAULT_MODEL


def image_part(jpeg_bytes):
    data = base64.b64encode(jpeg_bytes).decode()
    return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{data}"}}


def text_part(text):
    return {"type": "text", "text": text}


def ask(system, parts, schema, model=None):
    """Send one message, get back (answer dict, stats dict)."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set. Add it to .env, see the main README.")
    model = model_name(model)
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": parts},
        ],
        # Ask for JSON in this exact shape. Most models support it, the
        # prompt also asks for JSON as a fallback for the ones that don't.
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "answer", "strict": True, "schema": schema},
        },
        "max_tokens": 4000,
        "usage": {"include": True},
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"OpenRouter said {e.code}: {e.read().decode()[:500]}")
    if "error" in data:
        raise SystemExit(f"OpenRouter error: {data['error']}")

    text = data["choices"][0]["message"]["content"] or ""
    usage = data.get("usage", {})
    stats = {
        "model": data.get("model", model),
        "seconds": round(time.time() - start, 1),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "cost_usd": usage.get("cost"),
    }
    return parse_json(text), stats


def parse_json(text):
    """Models without structured output sometimes wrap JSON in ```json fences."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise SystemExit(f"Model did not return JSON:\n{text[:1000]}")
