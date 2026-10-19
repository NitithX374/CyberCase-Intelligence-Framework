from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import string
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
ROOT_ENV = HERE.parents[1] / ".env"
PROMPTS = HERE / "data" / "attrfirst" / "MDS.json"
MODEL, PROVIDERS = "google/gemma-4-26b-a4b-it", ["nextbit/bf16", "coreweave/bf16"]
PRICE = {"input": 0.10e-6, "output": 0.30e-6}
PRICES = {"google/gemma-4-26b-a4b-it": PRICE, "deepseek/deepseek-v4.1-flash": {"input": 0.30e-6, "output": 1.20e-6},
          "google/gemini-2.5-flash-lite": {"input": 0.10e-6, "output": 0.40e-6}}
TEMPERATURE, ATTEMPTS, MAX_TOKENS = 0.1, 5, 4096
SELECTION_DEMOS, FIC_DEMOS = (0, 2), (0, 1, 2)
HS, HE = "<highlight_start>", "<highlight_end>"
THAI_SENTENCE = " Write the summary in Thai."
FUSION = re.compile(r"highlight(?:s)? ([\d, and]+) (?:is|are) combined to form sentence (\d+):[\n ]*(.*?)(?=[\n]+|\Z)",
                    re.IGNORECASE)


def rmv_spaces_and_punct(text: str) -> str:
    return text.lower().translate(str.maketrans("", "", string.whitespace + string.punctuation))


def alnum_only(text: str) -> str:
    cleaned = re.sub(r"[" + re.escape(string.punctuation + string.whitespace) + r"\s]", "", text)
    return "".join(c for c in cleaned if c.isalnum())


def find_substring(s: str, sb: str) -> tuple[int, int]:
    if sb.lower().strip() in s.lower():
        start = s.lower().index(sb.lower().strip())
        return start, start + len(sb.strip())
    index = alnum_only(s).lower().find(alnum_only(sb).lower())
    if index == -1:
        return -1, -1
    start = count = 0
    for char in s:
        removed = alnum_only(char) == ""
        if count == index and not removed:
            break
        if not removed:
            count += 1
        start += 1
    end, left = start, len(alnum_only(sb))
    while left > 0 and end < len(s):
        if s[end].isalnum():
            left -= 1
        end += 1
    return start, end


def extract_highlights(text: str, start: str = "{HS}", end: str = "{HE}") -> list[str]:
    return re.findall(re.escape(start) + r"(.*?)" + re.escape(end), text, re.DOTALL)


def selection_demo(prompts: dict, demo: dict, instruction: str) -> str:
    docs = "".join(prompts["doc_prompt"].replace("{P}", d["text"]).replace("{ID}", str(i + 1))
                   for i, d in enumerate(demo["docs"])).replace("{HS}", "").replace("{HE}", "")
    answer = "\n".join(prompts["answer_content_selection_format"].replace("{ID}", str(i + 1)).replace(
        "{CONTENT_LIST}", " <SPAN_DELIM> ".join(extract_highlights(d["text"]))) for i, d in enumerate(demo["docs"]))
    block = prompts["demo_prompt"].replace("{INST}", instruction).replace("{D}", docs).replace(
        "{A}", prompts["answer_content_selection_prompt"]).replace("{HDOCS}", answer)
    return block.replace("{HS}", HS).replace("{HE}", HE).strip()


def listing(prompts: dict, docs: list[str]) -> str:
    out, count = "", 0
    for i, text in enumerate(docs):
        items = extract_highlights(text)
        out += prompts["answer_highlights_listing_prompt"].replace("{ID}", str(i + 1)).replace(
            "{HLIST_DOC}", "\n".join(f"{j + count + 1}. {h}" for j, h in enumerate(items)))
        count += len(items)
    return out


def fic_demo(prompts: dict, demo: dict, instruction: str) -> str:
    docs = [d["shorter_text"] for d in demo["docs"]]
    docs_text = "".join(prompts["doc_prompt"].replace("{P}", t).replace("{ID}", str(i + 1)) for i, t in enumerate(docs))
    fusion = ""
    for k, plan in enumerate(demo["planning"]):
        indices = sorted(h for c in plan["highlights_cluster"] for h in c["highlights"])
        fusion += prompts["answer_highlights_fusion_prompt"].replace("{HFUSE_SENT}", ",".join(map(str, indices))).replace(
            "{SENT_ID}", str(k + 1)).replace("{SENT}", plan["output"])
    planning = prompts["answer_FiC_planning_prompt"].replace("{HFUSE}", fusion).replace("{SUMM}", demo["answer"])
    block = prompts["demo_prompt"].replace("{INST}", instruction).replace("{D}", docs_text).replace(
        "{A}", prompts["answer_FiC-CoT_prompt"]).replace("{HLIST}", listing(prompts, docs)).replace("{PLANNING}", planning)
    return block.replace("{HS}", HS).replace("{HE}", HE)


