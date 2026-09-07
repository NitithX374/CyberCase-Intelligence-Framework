import os
import sys
import shutil
import docx

from kmutnb_thai_helpers import setup_page_setup
from kmutnb_thai_front_matter import build_front_matter
from kmutnb_thai_chapter_1_2 import build_chapter_1, build_chapter_2
from kmutnb_thai_chapter_3 import build_chapter_3
from kmutnb_thai_chapter_4 import build_chapter_4
from kmutnb_thai_chapter_5_6 import build_chapter_5, build_chapter_6, build_bibliography

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DELIVERABLES_DIR = r"f:\Cybercase Framework\deliverables\thesis_kmutnb_thai"
ROOT_DIR = r"f:\Cybercase Framework"
os.makedirs(DELIVERABLES_DIR, exist_ok=True)

def build_monolithic_thesis():
    print("Building full monolithic KMUTNB Thai thesis document...")
    doc = docx.Document()
    setup_page_setup(doc.sections[0])
    
    print("  -> Adding Front Matter...")
    build_front_matter(doc)
    
    print("  -> Adding Chapter 1: บทนำ...")
    build_chapter_1(doc)
    
    print("  -> Adding Chapter 2: ทฤษฎีและงานวิจัยที่เกี่ยวข้อง...")
    build_chapter_2(doc)
    
    print("  -> Adding Chapter 3: ขั้นตอนและวิธีการดำเนินงาน (Use Cases & Data Dictionaries)...")
    build_chapter_3(doc)
    
    print("  -> Adding Chapter 4: การพัฒนาระบบ (Code Walkthroughs)...")
    build_chapter_4(doc)
    
    print("  -> Adding Chapter 5: ผลการดำเนินโครงการและการแสดงผล (UI & Test Receipts)...")
    build_chapter_5(doc)
    
    print("  -> Adding Chapter 6: บทสรุป ปัญหา และแนวทางในการพัฒนาต่อ...")
    build_chapter_6(doc)
    
    print("  -> Adding บรรณานุกรม...")
    build_bibliography(doc)
    
    out_deliverable = os.path.join(DELIVERABLES_DIR, "Cybercase_Thesis_KMUTNB_Full_Detailed_Thai.docx")
    doc.save(out_deliverable)
    print(f"Saved monolithic deliverable to: {out_deliverable} ({os.path.getsize(out_deliverable):,} bytes)")
    
    out_root = os.path.join(ROOT_DIR, "Cybercase_Thesis_KMUTNB_Full_Detailed_Thai.docx")
    shutil.copyfile(out_deliverable, out_root)
    print(f"Copied to root workspace: {out_root} ({os.path.getsize(out_root):,} bytes)")

def build_individual_chapters():
    print("\nBuilding individual chapter documents...")
    chapters = [
        ("บทที่_1_บทนำ.docx", build_chapter_1),
        ("บทที่_2_ทฤษฎีและงานวิจัยที่เกี่ยวข้อง.docx", build_chapter_2),
        ("บทที่_3_ขั้นตอนและวิธีการดำเนินงาน.docx", build_chapter_3),
        ("บทที่_4_การพัฒนาระบบ.docx", build_chapter_4),
        ("บทที่_5_ผลการดำเนินโครงการและการแสดงผล.docx", build_chapter_5),
        ("บทที่_6_บทสรุปและแนวทางการพัฒนาต่อ.docx", build_chapter_6),
    ]
    
    for filename, builder_fn in chapters:
        doc = docx.Document()
        setup_page_setup(doc.sections[0])
        builder_fn(doc)
        out_path = os.path.join(DELIVERABLES_DIR, filename)
        doc.save(out_path)
        print(f"  -> Generated: {filename} ({os.path.getsize(out_path):,} bytes)")

if __name__ == "__main__":
    build_monolithic_thesis()
    build_individual_chapters()
    print("\nAll KMUTNB Thai thesis documents built successfully!")
