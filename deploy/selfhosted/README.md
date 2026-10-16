# Self-hosted models

CyberCase calls two hosted models: Gemma 4 26B A4B through OpenRouter for every LLM call, and
Typhoon OCR through the Typhoon API for document recognition. This folder runs the same weights
on servers you control, as two vLLM containers, and `docker-compose.selfhosted.yml` points the
services at them. The RAG service changes by environment only.

## What runs where

| Part | Today | Self-hosted |
|---|---|---|
| Backend LLM calls: assess, MITRE gate, reading, views, judgement, chat | OpenRouter, `google/gemma-4-26b-a4b-it`, BF16 endpoints `nextbit/bf16`, `coreweave/bf16` | vLLM, `google/gemma-4-26B-A4B-it` BF16, revision `4d7ae498` |
| RAG service LLM calls | OpenRouter, the same model | the same vLLM server |
| OCR | Typhoon API, `typhoon-ocr`, which the API documents as Typhoon OCR 1.5 (2B) | vLLM, `typhoon-ai/typhoon-ocr1.5-2b` BF16, revision `15b381a2` |
| Embeddings and reranker (RAG service); NLI verifier, source selector, XLM-R gate, sentence splitter (backend) | local, inside their own containers | unchanged |
| Qdrant and Neo4j | cloud | unchanged, still online |
| Thanoy legal lookup | online API | unchanged, still online |

Each server answers to the model name the services already send, so the only code change is one
backend setting, `CASE_ANALYSIS_SERVER=vllm`.

## Same weights, different serving

- vLLM has no thinking budget. With `CASE_ANALYSIS_SERVER=vllm` the backend sends
  `chat_template_kwargs: {"enable_thinking": true}` for a stage with a thinking budget and `false`
  for a stage without one. `max_tokens` still bounds output and thinking together.
- The RAG service sends no thinking setting, so on vLLM its calls run with the chat template's
  default, which is off. What OpenRouter does with such a request was not checked.
- Unset sampling parameters come from the model's `generation_config.json`. The OpenRouter
  endpoints may use other defaults.
- The LLM server's context is 131,072 tokens. The backend plans every call within 128,000;
  OpenRouter's endpoints offer 262,144.
- Replies are sampled on both sides. Compare stage results, counts and timing, not the wording.

## Option A: Modal

Nothing needs a GPU on this machine. `modal_app.py` holds two apps, `cybercase-llm` and
`cybercase-ocr`, deployed and stopped separately. Prices from modal.com/pricing on 2026-10-16:

| Server | GPU | Per second | Per hour |
|---|---|---|---|
| `Llm` | A100 80 GB | $0.000694 | $2.50 |
| `Ocr` | L4 | $0.000222 | $0.80 |

A server costs nothing while it has no container. The first request starts one, which stops 3
minutes after the last request, and `max_containers=1` caps each at one GPU. The weights are
downloaded by a CPU function first, so no GPU time is spent downloading.

Modal refuses every GPU function, the L4 included, until the workspace has a payment method.
Without one, the workspace on 2026-10-16 showed $1.00 of monthly credit and a $1 usage limit
set by Modal. The pricing page says the Starter plan includes $30 of compute a month.

1. Install the client and sign in. `modal setup` opens the browser.

   ```bash
   pip install modal
   ```

   ```bash
   modal setup
   ```

2. Create a proxy token and add it to the repository's `.env` as
   `SELFHOSTED_TOKEN=<token id>.<token secret>`: the `wk-...` and `ws-...` parts joined by a
   period. `modal workspace proxy-tokens create --json` prints both parts once. Modal's proxy
   refuses a request without the token with HTTP 401, so the servers are not open to the
   internet.

3. Deploy both apps. This builds the image from `vllm/vllm-openai:v0.28.0`; no GPU runs yet.

   ```bash
   modal deploy deploy/selfhosted/modal_app.py::llm_app
   ```

   ```bash
   modal deploy deploy/selfhosted/modal_app.py::ocr_app
   ```

4. Download the weights, about 52 GB and 4 GB, into the `cybercase-hf-cache` volume on CPU.

   ```bash
   modal run deploy/selfhosted/modal_app.py::download_llm_weights
   ```

   ```bash
   modal run deploy/selfhosted/modal_app.py::download_ocr_weights
   ```

5. Add the two server URLs to `.env` as `SELFHOSTED_LLM_URL=https://...` and
   `SELFHOSTED_OCR_URL=https://...`, without `/v1`. This prints them:

   ```bash
   python -c "import modal; print(modal.Server.from_name('cybercase-llm', 'Llm').get_url()); print(modal.Server.from_name('cybercase-ocr', 'Ocr').get_url())"
   ```