def selection_prompt(prompts: dict, text: str) -> str:
    instruction = prompts["instruction-content-selection"]
    head = "".join(selection_demo(prompts, prompts["demos"][i], instruction) + prompts["demo_sep"] for i in SELECTION_DEMOS)
    tail = prompts["demo_prompt"].replace("{INST}", instruction).replace(
        "{D}", prompts["doc_prompt"].replace("{P}", text).replace("{ID}", "1")).replace(
        "{A}", prompts["answer_content_selection_prompt"]).replace("{HDOCS}", "").strip()
    return head + tail


def parse_selection(response: str, text: str) -> list[str]:
    pairs = [(m.group(1), m.group(2).strip()) for m in re.finditer(r"(Document \[\d+\]):(.*?)(?=Document \[|\Z)",
                                                                       response, re.DOTALL)]
    if not pairs:
        raise ValueError("no content was found")
    if any(name != "Document [1]" for name, _ in pairs):
        raise ValueError("not only relevant documents are included")
    spans = [s for _, body in pairs for s in body.split("<SPAN_DELIM>") if rmv_spaces_and_punct(s)]
    if not all(rmv_spaces_and_punct(s) in rmv_spaces_and_punct(text) for s in spans):
        raise ValueError("not all selected content is traceable")
    return spans


def highlighted(text: str, spans: list[str], sentences: list[tuple[int, int]]) -> tuple[str, list[list[int]], int]:
    pieces, unfound = [], 0
    for span in spans:
        a, b = find_substring(text, span.strip())
        if a == -1:
            unfound += 1
            continue
        inside = [(max(a, s), min(b, e)) for s, e in sentences if s < b and a < e]
        pieces += [list(p) for p in (inside or [(a, b)]) if rmv_spaces_and_punct(text[p[0]:p[1]])]
    merged: list[list[int]] = []
    for s, e in sorted({tuple(p) for p in pieces}):
        if merged and s < merged[-1][1] and any(ss <= merged[-1][0] < ee and ss <= s < ee for ss, ee in sentences):
            merged[-1][1] = max(merged[-1][1], e)
        elif not merged or s >= merged[-1][1]:
            merged.append([s, e])
    out, last = "", 0
    for s, e in merged:
        out += text[last:s] + "{HS}" + text[s:e] + "{HE}"
        last = e
    out += text[last:]
    return out, merged, unfound


def fic_prompt(prompts: dict, marked: str, thai: bool) -> str:
    instruction = prompts["instruction-FiC-CoT"] + (THAI_SENTENCE if thai else "")
    head = "".join(fic_demo(prompts, prompts["demos"][i], instruction) + prompts["demo_sep"] for i in FIC_DEMOS)
    cut = "{HE}".join(marked.split("{HE}")[:-1]) + "{HE}"
    tail = prompts["demo_prompt"].replace("{INST}", instruction).replace(
        "{D}", prompts["doc_prompt"].replace("{P}", cut).replace("{ID}", "1")).replace(
        "{A}", prompts["answer_FiC-CoT_prompt"]).replace("{HLIST}", listing(prompts, [cut])).replace("{PLANNING}", "")
    return head + tail.replace("{HS}", HS).replace("{HE}", HE).strip()


def parse_fic(response: str) -> dict:
    if "So the final summary is:" not in response:
        raise ValueError("cannot find the final summary in the model's response")
    at = response.index("So the final summary is:")
    final, planning = response[at:].replace("So the final summary is:", "").strip(), response[:at]
    alignments = sorted(({"sent_id": int(m[1]),
                          "highlights": sorted(int(h.replace("and", "")) for h in m[0].split(",") if h.replace("and", "").strip()),
                          "sent_text": m[2]} for m in FUSION.findall(planning)), key=lambda x: x["sent_id"])
    return {"final": final, "alignments": alignments}


