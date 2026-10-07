from app.analysis.views import DerivedCaseViewsReply


async def empty_view_reply(**kwargs):
    return DerivedCaseViewsReply(parties=[], timeline=[], impacts=[])
