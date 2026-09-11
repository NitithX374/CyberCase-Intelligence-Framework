import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from app.services.case_analysis.claim_anchored.service import analyze_claim_anchored
from app.services.case_analysis.claim_anchored.contracts import ClaimAnchoredFailure
from app.services.case_analysis.pipelineConfig import (
    AnalysisPipelineConfig,
)


async def smoke(output: Path) -> None:
    content = (
        "นายสมชายแจ้งว่าจักรยานของตนหายจากหน้าบ้านเมื่อวันที่ 1 กันยายน 2569 "
        "นางมาลีระบุว่าไม่เห็นผู้ที่นำจักรยานไป และยังไม่ทราบว่ามีกล้องวงจรปิดบริเวณนั้นหรือไม่"
    )
    raw = f"[INITIAL CASE NARRATIVE]\n{content}"
    config = AnalysisPipelineConfig(pipeline="claim_anchored")
    context = {
        "source_message_ids": ["synthetic-source-1"],
        "_source_text_by_message_id": {"synthetic-source-1": content},
        "_evidence_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "_analysis_pipeline": config.model_dump(mode="json"),
    }
    try:
        result = await analyze_claim_anchored(
            raw_evidence=raw,
            analysis_context=context,
            user_message=content,
            config=config,
        )
    except ClaimAnchoredFailure as error:
        receipt = {
            "status": "failed",
            "error_code": error.code,
            "execution": error.receipt,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps({"status": "failed", "code": error.code}))
        raise SystemExit(1) from error
    receipt = {
        "status": "completed",
        "input_kind": "synthetic_thai_case",
        "trace": result.trace.model_dump(mode="json"),
        "execution": result.execution_receipt,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "completed",
                "claim_count": len(result.trace.claims),
                "summary": result.answer,
                "calls": result.execution_receipt["calls"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(smoke(parser.parse_args().output))
