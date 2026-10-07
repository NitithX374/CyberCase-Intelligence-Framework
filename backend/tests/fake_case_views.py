from app.analysis.view_schema import DerivedCaseViewsReply


async def empty_view_reply(**kwargs):
    return DerivedCaseViewsReply(parties=[], timeline=[], impacts=[])
