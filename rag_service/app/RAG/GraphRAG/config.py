"""
Central Configuration for MITRE ATT&CK GraphRAG
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent.parent

load_dotenv(_SCRIPT_DIR / ".env")
load_dotenv()

# STIX data folders (each contains versioned .json bundles).
# _PROJECT_ROOT is rag_service/, which is where the bundles sit inside the Docker
# image (the build context root). In a repo checkout they live one level up, at
# the repo root, so fall back there — this is why the existence check exists
# rather than a single hard-coded path.
_STIX_DATA_DIR = _PROJECT_ROOT / "Mitre_ATT&CK Doc"
if not _STIX_DATA_DIR.exists():
    _STIX_DATA_DIR = _PROJECT_ROOT.parent / "Mitre_ATT&CK Doc"
ENTERPRISE_ATTACK_DIR = _STIX_DATA_DIR / "enterprise-attack"
MOBILE_ATTACK_DIR = _STIX_DATA_DIR / "mobile-attack"
ICS_ATTACK_DIR = _STIX_DATA_DIR / "ics-attack"

# ──────────────────────────────────────────────────────────────────────────────
# EMBEDDING MODEL — BGE-M3 (Hybrid: Dense + Sparse)
# ──────────────────────────────────────────────────────────────────────────────
EMBED_MODEL = "BAAI/bge-m3"
EMBED_DIM = 1024  # BGE-M3 dense vector dimension


# ──────────────────────────────────────────────────────────────────────────────
# INFERENCE DEVICE — auto-detect GPU, else CPU
# ──────────────────────────────────────────────────────────────────────────────
# BGE-M3 and the cross-encoder reranker run on GPU when one is available (local
# dev), else CPU (Railway prod ships the CPU torch wheel + a slim base image, so
# there is no GPU there). fp16 is a GPU optimization — on CPU it is emulated and
# slower, so it is enabled ONLY on CUDA. Override with RAG_DEVICE=cpu|cuda (set
# in the shell BEFORE start so it takes effect before torch initializes CUDA).
def _resolve_device() -> str:
    forced = os.getenv("RAG_DEVICE", "").strip().lower()
    if forced == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # hide GPU from all torch models
        return "cpu"
    try:
        import torch
        if forced == "cuda":
            if not torch.cuda.is_available():
                print("[CONFIG] RAG_DEVICE=cuda but no CUDA device; using CPU")
                return "cpu"
            return "cuda"
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


DEVICE = _resolve_device()
USE_FP16 = DEVICE == "cuda"  # fp16 only on GPU; CPU uses fp32
print(f"[CONFIG] Inference device: {DEVICE} (fp16={USE_FP16})")

# ──────────────────────────────────────────────────────────────────────────────
# LEGACY — E5 Configuration (kept for reference / rollback)
# ──────────────────────────────────────────────────────────────────────────────
# EMBED_MODEL = "intfloat/multilingual-e5-large"
# EMBED_DIM = 1024
# E5_QUERY_PREFIX = "query: "
# E5_PASSAGE_PREFIX = "passage: "

# ──────────────────────────────────────────────────────────────────────────────
# QDRANT — Vector Database (replaces ChromaDB)
# ──────────────────────────────────────────────────────────────────────────────
# Supports: local Docker, Qdrant Cloud, or in-memory (fallback)
QDRANT_HOST = os.getenv("QDRANT_HOST")
_qdrant_port_str = os.getenv("QDRANT_PORT")
QDRANT_PORT = int(_qdrant_port_str) if _qdrant_port_str else 6333
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv(
    "QDRANT_URL"
)  # Full URL for Qdrant Cloud (e.g., https://xxx.aws.cloud.qdrant.io)

QDRANT_COLLECTION_ENTITIES = os.getenv("QDRANT_COLLECTION_ENTITIES", "mitre_entities")
QDRANT_COLLECTION_RELATIONSHIPS = os.getenv(
    "QDRANT_COLLECTION_RELATIONSHIPS", "mitre_relationships"
)

# ──────────────────────────────────────────────────────────────────────────────
# HYBRID RETRIEVAL — RRF (Reciprocal Rank Fusion)
# ──────────────────────────────────────────────────────────────────────────────
RRF_K = 60  # Standard RRF constant: score = 1 / (k + rank)
DENSE_WEIGHT = 1.0  # Weight for dense (semantic) results in RRF
SPARSE_WEIGHT = 1.0  # Weight for sparse (lexical/keyword) results in RRF
# Tip: For CTI domain, try SPARSE_WEIGHT=1.2 to boost exact ID matches

# ──────────────────────────────────────────────────────────────────────────────
# NEO4J
# ──────────────────────────────────────────────────────────────────────────────
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# ──────────────────────────────────────────────────────────────────────────────
# LLM (Claude & OpenRouter)
# ──────────────────────────────────────────────────────────────────────────────
def validate_core_llm_provider(value: str) -> str:
    provider = value.strip().lower()
    if provider not in {"anthropic", "openrouter"}:
        raise ValueError(
            "CORE_LLM_PROVIDER must be exactly 'anthropic' or 'openrouter'"
        )
    return provider


from .model_registry import DEFAULT_OPENROUTER_MODEL, resolve_openrouter_model

CORE_LLM_PROVIDER = validate_core_llm_provider(
    os.getenv("CORE_LLM_PROVIDER", "openrouter")
)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENROUTER_CYBERCASE = os.getenv("OPENROUTER_CYBERCASE", "")
CORE_LLM_ANTHROPIC_MODEL = os.getenv(
    "CORE_LLM_ANTHROPIC_MODEL", "claude-haiku-4-5"
)
CORE_LLM_OPENROUTER_MODEL = resolve_openrouter_model(
    os.getenv("CORE_LLM_OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
)
CORE_LLM_ANTHROPIC_BASE_URL = os.getenv(
    "CORE_LLM_ANTHROPIC_BASE_URL", "https://api.anthropic.com"
).rstrip("/")
CORE_LLM_OPENROUTER_BASE_URL = os.getenv(
    # The Anthropic SDK appends /v1/messages to this base URL.
    "CORE_LLM_OPENROUTER_BASE_URL", "https://openrouter.ai/api"
).rstrip("/")
CORE_LLM_EFFECTIVE_PROVIDER = CORE_LLM_PROVIDER
CORE_LLM_EFFECTIVE_MODEL = (
    CORE_LLM_OPENROUTER_MODEL
    if CORE_LLM_PROVIDER == "openrouter"
    else CORE_LLM_ANTHROPIC_MODEL
)
CORE_LLM_EFFECTIVE_API_KEY = (
    OPENROUTER_CYBERCASE
    if CORE_LLM_PROVIDER == "openrouter"
    else ANTHROPIC_API_KEY
)
CORE_LLM_EFFECTIVE_BASE_URL = (
    CORE_LLM_OPENROUTER_BASE_URL
    if CORE_LLM_PROVIDER == "openrouter"
    else CORE_LLM_ANTHROPIC_BASE_URL
)

# Legacy Anthropic aliases remain for offline tooling outside the production
# provider factory.
LLM_MODEL = CORE_LLM_ANTHROPIC_MODEL
LLM_MAX_TOKENS = 8192
LLM_TEMPERATURE = 0

# Per-request ceiling for every core LLM call. Without one the Anthropic client
# waits up to its own 10-minute default, three times with retries, and a hung
# call holds one of the MAX_CONCURRENT_QUERIES worker slots for all of it. The
# slowest stage measured, the reasoning call, takes about 25 s on average.
CORE_LLM_TIMEOUT_SECONDS = float(os.getenv("CORE_LLM_TIMEOUT_SECONDS", "120"))

# Ultrafast mode (--ultrafast): vector-only retrieve (no graph) + terse, capped
# output. Output-token count dominates LLM latency, so the answer is short.
ULTRAFAST_MAX_TOKENS = int(os.getenv("ULTRAFAST_MAX_TOKENS", "2048"))
ULTRAFAST_TOP_K = int(os.getenv("ULTRAFAST_TOP_K", "6"))

EVALUATOR_LLM_MODEL = CORE_LLM_ANTHROPIC_MODEL
EVALUATOR_MAX_TOKENS = (
    4096  # Must fit: reasoning/thinking + verdict + reason + covered/missing phases + rewritten_query
)
EVALUATOR_TEMPERATURE = 0

RAGAS_LLM_MODEL = "qwen/qwen-2.5-72b-instruct"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ──────────────────────────────────────────────────────────────────────────────
# LOCAL MODELS (Ollama) — OFFLINE TOOLING ONLY, not the service
# ──────────────────────────────────────────────────────────────────────────────
# The served pipeline is cloud-only: GraphRAGAgent and ContextEvaluator no longer
# take a use_local switch, and there is no --local flag on the RAG CLI. What is
# left here is consumed by evaluation/ and by the chain path it still exercises:
#   evaluation/eval_runner.py --local          → LOCAL_LLM_MODEL, LOCAL_EVAL_MODEL
#   evaluation/generation_metrics.py           → RAGAS nomic-embed-text embeddings
#   evaluation/crosslingual_generation_benchmark.py "ollama:<name>" → fine-tune A/B
# Retiring these means giving evaluation/ a cloud embedding provider and dropping
# the local arm of the fine-tune comparison — a change to that directory, not a
# cleanup of this one.
# Setup: https://ollama.com | pip install langchain-ollama
#        ollama pull qwen2.5:7b && ollama pull gemma3:4b
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Model 1 — Pipeline  (reasoning + translation + routing)
# qwen2.5:7b  Q4_K_M ≈ 4.1 GB VRAM  |  best multilingual in 7B class, good Thai support
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:7b")

# Model 2 — Evaluation judge  (context sufficiency + query merger + offline RAGAS)
# gemma3:4b   Q4_K_M ≈ 2.6 GB VRAM  |  different family → lower judge bias
LOCAL_EVAL_MODEL = os.getenv("LOCAL_EVAL_MODEL", "gemma3:4b")

# Context window for local Ollama models. ChatOllama otherwise defaults to a small
# num_ctx and SILENTLY truncates large prompts (decomposition input + retrieved
# context) → degenerate/empty output. Must comfortably hold the incident text.
LOCAL_NUM_CTX = int(os.getenv("LOCAL_NUM_CTX", "8192"))

# ──────────────────────────────────────────────────────────────────────────────
# SERVICE CONCURRENCY
# ──────────────────────────────────────────────────────────────────────────────
# GraphRAGAgent.query() is synchronous and long-running, so POST /query runs it
# in a worker thread instead of on the event loop (see routers/rag.py). This is
# the cap on how many of those pipelines may run at once: sessions beyond it
# queue rather than thrashing CPU (BGE-M3 embed + rerank run on CPU in prod) or
# opening unbounded Neo4j/Qdrant/LLM connections. Requests are not rejected when
# the cap is reached — they simply wait their turn.
MAX_CONCURRENT_QUERIES = max(1, int(os.getenv("RAG_MAX_CONCURRENT_QUERIES", "4")))

# ──────────────────────────────────────────────────────────────────────────────
# RETRIEVAL
# ──────────────────────────────────────────────────────────────────────────────
VECTOR_TOP_K = 10  # Initial vector retrieval count
FINAL_TOP_K = 5  # After reranking

# Rendered-context budget on the agent path (quota retrieval).
AGENT_MAX_VECTOR = 15
AGENT_MAX_GRAPH = 8
AGENT_MAX_CONTEXT_CHARS = 10000

# Quota retrieval keeps only hits that can evidence a technique (Technique /
# Subtechnique nodes, relationships with a technique end) and dedups them by
# parent technique, so a relationship and the technique it points at share
# one slot. Group/Software/Campaign hits stay only when the query names them.
# On the real-CTI held-out split (45 incidents) this raised StepCoverage@15 —
# the share of attack steps whose technique reaches the context at all —
# 0.832 → 0.893 with no incident worse (branch sandbox/retrieval-lab,
# evaluation/results/retrieval_lab/). "false" restores the old pool.
TECHNIQUE_POOL = os.getenv("TECHNIQUE_POOL", "true").lower() == "true"

# How many hits each sub-query may contribute to the agent's vector list.
# Deduping by technique frees slots (some incidents fell to 9–13 of 15), so
# with the pool each sub-query offers 5 to fill them: held-out
# StepCoverage@15 0.893 → 0.915, top ranks unchanged. 3 was tested only
# without the pool, so it stays the value when the pool is off.
AGENT_PER_QUERY_K = 5 if TECHNIQUE_POOL else 3

# Each broaden round adds this much budget instead of competing for the same
# space. The first pass already fills the character budget (mean 9258 of 10000
# over 100 real-CTI incidents), so under a fixed budget a second retrieval can
# only displace what the first found: measured over the 25 broadened samples it
# lost gold techniques on 6 and gained on 6, a wash paid for with two LLM calls
# (evaluation/results/agentic_ablation.md).
BROADEN_VECTOR_STEP = 10
BROADEN_GRAPH_STEP = 4
BROADEN_CONTEXT_CHARS_STEP = 5000
# Neighbour names listed per relation in a rendered subgraph ("Used by: …").
# Well-known techniques and groups have 80–400 neighbours; uncapped, one
# subgraph filled the whole context and every later one was truncated away.
GRAPH_CONTEXT_MAX_NAMES = 10

# Restrict entity vector search to one ATT&CK domain. The corpus is ingested with
# mobile + enterprise, but mobile entities (Pegasus, FluBot, mobile-only Phishing
# variants) pollute enterprise incident analysis. Set to "" / unset to disable.
# NOTE: only the ENTITY collection is domain-tagged; relationships are not, so a
# few mobile relationship hits can still slip through — re-ingest enterprise-only
# for a 100% clean corpus.
ATTACK_DOMAIN_FILTER = os.getenv("ATTACK_DOMAIN_FILTER", "enterprise").strip() or None

# Reranker — must handle Thai↔English pairs, because the agent does no input
# translation: a Thai incident is scored directly against English MITRE text.
# (mmarco-mMiniLMv2 was trained on 14 mMARCO languages, Thai not included)
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

# MITRE mapping table sent to the backend: an UNCITED vector hit becomes a
# "retrieved_only" row only if its rerank score (sigmoid [0,1] x type weight)
# reaches this. Rows the answer cites are kept whatever they score.
#
# 0.50 was measured by evaluation/mitre_threshold_calibration.py. Cited rows
# bypass the cut exactly as build_mitre_table lets them.
#
#                real CTI (100 incidents,     gen_bench (45 incidents,
#                 answers: ablation arm M)     answers: variant C)
#   thr           P     R     F1               P     R     F1
#   0.05         .394  .676  .487             .527  .651  .563
#   0.50         .439  .664  .518             .610  .645  .606
#   cited only   .464  .661  .536             .641  .637  .621
#
# On both sets 0.50 beats 0.05 on F1 and costs 1-2% of recall. Two alternative
# rules did no better: the score divided by the sub-query's top score, and the
# rank within the sub-query.
#
# On real CTI the score barely tells correct uncited rows from noise: 16-25%
# of them are correct at every cut. The threshold therefore mostly sets how
# many retrieved_only rows appear. Over the 100 incidents:
#   0.05 keeps 25 correct technique rows, 98 noise rows and 95 non-technique rows
#   0.50 keeps 9, 32 and 19
# Reports: evaluation/results/mitre_threshold_calibration_*.md.
#
# History:
# - 0.62 (2026-07-03) was set while reranker.py applied sigmoid twice, which
#   compressed scores into [0.5, 0.731].
# - 0.05 (2026-08-15) was that value translated by hand when the double
#   sigmoid was removed.
# - A 2026-08-17 sweep on 30 real-CTI cases kept 0.05 because 0.50 cost 30% of
#   recall:
#
#     thr    kept   precision   recall    F1
#     0.05    132       .409     .524    .460
#     0.50     56       .679     .369    .478
#
# That sweep ran before any answers existed, so it filtered cited rows too.
# Replaying it that way on the 100 real-CTI incidents reproduces it: recall is
# .560 with no cut and .508 at 0.05 (the sweep had .583 and .524). As served,
# recall moves only from .676 to .664. Its retrieval ceiling still stands: only
# 60 of its 103 gold ids reached the candidate list, and no threshold can move
# that.
MITRE_TABLE_SCORE_THRESHOLD = float(os.getenv("MITRE_TABLE_SCORE_THRESHOLD", "0.5"))

# Re-read the case file to decide the table's Enterprise technique rows
# (pipeline/table_reread.py): READINGS calls against the whole technique list,
# then READINGS calls against the shortlist they and the answer produce, and a
# technique is a row when VOTES of the second round name it. Six calls a query
# at the defaults, three of them carrying the 222-technique list (about 41K
# characters).
#
# Two served runs of the 100 real-CTI incidents on google/gemma-4-26b-a4b-it,
# parent-level technique F1, against the answer-grounded table built from the
# same retrieval and answer:
#
#                    answer-grounded   with the re-read
#     all 100           .640 – .647       .738 – .744
#     held-out 45       .631 – .640       .722 – .723
#
# No other model was measured. Set MITRE_TABLE_REREAD=false for the
# answer-grounded table alone; a re-read that fails falls back to it by itself.
# Report: evaluation/results/table_reread_e2e.md.
MITRE_TABLE_REREAD = os.getenv("MITRE_TABLE_REREAD", "true").lower() == "true"
MITRE_TABLE_REREAD_READINGS = max(1, int(os.getenv("MITRE_TABLE_REREAD_READINGS", "3")))
MITRE_TABLE_REREAD_VOTES = max(1, int(os.getenv("MITRE_TABLE_REREAD_VOTES", "2")))
# A reply is a short JSON list of steps. create_core_chat_model raises this to
# 4096 on OpenRouter whatever is asked for.
MITRE_TABLE_REREAD_MAX_TOKENS = 4096

# Send each table row with the parts of the case file it rests on
# (pipeline/case_evidence.py). The backend validates rows with extra="forbid",
# so a backend that predates the `evidence` field rejects every /query reply
# that carries it: set this to false until that backend is deployed. With it
# off the re-read does not ask its replies for the sentences either, so the
# time they cost is not spent.
MITRE_TABLE_EVIDENCE = os.getenv("MITRE_TABLE_EVIDENCE", "true").lower() == "true"

# ──────────────────────────────────────────────────────────────────────────────
# LEGACY — mmarco reranker (kept for reference / rollback)
# ──────────────────────────────────────────────────────────────────────────────
# RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

# ──────────────────────────────────────────────────────────────────────────────
# CROSS-LINGUAL RETRIEVAL — Dual-Query (Thai original + English translation)
# ──────────────────────────────────────────────────────────────────────────────
# Translate-then-retrieve alone (tRAG) makes the LLM translation a single
# point of failure: one bad translation poisons dense, sparse, and every
# follow-up rewrite (cf. arXiv:2504.03616). With dual-query the original
# Thai query is retrieved in parallel — BGE-M3's cross-lingual dense space
# and exact English keywords embedded in the Thai text (sparse) can recover
# results the translation missed.
DUAL_QUERY_RETRIEVAL = os.getenv("DUAL_QUERY_RETRIEVAL", "true").lower() == "true"

# ──────────────────────────────────────────────────────────────────────────────
# DOMAINS
# ──────────────────────────────────────────────────────────────────────────────
# Ingest historical files (default: False, parsing only latest enterprise-attack.json / mobile-attack.json)
INGEST_HISTORICAL = os.getenv("INGEST_HISTORICAL", "false").lower() in ("1", "true", "yes")

ATTACK_DOMAINS = {"enterprise": ENTERPRISE_ATTACK_DIR, "mobile": MOBILE_ATTACK_DIR}


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def sep(title=""):
    """Print a separator line for console output."""
    width = 72
    if title:
        pad = (width - len(title) - 2) // 2
        print("\n" + "─" * pad + f" {title} " + "─" * pad)
    else:
        print("\n" + "─" * width)
