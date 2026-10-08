from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class SourceTable:
    start: int
    end: int
    row_starts: tuple[int, ...]


class TableParser(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.text = text
        self.line_offsets = [0]
        for match in re.finditer("\n", text):
            self.line_offsets.append(match.end())
        self.depth = 0
        self.start = 0
        self.rows: list[int] = []
        self.tables: list[SourceTable] = []

    def source_offset(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            if self.depth == 0:
                self.start, self.rows = self.source_offset(), []
            self.depth += 1
        elif tag == "tr" and self.depth == 1:
            self.rows.append(self.source_offset())

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self.depth:
            self.depth -= 1
            if self.depth == 0:
                end = self.text.index(">", self.source_offset()) + 1
                self.tables.append(SourceTable(self.start, end, tuple(self.rows)))


def source_tables(text: str) -> list[SourceTable]:
    parser = TableParser(text)
    parser.feed(text)
    parser.close()
    if parser.depth:
        parser.tables.append(SourceTable(parser.start, len(text), tuple(parser.rows)))
    return parser.tables