6. Wake the servers and check them. The first start compiles and captures CUDA graphs, which
   takes a few minutes; later starts reuse the `cybercase-vllm-cache` volume.

   ```bash
   python deploy/selfhosted/smoke.py
   ```

7. Recreate the two services with the override. Compose fixes a container's environment when it
   is created, so a restart is not enough.

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.selfhosted.yml up -d backend rag-service
   ```

A request that reaches a server with no container gets HTTP 503 while one starts. The backend
retries once after 2 seconds and then reports the provider as down, so run `smoke.py` again
after a quiet spell.

Back to OpenRouter and the Typhoon API:

```bash
docker compose up -d backend rag-service
```

Stop the servers:

```bash
modal app stop cybercase-llm
```

```bash
modal app stop cybercase-ocr
```

## Option B: a local GPU host

The same image and flags in two containers, `llm` and `ocr`. They need NVIDIA GPU memory for
the 52 GB of Gemma weights, the 4 GB OCR model, their caches and the RAG service's models: one
80 GB GPU, shared 0.80 / 0.10 by default (`LOCAL_LLM_GPU_SHARE`, `LOCAL_OCR_GPU_SHARE`). Set in
`.env`:

```
SELFHOSTED_LLM_URL=http://llm:8000
SELFHOSTED_OCR_URL=http://ocr:8000
SELFHOSTED_TOKEN=<any string>
LOCAL_MODEL_CACHE=<a folder with 60 GB free>
```

```bash
docker compose -f docker-compose.yml -f docker-compose.selfhosted.yml --profile local-models up -d
```

This profile has not been run: no machine here has such a GPU.

## Measured on Modal, 2026-10-16

- Downloading the weights on CPU took 63 s for Typhoon OCR and 4 min 33 s for Gemma.
- A cold start took 273 s for `Llm` on the A100 and 272 s for `Ocr` on the L4, from the first
  request to a healthy server.
- Two Thai news articles ran through every LLM stage the backend has: assess, MITRE gate,
  reading, views, judgement and a chat answer. Both completed on both servers, with the same
  `.env` thinking settings.
  - Per article it took 116 to 126 s on OpenRouter and 151 to 155 s on the A100, with both
    articles running at once. The A100 run spent more of its time on retries for invalid
    replies.
  - The slowest single call was judgement on both: 68 to 85 s on OpenRouter, 63 to 70 s on the
    A100. No call came near the backend's 120 s limit.
- A synthetic Thai page read by the backend's own OCR client came back identical to the Typhoon
  API's reading: 6.5 s through the API, 10.4 s on the L4.
- Modal usage for the whole session was $0.64, all of it from credits.

The comparison script, `backend/experiments/selfhosted_compare.py`, stays local: the repository
tracks only `analysis_arms.py` in that folder.

### Grammar on this server

The LLM server starts with `--structured-outputs-config '{"backend": "xgrammar",
"disable_any_whitespace": true}'`. That setting changes only requests that send a grammar, so
the backend's prompt-only requests are unaffected. Ten Thai news articles ran in two arms at once
on one A100, with the same `.env` thinking settings. Arm B sent each stage's contract as
`output_config.format` as well as in the prompt; arm C sent it in the prompt only.

| | C: prompt only | B: grammar, no whitespace |
|---|---|---|
| Articles completed | 10 / 10 | 10 / 10 |
| Calls that ran to `max_tokens` | 0 | 0 |
| Calls repeated for an invalid reply | 3 | 0 |
| Claims, of them supported | 129, 79 | 130, 83 |
| Summary units, chat units | 46, 41 | 46, 41 |
| Views lost to the views stage's 60 s deadline | 5 | 1 |

Twenty analyses at once on one GPU made requests queue. The views deadline and every timing
reflect that load, not a single analysis. Ten articles cannot show a quality difference. They
show that on this server the grammar did not bring back the whitespace runaway the hosted
providers had. The run used $0.81 of credits.

`modal container stop` is not a reliable way to stop paying: within the scaledown window the
autoscaler replaced the stopped container with a new one. `modal app stop` ends it; deploy again
to bring it back.

## Checks

`smoke.py` waits for each server's `/health`, asks the LLM for a JSON reply with thinking off and
again with thinking on (the second must come back as a separate thinking block), and checks that
the OCR server serves `typhoon-ocr`. It reads the three `SELFHOSTED_` values from the environment
or from `.env` and never prints the token.
