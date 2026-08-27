from app.services.document_ingestion.contracts import DocumentRegion


def order_regions(regions: list[DocumentRegion]) -> list[DocumentRegion]:
    return sorted(
        regions,
        key=lambda region: (
            region.bbox.y0 if region.bbox else float("inf"),
            region.bbox.x0 if region.bbox else float("inf"),
            region.region_id,
        ),
    )


def merge_region_text(regions: list[DocumentRegion]) -> str:
    return "\n".join(region.text for region in order_regions(regions) if region.text)
