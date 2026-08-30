from __future__ import annotations

from typing import Any

from .contracts import RefinedContext


DEFAULT_COMPRESSOR_MODEL = "microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank"
DEFAULT_COMPRESSION_RATE = 1.5


class CompressorFailure(RuntimeError):
    pass


class LLMLingua2Refiner:
    name = "llmlingua2"

    def __init__(
        self,
        model_name: str = DEFAULT_COMPRESSOR_MODEL,
        compression_rate: float = DEFAULT_COMPRESSION_RATE,
        device_map: str = "cpu",
    ) -> None:
        if compression_rate < 1.0:
            raise ValueError("LLMLingua-2 compression_rate must be at least 1.0")
        try:
            from llmlingua import PromptCompressor
        except ImportError as exc:
            raise CompressorFailure(
                "LLMLingua is required for refined runs; install experiments/context_refinement/requirements.txt"
            ) from exc
        self.name = self.__class__.name
        self.config = {
            "name": self.name,
            "model_name": model_name,
            "compression_rate": compression_rate,
            "device_map": device_map,
            "force_tokens": [],
            "force_reserve_digit": False,
            "task_aware": False,
        }
        try:
            self._compressor = PromptCompressor(
                model_name=model_name,
                device_map=device_map,
                use_llmlingua2=True,
            )
        except Exception as exc:
            raise CompressorFailure(f"Failed to load LLMLingua-2 compressor: {exc}") from exc
        self._compression_rate = compression_rate

    def refine(self, context: str) -> RefinedContext:
        if not context.strip():
            raise CompressorFailure("Cannot refine an empty context")
        try:
            result = self._compressor.compress_prompt_llmlingua2(
                [context],
                rate=self._compression_rate,
                force_tokens=[],
                force_reserve_digit=False,
                chunk_end_tokens=[".", "\n"],
            )
        except Exception as exc:
            raise CompressorFailure(f"LLMLingua-2 compression failed: {exc}") from exc
        refined = result.get("compressed_prompt") if isinstance(result, dict) else None
        if not isinstance(refined, str) or not refined.strip():
            raise CompressorFailure("LLMLingua-2 returned no refined context")
        return RefinedContext(
            raw_context=context,
            refined_context=refined.strip(),
            origin_tokens=_as_int(result.get("origin_tokens")),
            refined_tokens=_as_int(result.get("compressed_tokens")),
        )


def _as_int(value: Any) -> int | None:
    return int(value) if isinstance(value, (int, float, str)) and str(value).isdigit() else None

