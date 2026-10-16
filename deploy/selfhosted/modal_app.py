import json
import subprocess

import modal

VLLM_IMAGE = "vllm/vllm-openai:v0.28.0"
PORT = 8000
MINUTES = 60

LLM_MODEL = "google/gemma-4-26B-A4B-it"
LLM_REVISION = "4d7ae4984b7db7de8f8457170b3f1a419ee76d52"
LLM_SERVED_NAME = "google/gemma-4-26b-a4b-it"
LLM_GPU = "A100-80GB"

OCR_MODEL = "typhoon-ai/typhoon-ocr1.5-2b"
OCR_REVISION = "15b381a2d62569e6736f9c085859dff68e48608d"
OCR_SERVED_NAME = "typhoon-ocr"
OCR_GPU = "L4"

image = (
    modal.Image.from_registry(VLLM_IMAGE)
    .entrypoint([])
    .run_commands("ln -sf $(which python3) /usr/bin/python")
    .env({"HF_HOME": "/root/.cache/huggingface", "HF_XET_HIGH_PERFORMANCE": "1"})
)
weights = modal.Volume.from_name("cybercase-hf-cache", create_if_missing=True)
volumes = {
    "/root/.cache/huggingface": weights,
    "/root/.cache/vllm": modal.Volume.from_name("cybercase-vllm-cache", create_if_missing=True),
}

llm_app = modal.App("cybercase-llm")
ocr_app = modal.App("cybercase-ocr")


def fetch(model: str, revision: str) -> None:
    from huggingface_hub import snapshot_download

    print(snapshot_download(model, revision=revision))
    weights.commit()


def vllm_serve(model: str, revision: str, served_name: str, *options: str) -> subprocess.Popen:
    command = [
        "vllm",
        "serve",
        model,
        "--revision",
        revision,
        "--served-model-name",
        served_name,
        "--host",
        "0.0.0.0",
        "--port",
        str(PORT),
        *options,
    ]
    print(*command)
    return subprocess.Popen(command)


@llm_app.function(image=image, volumes=volumes, cpu=4, memory=8192, timeout=60 * MINUTES)
def download_llm_weights():
    fetch(LLM_MODEL, LLM_REVISION)


@ocr_app.function(image=image, volumes=volumes, cpu=2, memory=4096, timeout=30 * MINUTES)
def download_ocr_weights():
    fetch(OCR_MODEL, OCR_REVISION)


@llm_app.server(
    image=image,
    gpu=LLM_GPU,
    volumes=volumes,
    port=PORT,
    startup_timeout=12 * MINUTES,
    scaledown_window=3 * MINUTES,
    max_containers=1,
    target_concurrency=16,
)
class Llm:
    @modal.enter()
    def start(self):
        self.process = vllm_serve(
            LLM_MODEL,
            LLM_REVISION,
            LLM_SERVED_NAME,
            "--max-model-len",
            "131072",
            "--max-num-seqs",
            "16",
            "--gpu-memory-utilization",
            "0.90",
            "--reasoning-parser",
            "gemma4",
            "--limit-mm-per-prompt",
            json.dumps({"image": 0, "video": 0, "audio": 0}),
        )

    @modal.exit()
    def stop(self):
        self.process.terminate()


@ocr_app.server(
    image=image,
    gpu=OCR_GPU,
    volumes=volumes,
    port=PORT,
    startup_timeout=10 * MINUTES,
    scaledown_window=3 * MINUTES,
    max_containers=1,
    target_concurrency=8,
)
class Ocr:
    @modal.enter()
    def start(self):
        self.process = vllm_serve(
            OCR_MODEL,
            OCR_REVISION,
            OCR_SERVED_NAME,
            "--max-model-len",
            "49152",
            "--max-num-seqs",
            "8",
            "--gpu-memory-utilization",
            "0.90",
            "--limit-mm-per-prompt",
            json.dumps({"image": 1, "video": 0}),
        )

    @modal.exit()
    def stop(self):
        self.process.terminate()
