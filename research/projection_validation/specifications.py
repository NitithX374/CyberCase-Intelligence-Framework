from __future__ import annotations

from research.projection_validation.controlled import projections

ENGLISH = [
    (
        "John",
        "a witness",
        "Jane",
        "a complainant",
        "13:00",
        "14:00",
        "John sent an email to North Company.",
        "John encrypted North Company's server.",
        "Jane filed a complaint.",
        "North Company lost 25,000 baht.",
        [
            "North Company lost 35,000 baht.",
            "South Company lost 25,000 baht.",
            "North Company suffered catastrophic and irreversible damage and lost 25,000 baht.",
            "Jane's laptop was damaged.",
        ],
    ),
    (
        "Jane Smith",
        "a victim",
        "Alex Jones",
        "a witness",
        "12 May 2026",
        "13 May 2026",
        "The bank approved Jane Smith's transfer.",
        "The bank reversed Jane Smith's transfer.",
        "Alex Jones sent an email.",
        "Jane Smith lost 25,000 baht.",
        [
            "Jane Smith lost 52,000 baht.",
            "Alex Jones lost 25,000 baht.",
            "Jane Smith became permanently bankrupt after losing 25,000 baht.",
            "Alex Jones's car was stolen.",
        ],
    ),
    (
        "Mira",
        "an employee",
        "Oleg",
        "an investigator",
        "09:00",
        "10:00",
        "The archive door was opened.",
        "The archive window was broken.",
        "Oleg reported the incident.",
        "Two laptops in the archive were damaged.",
        [
            "Three laptops in the archive were damaged.",
            "Two printers in the archive were damaged.",
            "The archive suffered catastrophic damage and two laptops were damaged.",
            "Oleg's laptop was lost.",
        ],
    ),
    (
        "Sam",
        "a dispatcher",
        "Priya",
        "a passenger",
        "12:00",
        "12:30",
        "The payroll server was restarted.",
        "The payroll server was encrypted.",
        "Priya purchased a train ticket.",
        "Payroll was interrupted for two days.",
        [
            "Payroll was interrupted for three days.",
            "Company email was interrupted for two days.",
            "Payroll data was permanently destroyed and payroll was interrupted for two days.",
            "Priya's train was cancelled.",
        ],
    ),
    (
        "Lina",
        "a complainant",
        "Ben",
        "a witness",
        "7 June 2026",
        "8 June 2026",
        "Lina's medical file was accessed.",
        "Lina's medical file was deleted.",
        "Ben signed a statement.",
        "One of Lina's medical files was exposed.",
        [
            "Two of Lina's medical files were exposed.",
            "One of Lina's payroll files was exposed.",
            "Lina suffered severe permanent injury when one of her medical files was exposed.",
            "Ben's phone was stolen.",
        ],
    ),
    (
        "Omar",
        "an investigator",
        "Eva",
        "an employee",
        "15:45",
        "16:45",
        "The police received the incident report.",
        "The police recovered a stolen car.",
        "Eva rented a car.",
        "Shop A lost five computers.",
        [
            "Shop A lost six computers.",
            "Shop B lost five computers.",
            "Shop A became permanently bankrupt after losing five computers.",
            "Eva's bicycle was broken.",
        ],
    ),
]

