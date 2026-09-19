"""Training material for the encoder gate, distilled from the LLM gate.

The gate answers a question no corpus answers: does this sentence of a police
report describe cyber behaviour that ATT&CK could interpret? ATT&CK's own
descriptions are doctrine -- "Adversaries may attempt to..." -- not the register
an investigator writes in, and a classifier trained on them learns to recognise
doctrine. So the same model that runs the gate today writes the material, one
sentence per technique, in the register the gate will actually be shown. The
encoder is then a student of the gate it replaces, which is also what makes
agreement with that gate the thing to measure.

Negatives are the harder half. Most of a case file is not about computers at
all, and that part is easy; what a gate gets wrong is the sentence where
technology is present and cyber behaviour is not -- a seized laptop, a printed
email, CCTV, a transfer. Those are written deliberately, from the traps already
named in the LLM gate's own prompt, and real Thai legal prose fills in the rest.

    python build_dataset.py                    # writes dataset.jsonl
    python build_dataset.py --techniques 20    # a small run, to look at output
"""

from __future__ import annotations

import argparse
import asyncio
import glob
import json
import os
import random
import re
from collections import Counter

import httpx
from dotenv import load_dotenv
from pythainlp.tokenize import sent_tokenize

BUNDLE = sorted(glob.glob("../../Mitre_ATT&CK Doc/enterprise-attack/*.json"))[-1]
MODEL = "openai/gpt-5.6-luna"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
PER_CALL = 10
CONCURRENCY = 6

REGISTER = """
You are writing material to train a classifier that reads Thai and English
police case files. Write the way an investigator records an observed fact: past
tense, specific, 12-35 words, no doctrine, no advice, no ATT&CK names or IDs,
no markdown.

Vary the opening of every sentence. Do not lean on a fixed frame such as
"Investigators found that" or "เจ้าหน้าที่พบว่า" -- begin from the system, the
account, the file, the time, the victim or the suspect as often as from the
officer, and vary the actors, the details and the sentence shape between items.
A classifier trained on these has to learn the behaviour described, not the way
the sentence opens.

Return only JSON.
""".strip()

POSITIVE_TASK = """
For each numbered behaviour below, write two case-file sentences recording that
something of that kind was observed in an investigation: one in Thai ("th") and
one in English ("en"). The reader must be able to tell that computer-system
behaviour occurred, without being told which technique it was.

Return {"items":[{"n":<number>,"th":"...","en":"..."}]}
""".strip()

NEGATIVE_TASK = """
For each numbered situation below, write two case-file sentences: one in Thai
("th") and one in English ("en"). Every sentence must describe the situation
with NO computer-system behaviour in it at all. Technology may appear as an
object, a location, a document or a possession -- never as something that ran,
connected, authenticated, was accessed without permission, or was attacked.
These are the sentences a cyber gate must not mistake for cyber behaviour.

Return {"items":[{"n":<number>,"th":"...","en":"..."}]}
""".strip()

# The near misses, taken from the traps the LLM gate's own prompt already names.
TRAPS = [
    "a computer, laptop, tablet or server seized and held as an exhibit",
    "a mobile phone reported lost, stolen or snatched",
    "CCTV footage being recorded, collected, copied or reviewed",
    "printouts or screenshots of emails or chat attached to a report",
    "money transferred by the victim after an ordinary deception, with no technical step",
    "an IP address, account number or phone number appearing in a document or a table",
    "ordinary everyday use of an account, phone, computer or app by its owner",
    "procedural text: forwarding a case file, an opinion to prosecute, a signature block",
    "a warrant, summons, court order or case reference being issued or recorded",
    "a witness describing people, vehicles, places or times",
    "identifying details of a complainant, a suspect or an officer",
    "physical damage, a physical break-in, or property taken from a room",
    "a suspect using a computer merely as a tool to type or print a forged paper document",
    "a bank statement, receipt or slip being obtained and attached to the file",
    "a victim being telephoned and persuaded to hand over cash in person",
    "the internal policy, staffing or organisational chart of a company being described",
    "goods ordered online that never arrived, described only as a purchase",
    "a photograph or a video taken on a phone and submitted as an exhibit",
    "an interview being conducted and a statement being recorded",
    "medical, injury or forensic findings about a person",
]


