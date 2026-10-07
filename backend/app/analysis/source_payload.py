from app.sources.bundle import CaseSourceItem


def provider_source_payload(source: CaseSourceItem) -> dict[str, object]:
    payload: dict[str, object] = {
        "source_id": source.source_id,
        "source_kind": source.source_kind,
        "text": source.text,
    }
    if source.source_kind == "document" or source.document_id or source.filename:
        document: dict[str, object] = {
            "document_id": source.document_id,
            "filename": source.filename,
        }
        for quality_key in ("extraction_method", "verification_status", "warnings"):
            if quality_key in source.provenance:
                document[quality_key] = source.provenance[quality_key]
        payload["document"] = document
    return payload