THAI = [
    (
        "สมชาย",
        "ผู้เห็นเหตุการณ์",
        "มาลี",
        "ผู้ร้องทุกข์",
        "13:00 น.",
        "14:00 น.",
        "สมชายส่งอีเมลถึงบริษัทเหนือ",
        "สมชายเข้ารหัสเซิร์ฟเวอร์ของบริษัทเหนือ",
        "มาลียื่นคำร้องทุกข์",
        "บริษัทเหนือสูญเสียเงิน 25,000 บาท",
        [
            "บริษัทเหนือสูญเสียเงิน 35,000 บาท",
            "บริษัทใต้สูญเสียเงิน 25,000 บาท",
            "บริษัทเหนือได้รับความเสียหายร้ายแรงที่ไม่สามารถฟื้นฟูได้และสูญเสียเงิน 25,000 บาท",
            "คอมพิวเตอร์ของมาลีเสียหาย",
        ],
    ),
    (
        "จันทร์",
        "ผู้เสียหาย",
        "อาทิตย์",
        "พยาน",
        "12 พฤษภาคม 2569",
        "13 พฤษภาคม 2569",
        "ธนาคารอนุมัติการโอนเงินของจันทร์",
        "ธนาคารยกเลิกการโอนเงินของจันทร์",
        "อาทิตย์ส่งอีเมล",
        "จันทร์สูญเสียเงิน 25,000 บาท",
        [
            "จันทร์สูญเสียเงิน 52,000 บาท",
            "อาทิตย์สูญเสียเงิน 25,000 บาท",
            "จันทร์ล้มละลายถาวรหลังสูญเสียเงิน 25,000 บาท",
            "รถยนต์ของอาทิตย์ถูกขโมย",
        ],
    ),
    (
        "มินา",
        "พนักงาน",
        "โอภาส",
        "พนักงานสอบสวน",
        "09:00 น.",
        "10:00 น.",
        "ประตูห้องเอกสารถูกเปิด",
        "หน้าต่างห้องเอกสารถูกทุบ",
        "โอภาสแจ้งเหตุ",
        "คอมพิวเตอร์พกพาในห้องเอกสารเสียหายสองเครื่อง",
        [
            "คอมพิวเตอร์พกพาในห้องเอกสารเสียหายสามเครื่อง",
            "เครื่องพิมพ์ในห้องเอกสารเสียหายสองเครื่อง",
            "ห้องเอกสารได้รับความเสียหายร้ายแรงและคอมพิวเตอร์พกพาเสียหายสองเครื่อง",
            "คอมพิวเตอร์พกพาของโอภาสสูญหาย",
        ],
    ),
    (
        "ศักดิ์",
        "พนักงานรับแจ้งเหตุ",
        "ปรียา",
        "ผู้โดยสาร",
        "12:00 น.",
        "12:30 น.",
        "เซิร์ฟเวอร์เงินเดือนถูกเริ่มระบบใหม่",
        "เซิร์ฟเวอร์เงินเดือนถูกเข้ารหัส",
        "ปรียาซื้อตั๋วรถไฟ",
        "การจ่ายเงินเดือนหยุดชะงักเป็นเวลาสองวัน",
        [
            "การจ่ายเงินเดือนหยุดชะงักเป็นเวลาสามวัน",
            "อีเมลบริษัทหยุดชะงักเป็นเวลาสองวัน",
            "ข้อมูลเงินเดือนถูกทำลายถาวรและการจ่ายเงินเดือนหยุดชะงักเป็นเวลาสองวัน",
            "ขบวนรถไฟของปรียาถูกยกเลิก",
        ],
    ),
    (
        "ลินา",
        "ผู้ร้องทุกข์",
        "เบญ",
        "พยาน",
        "7 มิถุนายน 2569",
        "8 มิถุนายน 2569",
        "แฟ้มประวัติการรักษาของลินาถูกเข้าถึง",
        "แฟ้มประวัติการรักษาของลินาถูกลบ",
        "เบญลงนามในคำให้การ",
        "แฟ้มประวัติการรักษาของลินาถูกเปิดเผยหนึ่งแฟ้ม",
        [
            "แฟ้มประวัติการรักษาของลินาถูกเปิดเผยสองแฟ้ม",
            "แฟ้มเงินเดือนของลินาถูกเปิดเผยหนึ่งแฟ้ม",
            "ลินาได้รับบาดเจ็บร้ายแรงถาวรหลังแฟ้มประวัติการรักษาถูกเปิดเผยหนึ่งแฟ้ม",
            "โทรศัพท์ของเบญถูกขโมย",
        ],
    ),
    (
        "อำนาจ",
        "พนักงานสอบสวน",
        "เอวา",
        "พนักงาน",
        "15:45 น.",
        "16:45 น.",
        "ตำรวจได้รับรายงานเหตุ",
        "ตำรวจพบรถยนต์ที่ถูกขโมย",
        "เอวาเช่ารถยนต์",
        "ร้าน ก สูญเสียคอมพิวเตอร์ห้าเครื่อง",
        [
            "ร้าน ก สูญเสียคอมพิวเตอร์หกเครื่อง",
            "ร้าน ข สูญเสียคอมพิวเตอร์ห้าเครื่อง",
            "ร้าน ก ล้มละลายถาวรหลังสูญเสียคอมพิวเตอร์ห้าเครื่อง",
            "จักรยานของเอวาชำรุด",
        ],
    ),
]


def controlled_specs() -> list[dict]:
    output = []
    for language, contexts in (("english", ENGLISH), ("thai", THAI)):
        for index, context in enumerate(contexts, 1):
            (
                name,
                role,
                other,
                other_role,
                time,
                wrong_time,
                event,
                wrong_event,
                other_event,
                impact,
                bad,
            ) = context
            thai = language == "thai"
            claims = [
                f"{name} เป็น{role}และได้รายงานเหตุ"
                if thai
                else f"{name} is {role} and reported the incident.",
                f"เวลา {time} {event}" if thai else f"At {time}, {event}",
                impact,
                (
                    f"{other} เป็น{other_role} เวลา 16:00 น. {other_event} {bad[-1]}"
                    if thai
                    else f"{other} is {other_role}. At 16:00, {other_event} {bad[-1]}"
                ),
            ]
            causal = (
                f"{event}เพราะผู้โจมตีข่มขู่{other}"
                if thai
                else event.rstrip(".") + f" because the attacker threatened {other}."
            )
            output.append(
                {
                    "case_id": f"controlled-{language}-{index:02d}",
                    "family_id": f"controlled-family-{index:02d}",
                    "language": language,
                    "claims": claims,
                    "projections": projections(
                        name,
                        other,
                        role,
                        "ผู้โจมตี" if thai else "the attacker",
                        other_role,
                        "ผู้กระทำผิดที่ศาลพิพากษาลงโทษ" if thai else "the convicted offender",
                        time,
                        wrong_time,
                        event,
                        wrong_event,
                        other_event,
                        causal,
                        impact,
                        bad,
                    ),
                }
            )
    return output
