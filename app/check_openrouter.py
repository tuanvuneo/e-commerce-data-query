import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv(
        "OPENROUTER_MODEL",
        "nvidia/nemotron-3.5-super-vl:free"
    ).strip()
    provider = os.getenv(
        "OPENROUTER_PROVIDER",
        "nvidia"
    ).strip()

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": model,
                "provider": {
                    "only": [provider],
                    "allow_fallbacks": False,
                },
                "messages": [
                    {
                        "role": "system",
                        "content": "Reply only in English",
                    },
                    {
                        "role": "user",
                        "content": (
                            "Reply with exactly: "
                            "OpenRouter connection successful."
                        ),
                    },
                ],
                "temperature": 0,
                "reasoning": {"enabled": False},
                "max_tokens": 512,
                "stream": False,
            },
            timeout=60.0,
        )
        response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        raise SystemExit(
            f"OpenRouter returned HTTP {exc.response.status_code}. "
            "Check your API key, credits, model, and allowed provider."
        ) from None

    except httpx.RequestError:
        raise SystemExit(
            "Could not reach OpenRouter. "
            "Check your network connection and try again."
        ) from None

    data = response.json()
    choices = data.get("choices", [])

    if not choices:
        raise SystemExit(
            "OpenRouter returned no choices. "
            "Check your OpenRouter account activity."
        )

    reply = choices[0]["message"].get("content")

    if not isinstance(reply, str) or not reply.strip():
        raise SystemExit("OpenRouter returned no text.")

    print("Model:", data.get("model", model))
    print("Provider:", data.get("provider", "not reported"))
    print("Reply:", reply.strip())

if __name__ == "__main__":
    main()
