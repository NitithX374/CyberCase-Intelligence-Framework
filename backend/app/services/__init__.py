"""Backend domain services.

Deliberately empty. Python runs this file on any ``app.services.*`` import, so
re-exporting the subpackages here made every import pull all of them — a
router that wanted a JWT helper loaded reportlab, the analysis pipeline and the
RAG client, and a mistake in any leaf broke the whole application. Nothing ever
imported the names it exported.
"""
