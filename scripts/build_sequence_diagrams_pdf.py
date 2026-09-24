import os
import shutil
import subprocess
import pypdf

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(base_dir, "docs", "architecture", "CyberCase_Sequence_Diagrams.html")
    pdf_path = os.path.join(base_dir, "docs", "architecture", "CyberCase_Sequence_Diagrams.pdf")
    root_pdf_path = os.path.join(base_dir, "CyberCase_Sequence_Diagrams.pdf")

    edge_bin = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_bin):
        edge_bin = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    html_url = "file:///" + html_path.replace("\\", "/")

    cmd = [
        edge_bin,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--virtual-time-budget=8000",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        html_url,
    ]

    print(f"Generating PDF from: {html_url}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("Process return code:", res.returncode)

    if os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        print(f"Generated PDF: {pdf_path} ({size:,} bytes)")
        shutil.copyfile(pdf_path, root_pdf_path)
        print(f"Copied to root: {root_pdf_path}")

        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            print(f"Total Pages: {len(reader.pages)}")
            for idx, page in enumerate(reader.pages):
                first_line = page.extract_text().split("\n")[0] if page.extract_text() else ""
                print(f"  - Page {idx + 1}: {first_line}")
    else:
        print("ERROR: PDF file was not created!")
        print("Stderr:", res.stderr)

if __name__ == "__main__":
    main()