def technique_seeds(limit: int) -> list[str]:
    """One line per ATT&CK technique: its name and the first line of doctrine."""

    objects = json.load(open(BUNDLE, encoding="utf-8"))["objects"]
    seeds: dict[str, str] = {}
    for entry in objects:
        if entry.get("type") != "attack-pattern":
            continue
        if entry.get("revoked") or entry.get("x_mitre_deprecated"):
            continue
        name, description = entry.get("name"), entry.get("description", "")
        if not name or not description:
            continue
        text = re.sub(r"<[^>]+>|\(Citation:[^)]*\)", "", description).strip()
        first = re.split(r"(?<=[.])\s", text)[0][:260]
        seeds[name] = f"{name}: {first}"
    chosen = sorted(seeds)
    random.Random(20260919).shuffle(chosen)
    return [seeds[name] for name in chosen[:limit]]


async def write_batch(client, key, task, seeds, offset):
    listing = "\n".join(f"{offset + i}. {seed}" for i, seed in enumerate(seeds))
    response = await client.post(
        ENDPOINT,
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": REGISTER},
                {"role": "user", "content": f"{task}\n\n{listing}"},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 1.0,
            "max_tokens": 4000,
        },
        timeout=180,
    )
    response.raise_for_status()
    body = json.loads(response.json()["choices"][0]["message"]["content"])
    return [item for item in body.get("items", []) if item.get("th") and item.get("en")]


async def generate(task, seeds, label, key):
    limit = asyncio.Semaphore(CONCURRENCY)
    batches = [(i, seeds[i : i + PER_CALL]) for i in range(0, len(seeds), PER_CALL)]

    async def one(client, offset, batch):
        async with limit:
            for attempt in range(3):
                try:
                    return await write_batch(client, key, task, batch, offset)
                except Exception as error:
                    if attempt == 2:
                        print(f"  batch {offset} failed: {type(error).__name__}")
                        return []
                    await asyncio.sleep(2 * (attempt + 1))

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(one(client, offset, batch) for offset, batch in batches)
        )

    rows = []
    for group in results:
        for item in group:
            for language in ("th", "en"):
                rows.append(
                    {
                        "text": item[language].strip(),
                        "label": label,
                        "lang": language,
                        "origin": "written",
                    }
                )
    print(f"  label={label}: {len(rows)} sentences from {len(batches)} calls")
    return rows


def prose_sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for line in text.splitlines()
        if line.strip()
        for sentence in sent_tokenize(line, engine="crfcut")
    ]


def thai_prose(limit: int) -> list[dict]:
    """Real Thai legal and news prose: the easy negatives, and free."""

    from datasets import load_dataset

    rows: list[dict] = []
    for name, field in (("pythainlp/thailaw-v1.0", "text"), ("thaisum", "body")):
        try:
            data = load_dataset(name, split="train", streaming=True)
            taken = 0
            for record in data:
                for sentence in prose_sentences(str(record.get(field, "")))[:6]:
                    if 40 <= len(sentence) <= 300:
                        rows.append(
                            {"text": sentence, "label": 0, "lang": "th", "origin": name}
                        )
                        taken += 1
                if taken >= limit // 2:
                    break
            print(f"  {name}: {taken} sentences")
        except Exception as error:
            print(f"  {name} unavailable: {type(error).__name__}: {error}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--techniques", type=int, default=360)
    parser.add_argument("--traps", type=int, default=12, help="sentences per trap")
    parser.add_argument("--prose", type=int, default=700)
    parser.add_argument("--out", default="dataset.jsonl")
    args = parser.parse_args()

    load_dotenv("../../.env")
    key = os.environ["OPENROUTER_CYBERCASE"]

    print(f"seeding from {os.path.basename(BUNDLE)}")
    positives = technique_seeds(args.techniques)
    traps = [trap for trap in TRAPS for _ in range(args.traps)]

    rows = asyncio.run(generate(POSITIVE_TASK, positives, 1, key))
    rows += asyncio.run(generate(NEGATIVE_TASK, traps, 0, key))
    if args.prose:
        rows += thai_prose(args.prose)

    seen, unique = set(), []
    for row in rows:
        if row["text"] not in seen:
            seen.add(row["text"])
            unique.append(row)

    with open(args.out, "w", encoding="utf-8") as handle:
        for row in unique:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\n{len(unique)} unique sentences -> {args.out}")
    print(" ", Counter((row["lang"], row["label"]) for row in unique))


if __name__ == "__main__":
    main()
