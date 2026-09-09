import asyncio
import json

import httpx
import pytest
from app.config import settings
from app.services.case_analysis.claim_anchored.failure import ClaimAnchoredFailure
from app.services.case_analysis.claim_anchored.service import analyze_claim_anchored
from app.services.case_analysis.pipeline_config import AnalysisPipelineConfig
from test_claim_anchored_binding import extraction, source_context
from test_claim_anchored_pipeline import envelope


@pytest.mark.parametrize("reject", [False, True])
def test_future_verifier_can_reject_but_cannot_mutate_bound_claims(monkeypatch, reject):
    monkeypatch.setattr(settings, "openrouter_cybercase", "test")
    requests = []
    checks = []
    content = "The witness did not see the suspect."

    class Verifier:
        async def check_claims(self, claims):
            checks.append("claims")
            if reject:
                raise ClaimAnchoredFailure(
                    "semantic_claim_rejected", "Claim was rejected"
                )
            claims[0].claim.text = "Mutation must not enter generation"

        async def check_summary(self, summary, claims):
            checks.append("summary")
            claims[0].claim.text = "Mutation must not enter persisted trace"

    def handler(request):
        requests.append(json.loads(request.content))
        assert "Mutation must not" not in request.content.decode()
        value = (
            extraction(content).model_dump(mode="json")
            if len(requests) == 1
            else {"units": [{"text": content, "claim_ids": ["A-01"]}]}
        )
        return httpx.Response(200, json=envelope(value))

    async def exercise():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await analyze_claim_anchored(
                raw_evidence=content,
                analysis_context=source_context(content),
                user_message=content,
                config=AnalysisPipelineConfig(pipeline="claim_anchored"),
                client=client,
                verifier=Verifier(),
            )

    if reject:
        with pytest.raises(ClaimAnchoredFailure) as error:
            asyncio.run(exercise())
        assert error.value.code == "semantic_claim_rejected"
        assert len(requests) == 1
        assert checks == ["claims"]
    else:
        result = asyncio.run(exercise())
        assert result.trace.claims[0].text == content
        assert checks == ["claims", "summary"]
        assert result.execution_receipt["semantic_verification"] == "completed"
