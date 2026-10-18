import argparse
from pathlib import Path

import pypdfium2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("key")
    parser.add_argument("pages", nargs="+", type=int)
    arguments = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    directory = project / "literature" / "previews"
    directory.mkdir(parents=True, exist_ok=True)
    document = pypdfium2.PdfDocument(project / "literature" / "papers" / f"{arguments.key}.pdf")
    for number in arguments.pages:
        page = document[number - 1]
        bitmap = page.render(scale=1.7)
        output = directory / f"{arguments.key}-p{number}.png"
        bitmap.to_pil().save(output)
        bitmap.close()
        page.close()
        print(output)
    document.close()


if __name__ == "__main__":
    main()
