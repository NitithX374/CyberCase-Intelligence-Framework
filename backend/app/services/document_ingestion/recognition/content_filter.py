import re


_FIGURE_PATTERN = re.compile(
    r"<figure\b[^>]*>(.*?)</figure>", re.DOTALL | re.IGNORECASE
)


def separate_generated_visual_descriptions(text: str) -> tuple[str, list[str]]:
    descriptions = [
        " ".join(match.split())
        for match in _FIGURE_PATTERN.findall(text)
        if match.strip()
    ]
    transcription = _FIGURE_PATTERN.sub("", text)
    transcription = re.sub(r"\n{3,}", "\n\n", transcription).strip()
    return transcription, descriptions
