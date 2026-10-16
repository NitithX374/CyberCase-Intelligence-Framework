import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LLM_MODEL = "google/gemma-4-26b-a4b-it"
OCR_MODEL = "typhoon-ocr"
WAIT_SECONDS = 30 * 60


def setting(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name].strip()
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").split("\n"):
            key, _, value = line.strip().partition("=")
            if key.strip() == name:
                return value.strip().strip('"').strip("'")
    raise SystemExit(f"{name} is not set in the environment or in {env_file}")


def call(url: str, token: str, body: dict | None = None, timeout: float = 60) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=None if body is None else json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="GET" if body is None else "POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as error:
        return error.code, {}
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return 0, {}


def wait_until_healthy(name: str, origin: str, token: str) -> bool:
    started = time.monotonic()
    last = None
    while time.monotonic() - started < WAIT_SECONDS:
        status, _ = call(f"{origin}/health", token, timeout=30)
        if status != last:
            print(
                f"{name}: /health {status or 'no answer'} after {time.monotonic() - started:.0f}s"
            )
            last = status
        if status == 200:
            return True
        if status in (401, 403):
            print(f"{name}: the token was refused")
            return False
        time.sleep(5)
    print(f"{name}: not healthy after {WAIT_SECONDS // 60} minutes")
    return False


def ask(origin: str, token: str, thinking: bool) -> bool:
    body = {
        "model": LLM_MODEL,
        "max_tokens": 4096 if thinking else 256,
        "system": "Reply with one JSON object and nothing else.",
        "messages": [{"role": "user", "content": 'Return {"ok": true}.'}],
        "chat_template_kwargs": {"enable_thinking": thinking},
    }
    started = time.monotonic()
    status, reply = call(f"{origin}/v1/messages", token, body, timeout=180)
    elapsed = time.monotonic() - started
    blocks = [block.get("type") for block in reply.get("content", [])]
    text = "".join(
        block.get("text", "") for block in reply.get("content", []) if block.get("type") == "text"
    )
    print(
        f"llm thinking={thinking}: HTTP {status} in {elapsed:.1f}s stop_reason={reply.get('stop_reason')} "
        f"blocks={blocks} usage={reply.get('usage')} text={text.strip()[:120]!r}"
    )
    try:
        answered = json.loads(text.strip().removeprefix("```json").removesuffix("```")) == {
            "ok": True
        }
    except ValueError:
        answered = False
    return status == 200 and answered and (("thinking" in blocks) == thinking)


def check_llm(origin: str, token: str) -> bool:
    if not wait_until_healthy("llm", origin, token):
        return False
    return all([ask(origin, token, thinking=False), ask(origin, token, thinking=True)])


def check_ocr(origin: str, token: str) -> bool:
    if not wait_until_healthy("ocr", origin, token):
        return False
    status, listing = call(f"{origin}/v1/models", token)
    names = [model.get("id") for model in listing.get("data", [])]
    print(f"ocr: /v1/models HTTP {status} serves {names}")
    return status == 200 and OCR_MODEL in names


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    wanted = set(sys.argv[1:]) or {"llm", "ocr"}
    token = setting("SELFHOSTED_TOKEN")
    results = {}
    if "llm" in wanted:
        results["llm"] = check_llm(setting("SELFHOSTED_LLM_URL").rstrip("/"), token)
    if "ocr" in wanted:
        results["ocr"] = check_ocr(setting("SELFHOSTED_OCR_URL").rstrip("/"), token)
    print(" ".join(f"{name}={'ok' if passed else 'FAILED'}" for name, passed in results.items()))
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