def api_key() -> str:
    for line in ROOT_ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("OPENROUTER_CYBERCASE"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_CYBERCASE not found")


async def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--stage", choices=("pilot", "main"), required=True)
    parser.add_argument("--cap-usd", type=float, required=True)
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--providers", default=",".join(PROVIDERS))
    args = parser.parse_args()
    sys.path.insert(0, args.backend)
    sys.path.insert(0, str(HERE))
    from app.trace.sentences import sentence_spans
    from judgement_claims_only import sample

    prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))
    items = sample(args.stage)
    if args.dry:
        for item in items[:1] + items[-1:]:
            p = selection_prompt(prompts, item["text"])
            print(item["key"], "selection prompt chars", len(p))
            print(p[-400:])
        return
    key = api_key()
    budget = {"spent": 0.0}
    limit = asyncio.Semaphore(int(os.environ.get("RUN_CONCURRENCY", "6")))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    model, providers, price = args.model, [p for p in args.providers.split(",") if p], PRICES[args.model]
    tag = "" if model == MODEL else "_" + model.split("/")[-1]
    raw = HERE / "results" / f"raw_attrfirst_cot{tag}_{args.stage}_{stamp}"
    raw.mkdir(parents=True)

    async def call(client: httpx.AsyncClient, prompt: str, calls: list) -> str:
        if budget["spent"] + len(prompt) / 3 * price["input"] + MAX_TOKENS * price["output"] > args.cap_usd:
            raise RuntimeError("cap reached")
        async with limit:
            started = time.monotonic()
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", timeout=600, headers={
                "Authorization": f"Bearer {key}"}, json={
                "model": model, "messages": [{"role": "user", "content": prompt}], "temperature": TEMPERATURE,
                "max_tokens": MAX_TOKENS, "usage": {"include": True},
                **({"provider": {"order": providers, "allow_fallbacks": False}} if providers else {})})
        body = response.json()
        usage = body.get("usage") or {}
        cost = usage.get("cost")
        if not isinstance(cost, (int, float)):
            cost = (usage.get("prompt_tokens") or 0) * price["input"] + (usage.get("completion_tokens") or 0) * price["output"]
        budget["spent"] += cost
        calls.append({"ms": round((time.monotonic() - started) * 1000), "status": response.status_code,
                      "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                      "usd": cost, "provider": body.get("provider")})
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: {str(body)[:200]}")
        return body["choices"][0]["message"].get("content") or ""

    async def attempt(client, prompt, parse, calls, log):
        problem = None
        for n in range(1, ATTEMPTS + 1):
            text = await call(client, prompt, calls)
            try:
                result = parse(text)
                log.append({"attempt": n, "ok": True})
                return result, text
            except ValueError as error:
                problem = str(error)
                log.append({"attempt": n, "ok": False, "problem": problem, "response": text[:4000]})
        raise RuntimeError(f"failed after {ATTEMPTS} attempts: {problem}")

    async def one(client: httpx.AsyncClient, item: dict) -> dict:
        out: dict = {"key": item["key"], "language": item["language"], "calls": [], "selection_log": [], "fic_log": []}
        try:
            spans, _ = await attempt(client, selection_prompt(prompts, item["text"]),
                                     lambda r: parse_selection(r, item["text"]), out["calls"], out["selection_log"])
            marked, merged, unfound = highlighted(item["text"], spans, sentence_spans(item["text"]))
            out.update({"spans": spans, "highlights": [item["text"][s:e] for s, e in merged], "offsets": merged,
                        "spans_unfound": unfound})
            if not merged:
                raise RuntimeError("no highlight located")
            fused, response = await attempt(client, fic_prompt(prompts, marked, item["language"] == "thai"),
                                            parse_fic, out["calls"], out["fic_log"])
            out.update({"summary": fused["final"], "alignments": fused["alignments"], "fic_response": response})
        except (RuntimeError, httpx.HTTPError, KeyError) as error:
            out["error"] = f"{type(error).__name__}: {error}"
        (raw / f"{item['key']}.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        print(item["key"], "error" if "error" in out else f"ok ({len(out['alignments'])} sentences)", flush=True)
        return out

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(one(client, item) for item in items))
    report = {"stage": args.stage, "model": model, "providers": providers, "prompts_sha256_prefix": "8214716b2d9c5901",
              "items": len(items), "spent_usd": round(budget["spent"], 4),
              "calls": sum(len(r["calls"]) for r in results),
              "errors": [f"{r['key']}: {r['error']}" for r in results if "error" in r]}
    (raw / "run.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
