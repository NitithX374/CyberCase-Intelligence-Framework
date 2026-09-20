"""Assemble Chapter 4 and write the .docx.

    cd docs/thesis && python make_chapter4.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import chapter4_content as part1  # noqa: E402
import chapter4_content2 as part2  # noqa: E402
import chapter4_content3 as part3  # noqa: E402
from build_chapter4 import OUTPUT, Chapter  # noqa: E402

SECTIONS = (
    part1.opening,
    part1.environment,
    part1.structure,
    part1.sources,
    part2.pipeline,
    part2.gate,
    part2.contract,
    part2.grounding,
    part3.verification,
    part3.followup,
    part3.reports,
    part3.frontend,
    part3.testing,
    part3.summary,
)


def main() -> int:
    chapter = Chapter()
    for section in SECTIONS:
        section(chapter)
    chapter.save()
    print(f"wrote {OUTPUT}")
    print(f"  {chapter.figure} code figures, {chapter.table_number} tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
