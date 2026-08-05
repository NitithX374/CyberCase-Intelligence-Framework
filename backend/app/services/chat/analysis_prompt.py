"""Build the internal task prompt used by the website chat workflow."""

from __future__ import annotations


CHAT_ANALYSIS_PREPROMPT = (
    "Determine the exact initial-access mechanism and MITRE ATT&CK sub-technique "
    "used to obtain access to the Microsoft 365 account. Return one "
    "incident-specific supported conclusion, not a list of possibilities, and "
    "do not infer facts that are not in the case file."
)
_CASE_CONTEXT_LABEL = "Incident information from the case file:"
_PROMPT_PREFIX = f"{CHAT_ANALYSIS_PREPROMPT}\n\n{_CASE_CONTEXT_LABEL}\n"


def build_chat_analysis_prompt(user_content: str) -> str:
    """Add the experiment task instruction without changing persisted user text."""

    content = user_content.strip()
    if content.startswith(_PROMPT_PREFIX):
        return content
    return f"{_PROMPT_PREFIX}{content}"
