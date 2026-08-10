# Real-CTI Thai Dataset — Review Sheet

100 สำนวน / 347 steps

ตรวจ 4 ข้อต่อสำนวน แล้วแก้ใน `data/CTI_dataset.json` โดยตรง:

1. **สำนวน** — อ่านแล้วเหมือนสำนวนคดีจริงไหม หรือยังกลิ่นแปล
2. **described cue** — อ่าน cue แล้วเดาออกไหมว่าเป็น technique ที่ระบุ ถ้าเดาไม่ออกเลย = กำกวมเกินไป / ถ้าเดาออกทันทีเพราะมีชื่อเทคนิคอยู่ = ควรเป็น named
3. **named cue** — ศัพท์อังกฤษที่แทรกดูฝืนไหม
4. **บริบทผู้เสียหาย** — ฉากที่แต่งขึ้นสมเหตุสมผลกับพฤติกรรมไหม

คอลัมน์ *ต้นฉบับ* คือข้อความอังกฤษจากแหล่งต้นทางที่ cue นั้นแปลมา — ใช้เทียบว่าแปลตรงและไม่ได้เติมเนื้อหาเอง

> ⚠️ ถ้าแก้ `cue` ต้องแก้ให้ยังเป็นข้อความย่อย**ตรงตัวอักษร**ใน `query` ไม่งั้น validator จะไม่ผ่าน ตรวจซ้ำด้วย `thai_dataset status`

---

## rcti_001 — CISA AA23-158A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-158a>

> เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่งในจังหวัดนนทบุรีแจ้งความว่าระบบรับส่งไฟล์ผ่านเว็บของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ของเว็บเซิร์ฟเวอร์พบว่าคนร้ายส่งคำสั่งฐานข้อมูลแทรกเข้าไปทางช่องกรอกข้อมูลบนหน้าเว็บที่เปิดให้บริการต่อสาธารณะ จนสามารถวางไฟล์สคริปต์สำหรับสั่งการระยะไกลไว้บนเซิร์ฟเวอร์ได้ ต่อมาพบว่าคนร้ายใช้เทคนิค Application Shimming เพื่อให้โปรแกรมของตนถูกเรียกทำงานทุกครั้งที่เครื่องเริ่มระบบ จากนั้นเมื่อเข้าถึงเครื่องแม่ข่ายที่ทำหน้าที่ควบคุมบัญชีผู้ใช้ขององค์กรได้แล้ว ปรากฏหลักฐานการไล่ค้นหารายชื่อเครื่องลูกข่ายอื่นในวงเครือข่ายเพื่อขยายขอบเขตการเข้าถึง สุดท้ายจากการตรวจสอบเครื่องคอมพิวเตอร์ของพนักงานพบโปรแกรมไม่พึงประสงค์ที่ทำหน้าที่รวบรวมรายละเอียดของเครื่องและบันทึกภาพหน้าจอส่งออกไปยังเครื่องปลายทางของคนร้าย

*EN:* On 12 May 2023 a private company in Nonthaburi province reported that its web-based file transfer system had been accessed without authorisation. Web server logs showed that the offender submitted database commands through an input field on a publicly reachable web page, and was thereby able to place a script for remote command execution on the server. The offender was subsequently found to have used the Application Shimming technique so that their program would be run every time the machine started. After reaching the server that manages the organisation's user accounts, evidence showed the offender enumerating the names of other client machines on the network in order to widen their access. Finally, examination of employee workstations found an unwanted program that gathered machine details and captured images of the screen, sending them out to the offender's endpoint.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1190 Exploit Public-Facing Application | คนร้ายส่งคำสั่งฐานข้อมูลแทรกเข้าไปทางช่องกรอกข้อมูลบนหน้าเว็บที่เปิดให้บริการต่อสาธารณะ จนสามารถวางไฟล์สคริปต์สำหรับสั่งการระยะไกลไว้บนเซิร์ฟเวอร์ได้ | In May 2023, the CL0P ransomware group exploited a SQL injection zero-day vulnerability CVE-2023-34362 to install a web shell named LEMURLOOT on MOVEit Transfer web applications |
| 2 | named | T1546 Event Triggered Execution | ใช้เทคนิค Application Shimming เพื่อให้โปรแกรมของตนถูกเรียกทำงานทุกครั้งที่เครื่องเริ่มระบบ | This malware uses application shimming for persistence and to avoid detection |
| 3 | described | T1018 Remote System Discovery | ปรากฏหลักฐานการไล่ค้นหารายชื่อเครื่องลูกข่ายอื่นในวงเครือข่ายเพื่อขยายขอบเขตการเข้าถึง | Cobalt Strike is used to expand network access after gaining access to the Active Directory (AD) server |
| 4 | described | T1113 Screen Capture | รวบรวมรายละเอียดของเครื่องและบันทึกภาพหน้าจอส่งออกไปยังเครื่องปลายทางของคนร้าย | Truebot is a first-stage downloader module that can collect system information and take screenshots , developed and attributed to the Silence hacking group |

- [ ] ผ่าน / แก้แล้ว

## rcti_002 — CISA AA22-294A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-294a>

> เมื่อวันที่ 3 ตุลาคม 2565 โรงพยาบาลเอกชนแห่งหนึ่งในจังหวัดเชียงใหม่แจ้งว่าระบบเวชระเบียนอิเล็กทรอนิกส์ไม่สามารถใช้งานได้ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายทำ Credential Dumping เพื่อดึงค่าแฮชรหัสผ่านออกจากหน่วยความจำของเครื่องแม่ข่าย แล้วนำค่าดังกล่าวไปทำ Pass the Hash เข้าสู่บัญชีที่มีสิทธิ์ระดับผู้ดูแลระบบโดยไม่ต้องทราบรหัสผ่านจริง ต่อมาปรากฏว่าคนร้ายใช้บัญชีสิทธิ์สูงดังกล่าวเข้าไปยังระบบบริหารจัดการเครื่องเสมือนของโรงพยาบาล และตั้งรหัสผ่านของบัญชีผู้ดูแลเครื่องแม่ข่ายเสมือนขึ้นใหม่ ทำให้เจ้าหน้าที่ของโรงพยาบาลเข้าใช้งานระบบของตนเองไม่ได้ จากการตรวจสอบปริมาณข้อมูลขาออกพบว่ามีการติดตั้งโปรแกรมสร้างช่องทางเชื่อมต่อออกสู่ภายนอกผ่านผู้ให้บริการรายหนึ่ง แล้วลำเลียงข้อมูลของโรงพยาบาลออกไปทางช่องทางนั้น สุดท้ายคนร้ายเชื่อมต่อเข้าเครื่องแม่ข่ายเสมือนทุกเครื่องผ่าน SSH แล้วสั่งเข้ารหัสลับข้อมูลทั้งหมดจนระบบหยุดให้บริการ

*EN:* On 3 October 2565 a private hospital in Chiang Mai province reported that its electronic medical record system was unusable. Digital forensic examination found that the offender performed Credential Dumping to extract password hashes from the memory of a server, then used those values to perform Pass the Hash into an account with administrator privileges without needing to know the real password. The offender then used that privileged account to reach the hospital's virtual machine management system and set a new password for the account administering the virtual servers, leaving hospital staff unable to log in to their own system. Examination of outbound traffic volume found that a program had been installed to create an outbound tunnel through a third-party provider, and hospital data was carried out through that channel. Finally the offender connected to every virtual server over SSH and ordered all data encrypted until the system stopped serving.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1003 OS Credential Dumping, T1550 Use Alternate Authentication Material | คนร้ายทำ Credential Dumping เพื่อดึงค่าแฮชรหัสผ่านออกจากหน่วยความจำของเครื่องแม่ข่าย แล้วนำค่าดังกล่าวไปทำ Pass the Hash เข้าสู่บัญชีที่มีสิทธิ์ระดับผู้ดูแลระบบโดยไม่ต้องทราบรหัสผ่านจริง | Daixin actors have sought to gain privileged account access through credential dumping and pass the hash |
| 2 | described | T1098 Account Manipulation | คนร้ายใช้บัญชีสิทธิ์สูงดังกล่าวเข้าไปยังระบบบริหารจัดการเครื่องเสมือนของโรงพยาบาล และตั้งรหัสผ่านของบัญชีผู้ดูแลเครื่องแม่ข่ายเสมือนขึ้นใหม่ | The actors have leveraged privileged accounts to gain access to VMware vCenter Server and reset account passwords for ESXi servers in the environment |
| 3 | described | T1567 Exfiltration Over Web Service | มีการติดตั้งโปรแกรมสร้างช่องทางเชื่อมต่อออกสู่ภายนอกผ่านผู้ให้บริการรายหนึ่ง แล้วลำเลียงข้อมูลของโรงพยาบาลออกไปทางช่องทางนั้น | In another compromise, the actors used Ngrok—a reverse proxy tool for proxying an internal service out onto an Ngrok domain—for data exfiltration |
| 4 | described | T1486 Data Encrypted for Impact | คนร้ายเชื่อมต่อเข้าเครื่องแม่ข่ายเสมือนทุกเครื่องผ่าน SSH แล้วสั่งเข้ารหัสลับข้อมูลทั้งหมดจนระบบหยุดให้บริการ | The actors have then used SSH to connect to accessible ESXi servers and deploy ransomware on those servers |

- [ ] ผ่าน / แก้แล้ว

## rcti_003 — CISA AA22-321A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-321a>

> เมื่อวันที่ 18 พฤศจิกายน 2565 สหกรณ์แห่งหนึ่งในจังหวัดขอนแก่นได้รับแจ้งเบาะแสจากเจ้าหน้าที่ฝ่ายเทคโนโลยีสารสนเทศว่าข้อมูลสมาชิกในเครื่องแม่ข่ายถูกเข้ารหัสลับทั้งหมด จากการตรวจสอบ log การเข้าใช้งานพบว่าคนร้ายล็อกอินเข้ามาจากภายนอกผ่านช่องทางเชื่อมต่อระยะไกลของสหกรณ์ โดยใช้เพียงชื่อผู้ใช้และรหัสผ่านชั้นเดียวไม่มีการยืนยันตัวตนขั้นที่สอง นอกจากนี้ยังพบอีกช่องทางหนึ่ง คือมีการส่งอีเมลแนบไฟล์อันตรายถึงพนักงาน ควบคู่กับการยิงคำสั่งโจมตีช่องโหว่ที่ยังไม่ได้ปรับปรุงบนเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ขององค์กร ต่อมาก่อนการเข้ารหัสลับข้อมูล ปรากฏหลักฐานว่าคนร้ายไล่ตรวจหารายการโปรแกรมที่ทำงานอยู่ซึ่งเกี่ยวกับการสำรองข้อมูลและการป้องกันไวรัส แล้วสั่งหยุดการทำงานของโปรแกรมเหล่านั้นทีละรายการ

*EN:* On 18 November 2565 a cooperative in Khon Kaen province received a tip-off from its IT staff that all member data on the server had been encrypted. Access logs showed that the offender logged in from outside through the cooperative's remote connection channel using only a username and password with no second factor of authentication. A second route was also found: malicious file attachments were emailed to staff, alongside attack commands fired at an unpatched vulnerability on the organisation's mail server. Before the data was encrypted, evidence showed the offender enumerating running programs related to backup and virus protection, then stopping each of those programs one by one.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1133 External Remote Services | คนร้ายล็อกอินเข้ามาจากภายนอกผ่านช่องทางเชื่อมต่อระยะไกลของสหกรณ์ โดยใช้เพียงชื่อผู้ใช้และรหัสผ่านชั้นเดียวไม่มีการยืนยันตัวตนขั้นที่สอง | Hive actors have gained initial access to victim networks by using single factor logins via Remote Desktop Protocol (RDP), virtual private networks (VPNs), and other remote network connection protocols |
| 2 | described | T1566 Phishing, T1190 Exploit Public-Facing Application | มีการส่งอีเมลแนบไฟล์อันตรายถึงพนักงาน ควบคู่กับการยิงคำสั่งโจมตีช่องโหว่ที่ยังไม่ได้ปรับปรุงบนเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ขององค์กร | Hive actors have also gained initial access to victim networks by distributing phishing emails with malicious attachments and by exploiting the following vulnerabilities against Microsoft Exchange servers |
| 3 | described | T1562 ? | คนร้ายไล่ตรวจหารายการโปรแกรมที่ทำงานอยู่ซึ่งเกี่ยวกับการสำรองข้อมูลและการป้องกันไวรัส แล้วสั่งหยุดการทำงานของโปรแกรมเหล่านั้นทีละรายการ | Identify processes related to backups, antivirus/anti-spyware, and file copying and then terminating those processes to facilitate file encryption |

- [ ] ผ่าน / แก้แล้ว

## rcti_004 — CISA AA20-301A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-301a>

> เมื่อวันที่ 9 ตุลาคม 2563 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ฝ่ายวิเทศสัมพันธ์มีพฤติกรรมผิดปกติ จากการตรวจสอบพบว่าเจ้าหน้าที่ได้รับจดหมายอิเล็กทรอนิกส์ที่แอบอ้างเป็นหนังสือเชิญประชุมจากหน่วยงานคู่ความร่วมมือ ภายในมีทั้งลิงก์และไฟล์เอกสารแนบ เมื่อเจ้าหน้าที่เปิดไฟล์ดังกล่าวจึงมีสคริปต์ทำงานขึ้นบนเครื่อง จากการตรวจสอบต่อพบว่าสคริปต์นี้สร้าง Registry Run Key ไว้ในระบบเพื่อให้ตัวเองถูกเรียกทำงานทุกครั้งที่เปิดเครื่อง ต่อมาพบว่าโปรแกรมดังกล่าวเก็บรวบรวมรายละเอียดของเครื่อง ได้แก่ ชื่อเครื่อง รุ่นของระบบปฏิบัติการ และรายการซอฟต์แวร์ที่ติดตั้ง แล้วส่งออกไปยังเครื่องสั่งการของคนร้ายเพื่อรอรับคำสั่งต่อไป

*EN:* On 9 October 2563 a government agency reported that a computer belonging to an officer in its international affairs division was behaving abnormally. Examination found that the officer had received an email posing as a meeting invitation from a partner agency, containing both a link and an attached document file. When the officer opened that file, a script ran on the machine. Further examination found that this script created a Registry Run Key in the system so that it would be run every time the machine was switched on. The program was then found to gather details of the machine — its name, operating system version and list of installed software — and send them out to the offender's command machine to await further instructions.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1566 Phishing | เจ้าหน้าที่ได้รับจดหมายอิเล็กทรอนิกส์ที่แอบอ้างเป็นหนังสือเชิญประชุมจากหน่วยงานคู่ความร่วมมือ ภายในมีทั้งลิงก์และไฟล์เอกสารแนบ เมื่อเจ้าหน้าที่เปิดไฟล์ดังกล่าวจึงมีสคริปต์ทำงานขึ้นบนเครื่อง | Open-source reporting indicates BabyShark is delivered via an email message containing a link or an attachment (see Initial Access section for more information) (Phishing: Spearphising Link , Phishing: Spearphishing Atta… |
| 2 | named | T1547 Boot or Logon Autostart Execution | สคริปต์นี้สร้าง Registry Run Key ไว้ในระบบเพื่อให้ตัวเองถูกเรียกทำงานทุกครั้งที่เปิดเครื่อง | The script maintains Persistence [TA0003] by creating a Registry key that runs on startup (Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder ) |
| 3 | described | T1082 System Information Discovery | โปรแกรมดังกล่าวเก็บรวบรวมรายละเอียดของเครื่อง ได้แก่ ชื่อเครื่อง รุ่นของระบบปฏิบัติการ และรายการซอฟต์แวร์ที่ติดตั้ง แล้วส่งออกไปยังเครื่องสั่งการของคนร้าย | It then collects system information (System Information Discovery ), sends it to the operator’s command control (C2) servers, and awaits further commands |

- [ ] ผ่าน / แก้แล้ว

## rcti_005 — Sandworm Team (G0034) (CTID emulation plan sandworm.yaml)

ต้นทาง: <https://www.welivesecurity.com/2016/12/13/rise-telebots-analyzing-disruptive-killdisk-attacks/>

> เมื่อวันที่ 22 กุมภาพันธ์ 2567 บริษัทรับเหมาก่อสร้างแห่งหนึ่งในจังหวัดระยองแจ้งว่าบัญชีผู้ใช้งานระบบภายในของพนักงานหลายรายถูกนำไปใช้โดยบุคคลอื่น จากการตรวจสอบพยานหลักฐานดิจิทัลบนเครื่องแม่ข่ายพบว่า คนร้ายดาวน์โหลดไฟล์โปรแกรมจากเครื่องภายนอกเข้ามาเก็บไว้บนดิสก์ของเครื่องที่ยึดครองได้ ต่อมาเมื่อสั่งโปรแกรมดังกล่าวทำงาน ปรากฏว่าโปรแกรมเข้าไปอ่านแฟ้มที่โปรแกรมท่องเว็บใช้เก็บรหัสผ่านของผู้ใช้ แล้วถอดข้อมูลบัญชีและรหัสผ่านที่บันทึกไว้ออกมา จากนั้นคนร้ายดาวน์โหลดไฟล์โปรแกรมอีกตัวหนึ่งเข้ามาไว้บนเครื่องเดียวกัน และสั่งให้ทำงานเบื้องหลังเพื่อดักบันทึกทุกปุ่มที่ผู้ใช้กดบนแป้นพิมพ์ลงไฟล์ข้อความที่ซ่อนไว้ในเครื่อง

*EN:* On 22 February 2567 a construction contractor in Rayong province reported that the internal system accounts of several employees were being used by other people. Digital forensic examination of the server found that the offender downloaded a program file from an external machine and stored it on the disk of a machine they had taken over. When that program was run, it read the file in which the web browser stores users' passwords and extracted the saved account names and passwords. The offender then downloaded a second program file onto the same machine and ran it in the background to capture every key the user pressed on the keyboard into a hidden text file.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1105 Ingress Tool Transfer | คนร้ายดาวน์โหลดไฟล์โปรแกรมจากเครื่องภายนอกเข้ามาเก็บไว้บนดิสก์ของเครื่องที่ยึดครองได้ | Sandworm downloads web credential dumper oradump.exe to disk. oradump.exe is a variant of the open source tool, LaZagne. It has been refactored, some functionality removed, and compiled into a portable executable via PyI… |
| 2 | described | T1555 Credentials from Password Stores | โปรแกรมเข้าไปอ่านแฟ้มที่โปรแกรมท่องเว็บใช้เก็บรหัสผ่านของผู้ใช้ แล้วถอดข้อมูลบัญชีและรหัสผ่านที่บันทึกไว้ออกมา | Sandworm executes web credential dumper oradump.exe. |
| 3 | described | T1105 Ingress Tool Transfer | คนร้ายดาวน์โหลดไฟล์โปรแกรมอีกตัวหนึ่งเข้ามาไว้บนเครื่องเดียวกัน | Sandworm downloads keylogger to disk. |
| 4 | described | T1056 Input Capture | สั่งให้ทำงานเบื้องหลังเพื่อดักบันทึกทุกปุ่มที่ผู้ใช้กดบนแป้นพิมพ์ลงไฟล์ข้อความที่ซ่อนไว้ในเครื่อง | Sandworm runs the keylogger in the background to log keystrokes to mslog.txt. Sandworm Team has used a keylogger to capture keystrokes by using the SetWindowsHookEx function. Wait 30 seconds to allow the operator to perf… |

- [ ] ผ่าน / แก้แล้ว

## rcti_006 — CISA AA22-055A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-055a>

> เมื่อวันที่ 24 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่าเครื่องคอมพิวเตอร์ในสำนักงานอธิการบดีถูกฝังโปรแกรมไม่พึงประสงค์ จากการตรวจสอบพบว่าตัวติดตั้งโปรแกรมได้วางไฟล์ประตูหลังที่เขียนด้วยภาษาไพทอนลงในเครื่อง แล้วเพิ่มรายการเรียกใช้งานไฟล์นั้นไว้ในทะเบียนระบบ ทำให้โปรแกรมทำงานเองทุกครั้งที่เปิดเครื่อง จากการตรวจสอบชื่อไฟล์ที่เกี่ยวข้องพบว่าคนร้ายตั้งชื่อไฟล์ให้คล้ายคลึงกับชื่อผู้ผลิตซอฟต์แวร์รายใหญ่และชื่อโปรแกรมรับส่งอีเมลที่ใช้กันทั่วไป โดยสะกดผิดเพียงเล็กน้อยเพื่อให้ผู้ใช้เข้าใจผิดว่าเป็นไฟล์ของระบบ ต่อมาจากการตรวจสอบปริมาณข้อมูลขาออกพบว่าโปรแกรมดังกล่าวติดต่อกลับไปยังคนร้ายและรับคำสั่งผ่านช่องทางแอปพลิเคชันสนทนายอดนิยมโดยอาศัยโพรโทคอลเว็บที่เข้ารหัสลับ อีกทั้งเนื้อหาที่รับส่งยังถูกแปลงด้วยการสลับตำแหน่งไบต์ร่วมกับการเข้ารหัสข้อความอีกชั้นหนึ่งเพื่อไม่ให้ตรวจจับได้

*EN:* On 24 February 2565 an educational institution in Bangkok reported that computers in the rector's office had been implanted with an unwanted program. Examination found that an installer had placed a backdoor file written in the Python language onto the machine and added an entry calling that file into the system registry, causing the program to run by itself every time the machine was switched on. Examination of the related filenames found that the offender had named files to resemble the name of a major software vendor and that of a commonly used email program, misspelled only slightly so that users would mistake them for system files. Examination of outbound traffic then found that the program contacted the offender and received instructions through a popular chat application channel over an encrypted web protocol, and that the content exchanged was further transformed by swapping byte positions together with an additional layer of text encoding so that it could not be detected.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1547 Boot or Logon Autostart Execution | ตัวติดตั้งโปรแกรมได้วางไฟล์ประตูหลังที่เขียนด้วยภาษาไพทอนลงในเครื่อง แล้วเพิ่มรายการเรียกใช้งานไฟล์นั้นไว้ในทะเบียนระบบ ทำให้โปรแกรมทำงานเองทุกครั้งที่เปิดเครื่อง | The NSIS installs the Python backdoor, index.exe, and adds it as a registry run key , enabling persistence [TA0003] |
| 2 | described | T1036 Masquerading | คนร้ายตั้งชื่อไฟล์ให้คล้ายคลึงกับชื่อผู้ผลิตซอฟต์แวร์รายใหญ่และชื่อโปรแกรมรับส่งอีเมลที่ใช้กันทั่วไป โดยสะกดผิดเพียงเล็กน้อยเพื่อให้ผู้ใช้เข้าใจผิดว่าเป็นไฟล์ของระบบ | The APT group has also used variations of Microsoft (e.g., "Microsift") and Outlook in its filenames associated with Small Sieve |
| 3 | described | T1071 Application Layer Protocol, T1027 Obfuscated Files or Information | โปรแกรมดังกล่าวติดต่อกลับไปยังคนร้ายและรับคำสั่งผ่านช่องทางแอปพลิเคชันสนทนายอดนิยมโดยอาศัยโพรโทคอลเว็บที่เข้ารหัสลับ อีกทั้งเนื้อหาที่รับส่งยังถูกแปลงด้วยการสลับตำแหน่งไบต์ร่วมกับการเข้ารหัสข้อความอีกชั้นหนึ่งเพื่อไม่ให้ตรวจจับได้ | Specifically, Small Sieve’s beacons and taskings are performed using Telegram API over Hypertext Transfer Protocol Secure (HTTPS) , and the tasking and beaconing data is obfuscated through a hex byte swapping encoding sc… |

- [ ] ผ่าน / แก้แล้ว

## rcti_007 — Wizard Spider (CTID emulation plan wizard_spider.yaml)

ต้นทาง: <https://www.cynet.com/attack-techniques-hands-on/emotet-vs-trump-deep-dive-analysis-of-a-killer-info-stealer/>

> เมื่อวันที่ 7 มีนาคม 2567 บริษัทโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งว่าเครื่องคอมพิวเตอร์ในแผนกบัญชีทำงานช้าผิดปกติและมีการเชื่อมต่อออกภายนอกโดยไม่ทราบสาเหตุ จากการตรวจสอบทะเบียนระบบของเครื่องพบว่ามีการเพิ่มคีย์ใหม่ที่ตั้งชื่อให้ดูคล้ายรายการของระบบ เพื่อให้โปรแกรมของคนร้ายถูกเรียกทำงานทุกครั้งที่ผู้ใช้ล็อกอินเข้าเครื่อง ต่อมาพบว่าโปรแกรมดังกล่าวเรียกดูข้อมูลพื้นฐานของเครื่อง ทั้งรุ่นและเวอร์ชันของระบบปฏิบัติการ ชื่อเครื่อง และรายละเอียดของฮาร์ดแวร์ จากนั้นยังปรากฏหลักฐานการไล่แจกแจงรายการโปรแกรมที่กำลังทำงานอยู่บนเครื่องในขณะนั้นทั้งหมด

*EN:* On 7 March 2567 a logistics company in Samut Prakan province reported that computers in its accounting department were unusually slow and were making outbound connections for no known reason. Examination of the machine's system registry found a new key added, named to look like a system entry, so that the offender's program would be run every time a user logged in. That program was then found to read basic information about the machine — the model and version of the operating system, the machine name and hardware details. Evidence was also found of it enumerating every program running on the machine at that moment.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1547 Boot or Logon Autostart Execution | มีการเพิ่มคีย์ใหม่ที่ตั้งชื่อให้ดูคล้ายรายการของระบบ เพื่อให้โปรแกรมของคนร้ายถูกเรียกทำงานทุกครั้งที่ผู้ใช้ล็อกอินเข้าเครื่อง | Wizard Spider establishes registry persistence by adding the blbdigital registry key. |
| 2 | described | T1082 System Information Discovery | โปรแกรมดังกล่าวเรียกดูข้อมูลพื้นฐานของเครื่อง ทั้งรุ่นและเวอร์ชันของระบบปฏิบัติการ ชื่อเครื่อง และรายละเอียดของฮาร์ดแวร์ | Wizard Spider performs system information discovery to collect information about the OS. |
| 3 | described | T1057 Process Discovery | ปรากฏหลักฐานการไล่แจกแจงรายการโปรแกรมที่กำลังทำงานอยู่บนเครื่องในขณะนั้นทั้งหมด | Emotet has been observed enumerating local processes. |

- [ ] ผ่าน / แก้แล้ว

## rcti_008 — APT29 (CTID emulation plan APT29.yaml)

ต้นทาง: <https://blog-assets.f-secure.com/wp-content/uploads/2020/03/18122307/F-Secure_Dukes_Whitepaper.pdf>

> เมื่อวันที่ 15 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความว่ามีการเข้าถึงข้อมูลภายในโดยไม่ได้รับอนุญาต จากการตรวจสอบเครื่องแม่ข่ายพบว่าคนร้ายใช้เครื่องมือทำ Credential Dumping โดยแทรกตัวเข้าไปในหน่วยความจำของกระบวนการที่ดูแลการยืนยันตัวตนของระบบปฏิบัติการ แล้วดึงค่าแฮชรหัสผ่านของบัญชีผู้ใช้ออกมา ต่อมาพบว่าคนร้ายแก้ไขไฟล์ทางลัดบนหน้าจอเดสก์ท็อปของผู้ใช้ให้ชี้ไปยังโปรแกรมที่ตนวางไว้แทนโปรแกรมเดิม เพื่อให้โปรแกรมของตนถูกเรียกทำงานเมื่อผู้ใช้กดเปิดใช้งานตามปกติ จากนั้นจากการตรวจสอบ log ของระบบพบว่ามีการรันสคริปต์ที่ขโมยสิทธิ์ประจำตัวจากกระบวนการของผู้ใช้รายอื่นที่เปิดค้างอยู่ แล้วสวมสิทธิ์นั้นเพื่อสั่งงานในนามของผู้ใช้รายดังกล่าว

*EN:* On 15 January 2567 a state enterprise reported unauthorised access to internal data. Examination of the server found that the offender used a tool to perform Credential Dumping, injecting into the memory of the process handling the operating system's authentication and extracting the password hashes of user accounts. The offender was then found to have modified a shortcut file on the user's desktop so that it pointed to a program they had placed rather than the original one, so that their program would run when the user opened it as normal. System logs then showed a script being run that stole the identity token of another user's already-open process and assumed it in order to issue commands in that user's name.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1003 OS Credential Dumping | คนร้ายใช้เครื่องมือทำ Credential Dumping โดยแทรกตัวเข้าไปในหน่วยความจำของกระบวนการที่ดูแลการยืนยันตัวตนของระบบปฏิบัติการ แล้วดึงค่าแฮชรหัสผ่านของบัญชีผู้ใช้ออกมา | Mimikatz lsadump::sam is executed via Invoke-Mimikatz to dump hashes via process injection into LSASS. |
| 2 | described | T1547 Boot or Logon Autostart Execution | คนร้ายแก้ไขไฟล์ทางลัดบนหน้าจอเดสก์ท็อปของผู้ใช้ให้ชี้ไปยังโปรแกรมที่ตนวางไว้แทนโปรแกรมเดิม เพื่อให้โปรแกรมของตนถูกเรียกทำงานเมื่อผู้ใช้กดเปิดใช้งานตามปกติ | Leverage modified Sysinternals |
| 3 | described | T1134 Access Token Manipulation | มีการรันสคริปต์ที่ขโมยสิทธิ์ประจำตัวจากกระบวนการของผู้ใช้รายอื่นที่เปิดค้างอยู่ แล้วสวมสิทธิ์นั้นเพื่อสั่งงานในนามของผู้ใช้รายดังกล่าว | A token theft script was executed to steal and assume the token of another user’s existing process, changing the user context of the process. |

- [ ] ผ่าน / แก้แล้ว

## rcti_009 — Carbanak (CTID emulation plan Carbanak.yaml)

ต้นทาง: <https://www.fireeye.com/content/dam/fireeye-www/summit/cds-2018/presentations/cds18-technical-s04-hello-carbanak.pdf>

> เมื่อวันที่ 11 เมษายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความว่ามีการเข้าถึงเครื่องแม่ข่ายเก็บเอกสารภายในโดยไม่ได้รับอนุญาต จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายอัปโหลดสคริปต์สำหรับข้ามการขออนุญาตยกระดับสิทธิ์ พร้อมกับเครื่องมือทำ Credential Dumping ที่ถูกดัดแปลงแล้ว ขึ้นไปไว้บนเครื่องที่ยึดครองได้ และสั่งให้ทำงานจนได้ค่ารหัสผ่านของผู้ดูแลระบบออกมา ต่อมาปรากฏหลักฐานว่าคนร้ายนำไฟล์เครื่องมือชุดใหม่จากเครื่องภายนอกเข้ามาเก็บไว้ในโฟลเดอร์ที่เตรียมไว้บนเครื่องเดียวกัน จากนั้นได้คัดลอกเครื่องมือชุดดังกล่าวจากเครื่องที่ยึดครองไว้แล้ว ต่อไปยังเครื่องแม่ข่ายเก็บเอกสารอีกเครื่องหนึ่งภายในวงเครือข่ายเดียวกัน สุดท้ายพบว่าคนร้ายเปิดการเชื่อมต่อเข้าไปยังเครื่องแม่ข่ายเก็บเอกสารนั้นผ่านช่องทาง SSH โดยใช้รหัสผ่านที่ได้มาก่อนหน้า

*EN:* On 11 April 2567 a commercial bank reported unauthorised access to an internal document server. Digital forensic examination found that the offender uploaded a script for bypassing the privilege elevation prompt, together with a modified Credential Dumping tool, onto a machine they had taken over, and ran them until the administrator's password values were obtained. Evidence then showed the offender bringing a further set of tool files in from an external machine and storing them in a prepared folder on the same machine. Those tools were then copied from the already-compromised machine onward to another document server inside the same network. Finally the offender was found opening a connection into that document server over SSH using the password obtained earlier.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1003 OS Credential Dumping | คนร้ายอัปโหลดสคริปต์สำหรับข้ามการขออนุญาตยกระดับสิทธิ์ พร้อมกับเครื่องมือทำ Credential Dumping ที่ถูกดัดแปลงแล้ว ขึ้นไปไว้บนเครื่องที่ยึดครองได้ และสั่งให้ทำงานจนได้ค่ารหัสผ่านของผู้ดูแลระบบออกมา | A UAC Bypass script and modified Mimikatz are uploaded to current directory and executed Read the dumped credentials from the previous UAC Bypass and Credential Dumping step |
| 2 | described | T1105 Ingress Tool Transfer | คนร้ายนำไฟล์เครื่องมือชุดใหม่จากเครื่องภายนอกเข้ามาเก็บไว้ในโฟลเดอร์ที่เตรียมไว้บนเครื่องเดียวกัน | Tools required for lateral movement are uploaded and moved to the expected directory. |
| 3 | described | T1570 Lateral Tool Transfer | ได้คัดลอกเครื่องมือชุดดังกล่าวจากเครื่องที่ยึดครองไว้แล้ว ต่อไปยังเครื่องแม่ข่ายเก็บเอกสารอีกเครื่องหนึ่งภายในวงเครือข่ายเดียวกัน | Previously uploaded tools are transferred to bankfileserver using pscp.exe |
| 4 | described | T1021 Remote Services | คนร้ายเปิดการเชื่อมต่อเข้าไปยังเครื่องแม่ข่ายเก็บเอกสารนั้นผ่านช่องทาง SSH โดยใช้รหัสผ่านที่ได้มาก่อนหน้า | Use plink.exe to SSH into bankfileserver |

- [ ] ผ่าน / แก้แล้ว

## rcti_010 — CISA AA20-296A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-296a>

> เมื่อวันที่ 20 ตุลาคม 2563 หน่วยงานปกครองส่วนท้องถิ่นหลายแห่งแจ้งความว่าระบบสารสนเทศของหน่วยงานถูกบุกรุก จากการตรวจสอบ log พบว่าคนร้ายเชื่อมต่อจากหมายเลขไอพีต่างประเทศเข้ามายังเครื่องแม่ข่ายเว็บของหน่วยงาน แล้วโจมตีช่องโหว่ของ Public-Facing Application ที่เปิดให้เข้าถึงจากอินเทอร์เน็ต นอกจากนี้ยังพบว่าเจ้าหน้าที่บางรายเพียงเปิดหน้าเว็บของหน่วยงานที่ถูกดัดแปลงไว้ ก็มีโปรแกรมถูกติดตั้งลงเครื่องทันทีโดยผู้ใช้ไม่ได้สั่งดาวน์โหลดหรือกดยืนยันใด ๆ ต่อมาปรากฏหลักฐานว่าคนร้ายเข้าใช้งานเครือข่ายภายในผ่าน External Remote Services ประเภท SSL VPN เพื่อล็อกอินจากระยะไกลเข้ามาในเครือข่ายของผู้เสียหาย จากนั้นเมื่อได้บัญชีผู้ใช้ที่ถูกต้องมาแล้ว คนร้ายใช้ Valid Accounts ดังกล่าวยืนยันตัวตนเข้าสู่เครื่องแม่ข่ายควบคุมบัญชีผู้ใช้และระบบจดหมายอิเล็กทรอนิกส์แบบคลาวด์ขององค์กรได้สำเร็จ ทั้งนี้ก่อนหน้านั้นยังพบความพยายามทำ Brute Force เดารหัสผ่านซ้ำ ๆ และการส่งคำสั่งฐานข้อมูลแทรกเข้าไปทางหน้าเว็บของหน่วยงานหลายครั้ง

*EN:* On 20 October 2563 several local government bodies reported that their information systems had been breached. Logs showed the offender connecting from foreign IP addresses to the agencies' web servers and attacking a vulnerability in a Public-Facing Application reachable from the internet. It was also found that some officers merely opened a tampered page on the agency's website and a program was installed on their machine at once, without the user requesting any download or confirming anything. Evidence then showed the offender using External Remote Services of the SSL VPN type to log in remotely to the victim's network. Having obtained legitimate user accounts, the offender used those Valid Accounts to authenticate successfully into the account-management server and the organisation's cloud email system. Earlier attempts were also found at Brute Force password guessing and repeated submission of injected database commands through the agency's web pages.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1190 Exploit Public-Facing Application | คนร้ายเชื่อมต่อจากหมายเลขไอพีต่างประเทศเข้ามายังเครื่องแม่ข่ายเว็บของหน่วยงาน แล้วโจมตีช่องโหว่ของ Public-Facing Application ที่เปิดให้เข้าถึงจากอินเทอร์เน็ต | The APT actor is using Turkish IP addresses 213.74.101[.]65, 213.74.139[.]196, and 212.252.30[.]170 to connect to victim web servers (Exploit Public Facing Application ) |
| 2 | described | T1189 Drive-by Compromise | เจ้าหน้าที่บางรายเพียงเปิดหน้าเว็บของหน่วยงานที่ถูกดัดแปลงไว้ ก็มีโปรแกรมถูกติดตั้งลงเครื่องทันทีโดยผู้ใช้ไม่ได้สั่งดาวน์โหลดหรือกดยืนยันใด ๆ | registered and are likely SLTT government targets (Drive-By Compromise ) |
| 3 | named | T1133 External Remote Services | คนร้ายเข้าใช้งานเครือข่ายภายในผ่าน External Remote Services ประเภท SSL VPN เพื่อล็อกอินจากระยะไกลเข้ามาในเครือข่ายของผู้เสียหาย | The APT actor has been observed using Cisco AnyConnect Secure Socket Layer (SSL) virtual private network (VPN) connections to enable remote logins on at least one victim network, possibly enabled by an Exim Simple Mail T… |
| 4 | named | T1078 Valid Accounts | คนร้ายใช้ Valid Accounts ดังกล่าวยืนยันตัวตนเข้าสู่เครื่องแม่ข่ายควบคุมบัญชีผู้ใช้และระบบจดหมายอิเล็กทรอนิกส์แบบคลาวด์ขององค์กรได้สำเร็จ | More recently, the APT actor enumerated and exploited a Fortinet VPN vulnerability (CVE-2018-13379) for Initial Access [TA0001] and a Windows Netlogon vulnerability (CVE-2020-1472) to obtain access to Windows Active Dire… |
| 5 | named | T1110 Brute Force, T1190 Exploit Public-Facing Application | พบความพยายามทำ Brute Force เดารหัสผ่านซ้ำ ๆ และการส่งคำสั่งฐานข้อมูลแทรกเข้าไปทางหน้าเว็บของหน่วยงานหลายครั้ง | The actor is using 213.74.101[.]65 and 213.74.139[.]196 to attempt brute force logins and, in several instances, attempted Structured Query Language (SQL) injections on victim websites (Brute Force ; Exploit Public Facin… |

- [ ] ผ่าน / แก้แล้ว

## rcti_011 — FIN7 (CTID emulation plan Fin7.yaml)

ต้นทาง: <https://www.fireeye.com/blog/threat-research/2017/05/fin7-shim-databases-persistence.html>

> เมื่อวันที่ 5 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งในจังหวัดชลบุรีแจ้งความว่าข้อมูลบัตรเครดิตของลูกค้าที่ชำระเงินผ่านเครื่องรับชำระเงินหน้าร้านรั่วไหล จากการตรวจสอบเครื่องรับชำระเงินพบว่ามีการรันคำสั่งบรรทัดเดียวผ่านหน้าต่างคำสั่งของระบบ โดยเนื้อหาคำสั่งถูกเข้ารหัสและย่อให้อ่านไม่ออกเพื่อไม่ให้เจ้าหน้าที่ตรวจพบว่าคำสั่งนั้นทำอะไร ผลของคำสั่งดังกล่าวคือการติดตั้งกลไก Application Shimming ไว้ในระบบ ซึ่งทำให้โปรแกรมของคนร้ายถูกเรียกทำงานอีกครั้งหลังจากเครื่องถูกรีสตาร์ต ต่อมาพบว่าคนร้ายอัปโหลดโปรแกรมที่ตั้งชื่อให้ดูเหมือนเครื่องมือตรวจสอบข้อผิดพลาดของระบบขึ้นไปบนเครื่อง แล้วสั่งให้โปรแกรมนั้นไล่ตรวจสอบรายการโปรแกรมที่กำลังทำงานอยู่ เพื่อค้นหากระบวนการของซอฟต์แวร์รับชำระเงินและดึงข้อมูลบัตรออกจากหน่วยความจำ สุดท้ายพบว่าข้อมูลบัตรที่รวบรวมได้ถูกบีบอัดรวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดไฟล์ทั่วไปก่อนนำออกจากเครื่อง

*EN:* On 5 June 2567 a department store in Chonburi province reported a leak of credit card data belonging to customers who paid at its point-of-sale terminals. Examination of the terminals found a single-line command run through the system's command window, whose contents were encoded and shortened to be unreadable so that staff could not see what the command did. The effect of that command was to install an Application Shimming mechanism in the system, causing the offender's program to be run again after the machine was restarted. The offender was then found to have uploaded a program named to look like a system error-checking tool and to have had it enumerate the running programs in order to locate the payment software's process and pull card data out of memory. Finally the collected card data was found compressed into a single file with an ordinary file compression program before being taken off the machine.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1027 Obfuscated Files or Information | มีการรันคำสั่งบรรทัดเดียวผ่านหน้าต่างคำสั่งของระบบ โดยเนื้อหาคำสั่งถูกเข้ารหัสและย่อให้อ่านไม่ออกเพื่อไม่ให้เจ้าหน้าที่ตรวจพบว่าคำสั่งนั้นทำอะไร | Execute PowerShell oneliner to install application shim. |
| 2 | named | T1546 Event Triggered Execution | การติดตั้งกลไก Application Shimming ไว้ในระบบ ซึ่งทำให้โปรแกรมของคนร้ายถูกเรียกทำงานอีกครั้งหลังจากเครื่องถูกรีสตาร์ต | Reboot the host to start shim persistence. |
| 3 | described | T1057 Process Discovery | สั่งให้โปรแกรมนั้นไล่ตรวจสอบรายการโปรแกรมที่กำลังทำงานอยู่ เพื่อค้นหากระบวนการของซอฟต์แวร์รับชำระเงินและดึงข้อมูลบัตรออกจากหน่วยความจำ | Upload and execute the PillowMint credit card scraper as debug.exe |
| 4 | described | T1560 Archive Collected Data | ข้อมูลบัตรที่รวบรวมได้ถูกบีบอัดรวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดไฟล์ทั่วไปก่อนนำออกจากเครื่อง | Compress credit card data into an archive using 7za.exe |

- [ ] ผ่าน / แก้แล้ว

## rcti_012 — menuPass (CTID emulation plan menupass.yaml)

ต้นทาง: <https://pwc.co.uk/cyber-secrity/pdf/cloud-hopper-report-final-v4.pdf>

> เมื่อวันที่ 28 สิงหาคม 2566 บริษัทที่ปรึกษาด้านวิศวกรรมแห่งหนึ่งแจ้งความว่าเอกสารโครงการของลูกค้าถูกนำออกไปจากระบบ จากการตรวจสอบพบว่ามีการอัปโหลดไฟล์เอกสารจำนวนมากขึ้นไปเก็บไว้ยังบัญชีบริการรับฝากข้อมูลออนไลน์ที่ไม่ใช่ของบริษัท จากการตรวจสอบย้อนกลับพบว่าก่อนหน้านั้นคนร้ายอาศัยกลไกบริหารจัดการเครื่องระยะไกลที่ติดมากับระบบปฏิบัติการวินโดวส์ สั่งให้สคริปต์ของตนทำงานบนเครื่องปลายทางโดยไม่ต้องติดตั้งโปรแกรมเพิ่ม นอกจากนี้ยังปรากฏหลักฐานว่าคนร้ายตั้งงานที่กำหนดเวลาไว้ในระบบ เพื่อให้โปรแกรมของตนถูกเรียกทำงานซ้ำตามช่วงเวลาที่กำหนด แม้ผู้ดูแลระบบจะปิดโปรแกรมไปแล้วก็ตาม

*EN:* On 28 August 2566 an engineering consultancy reported that client project documents had been taken out of its systems. Examination found a large number of document files uploaded to an online storage account that did not belong to the company. Tracing backwards, the offender was found to have used the remote machine management mechanism built into the Windows operating system to run their own script on the target machine without installing additional software. Evidence was also found that the offender created a timed job in the system so that their program would be run repeatedly at set intervals even after an administrator shut it down.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1537 Transfer Data to Cloud Account | มีการอัปโหลดไฟล์เอกสารจำนวนมากขึ้นไปเก็บไว้ยังบัญชีบริการรับฝากข้อมูลออนไลน์ที่ไม่ใช่ของบริษัท | Exfil data to cloud account |
| 2 | described | T1047 Windows Management Instrumentation | คนร้ายอาศัยกลไกบริหารจัดการเครื่องระยะไกลที่ติดมากับระบบปฏิบัติการวินโดวส์ สั่งให้สคริปต์ของตนทำงานบนเครื่องปลายทางโดยไม่ต้องติดตั้งโปรแกรมเพิ่ม | Using wmiexec.vbs to execute tactical malware |
| 3 | described | T1053 Scheduled Task/Job | คนร้ายตั้งงานที่กำหนดเวลาไว้ในระบบ เพื่อให้โปรแกรมของตนถูกเรียกทำงานซ้ำตามช่วงเวลาที่กำหนด | menuPass is reported to have used scheduled tasks to persist |

- [ ] ผ่าน / แก้แล้ว

## rcti_013 — Sandworm Team (G0034) (CTID emulation plan sandworm.yaml)

ต้นทาง: <https://blog.talosintelligence.com/2017/06/worldwide-ransomware-variant.html>

> เมื่อวันที่ 14 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งว่าเครื่องคอมพิวเตอร์ในห้องควบคุมถูกติดตั้งโปรแกรมแปลกปลอม จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายใช้บัญชีผู้ใช้ที่ได้มาก่อนหน้า ผลักไฟล์โปรแกรมของตนเข้าไปยังเครื่องปลายทางผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบบที่เปิดใช้งานอยู่ในเครือข่ายภายใน ต่อมาปรากฏหลักฐานว่าคนร้ายสร้างบริการของระบบขึ้นใหม่บนเครื่องปลายทางแล้วสั่งให้บริการนั้นเริ่มทำงาน เพื่อเรียกใช้ไฟล์โปรแกรมที่ผลักเข้ามาก่อนหน้าโดยได้สิทธิ์ระดับระบบ จากนั้นคนร้ายได้เพิ่มรายการเรียกใช้งานโปรแกรมของตนไว้ใน Registry Run Key ของบัญชีผู้ใช้เป้าหมาย แล้วเข้าใช้งานเครื่องดังกล่าวผ่านช่องทางเดสก์ท็อประยะไกลเพื่อกระตุ้นให้รายการนั้นทำงาน

*EN:* On 14 July 2567 a provincial electricity authority branch reported that computers in its control room had been implanted with a foreign program. Digital forensic examination found that the offender used a previously obtained user account to push their own program files onto the target machine through an administrative file sharing channel enabled on the internal network. Evidence then showed the offender creating a new system service on the target machine and starting it in order to run the program files pushed in earlier with system-level privileges. The offender then added an entry calling their program into the target user account's Registry Run Key and connected to that machine over remote desktop to trigger the entry.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1021 Remote Services | คนร้ายใช้บัญชีผู้ใช้ที่ได้มาก่อนหน้า ผลักไฟล์โปรแกรมของตนเข้าไปยังเครื่องปลายทางผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบบที่เปิดใช้งานอยู่ในเครือข่ายภายใน | Sandworm Team has pushed additional malicious tools onto an infected system to steal user credentials, move laterally, and destroy data. Sandworm Team has used previously acquired legitimate credentials prior to attacks.… |
| 2 | described | T1569 System Services | คนร้ายสร้างบริการของระบบขึ้นใหม่บนเครื่องปลายทางแล้วสั่งให้บริการนั้นเริ่มทำงาน เพื่อเรียกใช้ไฟล์โปรแกรมที่ผลักเข้ามาก่อนหน้าโดยได้สิทธิ์ระดับระบบ | Uses psexec.py to gain a bind-shell to target over SMB (TCP 445). Loads the registry hive for target user. Set registry persistence for target user only, which will execute the previously uploaded agent executable. This … |
| 3 | named | T1547 Boot or Logon Autostart Execution | คนร้ายได้เพิ่มรายการเรียกใช้งานโปรแกรมของตนไว้ใน Registry Run Key ของบัญชีผู้ใช้เป้าหมาย | RDP into target host to trigger the registry persistence which will execute the uploaded agent implant. This ability must be run by an agent running on the attacker-controlled machine (e.g. on the C2 server itself). Wait… |

- [ ] ผ่าน / แก้แล้ว

## rcti_014 — CISA AA22-249A-0 (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-249a-0>

> เมื่อวันที่ 8 กันยายน 2565 โรงเรียนมัธยมแห่งหนึ่งในจังหวัดสงขลาแจ้งความว่าระบบทะเบียนนักเรียนถูกเข้ารหัสลับและมีข้อความเรียกค่าไถ่ปรากฏบนหน้าจอ จากการตรวจสอบพบว่าคนร้ายเข้าสู่ระบบครั้งแรกโดยใช้ชื่อผู้ใช้และรหัสผ่านของเจ้าหน้าที่ที่หลุดออกไปก่อนหน้า ผ่านแอปพลิเคชันของโรงเรียนที่เปิดให้เข้าถึงได้จากอินเทอร์เน็ต ต่อมาปรากฏหลักฐานว่าคนร้ายอาศัยเครื่องมือที่ติดมากับระบบปฏิบัติการอยู่แล้วในการทำงาน โดยเรียกใช้บริการ Windows Management Instrumentation ของวินโดวส์ และแทรกไฟล์อันตรายลงในโฟลเดอร์ที่ใช้แบ่งปันร่วมกันภายในองค์กร จากนั้นพบว่าคนร้ายยิงคำสั่งโจมตีช่องโหว่ของบริการจัดการเครื่องพิมพ์บนเครื่องแม่ข่าย เพื่อยกระดับสิทธิ์ของตนจากผู้ใช้ทั่วไปขึ้นเป็นผู้ดูแลระบบ

*EN:* On 8 September 2565 a secondary school in Songkhla province reported that its student registration system had been encrypted and a ransom message appeared on screen. Examination found that the offender first entered the system using a staff member's previously leaked username and password, through a school application reachable from the internet. Evidence then showed the offender working with tools already shipped with the operating system, invoking the Windows Management Instrumentation service and planting malicious files into folders shared within the organisation. The offender was then found firing attack commands at a vulnerability in the print management service on the server in order to raise their privileges from ordinary user to administrator.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1190 Exploit Public-Facing Application | คนร้ายเข้าสู่ระบบครั้งแรกโดยใช้ชื่อผู้ใช้และรหัสผ่านของเจ้าหน้าที่ที่หลุดออกไปก่อนหน้า ผ่านแอปพลิเคชันของโรงเรียนที่เปิดให้เข้าถึงได้จากอินเทอร์เน็ต | Vice Society actors likely obtain initial network access through compromised credentials by exploiting internet-facing applications |
| 2 | named | T1047 Windows Management Instrumentation, T1080 Taint Shared Content | คนร้ายอาศัยเครื่องมือที่ติดมากับระบบปฏิบัติการอยู่แล้วในการทำงาน โดยเรียกใช้บริการ Windows Management Instrumentation ของวินโดวส์ และแทรกไฟล์อันตรายลงในโฟลเดอร์ที่ใช้แบ่งปันร่วมกันภายในองค์กร | They have also used “living off the land” techniques targeting the legitimate Windows Management Instrumentation (WMI) service and tainting shared content |
| 3 | described | T1068 Exploitation for Privilege Escalation | คนร้ายยิงคำสั่งโจมตีช่องโหว่ของบริการจัดการเครื่องพิมพ์บนเครื่องแม่ข่าย เพื่อยกระดับสิทธิ์ของตนจากผู้ใช้ทั่วไปขึ้นเป็นผู้ดูแลระบบ | Vice Society actors have been observed exploiting the PrintNightmare vulnerability (CVE-2021-1675 and CVE-2021-34527 ) to escalate privileges |

- [ ] ผ่าน / แก้แล้ว

## rcti_015 — Turla - Carbon (CTID emulation plan turla_carbon.yaml)

> เมื่อวันที่ 3 ธันวาคม 2566 สำนักงานกฎหมายแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่ามีผู้ลักลอบเข้าถึงเครื่องคอมพิวเตอร์ของทนายความในสำนักงาน จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าโปรแกรมฝังตัวที่อยู่บนเครื่องได้รับคำสั่งจากภายนอกให้ลบไฟล์โปรแกรมดักบันทึกแป้นพิมพ์และไฟล์บันทึกผลที่เก็บไว้ออกจากเครื่อง เพื่อไม่ให้เหลือร่องรอยไว้ให้ตรวจสอบ ต่อมาปรากฏว่าโปรแกรมฝังตัวเดียวกันได้รับคำสั่งให้ดาวน์โหลดไฟล์โปรแกรมชุดใหม่จากเครื่องสั่งการภายนอกเข้ามาเก็บไว้บนเครื่องของทนายความ โดยตั้งชื่อไฟล์ให้ดูเหมือนไฟล์ชั่วคราวของระบบ สุดท้ายพบว่าคนร้ายสั่งให้คัดลอกไฟล์โปรแกรมดังกล่าวต่อไปยังเครื่องแม่ข่ายเว็บของสำนักงาน โดยเชื่อมต่อผ่านช่องทาง SSH ด้วยรหัสผ่านของผู้ใช้รายที่สาม

*EN:* On 3 December 2566 a law firm in Bangkok reported that someone had gained access to the computer of one of its lawyers. Digital forensic examination found that an implanted program on the machine received a command from outside to delete the keystroke-logging program file and the stored output file from the machine so that no traces would remain for examination. The same implanted program was then found to have received a command to download a new set of program files from an external command machine onto the lawyer's computer, named to look like temporary system files. Finally the offender was found ordering those program files copied onward to the firm's web server, connecting over SSH with the password of a third user.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1070 Indicator Removal | โปรแกรมฝังตัวที่อยู่บนเครื่องได้รับคำสั่งจากภายนอกให้ลบไฟล์โปรแกรมดักบันทึกแป้นพิมพ์และไฟล์บันทึกผลที่เก็บไว้ออกจากเครื่อง เพื่อไม่ให้เหลือร่องรอยไว้ให้ตรวจสอบ | Task the CARBON-DLL implant to remove the keylogger and keylogger output file. |
| 2 | described | T1105 Ingress Tool Transfer | โปรแกรมฝังตัวเดียวกันได้รับคำสั่งให้ดาวน์โหลดไฟล์โปรแกรมชุดใหม่จากเครื่องสั่งการภายนอกเข้ามาเก็บไว้บนเครื่องของทนายความ | Task the CARBON-DLL implant on Adawolfa's workstation to download Penquin (named tmp504e.tmp). Task the implant to download pscp.exe |
| 3 | described | T1021 Remote Services | คนร้ายสั่งให้คัดลอกไฟล์โปรแกรมดังกล่าวต่อไปยังเครื่องแม่ข่ายเว็บของสำนักงาน โดยเชื่อมต่อผ่านช่องทาง SSH ด้วยรหัสผ่านของผู้ใช้รายที่สาม | Task the implant to copy Penquin to the Apache web server using the third target user's credentials. |

- [ ] ผ่าน / แก้แล้ว

## rcti_016 — Carbanak (CTID emulation plan Carbanak.yaml)

ต้นทาง: <https://www.fireeye.com/blog/threat-research/2017/04/fin7-phishing-lnk.html>

> เมื่อวันที่ 19 พฤษภาคม 2567 บริษัทหลักทรัพย์แห่งหนึ่งแจ้งความว่าหน้าจอการทำงานของเจ้าหน้าที่ฝ่ายซื้อขายถูกลักลอบบันทึกไว้ จากการตรวจสอบพบว่าคนร้ายดาวน์โหลดสคริปต์เข้ามาไว้บนเครื่องเป้าหมายและสั่งให้ทำงาน โดยสคริปต์ดังกล่าวทำหน้าที่ถ่ายภาพสิ่งที่ปรากฏบนจอของผู้ใช้เป็นระยะแล้วส่งออกไปภายนอก ต่อมาจากการตรวจสอบทะเบียนระบบของเครื่องพบว่ามีการเขียนชุดข้อมูลคำสั่งขนาดยาวของโปรแกรมควบคุมระยะไกลขั้นที่สองลงไปเก็บไว้ในค่าของทะเบียนระบบแทนการเก็บเป็นไฟล์บนดิสก์ เพื่อหลีกเลี่ยงการตรวจจับจากโปรแกรมป้องกันไวรัส สุดท้ายพบว่ามีสคริปต์อีกตัวหนึ่งทำหน้าที่อ่านชุดข้อมูลที่ซ่อนไว้นั้นกลับออกมา แปลงกลับให้อยู่ในรูปที่ประมวลผลได้ แล้วสั่งให้โปรแกรมควบคุมระยะไกลขั้นที่สองทำงานในหน่วยความจำ

*EN:* On 19 May 2567 a securities company reported that the working screens of its trading staff had been covertly recorded. Examination found that the offender downloaded a script onto the target machine and ran it, the script capturing images of what appeared on the user's display at intervals and sending them out. Examination of the machine's system registry then found a long instruction blob for a second-stage remote control program written into a registry value instead of being stored as a file on disk, in order to evade detection by antivirus software. Finally another script was found reading that hidden blob back out, converting it into a processable form and running the second-stage remote control program in memory.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1113 Screen Capture | สคริปต์ดังกล่าวทำหน้าที่ถ่ายภาพสิ่งที่ปรากฏบนจอของผู้ใช้เป็นระยะแล้วส่งออกไปภายนอก | Download screen capture PowerShell script to target and execute |
| 2 | described | T1112 Modify Registry | มีการเขียนชุดข้อมูลคำสั่งขนาดยาวของโปรแกรมควบคุมระยะไกลขั้นที่สองลงไปเก็บไว้ในค่าของทะเบียนระบบแทนการเก็บเป็นไฟล์บนดิสก์ เพื่อหลีกเลี่ยงการตรวจจับจากโปรแกรมป้องกันไวรัส | The shellcode for the 2nd stage RAT, which is a reverse Meterpreter shell, is written to the Registry |
| 3 | described | T1140 Deobfuscate/Decode Files or Information | มีสคริปต์อีกตัวหนึ่งทำหน้าที่อ่านชุดข้อมูลที่ซ่อนไว้นั้นกลับออกมา แปลงกลับให้อยู่ในรูปที่ประมวลผลได้ แล้วสั่งให้โปรแกรมควบคุมระยะไกลขั้นที่สองทำงานในหน่วยความจำ | A PowerShell script is used to execute the staged 2nd stage RAT, which is a reverse Meterpreter shell |

- [ ] ผ่าน / แก้แล้ว

## rcti_017 — CISA AA22-294A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-294a>

> เมื่อวันที่ 26 ตุลาคม 2565 คลินิกเวชกรรมเครือข่ายแห่งหนึ่งแจ้งความว่าข้อมูลคนไข้ในระบบถูกเข้าถึงโดยบุคคลภายนอก จากการตรวจสอบพบว่าอุปกรณ์เชื่อมต่อเครือข่ายส่วนตัวเสมือนของคลินิกยังไม่ได้ติดตั้งชุดแก้ไขช่องโหว่ที่ผู้ผลิตประกาศไว้ และคนร้ายได้ยิงคำสั่งโจมตีช่องโหว่ดังกล่าวจนเข้าถึงอุปกรณ์ได้สำเร็จ นอกจากนี้ยังพบอีกกรณีหนึ่งที่คนร้ายนำชื่อผู้ใช้และรหัสผ่านที่รั่วไหลออกไปก่อนหน้ามาล็อกอินเข้าอุปกรณ์เชื่อมต่อระยะไกลรุ่นเก่าที่ยังไม่ได้เปิดใช้การยืนยันตัวตนหลายขั้นตอน ต่อมาเมื่อเข้ามาอยู่ในวงเครือข่ายภายในได้แล้ว ปรากฏหลักฐานว่าคนร้ายเปิดการเชื่อมต่อต่อเนื่องไปยังเครื่องอื่น ๆ ในวงเดียวกันผ่านช่องทาง SSH และเดสก์ท็อประยะไกล เพื่อขยายการเข้าถึงไปทีละเครื่อง

*EN:* On 26 October 2565 a network of medical clinics reported that patient data in its systems had been accessed by outsiders. Examination found that the clinic's virtual private network appliance had not had the vendor-announced vulnerability patch installed, and the offender fired attack commands at that vulnerability until they reached the appliance. A second case was also found in which the offender used a previously leaked username and password to log in to an older remote connection appliance on which multi-factor authentication had not been enabled. Once inside the internal network, evidence showed the offender opening onward connections to other machines in the same segment over SSH and remote desktop, widening their access machine by machine.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1190 Exploit Public-Facing Application | อุปกรณ์เชื่อมต่อเครือข่ายส่วนตัวเสมือนของคลินิกยังไม่ได้ติดตั้งชุดแก้ไขช่องโหว่ที่ผู้ผลิตประกาศไว้ และคนร้ายได้ยิงคำสั่งโจมตีช่องโหว่ดังกล่าวจนเข้าถึงอุปกรณ์ได้สำเร็จ | In one confirmed compromise, the actors likely exploited an unpatched vulnerability in the organization’s VPN server |
| 2 | described | T1078 Valid Accounts | คนร้ายนำชื่อผู้ใช้และรหัสผ่านที่รั่วไหลออกไปก่อนหน้ามาล็อกอินเข้าอุปกรณ์เชื่อมต่อระยะไกลรุ่นเก่าที่ยังไม่ได้เปิดใช้การยืนยันตัวตนหลายขั้นตอน | In another confirmed compromise, the actors used previously compromised credentials to access a legacy VPN server that did not have multifactor authentication (MFA) enabled |
| 3 | described | T1563 Remote Service Session Hijacking | คนร้ายเปิดการเชื่อมต่อต่อเนื่องไปยังเครื่องอื่น ๆ ในวงเดียวกันผ่านช่องทาง SSH และเดสก์ท็อประยะไกล เพื่อขยายการเข้าถึงไปทีละเครื่อง | After obtaining access to the victim’s VPN server, Daixin actors move laterally via Secure Shell (SSH) and Remote Desktop Protocol (RDP) |

- [ ] ผ่าน / แก้แล้ว

## rcti_018 — Wizard Spider (CTID emulation plan wizard_spider.yaml)

ต้นทาง: <https://thedfirreport.com/2020/10/08/ryuks-return/>

> เมื่อวันที่ 2 กันยายน 2567 บริษัทประกันภัยแห่งหนึ่งแจ้งความว่าบัญชีผู้ดูแลระบบของบริษัทถูกนำไปใช้โดยไม่ได้รับอนุญาต จากการตรวจสอบ log ของเครื่องแม่ข่ายควบคุมบัญชีผู้ใช้พบว่า คนร้ายใช้เครื่องมือสาธารณะร้องขอตั๋วยืนยันสิทธิ์ของบัญชีบริการจำนวนมากจากระบบยืนยันตัวตนขององค์กร แล้วนำตั๋วที่ได้ไปถอดรหัสนอกระบบเพื่อให้ได้รหัสผ่านของบัญชีเหล่านั้น ต่อมาปรากฏหลักฐานว่าคนร้ายเปิดการเชื่อมต่อหน้าจอระยะไกลเข้ามายังเครื่องเป้าหมายเครื่องที่สองภายในองค์กร แล้วปิดการเชื่อมต่อนั้นลงเมื่อดำเนินการเสร็จ นอกจากนี้ยังพบว่าคนร้ายเตรียมโฟลเดอร์บนเครื่องต้นทางของตนซึ่งบรรจุไฟล์สคริปต์และไฟล์โปรแกรมเรียกค่าไถ่ไว้ แล้วอาศัยการแบ่งปันไดรฟ์ผ่านการเชื่อมต่อหน้าจอระยะไกลนั้นส่งไฟล์เข้ามายังเครื่องของผู้เสียหาย

*EN:* On 2 September 2567 an insurance company reported that its administrator account had been used without authorisation. Logs on the account-management server showed the offender using a public tool to request authentication tickets for a large number of service accounts from the organisation's authentication system, then cracking the obtained tickets offline to recover those accounts' passwords. Evidence then showed the offender opening a remote screen connection to a second target machine inside the organisation and closing it when finished. The offender was also found preparing a folder on their own machine containing script files and a ransom program file, and using drive sharing over that remote screen connection to send the files into the victim's machine.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1558 Steal or Forge Kerberos Tickets | คนร้ายใช้เครื่องมือสาธารณะร้องขอตั๋วยืนยันสิทธิ์ของบัญชีบริการจำนวนมากจากระบบยืนยันตัวตนขององค์กร แล้วนำตั๋วที่ได้ไปถอดรหัสนอกระบบเพื่อให้ได้รหัสผ่านของบัญชีเหล่านั้น | Wizard Spider performs Kerberoasting using a public tool, Rubeus. Through Kerberoasting, Wizard Spider obtains encrypted credentials. |
| 2 | described | T1021 Remote Services | คนร้ายเปิดการเชื่อมต่อหน้าจอระยะไกลเข้ามายังเครื่องเป้าหมายเครื่องที่สองภายในองค์กร แล้วปิดการเชื่อมต่อนั้นลงเมื่อดำเนินการเสร็จ | End the RDP session to the second target. This ability must be run by an agent running on the attacker-controlled machine (e.g. on the C2 server itself), since the RDP connection originates from the attacker's machine. |
| 3 | described | T1105 Ingress Tool Transfer | คนร้ายเตรียมโฟลเดอร์บนเครื่องต้นทางของตนซึ่งบรรจุไฟล์สคริปต์และไฟล์โปรแกรมเรียกค่าไถ่ไว้ แล้วอาศัยการแบ่งปันไดรฟ์ผ่านการเชื่อมต่อหน้าจอระยะไกลนั้นส่งไฟล์เข้ามายังเครื่องของผู้เสียหาย | Prepares the local folder with kill.bat, window.bat, and ryuk.exe to use as the RDP shared-drive. This ability must be run by an agent running on the attacker-controlled Linux machine (e.g. on the C2 server itself), sinc… |

- [ ] ผ่าน / แก้แล้ว

## rcti_019 — CISA AA22-138B (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-138b>

> เมื่อวันที่ 14 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดการอุปกรณ์ปลายทางขององค์กรถูกบุกรุก จากการตรวจสอบ log ของเว็บเซิร์ฟเวอร์พบว่าคนร้ายส่งคำขอเข้ามายังเครื่องแม่ข่ายเป็นจำนวนมากติดต่อกันสองวัน เพื่อโจมตีช่องโหว่ที่ทำให้สั่งรันคำสั่งจากระยะไกลได้ แล้วอัปโหลดไฟล์โปรแกรมและไฟล์สคริปต์สำหรับสั่งการผ่านหน้าเว็บขึ้นไปฝังไว้บนเครื่อง เพื่อให้กลับเข้ามาใช้งานได้อีกในภายหลัง ต่อมาปรากฏหลักฐานว่าสคริปต์ดังกล่าวได้แก้ไขไฟล์บันทึกเหตุการณ์ของระบบให้กลับไปมีเนื้อหาเหมือนก่อนถูกบุกรุก และลบไฟล์ที่ตนสร้างขึ้นทิ้ง เพื่อกลบร่องรอยการเข้าถึง สุดท้ายจากการตรวจสอบพบว่าสคริปต์เดียวกันได้รวบรวมไฟล์สำคัญของระบบ ทั้งรายชื่อผู้ใช้ รหัสผ่าน กุญแจหลัก และกฎของไฟร์วอลล์ แล้วนำมารวมบีบอัดไว้เป็นไฟล์เดียวเพื่อเตรียมนำออก

*EN:* On 14 April 2565 an agency reported that its endpoint management server had been breached. Web server logs showed the offender sending a large number of requests to the server over two consecutive days in order to attack a vulnerability allowing remote command execution, then uploading program files and a web-based command script onto the machine so they could return to it later. Evidence then showed that script restoring the system event log files to their pre-breach contents and deleting the files it had created, in order to cover the traces of access. Finally the same script was found gathering important system files — usernames, passwords, master keys and firewall rules — and compressing them together into a single file ready to be taken out.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1505 Server Software Component | คนร้ายส่งคำขอเข้ามายังเครื่องแม่ข่ายเป็นจำนวนมากติดต่อกันสองวัน เพื่อโจมตีช่องโหว่ที่ทำให้สั่งรันคำสั่งจากระยะไกลได้ แล้วอัปโหลดไฟล์โปรแกรมและไฟล์สคริปต์สำหรับสั่งการผ่านหน้าเว็บขึ้นไปฝังไว้บนเครื่อง เพื่อให้กลับเข้ามาใช้งานได้อีกในภายหลัง | On April 13 and 14, TA2 sent many GET requests to the server exploiting—or attempting to exploit—CVE 2022-22954 to obtain RCE, upload binaries, and upload webshells for persistence [TA0003] |
| 2 | described | T1070 Indicator Removal | สคริปต์ดังกล่าวได้แก้ไขไฟล์บันทึกเหตุการณ์ของระบบให้กลับไปมีเนื้อหาเหมือนก่อนถูกบุกรุก และลบไฟล์ที่ตนสร้างขึ้นทิ้ง เพื่อกลบร่องรอยการเข้าถึง | The malicious script then deleted evidence of compromise [TA0005] by modifying logs to their original state and deleting files |
| 3 | described | T1560 Archive Collected Data | สคริปต์เดียวกันได้รวบรวมไฟล์สำคัญของระบบ ทั้งรายชื่อผู้ใช้ รหัสผ่าน กุญแจหลัก และกฎของไฟร์วอลล์ แล้วนำมารวมบีบอัดไว้เป็นไฟล์เดียวเพื่อเตรียมนำออก | The malicious script collected [TA0009] sensitive files–including user names, passwords, master keys, and firewall rules–and stored them in a “tar ball” (a “tar ball” is a compressed and zipped file used by threat actors… |

- [ ] ผ่าน / แก้แล้ว

## rcti_020 — Wizard Spider (CTID emulation plan wizard_spider.yaml)

ต้นทาง: <https://www.cybereason.com/blog/dropping-anchor-from-a-trickbot-infection-to-the-discovery-of-the-anchor-malware>

> เมื่อวันที่ 21 ตุลาคม 2567 บริษัทผู้ผลิตชิ้นส่วนยานยนต์แห่งหนึ่งในจังหวัดปทุมธานีแจ้งว่าเครื่องคอมพิวเตอร์ในสำนักงานติดโปรแกรมไม่พึงประสงค์เป็นวงกว้าง จากการตรวจสอบพฤติกรรมของโปรแกรมดังกล่าวพบว่า โปรแกรมได้เรียกดูรายการการเชื่อมต่อเครือข่ายที่เปิดค้างอยู่บนเครื่องของผู้เสียหาย ทั้งหมายเลขปลายทางและพอร์ตที่ใช้ติดต่อ จากนั้นโปรแกรมยังเก็บรวบรวมข้อมูลประจำเครื่อง ได้แก่ ชื่อเครื่อง รุ่นระบบปฏิบัติการ และรายละเอียดการตั้งค่าของเครื่องลูกข่าย ต่อมาปรากฏหลักฐานว่าโปรแกรมสอบถามความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนขององค์กรกับโดเมนอื่นที่เชื่อมโยงกันอยู่ และสุดท้ายได้ตรวจสอบว่าบัญชีผู้ใช้บนเครื่องที่ยึดครองไว้เป็นสมาชิกของกลุ่มสิทธิ์ใดบ้างในระบบ

*EN:* On 21 October 2567 an automotive parts manufacturer in Pathum Thani province reported that office computers had been widely infected with an unwanted program. Examination of that program's behaviour found that it read the list of network connections open on the victim's machine, including destination addresses and the ports in use. The program also gathered machine-specific information — machine name, operating system version and client configuration details. Evidence then showed the program querying the trust relationships between the organisation's domain and other linked domains, and finally checking which permission groups the user account on the compromised machine belonged to.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1049 System Network Connections Discovery | โปรแกรมได้เรียกดูรายการการเชื่อมต่อเครือข่ายที่เปิดค้างอยู่บนเครื่องของผู้เสียหาย ทั้งหมายเลขปลายทางและพอร์ตที่ใช้ติดต่อ | Wizard Spider uses TrickBot to obtain the network connection information from the victim’s machine. |
| 2 | described | T1082 System Information Discovery | โปรแกรมยังเก็บรวบรวมข้อมูลประจำเครื่อง ได้แก่ ชื่อเครื่อง รุ่นระบบปฏิบัติการ และรายละเอียดการตั้งค่าของเครื่องลูกข่าย | Wizard Spider uses TrickBot to gather client specfic information |
| 3 | described | T1482 Domain Trust Discovery | โปรแกรมสอบถามความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนขององค์กรกับโดเมนอื่นที่เชื่อมโยงกันอยู่ | Wizard Spider uses TrickBot to gather domain specfic information |
| 4 | described | T1069 Permission Groups Discovery | ได้ตรวจสอบว่าบัญชีผู้ใช้บนเครื่องที่ยึดครองไว้เป็นสมาชิกของกลุ่มสิทธิ์ใดบ้างในระบบ | Wizard Spider uses TrickBot to identify the groups the user on a compromised host belongs to. |

- [ ] ผ่าน / แก้แล้ว

## rcti_021 — CISA AA21-048A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-048a>

> เมื่อวันที่ 17 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งซึ่งประกอบธุรกิจซื้อขายสินทรัพย์ดิจิทัลแจ้งความว่าถูกหลอกให้ติดตั้งโปรแกรมซื้อขายปลอมบนเครื่องคอมพิวเตอร์ระบบปฏิบัติการแมค จากการตรวจสอบตัวติดตั้งโปรแกรมพบว่ามีชุดคำสั่งที่ถูกกำหนดให้ทำงานต่อทันทีหลังการติดตั้งเสร็จสิ้น ซึ่งทำงานผ่านตัวแปลคำสั่งของระบบ ชุดคำสั่งดังกล่าวได้ย้ายไฟล์ตั้งค่าจากแพ็กเกจติดตั้งไปวางไว้ในโฟลเดอร์ Scheduled Task/Job: Launchd ของระบบ เพื่อให้ระบบเรียกโปรแกรมของคนร้ายทำงานเองทุกครั้งที่เปิดเครื่อง ต่อมาเมื่อโปรแกรมทำงาน พบว่าโปรแกรมตรวจสอบพารามิเตอร์ที่กำหนดไว้ก่อน แล้วจึงเก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่กำลังใช้งานอยู่ ตรงกับลักษณะของ System Owner/User Discovery จากนั้นเข้ารหัสข้อมูลที่รวบรวมได้ด้วยกุญแจที่ฝังไว้ในตัวโปรแกรม แล้วส่งออกไปยังเว็บไซต์สั่งการของคนร้ายผ่านช่องทางเดียวกับที่ใช้รับคำสั่ง อันเป็นลักษณะของ Exfiltration Over C2 Channel

*EN:* On 17 February 2564 a victim trading digital assets reported being tricked into installing a fake trading program on a Mac computer. Examination of the installer found a set of instructions configured to run immediately after installation completed, executing through the system's command interpreter. Those instructions moved a configuration file from the installation package into the system's Scheduled Task/Job: Launchd folder so that the system would run the offender's program by itself every time the machine started. When the program ran, it was found to check a preset parameter first, then gather the machine owner and currently logged-in username — matching System Owner/User Discovery — then encrypt the gathered information with a key embedded in the program and send it out to the offender's command website over the same channel used to receive commands, a case of Exfiltration Over C2 Channel.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1059 Command and Scripting Interpreter | มีชุดคำสั่งที่ถูกกำหนดให้ทำงานต่อทันทีหลังการติดตั้งเสร็จสิ้น ซึ่งทำงานผ่านตัวแปลคำสั่งของระบบ | The postinstall script is a sequence of instructions that runs after successfully installing an application (Command and Scripting Interpreter: Unix Shell ) |
| 2 | named | T1053 Scheduled Task/Job | ย้ายไฟล์ตั้งค่าจากแพ็กเกจติดตั้งไปวางไว้ในโฟลเดอร์ Scheduled Task/Job: Launchd ของระบบ เพื่อให้ระบบเรียกโปรแกรมของคนร้ายทำงานเองทุกครั้งที่เปิดเครื่อง | This script moves property list (plist) file .com.celastradepro.plist from the installer package to the LaunchDaemons folder (Scheduled Task/Job: Launchd ) |
| 3 | named | T1033 System Owner/User Discovery, T1041 Exfiltration Over C2 Channel | เก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่กำลังใช้งานอยู่ ตรงกับลักษณะของ System Owner/User Discovery จากนั้นเข้ารหัสข้อมูลที่รวบรวมได้ด้วยกุญแจที่ฝังไว้ในตัวโปรแกรม แล้วส่งออกไปยังเว็บไซต์สั่งการของคนร้ายผ่านช่องทางเดียวกับที่ใช้รับคำสั่ง อันเป็นลักษณะของ Exfiltration Over C2 Channel | When run, it checks for the CheckUpdate parameter, collects the victim’s host information (System Owner/User Discovery ), encrypts the collected information with a hardcoded XOR encryption, and sends information to a C2 … |

- [ ] ผ่าน / แก้แล้ว

## rcti_022 — Turla - Snake (CTID emulation plan turla_snake.yaml)

> เมื่อวันที่ 6 พฤศจิกายน 2566 สถานเอกอัครราชทูตแห่งหนึ่งแจ้งว่าเครื่องแม่ข่ายเก็บไฟล์ของสำนักงานถูกบุกรุก จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายได้ลบไฟล์เครื่องมือที่ใช้สั่งงานเครื่องระยะไกล ไฟล์ตัวติดตั้งโปรแกรมฝังตัว และไฟล์เครื่องมือดึงรหัสผ่าน ออกจากเครื่องแม่ข่ายเก็บไฟล์จนหมด ต่อมาปรากฏหลักฐานว่าโปรแกรมฝังตัวได้รับคำสั่งให้ไล่แจกแจงรายการโปรแกรมที่กำลังทำงานอยู่บนเครื่อง เพื่อค้นหากระบวนการที่ทำงานอยู่ภายใต้สิทธิ์ของผู้ดูแลโดเมน สุดท้ายพบว่าคนร้ายอาศัยสิทธิ์ประจำตัวที่ได้จากกระบวนการดังกล่าว สร้างบัญชีผู้ใช้ใหม่ขึ้นในโดเมนขององค์กรและกำหนดให้มีสิทธิ์ระดับผู้ดูแล เพื่อใช้เป็นช่องทางกลับเข้ามาในภายหลัง

*EN:* On 6 November 2566 an embassy reported that its office file server had been breached. Digital forensic examination found that the offender deleted the remote command tool file, the implant installer file and the password extraction tool file from the file server entirely. Evidence then showed the implant receiving a command to enumerate the programs running on the machine in order to find a process running under domain administrator privileges. Finally the offender was found using the identity token obtained from that process to create a new user account in the organisation's domain and grant it administrator-level rights, to serve as a way back in later.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1070 Indicator Removal | คนร้ายได้ลบไฟล์เครื่องมือที่ใช้สั่งงานเครื่องระยะไกล ไฟล์ตัวติดตั้งโปรแกรมฝังตัว และไฟล์เครื่องมือดึงรหัสผ่าน ออกจากเครื่องแม่ข่ายเก็บไฟล์จนหมด | Delete PsExec, the Snake installer, and Mimikatz from the file server. |
| 2 | described | T1057 Process Discovery | โปรแกรมฝังตัวได้รับคำสั่งให้ไล่แจกแจงรายการโปรแกรมที่กำลังทำงานอยู่บนเครื่อง เพื่อค้นหากระบวนการที่ทำงานอยู่ภายใต้สิทธิ์ของผู้ดูแลโดเมน | Task Snake to enumerate running processes on the machine to discover processes under the domain admin. |
| 3 | described | T1136 Create Account | คนร้ายอาศัยสิทธิ์ประจำตัวที่ได้จากกระบวนการดังกล่าว สร้างบัญชีผู้ใช้ใหม่ขึ้นในโดเมนขององค์กรและกำหนดให้มีสิทธิ์ระดับผู้ดูแล เพื่อใช้เป็นช่องทางกลับเข้ามาในภายหลัง | Task Snake to create a new domain user using an access token from one of the domain admin processes. The new domain user will be used as a backdoor domain admin account for persistence on the domain. Task Snake to create… |

- [ ] ผ่าน / แก้แล้ว

## rcti_023 — CISA AA22-181A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-181a>

> เมื่อวันที่ 30 มิถุนายน 2565 บริษัทขนส่งแห่งหนึ่งในจังหวัดพระนครศรีอยุธยาแจ้งความว่าไฟล์งานในเครื่องแม่ข่ายและเครื่องลูกข่ายถูกเข้ารหัสลับทั้งหมดพร้อมมีข้อความเรียกค่าไถ่ จากการตรวจสอบพบว่าก่อนลงมือ คนร้ายสั่งให้เครื่องเริ่มระบบใหม่เข้าสู่โหมดปลอดภัย ซึ่งทำให้โปรแกรมด้านความปลอดภัยที่ติดตั้งไว้ไม่ถูกโหลดขึ้นมาทำงานและไม่สามารถตรวจจับพฤติกรรมของคนร้ายได้ ต่อมาพบว่าไฟล์ของผู้เสียหายถูกเข้ารหัสลับด้วยอัลกอริทึมแบบสมมาตรขนาดสองร้อยห้าสิบหกบิต แล้วกุญแจที่ใช้ยังถูกนำไปเข้ารหัสซ้ำด้วยกุญแจสาธารณะขนาดสองพันสี่สิบแปดบิตอีกชั้นหนึ่ง สุดท้ายจากการตรวจสอบพบว่าคนร้ายพยายามตัดหนทางกู้คืนข้อมูลของผู้เสียหาย โดยลบข้อมูลสำรองที่เก็บไว้ในเครื่อง ปิดตัวเลือกการกู้คืนระบบตอนเริ่มเครื่อง และลบสำเนาเงาของไฟล์ทิ้งทั้งหมด

*EN:* On 30 June 2565 a transport company in Phra Nakhon Si Ayutthaya province reported that work files on its servers and clients had all been encrypted and a ransom message left. Examination found that before acting, the offender had the machines restarted into safe mode, which meant the installed security software was not loaded and could not detect the offender's behaviour. The victim's files were then found encrypted with a 256-bit symmetric algorithm, with the key used further encrypted under a 2048-bit public key. Finally the offender was found to have tried to cut off the victim's routes to recovery by deleting locally stored backups, disabling the startup recovery option and deleting all shadow copies of files.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1562 ? | คนร้ายสั่งให้เครื่องเริ่มระบบใหม่เข้าสู่โหมดปลอดภัย ซึ่งทำให้โปรแกรมด้านความปลอดภัยที่ติดตั้งไว้ไม่ถูกโหลดขึ้นมาทำงานและไม่สามารถตรวจจับพฤติกรรมของคนร้ายได้ | Restarts the machine in safe mode to avoid detection by security software |
| 2 | described | T1486 Data Encrypted for Impact | ไฟล์ของผู้เสียหายถูกเข้ารหัสลับด้วยอัลกอริทึมแบบสมมาตรขนาดสองร้อยห้าสิบหกบิต แล้วกุญแจที่ใช้ยังถูกนำไปเข้ารหัสซ้ำด้วยกุญแจสาธารณะขนาดสองพันสี่สิบแปดบิตอีกชั้นหนึ่ง | Encrypts victim files with the AES-256 encryption algorithm; the resulting key is then encrypted with an RSA-2048 public key |
| 3 | described | T1490 Inhibit System Recovery | คนร้ายพยายามตัดหนทางกู้คืนข้อมูลของผู้เสียหาย โดยลบข้อมูลสำรองที่เก็บไว้ในเครื่อง ปิดตัวเลือกการกู้คืนระบบตอนเริ่มเครื่อง และลบสำเนาเงาของไฟล์ทิ้งทั้งหมด | Attempts to prevent standard recovery techniques by deleting local backups, disabling startup recovery options, and deleting shadow copies |

- [ ] ผ่าน / แก้แล้ว

## rcti_024 — FIN7 (CTID emulation plan Fin7.yaml)

ต้นทาง: <https://securelist.com/fin7-5-the-infamous-cybercrime-rig-fin7-continues-its-activities/90703/>

> เมื่อวันที่ 25 มกราคม 2567 โรงแรมแห่งหนึ่งในจังหวัดภูเก็ตแจ้งความว่าเครื่องคอมพิวเตอร์ที่แผนกต้อนรับส่วนหน้าถูกควบคุมจากระยะไกล จากการตรวจสอบพบว่ามีโปรแกรมแปลกปลอมทำหน้าที่บันทึกภาพสิ่งที่ปรากฏบนจอของพนักงานขณะปฏิบัติงานไว้เป็นระยะ ต่อมาปรากฏหลักฐานว่าคนร้ายสั่งให้ไฟล์โปรแกรมที่วางไว้บนเครื่องก่อนหน้าเริ่มทำงาน โดยเรียกผ่านหน้าต่างพิมพ์คำสั่งของระบบปฏิบัติการวินโดวส์ จากนั้นเมื่อโปรแกรมทำงานแล้ว พบว่ามีการไล่ตรวจสอบรายการกระบวนการที่กำลังทำงานอยู่บนเครื่องทั้งหมดเพื่อสำรวจสภาพแวดล้อมก่อนดำเนินการขั้นต่อไป

*EN:* On 25 January 2567 a hotel in Phuket province reported that a computer at its front desk was being controlled remotely. Examination found a foreign program periodically recording images of what appeared on staff screens while they worked. Evidence then showed the offender starting a program file previously placed on the machine, invoking it through the Windows operating system's command prompt window. Once the program was running, it was found enumerating all processes running on the machine to survey the environment before proceeding.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1113 Screen Capture | มีโปรแกรมแปลกปลอมทำหน้าที่บันทึกภาพสิ่งที่ปรากฏบนจอของพนักงานขณะปฏิบัติงานไว้เป็นระยะ | Take screenshots of end user's endpoint. |
| 2 | described | T1059 Command and Scripting Interpreter | คนร้ายสั่งให้ไฟล์โปรแกรมที่วางไว้บนเครื่องก่อนหน้าเริ่มทำงาน โดยเรียกผ่านหน้าต่างพิมพ์คำสั่งของระบบปฏิบัติการวินโดวส์ | Execution of previously placed stager. |
| 3 | described | T1057 Process Discovery | มีการไล่ตรวจสอบรายการกระบวนการที่กำลังทำงานอยู่บนเครื่องทั้งหมดเพื่อสำรวจสภาพแวดล้อมก่อนดำเนินการขั้นต่อไป | Perform process discovery (T1057) |

- [ ] ผ่าน / แก้แล้ว

## rcti_025 — Turla - Carbon (CTID emulation plan turla_carbon.yaml)

> เมื่อวันที่ 12 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งว่าเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ระดับบริหารถูกฝังโปรแกรมควบคุมระยะไกล จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าโปรแกรมฝังตัวที่ทำงานด้วยสิทธิ์ระดับระบบได้เรียกตัวติดตั้งของโปรแกรมฝังตัวรุ่นถัดไปขึ้นมาทำงาน โดยตัวติดตั้งดังกล่าวได้แก้ไขค่าในทะเบียนระบบของเครื่องเพื่อวางการตั้งค่าของตนเองไว้ ต่อมาปรากฏหลักฐานว่าโปรแกรมฝังตัวได้รับคำสั่งให้ตรวจสอบว่าขณะนั้นกำลังทำงานอยู่ภายใต้ชื่อบัญชีผู้ใช้ใดของระบบ สุดท้ายพบว่าคนร้ายสั่งให้โปรแกรมดาวน์โหลดสคริปต์เข้ามาแล้วทำ Password Spraying โดยนำรหัสผ่านที่คาดเดาง่ายจำนวนหนึ่งไปลองล็อกอินกับบัญชีผู้ดูแลโดเมนหลายบัญชี พร้อมกับพยายามเชื่อมต่อไดรฟ์ของเครื่องแม่ข่ายควบคุมโดเมน

*EN:* On 12 October 2566 a security agency reported that an executive's computer had been implanted with a remote control program. Digital forensic examination found that an implant running with system-level privileges launched the installer of a follow-on implant, and that installer modified values in the machine's system registry to place its own configuration there. Evidence then showed the implant receiving a command to check which system user account it was currently running under. Finally the offender was found ordering the program to download a script and carry out Password Spraying, trying a set of easily guessed passwords against several domain administrator accounts while attempting to mount a drive on the domain controller.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1112 Modify Registry | ตัวติดตั้งดังกล่าวได้แก้ไขค่าในทะเบียนระบบของเครื่องเพื่อวางการตั้งค่าของตนเองไว้ | Task the SYSTEM level EPIC implant to execute the CARBON-DLL installer. |
| 2 | described | T1033 System Owner/User Discovery | โปรแกรมฝังตัวได้รับคำสั่งให้ตรวจสอบว่าขณะนั้นกำลังทำงานอยู่ภายใต้ชื่อบัญชีผู้ใช้ใดของระบบ | Task the Carbon implant to execute the whoami discovery command. |
| 3 | named | T1110 Brute Force | คนร้ายสั่งให้โปรแกรมดาวน์โหลดสคริปต์เข้ามาแล้วทำ Password Spraying โดยนำรหัสผ่านที่คาดเดาง่ายจำนวนหนึ่งไปลองล็อกอินกับบัญชีผู้ดูแลโดเมนหลายบัญชี | Task CARBON-DLL to download and execute the batch script to spray weak passwords against the domain admin accounts and attempt to mount the C$ drive of the DC. |

- [ ] ผ่าน / แก้แล้ว

## rcti_026 — CISA AA22-055A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-055a>

> เมื่อวันที่ 21 กุมภาพันธ์ 2565 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าตรวจพบโปรแกรมไม่พึงประสงค์ฝังอยู่ในเครื่องแม่ข่ายของหน่วยงาน จากการตรวจสอบพบว่าคนร้ายวางไฟล์สคริปต์ PowerShell ที่ถูกอำพรางให้มีนามสกุลเป็นไฟล์ข้อมูลธรรมดาไว้บนเครื่อง โดยสคริปต์นั้นทำหน้าที่ถอดรหัสและเรียกสคริปต์ PowerShell อีกชั้นหนึ่งที่ถูกอำพรางไว้เช่นกันขึ้นมาทำงานต่อ ต่อมาปรากฏหลักฐานว่าคนร้ายใช้เทคนิค DLL Side-Loading หลอกให้โปรแกรมที่ถูกต้องตามลิขสิทธิ์เรียกไฟล์ของคนร้ายขึ้นมาทำงานแทน ควบคู่กับการอำพรางเนื้อหาสคริปต์ PowerShell เพื่อซ่อนคำสั่งที่ใช้ติดต่อกับเครื่องสั่งการ นอกจากนี้ยังพบว่าคนร้ายเปลี่ยนชื่อไฟล์ DLL ของตนให้ตรงกับชื่อไฟล์ของโปรแกรมที่ถูกต้อง เพื่อให้กลไก DLL Side-Loading ทำงานได้สำเร็จ

*EN:* On 21 February 2565 a government agency reported finding an unwanted program implanted on one of its servers. Examination found that the offender placed a PowerShell script file on the machine disguised with an ordinary data-file extension, and that script decrypted and ran a second, likewise disguised PowerShell script. Evidence then showed the offender using the DLL Side-Loading technique to trick a legitimately licensed program into loading the offender's file instead, alongside obfuscating the contents of PowerShell scripts to hide the commands used to contact the command machine. The offender was also found renaming their own DLL file to match the filename of the legitimate program so that the DLL Side-Loading mechanism would succeed.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1059 Command and Scripting Interpreter | คนร้ายวางไฟล์สคริปต์ PowerShell ที่ถูกอำพรางให้มีนามสกุลเป็นไฟล์ข้อมูลธรรมดาไว้บนเครื่อง โดยสคริปต์นั้นทำหน้าที่ถอดรหัสและเรียกสคริปต์ PowerShell อีกชั้นหนึ่งที่ถูกอำพรางไว้เช่นกันขึ้นมาทำงานต่อ | A PowerShell script, obfuscated as a .dat file, goopdate.dat, used to decrypt and run a second obfuscated PowerShell script, config.txt According to a sample analyzed by NCSC-UK, Small Sieve is a simple Python backdoor d… |
| 2 | named | T1574 Hijack Execution Flow, T1059 Command and Scripting Interpreter, T1027 Obfuscated Files or Information | คนร้ายใช้เทคนิค DLL Side-Loading หลอกให้โปรแกรมที่ถูกต้องตามลิขสิทธิ์เรียกไฟล์ของคนร้ายขึ้นมาทำงานแทน ควบคู่กับการอำพรางเนื้อหาสคริปต์ PowerShell เพื่อซ่อนคำสั่งที่ใช้ติดต่อกับเครื่องสั่งการ | MuddyWater actors also use techniques such as side-loading DLLs to trick legitimate programs into running malware and obfuscating PowerShell scripts to hide C2 functions (see the PowGoop section for more information) |
| 3 | named | T1574 Hijack Execution Flow | คนร้ายเปลี่ยนชื่อไฟล์ DLL ของตนให้ตรงกับชื่อไฟล์ของโปรแกรมที่ถูกต้อง เพื่อให้กลไก DLL Side-Loading ทำงานได้สำเร็จ | A DLL file renamed as a legitimate filename, Goopdate.dll, to enable the DLL side-loading technique |

- [ ] ผ่าน / แก้แล้ว

## rcti_027 — CISA AA20-301A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-301a>

> เมื่อวันที่ 27 ตุลาคม 2563 หน่วยงานวิจัยแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของนักวิจัยหลายรายถูกบุกรุก จากการตรวจสอบพบว่าคนร้ายส่งจดหมายอิเล็กทรอนิกส์แนบไฟล์เอกสารอันตรายมายังนักวิจัยเป็นรายบุคคล โดยเนื้อความออกแบบมาให้ผู้รับหลงเชื่อและเปิดไฟล์แนบ ซึ่งเป็นวิธีที่พบมากที่สุดในคดีนี้ นอกจากนี้ยังพบช่องทางอื่นอีกหลายแบบ ได้แก่ อีเมลอ้างว่าเป็นการแจ้งเตือนความปลอดภัยของบัญชีพร้อมแนบลิงก์ การดัดแปลงเว็บไซต์ที่กลุ่มเป้าหมายเข้าใช้ประจำให้ติดตั้งโปรแกรมลงเครื่องผู้เข้าชม การแจกจ่ายโปรแกรมอันตรายผ่านเว็บแบ่งปันไฟล์ และการหลอกให้ผู้เสียหายติดตั้งส่วนขยายของโปรแกรมท่องเว็บที่คนร้ายทำขึ้นเพื่อแทรกกลางการใช้งาน ต่อมาปรากฏหลักฐานว่าเครื่องที่ถูกยึดครองเรียกใช้โปรแกรม mshta.exe ซึ่งเป็นเครื่องมือที่ติดมากับระบบปฏิบัติการวินโดวส์ ให้ไปดาวน์โหลดและสั่งรันไฟล์แอปพลิเคชันเอชทีเอ็มแอลจากเครื่องปลายทางภายนอก

*EN:* On 27 October 2563 a research organisation reported that several researchers' computers had been breached. Examination found the offender sending emails with malicious document attachments to researchers individually, the wording designed to make recipients trust and open the attachment — the most common method in this case. Several other routes were also found: emails claiming to be account security alerts with links attached, tampering with websites the targets visited regularly so that a program was installed on visitors' machines, distributing malicious programs through file-sharing sites, and tricking victims into installing a browser extension made by the offender to interpose itself in their sessions. Evidence then showed the compromised machine invoking mshta.exe, a tool shipped with the Windows operating system, to download and run an HTML application file from an external endpoint.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1566 Phishing | คนร้ายส่งจดหมายอิเล็กทรอนิกส์แนบไฟล์เอกสารอันตรายมายังนักวิจัยเป็นรายบุคคล โดยเนื้อความออกแบบมาให้ผู้รับหลงเชื่อและเปิดไฟล์แนบ ซึ่งเป็นวิธีที่พบมากที่สุดในคดีนี้ | Kimsuky uses various spearphishing and social engineering methods to obtain Initial Access [TA0001] to victim networks.,, Spearphishing—with a malicious attachment embedded in the email—is the most observed Kimsuky tacti… |
| 2 | described | T1566 Phishing, T1189 Drive-by Compromise, T1185 Browser Session Hijacking | อีเมลอ้างว่าเป็นการแจ้งเตือนความปลอดภัยของบัญชีพร้อมแนบลิงก์ การดัดแปลงเว็บไซต์ที่กลุ่มเป้าหมายเข้าใช้ประจำให้ติดตั้งโปรแกรมลงเครื่องผู้เข้าชม การแจกจ่ายโปรแกรมอันตรายผ่านเว็บแบ่งปันไฟล์ และการหลอกให้ผู้เสียหายติดตั้งส่วนขยายของโปรแกรมท่องเว็บที่คนร้ายทำขึ้นเพื่อแทรกกลางการใช้งาน | Kimsuky’s other methods for obtaining initial access include login-security-alert-themed phishing emails, watering hole attacks, distributing malware through torrent sharing sites, and directing victims to install malici… |
| 3 | named | T1218 System Binary Proxy Execution | เครื่องที่ถูกยึดครองเรียกใช้โปรแกรม mshta.exe ซึ่งเป็นเครื่องมือที่ติดมากับระบบปฏิบัติการวินโดวส์ ให้ไปดาวน์โหลดและสั่งรันไฟล์แอปพลิเคชันเอชทีเอ็มแอลจากเครื่องปลายทางภายนอก | First, the compromised host system uses the native Microsoft Windows utility, mshta.exe, to download and execute an HTML application (HTA) file from a remote system (Signed Binary Proxy Execution: Mshta ) |

- [ ] ผ่าน / แก้แล้ว

## rcti_028 — CISA AA22-181A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-181a>

> เมื่อวันที่ 12 กรกฎาคม 2565 บริษัทรับจ้างผลิตแห่งหนึ่งในจังหวัดสมุทรสาครแจ้งความว่าไฟล์งานในเครื่องแม่ข่ายถูกเข้ารหัสลับและมีข้อความเรียกค่าไถ่ จากการตรวจสอบ log การเข้าใช้งานพบว่าคนร้ายเข้าถึงเครื่องของผู้เสียหายผ่านบริการเดสก์ท็อประยะไกลที่ตั้งค่าไว้ไม่รัดกุม โดยเปิดให้เข้าถึงได้จากอินเทอร์เน็ตและใช้รหัสผ่านที่คาดเดาได้ นอกจากนี้ยังพบอีกช่องทางหนึ่ง คือคนร้ายส่งอีเมลหลอกลวงและอีเมลขยะจำนวนมากถึงพนักงาน โดยแนบไฟล์โปรแกรมเรียกค่าไถ่มากับอีเมลโดยตรง ต่อมาปรากฏหลักฐานว่าคนร้ายใช้ไฟล์แบตช์เรียกสคริปต์ PowerShell ขึ้นมาทำงาน เพื่อโหลดโปรแกรมเรียกค่าไถ่เข้าไปทำงานในหน่วยความจำของเครื่องโดยไม่ต้องเขียนไฟล์ลงดิสก์

*EN:* On 12 July 2565 a contract manufacturer in Samut Sakhon province reported that work files on its server had been encrypted with a ransom message. Access logs showed the offender reaching the victim's machines through a loosely configured remote desktop service, exposed to the internet and using a guessable password. A second route was also found: the offender sent large numbers of phishing and spam emails to staff with the ransom program file attached directly. Evidence then showed the offender using a batch file to launch a PowerShell script in order to load the ransom program into the machine's memory without writing a file to disk.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1133 External Remote Services | คนร้ายเข้าถึงเครื่องของผู้เสียหายผ่านบริการเดสก์ท็อประยะไกลที่ตั้งค่าไว้ไม่รัดกุม โดยเปิดให้เข้าถึงได้จากอินเทอร์เน็ตและใช้รหัสผ่านที่คาดเดาได้ | MedusaLocker ransomware actors most often gain access to victim devices through vulnerable Remote Desktop Protocol (RDP) configurations |
| 2 | described | T1566 Phishing | คนร้ายส่งอีเมลหลอกลวงและอีเมลขยะจำนวนมากถึงพนักงาน โดยแนบไฟล์โปรแกรมเรียกค่าไถ่มากับอีเมลโดยตรง | Actors also frequently use email phishing and spam email campaigns—directly attaching the ransomware to the email—as initial intrusion vectors |
| 3 | named | T1059 Command and Scripting Interpreter | คนร้ายใช้ไฟล์แบตช์เรียกสคริปต์ PowerShell ขึ้นมาทำงาน เพื่อโหลดโปรแกรมเรียกค่าไถ่เข้าไปทำงานในหน่วยความจำของเครื่องโดยไม่ต้องเขียนไฟล์ลงดิสก์ | MedusaLocker ransomware uses a batch file to execute PowerShell script invoke-ReflectivePEInjection |

- [ ] ผ่าน / แก้แล้ว

## rcti_029 — CISA AA22-138B (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-138b>

> เมื่อวันที่ 13 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบยูนิกซ์ขององค์กรถูกบุกรุก จากการตรวจสอบ log พบว่าคนร้ายส่งคำสั่งของระบบยูนิกซ์เข้ามายังเครื่องแม่ข่ายนับพันคำสั่งจากหมายเลขไอพีเดียวกัน ซึ่งบางคำสั่งทำให้คนร้ายเปิดอ่านไฟล์ที่เก็บรายชื่อบัญชีผู้ใช้และไฟล์ที่เก็บค่ารหัสผ่านของระบบได้ ต่อมาปรากฏหลักฐานว่าคนร้ายส่งคำขอเข้ามาเพื่อเปลี่ยนสิทธิ์การเข้าถึงของไฟล์ที่ซ่อนไว้ในโฟลเดอร์ไฟล์ชั่วคราวของระบบก่อนเป็นอันดับแรก จากการตรวจสอบเนื้อหาที่รับส่งพบว่าคำสั่งและผลลัพธ์ที่ส่งกลับถูกแปลงด้วยกุญแจลับก่อนเสมอ ทำให้อุปกรณ์ตรวจจับของหน่วยงานอ่านเนื้อหาไม่ได้ สุดท้ายในวันถัดมาพบว่าคนร้ายดาวน์โหลดโปรแกรมสำหรับเปิดช่องทางส่งต่อการเชื่อมต่อแบบย้อนกลับเข้ามาไว้บนเครื่อง เพื่อให้เข้าถึงเครือข่ายภายในจากภายนอกได้

*EN:* On 13 April 2565 an agency reported that its Unix server had been breached. Logs showed the offender sending thousands of Unix system commands to the server from a single IP address, some of which let the offender read the file listing user accounts and the file holding the system's password values. Evidence then showed the offender first sending a request to change the access permissions of a hidden file in the system's temporary file folder. Examination of the exchanged content found that commands and returned output were always transformed with a secret key, leaving the agency's detection devices unable to read them. Finally, the next day, the offender was found downloading a program to open a reverse forwarding channel onto the machine so that the internal network could be reached from outside.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1059 Command and Scripting Interpreter, T1003 OS Credential Dumping | คนร้ายส่งคำสั่งของระบบยูนิกซ์เข้ามายังเครื่องแม่ข่ายนับพันคำสั่งจากหมายเลขไอพีเดียวกัน ซึ่งบางคำสั่งทำให้คนร้ายเปิดอ่านไฟล์ที่เก็บรายชื่อบัญชีผู้ใช้และไฟล์ที่เก็บค่ารหัสผ่านของระบบได้ | On April 13, TA2 sent thousands of Unix commands from IP address 84.38.133[.]149, some of which enabled TA2 to view /etc/passwd and /etc/shadow password files ([TA0006], ) |
| 2 | described | T1222 File and Directory Permissions Modification | คนร้ายส่งคำขอเข้ามาเพื่อเปลี่ยนสิทธิ์การเข้าถึงของไฟล์ที่ซ่อนไว้ในโฟลเดอร์ไฟล์ชั่วคราวของระบบก่อนเป็นอันดับแรก | TA2 first sent a GET request with the CHMOD command to change the permissions of .tmp12865xax, a hidden file in the /tmp directory |
| 3 | described | T1573 Encrypted Channel | คำสั่งและผลลัพธ์ที่ส่งกลับถูกแปลงด้วยกุญแจลับก่อนเสมอ ทำให้อุปกรณ์ตรวจจับของหน่วยงานอ่านเนื้อหาไม่ได้ | The commands and output were encrypted with an XOR key |
| 4 | described | T1090 Proxy | คนร้ายดาวน์โหลดโปรแกรมสำหรับเปิดช่องทางส่งต่อการเชื่อมต่อแบบย้อนกลับเข้ามาไว้บนเครื่อง เพื่อให้เข้าถึงเครือข่ายภายในจากภายนอกได้ | On April 14, TA2 downloaded a reverse SOCKS proxy |

- [ ] ผ่าน / แก้แล้ว

## rcti_030 — OilRig (CTID emulation plan oilrig.yaml)

> เมื่อวันที่ 4 สิงหาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความว่าฐานข้อมูลสำรองของระบบงานภายในถูกนำออกไปจากเครือข่าย จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายสั่งรันคำสั่งไล่สำรวจรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่ายที่ยึดครองไว้ เพื่อค้นหาว่ามีข้อมูลสำคัญเก็บอยู่ที่ใดบ้าง ต่อมาปรากฏหลักฐานว่าคนร้ายสร้างโฟลเดอร์ขึ้นใหม่สำหรับพักข้อมูลที่รวบรวมได้ แล้วทยอยอ่านไฟล์ฐานข้อมูลสำรองออกเป็นชิ้นเล็ก ๆ ส่งออกไปยังบัญชีจดหมายอิเล็กทรอนิกส์ของคนร้ายผ่านช่องทางบริการอีเมลขององค์กรเอง ซึ่งเป็นคนละช่องทางกับที่ใช้รับคำสั่งและไม่ได้เข้ารหัสลับเนื้อหา สุดท้ายเมื่อดำเนินการเสร็จ พบว่าคนร้ายลบไฟล์เครื่องมือทั้งหมดที่นำเข้ามาออกจากเครื่อง และสั่งให้โปรแกรมฝังตัวของตนหยุดทำงานและลบตัวเองทิ้ง

*EN:* On 4 August 2567 an energy company reported that a backup database of its internal systems had been taken out of the network. Digital forensic examination found the offender running commands to enumerate file and folder names on the compromised server in order to locate important data. Evidence then showed the offender creating a new folder to stage the collected data, then reading the backup database file out in small chunks and sending it to the offender's own email account through the organisation's own mail service — a different channel from the one used to receive commands, and one that did not encrypt the content. Finally, on completion, the offender was found deleting every tool file they had brought in and ordering their implant to stop and delete itself.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1083 File and Directory Discovery | คนร้ายสั่งรันคำสั่งไล่สำรวจรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่ายที่ยึดครองไว้ เพื่อค้นหาว่ามีข้อมูลสำคัญเก็บอยู่ที่ใดบ้าง | Requires xdotool to be installed on the running machine. Uses xdotool to execute file and directory discovery commands on ENDOFROAD |
| 2 | described | T1048 Exfiltration Over Alternative Protocol | ทยอยอ่านไฟล์ฐานข้อมูลสำรองออกเป็นชิ้นเล็ก ๆ ส่งออกไปยังบัญชีจดหมายอิเล็กทรอนิกส์ของคนร้ายผ่านช่องทางบริการอีเมลขององค์กรเอง ซึ่งเป็นคนละช่องทางกับที่ใช้รับคำสั่งและไม่ได้เข้ารหัสลับเนื้อหา | Requires xdotool to be installed on the running machine. Creates a directory to stage collected data and moves RDAT to the newly created directory. Read and exfiltrate the data from sitedata_db.bak in chunks via EWS API … |
| 3 | described | T1070 Indicator Removal | คนร้ายลบไฟล์เครื่องมือทั้งหมดที่นำเข้ามาออกจากเครื่อง และสั่งให้โปรแกรมฝังตัวของตนหยุดทำงานและลบตัวเองทิ้ง | Requires xdotool to be installed on the running machine. Emulates OilRig's cleanup and egress from the target network. Delete VALUEVAULT plink.exe. Gosta Agent kills itself |

- [ ] ผ่าน / แก้แล้ว

## rcti_031 — OilRig (CTID emulation plan oilrig.yaml)

> เมื่อวันที่ 16 กันยายน 2567 บริษัทนำเข้าส่งออกแห่งหนึ่งแจ้งความว่าบัญชีผู้ใช้งานระบบภายในถูกสวมรอย จากการตรวจสอบเครื่องคอมพิวเตอร์ของพนักงานพบว่าคนร้ายรันโปรแกรมที่เข้าไปอ่านคลังเก็บรหัสผ่านของระบบปฏิบัติการวินโดวส์ ซึ่งเป็นที่ที่โปรแกรมท่องเว็บบันทึกชื่อผู้ใช้และรหัสผ่านไว้ให้ผู้ใช้เข้าระบบอัตโนมัติ แล้วเขียนผลที่ได้ลงเป็นไฟล์ฐานข้อมูลขนาดเล็กบนเครื่อง ต่อมาปรากฏหลักฐานว่าคนร้ายส่งไฟล์ฐานข้อมูลดังกล่าวออกไปยังเครื่องสั่งการภายนอก โดยใช้ช่องทางเดียวกับที่โปรแกรมฝังตัวใช้ติดต่อรับคำสั่งอยู่แล้ว สุดท้ายพบว่าโปรแกรมที่ฝังอยู่บนเครื่องได้ดาวน์โหลดไฟล์ชุดคำสั่งเพิ่มเติมจากเครื่องภายนอกเข้ามาเก็บไว้บนเครื่องของผู้เสียหายอีกด้วย

*EN:* On 16 September 2567 an import-export company reported that internal system accounts had been impersonated. Examination of an employee's computer found the offender running a program that read the Windows operating system's password store — where the web browser saves usernames and passwords so users can log in automatically — and wrote the results into a small database file on the machine. Evidence then showed the offender sending that database file out to an external command machine using the same channel the implant already used to receive its instructions. Finally the implanted program on the machine was found downloading a further instruction file from an external machine onto the victim's computer.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1555 Credentials from Password Stores | คนร้ายรันโปรแกรมที่เข้าไปอ่านคลังเก็บรหัสผ่านของระบบปฏิบัติการวินโดวส์ ซึ่งเป็นที่ที่โปรแกรมท่องเว็บบันทึกชื่อผู้ใช้และรหัสผ่านไว้ให้ผู้ใช้เข้าระบบอัตโนมัติ แล้วเขียนผลที่ได้ลงเป็นไฟล์ฐานข้อมูลขนาดเล็กบนเครื่อง | Create a SQLite database with output of Windows Credential Value for Internet Explorer |
| 2 | described | T1041 Exfiltration Over C2 Channel | คนร้ายส่งไฟล์ฐานข้อมูลดังกล่าวออกไปยังเครื่องสั่งการภายนอก โดยใช้ช่องทางเดียวกับที่โปรแกรมฝังตัวใช้ติดต่อรับคำสั่งอยู่แล้ว | Exfil the SQLite database fsociety.dat created by b.exe |
| 3 | described | T1105 Ingress Tool Transfer | โปรแกรมที่ฝังอยู่บนเครื่องได้ดาวน์โหลดไฟล์ชุดคำสั่งเพิ่มเติมจากเครื่องภายนอกเข้ามาเก็บไว้บนเครื่องของผู้เสียหายอีกด้วย | SystemFailureReporter.exe downloads contact.aspx |

- [ ] ผ่าน / แก้แล้ว

## rcti_032 — CISA AA20-227A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-227a>

> เมื่อวันที่ 14 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ได้รับอีเมลต้องสงสัยและเครื่องคอมพิวเตอร์มีอาการผิดปกติหลังเปิดไฟล์แนบ จากการตรวจสอบพบว่าคนร้ายส่งโปรแกรมอันตรายมากับอีเมลหลอกลวงในรูปของไฟล์เอกสารเวิร์ดที่มีชุดคำสั่งมาโครอันตรายฝังอยู่ภายใน ต่อมาปรากฏหลักฐานว่าชุดคำสั่งดังกล่าวเปลี่ยนสีตัวอักษรในเอกสารจากสีเทาอ่อนเป็นสีดำเพื่อหลอกให้ผู้ใช้กดอนุญาตให้เนื้อหาทำงาน ตรวจสอบว่าระบบปฏิบัติการเป็นรุ่นสามสิบสองบิตหรือหกสิบสี่บิต แล้วประกอบบรรทัดคำสั่งขึ้นมาสั่งงานผ่าน Windows Command Shell เพื่อดาวน์โหลดไฟล์เพิ่มเติมเข้ามาในเครื่อง สุดท้ายจากการตรวจสอบปริมาณข้อมูลขาออกพบว่าข้อมูลที่รวบรวมได้จากเครื่องผู้เสียหายถูกส่งออกไปทางโพรโทคอลรับส่งไฟล์ธรรมดาที่ไม่ได้เข้ารหัสลับ ซึ่งเป็นคนละช่องทางกับที่ใช้รับคำสั่ง

*EN:* On 14 August 2563 an agency reported that staff had received a suspicious email and that a computer behaved abnormally after the attachment was opened. Examination found the offender delivering a malicious program with a phishing email in the form of a Word document with malicious macro instructions embedded inside. Evidence then showed those instructions changing the document's font colour from light grey to black to trick the user into enabling content, checking whether the operating system was 32-bit or 64-bit, and assembling a command line to issue through the Windows Command Shell in order to download further files onto the machine. Finally, examination of outbound traffic found that data gathered from the victim's machine was sent out over an ordinary unencrypted file transfer protocol, a different channel from the one used to receive commands.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1566 Phishing | คนร้ายส่งโปรแกรมอันตรายมากับอีเมลหลอกลวงในรูปของไฟล์เอกสารเวิร์ดที่มีชุดคำสั่งมาโครอันตรายฝังอยู่ภายใน | KONNI malware is often delivered via phishing emails as a Microsoft Word document with a malicious VBA macro code (Phishing: Spearphising Attachment ) |
| 2 | named | T1059 Command and Scripting Interpreter | ประกอบบรรทัดคำสั่งขึ้นมาสั่งงานผ่าน Windows Command Shell เพื่อดาวน์โหลดไฟล์เพิ่มเติมเข้ามาในเครื่อง | The malicious code can change the font color from light grey to black (to fool the user to enable content), check if the Windows operating system is a 32-bit or 64-bit version, and construct and execute the command line … |
| 3 | described | T1048 Exfiltration Over Alternative Protocol | ข้อมูลที่รวบรวมได้จากเครื่องผู้เสียหายถูกส่งออกไปทางโพรโทคอลรับส่งไฟล์ธรรมดาที่ไม่ได้เข้ารหัสลับ ซึ่งเป็นคนละช่องทางกับที่ใช้รับคำสั่ง | Exfiltration Over Alternative Protocol: Exfiltration Over Unencrypted/Obfuscated Non-C2 Protocol |

- [ ] ผ่าน / แก้แล้ว

## rcti_033 — menuPass (CTID emulation plan menupass.yaml)

ต้นทาง: <https://go.recordedfuture.com/hubfs/reports/cta-2019-0206.pdf>

> เมื่อวันที่ 30 พฤศจิกายน 2566 บริษัทผู้ให้บริการด้านเทคโนโลยีสารสนเทศแห่งหนึ่งแจ้งความว่าข้อมูลของลูกค้าที่บริษัทดูแลอยู่ถูกนำออกไป จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายใช้เครื่องมือทำ Credential Dumping ดึงค่ารหัสผ่านออกจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่องที่ยึดครองได้ ทั้งแบบรันบนเครื่องนั้นโดยตรงและแบบสั่งดึงจากเครื่องอื่นในเครือข่ายจากระยะไกล ต่อมาปรากฏหลักฐานว่าคนร้ายอาศัยการสร้างบริการของระบบขึ้นบนเครื่องปลายทางเพื่อสั่งรันคำสั่งจากระยะไกลบนเครื่องนั้น จากนั้นได้รวบรวมไฟล์ข้อมูลของลูกค้ามาบีบอัดรวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดทั่วไปเพื่อเตรียมนำออก และสุดท้ายพบว่าไฟล์ที่บีบอัดแล้วถูกนำไปพักไว้ในถังขยะของเครื่องซึ่งเป็นตำแหน่งที่ผู้ดูแลระบบมักไม่ตรวจสอบ ก่อนจะถูกส่งออกไปภายนอก

*EN:* On 30 November 2566 an IT service provider reported that data belonging to the clients it managed had been taken out. Digital forensic examination found the offender using a Credential Dumping tool to pull password values from the memory of the authentication process on a compromised machine, both by running it on that machine directly and by pulling from other machines on the network remotely. Evidence then showed the offender creating a system service on a target machine in order to run commands on it remotely, then gathering client data files and compressing them into a single file with an ordinary compression program ready to be taken out. Finally the compressed file was found staged in the machine's recycle bin — a location administrators rarely check — before being sent outside.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1003 OS Credential Dumping | คนร้ายใช้เครื่องมือทำ Credential Dumping ดึงค่ารหัสผ่านออกจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่องที่ยึดครองได้ ทั้งแบบรันบนเครื่องนั้นโดยตรงและแบบสั่งดึงจากเครื่องอื่นในเครือข่ายจากระยะไกล | menuPass has used mimikatz.exe to dump credentials locally menuPass has used secretsdump.exe to dump credentials remotely |
| 2 | described | T1569 System Services | คนร้ายอาศัยการสร้างบริการของระบบขึ้นบนเครื่องปลายทางเพื่อสั่งรันคำสั่งจากระยะไกลบนเครื่องนั้น | Using compiled psexec.py to achieve remote code execution |
| 3 | described | T1560 Archive Collected Data | ได้รวบรวมไฟล์ข้อมูลของลูกค้ามาบีบอัดรวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดทั่วไปเพื่อเตรียมนำออก | Compress and stage data for exfiltration |
| 4 | described | T1074 Data Staged | ไฟล์ที่บีบอัดแล้วถูกนำไปพักไว้ในถังขยะของเครื่องซึ่งเป็นตำแหน่งที่ผู้ดูแลระบบมักไม่ตรวจสอบ ก่อนจะถูกส่งออกไปภายนอก | menuPass actors are thought to have staged archives in the Recycle Bin for exfiltration. |

- [ ] ผ่าน / แก้แล้ว

## rcti_034 — menuPass (CTID emulation plan menupass.yaml)

ต้นทาง: <https://recordedfuture.com/apt10-cyberespionage-campaign/>

> เมื่อวันที่ 8 ธันวาคม 2566 บริษัทที่ปรึกษาแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายในถูกบุกรุกและมีการสำรวจเครือข่ายผิดปกติ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายผลักไฟล์เครื่องมือของตนเข้ามาเก็บไว้บนเครื่องที่ยึดครองได้เป็นอันดับแรก ต่อมาปรากฏหลักฐานว่าคนร้ายสั่งแสดงรายการโฟลเดอร์ที่เปิดแบ่งปันไว้บนเครือข่ายภายในทั้งหมด จากนั้นได้ไล่ค้นหารายชื่อเครื่องอื่น ๆ ที่อยู่ในวงเครือข่ายเดียวกัน โดยใช้ทั้งคำสั่งพื้นฐานของระบบและสคริปต์ที่เขียนขึ้นเอง แล้วยังพบว่าคนร้ายทยอยตรวจสอบว่าเครื่องปลายทางแต่ละเครื่องเปิดพอร์ตให้บริการใดไว้บ้าง สุดท้ายพบการสอบถามรายการเครื่องแม่ข่ายที่ทำหน้าที่แปลงชื่อโดเมน และการไล่แจกแจงการเชื่อมต่อที่ค้างอยู่ระหว่างเครื่องในเครือข่าย

*EN:* On 8 December 2566 a consultancy reported that an internal server had been breached and that unusual network reconnaissance was taking place. Digital forensic examination found the offender first pushing their own tool files onto the compromised machine. Evidence then showed the offender listing all folders shared on the internal network, then enumerating the names of other machines in the same network segment using both basic system commands and their own scripts. The offender was also found checking, machine by machine, which service ports each endpoint had open. Finally, queries were found for the list of servers performing domain name resolution, and enumeration of the sessions still open between machines on the network.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1105 Ingress Tool Transfer | คนร้ายผลักไฟล์เครื่องมือของตนเข้ามาเก็บไว้บนเครื่องที่ยึดครองได้เป็นอันดับแรก | Pushing tools to compromised host |
| 2 | described | T1135 Network Share Discovery | คนร้ายสั่งแสดงรายการโฟลเดอร์ที่เปิดแบ่งปันไว้บนเครือข่ายภายในทั้งหมด | Display network shares |
| 3 | described | T1018 Remote System Discovery | ได้ไล่ค้นหารายชื่อเครื่องอื่น ๆ ที่อยู่ในวงเครือข่ายเดียวกัน โดยใช้ทั้งคำสั่งพื้นฐานของระบบและสคริปต์ที่เขียนขึ้นเอง | Identify remote systems using net Identify remote system using Powershell |
| 4 | described | T1046 Network Service Discovery | คนร้ายทยอยตรวจสอบว่าเครื่องปลายทางแต่ละเครื่องเปิดพอร์ตให้บริการใดไว้บ้าง | Enumerate remote hosts for running services using tcping |
| 5 | described | T1016 System Network Configuration Discovery | พบการสอบถามรายการเครื่องแม่ข่ายที่ทำหน้าที่แปลงชื่อโดเมน และการไล่แจกแจงการเชื่อมต่อที่ค้างอยู่ระหว่างเครื่องในเครือข่าย | Scan for nameservers and enumerate NetBIOS sessions |

- [ ] ผ่าน / แก้แล้ว

## rcti_035 — Turla - Snake (CTID emulation plan turla_snake.yaml)

> เมื่อวันที่ 19 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายเก็บไฟล์ถูกบุกรุกและตรวจไม่พบร่องรอยด้วยโปรแกรมป้องกันไวรัสตามปกติ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าโปรแกรมฝังตัวเดิมบนเครื่องได้รับคำสั่งให้ดาวน์โหลดตัวติดตั้งของโปรแกรมฝังตัวชุดใหม่เข้ามาไว้บนเครื่อง ต่อมาปรากฏหลักฐานว่าคนร้ายสั่งรันตัวติดตั้งดังกล่าวพร้อมตัวเลือกยกระดับสิทธิ์ ทำให้ได้โปรแกรมที่ฝังตัวลึกในระดับแกนกลางของระบบปฏิบัติการและซ่อนตัวเองจากรายการไฟล์และรายการกระบวนการปกติ จากนั้นโปรแกรมดังกล่าวได้รับคำสั่งให้ไล่แจกแจงรายการกระบวนการที่ทำงานอยู่บนเครื่อง แล้วสั่งตรวจสอบว่าบัญชีผู้ใช้ที่ใช้อยู่เป็นสมาชิกกลุ่มผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์ในโดเมนหรือไม่ สุดท้ายพบการสั่งแจกแจงรายการเชื่อมต่อเครือข่ายที่ค้างอยู่ไปยังไดรฟ์ที่เชื่อมกับเครื่องแม่ข่ายเก็บไฟล์นั้น

*EN:* On 19 September 2566 a government agency reported that its file server had been breached and that ordinary antivirus software found no trace. Digital forensic examination found that an existing implant on the machine received a command to download the installer of a new implant onto the machine. Evidence then showed the offender running that installer with a privilege escalation option, producing a program embedded deep at the operating system's core level that hid itself from ordinary file and process listings. That program then received a command to enumerate the processes running on the machine, and to check whether the account in use belonged to the domain group administering the file server. Finally, enumeration was found of the open network connections to the drive mapped to that file server.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1105 Ingress Tool Transfer | โปรแกรมฝังตัวเดิมบนเครื่องได้รับคำสั่งให้ดาวน์โหลดตัวติดตั้งของโปรแกรมฝังตัวชุดใหม่เข้ามาไว้บนเครื่อง | Task the EPIC implant to download the Snake rootkit installer. |
| 2 | described | T1014 Rootkit | คนร้ายสั่งรันตัวติดตั้งดังกล่าวพร้อมตัวเลือกยกระดับสิทธิ์ ทำให้ได้โปรแกรมที่ฝังตัวลึกในระดับแกนกลางของระบบปฏิบัติการและซ่อนตัวเองจากรายการไฟล์และรายการกระบวนการปกติ | Task the EPIC implant to execute the Snake rootkit installer with the privilege escalation option |
| 3 | described | T1057 Process Discovery | โปรแกรมดังกล่าวได้รับคำสั่งให้ไล่แจกแจงรายการกระบวนการที่ทำงานอยู่บนเครื่อง | Task the Snake rootkit to run the process discovery command. |
| 4 | described | T1087 Account Discovery | สั่งตรวจสอบว่าบัญชีผู้ใช้ที่ใช้อยู่เป็นสมาชิกกลุ่มผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์ในโดเมนหรือไม่ | Execute the discovery command to confirm the user is in the file server admin's groups. |
| 5 | described | T1049 System Network Connections Discovery | พบการสั่งแจกแจงรายการเชื่อมต่อเครือข่ายที่ค้างอยู่ไปยังไดรฟ์ที่เชื่อมกับเครื่องแม่ข่ายเก็บไฟล์นั้น | Execute the discovery command to the drive mapped to the file server. |

- [ ] ผ่าน / แก้แล้ว

## rcti_036 — CISA AA22-055A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-055a>

> เมื่อวันที่ 22 กุมภาพันธ์ 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ถูกหลอกให้เปิดไฟล์เอกสารอันตราย จากการตรวจสอบพบว่าคนร้ายส่งจดหมายอิเล็กทรอนิกส์แนบไฟล์เอกสารที่จัดทำขึ้นเจาะจงถึงเจ้าหน้าที่รายนั้นโดยเฉพาะ เพื่อกระจายโปรแกรมไม่พึงประสงค์เข้าสู่เครือข่ายขององค์กร ต่อมาปรากฏหลักฐานว่าเมื่อผู้เสียหายเปิดไฟล์ตารางคำนวณที่แนบมา ระบบได้แสดงข้อความให้ผู้ใช้กดอนุญาตให้ชุดคำสั่งมาโครทำงาน ซึ่งผู้เสียหายได้กดยืนยันไป ทำให้ชุดคำสั่งดังกล่าวเริ่มทำงานบนเครื่อง สุดท้ายจากการตรวจสอบพบว่าไฟล์สคริปต์ที่ถูกวางลงมาถูกนำไปติดตั้งไว้ในโฟลเดอร์เริ่มต้นระบบของบัญชีผู้ใช้ที่ใช้งานอยู่ เพื่อให้ถูกเรียกทำงานอีกครั้งทุกครั้งที่ผู้ใช้ล็อกอินเข้าเครื่อง

*EN:* On 22 February 2565 an agency reported that an officer had been tricked into opening a malicious document file. Examination found the offender sending an email with a document attachment prepared specifically for that officer in order to spread an unwanted program into the organisation's network. Evidence then showed that when the victim opened the attached spreadsheet file, the system displayed a prompt asking the user to allow macro instructions to run, which the victim confirmed, causing those instructions to start running on the machine. Finally the dropped script file was found installed in the startup folder of the account in use, so that it would be run again every time the user logged in.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1566 Phishing | คนร้ายส่งจดหมายอิเล็กทรอนิกส์แนบไฟล์เอกสารที่จัดทำขึ้นเจาะจงถึงเจ้าหน้าที่รายนั้นโดยเฉพาะ เพื่อกระจายโปรแกรมไม่พึงประสงค์เข้าสู่เครือข่ายขององค์กร | MuddyWater also uses Canopy/Starwhale malware, likely distributed via spearphishing emails with targeted attachments |
| 2 | described | T1204 User Execution | เมื่อผู้เสียหายเปิดไฟล์ตารางคำนวณที่แนบมา ระบบได้แสดงข้อความให้ผู้ใช้กดอนุญาตให้ชุดคำสั่งมาโครทำงาน ซึ่งผู้เสียหายได้กดยืนยันไป ทำให้ชุดคำสั่งดังกล่าวเริ่มทำงานบนเครื่อง | When the victim opens the Excel file, they receive a prompt to enable macros |
| 3 | described | T1547 Boot or Logon Autostart Execution | ไฟล์สคริปต์ที่ถูกวางลงมาถูกนำไปติดตั้งไว้ในโฟลเดอร์เริ่มต้นระบบของบัญชีผู้ใช้ที่ใช้งานอยู่ เพื่อให้ถูกเรียกทำงานอีกครั้งทุกครั้งที่ผู้ใช้ล็อกอินเข้าเครื่อง | The first .wsf is installed in the current user startup folder for persistence |

- [ ] ผ่าน / แก้แล้ว

## rcti_037 — Sandworm Team (G0034) (CTID emulation plan sandworm.yaml)

ต้นทาง: <https://www.justice.gov/opa/press-release/file/1328521/download>

> เมื่อวันที่ 27 มิถุนายน 2567 บริษัทโลจิสติกส์ข้ามชาติสาขาประเทศไทยแจ้งความว่าเครื่องคอมพิวเตอร์ทั่วทั้งองค์กรถูกทำให้ใช้งานไม่ได้พร้อมกัน จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายเปิดการเชื่อมต่อหน้าจอระยะไกลจากเครื่องภายนอกเข้ามายังเครื่องแม่ข่ายควบคุมโดเมนขององค์กร ต่อมาปรากฏหลักฐานว่าคนร้ายดาวน์โหลดไฟล์โปรแกรมชุดใหม่เข้ามาไว้บนเครื่องแม่ข่ายควบคุมโดเมนแล้วสั่งให้ทำงานผ่านการเชื่อมต่อดังกล่าว จากนั้นโปรแกรมที่ถูกเรียกทำงานได้สร้างงานตั้งเวลาสำหรับรีสตาร์ตเครื่อง เข้ารหัสลับไฟล์ทั้งหมดในโฟลเดอร์ผู้ใช้ วางไฟล์ข้อความเรียกค่าไถ่ไว้ที่ไดรฟ์หลัก และคัดลอกตัวเองไปทำงานต่อบนเครื่องอื่นในเครือข่าย สุดท้ายเมื่อดำเนินการเสร็จ พบว่าคนร้ายปิดการเชื่อมต่อหน้าจอระยะไกลที่เปิดค้างไว้กับเครื่องแม่ข่ายควบคุมโดเมนลง

*EN:* On 27 June 2567 the Thai branch of a multinational logistics company reported that computers across the whole organisation had been disabled simultaneously. Digital forensic examination found the offender opening a remote screen connection from an external machine to the organisation's domain controller. Evidence then showed the offender downloading a new program file onto the domain controller and running it over that connection. The program then created a timed task to restart the machine, encrypted all files in the user folders, dropped a ransom text file on the main drive and copied itself to run on other machines on the network. Finally, on completion, the offender was found closing the remote screen connection left open to the domain controller.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1021 Remote Services | คนร้ายเปิดการเชื่อมต่อหน้าจอระยะไกลจากเครื่องภายนอกเข้ามายังเครื่องแม่ข่ายควบคุมโดเมนขององค์กร | This ability must be run by an agent running on the attacker-controlled machine (e.g. on the C2 server itself), since the RDP connection must originate from the attacker's machine. |
| 2 | described | T1105 Ingress Tool Transfer | คนร้ายดาวน์โหลดไฟล์โปรแกรมชุดใหม่เข้ามาไว้บนเครื่องแม่ข่ายควบคุมโดเมนแล้วสั่งให้ทำงานผ่านการเชื่อมต่อดังกล่าว | Downloads a new agent executable and executes it on the domain controller over RDP. This ability must be run by an agent running on the attacker-controlled Linux machine (e.g. on the C2 server itself), since the RDP conn… |
| 3 | described | T1486 Data Encrypted for Impact | โปรแกรมที่ถูกเรียกทำงานได้สร้างงานตั้งเวลาสำหรับรีสตาร์ตเครื่อง เข้ารหัสลับไฟล์ทั้งหมดในโฟลเดอร์ผู้ใช้ วางไฟล์ข้อความเรียกค่าไถ่ไว้ที่ไดรฟ์หลัก และคัดลอกตัวเองไปทำงานต่อบนเครื่องอื่นในเครือข่าย | Sandworm executes NotPetya (perfc.dat). NotPetya creates a scheduled task called "Restart" that reboots the workstation and is executed at the end of the program. NotPetya encrypts files under C:\Users (recursive) via AE… |
| 4 | described | T1021 Remote Services | คนร้ายปิดการเชื่อมต่อหน้าจอระยะไกลที่เปิดค้างไว้กับเครื่องแม่ข่ายควบคุมโดเมนลง | End the RDP session to the domain controller. This ability must be run by an agent running on the attacker-controlled machine (e.g. on the C2 server itself), since the RDP connection originates from the attacker's machin… |

- [ ] ผ่าน / แก้แล้ว

## rcti_038 — CISA AA21-048A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-048a>

> เมื่อวันที่ 18 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ระบบปฏิบัติการแมคของตนถูกฝังโปรแกรมไม่พึงประสงค์หลังติดตั้งแอปพลิเคชันซื้อขายที่ดาวน์โหลดมาจากเว็บไซต์ปลอม จากการตรวจสอบพบว่าเนื่องจากบริการเบื้องหลังจะยังไม่เริ่มทำงานทันทีหลังวางไฟล์ตั้งค่าไว้ ชุดคำสั่งหลังการติดตั้งจึงเรียกโปรแกรมของคนร้ายขึ้นมาทำงานเบื้องหลังเองทันที ในลักษณะ Create or Modify System Process: Launch Daemon ต่อมาปรากฏหลักฐานว่าคนร้ายตั้งชื่อไฟล์ให้ขึ้นต้นด้วยจุด ซึ่งเข้าลักษณะ Hide Artifacts: Hidden Files and Directories ทำให้ไฟล์นั้นไม่ปรากฏในหน้าต่างจัดการไฟล์และไม่แสดงในรายการไฟล์ปกติของหน้าต่างคำสั่ง สุดท้ายจากการตรวจสอบไฟล์ที่ถูกดาวน์โหลดตามมาพบว่าเป็นไฟล์โปรแกรมที่ถูกเข้ารหัสลับและอำพรางไว้ ตรงกับลักษณะ Obfuscated Files or Information ซึ่งเมื่อทำงานแล้วจะวางโปรแกรมควบคุมระยะไกลลงบนเครื่องและติดตั้งให้ทำงานเป็นบริการของระบบ

*EN:* On 18 February 2564 a victim reported that their Mac computer had been implanted with an unwanted program after installing a trading application downloaded from a fake website. Examination found that because the background service would not start immediately after the configuration file was placed, the post-installation instructions launched the offender's program in the background at once, in the manner of Create or Modify System Process: Launch Daemon. Evidence then showed the offender naming files with a leading dot, matching Hide Artifacts: Hidden Files and Directories, so that the file did not appear in the file manager window or in the ordinary listing of the command window. Finally the subsequently downloaded file was found to be an encrypted and disguised program file matching Obfuscated Files or Information, which on running dropped a remote control program onto the machine and installed it as a system service.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1543 Create or Modify System Process | ชุดคำสั่งหลังการติดตั้งจึงเรียกโปรแกรมของคนร้ายขึ้นมาทำงานเบื้องหลังเองทันที ในลักษณะ Create or Modify System Process: Launch Daemon | Because the LaunchDaemon will not run automatically after the plist file is moved, the postinstall script launches the Updater program with the CheckUpdate parameter and runs it in the background (Create or Modify System… |
| 2 | named | T1564 Hide Artifacts | คนร้ายตั้งชื่อไฟล์ให้ขึ้นต้นด้วยจุด ซึ่งเข้าลักษณะ Hide Artifacts: Hidden Files and Directories ทำให้ไฟล์นั้นไม่ปรากฏในหน้าต่างจัดการไฟล์และไม่แสดงในรายการไฟล์ปกติของหน้าต่างคำสั่ง | The leading “.” makes it unlisted in the Finder app or default Terminal directory listing (Hide Artifacts: Hidden Files and Directories ) |
| 3 | named | T1027 Obfuscated Files or Information, T1543 Create or Modify System Process | เป็นไฟล์โปรแกรมที่ถูกเข้ารหัสลับและอำพรางไว้ ตรงกับลักษณะ Obfuscated Files or Information ซึ่งเมื่อทำงานแล้วจะวางโปรแกรมควบคุมระยะไกลลงบนเครื่องและติดตั้งให้ทำงานเป็นบริการของระบบ | The cybersecurity company that published the report states the payload was an encrypted and obfuscated binary (Obfuscated Files or Information ), which eventually drops FALLCHILL onto the machine and installs it as a ser… |

- [ ] ผ่าน / แก้แล้ว

## rcti_039 — Turla - Carbon (CTID emulation plan turla_carbon.yaml)

> เมื่อวันที่ 21 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโดเมนขององค์กรถูกยึดครอง จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าโปรแกรมฝังตัวบนเครื่องแม่ข่ายควบคุมโดเมนได้รับคำสั่งให้ดาวน์โหลดและเรียกใช้เครื่องมือทำ Credential Dumping เพื่อดึงค่าความลับของบัญชีผู้ใช้ออกจากฐานข้อมูลความปลอดภัยของระบบ ต่อมาปรากฏหลักฐานว่าโปรแกรมฝังตัวเดียวกันได้รับคำสั่งให้ดาวน์โหลดเครื่องมือสำหรับสั่งงานเครื่องระยะไกล และดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวสำเนาที่สามเข้ามาเก็บไว้บนเครื่อง สุดท้ายพบว่าคนร้ายนำค่าแฮชรหัสผ่านที่ได้มาก่อนหน้าไปยืนยันตัวตนกับเครื่องปลายทางโดยไม่ต้องใช้รหัสผ่านจริง แล้วคัดลอกตัวติดตั้งไปวางบนเครื่องคอมพิวเตอร์ของพนักงานรายหนึ่งพร้อมสั่งให้ทำงานผ่านเครื่องมือสั่งงานระยะไกลนั้น

*EN:* On 21 November 2566 an agency reported that its domain controller had been taken over. Digital forensic examination found that an implant on the domain controller received a command to download and run a Credential Dumping tool in order to pull account secrets out of the system's security database. Evidence then showed the same implant receiving commands to download a remote command tool and to download a third copy of the implant installer onto the machine. Finally the offender was found using the previously obtained password hash to authenticate to a target machine without the real password, then copying the installer onto an employee's computer and running it through that remote command tool.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1003 OS Credential Dumping | โปรแกรมฝังตัวบนเครื่องแม่ข่ายควบคุมโดเมนได้รับคำสั่งให้ดาวน์โหลดและเรียกใช้เครื่องมือทำ Credential Dumping เพื่อดึงค่าความลับของบัญชีผู้ใช้ออกจากฐานข้อมูลความปลอดภัยของระบบ | Task the CARBON-DLL implant on the DC to download and execute mimikatz lsadump |
| 2 | described | T1105 Ingress Tool Transfer | โปรแกรมฝังตัวเดียวกันได้รับคำสั่งให้ดาวน์โหลดเครื่องมือสำหรับสั่งงานเครื่องระยะไกล และดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวสำเนาที่สามเข้ามาเก็บไว้บนเครื่อง | Task the CARBON-DLL implant on the domain controller to download PsExec. Task the CARBON-DLL implant on the domain controller to download a third copy of the CARBON-DLL installer. |
| 3 | described | T1550 Use Alternate Authentication Material | คนร้ายนำค่าแฮชรหัสผ่านที่ได้มาก่อนหน้าไปยืนยันตัวตนกับเครื่องปลายทางโดยไม่ต้องใช้รหัสผ่านจริง | Task the CARBON-DLL implant on the domain controller to use the previously downloaded Mimikatz to pass-the-hash and (1) copy the installer to Adalwolfa's workstation and (2) execute it using PsExec. |

- [ ] ผ่าน / แก้แล้ว

## rcti_040 — CISA AA21-048A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-048a>

> เมื่อวันที่ 19 กุมภาพันธ์ 2564 ผู้เสียหายอีกรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของตนถูกฝังโปรแกรมที่ทำงานเองทุกครั้งที่เปิดเครื่อง จากการตรวจสอบพบว่าโปรแกรมที่ติดตั้งเข้ามาได้สร้างงานตั้งเวลาที่ทำงานด้วยสิทธิ์ระดับระบบขึ้นในเครื่อง ในลักษณะ Scheduled Task/Job: Scheduled Task โดยกำหนดให้เรียกไฟล์ที่อ้างว่าเป็นตัวรายงานข้อผิดพลาดขึ้นมาทำงานทุกครั้งที่มีผู้ใช้รายใดล็อกอิน ต่อมาปรากฏหลักฐานว่าเมื่อโปรแกรมดังกล่าวถูกเรียกทำงาน จะตรวจสอบพารามิเตอร์ที่กำหนดไว้ก่อน แล้วเก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่ล็อกอินอยู่ ตรงกับลักษณะ System Owner/User Discovery จากนั้นเข้ารหัสข้อมูลด้วยกุญแจที่ฝังไว้ในตัวโปรแกรมแล้วส่งออกไปยังเว็บไซต์สั่งการผ่านช่องทางเดิม อันเป็นลักษณะ Exfiltration Over C2 Channel และจากการตรวจสอบโปรแกรมอีกตัวหนึ่งที่ทำงานคู่กันพบพฤติกรรมซ้ำเดิม คือเมื่อพบพารามิเตอร์ที่กำหนด จะรวบรวมข้อมูลประจำเครื่องของผู้เสียหาย เข้ารหัสด้วยกุญแจชุดเดียวกัน แล้วส่งออกไปยังเว็บไซต์สั่งการเดียวกัน

*EN:* On 19 February 2564 another victim reported that their computer had been implanted with a program that ran by itself every time the machine started. Examination found that the installed program created a timed task running with system-level privileges, in the manner of Scheduled Task/Job: Scheduled Task, configured to launch a file claiming to be an error reporter whenever any user logged in. Evidence then showed that when that program ran it first checked a preset parameter, then gathered the machine owner and logged-in username matching System Owner/User Discovery, encrypted the data with a key embedded in the program and sent it out to the command website over the same channel, a case of Exfiltration Over C2 Channel. Examination of a second program running alongside found the same behaviour: on finding its preset parameter it gathered the victim's machine information, encrypted it with the same key and sent it to the same command website.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1053 Scheduled Task/Job | โปรแกรมที่ติดตั้งเข้ามาได้สร้างงานตั้งเวลาที่ทำงานด้วยสิทธิ์ระดับระบบขึ้นในเครื่อง ในลักษณะ Scheduled Task/Job: Scheduled Task โดยกำหนดให้เรียกไฟล์ที่อ้างว่าเป็นตัวรายงานข้อผิดพลาดขึ้นมาทำงานทุกครั้งที่มีผู้ใช้รายใดล็อกอิน | The program also creates a scheduled SYSTEM task, named JMTCrashReporter, which runs CrashReporter.exe with the Maintain parameter at any user’s login (Scheduled Task/Job: Scheduled Task ) |
| 2 | named | T1033 System Owner/User Discovery, T1041 Exfiltration Over C2 Channel | เก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่ล็อกอินอยู่ ตรงกับลักษณะ System Owner/User Discovery จากนั้นเข้ารหัสข้อมูลด้วยกุญแจที่ฝังไว้ในตัวโปรแกรมแล้วส่งออกไปยังเว็บไซต์สั่งการผ่านช่องทางเดิม อันเป็นลักษณะ Exfiltration Over C2 Channel | When run, it checks for the Maintain parameter and collects the victim’s host information (System Owner/User Discovery ), encrypts the collected information with a hardcoded XOR key before exfiltration, and sends the enc… |
| 3 | described | T1033 System Owner/User Discovery, T1041 Exfiltration Over C2 Channel | เมื่อพบพารามิเตอร์ที่กำหนด จะรวบรวมข้อมูลประจำเครื่องของผู้เสียหาย เข้ารหัสด้วยกุญแจชุดเดียวกัน แล้วส่งออกไปยังเว็บไซต์สั่งการเดียวกัน | When it finds the Maintain parameter, it collects the victim’s host information (System Owner/User Discovery ), encrypts the collected information with a hardcoded XOR key before exfiltration, and sends the encrypted inf… |

- [ ] ผ่าน / แก้แล้ว

## rcti_041 — OilRig (CTID emulation plan oilrig.yaml)

> เมื่อวันที่ 11 ตุลาคม 2567 บริษัทวิศวกรรมแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายในถูกใช้เป็นทางผ่านเชื่อมต่อจากภายนอก จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายลบไฟล์โปรแกรมและไฟล์ผลลัพธ์ที่ตนเคยวางไว้ออกจากเครื่องเพื่อเก็บกวาดร่องรอยก่อนดำเนินการขั้นต่อไป ต่อมาปรากฏหลักฐานว่าคนร้ายดาวน์โหลดโปรแกรมเชื่อมต่อระยะไกลขนาดเล็กเข้ามาเก็บไว้บนเครื่อง เพื่อเตรียมเปิดทางเข้าใช้งานหน้าจอระยะไกล สุดท้ายพบว่าคนร้ายสั่งโปรแกรมดังกล่าวทำงานเพื่อห่อหุ้มการเชื่อมต่อหน้าจอระยะไกลไว้ภายในช่องทางเชื่อมต่ออีกชั้นหนึ่ง ทำให้อุปกรณ์ตรวจจับของบริษัทมองเห็นเป็นเพียงการเชื่อมต่อธรรมดาและไม่สามารถแยกแยะได้

*EN:* On 11 October 2567 an engineering company reported that an internal server was being used as a relay for connections from outside. Digital forensic examination found the offender deleting the program and output files they had previously placed on the machine to clean up traces before proceeding. Evidence then showed the offender downloading a small remote connection program onto the machine in preparation for opening remote screen access. Finally the offender was found running that program to wrap the remote screen connection inside another connection channel, so that the company's detection devices saw only an ordinary connection and could not distinguish it.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1070 Indicator Removal | คนร้ายลบไฟล์โปรแกรมและไฟล์ผลลัพธ์ที่ตนเคยวางไว้ออกจากเครื่องเพื่อเก็บกวาดร่องรอยก่อนดำเนินการขั้นต่อไป | Clean up by removing the binary and output file |
| 2 | described | T1105 Ingress Tool Transfer | คนร้ายดาวน์โหลดโปรแกรมเชื่อมต่อระยะไกลขนาดเล็กเข้ามาเก็บไว้บนเครื่อง เพื่อเตรียมเปิดทางเข้าใช้งานหน้าจอระยะไกล | Download Plink in order to gain RDP access |
| 3 | described | T1572 Protocol Tunneling | คนร้ายสั่งโปรแกรมดังกล่าวทำงานเพื่อห่อหุ้มการเชื่อมต่อหน้าจอระยะไกลไว้ภายในช่องทางเชื่อมต่ออีกชั้นหนึ่ง ทำให้อุปกรณ์ตรวจจับของบริษัทมองเห็นเป็นเพียงการเชื่อมต่อธรรมดาและไม่สามารถแยกแยะได้ | Run Plink |

- [ ] ผ่าน / แก้แล้ว

## rcti_042 — Turla - Carbon (CTID emulation plan turla_carbon.yaml)

> เมื่อวันที่ 29 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโดเมนถูกสั่งงานจากระยะไกลโดยไม่ได้รับอนุญาต จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายอาศัยรหัสผ่านของผู้ดูแลโดเมนที่ได้มาก่อนหน้า เข้าไปแก้ไขงานตั้งเวลาที่มีอยู่เดิมบนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล แล้วสั่งให้งานที่แก้ไขแล้วนั้นเริ่มทำงานทันที ต่อมาปรากฏหลักฐานว่าโปรแกรมฝังตัวที่ถูกติดตั้งขึ้นใหม่ได้รับคำสั่งให้แจกแจงรายชื่อสมาชิกของกลุ่มสิทธิ์ในโดเมนหลายกลุ่ม เพื่อดูว่ามีบัญชีใดอยู่ในกลุ่มผู้มีสิทธิ์สูงบ้าง สุดท้ายพบว่าคนร้ายสั่งให้โปรแกรมดังกล่าวไล่แจกแจงรายชื่อเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนอยู่ในระบบทะเบียนโดเมนขององค์กร

*EN:* On 29 November 2566 an agency reported that its domain controller was being commanded remotely without authorisation. Digital forensic examination found the offender using a previously obtained domain administrator password to remotely modify an existing timed task on the domain controller, then starting the modified task immediately. Evidence then showed the newly installed implant receiving a command to enumerate the members of several domain permission groups in order to see which accounts held elevated rights. Finally the offender was found ordering that program to enumerate all computer names registered in the organisation's domain directory.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1053 Scheduled Task/Job | คนร้ายอาศัยรหัสผ่านของผู้ดูแลโดเมนที่ได้มาก่อนหน้า เข้าไปแก้ไขงานตั้งเวลาที่มีอยู่เดิมบนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล แล้วสั่งให้งานที่แก้ไขแล้วนั้นเริ่มทำงานทันที | Task CARBON-DLL to modify a remote scheduled task using the discovered password for the domain admin Task CARBON-DLL to remotely start the modified scheduled task on the domain controller |
| 2 | described | T1069 Permission Groups Discovery | โปรแกรมฝังตัวที่ถูกติดตั้งขึ้นใหม่ได้รับคำสั่งให้แจกแจงรายชื่อสมาชิกของกลุ่มสิทธิ์ในโดเมนหลายกลุ่ม เพื่อดูว่ามีบัญชีใดอยู่ในกลุ่มผู้มีสิทธิ์สูงบ้าง | Task the new CARBON-DLL implant with discovery commands to be run on the domain controller. Task CARBON-DLL to enumerate both groups for their members |
| 3 | described | T1018 Remote System Discovery | คนร้ายสั่งให้โปรแกรมดังกล่าวไล่แจกแจงรายชื่อเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนอยู่ในระบบทะเบียนโดเมนขององค์กร | Task CARBON-DLL to enumerate the Active Directory Computers |

- [ ] ผ่าน / แก้แล้ว

## rcti_043 — CISA AA23-319A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-319a>

> เมื่อวันที่ 15 พฤศจิกายน 2566 มหาวิทยาลัยแห่งหนึ่งแจ้งความว่าระบบสารสนเทศของมหาวิทยาลัยถูกบุกรุกและข้อมูลนักศึกษาถูกเข้ารหัสลับ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายยิงคำสั่งโจมตีช่องโหว่ร้ายแรงของโพรโทคอลยืนยันตัวตนระหว่างเครื่องลูกข่ายกับเครื่องแม่ข่ายควบคุมโดเมน ซึ่งทำให้ยกระดับสิทธิ์ขึ้นเป็นผู้ดูแลระบบได้ ควบคู่กับการส่งอีเมลหลอกลวงถึงบุคลากรจนมีผู้หลงเชื่อ ต่อมาปรากฏหลักฐานว่าคนร้ายนำชื่อผู้ใช้และรหัสผ่านที่ยังใช้งานได้ซึ่งได้มาก่อนหน้า ไปยืนยันตัวตนเข้าสู่จุดเชื่อมต่อเครือข่ายส่วนตัวเสมือนของมหาวิทยาลัย ซึ่งไม่ได้เปิดใช้การยืนยันตัวตนหลายขั้นตอนไว้เป็นค่าเริ่มต้น สุดท้ายจากการตรวจสอบพบว่าคนร้ายอาศัยเครื่องมือที่ติดมากับระบบปฏิบัติการเป็นหลัก โดยเปิดการเชื่อมต่อ Remote Desktop Protocol ไปยังเครื่องอื่นเพื่อขยายการเข้าถึงภายในเครือข่าย เปิดช่องทางเครือข่ายส่วนตัวเสมือนไว้ใช้งานต่อเนื่อง และสั่งงานผ่าน PowerShell

*EN:* On 15 November 2566 a university reported that its information systems had been breached and student data encrypted. Digital forensic examination found the offender firing attack commands at a critical vulnerability in the authentication protocol between clients and the domain controller, which allowed privileges to be raised to administrator, alongside sending phishing emails to staff until someone was taken in. Evidence then showed the offender using still-valid usernames and passwords obtained earlier to authenticate into the university's virtual private network access point, which did not have multi-factor authentication enabled by default. Finally the offender was found relying mainly on tools shipped with the operating system, opening Remote Desktop Protocol connections to other machines to widen access inside the network, keeping a virtual private network channel open for continued use, and issuing commands through PowerShell.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1190 Exploit Public-Facing Application, T1566 Phishing | คนร้ายยิงคำสั่งโจมตีช่องโหว่ร้ายแรงของโพรโทคอลยืนยันตัวตนระหว่างเครื่องลูกข่ายกับเครื่องแม่ข่ายควบคุมโดเมน ซึ่งทำให้ยกระดับสิทธิ์ขึ้นเป็นผู้ดูแลระบบได้ ควบคู่กับการส่งอีเมลหลอกลวงถึงบุคลากรจนมีผู้หลงเชื่อ | Additionally, actors have been observed exploiting Zerologon (CVE-2020-1472)—a critical elevation of privileges vulnerability in Microsoft’s Netlogon Remote Protocol —as well as conducting successful phishing attempts |
| 2 | described | T1078 Valid Accounts | คนร้ายนำชื่อผู้ใช้และรหัสผ่านที่ยังใช้งานได้ซึ่งได้มาก่อนหน้า ไปยืนยันตัวตนเข้าสู่จุดเชื่อมต่อเครือข่ายส่วนตัวเสมือนของมหาวิทยาลัย ซึ่งไม่ได้เปิดใช้การยืนยันตัวตนหลายขั้นตอนไว้เป็นค่าเริ่มต้น | Rhysida actors have commonly been observed authenticating to internal VPN access points with compromised valid credentials , notably due to organizations lacking MFA enabled by default |
| 3 | named | T1021 Remote Services, T1059 Command and Scripting Interpreter | คนร้ายอาศัยเครื่องมือที่ติดมากับระบบปฏิบัติการเป็นหลัก โดยเปิดการเชื่อมต่อ Remote Desktop Protocol ไปยังเครื่องอื่นเพื่อขยายการเข้าถึงภายในเครือข่าย เปิดช่องทางเครือข่ายส่วนตัวเสมือนไว้ใช้งานต่อเนื่อง และสั่งงานผ่าน PowerShell | Analysis identified Rhysida actors using living off the land techniques, such as creating Remote Desktop Protocol (RDP) connections for lateral movement , establishing VPN access, and utilizing PowerShell |

- [ ] ผ่าน / แก้แล้ว

## rcti_044 — CISA AA23-352A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-352a>

> เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความว่าข้อมูลลูกค้าถูกนำออกไปและระบบงานถูกเข้ารหัสลับจนใช้การไม่ได้ จากการตรวจสอบปริมาณข้อมูลขาออกพบว่าคนร้ายใช้โปรแกรมรับส่งไฟล์ลำเลียงข้อมูลจากเครือข่ายของผู้เสียหายออกไปเก็บไว้ยังบัญชีปลายทางที่คนร้ายควบคุมอยู่ ต่อมาเมื่อนำข้อมูลออกไปเรียบร้อยแล้ว ปรากฏหลักฐานว่าไฟล์ในระบบถูกเข้ารหัสลับด้วยวิธีผสมระหว่างการเข้ารหัสแบบสมมาตรและแบบกุญแจสาธารณะ โดยเลือกเข้ารหัสเพียงบางช่วงของไฟล์สลับกันไปเพื่อให้ทำงานได้เร็วขึ้นและตรวจจับได้ยากขึ้น สุดท้ายพบว่าคนร้ายใช้วิธีข่มขู่สองชั้น คือนอกจากเข้ารหัสลับระบบจนใช้งานไม่ได้แล้ว ยังขู่จะเปิดเผยข้อมูลที่นำออกไปต่อสาธารณะหากผู้เสียหายไม่ยอมจ่ายเงิน

*EN:* On 18 December 2566 a retail company reported that customer data had been taken out and its systems encrypted until unusable. Examination of outbound traffic found the offender using a file transfer program to move data from the victim's network out to a destination account under the offender's control. Once the data had been taken out, evidence showed files in the system encrypted with a method combining symmetric and public-key encryption, encrypting only alternating portions of each file to work faster and be harder to detect. Finally the offender was found using double extortion: beyond encrypting the systems until unusable, they also threatened to publish the extracted data if the victim did not pay.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1048 Exfiltration Over Alternative Protocol | คนร้ายใช้โปรแกรมรับส่งไฟล์ลำเลียงข้อมูลจากเครือข่ายของผู้เสียหายออกไปเก็บไว้ยังบัญชีปลายทางที่คนร้ายควบคุมอยู่ | Play ransomware actors have used it to transfer data from a compromised network to actor-controlled accounts |
| 2 | described | T1486 Data Encrypted for Impact | ไฟล์ในระบบถูกเข้ารหัสลับด้วยวิธีผสมระหว่างการเข้ารหัสแบบสมมาตรและแบบกุญแจสาธารณะ โดยเลือกเข้ารหัสเพียงบางช่วงของไฟล์สลับกันไปเพื่อให้ทำงานได้เร็วขึ้นและตรวจจับได้ยากขึ้น | Following exfiltration, files are encrypted with AES-RSA hybrid encryption using intermittent encryption, encrypting every other file portion of 0x100000 bytes |
| 3 | described | T1657 Financial Theft | คนร้ายใช้วิธีข่มขู่สองชั้น คือนอกจากเข้ารหัสลับระบบจนใช้งานไม่ได้แล้ว ยังขู่จะเปิดเผยข้อมูลที่นำออกไปต่อสาธารณะหากผู้เสียหายไม่ยอมจ่ายเงิน | The Play ransomware group uses a double-extortion model , encrypting systems after exfiltrating data |

- [ ] ผ่าน / แก้แล้ว

## rcti_045 — CISA AA20-336A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-336a>

> เมื่อวันที่ 1 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าแม้จะล้างเครื่องและติดตั้งโปรแกรมป้องกันใหม่แล้ว โปรแกรมของคนร้ายก็ยังกลับมาทำงานได้อีกทุกครั้ง จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายวางกลไกให้ตัวเองกลับมาทำงานไว้หลายชั้นซ้อนกัน ชั้นแรกคือการกำหนดสคริปต์ให้ระบบเรียกทำงานอัตโนมัติทุกครั้งที่ผู้ใช้ล็อกอินเข้าสู่ระบบ ชั้นที่สองพบว่าคนร้ายลงทะเบียนการสมัครรับเหตุการณ์ไว้กับกลไกบริหารจัดการเครื่องของวินโดวส์ โดยผูกไว้กับเงื่อนไขเวลาหนึ่ง เมื่อเงื่อนไขนั้นเกิดขึ้นระบบจะเรียกคำสั่งของคนร้ายขึ้นมาทำงานเองโดยไม่ต้องมีไฟล์โปรแกรมค้างอยู่บนดิสก์ และชั้นสุดท้ายพบการเพิ่มรายการเรียกใช้งานไว้ในทะเบียนระบบและในโฟลเดอร์เริ่มต้นระบบ เพื่อให้โปรแกรมถูกเรียกขึ้นมาอีกครั้งทุกครั้งที่เปิดเครื่อง

*EN:* On 1 December 2563 an agency reported that even after wiping machines and installing fresh protection software, the offender's program returned every time. Digital forensic examination found the offender had laid down several overlapping mechanisms for coming back. The first was configuring a script for the system to run automatically whenever a user logged in. The second was registering an event subscription with the Windows machine management mechanism, bound to a timing condition; when that condition occurred the system would run the offender's commands by itself without any program file left on disk. The last was adding launch entries to the system registry and the startup folder so the program would be started again every time the machine was switched on.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1037 Boot or Logon Initialization Scripts | ชั้นแรกคือการกำหนดสคริปต์ให้ระบบเรียกทำงานอัตโนมัติทุกครั้งที่ผู้ใช้ล็อกอินเข้าสู่ระบบ | Boot or Logon Initialization Scripts: Logon Script (Windows) |
| 2 | described | T1546 Event Triggered Execution | คนร้ายลงทะเบียนการสมัครรับเหตุการณ์ไว้กับกลไกบริหารจัดการเครื่องของวินโดวส์ โดยผูกไว้กับเงื่อนไขเวลาหนึ่ง เมื่อเงื่อนไขนั้นเกิดขึ้นระบบจะเรียกคำสั่งของคนร้ายขึ้นมาทำงานเองโดยไม่ต้องมีไฟล์โปรแกรมค้างอยู่บนดิสก์ | Event Triggered Execution: Windows Management Instrumentation Event Subscription |
| 3 | described | T1547 Boot or Logon Autostart Execution | พบการเพิ่มรายการเรียกใช้งานไว้ในทะเบียนระบบและในโฟลเดอร์เริ่มต้นระบบ เพื่อให้โปรแกรมถูกเรียกขึ้นมาอีกครั้งทุกครั้งที่เปิดเครื่อง | Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder |

- [ ] ผ่าน / แก้แล้ว

## rcti_046 — CISA AA22-174A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-174a>

> เมื่อวันที่ 23 มิถุนายน 2565 บริษัทเทคโนโลยีแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายของบริษัทถูกฝังโปรแกรมควบคุมระยะไกล จากการตรวจสอบพบว่าเมื่อไฟล์โปรแกรมของคนร้ายถูกเรียกทำงานครั้งแรก โปรแกรมได้สร้าง Scheduled Task ขึ้นในระบบโดยตั้งชื่อให้ดูเหมือนงานปรับปรุงเซสชันของวินโดวส์ และกำหนดให้เรียกโปรแกรมของคนร้ายทำงานซ้ำทุกหนึ่งชั่วโมง ต่อมาปรากฏหลักฐานว่าโปรแกรมดังกล่าวยังทำหน้าที่เป็นจุดพักส่งต่อการเชื่อมต่อให้คนร้ายที่อยู่ภายนอก สามารถกระโดดผ่านเครื่องนี้เข้าไปยังเครื่องอื่นและเจาะลึกเข้าไปในเครือข่ายภายในได้ สุดท้ายจากการตรวจสอบข้อมูลที่รับส่งพบว่าการติดต่อทั้งขาเข้าและขาออกของโปรแกรมถูกแปลงด้วยกุญแจลับขนาดหนึ่งร้อยยี่สิบแปดบิตทุกครั้ง ทำให้อุปกรณ์ตรวจจับของบริษัทไม่สามารถอ่านเนื้อหาได้

*EN:* On 23 June 2565 a technology company reported that its server had been implanted with a remote control program. Examination found that when the offender's program file was first run, it created a Scheduled Task in the system named to look like a Windows session update job, configured to run the offender's program again every hour. Evidence then showed that program also acting as a relay point, allowing the offender outside to hop through this machine to others and push deeper into the internal network. Finally, examination of the exchanged data found the program's inbound and outbound communications always transformed with a 128-bit secret key, leaving the company's detection devices unable to read the content.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1053 Scheduled Task/Job | โปรแกรมได้สร้าง Scheduled Task ขึ้นในระบบโดยตั้งชื่อให้ดูเหมือนงานปรับปรุงเซสชันของวินโดวส์ และกำหนดให้เรียกโปรแกรมของคนร้ายทำงานซ้ำทุกหนึ่งชั่วโมง | When first executed, hmsvc.exe creates the Scheduled Task , C:\Windows\System32\Tasks\Local Session Updater, which executes malware every hour |
| 2 | described | T1090 Proxy | โปรแกรมดังกล่าวยังทำหน้าที่เป็นจุดพักส่งต่อการเชื่อมต่อให้คนร้ายที่อยู่ภายนอก สามารถกระโดดผ่านเครื่องนี้เข้าไปยังเครื่องอื่นและเจาะลึกเข้าไปในเครือข่ายภายในได้ | The malware can function as a C2 tunneling proxy , allowing a remote operator to pivot to other systems and move further into a network |
| 3 | described | T1573 Encrypted Channel | การติดต่อทั้งขาเข้าและขาออกของโปรแกรมถูกแปลงด้วยกุญแจลับขนาดหนึ่งร้อยยี่สิบแปดบิตทุกครั้ง ทำให้อุปกรณ์ตรวจจับของบริษัทไม่สามารถอ่านเนื้อหาได้ | The executable’s inbound and outbound communications are encrypted with a 128-bit key |

- [ ] ผ่าน / แก้แล้ว

## rcti_047 — OilRig (CTID emulation plan oilrig.yaml)

> เมื่อวันที่ 9 กรกฎาคม 2567 บริษัทปิโตรเคมีแห่งหนึ่งในจังหวัดระยองแจ้งความว่าเครื่องคอมพิวเตอร์ในสำนักงานถูกฝังโปรแกรมสำรวจข้อมูล จากการตรวจสอบพฤติกรรมของโปรแกรมพบว่าโปรแกรมเรียกดูชื่อเครื่องของผู้เสียหายเป็นอันดับแรก ต่อมาได้เรียกดูชื่อบัญชีผู้ใช้ที่กำลังใช้งานอยู่ในขณะนั้น จากนั้นเมื่อคนร้ายเข้าถึงเครื่องเป้าหมายอีกเครื่องหนึ่งได้ พบว่ามีการเรียกดูชื่อของเครื่องนั้นซ้ำอีกครั้งเพื่อยืนยันว่าอยู่บนเครื่องใด ต่อมาปรากฏหลักฐานว่าโปรแกรมเรียกดูรายละเอียดการตั้งค่าเครือข่ายของเครื่อง ทั้งหมายเลขไอพี เกตเวย์ และเครื่องแม่ข่ายแปลงชื่อโดเมนที่ใช้ จากนั้นคนร้ายใช้คำสั่งพื้นฐานของระบบผ่านหน้าต่างคำสั่งเพื่อแจกแจงรายชื่อบัญชีผู้ใช้ทั้งหมดในโดเมนขององค์กร แล้วยังแจกแจงรายชื่อกลุ่มสิทธิ์ในโดเมนโดยเจาะจงดูสมาชิกของกลุ่มผู้ดูแลโดเมนและกลุ่มที่ดูแลระบบจดหมายอิเล็กทรอนิกส์ สุดท้ายพบว่าคนร้ายเรียกดูนโยบายการตั้งรหัสผ่านของโดเมน เพื่อดูว่ากำหนดความยาวขั้นต่ำและจำนวนครั้งที่ยอมให้ล็อกอินผิดไว้เท่าใด

*EN:* On 9 July 2567 a petrochemical company in Rayong province reported that office computers had been implanted with a reconnaissance program. Examination of the program's behaviour found it first reading the victim's machine name, then reading the name of the account currently in use. When the offender reached a second target machine, the machine name was read again to confirm which machine they were on. Evidence then showed the program reading the machine's network configuration details — IP address, gateway and the domain name servers in use. The offender then used basic system commands through the command window to enumerate all user accounts in the organisation's domain, and further enumerated domain permission groups, specifically inspecting the members of the domain administrators group and the group administering the mail system. Finally the offender was found reading the domain's password policy to see what minimum length and permitted number of failed logins were set.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1082 System Information Discovery | โปรแกรมเรียกดูชื่อเครื่องของผู้เสียหายเป็นอันดับแรก | Executes the payload to collect the hostname of the victim machine. |
| 2 | described | T1033 System Owner/User Discovery | ได้เรียกดูชื่อบัญชีผู้ใช้ที่กำลังใช้งานอยู่ในขณะนั้น | Executes the payload to collect the username of the victim machine. Obtain user from current session |
| 3 | described | T1082 System Information Discovery | มีการเรียกดูชื่อของเครื่องนั้นซ้ำอีกครั้งเพื่อยืนยันว่าอยู่บนเครื่องใด | Find the hostname |
| 4 | described | T1016 System Network Configuration Discovery | โปรแกรมเรียกดูรายละเอียดการตั้งค่าเครือข่ายของเครื่อง ทั้งหมายเลขไอพี เกตเวย์ และเครื่องแม่ข่ายแปลงชื่อโดเมนที่ใช้ | View network configuration information for host |
| 5 | described | T1087 Account Discovery | คนร้ายใช้คำสั่งพื้นฐานของระบบผ่านหน้าต่างคำสั่งเพื่อแจกแจงรายชื่อบัญชีผู้ใช้ทั้งหมดในโดเมนขององค์กร | The net utility is executed via cmd to enumerate domain user accounts. |
| 6 | described | T1069 Permission Groups Discovery | แจกแจงรายชื่อกลุ่มสิทธิ์ในโดเมนโดยเจาะจงดูสมาชิกของกลุ่มผู้ดูแลโดเมนและกลุ่มที่ดูแลระบบจดหมายอิเล็กทรอนิกส์ | The net utility is executed via cmd to enumerate group accounts. The net utility is executed via cmd to enumerate the "domain admins" group The net utility is executed via cmd to enumerate the "Exchange Trusted Subsystem… |
| 7 | described | T1201 Password Policy Discovery | คนร้ายเรียกดูนโยบายการตั้งรหัสผ่านของโดเมน เพื่อดูว่ากำหนดความยาวขั้นต่ำและจำนวนครั้งที่ยอมให้ล็อกอินผิดไว้เท่าใด | View domain account settings and password policy |

- [ ] ผ่าน / แก้แล้ว

## rcti_048 — APT29 (CTID emulation plan APT29.yaml)

ต้นทาง: <https://blog-assets.f-secure.com/wp-content/uploads/2019/10/15163405/CosmicDuke.pdf>

> เมื่อวันที่ 20 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่เปิดไฟล์แนบแล้วเครื่องถูกยึดครอง จากการตรวจสอบพบว่าคนร้ายตั้งชื่อไฟล์โดยแทรกอักขระพิเศษที่สั่งให้ระบบแสดงตัวอักษรกลับด้าน ทำให้ผู้ใช้มองเห็นนามสกุลไฟล์เป็นไฟล์เอกสารทั้งที่ความจริงเป็นไฟล์โปรแกรมที่รันได้ ต่อมาปรากฏหลักฐานว่าเมื่อไฟล์ดังกล่าวถูกเปิด ได้มีการเรียกโปรแกรม PowerShell ขึ้นมาทำงานต่อจากหน้าต่างคำสั่งของระบบ สุดท้ายพบว่าคนร้ายสั่งงานผ่านหน้าต่างคำสั่งอีกครั้งเพื่อให้สคริปต์ไล่เก็บรวบรวมไฟล์ในเครื่องที่มีนามสกุลตามที่กำหนดไว้โดยอัตโนมัติ แล้วบีบอัดรวมไว้เป็นไฟล์เดียวเพื่อเตรียมนำออก

*EN:* On 20 February 2567 a foreign affairs agency reported that an officer opened an attachment and the machine was taken over. Examination found the offender naming the file with a special character inserted that instructs the system to display text reversed, so the user saw a document file extension when it was in fact an executable program file. Evidence then showed that when the file was opened, PowerShell was launched from the system command window. Finally the offender was found issuing commands through the command window again so that a script automatically gathered files on the machine matching specified extensions and compressed them into a single file ready to be taken out.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1036 Masquerading | คนร้ายตั้งชื่อไฟล์โดยแทรกอักขระพิเศษที่สั่งให้ระบบแสดงตัวอักษรกลับด้าน ทำให้ผู้ใช้มองเห็นนามสกุลไฟล์เป็นไฟล์เอกสารทั้งที่ความจริงเป็นไฟล์โปรแกรมที่รันได้ | Perform RTLO technique with SANDCAT |
| 2 | named | T1059 Command and Scripting Interpreter | ได้มีการเรียกโปรแกรม PowerShell ขึ้นมาทำงานต่อจากหน้าต่างคำสั่งของระบบ | Spawn powershell.exe from cmd.exe |
| 3 | described | T1119 Automated Collection | คนร้ายสั่งงานผ่านหน้าต่างคำสั่งอีกครั้งเพื่อให้สคริปต์ไล่เก็บรวบรวมไฟล์ในเครื่องที่มีนามสกุลตามที่กำหนดไว้โดยอัตโนมัติ แล้วบีบอัดรวมไว้เป็นไฟล์เดียวเพื่อเตรียมนำออก | Execute PowerShell from cmd.exe to collect and compress files of specific extensions. |

- [ ] ผ่าน / แก้แล้ว

## rcti_049 — Carbanak (CTID emulation plan Carbanak.yaml)

ต้นทาง: <https://securelist.com/the-great-bank-robbery-the-carbanak-apt/68732/>

> เมื่อวันที่ 6 มิถุนายน 2567 บริษัทมหาชนแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของผู้บริหารฝ่ายการเงินถูกลักลอบเข้าถึง จากการตรวจสอบทะเบียนระบบพบว่ามีการเพิ่มรายการเรียกใช้งานสคริปต์ของคนร้ายไว้ในทะเบียนระบบของบัญชีผู้บริหารรายนั้น เพื่อให้สคริปต์ถูกเรียกทำงานทุกครั้งที่เจ้าตัวล็อกอินเข้าเครื่อง ต่อมาปรากฏหลักฐานว่าคนร้ายอัปโหลดโปรแกรมดักบันทึกแป้นพิมพ์ขึ้นไปบนเครื่องแล้วสั่งให้ทำงานภายใต้สิทธิ์ของผู้บริหารรายนั้น พร้อมทั้งเปิดอ่านไฟล์ผลลัพธ์ที่โปรแกรมบันทึกไว้ จากนั้นยังพบว่าคนร้ายอัปโหลดโปรแกรมอีกตัวหนึ่งขึ้นไปทำงานเพื่อดึงชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บบันทึกไว้ในเครื่องออกมา สุดท้ายเมื่อได้ข้อมูลที่ต้องการแล้ว พบว่าคนร้ายสั่งหยุดโปรแกรมดักบันทึกแป้นพิมพ์และลบไฟล์ที่เกี่ยวข้องในโฟลเดอร์ไฟล์ชั่วคราวทิ้งทั้งหมด

*EN:* On 6 June 2567 a public company reported that the computer of its chief financial officer had been covertly accessed. Examination of the system registry found an entry added to launch the offender's script under that executive's account so it would run every time they logged in. Evidence then showed the offender uploading a keystroke-logging program to the machine and running it under that executive's privileges, and reading the output file the program recorded. The offender was also found uploading a second program to extract the usernames and passwords the web browser had saved on the machine. Finally, having obtained what they wanted, the offender was found stopping the keystroke-logging program and deleting all related files from the temporary file folder.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1547 Boot or Logon Autostart Execution | มีการเพิ่มรายการเรียกใช้งานสคริปต์ของคนร้ายไว้ในทะเบียนระบบของบัญชีผู้บริหารรายนั้น เพื่อให้สคริปต์ถูกเรียกทำงานทุกครั้งที่เจ้าตัวล็อกอินเข้าเครื่อง | Set Registry Persistence on CFO to run Java-Update.vbs when the CFO user logs in |
| 2 | described | T1056 Input Capture | คนร้ายอัปโหลดโปรแกรมดักบันทึกแป้นพิมพ์ขึ้นไปบนเครื่องแล้วสั่งให้ทำงานภายใต้สิทธิ์ของผู้บริหารรายนั้น พร้อมทั้งเปิดอ่านไฟล์ผลลัพธ์ที่โปรแกรมบันทึกไว้ | Upload and Execute Keylogger on CFO as CFO Read contents of keylogger output file |
| 3 | described | T1555 Credentials from Password Stores | คนร้ายอัปโหลดโปรแกรมอีกตัวหนึ่งขึ้นไปทำงานเพื่อดึงชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บบันทึกไว้ในเครื่องออกมา | Upload and Execute Web Cred Dumper on CFO as CFO |
| 4 | described | T1070 Indicator Removal | คนร้ายสั่งหยุดโปรแกรมดักบันทึกแป้นพิมพ์และลบไฟล์ที่เกี่ยวข้องในโฟลเดอร์ไฟล์ชั่วคราวทิ้งทั้งหมด | Stop Keylogger and clean artifacts in TEMP directory |

- [ ] ผ่าน / แก้แล้ว

## rcti_050 — CISA AA23-158A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-158a>

> เมื่อวันที่ 2 มิถุนายน 2566 บริษัทแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กรติดโปรแกรมไม่พึงประสงค์และแพร่กระจายต่อไปยังเครื่องอื่น จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าโปรแกรมที่ฝังอยู่ทำหน้าที่เป็นประตูหลัง เปิดทางให้คนร้ายส่งคำสั่งอื่น ๆ เข้ามาสั่งงานบนเครื่องที่ยึดครองได้ตามต้องการ ต่อมาปรากฏหลักฐานว่าโปรแกรมควบคุมระยะไกลอีกตัวหนึ่งบนเครื่องเดียวกันได้เก็บรวบรวมข้อมูลของเครื่องแล้วพยายามติดต่อกลับไปยังเครื่องสั่งการของคนร้าย เพื่อขอดาวน์โหลดส่วนประกอบเพิ่มเติมของโปรแกรมอันตรายเข้ามาติดตั้งต่อ สุดท้ายพบว่าโปรแกรมประตูหลังยังแพร่กระจายตัวเองต่อไปโดยอาศัยช่องโหว่ของเครื่องอื่น และคัดลอกสำเนาของตนเองไปวางไว้ในสื่อบันทึกแบบถอดได้และในโฟลเดอร์ที่เปิดแบ่งปันบนเครือข่าย

*EN:* On 2 June 2566 a company reported that computers in the organisation were infected with an unwanted program that was spreading to other machines. Digital forensic examination found the implanted program acting as a backdoor, letting the offender send further commands to operate the compromised machine at will. Evidence then showed another remote control program on the same machine gathering machine information and attempting to contact the offender's command machine in order to download additional malicious components for installation. Finally the backdoor program was found spreading itself further by exploiting vulnerabilities on other machines and copying itself into removable media and network shared folders.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1059 Command and Scripting Interpreter | โปรแกรมที่ฝังอยู่ทำหน้าที่เป็นประตูหลัง เปิดทางให้คนร้ายส่งคำสั่งอื่น ๆ เข้ามาสั่งงานบนเครื่องที่ยึดครองได้ตามต้องการ | SDBot is used as a backdoor to enable other commands and functions to be executed in the compromised computer |
| 2 | described | T1071 Application Layer Protocol, T1105 Ingress Tool Transfer | โปรแกรมควบคุมระยะไกลอีกตัวหนึ่งบนเครื่องเดียวกันได้เก็บรวบรวมข้อมูลของเครื่องแล้วพยายามติดต่อกลับไปยังเครื่องสั่งการของคนร้าย เพื่อขอดาวน์โหลดส่วนประกอบเพิ่มเติมของโปรแกรมอันตรายเข้ามาติดตั้งต่อ | FlawedAmmyy/FlawedGrace remote access trojan (RAT) collects information and attempts to communicate with the Command and Control (C2) server to enable the download of additional malware components |
| 3 | described | T1105 Ingress Tool Transfer | โปรแกรมประตูหลังยังแพร่กระจายตัวเองต่อไปโดยอาศัยช่องโหว่ของเครื่องอื่น และคัดลอกสำเนาของตนเองไปวางไว้ในสื่อบันทึกแบบถอดได้และในโฟลเดอร์ที่เปิดแบ่งปันบนเครือข่าย | SDBot RAT propagates the infection, exploiting vulnerabilities and dropping copies of itself in removable drives and network shares |

- [ ] ผ่าน / แก้แล้ว

## rcti_051 — Turla - Snake (CTID emulation plan turla_snake.yaml)

> เมื่อวันที่ 12 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าจดหมายอิเล็กทรอนิกส์ของผู้บริหารถูกลักลอบอ่านและถูกส่งต่อออกไปภายนอก จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าโปรแกรมฝังตัวบนเครื่องที่ยึดครองได้รับคำสั่งให้ดาวน์โหลดชุดไฟล์หลายรายการเข้ามาเก็บไว้ ทั้งไฟล์โปรแกรมหลัก ไฟล์ประกอบ สคริปต์สำหรับติดตั้ง ไฟล์กำหนดกฎการคัดกรองจดหมาย และไฟล์ตั้งค่า ต่อมาปรากฏหลักฐานว่าคนร้ายสวมสิทธิ์ประจำตัวของผู้ดูแลโดเมนเพื่อคัดลอกไฟล์ชุดดังกล่าวทั้งหมดจากเครื่องที่ยึดครองไว้ ต่อไปยังเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ขององค์กร สุดท้ายพบว่าคนร้ายสั่งติดตั้งโปรแกรมนั้นบนเครื่องแม่ข่ายจดหมายจากระยะไกล ทำให้โปรแกรมกลายเป็นส่วนต่อขยายที่ทำงานแทรกอยู่ในขั้นตอนรับส่งจดหมายของเครื่องแม่ข่ายโดยตรง

*EN:* On 12 December 2566 a government agency reported that executives' email was being covertly read and forwarded outside. Digital forensic examination found the implant on the compromised machine receiving commands to download several files — the main program file, a companion file, an installation script, a mail filtering rules file and a configuration file. Evidence then showed the offender impersonating a domain administrator's identity token to copy all of those files from the compromised machine onward to the organisation's mail server. Finally the offender was found installing that program on the mail server remotely, making it an extension component running inside the server's own mail handling pipeline.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1105 Ingress Tool Transfer | โปรแกรมฝังตัวบนเครื่องที่ยึดครองได้รับคำสั่งให้ดาวน์โหลดชุดไฟล์หลายรายการเข้ามาเก็บไว้ ทั้งไฟล์โปรแกรมหลัก ไฟล์ประกอบ สคริปต์สำหรับติดตั้ง ไฟล์กำหนดกฎการคัดกรองจดหมาย และไฟล์ตั้งค่า | Task Snake to download LightNeuron Task Snake to download the companion DLL for LightNeuron. Task Snake to download the Powershell installation script for LightNeuron. Task Snake to download the LightNeuron email rules f… |
| 2 | described | T1570 Lateral Tool Transfer | คนร้ายสวมสิทธิ์ประจำตัวของผู้ดูแลโดเมนเพื่อคัดลอกไฟล์ชุดดังกล่าวทั้งหมดจากเครื่องที่ยึดครองไว้ ต่อไปยังเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ขององค์กร | Task Snake to copy LightNeuron using token impersonation to perform the copy as the domain admin. Task Snake to copy the LightNeuron companion DLL using token impersonation to perform the copy as the domain admin. Task S… |
| 3 | described | T1505 Server Software Component | คนร้ายสั่งติดตั้งโปรแกรมนั้นบนเครื่องแม่ข่ายจดหมายจากระยะไกล ทำให้โปรแกรมกลายเป็นส่วนต่อขยายที่ทำงานแทรกอยู่ในขั้นตอนรับส่งจดหมายของเครื่องแม่ข่ายโดยตรง | Task Snake to install LightNeuron remotely using WMI and PowerShell, using the domain admin's token |

- [ ] ผ่าน / แก้แล้ว

## rcti_052 — Sandworm Team (G0034) (CTID emulation plan sandworm.yaml)

ต้นทาง: <https://www.cert.ssi.gouv.fr/uploads/CERTFR-2021-CTI-005.pdf>

> เมื่อวันที่ 8 พฤษภาคม 2567 ผู้ให้บริการโครงข่ายแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบลินุกซ์ของบริษัทถูกยึดครอง จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายเพิ่มรายการงานตั้งเวลาของระบบลินุกซ์ไว้ในตารางเวลาของเครื่อง เพื่อให้โปรแกรมของตนถูกเรียกทำงานซ้ำตามรอบเวลาที่กำหนด ต่อมาปรากฏหลักฐานว่าคนร้ายยังสร้างหน่วยบริการเบื้องหลังของระบบขึ้นใหม่บนเครื่องเดียวกัน เพื่อให้ระบบเรียกโปรแกรมของตนทำงานเองทุกครั้งที่เครื่องเริ่มระบบ จากนั้นพบว่าคนร้ายเปิดอ่านไฟล์ที่ระบบใช้เก็บค่ารหัสผ่านของบัญชีผู้ใช้ทั้งหมดบนเครื่อง สุดท้ายยังพบว่าคนร้ายเปิดอ่านไฟล์ประวัติคำสั่งที่ผู้ดูแลระบบเคยพิมพ์ไว้ และไฟล์กุญแจสำหรับเชื่อมต่อระยะไกลที่เก็บไว้ในโฟลเดอร์ส่วนตัวของผู้ใช้

*EN:* On 8 May 2567 a network operator reported that its Linux server had been taken over. Digital forensic examination found the offender adding a Linux scheduled job entry to the machine's timetable so that their program would be run repeatedly on a set cycle. Evidence then showed the offender also creating a new background service unit on the same machine so the system would run their program by itself every time the machine booted. The offender was then found reading the file the system uses to store the password values of every user account on the machine. Finally the offender was found reading the command history file the administrator had typed and the remote connection key files stored in the user's home folder.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1053 Scheduled Task/Job | คนร้ายเพิ่มรายการงานตั้งเวลาของระบบลินุกซ์ไว้ในตารางเวลาของเครื่อง เพื่อให้โปรแกรมของตนถูกเรียกทำงานซ้ำตามรอบเวลาที่กำหนด | Sandworm establishes crontab persistence. |
| 2 | described | T1543 Create or Modify System Process | คนร้ายยังสร้างหน่วยบริการเบื้องหลังของระบบขึ้นใหม่บนเครื่องเดียวกัน เพื่อให้ระบบเรียกโปรแกรมของตนทำงานเองทุกครั้งที่เครื่องเริ่มระบบ | Sandworm establishes systemd persistence. |
| 3 | described | T1003 OS Credential Dumping | คนร้ายเปิดอ่านไฟล์ที่ระบบใช้เก็บค่ารหัสผ่านของบัญชีผู้ใช้ทั้งหมดบนเครื่อง | Sandworm reads /etc/shadow. Note: not in CTI but in TTP scope. |
| 4 | described | T1552 Unsecured Credentials | คนร้ายเปิดอ่านไฟล์ประวัติคำสั่งที่ผู้ดูแลระบบเคยพิมพ์ไว้ และไฟล์กุญแจสำหรับเชื่อมต่อระยะไกลที่เก็บไว้ในโฟลเดอร์ส่วนตัวของผู้ใช้ | Sandworm reads bash history. Note: not in CTI but in TTP scope. Sandworm reads SSH keys. Note: not in CTI but in TTP scope. |

- [ ] ผ่าน / แก้แล้ว

## rcti_053 — CISA AA22-138B (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-138b>

> เมื่อวันที่ 12 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดการอุปกรณ์ปลายทางถูกบุกรุกจากภายนอก จากการตรวจสอบ log พบว่าคนร้ายยิงคำสั่งโจมตีช่องโหว่ของซอฟต์แวร์บนเครื่องแม่ข่าย จนสามารถสั่งให้เครื่องดาวน์โหลดไฟล์สคริปต์อันตรายจากเว็บไซต์ภายนอกเข้ามาแล้วสั่งให้ทำงานบนเครื่องได้ ต่อมาปรากฏหลักฐานว่าคนร้ายนำช่องโหว่อีกรายการหนึ่งมาใช้ต่อเนื่องกับช่องโหว่แรก เพื่อให้สคริปต์ดังกล่าวทำงานด้วยสิทธิ์สูงสุดของระบบแทนสิทธิ์ของผู้ใช้ธรรมดา สุดท้ายจากการตรวจสอบรูปแบบการติดต่อสื่อสารพบว่าคนร้ายอาศัยส่วนประกอบสร้างข้อความแจ้งเตือนของซอฟต์แวร์ที่ติดตั้งอยู่แล้วบนเครื่อง เป็นช่องทางส่งคำขอผ่านโพรโทคอลเว็บเข้ามาสั่งงานเครื่องที่ยึดครองไว้ ทำให้การติดต่อดูกลมกลืนไปกับการใช้งานปกติ

*EN:* On 12 April 2565 an agency reported that its endpoint management server had been breached from outside. Logs showed the offender firing attack commands at a vulnerability in software on the server until they could make the machine download a malicious script file from an external website and run it. Evidence then showed the offender chaining a second vulnerability onto the first so that the script ran with the system's highest privileges rather than an ordinary user's. Finally, examination of the communication pattern found the offender using a notification-template component of software already installed on the machine as a channel to send web protocol requests in and command the compromised machine, making the traffic blend in with normal use.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1203 Exploitation for Client Execution, T1105 Ingress Tool Transfer, T1059 Command and Scripting Interpreter | คนร้ายยิงคำสั่งโจมตีช่องโหว่ของซอฟต์แวร์บนเครื่องแม่ข่าย จนสามารถสั่งให้เครื่องดาวน์โหลดไฟล์สคริปต์อันตรายจากเว็บไซต์ภายนอกเข้ามาแล้วสั่งให้ทำงานบนเครื่องได้ | On April 12, TA1 exploited CVE 2022-22954 to download a malicious shell script from https://20.232.97[.]189/up/80b6ae2cea.sh |
| 2 | described | T1068 Exploitation for Privilege Escalation | คนร้ายนำช่องโหว่อีกรายการหนึ่งมาใช้ต่อเนื่องกับช่องโหว่แรก เพื่อให้สคริปต์ดังกล่าวทำงานด้วยสิทธิ์สูงสุดของระบบแทนสิทธิ์ของผู้ใช้ธรรมดา | TA1 then chained CVE 2022-22960 to the initial exploit to run the shell script with root privileges (, [TA0004]) |
| 3 | described | T1071 Application Layer Protocol | คนร้ายอาศัยส่วนประกอบสร้างข้อความแจ้งเตือนของซอฟต์แวร์ที่ติดตั้งอยู่แล้วบนเครื่อง เป็นช่องทางส่งคำขอผ่านโพรโทคอลเว็บเข้ามาสั่งงานเครื่องที่ยึดครองไว้ ทำให้การติดต่อดูกลมกลืนไปกับการใช้งานปกติ | TA1 first targeted Freemarker—a legitimate application that allows for customized notifications by creating templates—to send the following customized GET request URI to the compromised server |

- [ ] ผ่าน / แก้แล้ว

## rcti_054 — Carbanak (CTID emulation plan Carbanak.yaml)

ต้นทาง: <https://www.fireeye.com/content/dam/fireeye-www/summit/cds-2018/presentations/cds18-technical-s04-hello-carbanak.pdf>

> เมื่อวันที่ 14 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกได้ลุกลามไปถึงเครื่องแม่ข่ายควบคุมโดเมนของธนาคาร จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายใช้คำสั่งสอบถามชื่อโดเมนเพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายควบคุมโดเมนที่เป็นเป้าหมายถัดไป ต่อมาปรากฏหลักฐานว่าคนร้ายอาศัยการสร้างบริการของระบบขึ้นบนเครื่องแม่ข่ายควบคุมโดเมนนั้น เพื่อสั่งรันคำสั่งจากเครื่องแม่ข่ายเก็บเอกสารที่ยึดครองไว้ก่อนหน้าข้ามมายังเครื่องใหม่ จากนั้นพบว่าคนร้ายอัปโหลดไฟล์โปรแกรมขนาดเล็กขึ้นไปทำงานบนเครื่องแม่ข่ายควบคุมโดเมน โดยกำหนดให้ติดต่อกลับออกไปยังเครื่องสั่งการภายนอกผ่านหมายเลขพอร์ตที่ไม่ใช่พอร์ตมาตรฐานของบริการนั้น เพื่อเลี่ยงการตรวจจับ สุดท้ายพบว่าคนร้ายสั่งคำสั่งบนเครื่องแม่ข่ายควบคุมโดเมนเพื่อเรียกดูรายละเอียดของเครื่องคอมพิวเตอร์ที่ผู้บริหารฝ่ายการเงินใช้งานอยู่จากระบบทะเบียนโดเมน

*EN:* On 14 June 2567 a commercial bank filed a further report that the breach had spread to the bank's domain controller. Digital forensic examination found the offender using a domain name lookup command to find the IP address of the domain controller as their next target. Evidence then showed the offender creating a system service on that domain controller in order to run commands across from the previously compromised document server to the new machine. The offender was then found uploading a small program file to run on the domain controller, configured to call back out to an external command machine over a port number that was not the standard one for that service, in order to evade detection. Finally the offender was found running a command on the domain controller to read details of the computer used by the chief financial officer from the domain directory.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1018 Remote System Discovery | คนร้ายใช้คำสั่งสอบถามชื่อโดเมนเพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายควบคุมโดเมนที่เป็นเป้าหมายถัดไป | The nslookup utility is used to find the IP address of bankdc |
| 2 | described | T1569 System Services | คนร้ายอาศัยการสร้างบริการของระบบขึ้นบนเครื่องแม่ข่ายควบคุมโดเมนนั้น เพื่อสั่งรันคำสั่งจากเครื่องแม่ข่ายเก็บเอกสารที่ยึดครองไว้ก่อนหน้าข้ามมายังเครื่องใหม่ | Lateral Movement to bankdc from bankfileserver using psexec.py |
| 3 | described | T1571 Non-Standard Port | คนร้ายอัปโหลดไฟล์โปรแกรมขนาดเล็กขึ้นไปทำงานบนเครื่องแม่ข่ายควบคุมโดเมน โดยกำหนดให้ติดต่อกลับออกไปยังเครื่องสั่งการภายนอกผ่านหมายเลขพอร์ตที่ไม่ใช่พอร์ตมาตรฐานของบริการนั้น เพื่อเลี่ยงการตรวจจับ | Upload and execute Tiny.exe on bankdc. Requires elevated agent |
| 4 | described | T1018 Remote System Discovery | คนร้ายสั่งคำสั่งบนเครื่องแม่ข่ายควบคุมโดเมนเพื่อเรียกดูรายละเอียดของเครื่องคอมพิวเตอร์ที่ผู้บริหารฝ่ายการเงินใช้งานอยู่จากระบบทะเบียนโดเมน | Get CFO Workstation Information from bankdc by running Get-ADComputer |

- [ ] ผ่าน / แก้แล้ว

## rcti_055 — CISA AA23-270A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-270a>

> เมื่อวันที่ 27 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความว่าอุปกรณ์เราเตอร์ที่ติดตั้งอยู่ตามสาขาถูกดัดแปลง จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายเข้าไปแก้ไขซอฟต์แวร์ระดับเฟิร์มแวร์ที่ฝังอยู่ในตัวอุปกรณ์เราเตอร์หลายเครื่อง โดยฝังชุดคำสั่งของตนเองเข้าไปในเฟิร์มแวร์เพื่อให้ยังคงอยู่แม้จะรีสตาร์ตหรือปรับปรุงระบบแล้ว ต่อมาปรากฏหลักฐานว่าเฟิร์มแวร์ที่ถูกดัดแปลงนั้นเปิดช่องทางเชื่อมต่อระยะไกลลับไว้ ทำให้คนร้ายเข้าใช้งานอุปกรณ์ได้ตลอดเวลาโดยที่การเชื่อมต่อของคนร้ายจะไม่ถูกบันทึกลงในไฟล์บันทึกเหตุการณ์ของอุปกรณ์ สุดท้ายพบว่าช่องทางลับดังกล่าวถูกออกแบบให้เปิดและปิดได้ด้วยการส่งแพ็กเก็ตที่ประกอบขึ้นเป็นพิเศษเข้ามายังอุปกรณ์ ทำให้ในเวลาปกติช่องทางนี้จะปิดอยู่และตรวจไม่พบ

*EN:* On 27 September 2566 an internet service provider reported that routers installed at its branches had been tampered with. Digital forensic examination found the offender modifying the firmware-level software embedded in several routers, implanting their own instructions into the firmware so that it would persist even after restarts or system updates. Evidence then showed the modified firmware opening a hidden remote connection channel, letting the offender use the device at any time without their connections being written to the device's event log. Finally that hidden channel was found designed to be opened and closed by sending specially crafted packets to the device, so that in normal times the channel stayed closed and undetectable.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1542 Pre-OS Boot | คนร้ายเข้าไปแก้ไขซอฟต์แวร์ระดับเฟิร์มแวร์ที่ฝังอยู่ในตัวอุปกรณ์เราเตอร์หลายเครื่อง โดยฝังชุดคำสั่งของตนเองเข้าไปในเฟิร์มแวร์เพื่อให้ยังคงอยู่แม้จะรีสตาร์ตหรือปรับปรุงระบบแล้ว | BlackTech actors have compromised several Cisco® routers using variations of a customized firmware backdoor |
| 2 | described | T1556 Modify Authentication Process, T1562 ? | เฟิร์มแวร์ที่ถูกดัดแปลงนั้นเปิดช่องทางเชื่อมต่อระยะไกลลับไว้ ทำให้คนร้ายเข้าใช้งานอุปกรณ์ได้ตลอดเวลาโดยที่การเชื่อมต่อของคนร้ายจะไม่ถูกบันทึกลงในไฟล์บันทึกเหตุการณ์ของอุปกรณ์ | The modified firmware uses a built-in SSH backdoor , allowing BlackTech actors to maintain access to the compromised router without BlackTech connections being logged |
| 3 | described | T1205 Traffic Signaling | ช่องทางลับดังกล่าวถูกออกแบบให้เปิดและปิดได้ด้วยการส่งแพ็กเก็ตที่ประกอบขึ้นเป็นพิเศษเข้ามายังอุปกรณ์ ทำให้ในเวลาปกติช่องทางนี้จะปิดอยู่และตรวจไม่พบ | The backdoor functionality is enabled and disabled through specially crafted TCP or UDP packets |

- [ ] ผ่าน / แก้แล้ว

## rcti_056 — CISA AA23-270A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-270a>

> เมื่อวันที่ 28 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความว่าเครือข่ายของสำนักงานใหญ่ในประเทศไทยถูกบุกรุกผ่านทางบริษัทลูกในต่างประเทศ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายสั่งปิดการบันทึกเหตุการณ์ของระบบเพื่อไม่ให้เหลือหลักฐาน แล้วอาศัยความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนของบริษัทลูกกับโดเมนของสำนักงานใหญ่ กระโดดข้ามจากเครือข่ายของบริษัทลูกเข้ามายังเครือข่ายในประเทศ ต่อมาปรากฏหลักฐานว่าคนร้ายนำใบรับรองสำหรับลงลายมือชื่อโปรแกรมที่ขโมยมาไปเซ็นกำกับไฟล์โปรแกรมอันตรายของตน ทำให้ไฟล์ดูเหมือนเป็นซอฟต์แวร์ที่ถูกต้องและโปรแกรมด้านความปลอดภัยตรวจจับได้ยากขึ้น สุดท้ายจากการตรวจสอบวิธีที่คนร้ายใช้คงอยู่ในเครื่องพบว่ามีทั้งการเปิดเชลล์รับการเชื่อมต่อค้างไว้ การแก้ไขทะเบียนระบบของเครื่องผู้เสียหายเพื่อเปิดใช้งาน Remote Desktop Protocol และการเข้าใช้งานผ่าน SSH

*EN:* On 28 September 2566 a multinational company reported that its Thai head office network had been breached by way of an overseas subsidiary. Digital forensic examination found the offender disabling system event logging so that no evidence would remain, then abusing the trust relationship between the subsidiary's domain and the head office domain to hop from the subsidiary's network into the domestic network. Evidence then showed the offender using stolen code-signing certificates to sign their malicious program files, making them appear to be legitimate software and harder for security software to detect. Finally, examination of how the offender persisted on machines found open listening shells, modification of the victim machine's registry to enable Remote Desktop Protocol, and access over SSH.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1562 ?, T1199 Trusted Relationship | คนร้ายสั่งปิดการบันทึกเหตุการณ์ของระบบเพื่อไม่ให้เหลือหลักฐาน แล้วอาศัยความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนของบริษัทลูกกับโดเมนของสำนักงานใหญ่ กระโดดข้ามจากเครือข่ายของบริษัทลูกเข้ามายังเครือข่ายในประเทศ | These TTPs allow the actors to disable logging and abuse trusted domain relationships to pivot between international subsidiaries and domestic headquarters’ networks |
| 2 | described | T1553 Subvert Trust Controls | คนร้ายนำใบรับรองสำหรับลงลายมือชื่อโปรแกรมที่ขโมยมาไปเซ็นกำกับไฟล์โปรแกรมอันตรายของตน ทำให้ไฟล์ดูเหมือนเป็นซอฟต์แวร์ที่ถูกต้องและโปรแกรมด้านความปลอดภัยตรวจจับได้ยากขึ้น | The actors also use stolen code-signing certificates to sign the malicious payloads, which make them appear legitimate and therefore more difficult for security software to detect |
| 3 | named | T1112 Modify Registry, T1021 Remote Services | มีทั้งการเปิดเชลล์รับการเชื่อมต่อค้างไว้ การแก้ไขทะเบียนระบบของเครื่องผู้เสียหายเพื่อเปิดใช้งาน Remote Desktop Protocol และการเข้าใช้งานผ่าน SSH | Common methods of persistence on a host include NetCat shells, modifying the victim registry to enable the remote desktop protocol (RDP) , and secure shell (SSH) |

- [ ] ผ่าน / แก้แล้ว

## rcti_057 — CISA AA23-319A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-319a>

> เมื่อวันที่ 16 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความว่าระบบงานทั้งหมดถูกเข้ารหัสลับและมีการเรียกค่าไถ่ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าโปรแกรมเรียกค่าไถ่แทรกชุดคำสั่งของตนเข้าไปทำงานในหน่วยความจำของกระบวนการที่กำลังทำงานอยู่บนเครื่องเป็นอันดับแรก ต่อมาปรากฏหลักฐานว่ามีการรันคำสั่งแก้ไขทะเบียนระบบผ่านหน้าต่างคำสั่งของวินโดวส์ โดยคำสั่งดังกล่าวไม่ได้ถูกอำพรางไว้และปรากฏเป็นข้อความอ่านได้ตามปกติ จากนั้นพบว่าโปรแกรมเข้ารหัสได้เปลี่ยนนามสกุลของไฟล์ที่เข้ารหัสแล้วทุกไฟล์ให้เป็นนามสกุลเฉพาะของตน และเมื่อเสร็จสิ้นได้สั่งคำสั่ง PowerShell ลบไฟล์โปรแกรมของตนออกจากเครือข่ายโดยเรียกผ่านหน้าต่างคำสั่งที่ถูกซ่อนไม่ให้ผู้ใช้มองเห็น ต่อมาหลังจากไล่สำรวจเครือข่ายเสร็จ ข้อมูลของโรงพยาบาลถูกเข้ารหัสลับด้วยกุญแจสาธารณะขนาดสี่พันเก้าสิบหกบิตร่วมกับอัลกอริทึมเข้ารหัสแบบสตรีม สุดท้ายพบว่าคนร้ายใช้วิธีข่มขู่สองชั้น คือเรียกเงินค่าถอดรหัสข้อมูลพร้อมขู่จะเผยแพร่ข้อมูลอ่อนไหวที่นำออกไปหากไม่ได้รับเงิน โดยให้ผู้เสียหายโอนเงินเป็นสกุลเงินดิจิทัลไปยังกระเป๋าเงินที่กำหนด

*EN:* On 16 November 2566 a hospital reported that all its systems had been encrypted with a ransom demand. Digital forensic examination found the ransom program first injecting its own instructions into the memory of processes already running on the machine. Evidence then showed registry modification commands run through the Windows command window, those commands not disguised and appearing as ordinary readable text. The encryption program was then found changing the extension of every encrypted file to its own distinctive extension, and on completion issuing a PowerShell command to delete its own program file from the network, invoked through a command window hidden from the user. After surveying the network, the hospital's data was encrypted with a 4096-bit public key together with a stream cipher algorithm. Finally the offender was found using double extortion — demanding payment for decryption while threatening to publish the sensitive data taken out — instructing the victim to transfer cryptocurrency to a specified wallet.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1055 Process Injection | โปรแกรมเรียกค่าไถ่แทรกชุดคำสั่งของตนเข้าไปทำงานในหน่วยความจำของกระบวนการที่กำลังทำงานอยู่บนเครื่องเป็นอันดับแรก | The cryptographic ransomware application first injects the PE into running processes on the compromised system |
| 2 | described | T1112 Modify Registry | มีการรันคำสั่งแก้ไขทะเบียนระบบผ่านหน้าต่างคำสั่งของวินโดวส์ โดยคำสั่งดังกล่าวไม่ได้ถูกอำพรางไว้และปรากฏเป็นข้อความอ่านได้ตามปกติ | Registry modification commands are not obfuscated, displayed as plain-text strings and executed via cmd.exe |
| 3 | named | T1070 Indicator Removal, T1564 Hide Artifacts | โปรแกรมเข้ารหัสได้เปลี่ยนนามสกุลของไฟล์ที่เข้ารหัสแล้วทุกไฟล์ให้เป็นนามสกุลเฉพาะของตน และเมื่อเสร็จสิ้นได้สั่งคำสั่ง PowerShell ลบไฟล์โปรแกรมของตนออกจากเครือข่ายโดยเรียกผ่านหน้าต่างคำสั่งที่ถูกซ่อนไม่ให้ผู้ใช้มองเห็น | Rhysida’s encryptor runs a file to encrypt and modify all encrypted files to display a .rhysida extension. Following encryption, a PowerShell command deletes the binary from the network using a hidden command window |
| 4 | described | T1486 Data Encrypted for Impact | ข้อมูลของโรงพยาบาลถูกเข้ารหัสลับด้วยกุญแจสาธารณะขนาดสี่พันเก้าสิบหกบิตร่วมกับอัลกอริทึมเข้ารหัสแบบสตรีม | After mapping the network, the ransomware encrypts data using a 4096-bit RSA encryption key with a ChaCha20 algorithm |
| 5 | described | T1657 Financial Theft | คนร้ายใช้วิธีข่มขู่สองชั้น คือเรียกเงินค่าถอดรหัสข้อมูลพร้อมขู่จะเผยแพร่ข้อมูลอ่อนไหวที่นำออกไปหากไม่ได้รับเงิน โดยให้ผู้เสียหายโอนเงินเป็นสกุลเงินดิจิทัลไปยังกระเป๋าเงินที่กำหนด | Rhysida actors reportedly engage in “double extortion” —demanding a ransom payment to decrypt victim data and threatening to publish the sensitive exfiltrated data unless the ransom is paid., Rhysida actors direct victim… |

- [ ] ผ่าน / แก้แล้ว

## rcti_058 — CISA AA21-076A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-076a>

> เมื่อวันที่ 17 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความว่าลูกค้าหลายรายถูกโอนเงินออกจากบัญชีทั้งที่ยืนยันว่าไม่ได้ทำรายการเอง จากการตรวจสอบเครื่องคอมพิวเตอร์ของผู้เสียหายพบว่ามีโปรแกรมไม่พึงประสงค์แทรกตัวอยู่ในโปรแกรมท่องเว็บของผู้ใช้ คอยดักจับและแก้ไขข้อมูลระหว่างที่ผู้ใช้กรอกข้อมูลบนหน้าเว็บธนาคาร ทำให้ได้ชื่อผู้ใช้และรหัสผ่านของผู้เสียหายไป ต่อมาปรากฏหลักฐานว่าโปรแกรมเดียวกันยังทำหน้าที่เป็นตัวดาวน์โหลด โดยดึงไฟล์โปรแกรมอันตรายตัวอื่นจากเครื่องภายนอกเข้ามาติดตั้งเพิ่มบนเครื่องของผู้เสียหาย สุดท้ายจากการตรวจสอบความสามารถของโปรแกรมพบว่าสามารถส่งข้อมูลที่รวบรวมได้ออกไปยังเครื่องสั่งการที่กำหนดไว้ตายตัวในตัวโปรแกรม อันเป็นลักษณะ Exfiltration Over C2 Channel ทั้งยังแอบใช้ทรัพยากรของเครื่องผู้เสียหายขุดเหรียญสกุลเงินดิจิทัล ซึ่งเข้าลักษณะ Resource Hijacking และเรียกดูข้อมูลของเครื่องรวมถึงข้อมูลเฟิร์มแวร์ระดับล่างด้วย

*EN:* On 17 March 2564 a bank reported that several customers had money transferred out of their accounts while insisting they had made no such transactions. Examination of the victims' computers found an unwanted program interposed inside the user's web browser, intercepting and altering data while the user filled in the bank's web pages, thereby obtaining the victims' usernames and passwords. Evidence then showed the same program also acting as a downloader, pulling other malicious program files from an external machine to install on the victim's computer. Finally, examination of the program's capabilities found it able to send collected data out to a command machine hardcoded in the program — a case of Exfiltration Over C2 Channel — as well as covertly using the victim machine's resources to mine cryptocurrency, matching Resource Hijacking, and reading machine information including low-level firmware data.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1185 Browser Session Hijacking | มีโปรแกรมไม่พึงประสงค์แทรกตัวอยู่ในโปรแกรมท่องเว็บของผู้ใช้ คอยดักจับและแก้ไขข้อมูลระหว่างที่ผู้ใช้กรอกข้อมูลบนหน้าเว็บธนาคาร ทำให้ได้ชื่อผู้ใช้และรหัสผ่านของผู้เสียหายไป | TrickBot uses person-in-the-browser attacks to steal information, such as login credentials (Man in the Browser ) |
| 2 | described | T1105 Ingress Tool Transfer | โปรแกรมเดียวกันยังทำหน้าที่เป็นตัวดาวน์โหลด โดยดึงไฟล์โปรแกรมอันตรายตัวอื่นจากเครื่องภายนอกเข้ามาติดตั้งเพิ่มบนเครื่องของผู้เสียหาย | Serve as an Emotet downloader (Ingress Tool Transfer ) |
| 3 | named | T1041 Exfiltration Over C2 Channel, T1496 Resource Hijacking | สามารถส่งข้อมูลที่รวบรวมได้ออกไปยังเครื่องสั่งการที่กำหนดไว้ตายตัวในตัวโปรแกรม อันเป็นลักษณะ Exfiltration Over C2 Channel ทั้งยังแอบใช้ทรัพยากรของเครื่องผู้เสียหายขุดเหรียญสกุลเงินดิจิทัล ซึ่งเข้าลักษณะ Resource Hijacking | TrickBot is capable of data exfiltration over a hardcoded C2 server, cryptomining, and host enumeration (e.g., reconnaissance of Unified Extensible Firmware Interface or Basic Input/Output System [UEFI/BIOS] firmware) (E… |

- [ ] ผ่าน / แก้แล้ว

## rcti_059 — CISA AA22-152A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-152a>

> เมื่อวันที่ 1 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครือข่ายภายในถูกบุกรุกผ่านอุปกรณ์ชายขอบเครือข่าย จากการตรวจสอบพบว่าอุปกรณ์เชื่อมต่อเครือข่ายส่วนตัวเสมือนแบบเอสเอสแอลของหน่วยงานเป็นรุ่นเก่าที่ยังไม่ได้ปรับปรุงซอฟต์แวร์ จึงยังมีช่องโหว่ที่ถูกประกาศไว้หลายรายการค้างอยู่ ต่อมาปรากฏหลักฐานว่าอุปกรณ์ไฟร์วอลล์และอุปกรณ์เชื่อมต่อระยะไกลของผู้ผลิตอีกรายหนึ่งที่ติดตั้งอยู่ในหน่วยงานเดียวกัน ก็อยู่ในสภาพเดียวกันคือยังไม่ได้ปรับปรุงและมีช่องโหว่ที่เปิดให้โจมตีจากอินเทอร์เน็ตได้ สุดท้ายจากการตรวจสอบ log การเข้าใช้งานพบว่าคนร้ายนำชื่อผู้ใช้และรหัสผ่านสำหรับเชื่อมต่อเครือข่ายส่วนตัวเสมือนและสำหรับเข้าใช้งานหน้าจอระยะไกล ซึ่งถูกขโมยออกไปก่อนหน้า มาล็อกอินเข้าสู่ระบบของหน่วยงานได้โดยตรง

*EN:* On 1 June 2565 an agency reported that its internal network had been breached through edge network devices. Examination found the agency's SSL virtual private network appliance was an older model whose software had not been updated, leaving several published vulnerabilities outstanding. Evidence then showed the firewall and remote connection appliances from another vendor installed at the same agency were in the same state — not updated and carrying vulnerabilities exposed to attack from the internet. Finally, access logs showed the offender using previously stolen virtual private network and remote desktop usernames and passwords to log directly into the agency's systems.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1133 External Remote Services | อุปกรณ์เชื่อมต่อเครือข่ายส่วนตัวเสมือนแบบเอสเอสแอลของหน่วยงานเป็นรุ่นเก่าที่ยังไม่ได้ปรับปรุงซอฟต์แวร์ จึงยังมีช่องโหว่ที่ถูกประกาศไว้หลายรายการค้างอยู่ | Outdated SonicWall SSL VPN appliances are vulnerable to multiple recent CVEs |
| 2 | described | T1133 External Remote Services, T1190 Exploit Public-Facing Application | อุปกรณ์ไฟร์วอลล์และอุปกรณ์เชื่อมต่อระยะไกลของผู้ผลิตอีกรายหนึ่งที่ติดตั้งอยู่ในหน่วยงานเดียวกัน ก็อยู่ในสภาพเดียวกันคือยังไม่ได้ปรับปรุงและมีช่องโหว่ที่เปิดให้โจมตีจากอินเทอร์เน็ตได้ | Outdated Fortinet FortiGate SSL VPN appliances /firewall appliances are vulnerable to multiple recent CVEs |
| 3 | described | T1078 Valid Accounts | คนร้ายนำชื่อผู้ใช้และรหัสผ่านสำหรับเชื่อมต่อเครือข่ายส่วนตัวเสมือนและสำหรับเข้าใช้งานหน้าจอระยะไกล ซึ่งถูกขโมยออกไปก่อนหน้า มาล็อกอินเข้าสู่ระบบของหน่วยงานได้โดยตรง | Stolen virtual private network (VPN) or Remote Desktop Protocol (RDP) credentials |

- [ ] ผ่าน / แก้แล้ว

## rcti_060 — Wizard Spider (CTID emulation plan wizard_spider.yaml)

ต้นทาง: <https://www.crowdstrike.com/blog/timelining-grim-spiders-big-game-hunting-tactics/>

> เมื่อวันที่ 3 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์หลายเครื่องในองค์กรถูกเข้าควบคุมต่อเนื่องกันเป็นทอด ๆ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายปิดการเชื่อมต่อหน้าจอระยะไกลที่เปิดค้างไว้กับเครื่องเป้าหมายเครื่องแรก แล้วนำชื่อผู้ใช้และรหัสผ่านที่ค้นพบระหว่างทางไปเปิดการเชื่อมต่อหน้าจอระยะไกลเข้าสู่เครื่องเป้าหมายเครื่องถัดไป ต่อมาปรากฏหลักฐานว่าคนร้ายดาวน์โหลดไฟล์โปรแกรมชุดใหม่เข้ามาไว้บนเครื่องเป้าหมายนั้นแล้วสั่งให้ทำงานผ่านการเชื่อมต่อดังกล่าว จากนั้นโปรแกรมได้เก็บรวบรวมข้อมูลประจำเครื่อง ทั้งรุ่นของระบบปฏิบัติการ ชื่อเครื่อง ชนิดของหน่วยประมวลผล ขนาดหน่วยความจำที่มี และข้อมูลเฟิร์มแวร์ระดับล่างของเครื่อง ต่อมายังพบการเรียกดูรายการโปรแกรมและบริการทั้งหมดที่ติดตั้งอยู่บนเครื่อง แล้วรวบรวมรายชื่อบัญชีผู้ใช้ที่มีอยู่บนเครื่องนั้นและรายชื่อบัญชีผู้ใช้ในโดเมนขององค์กร สุดท้ายพบว่าโปรแกรมเรียกดูหมายเลขไอพี ตำแหน่งที่ตั้ง และรายละเอียดการตั้งค่าเครือข่ายอื่น ๆ ของเครื่องผู้เสียหาย

*EN:* On 3 October 2567 a wholesale company reported that several computers in the organisation had been taken over one after another in a chain. Digital forensic examination found the offender closing the remote screen connection left open to the first target machine, then using credentials discovered along the way to open a remote screen connection into the next target. Evidence then showed the offender downloading a new program file onto that target and running it over the connection. The program then gathered machine information — operating system version, machine name, processor type, available memory size and the machine's low-level firmware information. It was then found reading the list of all programs and services installed on the machine, then collecting the user accounts present on that machine and the user accounts in the organisation's domain. Finally the program was found reading the IP address, location and other network configuration details of the victim's machine.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1021 Remote Services | คนร้ายปิดการเชื่อมต่อหน้าจอระยะไกลที่เปิดค้างไว้กับเครื่องเป้าหมายเครื่องแรก แล้วนำชื่อผู้ใช้และรหัสผ่านที่ค้นพบระหว่างทางไปเปิดการเชื่อมต่อหน้าจอระยะไกลเข้าสู่เครื่องเป้าหมายเครื่องถัดไป | End the RDP session to the initial target. This ability must be run by an agent running on the attacker-controlled machine (e.g. on the C2 server itself), since the RDP connection originates from the attacker's machine. … |
| 2 | described | T1105 Ingress Tool Transfer | คนร้ายดาวน์โหลดไฟล์โปรแกรมชุดใหม่เข้ามาไว้บนเครื่องเป้าหมายนั้นแล้วสั่งให้ทำงานผ่านการเชื่อมต่อดังกล่าว | Downloads a new agent executable and executes it on the target host over RDP. This ability must be run by an agent running on the attacker-controlled Linux machine (e.g. on the C2 server itself), since the RDP connection… |
| 3 | described | T1082 System Information Discovery | โปรแกรมได้เก็บรวบรวมข้อมูลประจำเครื่อง ทั้งรุ่นของระบบปฏิบัติการ ชื่อเครื่อง ชนิดของหน่วยประมวลผล ขนาดหน่วยความจำที่มี และข้อมูลเฟิร์มแวร์ระดับล่างของเครื่อง | Wizard Spider uses TrickBot to gathers the OS version, machine name, CPU type, amount of RAM available, and UEFI/BIOS firmware information from the victim’s machine. |
| 4 | described | T1007 System Service Discovery | พบการเรียกดูรายการโปรแกรมและบริการทั้งหมดที่ติดตั้งอยู่บนเครื่อง | Wizard Spider uses TrickBot to collect a list of installed programs and services on the system’s machine |
| 5 | described | T1087 Account Discovery | รวบรวมรายชื่อบัญชีผู้ใช้ที่มีอยู่บนเครื่องนั้นและรายชื่อบัญชีผู้ใช้ในโดเมนขององค์กร | Wizard Spider uses TrickBot to collect the local users of the system. Wizard Spider uses TrickBot to collect the domain users of the system. |
| 6 | described | T1016 System Network Configuration Discovery | โปรแกรมเรียกดูหมายเลขไอพี ตำแหน่งที่ตั้ง และรายละเอียดการตั้งค่าเครือข่ายอื่น ๆ ของเครื่องผู้เสียหาย | Wizard Spider uses TrickBot to obtain the IP address, location, and other relevant network information from the victim’s machine. |

- [ ] ผ่าน / แก้แล้ว

## rcti_061 — CISA AA22-174A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-174a>

> เมื่อวันที่ 20 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบเดสก์ท็อปเสมือนขององค์กรถูกบุกรุก จากการตรวจสอบพบว่าเครื่องแม่ข่ายดังกล่าวเปิดให้เข้าถึงได้จากอินเทอร์เน็ตและยังไม่ได้ติดตั้งชุดแก้ไขช่องโหว่ของไลบรารีบันทึกเหตุการณ์ที่ผู้ผลิตประกาศไว้ตั้งแต่ปลายปีก่อน คนร้ายจึงอาศัยช่องโหว่นั้นเข้าถึงเครือข่ายขององค์กรได้เป็นครั้งแรก ต่อมาปรากฏหลักฐานว่าคนร้ายวางไฟล์โปรแกรมที่ตั้งชื่อและแสดงรายละเอียดให้ดูเหมือนเป็นบริการที่ถูกต้องของระบบปฏิบัติการวินโดวส์ โดยดัดแปลงมาจากเครื่องมือตรวจสอบเซสชันการล็อกอินของผู้ผลิตรายหนึ่ง แล้วฝังชุดคำสั่งอันตรายที่ถูกบีบอัดไว้ภายใน สุดท้ายจากการตรวจสอบความสามารถของไฟล์ที่ฝังอยู่ภายในพบว่าเป็นเครื่องมือควบคุมเครื่องระยะไกล ซึ่งดักบันทึกทุกปุ่มที่ผู้ใช้กดบนแป้นพิมพ์ อัปโหลดและสั่งรันไฟล์เพิ่มเติมเข้ามาบนเครื่องได้ และเปิดให้คนร้ายมองเห็นและควบคุมหน้าจอของเครื่องเป้าหมายได้โดยตรง

*EN:* On 20 June 2565 an agency reported that its virtual desktop server had been breached. Examination found the server was reachable from the internet and had not had the vendor's patch for a logging library vulnerability, announced late the previous year, installed; the offender used that vulnerability to first reach the organisation's network. Evidence then showed the offender placing a program file named and described to look like a legitimate Windows service, adapted from one vendor's logon session inspection tool with compressed malicious instructions embedded inside. Finally, examination of the embedded file's capabilities found it to be a remote machine control tool that logged every key the user pressed, could upload and run further files on the machine, and let the offender see and control the target machine's screen directly.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1190 Exploit Public-Facing Application | เครื่องแม่ข่ายดังกล่าวเปิดให้เข้าถึงได้จากอินเทอร์เน็ตและยังไม่ได้ติดตั้งชุดแก้ไขช่องโหว่ของไลบรารีบันทึกเหตุการณ์ที่ผู้ผลิตประกาศไว้ตั้งแต่ปลายปีก่อน คนร้ายจึงอาศัยช่องโหว่นั้นเข้าถึงเครือข่ายขององค์กรได้เป็นครั้งแรก | VMware made fixes available in December 2021 and confirmed exploitation in the wild on December 10, 2021. Since December 2021, multiple cyber threat actor groups have exploited Log4Shell on unpatched, public-facing VMwar… |
| 2 | described | T1036 Masquerading | คนร้ายวางไฟล์โปรแกรมที่ตั้งชื่อและแสดงรายละเอียดให้ดูเหมือนเป็นบริการที่ถูกต้องของระบบปฏิบัติการวินโดวส์ โดยดัดแปลงมาจากเครื่องมือตรวจสอบเซสชันการล็อกอินของผู้ผลิตรายหนึ่ง แล้วฝังชุดคำสั่งอันตรายที่ถูกบีบอัดไว้ภายใน | hmsvc.exe masquerades as a legitimate Microsoft® Windows® service (SysInternals LogonSessions software) and appears to be a modified version of SysInternals LogonSessions software embedded with malicious packed code |
| 3 | described | T1056 Input Capture, T1105 Ingress Tool Transfer | เป็นเครื่องมือควบคุมเครื่องระยะไกล ซึ่งดักบันทึกทุกปุ่มที่ผู้ใช้กดบนแป้นพิมพ์ อัปโหลดและสั่งรันไฟล์เพิ่มเติมเข้ามาบนเครื่องได้ และเปิดให้คนร้ายมองเห็นและควบคุมหน้าจอของเครื่องเป้าหมายได้โดยตรง | The embedded executable is a remote access tool that provides an array of C2 capabilities, including the ability to log keystrokes , upload and execute additional payloads , and provide graphical user interface (GUI) acc… |

- [ ] ผ่าน / แก้แล้ว

## rcti_062 — Sandworm Team (G0034) (CTID emulation plan sandworm.yaml)

ต้นทาง: <https://www.cert.ssi.gouv.fr/uploads/CERTFR-2021-CTI-005.pdf>

> เมื่อวันที่ 5 เมษายน 2567 บริษัทผู้ให้บริการระบบสารสนเทศแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายเว็บของบริษัทถูกยึดครอง จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายล็อกอินเข้าเครื่องแม่ข่ายเว็บผ่านช่องทาง SSH ด้วยบัญชีที่ถูกต้อง แล้วส่งไฟล์สคริปต์ภาษาพีเอชพีจากเครื่องภายนอกเข้ามาวางไว้บนเครื่อง ต่อมาปรากฏหลักฐานว่าไฟล์สคริปต์ที่วางไว้นั้นถูกติดตั้งให้ทำงานเป็นหน้าเว็บสำหรับรับคำสั่ง ทำให้คนร้ายกลับเข้ามาสั่งงานเครื่องได้ตลอดเวลาผ่านการเรียกหน้าเว็บนั้น จากนั้นพบว่าคนร้ายส่งคำสั่งผ่านหน้าเว็บดังกล่าวเพื่อเรียกดูชื่อบัญชีผู้ใช้ที่สคริปต์กำลังทำงานอยู่ ต่อมายังเรียกดูรายละเอียดของระบบปฏิบัติการที่ติดตั้งบนเครื่องที่ยึดครองได้ และสุดท้ายสั่งไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์ที่มีอยู่บนเครื่องแม่ข่ายนั้น

*EN:* On 5 April 2567 an IT services provider reported that its web server had been taken over. Digital forensic examination found the offender logging into the web server over SSH with a valid account, then sending a PHP script file in from an external machine and placing it on the server. Evidence then showed that script installed to run as a web page for receiving commands, letting the offender return and operate the machine at any time by requesting that page. The offender was then found sending commands through that page to read the name of the account the script was running as, then to read details of the operating system installed on the compromised machine, and finally to enumerate the files and folders present on that server.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1105 Ingress Tool Transfer | คนร้ายล็อกอินเข้าเครื่องแม่ข่ายเว็บผ่านช่องทาง SSH ด้วยบัญชีที่ถูกต้อง แล้วส่งไฟล์สคริปต์ภาษาพีเอชพีจากเครื่องภายนอกเข้ามาวางไว้บนเครื่อง | Sandworm logs into patient zero via SSH using Valid Accounts. It is unknown how Sandworm obtained the credentials (perhaps an SSH password guessing attack, or zero day exploit). Sandworm then deploys a PHP webshell for p… |
| 2 | described | T1505 Server Software Component | ไฟล์สคริปต์ที่วางไว้นั้นถูกติดตั้งให้ทำงานเป็นหน้าเว็บสำหรับรับคำสั่ง ทำให้คนร้ายกลับเข้ามาสั่งงานเครื่องได้ตลอดเวลาผ่านการเรียกหน้าเว็บนั้น | Sandworm logs into patient zero via SSH using Valid Accounts. It is unknown how Sandworm obtained the credentials (perhaps an SSH password guessing attack, or zero day exploit). Sandworm then deploys a PHP webshell for p… |
| 3 | described | T1033 System Owner/User Discovery | คนร้ายส่งคำสั่งผ่านหน้าเว็บดังกล่าวเพื่อเรียกดูชื่อบัญชีผู้ใช้ที่สคริปต์กำลังทำงานอยู่ | Sandworm collects the username from a compromised host by issuing shell commands through the PHP webshell. This ability must be run by an agent running on the attacker-controlled machine (e.g. on the C2 server itself), s… |
| 4 | described | T1082 System Information Discovery | เรียกดูรายละเอียดของระบบปฏิบัติการที่ติดตั้งบนเครื่องที่ยึดครองได้ | Sandworm enumerates information about the infected system's operating system by issuing shell commands through the PHP webshell. This ability must be run by an agent running on the attacker-controlled machine (e.g. on th… |
| 5 | described | T1083 File and Directory Discovery | สั่งไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์ที่มีอยู่บนเครื่องแม่ข่ายนั้น | Sandworm enumerates files on a compromised host by issuing shell commands through the PHP webshell. This ability must be run by an agent running on the attacker-controlled machine (e.g. on the C2 server itself), since it… |

- [ ] ผ่าน / แก้แล้ว

## rcti_063 — CISA AA20-301A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-301a>

> เมื่อวันที่ 30 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเอกสารราชการในเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ถูกลักลอบคัดลอกออกไป จากการตรวจสอบพบว่าโปรแกรมขโมยเอกสารของคนร้ายเข้าไปแก้ไขค่าในทะเบียนระบบ เพื่อเปลี่ยนโปรแกรมที่ระบบจะเรียกใช้เป็นค่าเริ่มต้นเมื่อผู้ใช้เปิดไฟล์เอกสารชนิดหนึ่ง ทำให้โปรแกรมของคนร้ายถูกเรียกทำงานแทนทุกครั้งที่มีการเปิดเอกสารชนิดนั้น ต่อมาปรากฏหลักฐานว่าคนร้ายคงการเข้าถึงเว็บไซต์ที่ยึดครองไว้ได้ ด้วยการอัปโหลด Web Shell ที่ดัดแปลงมาจากโครงการโอเพนซอร์ซขึ้นไปวางไว้บนเครื่องแม่ข่าย ทำให้สามารถอัปโหลด ดาวน์โหลด และลบไฟล์กับโฟลเดอร์บนเว็บไซต์นั้นได้ สุดท้ายพบว่าคนร้ายใช้เครื่องมือที่สามารถเพิ่มบัญชีผู้ดูแลระบบของวินโดวส์ขึ้นใหม่ และเปิดใช้งาน Remote Desktop Protocol โดยหลบเลี่ยงกฎของไฟร์วอลล์ที่ตั้งไว้

*EN:* On 30 October 2563 an agency reported that official documents on staff computers had been covertly copied out. Examination found the offender's document-stealing program modifying a registry value to change the program the system would launch by default when a user opened a certain document type, so that the offender's program ran instead every time such a document was opened. Evidence then showed the offender maintaining access to a compromised website by uploading a Web Shell adapted from an open-source project onto the server, allowing files and folders on that site to be uploaded, downloaded and deleted. Finally the offender was found using a tool able to add a new Windows administrator account and enable Remote Desktop Protocol while evading the firewall rules in place.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1546 Event Triggered Execution | โปรแกรมขโมยเอกสารของคนร้ายเข้าไปแก้ไขค่าในทะเบียนระบบ เพื่อเปลี่ยนโปรแกรมที่ระบบจะเรียกใช้เป็นค่าเริ่มต้นเมื่อผู้ใช้เปิดไฟล์เอกสารชนิดหนึ่ง ทำให้โปรแกรมของคนร้ายถูกเรียกทำงานแทนทุกครั้งที่มีการเปิดเอกสารชนิดนั้น | Kimsuky uses a document stealer module that changes the default program associated with Hangul Word Processor (HWP) documents (.hwp files) in the Registry (Event Triggered Execution: Change Default File Association ) |
| 2 | named | T1505 Server Software Component | คนร้ายคงการเข้าถึงเว็บไซต์ที่ยึดครองไว้ได้ ด้วยการอัปโหลด Web Shell ที่ดัดแปลงมาจากโครงการโอเพนซอร์ซขึ้นไปวางไว้บนเครื่องแม่ข่าย ทำให้สามารถอัปโหลด ดาวน์โหลด และลบไฟล์กับโฟลเดอร์บนเว็บไซต์นั้นได้ | Kimsuky maintains access to compromised domains by uploading actor-modified versions of open-source Hypertext Processor (PHP)-based web shells; these web shells enable the APT actor to upload, download, and delete files … |
| 3 | named | T1021 Remote Services | คนร้ายใช้เครื่องมือที่สามารถเพิ่มบัญชีผู้ดูแลระบบของวินโดวส์ขึ้นใหม่ และเปิดใช้งาน Remote Desktop Protocol โดยหลบเลี่ยงกฎของไฟร์วอลล์ที่ตั้งไว้ | GREASE is a tool capable of adding a Windows administrator account and enabling RDP while avoiding firewall rules (Remote Services: Remote Desktop Protocol ) |

- [ ] ผ่าน / แก้แล้ว

## rcti_064 — Wizard Spider (CTID emulation plan wizard_spider.yaml)

ต้นทาง: <https://www.crowdstrike.com/blog/timelining-grim-spiders-big-game-hunting-tactics/>

> เมื่อวันที่ 18 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกลุกลามถึงเครื่องแม่ข่ายควบคุมโดเมนขององค์กร จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายนำชื่อผู้ใช้และรหัสผ่านที่ค้นพบระหว่างการบุกรุกไปเปิดการเชื่อมต่อหน้าจอระยะไกลเข้าสู่เครื่องแม่ข่ายควบคุมโดเมนโดยตรง ต่อมาปรากฏหลักฐานว่าคนร้ายดาวน์โหลดไฟล์โปรแกรมชุดใหม่เข้ามาไว้บนเครื่องแม่ข่ายควบคุมโดเมนแล้วสั่งให้ทำงานผ่านการเชื่อมต่อดังกล่าว สุดท้ายพบว่าคนร้ายแก้ไขค่าในทะเบียนระบบส่วนที่ควบคุมกระบวนการล็อกอินของวินโดวส์ โดยเพิ่มชื่อไฟล์ของตนเข้าไปในค่าที่ระบบจะเรียกทำงานระหว่างขั้นตอนล็อกอิน ทำให้โปรแกรมของคนร้ายถูกเรียกขึ้นมาทุกครั้งที่มีผู้ใช้ล็อกอินเข้าเครื่องแม่ข่ายนั้น

*EN:* On 18 October 2567 a wholesale company filed a further report that the breach had reached the organisation's domain controller. Digital forensic examination found the offender using credentials discovered during the intrusion to open a remote screen connection directly into the domain controller. Evidence then showed the offender downloading a new program file onto the domain controller and running it over that connection. Finally the offender was found modifying the registry values controlling the Windows logon process, adding their own filename to the value the system runs during logon, so that the offender's program was launched every time a user logged in to that server.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1021 Remote Services | คนร้ายนำชื่อผู้ใช้และรหัสผ่านที่ค้นพบระหว่างการบุกรุกไปเปิดการเชื่อมต่อหน้าจอระยะไกลเข้าสู่เครื่องแม่ข่ายควบคุมโดเมนโดยตรง | Uses discovered credentials to RDP into the domain controller. This ability must be run by an agent running on the attacker-controlled machine (e.g. on the C2 server itself), since the RDP connection must originate from … |
| 2 | described | T1105 Ingress Tool Transfer | คนร้ายดาวน์โหลดไฟล์โปรแกรมชุดใหม่เข้ามาไว้บนเครื่องแม่ข่ายควบคุมโดเมนแล้วสั่งให้ทำงานผ่านการเชื่อมต่อดังกล่าว | Downloads a new agent executable and executes it on the domain controller over RDP. This ability must be run by an agent running on the attacker-controlled Linux machine (e.g. on the C2 server itself), since the RDP conn… |
| 3 | described | T1547 Boot or Logon Autostart Execution | คนร้ายแก้ไขค่าในทะเบียนระบบส่วนที่ควบคุมกระบวนการล็อกอินของวินโดวส์ โดยเพิ่มชื่อไฟล์ของตนเข้าไปในค่าที่ระบบจะเรียกทำงานระหว่างขั้นตอนล็อกอิน | Wizard Spider has established persistence using Userinit by adding the Registry key HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon. |

- [ ] ผ่าน / แก้แล้ว

## rcti_065 — OilRig (CTID emulation plan oilrig.yaml)

> เมื่อวันที่ 24 กรกฎาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการสำรวจข้อมูลในเครือข่ายเพิ่มขึ้นก่อนเกิดเหตุ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายเปิดอ่านค่าในทะเบียนระบบส่วนที่โปรแกรมเชื่อมต่อหน้าจอระยะไกลใช้เก็บประวัติเครื่องปลายทางที่ผู้ใช้เคยเชื่อมต่อไว้ เพื่อดูว่าผู้ใช้รายนั้นเคยเข้าใช้งานเครื่องใดบ้าง ต่อมาปรากฏหลักฐานว่าคนร้ายใช้คำสั่งพื้นฐานของระบบผ่านหน้าต่างคำสั่ง เรียกดูรายละเอียดของบัญชีผู้ใช้รายหนึ่งในโดเมนขององค์กรอย่างละเอียด จากนั้นได้เรียกดูรายชื่อสมาชิกของกลุ่มสิทธิ์ที่ดูแลระบบฐานข้อมูลขององค์กร สุดท้ายพบว่าคนร้ายใช้คำสั่งสอบถามชื่อโดเมนเพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายอีกเครื่องหนึ่งที่เป็นเป้าหมายถัดไป

*EN:* On 24 July 2567 an energy company filed a further report of increased reconnaissance on its network before the incident. Digital forensic examination found the offender reading the registry values in which the remote screen connection program stores the history of endpoints a user has connected to, in order to see which machines that user had accessed. Evidence then showed the offender using basic system commands through the command window to read detailed information about one user account in the organisation's domain, then reading the member list of the permission group administering the organisation's database systems. Finally the offender was found using a domain name lookup command to find the IP address of another server as their next target.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1012 Query Registry | คนร้ายเปิดอ่านค่าในทะเบียนระบบส่วนที่โปรแกรมเชื่อมต่อหน้าจอระยะไกลใช้เก็บประวัติเครื่องปลายทางที่ผู้ใช้เคยเชื่อมต่อไว้ เพื่อดูว่าผู้ใช้รายนั้นเคยเข้าใช้งานเครื่องใดบ้าง | Query the Windows registry key HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Default |
| 2 | described | T1087 Account Discovery | คนร้ายใช้คำสั่งพื้นฐานของระบบผ่านหน้าต่างคำสั่ง เรียกดูรายละเอียดของบัญชีผู้ใช้รายหนึ่งในโดเมนขององค์กรอย่างละเอียด | The net utility is executed via cmd to enumerate detailed information about the Gosta user account |
| 3 | described | T1069 Permission Groups Discovery | ได้เรียกดูรายชื่อสมาชิกของกลุ่มสิทธิ์ที่ดูแลระบบฐานข้อมูลขององค์กร | The net utility is executed via cmd to enumerate the "SQL Admins" group |
| 4 | described | T1018 Remote System Discovery | คนร้ายใช้คำสั่งสอบถามชื่อโดเมนเพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายอีกเครื่องหนึ่งที่เป็นเป้าหมายถัดไป | Perform DNS lookup for WATERFALLS |

- [ ] ผ่าน / แก้แล้ว

## rcti_066 — CISA AA22-321A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-321a>

> เมื่อวันที่ 21 พฤศจิกายน 2565 บริษัทแห่งหนึ่งแจ้งความว่าข้อมูลในระบบถูกเข้ารหัสลับทั้งหมดและไม่สามารถกู้คืนจากสำเนาสำรองได้ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายสั่งหยุดบริการที่ทำหน้าที่สร้างสำเนาเงาของไฟล์ และลบสำเนาเงาที่มีอยู่เดิมออกทั้งหมด โดยเรียกใช้ผ่านหน้าต่างคำสั่งและผ่านสคริปต์ ต่อมาปรากฏหลักฐานว่าคนร้ายลบไฟล์บันทึกเหตุการณ์ของวินโดวส์ทิ้ง โดยเจาะจงลบส่วนที่บันทึกเหตุการณ์ของระบบ เหตุการณ์ด้านความปลอดภัย และเหตุการณ์ของแอปพลิเคชัน จากนั้นก่อนลงมือเข้ารหัส พบว่าคนร้ายแก้ไขค่าในทะเบียนระบบเพื่อลบฐานข้อมูลลายเซ็นไวรัสและปิดการทำงานของโปรแกรมป้องกันไวรัสที่ติดตั้งอยู่ในเครื่องทั้งหมด ต่อมายังพบว่าข้อมูลของบริษัทถูกลำเลียงออกไปเก็บไว้ยังบริการรับฝากข้อมูลออนไลน์รายหนึ่งโดยใช้โปรแกรมคัดลอกไฟล์ที่คนร้ายนำเข้ามา สุดท้ายพบไฟล์ข้อความเรียกค่าไถ่ถูกวางไว้ในทุกโฟลเดอร์ที่ได้รับผลกระทบ พร้อมข้อความเตือนว่าห้ามแก้ไข เปลี่ยนชื่อ หรือลบไฟล์กุญแจ มิฉะนั้นจะกู้ข้อมูลคืนไม่ได้

*EN:* On 21 November 2565 a company reported that all data in its systems had been encrypted and could not be recovered from backups. Digital forensic examination found the offender stopping the service that creates shadow copies of files and deleting all existing shadow copies, invoked through the command window and through scripts. Evidence then showed the offender deleting Windows event log files, specifically those recording system events, security events and application events. Before encrypting, the offender was found modifying registry values to remove virus signature databases and disable every antivirus program installed on the machines. The company's data was then found moved out to an online storage service using a file copying program the offender brought in. Finally a ransom text file was found placed in every affected folder, warning that the key file must not be modified, renamed or deleted or the data could not be recovered.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1059 Command and Scripting Interpreter, T1490 Inhibit System Recovery | คนร้ายสั่งหยุดบริการที่ทำหน้าที่สร้างสำเนาเงาของไฟล์ และลบสำเนาเงาที่มีอยู่เดิมออกทั้งหมด โดยเรียกใช้ผ่านหน้าต่างคำสั่งและผ่านสคริปต์ | Stop the volume shadow copy services and remove all existing shadow copies via vssadmin on command line or via PowerShell |
| 2 | described | T1070 Indicator Removal | คนร้ายลบไฟล์บันทึกเหตุการณ์ของวินโดวส์ทิ้ง โดยเจาะจงลบส่วนที่บันทึกเหตุการณ์ของระบบ เหตุการณ์ด้านความปลอดภัย และเหตุการณ์ของแอปพลิเคชัน | Delete Windows event logs, specifically the System, Security and Application logs |
| 3 | described | T1112 Modify Registry | คนร้ายแก้ไขค่าในทะเบียนระบบเพื่อลบฐานข้อมูลลายเซ็นไวรัสและปิดการทำงานของโปรแกรมป้องกันไวรัสที่ติดตั้งอยู่ในเครื่องทั้งหมด | Prior to encryption, Hive ransomware removes virus definitions and disables all portions of Windows Defender and other common antivirus programs in the system registry |
| 4 | described | T1537 Transfer Data to Cloud Account | ข้อมูลของบริษัทถูกลำเลียงออกไปเก็บไว้ยังบริการรับฝากข้อมูลออนไลน์รายหนึ่งโดยใช้โปรแกรมคัดลอกไฟล์ที่คนร้ายนำเข้ามา | Hive actors exfiltrate data likely using a combination of Rclone and the cloud storage service Mega.nz |
| 5 | described | T1486 Data Encrypted for Impact | พบไฟล์ข้อความเรียกค่าไถ่ถูกวางไว้ในทุกโฟลเดอร์ที่ได้รับผลกระทบ พร้อมข้อความเตือนว่าห้ามแก้ไข เปลี่ยนชื่อ หรือลบไฟล์กุญแจ มิฉะนั้นจะกู้ข้อมูลคืนไม่ได้ | The ransom note, HOW_TO_DECRYPT.txt is dropped into each affected directory and states the *.key file cannot be modified, renamed, or deleted, otherwise the encrypted files cannot be recovered |

- [ ] ผ่าน / แก้แล้ว

## rcti_067 — CISA AA20-227A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-227a>

> เมื่อวันที่ 21 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ถูกฝังโปรแกรมขโมยรหัสผ่าน จากการตรวจสอบทะเบียนระบบพบว่าคนร้ายเพิ่มรายการเรียกใช้งานโปรแกรมของตนไว้ใน Registry Run Key และในโฟลเดอร์เริ่มต้นระบบ เพื่อให้โปรแกรมถูกเรียกทำงานเองทุกครั้งที่เปิดเครื่องหรือผู้ใช้ล็อกอิน ต่อมาปรากฏหลักฐานว่าคนร้ายใช้วิธีหลบเลี่ยงกลไกที่ระบบใช้ถามยืนยันก่อนยกระดับสิทธิ์ ทำให้โปรแกรมของตนทำงานด้วยสิทธิ์ผู้ดูแลระบบได้โดยผู้ใช้ไม่ทันสังเกตและไม่มีหน้าต่างขออนุญาตปรากฏขึ้น สุดท้ายพบว่าโปรแกรมดังกล่าวเข้าไปอ่าน Credentials from Web Browsers คือชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของผู้เสียหายบันทึกเก็บไว้ในเครื่อง แล้วส่งออกไปยังคนร้าย

*EN:* On 21 August 2563 an agency reported that a staff computer had been implanted with a password-stealing program. Examination of the system registry found the offender adding entries launching their program to the Registry Run Key and the startup folder, so it would run by itself every time the machine started or the user logged in. Evidence then showed the offender using a method to bypass the mechanism the system uses to ask for confirmation before elevating privileges, letting their program run with administrator rights without the user noticing and without any permission dialog appearing. Finally that program was found reading Credentials from Web Browsers — the usernames and passwords the victim's web browser had saved on the machine — and sending them out to the offender.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1547 Boot or Logon Autostart Execution | คนร้ายเพิ่มรายการเรียกใช้งานโปรแกรมของตนไว้ใน Registry Run Key และในโฟลเดอร์เริ่มต้นระบบ เพื่อให้โปรแกรมถูกเรียกทำงานเองทุกครั้งที่เปิดเครื่องหรือผู้ใช้ล็อกอิน | Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder |
| 2 | described | T1548 Abuse Elevation Control Mechanism | คนร้ายใช้วิธีหลบเลี่ยงกลไกที่ระบบใช้ถามยืนยันก่อนยกระดับสิทธิ์ ทำให้โปรแกรมของตนทำงานด้วยสิทธิ์ผู้ดูแลระบบได้โดยผู้ใช้ไม่ทันสังเกตและไม่มีหน้าต่างขออนุญาตปรากฏขึ้น | Abuse Elevation Control Mechanism: Bypass User Access Control |
| 3 | named | T1555 Credentials from Password Stores | โปรแกรมดังกล่าวเข้าไปอ่าน Credentials from Web Browsers คือชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของผู้เสียหายบันทึกเก็บไว้ในเครื่อง แล้วส่งออกไปยังคนร้าย | Credentials from Password Stores: Credentials from Web Browsers |

- [ ] ผ่าน / แก้แล้ว

## rcti_068 — FIN6 (CTID emulation plan FIN6.yaml)

ต้นทาง: <https://www.fireeye.com/blog/threat-research/2019/04/pick-six-intercepting-a-fin6-intrusion.html>

> เมื่อวันที่ 11 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าข้อมูลที่รวบรวมไว้ถูกส่งออกนอกองค์กรและมีการลุกลามไปยังเครื่องอื่น จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายเปิดการเชื่อมต่อแบบโต้ตอบไปยังเครื่องแม่ข่ายภายนอกองค์กร แล้วใช้โปรแกรมคัดลอกไฟล์ผ่านช่องทางเข้ารหัสลำเลียงข้อมูลที่รวบรวมไว้ออกไปเก็บบนพื้นที่จัดเก็บของเครื่องปลายทางนั้น ต่อมาปรากฏหลักฐานว่าคนร้ายใช้เครื่องมือสั่งงานระยะไกลสร้างบริการของระบบขึ้นบนเครื่องปลายทางในเครือข่าย เพื่อสั่งรันคำสั่งบนเครื่องนั้นจากระยะไกล สุดท้ายพบว่าคนร้ายยังใช้กลไกบริหารจัดการเครื่องของวินโดวส์สั่งให้กระบวนการทำงานขึ้นบนเครื่องปลายทางอีกเครื่องหนึ่ง โดยระบุหมายเลขเครื่องปลายทางเป็นพารามิเตอร์ในคำสั่ง

*EN:* On 11 May 2567 a retail chain filed a further report that collected data had been sent outside the organisation and that the intrusion had spread to other machines. Digital forensic examination found the offender opening an interactive connection to a server outside the organisation, then using a file copying program over an encrypted channel to move the collected data out to that endpoint's storage. Evidence then showed the offender using a remote command tool to create a system service on a target machine on the network in order to run commands on it remotely. Finally the offender was found using the Windows machine management mechanism to start a process on another target machine, specifying the target machine's address as a parameter in the command.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1567 Exfiltration Over Web Service | คนร้ายเปิดการเชื่อมต่อแบบโต้ตอบไปยังเครื่องแม่ข่ายภายนอกองค์กร แล้วใช้โปรแกรมคัดลอกไฟล์ผ่านช่องทางเข้ารหัสลำเลียงข้อมูลที่รวบรวมไว้ออกไปเก็บบนพื้นที่จัดเก็บของเครื่องปลายทางนั้น | Initiate an interactive SSH session with a remote server with pscp Initiate an interactive SSH session with a remote server |
| 2 | described | T1569 System Services | คนร้ายใช้เครื่องมือสั่งงานระยะไกลสร้างบริการของระบบขึ้นบนเครื่องปลายทางในเครือข่าย เพื่อสั่งรันคำสั่งบนเครื่องนั้นจากระยะไกล | Use PsExec to execute a command on a remote host. FIN6 is reported to have used a variant of PsExec to execute code on remote hosts. |
| 3 | described | T1047 Windows Management Instrumentation | คนร้ายยังใช้กลไกบริหารจัดการเครื่องของวินโดวส์สั่งให้กระบวนการทำงานขึ้นบนเครื่องปลายทางอีกเครื่องหนึ่ง โดยระบุหมายเลขเครื่องปลายทางเป็นพารามิเตอร์ในคำสั่ง | WMIC to execute a process on a remote host. Specify the remote IP using node parameter. FIN6 is reported to have used WMI to execute code on remote systems. |

- [ ] ผ่าน / แก้แล้ว

## rcti_069 — CISA AA23-319A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-319a>

> เมื่อวันที่ 17 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดเครื่องมือที่คนร้ายใช้ก่อนลงมือเข้ารหัสลับข้อมูล จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายใช้ไฟล์แบตช์เป็นตัวนำไฟล์สคริปต์ไปวางไว้บนเครื่องของผู้เสียหายหลายเครื่อง เพื่อเตรียมการก่อนปล่อยโปรแกรมเรียกค่าไถ่ ต่อมาปรากฏหลักฐานว่าคนร้ายใช้เครื่องมือหนึ่งลบไฟล์บันทึกเหตุการณ์ของวินโดวส์ออกเป็นจำนวนมาก ทั้งส่วนที่บันทึกเหตุการณ์ของระบบ ของแอปพลิเคชัน และด้านความปลอดภัย สุดท้ายพบว่าคนร้ายติดตั้งซอฟต์แวร์ควบคุมเครื่องระยะไกลที่มีจำหน่ายทั่วไปและใช้งานกันตามปกติในองค์กร เพื่อใช้เป็นช่องทางเข้าถึงเครื่องของผู้เสียหายและคงการเข้าถึงไว้โดยไม่ให้ผิดสังเกต

*EN:* On 17 November 2566 a hospital filed a further report detailing the tools the offender used before encrypting the data. Digital forensic examination found the offender using a batch file to place script files on several of the victim's machines in preparation for releasing the ransom program. Evidence then showed the offender using a tool to delete large numbers of Windows event log files, covering system, application and security events. Finally the offender was found installing commercially available remote machine control software of the kind organisations use routinely, as a channel to reach the victim's machines and maintain access without arousing suspicion.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1059 Command and Scripting Interpreter | คนร้ายใช้ไฟล์แบตช์เป็นตัวนำไฟล์สคริปต์ไปวางไว้บนเครื่องของผู้เสียหายหลายเครื่อง เพื่อเตรียมการก่อนปล่อยโปรแกรมเรียกค่าไถ่ | A batch script likely used to place 1.ps1 on victim systems for ransomware staging purposes |
| 2 | described | T1070 Indicator Removal | คนร้ายใช้เครื่องมือหนึ่งลบไฟล์บันทึกเหตุการณ์ของวินโดวส์ออกเป็นจำนวนมาก ทั้งส่วนที่บันทึกเหตุการณ์ของระบบ ของแอปพลิเคชัน และด้านความปลอดภัย | Rhysida actors used this tool to clear a significant number of Windows event logs, including system, application, and security logs |
| 3 | described | T1219 Remote Access Tools | คนร้ายติดตั้งซอฟต์แวร์ควบคุมเครื่องระยะไกลที่มีจำหน่ายทั่วไปและใช้งานกันตามปกติในองค์กร เพื่อใช้เป็นช่องทางเข้าถึงเครื่องของผู้เสียหายและคงการเข้าถึงไว้โดยไม่ให้ผิดสังเกต | A common software that can be maliciously used by threat actors to obtain remote access and maintain persistence |

- [ ] ผ่าน / แก้แล้ว

## rcti_070 — Carbanak (CTID emulation plan Carbanak.yaml)

ต้นทาง: <https://securelist.com/the-great-bank-robbery-the-carbanak-apt/68732/>

> เมื่อวันที่ 20 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการเชื่อมต่อผิดปกติจากเครื่องแม่ข่ายภายในออกสู่ภายนอก จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายอาศัยการสอบถามชื่อโดเมนเป็นช่องทางห่อหุ้มการติดต่อสั่งการของตนไว้ภายใน ทำให้ข้อมูลคำสั่งไหลผ่านออกไปได้โดยอุปกรณ์ตรวจจับมองเห็นเป็นเพียงการสอบถามชื่อโดเมนตามปกติ ต่อมาปรากฏหลักฐานว่าคนร้ายรันคำสั่งตรวจสอบสถานะเซสชันบนเครื่องปลายทาง เพื่อดูว่าผู้บริหารฝ่ายการเงินกำลังล็อกอินใช้งานเครื่องของตนอยู่หรือไม่ สุดท้ายพบว่าคนร้ายอัปโหลดไฟล์โปรแกรมและไฟล์สคริปต์ขึ้นไปวางไว้บนเครื่องของผู้บริหารรายนั้น โดยตั้งชื่อไฟล์ให้ดูเหมือนตัวปรับปรุงซอฟต์แวร์ทั่วไปเพื่อไม่ให้ถูกลบอัตโนมัติหลังทำงานเสร็จ

*EN:* On 20 June 2567 a commercial bank filed a further report of unusual connections from an internal server out to the internet. Digital forensic examination found the offender using domain name queries as a channel wrapping their own command traffic inside, so that command data flowed out while detection devices saw only ordinary domain name lookups. Evidence then showed the offender running a command to check session status on a target machine, to see whether the chief financial officer was logged in and using their workstation. Finally the offender was found uploading a program file and a script file onto that executive's machine, named to look like an ordinary software updater so they would not be removed automatically after running.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1572 Protocol Tunneling | คนร้ายอาศัยการสอบถามชื่อโดเมนเป็นช่องทางห่อหุ้มการติดต่อสั่งการของตนไว้ภายใน ทำให้ข้อมูลคำสั่งไหลผ่านออกไปได้โดยอุปกรณ์ตรวจจับมองเห็นเป็นเพียงการสอบถามชื่อโดเมนตามปกติ | The nslookup utility is used to find the IP address of bankdc |
| 2 | described | T1033 System Owner/User Discovery | คนร้ายรันคำสั่งตรวจสอบสถานะเซสชันบนเครื่องปลายทาง เพื่อดูว่าผู้บริหารฝ่ายการเงินกำลังล็อกอินใช้งานเครื่องของตนอยู่หรือไม่ | Use qwinsta to check if the CFO user is logged into their workstation |
| 3 | described | T1105 Ingress Tool Transfer | คนร้ายอัปโหลดไฟล์โปรแกรมและไฟล์สคริปต์ขึ้นไปวางไว้บนเครื่องของผู้บริหารรายนั้น โดยตั้งชื่อไฟล์ให้ดูเหมือนตัวปรับปรุงซอฟต์แวร์ทั่วไปเพื่อไม่ให้ถูกลบอัตโนมัติหลังทำงานเสร็จ | Upload JavaUpdater.exe and Create JavaUpdater.vbs on CFO. Files renamed to prevent auto-removal after execution of step |

- [ ] ผ่าน / แก้แล้ว

## rcti_071 — FIN6 (CTID emulation plan FIN6.yaml)

ต้นทาง: <https://blog.morphisec.com/new-global-attack-on-point-of-sale-systems>

> เมื่อวันที่ 19 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายใช้คงอยู่ในระบบและนำข้อมูลออก จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายสั่งคำสั่งผ่านหน้าต่างคำสั่งของระบบเพื่อเพิ่มรายการเรียกใช้งานโปรแกรมของตนไว้ในทะเบียนระบบ ทำให้โปรแกรมทำงานเองทุกครั้งที่เปิดเครื่อง ต่อมาปรากฏหลักฐานว่าคนร้ายสั่งคำสั่งผ่านหน้าต่างคำสั่งอีกครั้งเพื่อสร้างงานตั้งเวลาขึ้นในระบบ เป็นกลไกสำรองอีกชั้นหนึ่งไว้เรียกโปรแกรมของตนหากรายการในทะเบียนระบบถูกลบ สุดท้ายพบว่าคนร้ายใช้สคริปต์ลำเลียงข้อมูลบัตรที่รวบรวมได้จากเครื่องรับชำระเงินออกไปภายนอก โดยซุกข้อมูลไว้ในคำขอสอบถามชื่อโดเมนที่ทยอยส่งออกไปทีละน้อย ซึ่งเป็นคนละช่องทางกับที่ใช้รับคำสั่งและไม่ได้เข้ารหัสลับเนื้อหา

*EN:* On 19 May 2567 a retail chain filed a further report on how the offender persisted in the system and took data out. Digital forensic examination found the offender issuing commands through the system command window to add an entry launching their program into the system registry, so it would run by itself every time the machine started. Evidence then showed the offender issuing commands through the command window again to create a timed job in the system as a second, backup mechanism for launching their program if the registry entry were removed. Finally the offender was found using a script to move the card data collected from the payment terminals out of the organisation, tucking the data into domain name query requests sent out a little at a time — a different channel from the one used to receive commands, and one that did not encrypt the content.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1547 Boot or Logon Autostart Execution | คนร้ายสั่งคำสั่งผ่านหน้าต่างคำสั่งของระบบเพื่อเพิ่มรายการเรียกใช้งานโปรแกรมของตนไว้ในทะเบียนระบบ ทำให้โปรแกรมทำงานเองทุกครั้งที่เปิดเครื่อง | FIN6 utilizes cmd to execute Registry Run Keys |
| 2 | described | T1053 Scheduled Task/Job | คนร้ายสั่งคำสั่งผ่านหน้าต่างคำสั่งอีกครั้งเพื่อสร้างงานตั้งเวลาขึ้นในระบบ เป็นกลไกสำรองอีกชั้นหนึ่งไว้เรียกโปรแกรมของตนหากรายการในทะเบียนระบบถูกลบ | FIN6 utilizes cmd to execute Scheduled Tasks |
| 3 | described | T1048 Exfiltration Over Alternative Protocol | คนร้ายใช้สคริปต์ลำเลียงข้อมูลบัตรที่รวบรวมได้จากเครื่องรับชำระเงินออกไปภายนอก โดยซุกข้อมูลไว้ในคำขอสอบถามชื่อโดเมนที่ทยอยส่งออกไปทีละน้อย ซึ่งเป็นคนละช่องทางกับที่ใช้รับคำสั่งและไม่ได้เข้ารหัสลับเนื้อหา | Powershell to execute POS data exfiltration over DNS tunnel via dnscat2 |

- [ ] ผ่าน / แก้แล้ว

## rcti_072 — APT29 (CTID emulation plan APT29.yaml)

ต้นทาง: <https://community.broadcom.com/symantecenterprise/communities/community-home/librarydocuments/viewdocument?DocumentKey=6ab66701-25d7-4685-ae9d-93d63708a11c&CommunityKey=1ecf5f55-9545-44d6-b0f4-4e4a7f5f5e68&tab=librarydocuments>

> เมื่อวันที่ 4 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนสุดท้ายก่อนคนร้ายถอนตัว จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายสั่งลบไฟล์ที่ตนเคยรวบรวมพักไว้บนเครื่องออกอย่างถาวร โดยใช้วิธีเขียนทับเนื้อที่บนดิสก์เพื่อไม่ให้กู้คืนเนื้อหากลับมาได้ ต่อมาปรากฏหลักฐานว่าคนร้ายรันเครื่องมือทำ Credential Dumping เก็บรวบรวมรหัสผ่านของบัญชีผู้ใช้บนเครื่องอีกรอบก่อนออกจากระบบ สุดท้ายพบว่าคนร้ายสั่งรีสตาร์ตเครื่อง เพื่อกระตุ้นให้รายการที่ฝังไว้ในทะเบียนระบบทำงาน โดยรายการดังกล่าวกำหนดให้เรียกไฟล์ของคนร้ายผ่านโปรแกรมช่วยเรียกไลบรารีที่ติดมากับระบบปฏิบัติการวินโดวส์ ซึ่งเป็นโปรแกรมที่มีลายเซ็นถูกต้องจึงไม่ถูกโปรแกรมป้องกันสงสัย

*EN:* On 4 March 2567 a foreign affairs agency filed a further report on the final steps before the offender withdrew. Digital forensic examination found the offender permanently deleting the files they had staged on the machine, overwriting the disk space so the contents could not be recovered. Evidence then showed the offender running a Credential Dumping tool to collect the machine's account passwords once more before leaving. Finally the offender was found restarting the machine to trigger the entry they had planted in the system registry, that entry being configured to invoke the offender's file through a library-loading helper program shipped with the Windows operating system — a correctly signed program and therefore not suspected by protection software.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1561 Disk Wipe | คนร้ายสั่งลบไฟล์ที่ตนเคยรวบรวมพักไว้บนเครื่องออกอย่างถาวร โดยใช้วิธีเขียนทับเนื้อที่บนดิสก์เพื่อไม่ให้กู้คืนเนื้อหากลับมาได้ | Securely delete previously staged files. |
| 2 | named | T1003 OS Credential Dumping | คนร้ายรันเครื่องมือทำ Credential Dumping เก็บรวบรวมรหัสผ่านของบัญชีผู้ใช้บนเครื่องอีกรอบก่อนออกจากระบบ | Perfofrm Mimikatz credential collection |
| 3 | described | T1218 System Binary Proxy Execution | รายการดังกล่าวกำหนดให้เรียกไฟล์ของคนร้ายผ่านโปรแกรมช่วยเรียกไลบรารีที่ติดมากับระบบปฏิบัติการวินโดวส์ ซึ่งเป็นโปรแกรมที่มีลายเซ็นถูกต้องจึงไม่ถูกโปรแกรมป้องกันสงสัย | Trigger RegKey persistence by rebooting the machine |

- [ ] ผ่าน / แก้แล้ว

## rcti_073 — APT29 (CTID emulation plan APT29.yaml)

ต้นทาง: <https://blog-assets.f-secure.com/wp-content/uploads/2020/03/18122307/F-Secure_Dukes_Whitepaper.pdf>

> เมื่อวันที่ 26 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการสำรวจข้อมูลภายในเครื่องอย่างเป็นระบบก่อนเกิดเหตุ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายเรียกดูรายการโปรแกรมที่กำลังทำงานอยู่บนเครื่อง ทั้งโดยเรียกผ่านฟังก์ชันของระบบโดยตรงและโดยรันคำสั่งผ่านหน้าต่างคำสั่ง ต่อมาได้เรียกดูรายการบริการเบื้องหลังที่กำลังทำงานอยู่บนเครื่องนั้น จากนั้นเรียกดูการตั้งค่าของระบบปฏิบัติการที่ติดตั้งอยู่โดยละเอียด ต่อมาปรากฏหลักฐานว่าคนร้ายแจกแจงรายชื่อสมาชิกของกลุ่มผู้ดูแลระบบทั้งบนเครื่องนั้น บนเครื่องแม่ข่ายควบคุมโดเมน และในระดับโดเมนขององค์กร แล้วยังแจกแจงรายชื่อบัญชีผู้ใช้ในโดเมนพร้อมเรียกดูรายละเอียดของบัญชีที่สนใจเป็นรายบัญชี สุดท้ายพบว่าคนร้ายเปิดอ่านค่าในทะเบียนระบบส่วนที่กำหนดนโยบายความปลอดภัยของเครื่อง เพื่อยืนยันว่าเมื่อยกระดับสิทธิ์แล้วระบบจะไม่แสดงหน้าต่างถามรหัสผ่านจากผู้ใช้

*EN:* On 26 February 2567 a foreign affairs agency filed a further report of systematic on-machine reconnaissance before the incident. Digital forensic examination found the offender reading the list of programs running on the machine, both by calling system functions directly and by running commands through the command window. They then read the list of background services running on that machine, then read the installed operating system's configuration in detail. Evidence then showed the offender enumerating the members of the administrators group on that machine, on the domain controller, and at the organisation's domain level, then enumerating the domain's user accounts and reading details of accounts of interest one by one. Finally the offender was found reading the registry values defining the machine's security policy, to confirm that on elevating privileges the system would not display a password prompt to the user.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1057 Process Discovery | คนร้ายเรียกดูรายการโปรแกรมที่กำลังทำงานอยู่บนเครื่อง ทั้งโดยเรียกผ่านฟังก์ชันของระบบโดยตรงและโดยรันคำสั่งผ่านหน้าต่างคำสั่ง | API call(s) are executed to enumerate local running processes. The tasklist utility is executed via cmd to enumerate local running processes. |
| 2 | described | T1007 System Service Discovery | ได้เรียกดูรายการบริการเบื้องหลังที่กำลังทำงานอยู่บนเครื่องนั้น | The sc utility is executed via cmd to enumerate local active services. The net utility is executed via cmd to enumerate local active services. |
| 3 | described | T1082 System Information Discovery | เรียกดูการตั้งค่าของระบบปฏิบัติการที่ติดตั้งอยู่โดยละเอียด | The systeminfo utility is executed via cmd to enumerate local operating system configuration. The net utility is executed via cmd to enumerate local operating system configuration. |
| 4 | described | T1069 Permission Groups Discovery | คนร้ายแจกแจงรายชื่อสมาชิกของกลุ่มผู้ดูแลระบบทั้งบนเครื่องนั้น บนเครื่องแม่ข่ายควบคุมโดเมน และในระดับโดเมนขององค์กร | The net utility is executed via cmd to enumerate members of the local system's administrators group. The net utility is executed via cmd to enumerate members of the domain controller’s administrators group. The net utili… |
| 5 | described | T1087 Account Discovery | แจกแจงรายชื่อบัญชีผู้ใช้ในโดเมนพร้อมเรียกดูรายละเอียดของบัญชีที่สนใจเป็นรายบัญชี | The net utility is executed via cmd to enumerate domain user accounts. The net utility is executed via cmd to enumerate detailed information about a specific user account. |
| 6 | described | T1012 Query Registry | คนร้ายเปิดอ่านค่าในทะเบียนระบบส่วนที่กำหนดนโยบายความปลอดภัยของเครื่อง เพื่อยืนยันว่าเมื่อยกระดับสิทธิ์แล้วระบบจะไม่แสดงหน้าต่างถามรหัสผ่านจากผู้ใช้ | The reg utility is executed via cmd to enumerate a specific Registry key associated with local system policies to ensure that the user will not be prompted for credentials when elevating permissions. |

- [ ] ผ่าน / แก้แล้ว

## rcti_074 — Turla - Snake (CTID emulation plan turla_snake.yaml)

> เมื่อวันที่ 4 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ติดโปรแกรมไม่พึงประสงค์หลังเข้าเว็บไซต์ข่าวต่างประเทศ จากการตรวจสอบพบว่าขณะที่เจ้าหน้าที่เปิดเว็บไซต์ดังกล่าวผ่านโปรแกรมท่องเว็บ ระบบได้เปลี่ยนเส้นทางไปยังเว็บไซต์อีกแห่งที่มีชื่อคล้ายกันซึ่งคนร้ายจัดทำขึ้น และแสดงข้อความชวนให้ดาวน์โหลดไฟล์ปรับปรุงโปรแกรม ต่อมาปรากฏหลักฐานว่าเจ้าหน้าที่ได้เปิดไฟล์ที่ดาวน์โหลดมานั้นด้วยตนเองผ่านช่องสั่งเรียกโปรแกรมของระบบ ทำให้โปรแกรมอันตรายที่แนบมากับไฟล์เริ่มทำงานบนเครื่อง สุดท้ายเมื่อโปรแกรมติดต่อกลับไปยังเครื่องสั่งการของคนร้ายผ่านเครื่องพักสัญญาณได้สำเร็จ พบว่ามีการเก็บรวบรวมข้อมูลรายละเอียดของเครื่องเป้าหมายและรายชื่อเครื่องคอมพิวเตอร์อื่นในโดเมนขององค์กรส่งกลับออกไป

*EN:* On 4 September 2566 a government agency reported that a staff computer had been infected after visiting a foreign news website. Examination found that while the officer had that site open in their browser, the system redirected to another, similarly named site set up by the offender, which displayed a message inviting them to download a program update file. Evidence then showed the officer opening the downloaded file themselves through the system's run box, starting the malicious program bundled with the file. Finally, once the program successfully contacted the offender's command machine through a relay, information about the target machine and the list of other computers in the organisation's domain was found being collected and sent back out.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1189 Drive-by Compromise | ขณะที่เจ้าหน้าที่เปิดเว็บไซต์ดังกล่าวผ่านโปรแกรมท่องเว็บ ระบบได้เปลี่ยนเส้นทางไปยังเว็บไซต์อีกแห่งที่มีชื่อคล้ายกันซึ่งคนร้ายจัดทำขึ้น และแสดงข้อความชวนให้ดาวน์โหลดไฟล์ปรับปรุงโปรแกรม | Use xdotool to open Microsoft Edge, browse to nato-int.com. After redirection to anto-int.com, click to download the update (NFVersion_5e.exe) bundled with EPIC (a.k.a. Tavdig/Wipbot). |
| 2 | described | T1204 User Execution | เจ้าหน้าที่ได้เปิดไฟล์ที่ดาวน์โหลดมานั้นด้วยตนเองผ่านช่องสั่งเรียกโปรแกรมของระบบ ทำให้โปรแกรมอันตรายที่แนบมากับไฟล์เริ่มทำงานบนเครื่อง | Run the downloaded malicious update via win+r, wait for it to finish running. |
| 3 | described | T1082 System Information Discovery | มีการเก็บรวบรวมข้อมูลรายละเอียดของเครื่องเป้าหมายและรายชื่อเครื่องคอมพิวเตอร์อื่นในโดเมนขององค์กรส่งกลับออกไป | Once C2 communications have been established between EPIC and the C2 via the proxy server, discovery is performed on the first host where information about the host device and domain computers is collected. |

- [ ] ผ่าน / แก้แล้ว

## rcti_075 — APT29 (CTID emulation plan APT29.yaml)

ต้นทาง: <https://www.slideshare.net/MatthewDunwoody1/no-easy-breach-derby-con-2016>

> เมื่อวันที่ 1 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายยกระดับสิทธิ์บนเครื่องที่ยึดครองได้ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายนำไฟล์ที่จะใช้ขยายการเข้าถึงไปพักไว้ในตำแหน่งและตั้งชื่อให้ตรงกับไฟล์ที่ถูกต้องของระบบ เพื่อให้กลมกลืนไปกับไฟล์อื่นในโฟลเดอร์เดียวกัน ต่อมาปรากฏหลักฐานว่าคนร้ายรันชุดคำสั่งที่ขโมยสิทธิ์ประจำตัวจากกระบวนการที่ทำงานอยู่ด้วยสิทธิ์สูง แล้วนำสิทธิ์นั้นไปเปิดโปรแกรมควบคุมระยะไกลตัวใหม่ขึ้นมาทำงานด้วยระดับสิทธิ์เดียวกัน สุดท้ายพบว่าคนร้ายแก้ไขค่าในทะเบียนระบบส่วนที่เกี่ยวกับเครื่องมือสำรองและกู้คืนข้อมูลของวินโดวส์ เพื่อหลบเลี่ยงกลไกที่ระบบใช้ถามยืนยันก่อนอนุญาตให้โปรแกรมทำงานด้วยสิทธิ์ผู้ดูแลระบบ

*EN:* On 1 March 2567 a foreign affairs agency filed a further report on how the offender escalated privileges on the compromised machine. Digital forensic examination found the offender staging the file they would use to widen access in a location and under a name matching a legitimate system file, so it blended in with the other files in that folder. Evidence then showed the offender running instructions that stole the identity token of a process running with high privileges and used it to launch a new remote control program at the same privilege level. Finally the offender was found modifying registry values relating to the Windows backup and recovery tool in order to bypass the mechanism the system uses to ask for confirmation before allowing a program to run with administrator rights.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1036 Masquerading | คนร้ายนำไฟล์ที่จะใช้ขยายการเข้าถึงไปพักไว้ในตำแหน่งและตั้งชื่อให้ตรงกับไฟล์ที่ถูกต้องของระบบ เพื่อให้กลมกลืนไปกับไฟล์อื่นในโฟลเดอร์เดียวกัน | Staging PNG for Lateral Movement |
| 2 | described | T1134 Access Token Manipulation | คนร้ายรันชุดคำสั่งที่ขโมยสิทธิ์ประจำตัวจากกระบวนการที่ทำงานอยู่ด้วยสิทธิ์สูง แล้วนำสิทธิ์นั้นไปเปิดโปรแกรมควบคุมระยะไกลตัวใหม่ขึ้นมาทำงานด้วยระดับสิทธิ์เดียวกัน | A UAC bypass technique is executed to steal the token of an existing high-integrity process and launch a new, high-integrity RAT with limited functionality. |
| 3 | described | T1548 Abuse Elevation Control Mechanism | คนร้ายแก้ไขค่าในทะเบียนระบบส่วนที่เกี่ยวกับเครื่องมือสำรองและกู้คืนข้อมูลของวินโดวส์ เพื่อหลบเลี่ยงกลไกที่ระบบใช้ถามยืนยันก่อนอนุญาตให้โปรแกรมทำงานด้วยสิทธิ์ผู้ดูแลระบบ | Modify registry values of sdclt to bypass UAC |

- [ ] ผ่าน / แก้แล้ว

## rcti_076 — CISA AA21-200A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-200a>

> เมื่อวันที่ 19 กรกฎาคม 2564 หน่วยงานแห่งหนึ่งแจ้งความว่าถูกลักลอบเข้าถึงข้อมูลภายในต่อเนื่องเป็นเวลานาน จากการตรวจสอบพบว่าคนร้ายเข้าถึงเครือข่ายขององค์กรผ่าน External Remote Services เช่น บริการเชื่อมต่อเครือข่ายส่วนตัวเสมือนที่เปิดให้พนักงานใช้จากภายนอก ต่อมาปรากฏหลักฐานว่าคนร้ายส่งเอกสารล่อลวงถึงเจ้าหน้าที่ ซึ่งเมื่อเปิดขึ้นมาจะอาศัยช่องโหว่ของโปรแกรมอ่านเอกสารบนเครื่องผู้ใช้ในการสั่งรันชุดคำสั่งและวางโปรแกรมอันตรายลงเครื่อง จากนั้นจากการตรวจสอบวิธีนำข้อมูลออกพบว่าคนร้ายซ่อนข้อมูลที่ขโมยได้ไว้ภายในไฟล์อื่นที่ดูเหมือนไฟล์ปกติ แล้วนำไปฝากไว้บนบริการเก็บซอร์สโค้ดสาธารณะ ต่อมายังพบว่าคนร้ายปลอมรูปแบบการติดต่อให้เหมือนการใช้งานปกติ โดยใช้กุญแจเรียกใช้บริการของผู้ให้บริการรับฝากไฟล์รายหนึ่งประกอบในคำสั่งอัปโหลดข้อมูลที่ขโมยมา ทำให้ดูเหมือนเป็นการใช้บริการนั้นตามปกติ อันเข้าลักษณะ Protocol Impersonation สุดท้ายพบว่าคนร้ายใช้ Protocol Tunneling ห่อหุ้มการติดต่อไว้ภายในโพรโทคอลอื่น ร่วมกับการส่งต่อการเชื่อมต่อผ่านเครื่องพักสัญญาณหลายทอดรวมถึงเครือข่ายนิรนาม

*EN:* On 19 July 2564 an agency reported prolonged covert access to its internal data. Examination found the offender reaching the organisation's network through External Remote Services such as the virtual private network service opened for staff to use from outside. Evidence then showed the offender sending lure documents to officers which, when opened, used vulnerabilities in the document reader on the user's machine to run instructions and drop a malicious program. Examination of how data was taken out found the offender hiding stolen data inside other, ordinary-looking files and depositing them on a public source code hosting service. The offender was also found imitating normal traffic patterns, using a file hosting provider's API keys in the commands uploading stolen data so it looked like ordinary use of that service, matching Protocol Impersonation. Finally the offender was found using Protocol Tunneling to wrap their traffic inside another protocol, together with relaying connections through multiple hops including an anonymity network.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1133 External Remote Services | คนร้ายเข้าถึงเครือข่ายขององค์กรผ่าน External Remote Services เช่น บริการเชื่อมต่อเครือข่ายส่วนตัวเสมือนที่เปิดให้พนักงานใช้จากภายนอก | External remote services (e.g., virtual private network [VPN] services) |
| 2 | described | T1203 Exploitation for Client Execution | คนร้ายส่งเอกสารล่อลวงถึงเจ้าหน้าที่ ซึ่งเมื่อเปิดขึ้นมาจะอาศัยช่องโหว่ของโปรแกรมอ่านเอกสารบนเครื่องผู้ใช้ในการสั่งรันชุดคำสั่งและวางโปรแกรมอันตรายลงเครื่อง | Exploitation of software vulnerabilities in client applications to execute code using lure documents that dropped malware exploiting various Common Vulnerabilities and Exposures (CVEs) |
| 3 | described | T1027 Obfuscated Files or Information | คนร้ายซ่อนข้อมูลที่ขโมยได้ไว้ภายในไฟล์อื่นที่ดูเหมือนไฟล์ปกติ แล้วนำไปฝากไว้บนบริการเก็บซอร์สโค้ดสาธารณะ | Use of steganography to hide stolen data inside other files stored on GitHub |
| 4 | named | T1001 Data Obfuscation | คนร้ายปลอมรูปแบบการติดต่อให้เหมือนการใช้งานปกติ โดยใช้กุญแจเรียกใช้บริการของผู้ให้บริการรับฝากไฟล์รายหนึ่งประกอบในคำสั่งอัปโหลดข้อมูลที่ขโมยมา ทำให้ดูเหมือนเป็นการใช้บริการนั้นตามปกติ อันเข้าลักษณะ Protocol Impersonation | Protocol impersonation by using Application Programming Interface (API) keys for Dropbox accounts in commands to upload stolen data to make it appear that the activity was a legitimate use of the Dropbox service |
| 5 | named | T1572 Protocol Tunneling, T1090 Proxy | คนร้ายใช้ Protocol Tunneling ห่อหุ้มการติดต่อไว้ภายในโพรโทคอลอื่น ร่วมกับการส่งต่อการเชื่อมต่อผ่านเครื่องพักสัญญาณหลายทอดรวมถึงเครือข่ายนิรนาม | Protocol tunneling and multi-hop proxies , including the use of Tor [S0183] |

- [ ] ผ่าน / แก้แล้ว

## rcti_077 — Turla - Snake (CTID emulation plan turla_snake.yaml)

> เมื่อวันที่ 25 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกได้ลุกลามจากเครื่องแรกไปยังเครื่องแม่ข่ายเก็บไฟล์ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าโปรแกรมฝังตัวบนเครื่องแรกได้รับคำสั่งให้ดาวน์โหลดเครื่องมือสำหรับสั่งงานเครื่องระยะไกล และดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดที่สองเข้ามาเก็บไว้ ต่อมาปรากฏหลักฐานว่าคนร้ายสั่งรันเครื่องมือดังกล่าวในนามของบัญชีผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์ ทำให้ตัวติดตั้งถูกเรียกทำงานบนเครื่องแม่ข่ายเก็บไฟล์ผ่านการสร้างบริการของระบบขึ้นบนเครื่องนั้น สุดท้ายเมื่อโปรแกรมฝังตัวบนเครื่องใหม่ติดต่อกลับมาได้แล้ว พบว่าคนร้ายสั่งลบไฟล์ที่เคยนำเข้าไปวางไว้บนเครื่องแรกออกทั้งหมดเพื่อเก็บกวาดร่องรอย

*EN:* On 25 September 2566 a government agency filed a further report that the intrusion had spread from the first machine to the file server. Digital forensic examination found the implant on the first machine receiving commands to download a remote command tool and a second implant installer. Evidence then showed the offender running that tool in the name of the file server administrator's account, so the installer was launched on the file server by creating a system service there. Finally, once the implant on the new machine called back, the offender was found deleting all the files they had placed on the first machine to clean up traces.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1105 Ingress Tool Transfer | โปรแกรมฝังตัวบนเครื่องแรกได้รับคำสั่งให้ดาวน์โหลดเครื่องมือสำหรับสั่งงานเครื่องระยะไกล และดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดที่สองเข้ามาเก็บไว้ | Task the implant to download PsExec. Task the implant to download the 2nd Snake installer. |
| 2 | described | T1569 System Services | คนร้ายสั่งรันเครื่องมือดังกล่าวในนามของบัญชีผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์ ทำให้ตัวติดตั้งถูกเรียกทำงานบนเครื่องแม่ข่ายเก็บไฟล์ผ่านการสร้างบริการของระบบขึ้นบนเครื่องนั้น | Run the following command to execute PsExec as the file server admin, which will run the Snake installer on the file server |
| 3 | described | T1070 Indicator Removal | คนร้ายสั่งลบไฟล์ที่เคยนำเข้าไปวางไว้บนเครื่องแรกออกทั้งหมดเพื่อเก็บกวาดร่องรอย | After the new beacon is received, remove files from the first target. |

- [ ] ผ่าน / แก้แล้ว

## rcti_078 — CISA AA23-270A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-270a>

> เมื่อวันที่ 29 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความเพิ่มเติมถึงเส้นทางที่คนร้ายใช้ขยายการเข้าถึงในองค์กร จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายมุ่งเป้าไปที่อุปกรณ์เราเตอร์ประจำสาขาซึ่งเป็นอุปกรณ์ขนาดเล็กที่สำนักงานสาขาใช้เชื่อมต่อกลับมายังสำนักงานใหญ่ แล้วอาศัยความสัมพันธ์ความน่าเชื่อถือที่อุปกรณ์เหล่านั้นมีอยู่กับเครือข่ายองค์กร เข้ามายังเครือข่ายเป้าหมาย อันเข้าลักษณะ Trusted Relationship ต่อมาปรากฏหลักฐานว่าคนร้ายใช้เครื่องมือสแกนสำรวจเครือข่ายภายใน และตั้งเครื่องแม่ข่ายรับส่งไฟล์ขึ้นภายในเครือข่ายของผู้เสียหายเอง เพื่อใช้ลำเลียงข้อมูลไปมาระหว่างเครื่องต่าง ๆ ในเครือข่าย สุดท้ายพบว่าคนร้ายใช้อุปกรณ์เราเตอร์ประจำสาขาที่ยึดครองไว้และเปิดสู่อินเทอร์เน็ตเป็นส่วนหนึ่งของโครงสร้างพื้นฐานของตน สำหรับส่งต่อการเชื่อมต่อให้กลมกลืนไปกับปริมาณข้อมูลปกติขององค์กร และใช้เป็นทางผ่านไปยังผู้เสียหายรายอื่นในเครือข่ายเดียวกัน

*EN:* On 29 September 2566 a multinational company filed a further report on the route the offender used to widen access within the organisation. Digital forensic examination found the offender targeting branch routers — the small appliances branch offices use to connect back to head office — and abusing the trust those devices held within the corporate network to enter the target network, a case of Trusted Relationship. Evidence then showed the offender using a scanning tool to survey the internal network and standing up a file transfer server inside the victim's own network to move data between machines. Finally the offender was found using the compromised, internet-facing branch routers as part of their own infrastructure, relaying connections so they blended into the organisation's normal traffic and using them as a route to other victims on the same network.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1199 Trusted Relationship | คนร้ายมุ่งเป้าไปที่อุปกรณ์เราเตอร์ประจำสาขาซึ่งเป็นอุปกรณ์ขนาดเล็กที่สำนักงานสาขาใช้เชื่อมต่อกลับมายังสำนักงานใหญ่ แล้วอาศัยความสัมพันธ์ความน่าเชื่อถือที่อุปกรณ์เหล่านั้นมีอยู่กับเครือข่ายองค์กร เข้ามายังเครือข่ายเป้าหมาย อันเข้าลักษณะ Trusted Relationship | To extend their foothold across an organization, BlackTech actors target branch routers—typically smaller appliances used at remote branch offices to connect to a corporate headquarters—and then abuse the trusted relatio… |
| 2 | described | T1071 Application Layer Protocol | คนร้ายใช้เครื่องมือสแกนสำรวจเครือข่ายภายใน และตั้งเครื่องแม่ข่ายรับส่งไฟล์ขึ้นภายในเครือข่ายของผู้เสียหายเอง เพื่อใช้ลำเลียงข้อมูลไปมาระหว่างเครื่องต่าง ๆ ในเครือข่าย | The actors have also used SNScan for enumeration [TA0007], and a local file transfer protocol (FTP) server to move data through the victim network |
| 3 | described | T1090 Proxy | คนร้ายใช้อุปกรณ์เราเตอร์ประจำสาขาที่ยึดครองไว้และเปิดสู่อินเทอร์เน็ตเป็นส่วนหนึ่งของโครงสร้างพื้นฐานของตน สำหรับส่งต่อการเชื่อมต่อให้กลมกลืนไปกับปริมาณข้อมูลปกติขององค์กร และใช้เป็นทางผ่านไปยังผู้เสียหายรายอื่นในเครือข่ายเดียวกัน | BlackTech actors then use the compromised public-facing branch routers as part of their infrastructure for proxying traffic [TA0011], blending in with corporate network traffic, and pivoting to other victims on the same … |

- [ ] ผ่าน / แก้แล้ว

## rcti_079 — CISA AA23-270A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-270a>

> เมื่อวันที่ 30 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายดัดแปลงอุปกรณ์เครือข่าย จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายหลบเลี่ยงกลไกตรวจสอบความถูกต้องของซอฟต์แวร์ที่ติดมากับตัวอุปกรณ์ ด้วยการติดตั้งซอฟต์แวร์รุ่นเก่าที่ยังมีลายเซ็นถูกต้องลงไปก่อน แล้วจึงแก้ไขซอฟต์แวร์นั้นในหน่วยความจำ เพื่อเปิดทางให้ติดตั้งตัวโหลดระบบและซอฟต์แวร์ที่ไม่มีลายเซ็นซึ่งคนร้ายดัดแปลงเองเข้าไปแทน ต่อมาปรากฏหลักฐานว่าตัวโหลดระบบที่ถูกดัดแปลงนั้นทำหน้าที่ช่วยให้ซอฟต์แวร์ดัดแปลงยังคงผ่านการตรวจสอบและไม่ถูกตรวจพบต่อไปได้ สุดท้ายจากการตรวจสอบการตั้งค่าของอุปกรณ์พบว่าคนร้ายวางกฎอัตโนมัติไว้สองอย่าง คือให้ตัดบรรทัดที่มีข้อความบางคำออกจากผลลัพธ์ของคำสั่งตรวจสอบที่ผู้ดูแลระบบเรียกใช้ และให้ขัดขวางไม่ให้คำสั่งคัดลอก เปลี่ยนชื่อ และย้ายไฟล์ทำงานได้ เพื่อกีดกันการตรวจพิสูจน์พยานหลักฐาน

*EN:* On 30 September 2566 an internet service provider filed a further report on how the offender modified its network devices. Digital forensic examination found the offender bypassing the software integrity checking built into the device by first installing an older, still validly signed software version, then modifying that software in memory to allow an unsigned bootloader and unsigned firmware of the offender's own making to be installed instead. Evidence then showed the modified bootloader serving to keep the modified software passing checks and undetected. Finally, examination of the device configuration found the offender placing two automatic rules: to strip lines containing certain strings out of the output of inspection commands run by administrators, and to block the copy, rename and move commands from working, so as to hinder forensic examination.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1601 Modify System Image | คนร้ายหลบเลี่ยงกลไกตรวจสอบความถูกต้องของซอฟต์แวร์ที่ติดมากับตัวอุปกรณ์ ด้วยการติดตั้งซอฟต์แวร์รุ่นเก่าที่ยังมีลายเซ็นถูกต้องลงไปก่อน แล้วจึงแก้ไขซอฟต์แวร์นั้นในหน่วยความจำ เพื่อเปิดทางให้ติดตั้งตัวโหลดระบบและซอฟต์แวร์ที่ไม่มีลายเซ็นซึ่งคนร้ายดัดแปลงเองเข้าไปแทน | BlackTech actors bypass the router's built-in security features by first installing older legitimate firmware that they then modify in memory to allow the installation of a modified, unsigned bootloader and modified, uns… |
| 2 | described | T1553 Subvert Trust Controls | ตัวโหลดระบบที่ถูกดัดแปลงนั้นทำหน้าที่ช่วยให้ซอฟต์แวร์ดัดแปลงยังคงผ่านการตรวจสอบและไม่ถูกตรวจพบต่อไปได้ | The modified bootloader enables the modified firmware to continue evading detection , however, it is not always necessary |
| 3 | described | T1562 ? | คนร้ายวางกฎอัตโนมัติไว้สองอย่าง คือให้ตัดบรรทัดที่มีข้อความบางคำออกจากผลลัพธ์ของคำสั่งตรวจสอบที่ผู้ดูแลระบบเรียกใช้ และให้ขัดขวางไม่ให้คำสั่งคัดลอก เปลี่ยนชื่อ และย้ายไฟล์ทำงานได้ เพื่อกีดกันการตรวจพิสูจน์พยานหลักฐาน | This policy has two functions: (1) to remove lines containing certain strings in the output of specified, legitimate Cisco IOS CLI commands , and (2) prevent the execution of other legitimate CLI commands, such as hinder… |

- [ ] ผ่าน / แก้แล้ว

## rcti_080 — CISA AA20-280A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-280a>

> เมื่อวันที่ 6 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กรติดโปรแกรมไม่พึงประสงค์และแพร่กระจายไปยังเครื่องอื่นในเครือข่าย จากการตรวจสอบทะเบียนระบบพบว่าคนร้ายเพิ่มรายการเรียกใช้งานโปรแกรมของตนไว้ใน Registry Run Key และในโฟลเดอร์เริ่มต้นระบบ เพื่อให้โปรแกรมทำงานเองทุกครั้งที่เปิดเครื่อง ต่อมาปรากฏหลักฐานว่าโปรแกรมดังกล่าวเข้าไปอ่าน Credentials from Web Browsers คือชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของผู้เสียหายบันทึกไว้ในเครื่อง จากนั้นจากการตรวจสอบปริมาณข้อมูลในเครือข่ายพบว่ามีการพยายามเชื่อมต่อจากหมายเลขไอพีที่เกี่ยวข้องไปยังเครื่องต้องสงสัยผ่านพอร์ตที่ใช้แบ่งปันไฟล์ของวินโดวส์ ซึ่งบ่งชี้ถึงการใช้ชุดเครื่องมือโจมตีช่องโหว่ของบริการดังกล่าวเพื่อขยายการเข้าถึงไปยังเครื่องอื่น สุดท้ายพบว่าการติดต่อกลับไปยังเครื่องสั่งการมีลักษณะเป็นการส่งคำขอผ่านโพรโทคอลเว็บ โดยเส้นทางที่ระบุในคำขอเป็นชื่อโฟลเดอร์ตัวอักษรสุ่มไม่มีความหมายและความยาวไม่แน่นอน

*EN:* On 6 October 2563 an agency reported that computers in the organisation were infected with an unwanted program spreading to other machines on the network. Examination of the system registry found the offender adding entries launching their program to the Registry Run Key and the startup folder so it would run by itself every time the machine started. Evidence then showed that program reading Credentials from Web Browsers — the usernames and passwords the victim's browser had saved on the machine. Examination of network traffic then found connection attempts from a related IP address to a suspect machine over the Windows file sharing port, indicating the use of exploitation toolkits against that service to widen access to other machines. Finally, callbacks to the command machine were found taking the form of requests over a web protocol, with the paths in those requests consisting of meaningless random-letter directory names of varying length.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1547 Boot or Logon Autostart Execution | คนร้ายเพิ่มรายการเรียกใช้งานโปรแกรมของตนไว้ใน Registry Run Key และในโฟลเดอร์เริ่มต้นระบบ เพื่อให้โปรแกรมทำงานเองทุกครั้งที่เปิดเครื่อง | Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder |
| 2 | named | T1555 Credentials from Password Stores | โปรแกรมดังกล่าวเข้าไปอ่าน Credentials from Web Browsers คือชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของผู้เสียหายบันทึกไว้ในเครื่อง | Credentials from Password Stores: Credentials from Web Browsers |
| 3 | described | T1210 Exploitation of Remote Services | มีการพยายามเชื่อมต่อจากหมายเลขไอพีที่เกี่ยวข้องไปยังเครื่องต้องสงสัยผ่านพอร์ตที่ใช้แบ่งปันไฟล์ของวินโดวส์ ซึ่งบ่งชี้ถึงการใช้ชุดเครื่องมือโจมตีช่องโหว่ของบริการดังกล่าวเพื่อขยายการเข้าถึงไปยังเครื่องอื่น | In one instance, traffic from an Emotet-related IP attempted to connect to a suspected compromised site over port 445, possibly indicating the use of Server Message Block exploitation frameworks along with Emotet (Exploi… |
| 4 | described | T1071 Application Layer Protocol | การติดต่อกลับไปยังเครื่องสั่งการมีลักษณะเป็นการส่งคำขอผ่านโพรโทคอลเว็บ โดยเส้นทางที่ระบุในคำขอเป็นชื่อโฟลเดอร์ตัวอักษรสุ่มไม่มีความหมายและความยาวไม่แน่นอน | Possible command and control network traffic involved HTTP POST requests to Uniform Resource Identifiers consisting of nonsensical random length alphabetical directories to known Emotet-related domains or IPs with the fo… |

- [ ] ผ่าน / แก้แล้ว

## rcti_081 — CISA AA20-336A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-336a>

> เมื่อวันที่ 2 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายหลบเลี่ยงการตรวจจับบนเครื่องที่ยึดครองไว้ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายใช้วิธีหลบเลี่ยงกลไกที่ระบบใช้ถามยืนยันก่อนยกระดับสิทธิ์ ทำให้โปรแกรมของตนได้สิทธิ์ผู้ดูแลระบบโดยไม่มีหน้าต่างขออนุญาตปรากฏให้ผู้ใช้เห็น ต่อมาปรากฏหลักฐานว่าคนร้ายปรับแต่งเครื่องมือของตนก่อนนำมาใช้ โดยตัดข้อความและค่าเฉพาะที่ผู้ผลิตโปรแกรมป้องกันใช้เป็นจุดสังเกตออกจากตัวไฟล์ ซึ่งเข้าลักษณะ Indicator Removal from Tools ทำให้เครื่องมือที่รู้จักกันดีอยู่แล้วไม่ถูกตรวจจับ สุดท้ายพบว่าเมื่อดำเนินการเสร็จ คนร้ายได้ล้างไฟล์บันทึกเหตุการณ์ของวินโดวส์ทิ้งทั้งหมด อันเป็นลักษณะ Indicator Removal on Host เพื่อไม่ให้เหลือร่องรอยการเข้าถึงไว้ตรวจสอบ

*EN:* On 2 December 2563 an agency filed a further report on how the offender evaded detection on the compromised machines. Digital forensic examination found the offender using a method to bypass the mechanism the system uses to ask for confirmation before elevating privileges, giving their program administrator rights with no permission dialog shown to the user. Evidence then showed the offender tuning their tools before use, stripping out the strings and specific values that protection vendors use as signatures — matching Indicator Removal from Tools — so that well-known tools went undetected. Finally, on completion, the offender was found clearing all the Windows event log files, a case of Indicator Removal on Host, so that no trace of the access remained to be examined.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1548 Abuse Elevation Control Mechanism | คนร้ายใช้วิธีหลบเลี่ยงกลไกที่ระบบใช้ถามยืนยันก่อนยกระดับสิทธิ์ ทำให้โปรแกรมของตนได้สิทธิ์ผู้ดูแลระบบโดยไม่มีหน้าต่างขออนุญาตปรากฏให้ผู้ใช้เห็น | Abuse Elevation Control Mechanism: Bypass User Access Control |
| 2 | named | T1027 Obfuscated Files or Information | คนร้ายปรับแต่งเครื่องมือของตนก่อนนำมาใช้ โดยตัดข้อความและค่าเฉพาะที่ผู้ผลิตโปรแกรมป้องกันใช้เป็นจุดสังเกตออกจากตัวไฟล์ ซึ่งเข้าลักษณะ Indicator Removal from Tools | Obfuscated Files or Information: Indicator Removal from Tools |
| 3 | named | T1070 Indicator Removal | คนร้ายได้ล้างไฟล์บันทึกเหตุการณ์ของวินโดวส์ทิ้งทั้งหมด อันเป็นลักษณะ Indicator Removal on Host | Indicator Removal on Host: Clear Windows Event Logs |

- [ ] ผ่าน / แก้แล้ว

## rcti_082 — CISA AA23-352A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-352a>

> เมื่อวันที่ 19 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายกระจายโปรแกรมและนำข้อมูลออก จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายอาศัยระบบนโยบายกลุ่มของโดเมน ซึ่งปกติผู้ดูแลระบบใช้แจกจ่ายการตั้งค่าให้เครื่องลูกข่ายทั้งองค์กร เป็นช่องทางส่งไฟล์โปรแกรมของตนไปติดตั้งบนเครื่องลูกข่ายพร้อมกันทีเดียวทั้งหมด ต่อมาปรากฏหลักฐานว่าคนร้ายแบ่งข้อมูลที่รวบรวมได้ออกเป็นส่วนย่อยหลายส่วน แล้วใช้โปรแกรมบีบอัดไฟล์ทั่วไปบีบอัดแต่ละส่วนไว้เพื่อเตรียมนำออก สุดท้ายพบว่าคนร้ายใช้โปรแกรมรับส่งไฟล์ลำเลียงข้อมูลที่บีบอัดแล้วออกจากเครือข่ายของผู้เสียหายไปยังบัญชีปลายทางที่คนร้ายควบคุมอยู่ ผ่านช่องทางที่ไม่ใช่ช่องทางเดียวกับที่ใช้รับคำสั่ง

*EN:* On 19 December 2566 a retail company filed a further report on how the offender distributed their program and took data out. Digital forensic examination found the offender using the domain's group policy system — normally used by administrators to distribute settings to client machines across the organisation — as a channel to push their own program file onto all client machines at once. Evidence then showed the offender splitting the collected data into several segments and compressing each with an ordinary file compression program ready to be taken out. Finally the offender was found using a file transfer program to move the compressed data out of the victim's network to a destination account under their control, over a channel other than the one used to receive commands.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1570 Lateral Tool Transfer, T1484 Domain or Tenant Policy Modification | คนร้ายอาศัยระบบนโยบายกลุ่มของโดเมน ซึ่งปกติผู้ดูแลระบบใช้แจกจ่ายการตั้งค่าให้เครื่องลูกข่ายทั้งองค์กร เป็นช่องทางส่งไฟล์โปรแกรมของตนไปติดตั้งบนเครื่องลูกข่ายพร้อมกันทีเดียวทั้งหมด | Actors then distribute executables via Group Policy Objects |
| 2 | described | T1560 Archive Collected Data | คนร้ายแบ่งข้อมูลที่รวบรวมได้ออกเป็นส่วนย่อยหลายส่วน แล้วใช้โปรแกรมบีบอัดไฟล์ทั่วไปบีบอัดแต่ละส่วนไว้เพื่อเตรียมนำออก | Play ransomware actors often split compromised data into segments and use tools like WinRAR to compress files into .RAR format for exfiltration |
| 3 | described | T1048 Exfiltration Over Alternative Protocol | คนร้ายใช้โปรแกรมรับส่งไฟล์ลำเลียงข้อมูลที่บีบอัดแล้วออกจากเครือข่ายของผู้เสียหายไปยังบัญชีปลายทางที่คนร้ายควบคุมอยู่ ผ่านช่องทางที่ไม่ใช่ช่องทางเดียวกับที่ใช้รับคำสั่ง | The actors then use WinSCP to transfer data from a compromised network to actor-controlled accounts |

- [ ] ผ่าน / แก้แล้ว

## rcti_083 — Turla - Carbon (CTID emulation plan turla_carbon.yaml)

> เมื่อวันที่ 24 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนที่คนร้ายขยายการเข้าถึงไปยังเครื่องแม่ข่ายควบคุมโดเมน จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าโปรแกรมฝังตัวได้รับคำสั่งให้ลบไฟล์สคริปต์ที่ใช้ลองรหัสผ่านกับบัญชีผู้ดูแลออกจากเครื่องทันทีหลังใช้งานเสร็จ ต่อมาปรากฏหลักฐานว่าโปรแกรมฝังตัวได้รับคำสั่งให้ดาวน์โหลดตัวติดตั้งของตนสำเนาที่สองเข้ามา แล้วคัดลอกไฟล์นั้นข้ามไปวางไว้ในโฟลเดอร์ระบบของเครื่องแม่ข่ายควบคุมโดเมนผ่านไดรฟ์ที่เชื่อมต่อไว้ สุดท้ายพบว่าคนร้ายอาศัยรหัสผ่านของผู้ดูแลโดเมนที่ได้มา สั่งให้โปรแกรมฝังตัวไล่แจกแจงรายการงานตั้งเวลาที่มีอยู่บนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล เพื่อหาช่องทางเรียกไฟล์ที่วางไว้ให้ทำงาน

*EN:* On 24 November 2566 an agency filed a further report on how the offender extended access to the domain controller. Digital forensic examination found the implant receiving a command to delete the script used for trying passwords against administrator accounts from the machine immediately after use. Evidence then showed the implant receiving a command to download a second copy of its own installer and copy that file across into the system folder of the domain controller through a mounted drive. Finally the offender was found using the domain administrator password they had obtained to have the implant remotely enumerate the timed jobs existing on the domain controller, looking for a way to get the planted file to run.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1070 Indicator Removal | โปรแกรมฝังตัวได้รับคำสั่งให้ลบไฟล์สคริปต์ที่ใช้ลองรหัสผ่านกับบัญชีผู้ดูแลออกจากเครื่องทันทีหลังใช้งานเสร็จ | Task CARBON-DLL to remove the password spray script |
| 2 | described | T1570 Lateral Tool Transfer | โปรแกรมฝังตัวได้รับคำสั่งให้ดาวน์โหลดตัวติดตั้งของตนสำเนาที่สองเข้ามา แล้วคัดลอกไฟล์นั้นข้ามไปวางไว้ในโฟลเดอร์ระบบของเครื่องแม่ข่ายควบคุมโดเมนผ่านไดรฟ์ที่เชื่อมต่อไว้ | Task CARBON-DLL to download a second version of the CARBON-DLL installer and move it to the System32 folder on the DC via the mounted drive. |
| 3 | described | T1053 Scheduled Task/Job | คนร้ายอาศัยรหัสผ่านของผู้ดูแลโดเมนที่ได้มา สั่งให้โปรแกรมฝังตัวไล่แจกแจงรายการงานตั้งเวลาที่มีอยู่บนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล เพื่อหาช่องทางเรียกไฟล์ที่วางไว้ให้ทำงาน | Task CARBON-DLL to enumerate remote scheduled tasks on the domain controller, using the discovered password for the domain admin |

- [ ] ผ่าน / แก้แล้ว

## rcti_084 — FIN7 (CTID emulation plan Fin7.yaml)

ต้นทาง: <https://www.fireeye.com/content/dam/fireeye-www/summit/cds-2018/presentations/cds18-technical-s05-att&cking-fin7.pdf>

> เมื่อวันที่ 15 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกลุกลามจากเครื่องรับชำระเงินไปยังเครื่องของฝ่ายเทคโนโลยีสารสนเทศ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายรันเครื่องมือดึงค่ารหัสผ่านออกจากฐานข้อมูลบัญชีผู้ใช้ที่เก็บอยู่ในเครื่องที่ยึดครองได้ ต่อมาปรากฏหลักฐานว่าคนร้ายใช้เครื่องมือสั่งงานเครื่องระยะไกลคัดลอกไฟล์โปรแกรมของตนจากเครื่องที่ยึดครองไว้แล้ว ข้ามไปยังเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ฝ่ายเทคโนโลยีสารสนเทศแล้วสั่งให้ทำงานบนเครื่องนั้น สุดท้ายพบว่าคนร้ายวางไฟล์ไลบรารีของตนไว้ในตำแหน่งที่ระบบจะค้นหาก่อนตำแหน่งจริง ทำให้เมื่อโปรแกรมที่ถูกต้องเริ่มทำงาน ระบบจะโหลดไฟล์ของคนร้ายขึ้นมาแทน และคนร้ายจึงได้สิทธิ์ที่สูงขึ้นตามสิทธิ์ของโปรแกรมนั้น

*EN:* On 15 June 2567 a department store filed a further report that the intrusion had spread from the payment terminals to IT staff machines. Digital forensic examination found the offender running a tool to extract password values from the user account database stored on the compromised machine. Evidence then showed the offender using a remote command tool to copy their own program file from the already-compromised machine across to an IT officer's computer and run it there. Finally the offender was found placing their own library file in a location the system searches before the real one, so that when the legitimate program started the system loaded the offender's file instead, giving the offender the higher privileges that program held.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1003 OS Credential Dumping | คนร้ายรันเครื่องมือดึงค่ารหัสผ่านออกจากฐานข้อมูลบัญชีผู้ใช้ที่เก็บอยู่ในเครื่องที่ยึดครองได้ | Dump SAM via Mimikatz(T1003.002) |
| 2 | described | T1570 Lateral Tool Transfer | คนร้ายใช้เครื่องมือสั่งงานเครื่องระยะไกลคัดลอกไฟล์โปรแกรมของตนจากเครื่องที่ยึดครองไว้แล้ว ข้ามไปยังเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ฝ่ายเทคโนโลยีสารสนเทศแล้วสั่งให้ทำงานบนเครื่องนั้น | Leverage PAExec to laterally move and execute on itadmin |
| 3 | described | T1574 Hijack Execution Flow | คนร้ายวางไฟล์ไลบรารีของตนไว้ในตำแหน่งที่ระบบจะค้นหาก่อนตำแหน่งจริง ทำให้เมื่อโปรแกรมที่ถูกต้องเริ่มทำงาน ระบบจะโหลดไฟล์ของคนร้ายขึ้นมาแทน และคนร้ายจึงได้สิทธิ์ที่สูงขึ้นตามสิทธิ์ของโปรแกรมนั้น | Perform DLL hijack to escalate privileges. |

- [ ] ผ่าน / แก้แล้ว

## rcti_085 — Sandworm Team (G0034) (CTID emulation plan sandworm.yaml)

ต้นทาง: <https://www.justice.gov/opa/press-release/file/1328521/download>

> เมื่อวันที่ 19 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งความเพิ่มเติมว่าพบการสำรวจข้อมูลบนเครื่องในห้องควบคุมก่อนเกิดเหตุ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายเรียกดูชื่อบัญชีผู้ใช้ที่กำลังทำงานอยู่บนเครื่องที่ยึดครองได้เป็นอันดับแรก ต่อมาได้เรียกดูรายละเอียดของระบบปฏิบัติการที่ติดตั้งอยู่บนเครื่องนั้น จากนั้นปรากฏหลักฐานว่าคนร้ายไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์ที่มีอยู่บนเครื่องเพื่อค้นหาข้อมูลที่ต้องการ สุดท้ายพบว่าคนร้ายเก็บรวบรวมข้อมูลของเซสชันการเชื่อมต่อหน้าจอระยะไกลที่ค้างอยู่บนเครื่อง ทั้งชื่อผู้ใช้ หมายเลขไอพี และชื่อเครื่องแม่ข่ายที่เกี่ยวข้อง เพื่อใช้เป็นข้อมูลสำหรับขยายการเข้าถึงต่อไป

*EN:* On 19 July 2567 a provincial electricity authority branch filed a further report of reconnaissance on control room machines before the incident. Digital forensic examination found the offender first reading the name of the account running on the compromised machine, then reading details of the operating system installed on it. Evidence then showed the offender enumerating the files and folders present on the machine in search of the data they wanted. Finally the offender was found collecting information on the remote screen connection sessions open on the machine — usernames, IP addresses and the names of the servers involved — as material for widening their access further.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1033 System Owner/User Discovery | คนร้ายเรียกดูชื่อบัญชีผู้ใช้ที่กำลังทำงานอยู่บนเครื่องที่ยึดครองได้เป็นอันดับแรก | Sandworm Team has collected the username from a compromised host. |
| 2 | described | T1082 System Information Discovery | ได้เรียกดูรายละเอียดของระบบปฏิบัติการที่ติดตั้งอยู่บนเครื่องนั้น | Sandworm Team enumerates information about the infected system's operating system. |
| 3 | described | T1083 File and Directory Discovery | คนร้ายไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์ที่มีอยู่บนเครื่องเพื่อค้นหาข้อมูลที่ต้องการ | Sandworm Team has enumerated files on a compromised host. |
| 4 | described | T1049 System Network Connections Discovery | คนร้ายเก็บรวบรวมข้อมูลของเซสชันการเชื่อมต่อหน้าจอระยะไกลที่ค้างอยู่บนเครื่อง ทั้งชื่อผู้ใช้ หมายเลขไอพี และชื่อเครื่องแม่ข่ายที่เกี่ยวข้อง เพื่อใช้เป็นข้อมูลสำหรับขยายการเข้าถึงต่อไป | Sandworm Team had gathered user, IP address, and server data related to RDP sessions on a compromised host. |

- [ ] ผ่าน / แก้แล้ว

## rcti_086 — CISA AA21-048A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-048a>

> เมื่อวันที่ 20 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าถูกหลอกให้ติดตั้งโปรแกรมซื้อขายสินทรัพย์ดิจิทัลปลอมบนเครื่องคอมพิวเตอร์ระบบวินโดวส์ จากการตรวจสอบพบว่าตัวติดตั้งของโปรแกรมได้แสดงหน้าต่างขอสิทธิ์ผู้ดูแลระบบจากผู้เสียหายเพื่อดำเนินการติดตั้งต่อ ซึ่งผู้เสียหายเป็นผู้กดอนุญาตเอง อันเข้าลักษณะ User Execution: Malicious File ต่อมาปรากฏหลักฐานว่าไฟล์โปรแกรมที่ถูกติดตั้งลงเครื่องถูกอำพรางเนื้อหาไว้อย่างหนักด้วยไลบรารีสำหรับบิดเบือนโครงสร้างโปรแกรม ทำให้การถอดรหัสวิเคราะห์การทำงานทำได้ยาก สุดท้ายจากการตรวจสอบการติดต่อสื่อสารของโปรแกรมพบว่าใช้อัลกอริทึมเข้ารหัสแบบสตรีมพร้อมกุญแจขนาดสิบหกไบต์ในการปกปิดเนื้อหาที่รับส่งกับเครื่องสั่งการ อันเข้าลักษณะ Encrypted Channel: Symmetric Cryptography

*EN:* On 20 February 2564 a victim reported being tricked into installing a fake digital asset trading program on a Windows computer. Examination found the program's installer displaying a dialog requesting administrator privileges from the victim in order to proceed, which the victim granted themselves — matching User Execution: Malicious File. Evidence then showed the installed program file heavily obfuscated with a library for distorting program structure, making it difficult to decompile and analyse its behaviour. Finally, examination of the program's communications found it using a stream cipher algorithm with a sixteen-byte key to conceal the content exchanged with the command machine, matching Encrypted Channel: Symmetric Cryptography.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1204 User Execution | ตัวติดตั้งของโปรแกรมได้แสดงหน้าต่างขอสิทธิ์ผู้ดูแลระบบจากผู้เสียหายเพื่อดำเนินการติดตั้งต่อ ซึ่งผู้เสียหายเป็นผู้กดอนุญาตเอง อันเข้าลักษณะ User Execution: Malicious File | The MSI Installer asks the victim for administrative privileges to run (User Execution: Malicious File ) |
| 2 | described | T1027 Obfuscated Files or Information | ไฟล์โปรแกรมที่ถูกติดตั้งลงเครื่องถูกอำพรางเนื้อหาไว้อย่างหนักด้วยไลบรารีสำหรับบิดเบือนโครงสร้างโปรแกรม ทำให้การถอดรหัสวิเคราะห์การทำงานทำได้ยาก | The program CrashReporter.exe is heavily obfuscated with the ADVObfuscation library, renamed “snowman” (Obfuscated Files or Information ) |
| 3 | named | T1573 Encrypted Channel | ใช้อัลกอริทึมเข้ารหัสแบบสตรีมพร้อมกุญแจขนาดสิบหกไบต์ในการปกปิดเนื้อหาที่รับส่งกับเครื่องสั่งการ อันเข้าลักษณะ Encrypted Channel: Symmetric Cryptography | FALLCHILL malware uses an RC4 encryption algorithm with a 16-byte key to protect its communications (Encrypted Channel: Symmetric Cryptography ) |

- [ ] ผ่าน / แก้แล้ว

## rcti_087 — CISA AA23-352A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-352a>

> เมื่อวันที่ 17 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงช่องทางที่คนร้ายเข้าสู่ระบบเป็นครั้งแรก จากการตรวจสอบ log การเข้าใช้งานพบว่าคนร้ายเข้าถึงเครือข่ายของบริษัทผ่าน External Remote Services ได้แก่ บริการเชื่อมต่อหน้าจอระยะไกลและบริการเครือข่ายส่วนตัวเสมือนที่เปิดให้เข้าถึงจากภายนอก ต่อมาปรากฏหลักฐานว่าคนร้ายใช้ Valid Accounts คือบัญชีผู้ใช้ที่ยังใช้งานได้ซึ่งได้มาก่อนหน้า ควบคู่กับการโจมตีช่องโหว่ของแอปพลิเคชันที่เปิดให้บริการต่อสาธารณะ ทั้งช่องโหว่ของอุปกรณ์ไฟร์วอลล์และช่องโหว่ของเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ที่ยังไม่ได้ปรับปรุง สุดท้ายเมื่อเข้ามาอยู่ในเครือข่ายแล้ว พบว่าคนร้ายใช้เครื่องมือสอบถามข้อมูลจากระบบทะเบียนโดเมนเพื่อไล่เก็บรายละเอียดของเครือข่าย และใช้โปรแกรมขโมยข้อมูลอีกตัวหนึ่งไล่ตรวจสอบว่าเครื่องแต่ละเครื่องติดตั้งโปรแกรมป้องกันไวรัสยี่ห้อใดไว้บ้าง

*EN:* On 17 December 2566 a retail company filed a further report on how the offender first entered its systems. Access logs showed the offender reaching the company's network through External Remote Services — the remote screen service and the virtual private network service exposed to the outside. Evidence then showed the offender using Valid Accounts, still-working user accounts obtained earlier, alongside attacking vulnerabilities in publicly reachable applications, both in the firewall appliance and in an unpatched mail server. Finally, once inside the network, the offender was found using a tool that queries the domain directory to gather network details, and another information-stealing program to check which brand of antivirus each machine had installed.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1133 External Remote Services | คนร้ายเข้าถึงเครือข่ายของบริษัทผ่าน External Remote Services ได้แก่ บริการเชื่อมต่อหน้าจอระยะไกลและบริการเครือข่ายส่วนตัวเสมือนที่เปิดให้เข้าถึงจากภายนอก | Play ransomware actors have been observed to use external-facing services such as Remote Desktop Protocol (RDP) and Virtual Private Networks (VPN) for initial access |
| 2 | named | T1078 Valid Accounts, T1190 Exploit Public-Facing Application | คนร้ายใช้ Valid Accounts คือบัญชีผู้ใช้ที่ยังใช้งานได้ซึ่งได้มาก่อนหน้า ควบคู่กับการโจมตีช่องโหว่ของแอปพลิเคชันที่เปิดให้บริการต่อสาธารณะ ทั้งช่องโหว่ของอุปกรณ์ไฟร์วอลล์และช่องโหว่ของเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ที่ยังไม่ได้ปรับปรุง | The Play ransomware group gains initial access to victim networks through the abuse of valid accounts and exploitation of public-facing applications , specifically through known FortiOS (CVE-2018-13379 and CVE-2020-12812… |
| 3 | described | T1016 System Network Configuration Discovery, T1518 Software Discovery | คนร้ายใช้เครื่องมือสอบถามข้อมูลจากระบบทะเบียนโดเมนเพื่อไล่เก็บรายละเอียดของเครือข่าย และใช้โปรแกรมขโมยข้อมูลอีกตัวหนึ่งไล่ตรวจสอบว่าเครื่องแต่ละเครื่องติดตั้งโปรแกรมป้องกันไวรัสยี่ห้อใดไว้บ้าง | Play ransomware actors use tools like AdFind to run Active Directory queries [TA0007] and Grixba , an information-stealer, to enumerate network information and scan for anti-virus software |

- [ ] ผ่าน / แก้แล้ว

## rcti_088 — CISA AA21-076A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-076a>

> เมื่อวันที่ 16 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความเพิ่มเติมถึงจุดเริ่มต้นที่ลูกค้าติดโปรแกรมขโมยข้อมูล จากการตรวจสอบพบว่าคนร้ายกระจายโปรแกรมม้าโทรจันด้วยการส่งอีเมลหลอกลวงที่เขียนเนื้อความให้ตรงกับผู้รับแต่ละราย โดยแนบทั้งไฟล์อันตรายและลิงก์มาในฉบับเดียวกัน ซึ่งหากผู้รับเปิดใช้งานก็จะทำให้โปรแกรมอันตรายเริ่มทำงาน ต่อมาปรากฏหลักฐานว่าผู้เสียหายเป็นผู้กดเปิดลิงก์และเปิดไฟล์แนบนั้นด้วยตนเอง อันเข้าลักษณะ User Execution: Malicious Link และ User Execution: Malicious File สุดท้ายพบว่าเมื่อผู้เสียหายกดที่ภาพในหน้าเว็บที่ลิงก์พาไป เครื่องได้ดาวน์โหลดไฟล์สคริปต์ภาษาจาวาสคริปต์ลงมาโดยผู้ใช้ไม่ทราบ และเมื่อไฟล์นั้นถูกเปิด สคริปต์จะติดต่อไปยังเครื่องสั่งการของคนร้ายเพื่อดาวน์โหลดตัวโปรแกรมม้าโทรจันเข้ามาติดตั้งบนเครื่องต่อไป

*EN:* On 16 March 2564 a bank filed a further report on how customers first became infected with the data-stealing program. Examination found the offender spreading a Trojan program by sending phishing emails whose wording was tailored to each recipient, attaching both a malicious file and a link in the same message; if the recipient opened either, the malicious program would start. Evidence then showed the victim clicking the link and opening the attachment themselves, matching User Execution: Malicious Link and User Execution: Malicious File. Finally, when the victim clicked an image on the page the link led to, the machine downloaded a JavaScript file without the user's knowledge, and when that file was opened the script contacted the offender's command machine to download and install the Trojan program.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1566 Phishing | คนร้ายกระจายโปรแกรมม้าโทรจันด้วยการส่งอีเมลหลอกลวงที่เขียนเนื้อความให้ตรงกับผู้รับแต่ละราย โดยแนบทั้งไฟล์อันตรายและลิงก์มาในฉบับเดียวกัน | TrickBot is an advanced Trojan that malicious actors spread primarily by spearphishing campaigns using tailored emails that contain malicious attachments or links, which—if enabled—execute malware (Phishing: Spearphishin… |
| 2 | named | T1204 User Execution | ผู้เสียหายเป็นผู้กดเปิดลิงก์และเปิดไฟล์แนบนั้นด้วยตนเอง อันเข้าลักษณะ User Execution: Malicious Link และ User Execution: Malicious File | (User Execution: Malicious Link , User Execution: Malicious File ) |
| 3 | named | T1059 Command and Scripting Interpreter | เครื่องได้ดาวน์โหลดไฟล์สคริปต์ภาษาจาวาสคริปต์ลงมาโดยผู้ใช้ไม่ทราบ และเมื่อไฟล์นั้นถูกเปิด สคริปต์จะติดต่อไปยังเครื่องสั่งการของคนร้ายเพื่อดาวน์โหลดตัวโปรแกรมม้าโทรจันเข้ามาติดตั้งบนเครื่องต่อไป | In clicking the photo, the victim unknowingly downloads a malicious JavaScript file that, when opened, automatically communicates with the malicious actor’s command and control (C2) server to download TrickBot to the vic… |

- [ ] ผ่าน / แก้แล้ว

## rcti_089 — FIN6 (CTID emulation plan FIN6.yaml)

ต้นทาง: <https://securityintelligence.com/posts/more_eggs-anyone-threat-actor-itg08-strikes-again/>

> เมื่อวันที่ 13 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายยกระดับสิทธิ์และรวบรวมข้อมูล จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายรันสคริปต์ที่สร้างช่องทางสื่อสารระหว่างกระบวนการขึ้นมาหลอกให้บริการของระบบเชื่อมต่อเข้ามา แล้วสวมสิทธิ์ประจำตัวของบริการนั้นเพื่อยกระดับตนเองขึ้นเป็นสิทธิ์ระดับระบบ ต่อมาปรากฏหลักฐานว่าคนร้ายเรียกสคริปต์จากเครื่องภายนอกเข้ามาทำงานผ่าน PowerShell เพื่อดึงค่ารหัสผ่านออกจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่อง สุดท้ายพบว่าคนร้ายนำไฟล์ข้อความที่รวบรวมไว้มาบีบอัดรวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดที่เปลี่ยนชื่อไฟล์ให้ดูไม่ผิดสังเกต เพื่อพักไว้เตรียมนำออกจากองค์กร

*EN:* On 13 May 2567 a retail chain filed a further report on how the offender escalated privileges and collected data. Digital forensic examination found the offender running a script that created an inter-process communication channel to lure a system service into connecting, then assuming that service's identity token to raise itself to system-level privileges. Evidence then showed the offender invoking a script from an external machine through PowerShell to extract password values from the memory of the machine's authentication process. Finally the offender was found compressing the collected text files into a single file with a compression program renamed to look unremarkable, staged ready to be taken out of the organisation.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1134 Access Token Manipulation | คนร้ายรันสคริปต์ที่สร้างช่องทางสื่อสารระหว่างกระบวนการขึ้นมาหลอกให้บริการของระบบเชื่อมต่อเข้ามา แล้วสวมสิทธิ์ประจำตัวของบริการนั้นเพื่อยกระดับตนเองขึ้นเป็นสิทธิ์ระดับระบบ | PowerSploit named-pipe impersonation, similar to the technique used to escalate to SYSTEM-level privileges by FIN6. |
| 2 | described | T1003 OS Credential Dumping | คนร้ายเรียกสคริปต์จากเครื่องภายนอกเข้ามาทำงานผ่าน PowerShell เพื่อดึงค่ารหัสผ่านออกจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่อง | Dump credentials from memory via PowerShell by invoking a remote Mimikatz script, similar to the procedure used by FIN6. FIN6 is reported to have used WCE to access credentials on at least one occasion. |
| 3 | described | T1560 Archive Collected Data | คนร้ายนำไฟล์ข้อความที่รวบรวมไว้มาบีบอัดรวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดที่เปลี่ยนชื่อไฟล์ให้ดูไม่ผิดสังเกต เพื่อพักไว้เตรียมนำออกจากองค์กร | Compress text files for exfiltration staging using 7zip, renamed to 7.exe |

- [ ] ผ่าน / แก้แล้ว

## rcti_090 — CISA AA23-352A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-352a>

> เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงเครื่องมือที่คนร้ายใช้ระหว่างอยู่ในเครือข่าย จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายรันชุดสคริปต์สำเร็จรูปบนเครื่องที่ยึดครองได้ เพื่อไล่ตรวจสอบหาช่องทางที่จะยกระดับสิทธิ์ของตนขึ้นไปได้อีก ต่อมาปรากฏหลักฐานว่าคนร้ายนำเครื่องมือหลายตัวเข้ามาใช้ปิดการทำงานของโปรแกรมป้องกันไวรัสที่ติดตั้งอยู่ และลบไฟล์บันทึกเหตุการณ์ของระบบทิ้ง สุดท้ายพบว่าเมื่อคนร้ายตั้งหลักในเครือข่ายได้แล้ว ได้ไล่ค้นหาข้อมูลรับรองตัวตนที่เก็บไว้โดยไม่ได้ป้องกันตามที่ต่าง ๆ ในระบบ และใช้เครื่องมือทำ Credential Dumping ดึงค่ารหัสผ่านออกจากหน่วยความจำ จนได้สิทธิ์ระดับผู้ดูแลโดเมนขององค์กร

*EN:* On 18 December 2566 a retail company filed a further report on the tools the offender used while inside the network. Digital forensic examination found the offender running a ready-made script suite on the compromised machine to search for further ways to raise their privileges. Evidence then showed the offender bringing in several tools to disable the installed antivirus software and delete the system event log files. Finally, once established in the network, the offender was found searching for unprotected stored credentials in various places in the system and using a Credential Dumping tool to extract password values from memory, obtaining domain administrator rights over the organisation.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1059 Command and Scripting Interpreter | คนร้ายรันชุดสคริปต์สำเร็จรูปบนเครื่องที่ยึดครองได้ เพื่อไล่ตรวจสอบหาช่องทางที่จะยกระดับสิทธิ์ของตนขึ้นไปได้อีก | According to open source reporting , to further enumerate vulnerabilities, Play ransomware actors use Windows Privilege Escalation Awesome Scripts (WinPEAS) to search for additional privilege escalation paths |
| 2 | described | T1562 ?, T1070 Indicator Removal | คนร้ายนำเครื่องมือหลายตัวเข้ามาใช้ปิดการทำงานของโปรแกรมป้องกันไวรัสที่ติดตั้งอยู่ และลบไฟล์บันทึกเหตุการณ์ของระบบทิ้ง | Actors also use tools like GMER, IOBit, and PowerTool to disable anti-virus software and remove log files |
| 3 | named | T1552 Unsecured Credentials, T1003 OS Credential Dumping | ได้ไล่ค้นหาข้อมูลรับรองตัวตนที่เก็บไว้โดยไม่ได้ป้องกันตามที่ต่าง ๆ ในระบบ และใช้เครื่องมือทำ Credential Dumping ดึงค่ารหัสผ่านออกจากหน่วยความจำ จนได้สิทธิ์ระดับผู้ดูแลโดเมนขององค์กร | Once established on a network, the ransomware actors search for unsecured credentials and use the Mimikatz credential dumper to gain domain administrator access |

- [ ] ผ่าน / แก้แล้ว

## rcti_091 — Turla - Carbon (CTID emulation plan turla_carbon.yaml)

> เมื่อวันที่ 6 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ถูกฝังโปรแกรมควบคุมระยะไกลหลังเปิดลิงก์ในอีเมล จากการตรวจสอบพบว่าเจ้าหน้าที่ได้รับจดหมายอิเล็กทรอนิกส์ที่เขียนถึงตนโดยเฉพาะ ภายในมีลิงก์ซึ่งเมื่อกดแล้วจะนำไปสู่การดาวน์โหลดไฟล์ตัวปล่อยโปรแกรมอันตรายลงมาไว้ในเครื่อง ต่อมาปรากฏหลักฐานว่าเจ้าหน้าที่ได้เปิดไฟล์ที่ดาวน์โหลดมาด้วยตนเอง ทำให้ตัวปล่อยโปรแกรมทำงานและวางโปรแกรมฝังตัวลงบนเครื่อง สุดท้ายเมื่อโปรแกรมทำงานแล้ว พบว่าคนร้ายรันคำสั่งไล่แจกแจงรายชื่อกลุ่มสิทธิ์ในโดเมนขององค์กร ควบคู่กับการเรียกดูรายการบริการที่กำลังทำงานอยู่บนเครื่องนั้น

*EN:* On 6 October 2566 a security agency reported that an officer's computer had been implanted with a remote control program after they opened a link in an email. Examination found the officer had received an email addressed specifically to them containing a link which, when clicked, led to a dropper file being downloaded onto the machine. Evidence then showed the officer opening the downloaded file themselves, causing the dropper to run and place an implant on the machine. Finally, once the program was running, the offender was found issuing commands to enumerate the permission groups in the organisation's domain, alongside reading the list of services running on that machine.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1566 Phishing | เจ้าหน้าที่ได้รับจดหมายอิเล็กทรอนิกส์ที่เขียนถึงตนโดยเฉพาะ ภายในมีลิงก์ซึ่งเมื่อกดแล้วจะนำไปสู่การดาวน์โหลดไฟล์ตัวปล่อยโปรแกรมอันตรายลงมาไว้ในเครื่อง | Using xdotool, send keystrokes to download the EPIC dropper. |
| 2 | described | T1204 User Execution | เจ้าหน้าที่ได้เปิดไฟล์ที่ดาวน์โหลดมาด้วยตนเอง ทำให้ตัวปล่อยโปรแกรมทำงานและวางโปรแกรมฝังตัวลงบนเครื่อง | Using xdotool, run the EPIC droppper. |
| 3 | described | T1069 Permission Groups Discovery | คนร้ายรันคำสั่งไล่แจกแจงรายชื่อกลุ่มสิทธิ์ในโดเมนขององค์กร ควบคู่กับการเรียกดูรายการบริการที่กำลังทำงานอยู่บนเครื่องนั้น | Execute net group discovery commands and execute `tasklist /svc` |

- [ ] ผ่าน / แก้แล้ว

## rcti_092 — CISA AA20-336A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-336a>

> เมื่อวันที่ 3 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายได้มาซึ่งรหัสผ่านและนำข้อมูลออก จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายหลบเลี่ยงกลไกที่ระบบใช้ถามยืนยันก่อนยกระดับสิทธิ์ ทำให้โปรแกรมของตนทำงานด้วยสิทธิ์ผู้ดูแลระบบโดยไม่มีหน้าต่างขออนุญาตปรากฏขึ้น ต่อมาปรากฏหลักฐานว่าคนร้ายใช้ทั้ง Brute Force: Password Cracking คือนำค่าแฮชรหัสผ่านที่ได้มาไปถอดรหัสนอกระบบ และ Brute Force: Password Spraying คือนำรหัสผ่านที่คาดเดาง่ายไปลองล็อกอินกับบัญชีจำนวนมาก จากนั้นพบว่าคนร้ายเข้าไปอ่าน Credentials from Web Browsers คือชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของผู้เสียหายบันทึกไว้ในเครื่อง สุดท้ายจากการตรวจสอบปริมาณข้อมูลขาออกพบว่าข้อมูลที่รวบรวมได้ถูกส่งออกไปทางโพรโทคอลรับส่งไฟล์ที่ไม่ได้เข้ารหัสลับ ซึ่งเป็นคนละช่องทางกับที่ใช้รับคำสั่ง

*EN:* On 3 December 2563 an agency filed a further report on how the offender obtained passwords and took data out. Digital forensic examination found the offender bypassing the mechanism the system uses to ask for confirmation before elevating privileges, so their program ran with administrator rights without any permission dialog appearing. Evidence then showed the offender using both Brute Force: Password Cracking — taking obtained password hashes and cracking them offline — and Brute Force: Password Spraying, trying easily guessed passwords against large numbers of accounts. The offender was then found reading Credentials from Web Browsers, the usernames and passwords the victim's browser had saved on the machine. Finally, examination of outbound traffic found the collected data sent out over an unencrypted file transfer protocol, a different channel from the one used to receive commands.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1548 Abuse Elevation Control Mechanism | คนร้ายหลบเลี่ยงกลไกที่ระบบใช้ถามยืนยันก่อนยกระดับสิทธิ์ ทำให้โปรแกรมของตนทำงานด้วยสิทธิ์ผู้ดูแลระบบโดยไม่มีหน้าต่างขออนุญาตปรากฏขึ้น | Abuse Elevation Control Mechanism: Bypass User Access Control |
| 2 | named | T1110 Brute Force | คนร้ายใช้ทั้ง Brute Force: Password Cracking คือนำค่าแฮชรหัสผ่านที่ได้มาไปถอดรหัสนอกระบบ และ Brute Force: Password Spraying คือนำรหัสผ่านที่คาดเดาง่ายไปลองล็อกอินกับบัญชีจำนวนมาก | Brute Force: Password Cracking Brute Force: Password Spraying |
| 3 | named | T1555 Credentials from Password Stores | คนร้ายเข้าไปอ่าน Credentials from Web Browsers คือชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของผู้เสียหายบันทึกไว้ในเครื่อง | Credentials from Password Stores: Credentials from Web Browsers |
| 4 | described | T1048 Exfiltration Over Alternative Protocol | ข้อมูลที่รวบรวมได้ถูกส่งออกไปทางโพรโทคอลรับส่งไฟล์ที่ไม่ได้เข้ารหัสลับ ซึ่งเป็นคนละช่องทางกับที่ใช้รับคำสั่ง | Exfiltration Over Alternative Protocol: Exfiltration Over Unencrypted/Obfuscated Non-C2 Protocol |

- [ ] ผ่าน / แก้แล้ว

## rcti_093 — APT29 (CTID emulation plan APT29.yaml)

ต้นทาง: <https://blog-assets.f-secure.com/wp-content/uploads/2020/03/18122307/F-Secure_Dukes_Whitepaper.pdf>

> เมื่อวันที่ 18 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความเพิ่มเติมถึงข้อมูลรับรองตัวตนที่ถูกขโมยไปจากเครื่องของเจ้าหน้าที่ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายรันโปรแกรมที่เข้าไปดึงชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของเจ้าหน้าที่บันทึกไว้ในเครื่องออกมาทั้งหมด ต่อมาปรากฏหลักฐานว่าคนร้ายรันสคริปต์ที่ขโมยสิทธิ์ประจำตัวจากกระบวนการของผู้ใช้รายอื่นที่เปิดค้างอยู่บนเครื่องเดียวกัน แล้วสวมสิทธิ์นั้นเพื่อสั่งงานในนามของผู้ใช้รายดังกล่าว สุดท้ายพบว่าคนร้ายรันสคริปต์ที่เขียนขึ้นเองไล่ค้นหาไฟล์กุญแจส่วนตัวสำหรับยืนยันตัวตนที่ผู้ใช้เก็บไว้ในเครื่องโดยไม่ได้ตั้งรหัสผ่านป้องกัน แล้วคัดลอกออกไป

*EN:* On 18 January 2567 a state enterprise filed a further report on the credentials stolen from a staff computer. Digital forensic examination found the offender running a program that extracted all the usernames and passwords the officer's web browser had saved on the machine. Evidence then showed the offender running a script that stole the identity token of another user's process still open on the same machine and assumed it in order to issue commands in that user's name. Finally the offender was found running a script of their own making to search for private authentication key files the user had stored on the machine without password protection, and copying them out.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1003 OS Credential Dumping | คนร้ายรันโปรแกรมที่เข้าไปดึงชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของเจ้าหน้าที่บันทึกไว้ในเครื่องออกมาทั้งหมด | Obtain credentials from Chrome Dumper |
| 2 | described | T1134 Access Token Manipulation | คนร้ายรันสคริปต์ที่ขโมยสิทธิ์ประจำตัวจากกระบวนการของผู้ใช้รายอื่นที่เปิดค้างอยู่บนเครื่องเดียวกัน แล้วสวมสิทธิ์นั้นเพื่อสั่งงานในนามของผู้ใช้รายดังกล่าว | A token theft script was executed to steal and assume the token of another user’s existing process, changing the user context of the process. |
| 3 | described | T1552 Unsecured Credentials | คนร้ายรันสคริปต์ที่เขียนขึ้นเองไล่ค้นหาไฟล์กุญแจส่วนตัวสำหรับยืนยันตัวตนที่ผู้ใช้เก็บไว้ในเครื่องโดยไม่ได้ตั้งรหัสผ่านป้องกัน แล้วคัดลอกออกไป | Obtain credentials via Custom PowerShell |

- [ ] ผ่าน / แก้แล้ว

## rcti_094 — CISA AA21-287A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-287a>

> เมื่อวันที่ 14 ตุลาคม 2564 การประปาส่วนภูมิภาคสาขาหนึ่งแจ้งความว่าระบบควบคุมการผลิตน้ำประปาถูกบุกรุก จากการตรวจสอบพบว่าคนร้ายส่งจดหมายอิเล็กทรอนิกส์หลอกลวงที่เขียนถึงเจ้าหน้าที่เป็นรายบุคคล โดยแนบไฟล์ที่เมื่อเปิดแล้วจะติดตั้งโปรแกรมอันตรายรวมถึงโปรแกรมเรียกค่าไถ่ลงบนเครื่อง ต่อมาปรากฏหลักฐานว่าคนร้ายอาศัยช่องโหว่ของบริการและแอปพลิเคชันที่เปิดให้เข้าถึงจากอินเทอร์เน็ตเพื่อเข้าใช้งานเครือข่ายของหน่วยงานจากระยะไกล แล้วขยายการเข้าถึงต่อไปยังเครื่องอื่นในเครือข่ายควบคุม สุดท้ายจากการประเมินความเสียหายพบว่าการเข้าถึงอุปกรณ์ควบคุมเหล่านี้ได้ ทำให้หน่วยงานอาจสูญเสียการควบคุมกระบวนการผลิต ระบบอาจหยุดให้บริการ และข้อมูลอ่อนไหวของหน่วยงานอาจรั่วไหลออกไป

*EN:* On 14 October 2564 a provincial waterworks branch reported that its water production control system had been breached. Examination found the offender sending phishing emails addressed to officers individually, attaching files which on opening installed malicious programs including ransomware on the machine. Evidence then showed the offender using vulnerabilities in services and applications reachable from the internet to reach the agency's network remotely, then widening access to other machines on the control network. Finally, damage assessment found that access to these control devices could cause the agency to lose control of the production process, the system to stop serving, and sensitive agency data to leak out.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1566 Phishing | คนร้ายส่งจดหมายอิเล็กทรอนิกส์หลอกลวงที่เขียนถึงเจ้าหน้าที่เป็นรายบุคคล โดยแนบไฟล์ที่เมื่อเปิดแล้วจะติดตั้งโปรแกรมอันตรายรวมถึงโปรแกรมเรียกค่าไถ่ลงบนเครื่อง | Spearphishing personnel to deliver malicious payloads, including ransomware |
| 2 | described | T1210 Exploitation of Remote Services | คนร้ายอาศัยช่องโหว่ของบริการและแอปพลิเคชันที่เปิดให้เข้าถึงจากอินเทอร์เน็ตเพื่อเข้าใช้งานเครือข่ายของหน่วยงานจากระยะไกล แล้วขยายการเข้าถึงต่อไปยังเครื่องอื่นในเครือข่ายควบคุม | Exploitation of internet-connected services and applications that enable remote access to WWS networks |
| 3 | described | T0827 ? | การเข้าถึงอุปกรณ์ควบคุมเหล่านี้ได้ ทำให้หน่วยงานอาจสูญเสียการควบคุมกระบวนการผลิต ระบบอาจหยุดให้บริการ และข้อมูลอ่อนไหวของหน่วยงานอาจรั่วไหลออกไป | Successful compromise of these devices may lead to loss of system control, denial of service, or loss of sensitive data |

- [ ] ผ่าน / แก้แล้ว

## rcti_095 — Turla - Snake (CTID emulation plan turla_snake.yaml)

> เมื่อวันที่ 20 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนสุดท้ายของการบุกรุกระบบจดหมายอิเล็กทรอนิกส์ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายสั่งให้โปรแกรมฝังตัวเปิดอ่านไฟล์บันทึกผลการติดตั้งผ่านหน้าต่างคำสั่งของวินโดวส์ เพื่อตรวจสอบว่าการติดตั้งครั้งก่อนมีข้อผิดพลาดใดหรือไม่ ต่อมาปรากฏหลักฐานว่าคนร้ายสั่งลบไฟล์และร่องรอยที่ตนทิ้งไว้บนเครื่องเป้าหมายเครื่องที่สี่ออกทั้งหมด จากนั้นพบว่าโปรแกรมที่ฝังอยู่บนเครื่องแม่ข่ายจดหมายได้รับคำสั่งให้เรียกดูรายละเอียดการตั้งค่าเครือข่ายของเครื่องแม่ข่ายนั้น สุดท้ายพบว่าคนร้ายสั่งให้โปรแกรมดังกล่าวส่งไฟล์บันทึกจดหมายอิเล็กทรอนิกส์ที่ดักเก็บไว้ออกไปยังคนร้าย โดยใช้ช่องทางเดียวกับที่โปรแกรมใช้ติดต่อรับคำสั่งอยู่แล้ว

*EN:* On 20 December 2566 a government agency filed a further report on the final stage of the mail system intrusion. Digital forensic examination found the offender having the implant read the installation log file through the Windows command window to check whether the previous installation had produced any errors. Evidence then showed the offender deleting all the files and traces they had left on the fourth target machine. The program implanted on the mail server was then found receiving a command to read that server's network configuration details. Finally the offender was found having that program send the captured email log file out to them, using the same channel the program already used to receive its commands.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1059 Command and Scripting Interpreter | คนร้ายสั่งให้โปรแกรมฝังตัวเปิดอ่านไฟล์บันทึกผลการติดตั้งผ่านหน้าต่างคำสั่งของวินโดวส์ เพื่อตรวจสอบว่าการติดตั้งครั้งก่อนมีข้อผิดพลาดใดหรือไม่ | Task Snake to check the installation log for any errors. |
| 2 | described | T1070 Indicator Removal | คนร้ายสั่งลบไฟล์และร่องรอยที่ตนทิ้งไว้บนเครื่องเป้าหมายเครื่องที่สี่ออกทั้งหมด | Task Snake to remove artifacts from the fourth target host: |
| 3 | described | T1016 System Network Configuration Discovery | โปรแกรมที่ฝังอยู่บนเครื่องแม่ข่ายจดหมายได้รับคำสั่งให้เรียกดูรายละเอียดการตั้งค่าเครือข่ายของเครื่องแม่ข่ายนั้น | Task LightNeuron to perform system network configuration discovery. |
| 4 | described | T1041 Exfiltration Over C2 Channel | คนร้ายสั่งให้โปรแกรมดังกล่าวส่งไฟล์บันทึกจดหมายอิเล็กทรอนิกส์ที่ดักเก็บไว้ออกไปยังคนร้าย โดยใช้ช่องทางเดียวกับที่โปรแกรมใช้ติดต่อรับคำสั่งอยู่แล้ว | Task the LightNeuron implant to exfiltrate the email log file. |

- [ ] ผ่าน / แก้แล้ว

## rcti_096 — CISA AA22-055A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-055a>

> เมื่อวันที่ 25 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งแจ้งความเพิ่มเติมถึงพฤติกรรมของไฟล์อันตรายที่ตรวจพบบนเครื่อง จากการตรวจสอบไฟล์ดังกล่าวพบว่าภายในบรรจุข้อความที่ถูกแปลงเป็นค่าฐานสิบหกและสลับตำแหน่งไว้ ทำให้อ่านไม่ออกและตรวจสอบเนื้อหาการทำงานได้ยาก ต่อมาปรากฏหลักฐานว่าเมื่อไฟล์นี้ทำงาน จะเก็บรวบรวมข้อมูลจากเครื่องของผู้เสียหาย ได้แก่ หมายเลขไอพีของเครื่อง ชื่อเครื่อง และชื่อบัญชีผู้ใช้ที่ล็อกอินอยู่ สุดท้ายจากการตรวจสอบปริมาณข้อมูลขาออกพบว่าข้อมูลที่เก็บรวบรวมได้ถูกแปลงเป็นค่าฐานสิบหกอีกครั้ง แล้วส่งออกไปยังหมายเลขไอพีที่คนร้ายควบคุมอยู่ผ่านคำขอแบบส่งข้อมูลของโพรโทคอลเว็บ ซึ่งเป็นช่องทางเดียวกับที่โปรแกรมใช้ติดต่อรับคำสั่ง

*EN:* On 25 February 2565 an educational institution filed a further report on the behaviour of the malicious file found on its machines. Examination of that file found it contained strings converted to hexadecimal values and reshuffled, making them unreadable and its behaviour hard to inspect. Evidence then showed that when this file ran it gathered information from the victim's machine — the machine's IP address, its name and the logged-in account name. Finally, examination of outbound traffic found the gathered data converted to hexadecimal again and sent out to an IP address under the offender's control via a web protocol POST request, the same channel the program used to receive its commands.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1027 Obfuscated Files or Information | ภายในบรรจุข้อความที่ถูกแปลงเป็นค่าฐานสิบหกและสลับตำแหน่งไว้ ทำให้อ่านไม่ออกและตรวจสอบเนื้อหาการทำงานได้ยาก | The file contains hexadecimal (hex)-encoded strings that have been reshuffled |
| 2 | described | T1005 Data from Local System | จะเก็บรวบรวมข้อมูลจากเครื่องของผู้เสียหาย ได้แก่ หมายเลขไอพีของเครื่อง ชื่อเครื่อง และชื่อบัญชีผู้ใช้ที่ล็อกอินอยู่ | This file collects [TA0035] the victim system’s IP address, computer name, and username |
| 3 | described | T1041 Exfiltration Over C2 Channel | ข้อมูลที่เก็บรวบรวมได้ถูกแปลงเป็นค่าฐานสิบหกอีกครั้ง แล้วส่งออกไปยังหมายเลขไอพีที่คนร้ายควบคุมอยู่ผ่านคำขอแบบส่งข้อมูลของโพรโทคอลเว็บ ซึ่งเป็นช่องทางเดียวกับที่โปรแกรมใช้ติดต่อรับคำสั่ง | The collected data is then hex-encoded and sent to an adversary-controlled IP address, http[:]88.119.170[.]124, via an HTTP POST request |

- [ ] ผ่าน / แก้แล้ว

## rcti_097 — CISA AA22-174A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-174a>

> เมื่อวันที่ 25 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดการเคลื่อนไหวของคนร้ายภายในเครือข่าย จากการตรวจสอบ log พบว่าไม่นานหลังเข้าถึงระบบได้ คนร้ายใช้สคริปต์ PowerShell ติดต่อออกไปยังหมายเลขไอพีภายนอกผ่านโพรโทคอลเว็บ เพื่อดึงสคริปต์ชุดถัดไปเข้ามาทำงานบนเครื่อง ต่อมาปรากฏหลักฐานว่าเมื่อยึดเครื่องแม่ข่ายเดสก์ท็อปเสมือนได้แล้ว คนร้ายเคลื่อนย้ายต่อไปยังเครื่องอื่นในระบบงานจริงผ่าน Remote Desktop Protocol ทั้งเครื่องแม่ข่ายบริหารจัดการความปลอดภัย เครื่องออกใบรับรอง ฐานข้อมูลที่เก็บข้อมูลการสืบสวนคดี และเครื่องส่งต่อจดหมายอิเล็กทรอนิกส์ จากการตรวจค้นเครื่องยังพบไฟล์บีบอัดที่บรรจุข้อมูลการสืบสวนคดีอ่อนไหวถูกสร้างขึ้นภายใต้บัญชีผู้ดูแลระบบที่ถูกยึดครอง ต่อมาในช่วงเวลาไล่เลี่ยกันพบว่าคนร้ายพยายามดาวน์โหลดไฟล์อันตรายจากหมายเลขไอพีภายนอกเดิมเข้ามาสั่งให้ทำงานบนเครื่อง สุดท้ายจากการตรวจสอบเนื้อหาที่รับส่งพบว่าการติดต่อทั้งขาเข้าและขาออกของไฟล์นั้นถูกแปลงด้วยกุญแจลับทุกครั้ง ทำให้อ่านเนื้อหาไม่ได้

*EN:* On 25 June 2565 an agency filed a further report detailing the offender's movements inside the network. Logs showed that shortly after gaining access, the offender used PowerShell scripts to call out to an external IP address over a web protocol to pull in the next set of scripts to run on the machine. Evidence then showed that having taken the virtual desktop server, the offender moved on to other machines in the production environment over Remote Desktop Protocol — the security management server, the certificate server, a database holding case investigation data and the mail relay server. Searches of the machines also found compressed files containing sensitive case investigation data created under a compromised administrator account. Around the same period the offender was found attempting to download a malicious file from the same external IP address and run it on the machine. Finally, examination of the exchanged content found the file's inbound and outbound communications always transformed with a secret key, leaving the content unreadable.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1059 Command and Scripting Interpreter, T1071 Application Layer Protocol | คนร้ายใช้สคริปต์ PowerShell ติดต่อออกไปยังหมายเลขไอพีภายนอกผ่านโพรโทคอลเว็บ เพื่อดึงสคริปต์ชุดถัดไปเข้ามาทำงานบนเครื่อง | On or around January 30, likely shortly after the threat actors gained access, CISA observed the actors using PowerShell scripts to callout to 109.248.150[.]13 via Hypertext Transfer Protocol (HTTP) to retrieve additiona… |
| 2 | named | T1021 Remote Services | คนร้ายเคลื่อนย้ายต่อไปยังเครื่องอื่นในระบบงานจริงผ่าน Remote Desktop Protocol ทั้งเครื่องแม่ข่ายบริหารจัดการความปลอดภัย เครื่องออกใบรับรอง ฐานข้อมูลที่เก็บข้อมูลการสืบสวนคดี และเครื่องส่งต่อจดหมายอิเล็กทรอนิกส์ | After gaining initial access to the VMware Horizon server, the threat actors moved laterally [TA0008] via Remote Desktop Protocol (RDP) to multiple other hosts in the production environment, including a security manageme… |
| 3 | described | T1560 Archive Collected Data | พบไฟล์บีบอัดที่บรรจุข้อมูลการสืบสวนคดีอ่อนไหวถูกสร้างขึ้นภายใต้บัญชีผู้ดูแลระบบที่ถูกยึดครอง | CISA also found .rar files containing sensitive law enforcement investigation data under a known compromised administrator account |
| 4 | described | T1105 Ingress Tool Transfer | คนร้ายพยายามดาวน์โหลดไฟล์อันตรายจากหมายเลขไอพีภายนอกเดิมเข้ามาสั่งให้ทำงานบนเครื่อง | Around the same period, CISA observed the actors attempt to download and execute a malicious file from 109.248.150[.]13 |
| 5 | described | T1573 Encrypted Channel | การติดต่อทั้งขาเข้าและขาออกของไฟล์นั้นถูกแปลงด้วยกุญแจลับทุกครั้ง ทำให้อ่านเนื้อหาไม่ได้ | The executable’s inbound and outbound communications are encrypted with an XOR key Commands and data sent are encrypted via RC4 |

- [ ] ผ่าน / แก้แล้ว

## rcti_098 — FIN6 (CTID emulation plan FIN6.yaml)

ต้นทาง: <https://www.fireeye.com/blog/threat-research/2020/05/tactics-techniques-procedures-associated-with-maze-ransomware-incidents.html>

> เมื่อวันที่ 22 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าโปรแกรมเรียกค่าไถ่ถูกกระจายไปทั่วองค์กรพร้อมกัน จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายอาศัยกลไกบริหารจัดการเครื่องของวินโดวส์เป็นช่องทางกระจายโปรแกรมเรียกค่าไถ่ไปยังเครื่องเป้าหมายที่กำหนดไว้ ต่อมาปรากฏหลักฐานว่าคนร้ายสั่งคำสั่งผ่านหน้าต่างคำสั่งเพื่อคัดลอกไฟล์โปรแกรมเรียกค่าไถ่ ไฟล์สคริปต์สำหรับกระจายงาน และไฟล์สคริปต์สำหรับหยุดการทำงานของโปรแกรมอื่น ไปเก็บไว้บนเครื่องแม่ข่ายที่ใช้เป็นจุดกระจายภายในองค์กร โดยส่งผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบบ จากนั้นพบว่าคนร้ายใช้กลไกบริหารจัดการเครื่องเดียวกันสั่งให้สคริปต์หยุดการทำงานของโปรแกรมอื่นและตัวโปรแกรมเรียกค่าไถ่ทำงานบนเครื่องเป้าหมายทั้งหมด สุดท้ายพบว่าคนร้ายยังใช้เครื่องมือสั่งงานเครื่องระยะไกลอีกตัวหนึ่ง สร้างบริการของระบบขึ้นบนเครื่องเป้าหมายเพื่อสั่งรันสคริปต์และโปรแกรมเรียกค่าไถ่ซ้ำอีกทางหนึ่ง

*EN:* On 22 May 2567 a retail chain filed a further report that ransomware had been distributed across the whole organisation at once. Digital forensic examination found the offender using the Windows machine management mechanism as a channel to distribute the ransom program to designated target machines. Evidence then showed the offender issuing commands through the command window to copy the ransom program file, a distribution script and a script for stopping other programs onto a server used as an internal distribution point, sending them through the administrative file sharing channel. The offender was then found using the same machine management mechanism to run the program-stopping script and the ransom program itself on all target machines. Finally the offender was found also using another remote command tool to create a system service on target machines in order to run the scripts and the ransom program by a second route.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1047 Windows Management Instrumentation | คนร้ายอาศัยกลไกบริหารจัดการเครื่องของวินโดวส์เป็นช่องทางกระจายโปรแกรมเรียกค่าไถ่ไปยังเครื่องเป้าหมายที่กำหนดไว้ | FIN6 utilizes WMI to distribute ransomware to intended targets |
| 2 | described | T1021 Remote Services | คนร้ายสั่งคำสั่งผ่านหน้าต่างคำสั่งเพื่อคัดลอกไฟล์โปรแกรมเรียกค่าไถ่ ไฟล์สคริปต์สำหรับกระจายงาน และไฟล์สคริปต์สำหรับหยุดการทำงานของโปรแกรมอื่น ไปเก็บไว้บนเครื่องแม่ข่ายที่ใช้เป็นจุดกระจายภายในองค์กร โดยส่งผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบบ | FIN6 utilizes cmd to copy ransomware to an internal distribution server FIN6 utilizes cmd to copy distribution scripts to an internal distribution server FIN6 utilizes cmd to copy kill scripts to an internal distribution… |
| 3 | described | T1047 Windows Management Instrumentation | คนร้ายใช้กลไกบริหารจัดการเครื่องเดียวกันสั่งให้สคริปต์หยุดการทำงานของโปรแกรมอื่นและตัวโปรแกรมเรียกค่าไถ่ทำงานบนเครื่องเป้าหมายทั้งหมด | FIN6 utilizes WMI to distribute ransomware to intended targets FIN6 has utilized WMI to distribute kill scripts to intended targets FIN6 has utilized WMI to execute kill scripts on intended targets FIN6 has utilized WMI … |
| 4 | described | T1569 System Services | คนร้ายยังใช้เครื่องมือสั่งงานเครื่องระยะไกลอีกตัวหนึ่ง สร้างบริการของระบบขึ้นบนเครื่องเป้าหมายเพื่อสั่งรันสคริปต์และโปรแกรมเรียกค่าไถ่ซ้ำอีกทางหนึ่ง | FIN6 has utilized PsExec to execute kill scripts on intended targets FIN6 has utilized PsExec to execute ransomware on intended targets |

- [ ] ผ่าน / แก้แล้ว

## rcti_099 — CISA AA20-266A (Zenodo 10.5281/zenodo.14659512)

ต้นทาง: <https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-266a>

> เมื่อวันที่ 22 กันยายน 2563 ผู้เสียหายหลายรายแจ้งความว่าบัญชีผู้ใช้งานออนไลน์ของตนถูกสวมรอยหลังติดโปรแกรมขโมยรหัสผ่าน จากการตรวจสอบพบว่าคนร้ายกระจายโปรแกรมดังกล่าวไปยังเครื่องระบบวินโดวส์และโทรศัพท์ระบบแอนดรอยด์ ผ่านทางอีเมล เว็บไซต์อันตราย ข้อความสั้น และข้อความส่วนตัวในช่องทางอื่น โดยผู้เสียหายเป็นผู้เปิดไฟล์ที่ได้รับด้วยตนเอง อันเข้าลักษณะ User Execution: Malicious File ต่อมาปรากฏหลักฐานว่าโปรแกรมดังกล่าวสร้างช่องทางลับไว้ในเครื่องที่ติด โดยอาศัยกลไกเรียกใช้งานฟีเจอร์ช่วยการเข้าถึงของระบบปฏิบัติการ ซึ่งเข้าลักษณะ Event Triggered Execution: Accessibility Features เพื่อให้คนร้ายกลับเข้ามาติดตั้งโปรแกรมเพิ่มเติมได้ภายหลัง จากนั้นพบว่าโปรแกรมขโมยข้อมูลรับรองตัวตนด้วยการดักบันทึกแป้นพิมพ์และเฝ้าดูการใช้งานทั้งบนโปรแกรมท่องเว็บและบนหน้าจอทั่วไป ตรงกับลักษณะ Credentials from Password Stores สุดท้ายจากการตรวจสอบพบว่าโปรแกรมยังเข้าไปอ่านชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของผู้เสียหายบันทึกเก็บไว้ในเครื่องออกมาด้วย

*EN:* On 22 September 2563 several victims reported their online accounts being impersonated after infection with a password-stealing program. Examination found the offender distributing that program to Windows machines and Android phones by email, malicious websites, text messages and private messages on other channels, with victims opening the received file themselves — matching User Execution: Malicious File. Evidence then showed the program creating a hidden channel on infected machines by way of the operating system's accessibility feature invocation mechanism, matching Event Triggered Execution: Accessibility Features, so the offender could return later to install further payloads. The program was then found stealing credentials by logging keystrokes and watching activity both in the browser and on the desktop generally, matching Credentials from Password Stores. Finally the program was found also reading out the usernames and passwords the victim's browser had saved on the machine.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | named | T1204 User Execution | คนร้ายกระจายโปรแกรมดังกล่าวไปยังเครื่องระบบวินโดวส์และโทรศัพท์ระบบแอนดรอยด์ ผ่านทางอีเมล เว็บไซต์อันตราย ข้อความสั้น และข้อความส่วนตัวในช่องทางอื่น โดยผู้เสียหายเป็นผู้เปิดไฟล์ที่ได้รับด้วยตนเอง อันเข้าลักษณะ User Execution: Malicious File | Malicious cyber actors typically use LokiBot to target Windows and Android operating systems and distribute the malware via email, malicious websites, text, and other private messages (User Execution: Malicious File ) |
| 2 | named | T1546 Event Triggered Execution | โปรแกรมดังกล่าวสร้างช่องทางลับไว้ในเครื่องที่ติด โดยอาศัยกลไกเรียกใช้งานฟีเจอร์ช่วยการเข้าถึงของระบบปฏิบัติการ ซึ่งเข้าลักษณะ Event Triggered Execution: Accessibility Features | LokiBot can also create a backdoor into infected systems to allow an attacker to install additional payloads (Event Triggered Execution: Accessibility Features ) |
| 3 | named | T1555 Credentials from Password Stores | โปรแกรมขโมยข้อมูลรับรองตัวตนด้วยการดักบันทึกแป้นพิมพ์และเฝ้าดูการใช้งานทั้งบนโปรแกรมท่องเว็บและบนหน้าจอทั่วไป ตรงกับลักษณะ Credentials from Password Stores | The malware steals credentials through the use of a keylogger to monitor browser and desktop activity (Credentials from Password Stores ) (Credentials from Password Stores: Credentials from Web Browsers ) |
| 4 | described | T1555 Credentials from Password Stores | โปรแกรมยังเข้าไปอ่านชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บของผู้เสียหายบันทึกเก็บไว้ในเครื่องออกมาด้วย | Credentials from Password Stores: Credentials from Web Browsers |

- [ ] ผ่าน / แก้แล้ว

## rcti_100 — FIN6 (CTID emulation plan FIN6.yaml)

ต้นทาง: <https://www.fireeye.com/blog/threat-research/2019/04/pick-six-intercepting-a-fin6-intrusion.html>

> เมื่อวันที่ 7 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าก่อนเกิดเหตุมีการสำรวจข้อมูลทะเบียนโดเมนขององค์กรอย่างเป็นระบบ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าคนร้ายใช้เครื่องมือสอบถามข้อมูลจากระบบทะเบียนโดเมนไล่ค้นหารายการบัญชีบุคคลทั้งหมดในโดเมน แล้วบันทึกผลลัพธ์ลงเป็นไฟล์ข้อความไว้บนเครื่อง ต่อมาได้ไล่ค้นหารายการเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนอยู่ในโดเมนพร้อมบันทึกผลลงไฟล์เช่นกัน จากนั้นปรากฏหลักฐานว่าคนร้ายแจกแจงรายการหน่วยจัดการภายในโดเมนที่ผู้ใช้รายนั้นสังกัดอยู่ และค้นหาความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนทั้งหมดในโครงสร้างขององค์กรออกมาเก็บไว้ ต่อมายังพบการเรียกดูรายการช่วงหมายเลขเครือข่ายย่อยที่องค์กรใช้งานอยู่ และสุดท้ายพบการแจกแจงรายชื่อกลุ่มสิทธิ์ทั้งหมดในโดเมนพร้อมบันทึกผลลัพธ์ลงไฟล์ข้อความ

*EN:* On 7 May 2567 a retail chain filed a further report that systematic reconnaissance of the organisation's domain directory had taken place before the incident. Digital forensic examination found the offender using a directory query tool to enumerate all person accounts in the domain, writing the results to a text file on the machine. They then enumerated all computers registered in the domain, likewise writing the results to a file. Evidence then showed the offender enumerating the organisational units the user belonged to and retrieving the trust relationships between all domains in the organisation's structure. Enumeration of the subnet ranges in use by the organisation was then found, and finally enumeration of all permission groups in the domain with the results written to a text file.

| # | cue_type | technique | cue (ไทย) | ต้นฉบับ (EN) |
|---|----------|-----------|-----------|--------------|
| 1 | described | T1087 Account Discovery | คนร้ายใช้เครื่องมือสอบถามข้อมูลจากระบบทะเบียนโดเมนไล่ค้นหารายการบัญชีบุคคลทั้งหมดในโดเมน แล้วบันทึกผลลัพธ์ลงเป็นไฟล์ข้อความไว้บนเครื่อง | Find all person objects and output the results to a text file. |
| 2 | described | T1018 Remote System Discovery | ได้ไล่ค้นหารายการเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนอยู่ในโดเมนพร้อมบันทึกผลลงไฟล์เช่นกัน | Identify all computer objects and output the results to a text file. |
| 3 | described | T1482 Domain Trust Discovery | คนร้ายแจกแจงรายการหน่วยจัดการภายในโดเมนที่ผู้ใช้รายนั้นสังกัดอยู่ และค้นหาความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนทั้งหมดในโครงสร้างขององค์กรออกมาเก็บไว้ | Enumerate all Organizational Units (OUs) in the domain of the user running the command and output the results to a text file. Performs a full forest search and dumps trust objects to a text file. |
| 4 | described | T1016 System Network Configuration Discovery | พบการเรียกดูรายการช่วงหมายเลขเครือข่ายย่อยที่องค์กรใช้งานอยู่ | List subnets and output the results to a text file. |
| 5 | described | T1069 Permission Groups Discovery | พบการแจกแจงรายชื่อกลุ่มสิทธิ์ทั้งหมดในโดเมนพร้อมบันทึกผลลัพธ์ลงไฟล์ข้อความ | List groups and output the results to a text file. |

- [ ] ผ่าน / แก้แล้ว
