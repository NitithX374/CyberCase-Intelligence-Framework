import argparse
import sys
from pathlib import Path

from pypdf import PdfReader


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("key")
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    arguments = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    reader = PdfReader(project / "literature" / "papers" / f"{arguments.key}.pdf")
    for index in range(arguments.start - 1, arguments.end):
        print(f"\n=== {arguments.key} PDF PAGE {index + 1} ===\n")
        print(reader.pages[index].extract_text())


if __name__ == "__main__":
    main()
