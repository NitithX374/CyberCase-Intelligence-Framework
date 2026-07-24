# Incident Draft Review Sheet

ตรวจแต่ละข้อ: (1) สำนวนเหมือนสำนวนคดีจริงไหม (2) cue ตรงกับ technique จริงไหม
(3) step แบบ described ไม่เผลอบอกชื่อเทคนิค — แก้ไขในไฟล์ incident_draft.json
แล้วลบข้อที่ใช้ไม่ได้ทิ้ง

## inc_camp2_001  (source: SharePoint ToolShell Exploitation C0058)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบคอมพิวเตอร์เซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ระบบพบว่าผู้โจมตีได้ทำการ Modify Registry เพื่อสร้างความถาวรในระบบปฏิบัติการ Windows Server 2016 ต่อมาจากการวิเคราะห์ไฟล์ประวัติกิจกรรม (event log) พบหลักฐานว่าผู้โจมตีได้สืบค้นข้อมูลบัญชีผู้ใช้ที่มีสิทธิ์ระดับสูง และเรียกดูข้อมูลโครงสร้างระบบเครือข่ายภายในองค์กร จากนั้นการตรวจสอบพยานหลักฐานดิจิทัลยังพบว่ามีการรวบรวมข้อมูลขนาดใหญ่จากฐานข้อมูลลูกค้าและบันทึกการทำธุรกรรมโดยใช้เครื่องมือ Automated Collection ที่ติดตั้งอยู่ในระบบ สุดท้าย จากการตรวจสอบการเชื่อมต่อเครือข่ายพบว่าข้อมูลที่รวบรวมได้ถูกส่งออกผ่านช่องทางการสื่อสารที่ผ่านการเข้ารหัสและซ่อนอยู่ในการเชื่อมต่อ HTTPS ปกติ ซึ่งใช้เป็นทางเชื่อมต่อกับเซิร์ฟเวอร์ควบคุมภายนอก

*EN:* On 22 February 2569, a private financial company in Bangkok reported unauthorized access to its primary server computer system. System log examination revealed that the attacker performed Modify Registry to establish persistence on Windows Server 2016 operating system. Subsequently, analysis of activity history files (event logs) uncovered evidence that the attacker enumerated user accounts with high-level privileges and examined internal network infrastructure information. Further digital forensic examination revealed large-scale data collection from customer databases and transaction records using an Automated Collection tool installed on the system. Finally, network traffic investigation showed that collected data was exfiltrated through an encrypted channel disguised within normal HTTPS connections, used as a communication path to an external control server.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1112 Modify Registry | ผู้โจมตีได้ทำการ Modify Registry เพื่อสร้างความถาวรในระบบปฏิบัติการ Windows Server 2016 |
| 2 | described | T1033 System Owner/User Discovery | ผู้โจมตีได้สืบค้นข้อมูลบัญชีผู้ใช้ที่มีสิทธิ์ระดับสูง และเรียกดูข้อมูลโครงสร้างระบบเครือข่ายภายในองค์กร |
| 3 | named | T1119 Automated Collection | มีการรวบรวมข้อมูลขนาดใหญ่จากฐานข้อมูลลูกค้าและบันทึกการทำธุรกรรมโดยใช้เครื่องมือ Automated Collection ที่ติดตั้งอยู่ในระบบ |
| 4 | described | T1572 Protocol Tunneling | ข้อมูลที่รวบรวมได้ถูกส่งออกผ่านช่องทางการสื่อสารที่ผ่านการเข้ารหัสและซ่อนอยู่ในการเชื่อมต่อ HTTPS ปกติ ซึ่งใช้เป็นทางเชื่อมต่อกับเซิร์ฟเวอร์ควบคุมภายนอก |
| 5 | described | T1041 Exfiltration Over C2 Channel | ข้อมูลที่รวบรวมได้ถูกส่งออกผ่านช่องทางการสื่อสารที่ผ่านการเข้ารหัสและซ่อนอยู่ในการเชื่อมต่อ HTTPS ปกติ ซึ่งใช้เป็นทางเชื่อมต่อกับเซิร์ฟเวอร์ควบคุมภายนอก |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_002  (source: Anthropic AI-orchestrated Campaign C0062)

**AUTO-FLAGS: step 3: cue not found verbatim in narrative; step 4: described cue names the technique (Exfiltration Over Web Service)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนแห่งหนึ่งที่ประกอบกิจการด้านการจัดการลอจิสติกส์ในจังหวัดสมุทรปราการได้แจ้งความว่าระบบเว็บแอปพลิเคชันสาธารณะของบริษัท (customer portal) ถูกเข้าถึงโดยไม่ได้รับอนุญาต โดยจากการตรวจสอบ log พบว่าผู้โจมตีได้ส่งคำขอ HTTP ที่มีพารามิเตอร์ที่ผิดปกติเข้าไปในหน้า login form ซึ่งส่งผลให้ได้รับการยืนยันตัวตนและเข้าสู่ระบบเป็นผู้ใช้ระดับสูง ต่อมาจากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าผู้โจมตีได้ทำการ Valid Accounts โดยใช้บัญชีผู้ดูแลระบบที่ถูกบุกรุก เพื่อสำรวจและค้นหา Account Discovery ของพนักงานอื่นๆ ในระบบไดเรกทอรี่ของบริษัท จากนั้นผู้โจมตีได้ทำการส่งข้อมูลลูกค้าจำนวนมากออกจากระบบผ่าน Exfiltration Over Web Service โดยการเชื่อมต่อไปยังเซิร์ฟเวอร์ภายนอกประเทศ ส่วนข้อมูลที่ถูกดึงออกไปประกอบด้วยฐานข้อมูลลูกค้า ประมาณ 150,000 เรคอร์ด รวมถึงข้อมูลการจัดส่งและที่อยู่ของผู้รับสินค้า

*EN:* On 22 February 2569, a private logistics company in Samut Prakan Province reported unauthorized access to its public-facing web application (customer portal). Log analysis revealed that the attacker submitted malformed HTTP requests with unusual parameters to the login form, resulting in successful authentication and access as a high-privilege user. Subsequent digital forensic examination showed the attacker used Valid Accounts by leveraging the compromised administrator account to perform Account Discovery, searching the company's directory system for other employee accounts. The attacker then exfiltrated customer data by Exfiltration Over Web Service, establishing connections to external servers outside Thailand. Approximately 150,000 customer records were extracted, including delivery information and recipient addresses.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ส่งคำขอ HTTP ที่มีพารามิเตอร์ที่ผิดปกติเข้าไปในหน้า login form ซึ่งส่งผลให้ได้รับการยืนยันตัวตนและเข้าสู่ระบบเป็นผู้ใช้ระดับสูง |
| 2 | named | T1078 Valid Accounts | ผู้โจมตีได้ทำการ Valid Accounts โดยใช้บัญชีผู้ดูแลระบบที่ถูกบุกรุก |
| 3 | named | T1087 Account Discovery | ผู้โจมตีได้ทำการ Account Discovery ของพนักงานอื่นๆ ในระบบไดเรกทอรี่ของบริษัท |
| 4 | described | T1567 Exfiltration Over Web Service | ผู้โจมตีได้ทำการส่งข้อมูลลูกค้าจำนวนมากออกจากระบบผ่าน Exfiltration Over Web Service โดยการเชื่อมต่อไปยังเซิร์ฟเวอร์ภายนอกประเทศ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_003  (source: C0015 C0015)

**AUTO-FLAGS: step 1: described cue names the technique (Windows Management Instrumentation)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการข้อมูลแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบเครื่องคอมพิวเตอร์ของพนักงานในแผนกบัญชีถูกใช้งานโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีทำการเรียกใช้ script ผ่าน Windows Management Instrumentation เพื่อให้ได้สิทธิการเข้าถึงระบบ ต่อมาผู้โจมตีทำการ Domain trust discovery เพื่อสำรวจความสัมพันธ์ของโดเมนและเครือข่ายภายในองค์กร จากนั้นผู้โจมตีเข้าถึงข้อมูลจากไดรฟ์ที่ใช้ร่วมกันในเครือข่าย โดยคัดลอกไฟล์เอกสารสำคัญจำนวนมากไปยังตำแหน่งการจัดเก็บชั่วคราว สุดท้ายผู้โจมตีทำการเข้ารหัสข้อมูล (Data Encrypted for Impact) ในหลายเครื่องเพื่อให้ข้อมูลเหล่านั้นไม่สามารถเข้าถึงได้ และทิ้งข้อความเรียกร้องค่าไถ่ไว้ในไฟล์ข้อความบนเดสก์ทอป

*EN:* On 22 February 2569, a private data management company in Bangkok reported that employee computers in the accounting department were accessed without authorization. Digital forensic examination of logs revealed that the attacker executed script via Windows Management Instrumentation to gain system access. Subsequently, the attacker performed Domain trust discovery to enumerate domain relationships and internal network topology. The attacker then accessed data from shared network drives, copying numerous sensitive documents to temporary storage locations. Finally, the attacker encrypted data (Data Encrypted for Impact) across multiple machines to render files inaccessible and left ransom demand messages in text files on affected desktops.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1047 Windows Management Instrumentation | ผู้โจมตีทำการเรียกใช้ script ผ่าน Windows Management Instrumentation เพื่อให้ได้สิทธิการเข้าถึงระบบ |
| 2 | named | T1482 Domain Trust Discovery | ผู้โจมตีทำการ Domain trust discovery เพื่อสำรวจความสัมพันธ์ของโดเมนและเครือข่ายภายในองค์กร |
| 3 | described | T1039 Data from Network Shared Drive | ผู้โจมตีเข้าถึงข้อมูลจากไดรฟ์ที่ใช้ร่วมกันในเครือข่าย โดยคัดลอกไฟล์เอกสารสำคัญจำนวนมากไปยังตำแหน่งการจัดเก็บชั่วคราว |
| 4 | named | T1486 Data Encrypted for Impact | ผู้โจมตีทำการเข้ารหัสข้อมูล (Data Encrypted for Impact) ในหลายเครื่องเพื่อให้ข้อมูลเหล่านั้นไม่สามารถเข้าถึงได้ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_004  (source: 2016 Ukraine Electric Power Attack C0025)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนจัดการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานคร แจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ระบบพบว่าผู้โจมตีได้ใช้ Windows Management Instrumentation เพื่อรันคำสั่งลับบนเครื่องเซิร์ฟเวอร์ตั้งแต่เวลา 03:47 น. ต่อมาจากการวิเคราะห์ไฟล์ไบนารีของโปรแกรม svchost.exe พบรหัสอันตรายแฝงอยู่ในตำแหน่งที่ผิดปกติ ซึ่งบ่งชี้ว่าไฟล์ดังกล่าวได้รับการปรับแต่งเพื่อให้ทำงานตามคำสั่งของผู้โจมตี จากนั้นในวันถัดมา ทีมเทคนิคพบว่าบัญชีผู้ใช้ระบบชื่อ 'admin_service' ซึ่งเดิมมีสิทธิ์ปกติได้ถูกเปลี่ยนแปลงให้มีสิทธิ์เข้าถึงระดับสูงสุด และเพิ่มลงในกลุ่มผู้ดูแลระบบแล้ว สุดท้ายจากการสืบสวนเพิ่มเติมพบร่องรอย brute force attack ที่มุ่งทดลองรหัสผ่านหลายพันครั้งต่อบัญชีผู้ใช้งานต่างๆ ระหว่างวันที่ 20-21 กุมภาพันธ์ และพบหลักฐานว่าเครื่องมือ PuTTY และ WinSCP ได้ถูกคัดลอกไปยังเซิร์ฟเวอร์เครือข่ายอื่นเพื่อสำเร็จการเคลื่อนไหวในระบบต่อเนื่อง

*EN:* On 22 February 2569, a private financial management company in Bangkok reported unauthorized access to its primary server system. Log analysis revealed that the attacker used Windows Management Instrumentation to execute hidden commands on the server starting at 03:47. Subsequently, examination of the svchost.exe binary file identified malicious code embedded in an abnormal location, indicating the file had been modified to execute attacker commands. The following day, the technical team discovered that the system account 'admin_service', which previously held standard privileges, had been altered to possess highest-level access rights and added to the administrator group. Further investigation uncovered evidence of brute force attack attempts that tested thousands of password combinations against multiple user accounts between 20-21 February. Additionally, tools including PuTTY and WinSCP were found to have been copied to other networked servers to facilitate continued lateral movement within the system.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1047 Windows Management Instrumentation | ผู้โจมตีได้ใช้ Windows Management Instrumentation เพื่อรันคำสั่งลับบนเครื่องเซิร์ฟเวอร์ |
| 2 | described | T1554 Compromise Host Software Binary | จากการวิเคราะห์ไฟล์ไบนารีของโปรแกรม svchost.exe พบรหัสอันตรายแฝงอยู่ในตำแหน่งที่ผิดปกติ ซึ่งบ่งชี้ว่าไฟล์ดังกล่าวได้รับการปรับแต่งเพื่อให้ทำงานตามคำสั่งของผู้โจมตี |
| 3 | described | T1098 Account Manipulation | บัญชีผู้ใช้ระบบชื่อ 'admin_service' ซึ่งเดิมมีสิทธิ์ปกติได้ถูกเปลี่ยนแปลงให้มีสิทธิ์เข้าถึงระดับสูงสุด และเพิ่มลงในกลุ่มผู้ดูแลระบบแล้ว |
| 4 | named | T1110 Brute Force | พบร่องรอย brute force attack ที่มุ่งทดลองรหัสผ่านหลายพันครั้งต่อบัญชีผู้ใช้งานต่างๆ |
| 5 | named | T1570 Lateral Tool Transfer | เครื่องมือ PuTTY และ WinSCP ได้ถูกคัดลอกไปยังเซิร์ฟเวอร์เครือข่ายอื่นเพื่อสำเร็จการเคลื่อนไหวในระบบต่อเนื่อง |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_005  (source: RedDelta Modified PlugX Infection Chain Operations C0047)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบคอมพิวเตอร์ของพนักงานหลายคนได้รับความเสียหาย จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่า ผู้โจมตีได้ส่งไฟล์ PDF ที่มีการ Exploitation for Client Execution ฝังตัวอยู่ภายใน ซึ่งเมื่อพนักงานเปิดไฟล์ดังกล่าวก็ได้รับการดำเนินการโดยไม่ได้รับอนุญาต จากนั้นจากการวิเคราะห์ process memory และ registry พบร่องรอยการสืบค้นข้อมูลระบบ เช่น การอ่านค่า Windows version, installed software list, network configuration และ user account information ต่อมาจากการตรวจสอบ network traffic logs พบว่าเครื่องคอมพิวเตอร์ที่ติดเชื้อได้ติดต่อกับเซิร์ฟเวอร์ภายนอกผ่าน Non-Application Layer Protocol ที่ใช้ raw socket communication โดยไม่ผ่าน standard HTTP หรือ HTTPS channels

*EN:* On 22 February 2569, a private logistics management company in Samut Prakan Province reported damage to multiple employee computers. Digital forensic examination revealed that the attacker sent a PDF file with Exploitation for Client Execution embedded within it, which executed unauthorized actions when employees opened the file. Subsequently, analysis of process memory and registry traces showed evidence of system information discovery, such as reading Windows version, installed software lists, network configuration, and user account information. Later, network traffic log examination revealed that the infected computers contacted external servers via Non-Application Layer Protocol using raw socket communication that bypassed standard HTTP or HTTPS channels.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1203 Exploitation for Client Execution | ผู้โจมตีได้ส่งไฟล์ PDF ที่มีการ Exploitation for Client Execution ฝังตัวอยู่ภายใน |
| 2 | described | T1082 System Information Discovery | จากการวิเคราะห์ process memory และ registry พบร่องรอยการสืบค้นข้อมูลระบบ เช่น การอ่านค่า Windows version, installed software list, network configuration และ user account information |
| 3 | named | T1095 Non-Application Layer Protocol | เครื่องคอมพิวเตอร์ที่ติดเชื้อได้ติดต่อกับเซิร์ฟเวอร์ภายนอกผ่าน Non-Application Layer Protocol ที่ใช้ raw socket communication |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_006  (source: Operation Sharpshooter C0013)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีใช้ Native API เพื่อดำเนินการโปรแกรมอันตรายบนเครื่องลูกข่ายของพนักงาน ต่อมาจากการวิเคราะห์หน่วยความจำ (memory dump) พบร่องรอยของกระบวนการที่ถูกฉีดเข้าไปในโปรแกรม svchost.exe ซึ่งเป็นกระบวนการระบบถูกต้องตามกฎหมาย ทำให้ผู้โจมตีมีสิทธิ์เข้าถึงทรัพยากรระดับสูง จากนั้นจากการติดตามการสื่อสารเครือข่ายพบว่ามีการถ่ายโอนเครื่องมือโจมตีเพิ่มเติมจาก command-and-control server ไปยังระบบเป้าหมายผ่านโปรโตคอล HTTPS ในช่วงเวลากลางคืน

*EN:* On 22 February 2569, a logistics services company in Samut Prakan Province reported unauthorized access to its primary server system. From log analysis, it was found that the attacker used Native API to execute malicious code on employee workstations. Subsequently, memory dump analysis revealed traces of a process injected into the legitimate system process svchost.exe, granting the attacker elevated resource access. Analysis of network communications then showed the transfer of additional attack tools from a command-and-control server to the target system via HTTPS protocol during nighttime hours.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1106 Native API | ผู้โจมตีใช้ Native API เพื่อดำเนินการโปรแกรมอันตรายบนเครื่องลูกข่ายของพนักงาน |
| 2 | described | T1055 Process Injection | จากการวิเคราะห์หน่วยความจำ (memory dump) พบร่องรอยของกระบวนการที่ถูกฉีดเข้าไปในโปรแกรม svchost.exe ซึ่งเป็นกระบวนการระบบถูกต้องตามกฎหมาย ทำให้ผู้โจมตีมีสิทธิ์เข้าถึงทรัพยากรระดับสูง |
| 3 | named | T1105 Ingress Tool Transfer | มีการถ่ายโอนเครื่องมือโจมตีเพิ่มเติมจาก command-and-control server ไปยังระบบเป้าหมายผ่านโปรโตคอล HTTPS |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_007  (source: Operation Wocao C0014)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานคร ได้แจ้งความว่าระบบเซิร์ฟเวอร์ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log และหลักฐานดิจิทัลพบว่า ผู้โจมตีได้ดำเนินการเรียกใช้ script ผ่านทาง Windows Management Instrumentation เพื่อให้ได้สิทธิในการเข้าถึงระบบ ต่อมาผู้โจมตีได้ทำการ Multi-Factor Authentication Interception โดยสกัดการส่งรหัส OTP ที่ส่งไปยังโทรศัพท์มือถือของผู้ใช้งาน และนำรหัสดังกล่าวไปใช้เพื่อเข้าสู่บัญชีผู้บริหารระดับสูง จากนั้นผู้โจมตีได้ทำการ Lateral Tool Transfer โดยถ่ายโอนเครื่องมือ Mimikatz ไปยังเซิร์ฟเวอร์อื่นๆ ภายในเครือข่ายเพื่อขยายการควบคุมและสกัดข้อมูลประจำตัวของผู้ใช้งานคนอื่นต่อไป

*EN:* On 22 February 2569, a private financial services company in Bangkok reported unauthorized access to its server systems. Digital forensics and log analysis revealed that the attacker executed scripts via Windows Management Instrumentation to gain system privileges. Subsequently, the attacker performed Multi-Factor Authentication Interception by intercepting OTP codes sent to a user's mobile phone and used those codes to access a senior administrator account. The attacker then conducted Lateral Tool Transfer by moving the Mimikatz tool to other servers within the network to expand control and extract credentials from additional users.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1106 Native API | ผู้โจมตีได้ดำเนินการเรียกใช้ script ผ่านทาง Windows Management Instrumentation เพื่อให้ได้สิทธิในการเข้าถึงระบบ |
| 2 | named | T1111 Multi-Factor Authentication Interception | ผู้โจมตีได้ทำการ Multi-Factor Authentication Interception โดยสกัดการส่งรหัส OTP ที่ส่งไปยังโทรศัพท์มือถือของผู้ใช้งาน |
| 3 | named | T1570 Lateral Tool Transfer | ผู้โจมตีได้ทำการ Lateral Tool Transfer โดยถ่ายโอนเครื่องมือ Mimikatz ไปยังเซิร์ฟเวอร์อื่นๆ ภายในเครือข่าย |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_008  (source: 2025 Poland Wiper Attacks C0063)

**AUTO-FLAGS: step 3: described cue names the technique (Network Service Discovery)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์ Windows Server 2016 ของพวกเขาเกิดความผิดปกติ จากการตรวจสอบ log พบว่าผู้โจมตีได้สร้างงาน Scheduled Task ชื่อ "SystemMaintenance" ภายใต้บัญชีผู้ดูแลระบบเพื่อให้ได้สิทธิ์ในการทำงานแบบต่อเนื่อง ต่อมาจากการวิเคราะห์ Kerberos authentication logs พบว่ามีการสร้างและใช้งาน ticket ที่ปลอมแปลงเพื่อให้ผู้โจมตีสามารถเข้าถึงเซิร์ฟเวอร์อื่น ๆ ในเครือข่ายได้โดยไม่ต้องใช้รหัสผ่านจริง จากนั้นผู้โจมตีได้ทำการ network service discovery โดยการสแกน port และ enumeration บริการที่ทำงานอยู่บนเครื่องอื่น ๆ ในโครงข่าย สุดท้ายจากการตรวจสอบพบว่าผู้โจมตีได้ใช้เครื่องมือ screen capture เพื่อบันทึกหน้าจออพยพข้อมูลการเข้าสู่ระบบของพนักงาน และทำการ inhibit system recovery โดยการลบ shadow copy และปิดการใช้งาน Windows Backup ทำให้ผู้บริหารไม่สามารถกู้คืนข้อมูลได้

*EN:* On 22 February 2569, a logistics services company in Samut Prakan Province reported abnormal activity on their Windows Server 2016 system. Log examination revealed that the attacker created a Scheduled Task named "SystemMaintenance" under an administrator account to maintain persistent privilege. Subsequently, analysis of Kerberos authentication logs showed forged tickets being generated and used, allowing the attacker to access other servers in the network without valid credentials. The attacker then performed network service discovery by scanning ports and enumerating services running on other machines in the network. Finally, examination confirmed the attacker used screen capture tools to record screenshots of employee login credentials, and performed inhibit system recovery by deleting shadow copies and disabling Windows Backup, preventing administrators from restoring data.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1053 Scheduled Task/Job | ผู้โจมตีได้สร้างงาน Scheduled Task ชื่อ "SystemMaintenance" ภายใต้บัญชีผู้ดูแลระบบเพื่อให้ได้สิทธิ์ในการทำงานแบบต่อเนื่อง |
| 2 | described | T1558 Steal or Forge Kerberos Tickets | มีการสร้างและใช้งาน ticket ที่ปลอมแปลงเพื่อให้ผู้โจมตีสามารถเข้าถึงเซิร์ฟเวอร์อื่น ๆ ในเครือข่ายได้โดยไม่ต้องใช้รหัสผ่านจริง |
| 3 | described | T1046 Network Service Discovery | ผู้โจมตีได้ทำการ network service discovery โดยการสแกน port และ enumeration บริการที่ทำงานอยู่บนเครื่องอื่น ๆ ในโครงข่าย |
| 4 | named | T1113 Screen Capture | ผู้โจมตีได้ใช้เครื่องมือ screen capture เพื่อบันทึกหน้าจออพยพข้อมูลการเข้าสู่ระบบของพนักงาน |
| 5 | named | T1490 Inhibit System Recovery | ทำการ inhibit system recovery โดยการลบ shadow copy และปิดการใช้งาน Windows Backup |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_009  (source: Operation Spalax C0005)

**AUTO-FLAGS: step 3: described cue names the technique (Web Service)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทบริหารสินทรัพย์ดิจิทัลแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ดำเนินการรันสคริปต์ PowerShell ผ่านบัญชี service account เพื่อดึงข้อมูลจากเครื่องเซิร์ฟเวอร์ที่มีสิทธิ์ในระบบ ต่อมาผู้โจมตีได้ทำการตรวจจับสภาพแวดล้อมด้วย Virtualization/Sandbox evasion เพื่อหลีกเลี่ยงการตรวจจับจากระบบ endpoint detection ของบริษัท จากนั้นผู้โจมตีได้ติดตั้ง malware ที่สื่อสารกับเซิร์ฟเวอร์ command-and-control ผ่านทาง HTTPS API endpoint ของบริการ web service ยอดนิยมเพื่อเก็บคำสั่งและส่งข้อมูลที่ขโมยได้กลับไป สุดท้ายทีมเทคนิคของบริษัทได้ยกเลิกสิทธิ์การเข้าถึงและแยกเครื่องที่ติดเชื้อออกจากเครือข่าย

*EN:* On 22 February 2569, a digital asset management company in Bangkok reported unauthorized access to its primary server system. Upon examination of system logs, investigators found that the attacker executed PowerShell scripts through a service account to extract data from servers with elevated privileges. Subsequently, the attacker performed virtualization and sandbox evasion techniques to evade the company's endpoint detection systems. The attacker then installed malware that communicated with a command-and-control server via HTTPS API endpoints of a popular web service to receive commands and exfiltrate stolen data. Finally, the company's technical team revoked access privileges and isolated the compromised machine from the network.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1059 Command and Scripting Interpreter | ผู้โจมตีได้ดำเนินการรันสคริปต์ PowerShell ผ่านบัญชี service account เพื่อดึงข้อมูลจากเครื่องเซิร์ฟเวอร์ |
| 2 | named | T1497 Virtualization/Sandbox Evasion | ผู้โจมตีได้ทำการตรวจจับสภาพแวดล้อมด้วย Virtualization/Sandbox evasion เพื่อหลีกเลี่ยงการตรวจจับจากระบบ endpoint detection |
| 3 | described | T1102 Web Service | ผู้โจมตีได้ติดตั้ง malware ที่สื่อสารกับเซิร์ฟเวอร์ command-and-control ผ่านทาง HTTPS API endpoint ของบริการ web service |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_010  (source: C0027 C0027)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการจัดการลอจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการได้แจ้งความต่อสำนักงานว่า ระบบเว็บแอปพลิเคชันสาธารณะของบริษัท (public-facing web application) ถูกเข้าถึงโดยไม่ได้รับอนุญาต โดยผู้โจมตีใช้ Exploit Public-Facing Application เพื่อแทรกซึมเข้าสู่เซิร์ฟเวอร์หลัก จากการตรวจสอบ log พบว่าหลังจากการแทรกซึมครั้งแรก ผู้โจมตีได้ทำการสแกนและระบุตำแหน่งของบริการเครือข่ายต่างๆ ที่ทำงานอยู่ในสภาพแวดล้อมภายใน รวมถึงการค้นหาฐานข้อมูลและระบบเก็บข้อมูลอื่นๆ ที่เชื่อมต่อ ต่อมาผู้โจมตีได้ขยายการเข้าถึงไปยังบริการเก็บข้อมูลบนคลาวด์ (cloud storage) ของบริษัท และทำการดึงข้อมูลจาก Data from Cloud Storage ซึ่งประกอบด้วยเอกสารสัญญา ข้อมูลลูกค้า และรายละเอียดการชำระเงิน จำนวนรวมประมาณ 2.3 GB

*EN:* On 22 February 2569, a logistics management services company in Samut Prakan Province reported to the office that its public-facing web application was accessed without authorization. The attacker used Exploit Public-Facing Application to penetrate the main server. Log examination revealed that following the initial penetration, the attacker scanned and identified various network services operating within the internal environment, including databases and connected data storage systems. Subsequently, the attacker expanded access to the company's cloud storage service and performed Data from Cloud Storage retrieval, which contained contract documents, customer information, and payment details totaling approximately 2.3 GB.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1190 Exploit Public-Facing Application | ผู้โจมตีใช้ Exploit Public-Facing Application เพื่อแทรกซึมเข้าสู่เซิร์ฟเวอร์หลัก |
| 2 | described | T1046 Network Service Discovery | ผู้โจมตีได้ทำการสแกนและระบุตำแหน่งของบริการเครือข่ายต่างๆ ที่ทำงานอยู่ในสภาพแวดล้อมภายใน รวมถึงการค้นหาฐานข้อมูลและระบบเก็บข้อมูลอื่นๆ ที่เชื่อมต่อ |
| 3 | named | T1530 Data from Cloud Storage | ผู้โจมตีได้ขยายการเข้าถึงไปยังบริการเก็บข้อมูลบนคลาวด์ (cloud storage) ของบริษัท และทำการดึงข้อมูลจาก Data from Cloud Storage |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_011  (source: Operation Dream Job C0022)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนแห่งหนึ่งในจังหวัดสมุทรปราการ ประกอบธุรกิจด้านการจัดการโลจิสติกส์ แจ้งความว่าพบกิจกรรมที่น่าสงสัยในระบบเครือข่ายภายในองค์กร จากการตรวจสอบ log และอีเมลเซิร์ฟเวอร์พบว่า บัญชีพนักงานชื่อ สมชาย ได้รับอีเมลที่ปลอมแปลงมาจากที่อยู่ของผู้บริหารระดับกลาง ซึ่งมีเนื้อหาขอให้คลิกลิงก์เพื่ออัปเดตข้อมูลระบบ บัญชีดังกล่าวได้ทำการ Internal spearphishing โดยส่งอีเมลที่คล้ายกันไปยังพนักงานอื่นในแผนกการเงิน ต่อมา จากการตรวจสอบพบว่า มีการเข้าถึงและดึงข้อมูลจาก Local system ของพนักงานที่ถูกโจมตี รวมถึงไฟล์ข้อมูลลูกค้า รายงานการเงิน และข้อมูลประจำตัวบัญชีธนาคาร จากนั้น ผู้โจมตีได้ทำการส่งไฟล์ที่มีขนาดใหญ่หลายไฟล์ผ่านช่องทาง HTTP ไปยังเซิร์ฟเวอร์ภายนอก และมีการดาวน์โหลดเครื่องมือเพิ่มเติมจากโฮสต์ต่างประเทศกลับเข้ามาในระบบเครือข่ายภายใน

*EN:* On 22 February 2569, a private logistics management company in Samut Prakan province reported suspicious activity in the organization's internal network. Upon examination of logs and email servers, it was found that an employee account named Somchai received a spoofed email purporting to be from a mid-level manager requesting a click on a link to update system information. The account then performed internal spearphishing by sending similar emails to other employees in the finance department. Subsequently, examination revealed unauthorized access to and extraction of data from the local systems of affected employees, including customer data files, financial reports, and banking credential information. The attacker then transferred multiple large files via HTTP to external servers and downloaded additional tools from foreign hosts back into the internal network.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1534 Internal Spearphishing | บัญชีดังกล่าวได้ทำการ Internal spearphishing โดยส่งอีเมลที่คล้ายกันไปยังพนักงานอื่นในแผนกการเงิน |
| 2 | named | T1005 Data from Local System | มีการเข้าถึงและดึงข้อมูลจาก Local system ของพนักงานที่ถูกโจมตี รวมถึงไฟล์ข้อมูลลูกค้า รายงานการเงิน และข้อมูลประจำตัวบัญชีธนาคาร |
| 3 | described | T1105 Ingress Tool Transfer | ผู้โจมตีได้ทำการส่งไฟล์ที่มีขนาดใหญ่หลายไฟล์ผ่านช่องทาง HTTP ไปยังเซิร์ฟเวอร์ภายนอก และมีการดาวน์โหลดเครื่องมือเพิ่มเติมจากโฮสต์ต่างประเทศกลับเข้ามาในระบบเครือข่ายภายใน |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_012  (source: 2015 Ukraine Electric Power Attack C0028)

> เมื่อวันที่ 12 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพได้แจ้งความว่าระบบเครือข่ายภายในถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ของ Active Directory พบว่าบัญชีผู้ใช้ชื่อ "sysadmin_backup" ซึ่งเป็นบัญชีเก่าที่ไม่ได้ใช้งานตั้งแต่ปีที่แล้ว ได้ถูกเปิดใช้งานและมีการเข้าสู่ระบบจากแอดเรส IP ต่างประเทศ ต่อมา จากการตรวจสอบ packet capture บนอุปกรณ์ gateway พบหลักฐานของ network sniffing ที่ดักจับการส่งข้อมูลรหัสผ่านในรูปแบบ plaintext ระหว่างสถานีคอมพิวเตอร์ของพนักงาน จากนั้น ผู้บุกรุกได้ทำการ remote system discovery โดยสแกนช่วง IP address ของเครือข่ายภายในเพื่อค้นหาเซิร์ฟเวอร์ที่มีช่องโหว่ สุดท้าย จากการตรวจสอบ forensic image ของเซิร์ฟเวอร์ที่ติดเชื้อพบการถ่ายโอนเครื่องมือ lateral tool transfer ผ่านการคัดลอกไฟล์ executable ไปยังเซิร์ฟเวอร์อื่น ๆ และมีหลักฐานการดาวน์โหลด malware payload จากเซิร์ฟเวอร์ C2 ที่อยู่ต่างประเทศ ซึ่งบ่งชี้ว่าผู้บุกรุกได้สร้างช่องทางสื่อสารสำหรับควบคุมระบบต่อเนื่อง

*EN:* On 12 February 2569, a private information technology company in Bangkok reported unauthorized access to its internal network. Upon examination of Active Directory logs, an old user account named "sysadmin_backup" that had been inactive since the previous year was found to have been reactivated with login attempts from foreign IP addresses. Subsequently, packet capture analysis on the gateway device revealed evidence of network sniffing intercepting plaintext password transmissions between employee workstations. The attacker then conducted remote system discovery by scanning IP address ranges within the internal network to identify vulnerable servers. Finally, forensic examination of infected servers revealed lateral tool transfer through copying executable files to other servers, and evidence of malware payload downloads from a foreign C2 server, indicating the attacker established persistent command and control channels.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | บัญชีผู้ใช้ชื่อ "sysadmin_backup" ซึ่งเป็นบัญชีเก่าที่ไม่ได้ใช้งานตั้งแต่ปีที่แล้ว ได้ถูกเปิดใช้งานและมีการเข้าสู่ระบบจากแอดเรส IP ต่างประเทศ |
| 2 | named | T1040 Network Sniffing | จากการตรวจสอบ packet capture บนอุปกรณ์ gateway พบหลักฐานของ network sniffing ที่ดักจับการส่งข้อมูลรหัสผ่านในรูปแบบ plaintext |
| 3 | named | T1018 Remote System Discovery | ผู้บุกรุกได้ทำการ remote system discovery โดยสแกนช่วง IP address ของเครือข่ายภายในเพื่อค้นหาเซิร์ฟเวอร์ที่มีช่องโหว่ |
| 4 | named | T1570 Lateral Tool Transfer | จากการตรวจสอบ forensic image ของเซิร์ฟเวอร์ที่ติดเชื้อพบการถ่ายโอนเครื่องมือ lateral tool transfer ผ่านการคัดลอกไฟล์ executable ไปยังเซิร์ฟเวอร์อื่น ๆ |
| 5 | described | T1105 Ingress Tool Transfer | มีหลักฐานการดาวน์โหลด malware payload จากเซิร์ฟเวอร์ C2 ที่อยู่ต่างประเทศ ซึ่งบ่งชี้ว่าผู้บุกรุกได้สร้างช่องทางสื่อสารสำหรับควบคุมระบบต่อเนื่อง |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_013  (source: ShadowRay C0045)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการซอฟต์แวร์แห่งหนึ่งในจังหวัดกรุงเทพได้รับแจ้งจากฝ่ายเทคนิคว่าพบกิจกรรมที่ผิดปกติในเซิร์ฟเวอร์ production จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ Exploit Public-Facing Application ผ่านช่องโหว่ในระบบจัดการเนื้อหา CMS ที่ไม่ได้ปรับปรุง เพื่อเข้าถึงเซิร์ฟเวอร์ด้วยสิทธิ์ผู้ใช้ทั่วไป ต่อมาผู้โจมตีได้ทำการ Exploitation for Privilege Escalation โดยใช้ช่องโหว่ kernel ในระบบปฏิบัติการ Linux เพื่อยกระดับสิทธิ์ขึ้นเป็น root จากนั้นผู้โจมตีได้ทำการสำรวจโครงสร้างเครือข่ายภายในโดยการรัน netstat, ifconfig และ arp scan เพื่อค้นหาอุปกรณ์อื่นๆ ในเครือข่ายภายในและแมปการเชื่อมต่อระหว่างโฮสต์ต่างๆ สุดท้ายผู้โจมตีได้ทำการ Ingress Tool Transfer โดยดาวน์โหลด reverse shell script และ privilege escalation toolkit จากเซิร์ฟเวอร์ภายนอกเพื่อใช้ในการสร้าง backdoor และเตรียมการสำหรับการเข้าถึงระบบอื่นๆ ต่อไป

*EN:* On 22 February 2569, a software services company in Bangkok was notified by the technical team of suspicious activity on the production server. Log examination revealed that the attacker used Exploit Public-Facing Application through an unpatched vulnerability in the CMS content management system to gain initial access with standard user privileges. Subsequently, the attacker performed Exploitation for Privilege Escalation by leveraging a kernel vulnerability in the Linux operating system to escalate privileges to root. The attacker then conducted reconnaissance of the internal network structure by executing netstat, ifconfig, and arp scan commands to discover other devices on the internal network and map connections between hosts. Finally, the attacker performed Ingress Tool Transfer by downloading a reverse shell script and privilege escalation toolkit from an external server to establish a backdoor and prepare for access to other systems.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ใช้ Exploit Public-Facing Application ผ่านช่องโหว่ในระบบจัดการเนื้อหา CMS |
| 2 | named | T1068 Exploitation for Privilege Escalation | ผู้โจมตีได้ทำการ Exploitation for Privilege Escalation โดยใช้ช่องโหว่ kernel ในระบบปฏิบัติการ Linux |
| 3 | described | T1016 System Network Configuration Discovery | ผู้โจมตีได้ทำการสำรวจโครงสร้างเครือข่ายภายในโดยการรัน netstat, ifconfig และ arp scan เพื่อค้นหาอุปกรณ์อื่นๆ ในเครือข่ายภายในและแมปการเชื่อมต่อระหว่างโฮสต์ต่างๆ |
| 4 | named | T1105 Ingress Tool Transfer | ผู้โจมตีได้ทำการ Ingress Tool Transfer โดยดาวน์โหลด reverse shell script และ privilege escalation toolkit จากเซิร์ฟเวอร์ภายนอก |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_014  (source: Operation CuckooBees C0012)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการบริหารจัดการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่า ระบบ web portal สำหรับลูกค้าได้รับความเสียหาย จากการตรวจสอบ log server พบว่า ผู้โจมตีได้ส่ง HTTP request ที่มีข้อมูล payload ผิดปกติไปยังฟอร์มกรอกข้อมูลการจองสินค้า และสามารถบุกเข้าระบบได้สำเร็จ ต่อมาจากการวิเคราะห์ evidence ดิจิทัล พบว่าผู้โจมตีได้ติดตั้ง SSH key และ reverse shell script ไว้ในไดเรกทอรี่ /var/www/.ssh เพื่อใช้เป็น external remote services สำหรับการเข้าถึงระบบอย่างต่อเนื่อง จากนั้นผู้โจมตีได้ทำการ remote system discovery โดยใช้คำสั่ง nmap และ netstat เพื่อสำรวจอุปกรณ์เครือข่ายอื่นๆ ที่เชื่อมต่ออยู่ในเซกเมนต์เดียวกัน สุดท้าย จากการตรวจสอบ file access log และ bash history พบว่าผู้โจมตีได้ดึงข้อมูลจากฐานข้อมูลท้องถิ่นไปยัง CSV file และ tar archive ซึ่งมีข้อมูลลูกค้าจำนวน 47,000 รายการและเอกสารสัญญาจำนวน 1,200 ฉบับ

*EN:* On 22 February 2569, a private logistics management company in Samut Prakan province reported damage to its customer web portal system. Log server examination revealed that the attacker sent malformed HTTP requests with unusual payload data to the booking form and successfully breached the system. Subsequent digital evidence analysis found that the attacker had installed SSH keys and reverse shell scripts in the /var/www/.ssh directory to serve as external remote services for persistent system access. The attacker then performed remote system discovery using nmap and netstat commands to enumerate other network devices connected to the same segment. Finally, examination of file access logs and bash history showed the attacker extracted data from the local database into CSV files and tar archives, containing customer information for 47,000 records and 1,200 contract documents.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ส่ง HTTP request ที่มีข้อมูล payload ผิดปกติไปยังฟอร์มกรอกข้อมูลการจองสินค้า และสามารถบุกเข้าระบบได้สำเร็จ |
| 2 | named | T1133 External Remote Services | ผู้โจมตีได้ติดตั้ง SSH key และ reverse shell script ไว้ในไดเรกทอรี่ /var/www/.ssh เพื่อใช้เป็น external remote services สำหรับการเข้าถึงระบบอย่างต่อเนื่อง |
| 3 | named | T1018 Remote System Discovery | ผู้โจมตีได้ทำการ remote system discovery โดยใช้คำสั่ง nmap และ netstat เพื่อสำรวจอุปกรณ์เครือข่ายอื่นๆ ที่เชื่อมต่ออยู่ในเซกเมนต์เดียวกัน |
| 4 | described | T1005 Data from Local System | ผู้โจมตีได้ดึงข้อมูลจากฐานข้อมูลท้องถิ่นไปยัง CSV file และ tar archive ซึ่งมีข้อมูลลูกค้าจำนวน 47,000 รายการและเอกสารสัญญาจำนวน 1,200 ฉบับ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_015  (source: HomeLand Justice C0038)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพมหานครแจ้งความว่าระบบเซิร์ฟเวอร์ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ระบบพบว่าบัญชีผู้ใช้ชื่อ "admin_backup" ซึ่งเป็นบัญชีของเจ้าหน้าที่ฝ่ายบำรุงรักษาที่เกษียณอายุไปแล้ว ถูกใช้เข้าสู่ระบบจากที่อยู่ IP ต่างประเทศและมีการเปลี่ยนแปลงสิทธิ์การเข้าถึงไปยังกลุ่มผู้ใช้อื่นๆ ต่อมา จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าผู้โจมตีได้ทำการ download เครื่องมือ malware ชื่อ "remote_agent.exe" ไปยังเครื่องคอมพิวเตอร์ในเครือข่ายภายในผ่านช่องทาง command and control ที่ติดต่อกับเซิร์ฟเวอร์ของผู้โจมตี จากนั้น ผู้โจมตีได้ใช้ Exfiltration over C2 channel เพื่อส่งข้อมูลลับของบริษัทรวมถึงรายชื่อลูกค้า ข้อมูลสัญญา และรายละเอียดโครงการพิเศษกลับไปยังเซิร์ฟเวอร์ remote ของผู้โจมตี ปริมาณข้อมูลที่ถูกสกัดออกไปทั้งสิ้นประมาณ 2.3 GB สุดท้าย ทีมรักษาความปลอดภัยได้ตัดการเชื่อมต่อเครือข่ายและทำการสืบสวนต่อเนื่อง

*EN:* On 22 February 2569, a private sector information technology company in Bangkok reported unauthorized access to its server systems. Upon examination of system logs, the account "admin_backup" belonging to a retired maintenance staff member was found to have logged in from a foreign IP address with subsequent privilege changes made to other user groups. Subsequently, digital forensic examination revealed that the attacker downloaded malware named "remote_agent.exe" to computers within the internal network via a command and control channel communicating with the attacker's server. The attacker then used exfiltration over C2 channel to transmit company confidential data including client lists, contract information, and special project details back to the attacker's remote server. The total volume of exfiltrated data was approximately 2.3 GB. Finally, the security team disconnected the network and initiated further investigation.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | บัญชีผู้ใช้ชื่อ "admin_backup" ซึ่งเป็นบัญชีของเจ้าหน้าที่ฝ่ายบำรุงรักษาที่เกษียณอายุไปแล้ว ถูกใช้เข้าสู่ระบบจากที่อยู่ IP ต่างประเทศและมีการเปลี่ยนแปลงสิทธิ์การเข้าถึงไปยังกลุ่มผู้ใช้อื่นๆ |
| 2 | described | T1105 Ingress Tool Transfer | ผู้โจมตีได้ทำการ download เครื่องมือ malware ชื่อ "remote_agent.exe" ไปยังเครื่องคอมพิวเตอร์ในเครือข่ายภายในผ่านช่องทาง command and control ที่ติดต่อกับเซิร์ฟเวอร์ของผู้โจมตี |
| 3 | named | T1041 Exfiltration Over C2 Channel | ผู้โจมตีได้ใช้ Exfiltration over C2 channel เพื่อส่งข้อมูลลับของบริษัทรวมถึงรายชื่อลูกค้า ข้อมูลสัญญา และรายละเอียดโครงการพิเศษกลับไปยังเซิร์ฟเวอร์ remote ของผู้โจมตี |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_016  (source: Night Dragon C0002)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานครแจ้งความว่าระบบเซิร์ฟเวอร์สำนักงานใหญ่ถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ระบบพบว่าผู้โจมตีได้เชื่อมต่อเข้าสู่ระบบผ่านทางบริการ VPN ระยะไกลที่เปิดให้บริการสาธารณะ โดยใช้ข้อมูลประจำตัวของพนักงานที่ขโมยมา ต่อมาจากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าผู้โจมตีได้ทำการ Modify Registry บนเครื่องเซิร์ฟเวอร์เพื่อสร้างจุดเข้าถึงแบบถาวร โดยเพิ่มค่า Run key ในระบบเพื่อให้โปรแกรมที่ฝังตัวสามารถทำงานอัตโนมัติเมื่อบูตระบบ จากนั้นการวิเคราะห์ traffic เครือข่ายแสดงว่าเครื่องที่ติดเชื้อได้ส่งคำขอ DNS ไปยังชื่อโดเมนที่เปลี่ยนแปลงอย่างสม่ำเสมอ เพื่อหลีกเลี่ยงการตรวจสอบของระบบป้องกัน ซึ่งบ่งชี้ถึงการใช้กลไก Dynamic Resolution ในการสื่อสารกับเซิร์ฟเวอร์ควบคุม

*EN:* On 22 February 2569, a private financial services company in Bangkok reported unauthorized access to its headquarters server system. Log examination revealed that the attacker connected to the system via a publicly exposed remote VPN service using stolen employee credentials. Subsequent digital evidence analysis showed that the attacker performed Registry modifications on the server machine to establish persistent access by adding Run key entries to enable embedded malware to execute automatically at system startup. Network traffic analysis then demonstrated that the compromised machine sent DNS queries to continuously changing domain names to evade security monitoring systems, indicating use of Dynamic Resolution for command-and-control communications.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1133 External Remote Services | ผู้โจมตีได้เชื่อมต่อเข้าสู่ระบบผ่านทางบริการ VPN ระยะไกลที่เปิดให้บริการสาธารณะ |
| 2 | named | T1112 Modify Registry | ผู้โจมตีได้ทำการ Modify Registry บนเครื่องเซิร์ฟเวอร์เพื่อสร้างจุดเข้าถึงแบบถาวร |
| 3 | described | T1568 Dynamic Resolution | เครื่องที่ติดเชื้อได้ส่งคำขอ DNS ไปยังชื่อโดเมนที่เปลี่ยนแปลงอย่างสม่ำเสมอ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_017  (source: RedPenguin C0056)

**AUTO-FLAGS: step 2: cue not found verbatim in narrative**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีใช้ข้อมูลประจำตัวของพนักงานส่วนหนึ่งที่ได้มาจากแหล่งอื่น เพื่อเข้าสู่ระบบ VPN ของบริษัท ต่อมาผู้โจมตีดำเนินการ Exploitation for Client Execution ผ่านเอกสาร Microsoft Office ที่ส่งไปยังเครื่องของพนักงาน ซึ่งทำให้โค้ดอันตรายทำงานบนเครื่องเป้าหมาย จากนั้นจากการตรวจสอบพยานหลักฐานดิจิทัลพบร่องรอยของ Network Sniffing เนื่องจากมีการติดตั้งเครื่องมือดักจับแพ็กเก็ตข้อมูลบนเซ็กเมนต์เครือข่ายภายใน สุดท้ายพบว่าผู้โจมตีได้ทำการสอบสวนกระบวนการที่ทำงานบนเซิร์ฟเวอร์ และสร้างการเชื่อมต่อกลับไปยังเซิร์ฟเวอร์ควบคุมภายนอกผ่านพอร์ต 8834 ซึ่งไม่ใช่พอร์ตมาตรฐานสำหรับการสื่อสารประเภทนั้น

*EN:* On 22 February 2569, a logistics services company in Samut Prakan province reported unauthorized access to its server system. From log examination, it was found that the attacker used employee credentials obtained from external sources to access the company's VPN. Subsequently, the attacker conducted Exploitation for Client Execution via a malicious Microsoft Office document sent to an employee machine, causing malicious code to execute on the target system. Later, digital forensic examination revealed traces of Network Sniffing, as packet capture tools were discovered installed on an internal network segment. Finally, evidence showed the attacker enumerated running processes on the server and established a reverse connection to an external command server via port 8834, which is non-standard for that communication type.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | ผู้โจมตีใช้ข้อมูลประจำตัวของพนักงานส่วนหนึ่งที่ได้มาจากแหล่งอื่น เพื่อเข้าสู่ระบบ VPN ของบริษัท |
| 2 | named | T1203 Exploitation for Client Execution | ผู้โจมตีดำเนินการ Exploitation for Client Execution ผ่านเอกสาร Microsoft Office ที่ส่งไปยังเครื่องของพนักงาย |
| 3 | named | T1040 Network Sniffing | พบร่องรอยของ Network Sniffing เนื่องจากมีการติดตั้งเครื่องมือดักจับแพ็กเก็ตข้อมูลบนเซ็กเมนต์เครือข่ายภายใน |
| 4 | described | T1057 Process Discovery | ผู้โจมตีได้ทำการสอบสวนกระบวนการที่ทำงานบนเซิร์ฟเวอร์ |
| 5 | described | T1571 Non-Standard Port | สร้างการเชื่อมต่อกลับไปยังเซิร์ฟเวอร์ควบคุมภายนอกผ่านพอร์ต 8834 ซึ่งไม่ใช่พอร์ตมาตรฐานสำหรับการสื่อสารประเภทนั้น |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_018  (source: C0018 C0018)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์หลักของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log และหลักฐานดิจิทัลพบว่า ผู้โจมตีได้ใช้ Software Deployment Tools ชื่อ Altiris Deployment Server ซึ่งเป็นเครื่องมือที่ติดตั้งแล้วในสภาพแวดล้อมการทำงาน เพื่อดำเนินการคำสั่งที่เป็นอันตรายบนเครื่องลูกข่าย ต่อมาจากการวิเคราะห์ traffic ภายในเครือข่ายพบการเชื่อมต่อผิดปกติจากเครื่องที่ติดเชื้อไปยังเครื่องอื่น ๆ ในเซกเมนต์เดียวกัน โดยมีการถ่ายโอนไฟล์เครื่องมือโจมตีระหว่างระบบต่าง ๆ ผ่านช่องทางการสื่อสารภายในเครือข่าย จากนั้นผู้วิเคราะห์พบว่า ผู้โจมตีได้ดึงเครื่องมือเพิ่มเติมจากเซิร์ฟเวอร์ C2 ภายนอก โดยใช้วิธีการดาวน์โหลดและติดตั้งบน endpoint ที่ถูกประนีประนวมแล้ว สุดท้ายเมื่อวันที่ 25 กุมภาพันธ์ 2569 ไฟล์ข้อมูลทั้งหมดในระบบหลักถูกเข้ารหัสด้วยอัลกอริทึม RSA-2048 และแสดงข้อความค้นคว้นค่าไถ่ โดยประมาณการว่าข้อมูลที่ได้รับผลกระทบมีจำนวนประมาณ 2.3 ล้านไฟล์ และผู้เสียหายไม่สามารถเข้าถึงข้อมูลการดำเนินงานของบริษัทต่อไปได้

*EN:* On 22 February 2569, a private logistics company in Samut Prakan Province reported unauthorized access to its primary server system. Upon examination of logs and digital evidence, investigators found that the attacker had used Software Deployment Tools named Altiris Deployment Server, a tool already installed in the operational environment, to execute malicious commands on client machines. Subsequently, analysis of internal network traffic revealed abnormal connections from an infected machine to other machines in the same segment, with transfer of attack tools between systems via internal network communication channels. The analyst then discovered that the attacker had retrieved additional tools from an external C2 server by downloading and installing them on already-compromised endpoints. Finally, on 25 February 2569, all data files in the primary system were encrypted using RSA-2048 algorithm and displayed a ransom note. Approximately 2.3 million files were estimated to be affected, and the victim organization could no longer access its operational data.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1072 Software Deployment Tools | ผู้โจมตีได้ใช้ Software Deployment Tools ชื่อ Altiris Deployment Server ซึ่งเป็นเครื่องมือที่ติดตั้งแล้วในสภาพแวดล้อมการทำงาน เพื่อดำเนินการคำสั่งที่เป็นอันตรายบนเครื่องลูกข่าย |
| 2 | described | T1570 Lateral Tool Transfer | จากการวิเคราะห์ traffic ภายในเครือข่ายพบการเชื่อมต่อผิดปกติจากเครื่องที่ติดเชื้อไปยังเครื่องอื่น ๆ ในเซกเมนต์เดียวกัน โดยมีการถ่ายโอนไฟล์เครื่องมือโจมตีระหว่างระบบต่าง ๆ ผ่านช่องทางการสื่อสารภายในเครือข่าย |
| 3 | described | T1105 Ingress Tool Transfer | ผู้โจมตีได้ดึงเครื่องมือเพิ่มเติมจากเซิร์ฟเวอร์ C2 ภายนอก โดยใช้วิธีการดาวน์โหลดและติดตั้งบน endpoint ที่ถูกประนีประนวมแล้ว |
| 4 | named | T1486 Data Encrypted for Impact | ไฟล์ข้อมูลทั้งหมดในระบบหลักถูกเข้ารหัสด้วยอัลกอริทึม RSA-2048 และแสดงข้อความค้นคว้นค่าไถ่ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_019  (source: CostaRicto C0004)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบคอมพิวเตอร์เซิร์ฟเวอร์ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ External Remote Services ผ่านพอร์ต SSH ที่เปิดออกสู่อินเทอร์เน็ตเพื่อเข้าสู่ระบบ ต่อมาผู้โจมตีได้ทำการสแกนและค้นหาเซอร์วิสเครือข่ายอื่น ๆ ที่เชื่อมต่ออยู่ในเครือข่ายภายในโดยใช้เครื่องมือ nmap และ netstat เพื่อระบุตำแหน่งของเซิร์ฟเวอร์ฐานข้อมูล จากนั้นผู้โจมตีได้ทำการ Data from Local System โดยการดึงไฟล์ประวัติการเข้าถึง bash_history และไฟล์ config ของแอปพลิเคชัน สุดท้าย ผู้โจมตีได้ทำการ Ingress Tool Transfer โดยดาวน์โหลดสคริป์ต Perl และเครื่องมือ privilege escalation จากเซิร์ฟเวอร์ภายนอกมายังเครื่องที่ถูกยึดไว้เพื่อเตรียมการสำหรับการโจมตีครั้งต่อไป

*EN:* On 22 February 2569, a logistics service company in Samut Prakan Province reported unauthorized access to its server computer system. Log examination revealed that the attacker used External Remote Services via SSH port exposed to the internet to gain system access. Subsequently, the attacker scanned and discovered other network services connected within the internal network using nmap and netstat tools to identify the database server location. The attacker then performed Data from Local System by extracting bash_history files and application configuration files. Finally, the attacker conducted Ingress Tool Transfer by downloading Perl scripts and privilege escalation tools from an external server to the compromised machine in preparation for subsequent attacks.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1133 External Remote Services | ผู้โจมตีได้ใช้ External Remote Services ผ่านพอร์ต SSH ที่เปิดออกสู่อินเทอร์เน็ต |
| 2 | described | T1046 Network Service Discovery | ผู้โจมตีได้ทำการสแกนและค้นหาเซอร์วิสเครือข่ายอื่น ๆ ที่เชื่อมต่ออยู่ในเครือข่ายภายในโดยใช้เครื่องมือ nmap และ netstat |
| 3 | named | T1005 Data from Local System | ผู้โจมตีได้ทำการ Data from Local System โดยการดึงไฟล์ประวัติการเข้าถึง bash_history และไฟล์ config ของแอปพลิเคชัน |
| 4 | named | T1105 Ingress Tool Transfer | ผู้โจมตีได้ทำการ Ingress Tool Transfer โดยดาวน์โหลดสคริป์ต Perl และเครื่องมือ privilege escalation จากเซิร์ฟเวอร์ภายนอก |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_020  (source: ArcaneDoor C0046)

**AUTO-FLAGS: step 5: cue not found verbatim in narrative**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนแห่งหนึ่งในจังหวัดสมุทรปราการที่ประกอบธุรกิจด้านการจัดการสินค้าคงคลังแจ้งความว่า ระบบ VPN และ RDP ของสำนักงานใหญ่ถูกเข้าถึงจากที่อยู่ IP ต่างประเทศโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ฉีด malicious code เข้าไปในกระบวนการ svchost.exe ผ่านเทคนิค Process Injection เพื่อให้ได้สิทธิการเข้าถึงระดับสูงขึ้น ต่อมา ระบบตรวจสอบพบการสื่อสารที่ผิดปกติระหว่างเซิร์ฟเวอร์ของบริษัทและอุปกรณ์ที่อยู่ในเครือข่ายภายนอก ซึ่งบ่งชี้ว่าการสื่อสารถูกสกัดกั้นและแก้ไขข้อมูล credentials ระหว่างการส่งผ่าน จากนั้น ผู้โจมตีได้ทำการสอบถามระบบเพื่อเก็บข้อมูลเกี่ยวกับสถาปัตยกรรมเครือข่าย ชื่อเซิร์ฟเวอร์ และรายชื่อบัญชีผู้ใช้ที่อยู่ในระบบ สุดท้าย ข้อมูลที่สำคัญจำนวน 450 GB รวมถึงรายชื่อลูกค้า ข้อมูลการทำธุรกรรม และแบบแผนการจัดการสินค้า ถูกส่งออกไปยังเซิร์ฟเวอร์ command and control ผ่านช่องทางการสื่อสารที่ผู้โจมตีสร้างขึ้นในระหว่างการรุกรานครั้งนี้

*EN:* On 22 February 2569, a private company in Samut Prakan province engaged in inventory management services reported that its VPN and RDP systems at the main office were accessed from foreign IP addresses without authorization. Log examination revealed that the attacker injected malicious code into the svchost.exe process using Process Injection technique to escalate privileges. Subsequently, the system detected abnormal communications between the company's servers and devices outside the network, indicating that communications were intercepted and credential data modified during transmission. The attacker then queried the system to gather information about network architecture, server names, and user account lists residing in the system. Finally, approximately 450 GB of critical data including customer lists, transaction records, and inventory management schemes were exfiltrated to a command and control server through a communication channel established during the intrusion.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1133 External Remote Services | ระบบ VPN และ RDP ของสำนักงานใหญ่ถูกเข้าถึงจากที่อยู่ IP ต่างประเทศโดยไม่ได้รับอนุญาต |
| 2 | named | T1055 Process Injection | ผู้โจมตีได้ฉีด malicious code เข้าไปในกระบวนการ svchost.exe ผ่านเทคนิค Process Injection |
| 3 | described | T1557 Adversary-in-the-Middle | การสื่อสารถูกสกัดกั้นและแก้ไขข้อมูล credentials ระหว่างการส่งผ่าน |
| 4 | described | T1082 System Information Discovery | ผู้โจมตีได้ทำการสอบถามระบบเพื่อเก็บข้อมูลเกี่ยวกับสถาปัตยกรรมเครือข่าย ชื่อเซิร์ฟเวอร์ และรายชื่อบัญชีผู้ใช้ที่อยู่ในระบบ |
| 5 | described | T1041 Exfiltration Over C2 Channel | ข้อมูลที่สำคัญจำนวน 450 GB ถูกส่งออกไปยังเซิร์ฟเวอร์ command and control ผ่านช่องทางการสื่อสารที่ผู้โจมตีสร้างขึ้น |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_021  (source: Operation AkaiRyū C0060)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพมหานครแจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log และหลักฐานดิจิทัลพบว่าผู้โจมตีได้ทำการเรียกใช้สคริปต์ผ่านทางช่องทาง WMI เพื่อดำเนินการคำสั่งบนระบบเป้าหมาย ต่อมาผู้โจมตีทำการ System Information Discovery เพื่อเก็บรวบรวมข้อมูลเกี่ยวกับสถาปัตยกรรมระบบและการกำหนดค่าของเครื่องที่ถูกบุกรุก จากนั้นผู้โจมตีได้ติดตั้ง Remote Access Tools บนเซิร์ฟเวอร์เพื่อรักษาความสามารถในการเข้าถึงระบบอย่างต่อเนื่อง ทำให้ผู้โจมตีสามารถควบคุมระบบได้อย่างเต็มที่และติดตามกิจกรรมของผู้ใช้ในเวลาจริง

*EN:* On 22 February 2569, an information technology company in Bangkok reported unauthorized access to its primary server system. Digital forensic examination of logs revealed that the attacker executed scripts via WMI channel to run commands on the target system. Subsequently, the attacker conducted System Information Discovery to gather data about the system architecture and configuration of the compromised machine. The attacker then installed Remote Access Tools on the server to maintain persistent access to the system, allowing full control and real-time monitoring of user activities.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1047 Windows Management Instrumentation | ผู้โจมตีได้ทำการเรียกใช้สคริปต์ผ่านทางช่องทาง WMI เพื่อดำเนินการคำสั่งบนระบบเป้าหมาย |
| 2 | named | T1082 System Information Discovery | ผู้โจมตีทำการ System Information Discovery เพื่อเก็บรวบรวมข้อมูลเกี่ยวกับสถาปัตยกรรมระบบและการกำหนดค่าของเครื่องที่ถูกบุกรุก |
| 3 | named | T1219 Remote Access Tools | ผู้โจมตีได้ติดตั้ง Remote Access Tools บนเซิร์ฟเวอร์เพื่อรักษาความสามารถในการเข้าถึงระบบอย่างต่อเนื่อง |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_022  (source: Operation MidnightEclipse C0048)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานคร แจ้งความว่าระบบเซิร์ฟเวอร์หลักของฝ่ายบัญชีได้ถูกเข้าถึงข้อมูลโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ของระบบ Active Directory พบว่า บัญชีผู้ใช้งานของพนักงานระดับกลางชื่อ สมชาย ด. ถูกใช้งานเพื่อเข้าสู่ระบบในช่วงเวลา 02:15 - 04:30 น. ของวันที่ 20 กุมภาพันธ์ ซึ่งนอกเหนือเวลาการทำงานปกติ ต่อมาจากการตรวจสอบไฟล์ log ของเซิร์ฟเวอร์ประเภท database server พบหลักฐานการสอบค้นและการอ่านข้อมูลแฟ้มเอกสารที่เกี่ยวกับรายชื่อลูกค้า บัญชีธนาคาร และข้อมูลการโอนเงินจำนวนมาก ซึ่งเป็นข้อมูลที่เก็บรักษาอยู่ในหน่วยความจำของระบบภายใน จากนั้นจากการตรวจสอบ network traffic ในช่วงเวลาเดียวกัน พบการส่งส่วนประกอบโปรแกรมขนาดใหญ่ 87 เมกะไบต์จากเซิร์ฟเวอร์ภายในไปยังที่อยู่ IP ภายนอกที่ตั้งอยู่ในประเทศเวียดนาม พร้อมกับเครื่องมือจำพวก packet sniffer และ credential extractor ที่ถูกสร้างขึ้นในโฟลเดอร์ temp ของระบบปฏิบัติการ

*EN:* On 22 February 2569, a private financial services company in Bangkok reported unauthorized access to its main accounting server system. From examination of Active Directory logs, the user account of a mid-level employee named Somchai D. was observed being used to log in during 02:15 - 04:30 hours on 20 February, outside normal business hours. Subsequently, review of the database server logs revealed evidence of queries and reads of files containing customer lists, bank account numbers, and fund transfer data stored in the system's local memory. Thereafter, examination of network traffic during the same period showed transmission of a large 87-megabyte software component from the internal server to an external IP address located in Vietnam, along with packet sniffer and credential extractor tools that were created in the system's temp folder.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | บัญชีผู้ใช้งานของพนักงานระดับกลางชื่อ สมชาย ด. ถูกใช้งานเพื่อเข้าสู่ระบบในช่วงเวลา 02:15 - 04:30 น. ของวันที่ 20 กุมภาพันธ์ |
| 2 | described | T1005 Data from Local System | จากการตรวจสอบไฟล์ log ของเซิร์ฟเวอร์ประเภท database server พบหลักฐานการสอบค้นและการอ่านข้อมูลแฟ้มเอกสารที่เกี่ยวกับรายชื่อลูกค้า บัญชีธนาคาร และข้อมูลการโอนเงินจำนวนมาก ซึ่งเป็นข้อมูลที่เก็บรักษาอยู่ในหน่วยความจำของระบบภายใน |
| 3 | described | T1105 Ingress Tool Transfer | จากการตรวจสอบ network traffic ในช่วงเวลาเดียวกัน พบการส่งส่วนประกอบโปรแกรมขนาดใหญ่ 87 เมกะไบต์จากเซิร์ฟเวอร์ภายในไปยังที่อยู่ IP ภายนอกที่ตั้งอยู่ในประเทศเวียดนาม พร้อมกับเครื่องมือจำพวก packet sniffer และ credential extractor ที่ถูกสร้างขึ้นในโฟลเดอร์ temp ของระบบปฏิบัติการ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_023  (source: 2022 Ukraine Electric Power Attack C0034)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ระบบพบว่าผู้โจมตีทำการคัดลอกและโอนย้ายเครื่องมือ penetration testing ไปยังเซิร์ฟเวอร์ข้างเคียงหลายเครื่อง เพื่อแพร่กระจายการเข้าถึงในเครือข่ายภายใน ต่อมาผู้โจมตีได้ใช้ Protocol Tunneling เพื่อสร้างช่องทางการสื่อสารที่ซ่อนอยู่ภายในโปรโตคอล DNS และ HTTP ปกติ เพื่อหลีกเลี่ยงการตรวจจับโดยระบบ firewall สุดท้ายจากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าผู้โจมตีได้ดำเนินการลบและเขียนทับข้อมูลในฐานข้อมูลสำคัญและไฟล์ log ระบบอย่างเป็นระบบ ทำให้ข้อมูลธุรกิจหลายปีสูญหาย

*EN:* On 22 February 2569, a logistics service company in Samut Prakan Province reported unauthorized access to its primary server. Log analysis revealed that the attacker copied and transferred penetration testing tools to multiple adjacent servers to propagate access throughout the internal network. Subsequently, the attacker employed Protocol Tunneling to establish hidden communication channels within normal DNS and HTTP protocols to evade firewall detection. Finally, digital forensic examination showed that the attacker systematically deleted and overwrote critical database records and system log files, resulting in the loss of several years of business data.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1570 Lateral Tool Transfer | ผู้โจมตีทำการคัดลอกและโอนย้ายเครื่องมือ penetration testing ไปยังเซิร์ฟเวอร์ข้างเคียงหลายเครื่อง เพื่อแพร่กระจายการเข้าถึงในเครือข่ายภายใน |
| 2 | named | T1572 Protocol Tunneling | ผู้โจมตีได้ใช้ Protocol Tunneling เพื่อสร้างช่องทางการสื่อสารที่ซ่อนอยู่ภายในโปรโตคอล DNS และ HTTP ปกติ |
| 3 | described | T1485 Data Destruction | ผู้โจมตีได้ดำเนินการลบและเขียนทับข้อมูลในฐานข้อมูลสำคัญและไฟล์ log ระบบอย่างเป็นระบบ ทำให้ข้อมูลธุรกิจหลายปีสูญหาย |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_024  (source: Cutting Edge C0029)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการสินค้าคงคลังแห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์หลักของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ดำเนินการรันสคริปต์ PowerShell ผ่านทาง Windows Command Prompt เพื่อเตรียมสภาพแวดล้อมสำหรับการโจมตีต่อเนื่อง ต่อมาผู้โจมตีได้ติดตั้ง Traffic Signaling mechanism เพื่อรักษาการเข้าถึงระบบและสร้างช่องทางสื่อสารแบบซ่อนตัวกับเซิร์ฟเวอร์ control ของตนเอง จากนั้นผู้โจมตีได้ทำการเรียกคำสั่ง systeminfo และ ipconfig เพื่อรวบรวมข้อมูลเกี่ยวกับสถาปัตยกรรมระบบและการตั้งค่าเครือข่ายของเซิร์ฟเวอร์เป้าหมาย สุดท้ายจากการสืบสวนพบว่าผู้โจมตีได้ดาวน์โหลด tools สำหรับการโจมตีเพิ่มเติมจากเซิร์ฟเวอร์ภายนอกมายังระบบเป้าหมายผ่านทาง HTTP request และ PowerShell download cmdlets

*EN:* On 22 February 2569, a private company specializing in inventory management in Samut Prakan Province reported unauthorized access to its primary server system. From log examination, investigators found that the attacker executed PowerShell scripts through Windows Command Prompt to prepare the environment for sustained attack. Subsequently, the attacker deployed Traffic Signaling mechanism to maintain system access and establish hidden communication channels with their control server. The attacker then issued systeminfo and ipconfig commands to gather information about the target server's system architecture and network configuration. Finally, investigation revealed that the attacker downloaded additional attack tools from external servers to the target system via HTTP requests and PowerShell download cmdlets.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1059 Command and Scripting Interpreter | ผู้โจมตีได้ดำเนินการรันสคริปต์ PowerShell ผ่านทาง Windows Command Prompt |
| 2 | named | T1205 Traffic Signaling | ผู้โจมตีได้ติดตั้ง Traffic Signaling mechanism เพื่อรักษาการเข้าถึงระบบและสร้างช่องทางสื่อสารแบบซ่อนตัว |
| 3 | described | T1082 System Information Discovery | ผู้โจมตีได้ทำการเรียกคำสั่ง systeminfo และ ipconfig เพื่อรวบรวมข้อมูลเกี่ยวกับสถาปัตยกรรมระบบและการตั้งค่าเครือข่าย |
| 4 | described | T1105 Ingress Tool Transfer | ผู้โจมตีได้ดาวน์โหลด tools สำหรับการโจมตีเพิ่มเติมจากเซิร์ฟเวอร์ภายนอกมายังระบบเป้าหมายผ่านทาง HTTP request และ PowerShell download cmdlets |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_025  (source: 3CX Supply Chain Attack C0057)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์หลักของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ระบบพบว่าผู้โจมตีได้ใช้ชื่อผู้ใช้และรหัสผ่านของพนักงานแผนกขายที่ได้มาจากการรั่วไหลข้อมูลจากแหล่งภายนอก เข้าสู่ระบบ VPN ของบริษัท ต่อมาผู้โจมตีทำการ Exploitation for Client Execution ผ่านการส่ง malicious attachment ในอีเมลภายใน ซึ่งเมื่อพนักงานเปิดไฟล์ดังกล่าว ระบบ workstation ของพนักงานถูกติดตั้ง backdoor ที่ทำให้ผู้โจมตีสามารถควบคุมได้จากระยะไกล จากนั้นจากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าผู้โจมตีได้เรียกดูข้อมูลการตั้งค่า browser เช่น stored credentials ประวัติการเยี่ยมชม และ cookies ที่เก็บไว้ในเครื่องผู้ใช้ เพื่อหาข้อมูลเข้าสู่ระบบอื่นๆ ของบริษัท

*EN:* On 22 February 2569, a logistics service company in Samut Prakan Province reported unauthorized access to the company's primary server system. Log examination revealed that the attacker used the username and password of a sales department employee obtained from an external data leak to access the company's VPN system. Subsequently, the attacker performed Exploitation for Client Execution by sending a malicious attachment via internal email, which when opened by an employee installed a backdoor on the workstation allowing remote control. Digital forensic examination then revealed that the attacker accessed browser configuration data such as stored credentials, browsing history, and cookies stored on the user's machine to obtain login information for other company systems.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | ผู้โจมตีได้ใช้ชื่อผู้ใช้และรหัสผ่านของพนักงานแผนกขายที่ได้มาจากการรั่วไหลข้อมูลจากแหล่งภายนอก เข้าสู่ระบบ VPN ของบริษัท |
| 2 | named | T1203 Exploitation for Client Execution | ผู้โจมตีทำการ Exploitation for Client Execution ผ่านการส่ง malicious attachment ในอีเมลภายใน ซึ่งเมื่อพนักงานเปิดไฟล์ดังกล่าว ระบบ workstation ของพนักงานถูกติดตั้ง backdoor |
| 3 | described | T1217 Browser Information Discovery | ผู้โจมตีได้เรียกดูข้อมูลการตั้งค่า browser เช่น stored credentials ประวัติการเยี่ยมชม และ cookies ที่เก็บไว้ในเครื่องผู้ใช้ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_026  (source: Operation Honeybee C0006)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทสัญญาณโทรคมนาคมขนาดกลางแห่งหนึ่งในจังหวัดสมุทรปราการได้แจ้งความว่าระบบเซิร์ฟเวอร์ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log และหลักฐานดิจิทัล พบว่าผู้โจมตีได้ใช้ Native API เพื่อเรียกใช้โปรแกรมอันตรายจากภายในระบบปฏิบัติการ และทำการ Modify Registry เพื่อให้โปรแกรมดังกล่าวทำงานอยู่เรื่อยๆ ต่อมาผู้โจมตีได้ค้นหาไฟล์และโฟลเดอร์ที่เก็บข้อมูลลูกค้าและสัญญาอยู่ในเครื่องเซิร์ฟเวอร์ จากนั้นได้ทำการสำรวจและดึงข้อมูลจากระบบเครื่องสำคัญหลายเครื่องโดยการอ่านไฟล์ฐานข้อมูลและเอกสารสำคัญ สุดท้ายผู้โจมตีได้ใช้ Ingress Tool Transfer เพื่อนำเข้าเครื่องมือเพิ่มเติมเข้าสู่ระบบ และทำการส่งข้อมูลที่เก็บรวบรวมได้ออกไปยังเซิร์ฟเวอร์ควบคุมภายนอกผ่านช่องทางสื่อสารที่ไม่ปกติ

*EN:* On 22 February 2569, a mid-sized telecommunications company in Samut Prakan Province reported unauthorized access to its server systems. Digital forensic examination and log analysis revealed that the attacker used Native API to execute malicious programs from within the operating system and performed Modify Registry operations to ensure persistence of the malicious code. Subsequently, the attacker conducted searches for files and folders containing customer data and contracts stored on the server machines. The attacker then extracted data from multiple critical systems by reading database files and sensitive documents. Finally, the attacker used Ingress Tool Transfer to introduce additional tools into the compromised environment and exfiltrated the collected data to an external command server through abnormal communication channels.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1106 Native API | ใช้ Native API เพื่อเรียกใช้โปรแกรมอันตรายจากภายในระบบปฏิบัติการ |
| 2 | named | T1112 Modify Registry | ทำการ Modify Registry เพื่อให้โปรแกรมดังกล่าวทำงานอยู่เรื่อยๆ |
| 3 | described | T1083 File and Directory Discovery | ได้ค้นหาไฟล์และโฟลเดอร์ที่เก็บข้อมูลลูกค้าและสัญญาอยู่ในเครื่องเซิร์ฟเวอร์ |
| 4 | described | T1005 Data from Local System | ได้ทำการสำรวจและดึงข้อมูลจากระบบเครื่องสำคัญหลายเครื่องโดยการอ่านไฟล์ฐานข้อมูลและเอกสารสำคัญ |
| 5 | named | T1105 Ingress Tool Transfer | ได้ใช้ Ingress Tool Transfer เพื่อนำเข้าเครื่องมือเพิ่มเติมเข้าสู่ระบบ |
| 6 | described | T1041 Exfiltration Over C2 Channel | ทำการส่งข้อมูลที่เก็บรวบรวมได้ออกไปยังเซิร์ฟเวอร์ควบคุมภายนอกผ่านช่องทางสื่อสารที่ไม่ปกติ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_027  (source: Operation Dust Storm C0016)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพ ได้รับแจ้งเบาะแสจากผู้ใช้งานว่าคอมพิวเตอร์ของพวกเขาทำงานช้าและมีกิจกรรมที่ผิดปกติ จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่า ผู้โจมตีได้ใช้ drive-by compromise ผ่านการเข้าชมเว็บไซต์ที่ถูกบุกรุกซึ่งมีโค้ด malicious ฝังอยู่ ต่อมาระบบได้ดาวน์โหลด payload และทำการ exploitation for client execution เพื่อรันโค้ดที่ไม่ได้อนุญาติบนเครื่องเหยื่อ จากนั้นมาลแวร์ได้ทำการ software discovery เพื่อค้นหาซอฟต์แวร์และเวอร์ชันที่ติดตั้งอยู่บนระบบ สุดท้ายจากการตรวจสอบ DNS log และ network traffic พบว่า malware ได้ส่งคำขอ DNS ไปยังชื่อโดเมนหลายตัวที่ได้รับการแก้ไขแบบ dynamic โดยเชื่อมต่อไปยัง command-and-control server ต่างๆ

*EN:* On 22 February 2569, a private financial services company in Bangkok received a report from a user that their computer was running slowly with unusual activity. Upon examination of digital evidence, it was found that the attacker used drive-by compromise via a compromised website containing embedded malicious code. Subsequently, the system downloaded a payload and performed exploitation for client execution to run unauthorized code on the victim machine. The malware then conducted software discovery to enumerate installed software and versions on the system. Finally, examination of DNS logs and network traffic revealed that the malware sent DNS queries to multiple domain names that were dynamically resolved, connecting to various command-and-control servers.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1189 Drive-by Compromise | ผู้โจมตีได้ใช้ drive-by compromise ผ่านการเข้าชมเว็บไซต์ที่ถูกบุกรุกซึ่งมีโค้ด malicious ฝังอยู่ |
| 2 | named | T1203 Exploitation for Client Execution | ระบบได้ดาวน์โหลด payload และทำการ exploitation for client execution เพื่อรันโค้ดที่ไม่ได้อนุญาติบนเครื่องเหยื่อ |
| 3 | named | T1518 Software Discovery | มาลแวร์ได้ทำการ software discovery เพื่อค้นหาซอฟต์แวร์และเวอร์ชันที่ติดตั้งอยู่บนระบบ |
| 4 | described | T1568 Dynamic Resolution | malware ได้ส่งคำขอ DNS ไปยังชื่อโดเมนหลายตัวที่ได้รับการแก้ไขแบบ dynamic โดยเชื่อมต่อไปยัง command-and-control server ต่างๆ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_028  (source: Leviathan Australian Intrusions C0049)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพมหานครได้รับแจ้งเบาะแสจากผู้ดูแลระบบว่าพบกิจกรรมที่น่าสงสัยบนเซิร์ฟเวอร์ core infrastructure จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ Valid Accounts ของพนักงานฝ่ายขายที่ลาออกไปแล้วเข้าสู่ระบบ VPN ของบริษัท ต่อมาผู้โจมตีทำการ Exploitation for Privilege Escalation ผ่านช่องโหว่ CVE-2021-44228 บนเซิร์ฟเวอร์ Linux เพื่อยกระดับสิทธิเป็น root จากนั้นจากการวิเคราะห์ memory dump และ command history พบหลักฐานว่าผู้โจมตีได้ค้นหาความสัมพันธ์ระหว่างโดเมน Active Directory ต่างๆ โดยใช้คำสั่ง nltest และ ldapsearch เพื่อสำรวจโครงสร้างเครือข่ายองค์กร สุดท้ายพบว่าผู้โจมตีได้ติดตั้ง keylogger บนสถานีงานสำคัญเพื่อบันทึกการพิมพ์ของผู้บริหาร และส่งข้อมูลที่เก็บรวบรวมได้ออกจากระบบผ่าน C2 channel ไปยัง IP address 185.220.101.x ในต่างประเทศ

*EN:* On 22 February 2569, a private sector information technology company in Bangkok reported suspicious activity on its core infrastructure server to the digital forensics unit. Log analysis revealed that the attacker used Valid Accounts belonging to a former sales employee to access the company's VPN. Subsequently, the attacker performed Exploitation for Privilege Escalation via CVE-2021-44228 vulnerability on a Linux server to achieve root privileges. Analysis of memory dumps and command history showed evidence that the attacker had searched for relationships between various Active Directory domains using nltest and ldapsearch commands to map the organization's network structure. Finally, investigators found that the attacker had installed a keylogger on critical workstations to record administrator keystrokes and exfiltrated collected data over a C2 channel to IP address 185.220.101.x abroad.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1078 Valid Accounts | ผู้โจมตีได้ใช้ Valid Accounts ของพนักงานฝ่ายขายที่ลาออกไปแล้วเข้าสู่ระบบ VPN |
| 2 | named | T1068 Exploitation for Privilege Escalation | ผู้โจมตีทำการ Exploitation for Privilege Escalation ผ่านช่องโหว่ CVE-2021-44228 บนเซิร์ฟเวอร์ Linux เพื่อยกระดับสิทธิเป็น root |
| 3 | described | T1482 Domain Trust Discovery | ผู้โจมตีได้ค้นหาความสัมพันธ์ระหว่างโดเมน Active Directory ต่างๆ โดยใช้คำสั่ง nltest และ ldapsearch เพื่อสำรวจโครงสร้างเครือข่ายองค์กร |
| 4 | described | T1056 Input Capture | ผู้โจมตีได้ติดตั้ง keylogger บนสถานีงานสำคัญเพื่อบันทึกการพิมพ์ของผู้บริหาร |
| 5 | named | T1041 Exfiltration Over C2 Channel | ส่งข้อมูลที่เก็บรวบรวมได้ออกจากระบบผ่าน C2 channel ไปยัง IP address 185.220.101.x ในต่างประเทศ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_029  (source: KV Botnet Activity C0035)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานคร ได้รับแจ้งเบาะแสจากทีมเทคนิคว่าระบบ Windows Server ของแผนกบัญชีเกิดการทำงานผิดปกติ จากการตรวจสอบ log พบว่าผู้โจมตีได้สร้าง Scheduled Task โดยใช้ Event Triggered Execution เพื่อให้มัลแวร์เรียกตัวเองขึ้นมาทุกครั้งที่มีการเข้าสู่ระบบ ต่อมาจากการวิเคราะห์ memory dump พบหลักฐานว่าโปรแกรมที่ติดมาได้ทำการ Process Discovery เพื่อค้นหาแอปพลิเคชันที่สำคัญและเครื่องมือ antivirus ที่ติดตั้งอยู่ สุดท้าย จากการสอบเทียบ network traffic ด้วย packet analyzer พบว่าข้อมูลที่ขโมยมาถูกส่งออกไปยังเซิร์ฟเวอร์ภายนอกผ่านช่องทางการสื่อสารที่เข้ารหัสลับอย่างเข้มงวด ซึ่งไม่สามารถถอดรหัสเพื่อดูเนื้อหาข้อมูลที่แลกเปลี่ยนได้

*EN:* On 22 February 2569, a private financial services company in Bangkok received notification from its technical team that a Windows Server in the accounting department was malfunctioning abnormally. Upon examination of logs, investigators discovered that the attacker had created a Scheduled Task using Event Triggered Execution to ensure the malware re-executed each time a user logged in. Subsequently, memory dump analysis revealed evidence that the installed program had performed Process Discovery to enumerate critical applications and installed antivirus tools. Finally, network traffic examination using a packet analyzer showed that exfiltrated data was transmitted to an external server through a heavily encrypted communication channel, the contents of which could not be decrypted for inspection.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1546 Event Triggered Execution | ผู้โจมตีได้สร้าง Scheduled Task โดยใช้ Event Triggered Execution เพื่อให้มัลแวร์เรียกตัวเองขึ้นมาทุกครั้งที่มีการเข้าสู่ระบบ |
| 2 | named | T1057 Process Discovery | โปรแกรมที่ติดมาได้ทำการ Process Discovery เพื่อค้นหาแอปพลิเคชันที่สำคัญและเครื่องมือ antivirus ที่ติดตั้งอยู่ |
| 3 | described | T1573 Encrypted Channel | ข้อมูลที่ขโมยมาถูกส่งออกไปยังเซิร์ฟเวอร์ภายนอกผ่านช่องทางการสื่อสารที่เข้ารหัสลับอย่างเข้มงวด |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_030  (source: Frankenstein C0001)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทสนับสนุนทางเทคนิคแห่งหนึ่งในจังหวัดกรุงเทพมหานคร ได้รับแจ้งเบาะแสจากแผนกไอทีว่าระบบ Windows Server หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีทำการ Process Discovery เพื่อค้นหารายชื่อและสถานะของ running processes ในเครื่องเซิร์ฟเวอร์ ต่อมาพบหลักฐานการดึงข้อมูลจำนวนมากจากฐานข้อมูลลูกค้าและไฟล์ประวัติการทำงาน โดยการทำงานดังกล่าวเกิดขึ้นซ้ำๆ ในช่วงเวลาต่างๆ ตามตารางอัตโนมัติ จากนั้นระบบพบการเชื่อมต่อขาเข้าไปยังเซิร์ฟเวอร์ภายนอกที่ไม่มีการอนุญาต และมีการโอนย้าย Ingress Tool Transfer ไปยังเครื่องเซิร์ฟเวอร์เพื่อใช้ในการโจมตี สุดท้าย ข้อมูลที่เก็บรวบรวมจำนวนประมาณ 2.3 GB ได้ถูกส่งออกไปยังเซิร์ฟเวอร์ควบคุมภายนอกผ่านช่องทางการสื่อสารที่เข้ารหัส โดยกระบวนการส่งออกเกิดขึ้นโดยอัตโนมัติในช่วงเวลากลางคืน

*EN:* On 22 February 2569, a technical support company in Bangkok received notification from the IT department that a primary Windows Server system had been accessed without authorization. Upon examination of logs, investigators found that the attacker performed Process Discovery to identify and monitor the status of running processes on the server. Subsequently, evidence was discovered of bulk data extraction from customer databases and operational history files occurring repeatedly on automated schedules. The system then detected unauthorized inbound connections to external servers, with Ingress Tool Transfer occurring to place tools on the server for exploitation purposes. Finally, approximately 2.3 GB of collected data was transmitted to external command servers via encrypted communication channels, with the exfiltration occurring automatically during nighttime hours.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1057 Process Discovery | ผู้โจมตีทำการ Process Discovery เพื่อค้นหารายชื่อและสถานะของ running processes ในเครื่องเซิร์ฟเวอร์ |
| 2 | described | T1119 Automated Collection | พบหลักฐานการดึงข้อมูลจำนวนมากจากฐานข้อมูลลูกค้าและไฟล์ประวัติการทำงาน โดยการทำงานดังกล่าวเกิดขึ้นซ้ำๆ ในช่วงเวลาต่างๆ ตามตารางอัตโนมัติ |
| 3 | named | T1105 Ingress Tool Transfer | มีการโอนย้าย Ingress Tool Transfer ไปยังเครื่องเซิร์ฟเวอร์เพื่อใช้ในการโจมตี |
| 4 | described | T1020 Automated Exfiltration | ข้อมูลที่เก็บรวบรวมจำนวนประมาณ 2.3 GB ได้ถูกส่งออกไปยังเซิร์ฟเวอร์ควบคุมภายนอกผ่านช่องทางการสื่อสารที่เข้ารหัส โดยกระบวนการส่งออกเกิดขึ้นโดยอัตโนมัติในช่วงเวลากลางคืน |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_031  (source: SolarWinds Compromise C0024)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการเงินดิจิทัลแห่งหนึ่งในจังหวัดกรุงเทพ แจ้งความว่าระบบ web portal ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log server พบว่าผู้โจมตีได้ส่ง HTTP request ที่มีค่า parameter ผิดปกติเข้าไปยังหน้า login form ของแอปพลิเคชันสาธารณะ และสามารถเข้าสู่ระบบได้สำเร็จ ต่อมาจากการตรวจสอบ database authentication พบว่าผู้โจมตีได้สร้างบัญชีผู้ใช้ชื่อ "admin_support" ขึ้นมาใหม่เพื่อรักษาการเข้าถึงต่อเนื่อง จากนั้นจากการวิเคราะห์ network traffic และ Active Directory logs พบว่าผู้โจมตีได้ทำการ query เพื่อค้นหาความสัมพันธ์ระหว่าง domain และ trust relationship ในสภาพแวดล้อม domain ของบริษัท สุดท้าย จากการตรวจสอบระบบพบว่าผู้โจมตีได้ใช้ Alternate Authentication Material ซึ่งเป็น NTLM hash ที่ได้มาจากการ lateral movement ไปยังเซิร์ฟเวอร์อื่นๆ และดำเนินการ Data from Local System โดยการ copy ไฟล์ข้อมูลลูกค้าจากโฟลเดอร์ shared drive ไปยังเซิร์ฟเวอร์ที่ผู้โจมตีควบคุม

*EN:* On 22 February 2569, a fintech service company in Bangkok reported unauthorized access to its web portal system. Log server examination revealed that the attacker sent HTTP requests with anomalous parameter values to the public login form and successfully authenticated. Subsequently, database authentication checks showed the attacker created a new user account named "admin_support" to maintain persistent access. Network traffic and Active Directory logs analysis then indicated the attacker queried to discover domain relationships and trust configurations within the company's domain environment. Finally, system investigation confirmed the attacker used Alternate Authentication Material in the form of NTLM hashes obtained through lateral movement to other servers, and performed Data from Local System by copying customer data files from shared drive folders to an attacker-controlled server.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ส่ง HTTP request ที่มีค่า parameter ผิดปกติเข้าไปยังหน้า login form ของแอปพลิเคชันสาธารณะ และสามารถเข้าสู่ระบบได้สำเร็จ |
| 2 | described | T1078 Valid Accounts | ผู้โจมตีได้สร้างบัญชีผู้ใช้ชื่อ "admin_support" ขึ้นมาใหม่เพื่อรักษาการเข้าถึงต่อเนื่อง |
| 3 | described | T1482 Domain Trust Discovery | ผู้โจมตีได้ทำการ query เพื่อค้นหาความสัมพันธ์ระหว่าง domain และ trust relationship ในสภาพแวดล้อม domain ของบริษัท |
| 4 | named | T1550 Use Alternate Authentication Material | ผู้โจมตีได้ใช้ Alternate Authentication Material ซึ่งเป็น NTLM hash ที่ได้มาจากการ lateral movement ไปยังเซิร์ฟเวอร์อื่นๆ |
| 5 | named | T1005 Data from Local System | ดำเนินการ Data from Local System โดยการ copy ไฟล์ข้อมูลลูกค้าจากโฟลเดอร์ shared drive ไปยังเซิร์ฟเวอร์ที่ผู้โจมตีควบคุม |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_032  (source: C0017 C0017)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพมหานคร ได้รับแจ้งเบาะแสจากทีมระบบความปลอดภัยว่าพบกิจกรรมที่ผิดปกติบนเซิร์ฟเวอร์ของพวกเขา จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ Exploit Public-Facing Application ผ่านช่องโหว่ในเว็บแอปพลิเคชันที่เปิดให้บริการต่อสาธารณชน เพื่อเข้าถึงระบบ ต่อมาผู้โจมตีทำการ Hijack Execution Flow โดยการแทรกโค้ดเพื่อดำเนินการคำสั่งโดยพลการบนเครื่องจักรที่ถูกบุกรุก จากนั้นผู้โจมตีได้ทำการสอบถามและเก็บรวบรวมข้อมูลเกี่ยวกับบัญชีผู้ใช้ที่มีสิทธิในระบบ รวมถึงชื่อผู้บริหารและสิทธิการเข้าถึงของพวกเขา สุดท้าย จากการวิเคราะห์ traffic พบว่าข้อมูลที่ได้รับการสกัดนั้นถูกส่งออกผ่านเชื่อมต่อกับเซิร์ฟเวอร์ระหว่างประเทศซึ่งทำหน้าที่เป็นจุดผ่านตัวกลาง โดยข้อมูลไหลออกมาอย่างต่อเนื่องผ่านช่องทางการสื่อสารที่ผู้โจมตีสร้างขึ้นมา

*EN:* On 22 February 2569, a private sector information technology company in Bangkok received an alert from its security team regarding suspicious activity on its servers. Upon examination of logs, investigators found that the attacker had used Exploit Public-Facing Application through a vulnerability in the publicly-facing web application to gain access to the system. Subsequently, the attacker performed Hijack Execution Flow by injecting code to execute arbitrary commands on the compromised machine. The attacker then conducted enumeration and collection of information regarding user accounts with system privileges, including administrator names and their access rights. Finally, traffic analysis revealed that the exfiltrated data was being transmitted through connections to an international server serving as an intermediary relay point, with data flowing continuously through a communication channel established by the attacker.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ใช้ Exploit Public-Facing Application ผ่านช่องโหว่ในเว็บแอปพลิเคชันที่เปิดให้บริการต่อสาธารณชน |
| 2 | named | T1574 Hijack Execution Flow | ผู้โจมตีทำการ Hijack Execution Flow โดยการแทรกโค้ดเพื่อดำเนินการคำสั่งโดยพลการบนเครื่องจักรที่ถูกบุกรุก |
| 3 | described | T1033 System Owner/User Discovery | ผู้โจมตีได้ทำการสอบถามและเก็บรวบรวมข้อมูลเกี่ยวกับบัญชีผู้ใช้ที่มีสิทธิในระบบ รวมถึงชื่อผู้บริหารและสิทธิการเข้าถึงของพวกเขา |
| 4 | described | T1090 Proxy | ข้อมูลที่ได้รับการสกัดนั้นถูกส่งออกผ่านเชื่อมต่อกับเซิร์ฟเวอร์ระหว่างประเทศซึ่งทำหน้าที่เป็นจุดผ่านตัวกลาง |
| 5 | described | T1041 Exfiltration Over C2 Channel | ข้อมูลไหลออกมาอย่างต่อเนื่องผ่านช่องทางการสื่อสารที่ผู้โจมตีสร้างขึ้นมา |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_033  (source: Salesforce Data Exfiltration C0059)

**AUTO-FLAGS: step 2: described cue names the technique (Proxy)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ทำการค้นหาและแสดงรายการไฟล์ในไดเรกทอรีต่าง ๆ ของระบบ เพื่อระบุตำแหน่งข้อมูลที่มีค่า ต่อมาผู้โจมตีได้ตั้งค่าการเชื่อมต่อผ่าน proxy server เพื่อปกปิดที่อยู่ IP แท้จริงและหลีกเลี่ยงการตรวจจับจากระบบป้องกัน จากนั้นผู้โจมตีได้ทำการ exfiltration over web service โดยส่งข้อมูลไฟล์สำคัญ เช่น ข้อมูลลูกค้า รายงานการเงิน และเอกสารสัญญา ไปยังเซิร์ฟเวอร์ภายนอกผ่านช่องทาง HTTPS ที่ปกปิดไว้ในเทรฟฟิกปกติ สุดท้ายทีมความปลอดภัยสามารถติดตามการส่งข้อมูลและหยุดการเชื่อมต่อได้ในเวลา 4 ชั่วโมง

*EN:* On 22 February 2569, a private financial company in Bangkok reported unauthorized access to its primary server system. Digital forensic examination of logs revealed that the attacker conducted systematic searching and listing of files across various system directories to identify valuable data locations. Subsequently, the attacker configured connections through a proxy server to mask the genuine IP address and evade detection systems. The attacker then performed exfiltration over web service by transmitting critical files including customer data, financial reports, and contract documents to an external server via HTTPS channels concealed within normal traffic. Finally, the security team was able to trace the data transmission and terminate the connection within 4 hours.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1083 File and Directory Discovery | ผู้โจมตีได้ทำการค้นหาและแสดงรายการไฟล์ในไดเรกทอรีต่าง ๆ ของระบบ |
| 2 | described | T1090 Proxy | ผู้โจมตีได้ตั้งค่าการเชื่อมต่อผ่าน proxy server เพื่อปกปิดที่อยู่ IP แท้จริง |
| 3 | named | T1567 Exfiltration Over Web Service | ผู้โจมตีได้ทำการ exfiltration over web service โดยส่งข้อมูลไฟล์สำคัญ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_034  (source: FunnyDream C0007)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพมหานคร แจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ของระบบพบว่าผู้โจมตีได้ใช้ Windows Management Instrumentation ในการดำเนินการคำสั่งบนเครื่องคอมพิวเตอร์เป้าหมาย ต่อมาผู้โจมตีได้ทำการสอบถามข้อมูลเกี่ยวกับรุ่นระบบปฏิบัติการ สถาปัตยกรรมโปรเซสเซอร์ และการกำหนดค่าฮาร์ดแวร์ของเครื่องที่ถูกบุกรุก จากนั้นผู้โจมตีได้ดาวน์โหลดไฟล์เครื่องมือจำนวนหลายไฟล์ขนาดใหญ่จากเซิร์ฟเวอร์ภายนอกมายังระบบของผู้เสียหาย ผ่านทางการเชื่อมต่อเครือข่ายที่ไม่ปลอดภัย

*EN:* On 22 February 2569, a private information technology company in Bangkok reported unauthorized access to its primary server system. From examination of system logs, investigators found that the attacker used Windows Management Instrumentation to execute commands on the target computer. Subsequently, the attacker queried information about the operating system version, processor architecture, and hardware configuration of the compromised machine. The attacker then downloaded multiple large tool files from an external server to the victim's system over an insecure network connection.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1047 Windows Management Instrumentation | ใช้ Windows Management Instrumentation ในการดำเนินการคำสั่งบนเครื่องคอมพิวเตอร์เป้าหมาย |
| 2 | described | T1082 System Information Discovery | ได้ทำการสอบถามข้อมูลเกี่ยวกับรุ่นระบบปฏิบัติการ สถาปัตยกรรมโปรเซสเซอร์ และการกำหนดค่าฮาร์ดแวร์ของเครื่องที่ถูกบุกรุก |
| 3 | described | T1105 Ingress Tool Transfer | ได้ดาวน์โหลดไฟล์เครื่องมือจำนวนหลายไฟล์ขนาดใหญ่จากเซิร์ฟเวอร์ภายนอกมายังระบบของผู้เสียหาย |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_035  (source: Operation CuckooBees C0012)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพฯ ได้รับแจ้งเบาะแสจากผู้ดูแลระบบว่าพบกิจกรรมที่น่าสงสัยบนเซิร์ฟเวอร์หลัก จากการตรวจสอบ log พบว่าผู้โจมตีได้เข้าถึงระบบผ่านทางการใช้บริการ Remote Desktop Protocol ที่เปิดให้บริการแบบสาธารณะบนอินเทอร์เน็ต โดยไม่มีการตรวจสอบความถูกต้องของแหล่งที่มา ต่อมา ผู้โจมตีได้ดำเนินการค้นหาบริการและโปรแกรมที่ติดตั้งบนระบบปฏิบัติการเพื่อทำความเข้าใจสภาพแวดล้อมของเครื่องคอมพิวเตอร์ จากนั้นผู้โจมตีได้ทำการ Data from Local System โดยการเข้าถึงและสำเนาไฟล์ข้อมูลที่เก็บไว้ในเครื่องเฉพาะเจาะจง รวมถึงไฟล์การตั้งค่าระบบและฐานข้อมูลท้องถิ่น

*EN:* On 22 February 2569, a private information technology company in Bangkok received notification from a system administrator of suspicious activity on the primary server. From log examination, it was found that the attacker gained access to the system via Remote Desktop Protocol service exposed publicly on the Internet without source authentication verification. Subsequently, the attacker conducted reconnaissance of services and installed programs on the operating system to understand the computer environment. Thereafter, the attacker performed Data from Local System by accessing and copying data files stored on the specific machine, including system configuration files and local databases.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1133 External Remote Services | ผู้โจมตีได้เข้าถึงระบบผ่านทางการใช้บริการ Remote Desktop Protocol ที่เปิดให้บริการแบบสาธารณะบนอินเทอร์เน็ต โดยไม่มีการตรวจสอบความถูกต้องของแหล่งที่มา |
| 2 | described | T1007 System Service Discovery | ผู้โจมตีได้ดำเนินการค้นหาบริการและโปรแกรมที่ติดตั้งบนระบบปฏิบัติการเพื่อทำความเข้าใจสภาพแวดล้อมของเครื่องคอมพิวเตอร์ |
| 3 | named | T1005 Data from Local System | ผู้โจมตีได้ทำการ Data from Local System โดยการเข้าถึงและสำเนาไฟล์ข้อมูลที่เก็บไว้ในเครื่องเฉพาะเจาะจง รวมถึงไฟล์การตั้งค่าระบบและฐานข้อมูลท้องถิ่น |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_036  (source: RedPenguin C0056)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพได้แจ้งความว่าระบบเซิร์ฟเวอร์ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ Valid Accounts ของพนักงานฝ่ายขายที่ลาออกมาแล้ว เข้าสู่ระบบ VPN ของบริษัท ต่อมาผู้โจมตีได้ทำการ Exploitation for Client Execution ผ่านการส่ง malicious PDF file ไปยังอีเมล์ของผู้บริหารเพื่อให้เกิด remote code execution บนเครื่อง workstation จากนั้นจากการตรวจสอบไฟล์ระบบพบว่ามีการแก้ไขไฟล์ binary ของโปรแกรม antivirus ที่ติดตั้งอยู่ เพื่อให้ antivirus ไม่สามารถตรวจจับการกระทำของ malware ได้ สุดท้ายผู้โจมตีได้ทำการ System Network Configuration Discovery โดยใช้ ipconfig และ arp -a เพื่อรวบรวมข้อมูลโครงสร้างเครือข่ายของบริษัท จากการตรวจสอบ outbound traffic พบว่ามีการโอนย้ายเครื่องมือ hacking tools ไปยังเครื่องที่ติดเชื้อผ่าน HTTP download จากเซิร์ฟเวอร์ C2 ภายนอก และสุดท้ายพบการส่งข้อมูลไฟล์ลับของบริษัทกลับไปยังเซิร์ฟเวอร์ C2 เดียวกันผ่านการเข้ารหัส HTTPS ที่ไม่ใช่ standard port

*EN:* On 22 February 2569, a private information technology company in Bangkok reported unauthorized access to its server systems. Log examination revealed that the attacker used Valid Accounts belonging to a former sales department employee to access the company's VPN. Subsequently, the attacker conducted Exploitation for Client Execution by sending a malicious PDF file to an executive's email to achieve remote code execution on a workstation machine. Later, system file inspection showed that the antivirus program binary had been modified to prevent the antivirus from detecting malware activity. Finally, the attacker performed System Network Configuration Discovery using ipconfig and arp -a commands to gather the company's network architecture information. Outbound traffic analysis revealed the transfer of hacking tools to the infected machine via HTTP download from an external C2 server. The investigation concluded with evidence of confidential company files being exfiltrated back to the same C2 server through encrypted HTTPS on a non-standard port.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1078 Valid Accounts | ผู้โจมตีได้ใช้ Valid Accounts ของพนักงานฝ่ายขายที่ลาออกมาแล้ว เข้าสู่ระบบ VPN ของบริษัท |
| 2 | named | T1203 Exploitation for Client Execution | ผู้โจมตีได้ทำการ Exploitation for Client Execution ผ่านการส่ง malicious PDF file ไปยังอีเมล์ของผู้บริหารเพื่อให้เกิด remote code execution บนเครื่อง workstation |
| 3 | described | T1554 Compromise Host Software Binary | มีการแก้ไขไฟล์ binary ของโปรแกรม antivirus ที่ติดตั้งอยู่ เพื่อให้ antivirus ไม่สามารถตรวจจับการกระทำของ malware ได้ |
| 4 | named | T1016 System Network Configuration Discovery | ผู้โจมตีได้ทำการ System Network Configuration Discovery โดยใช้ ipconfig และ arp -a เพื่อรวบรวมข้อมูลโครงสร้างเครือข่ายของบริษัท |
| 5 | described | T1105 Ingress Tool Transfer | มีการโอนย้ายเครื่องมือ hacking tools ไปยังเครื่องที่ติดเชื้อผ่าน HTTP download จากเซิร์ฟเวอร์ C2 ภายนอก |
| 6 | described | T1041 Exfiltration Over C2 Channel | พบการส่งข้อมูลไฟล์ลับของบริษัทกลับไปยังเซิร์ฟเวอร์ C2 เดียวกันผ่านการเข้ารหัส HTTPS ที่ไม่ใช่ standard port |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_037  (source: Versa Director Zero Day Exploitation C0039)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการสินค้าคงคลังแห่งหนึ่งในจังหวัดสมุทรปราการได้แจ้งความเข้าถึงระบบที่ไม่ได้รับอนุญาต จากการตรวจสอบ log ของเซิร์ฟเวอร์ web application พบว่าผู้โจมตีได้ส่ง HTTP request ที่มีค่า parameter ผิดปกติไปยัง endpoint ของระบบสินค้าคงคลัง ซึ่งเป็นส่วนที่เปิดให้บุคลากรภายนอกเข้าถึงได้ และสามารถเข้าไปในระบบได้สำเร็จ ต่อมา จากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าผู้โจมตีได้ปลูกไฟล์ JavaScript ในหน้า login form เพื่อจับข้อมูลชื่อผู้ใช้และรหัสผ่านของพนักงานที่เข้าสู่ระบบ จากนั้น ผู้โจมตีได้ใช้ข้อมูลประจำตัวที่ได้มาเพื่อเชื่อมต่อไปยังเซิร์ฟเวอร์ผ่าน DNS tunnel protocol ซึ่งเป็นการสื่อสารระหว่างเครื่องที่ติดเชื้อกับเซิร์ฟเวอร์ควบคุมจากระยะไกล ทำให้ผู้โจมตีสามารถควบคุมระบบได้อย่างต่อเนื่อง

*EN:* On 22 February 2569, a private logistics company in Samut Prakan province reported unauthorized system access. Upon examination of web server logs, investigators found that the attacker sent malformed HTTP requests with abnormal parameter values to the inventory system endpoint, which was accessible to external personnel, and successfully gained entry. Subsequently, digital forensic examination revealed that the attacker planted JavaScript code within the login form page to capture usernames and passwords from employees logging into the system. Thereafter, the attacker used the obtained credentials to connect to the server via DNS tunnel protocol, a communication method between the infected machine and a remote command server, enabling persistent control of the system.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ส่ง HTTP request ที่มีค่า parameter ผิดปกติไปยัง endpoint ของระบบสินค้าคงคลัง ซึ่งเป็นส่วนที่เปิดให้บุคลากรภายนอกเข้าถึงได้ และสามารถเข้าไปในระบบได้สำเร็จ |
| 2 | described | T1056 Input Capture | ปลูกไฟล์ JavaScript ในหน้า login form เพื่อจับข้อมูลชื่อผู้ใช้และรหัสผ่านของพนักงานที่เข้าสู่ระบบ |
| 3 | described | T1095 Non-Application Layer Protocol | เชื่อมต่อไปยังเซิร์ฟเวอร์ผ่าน DNS tunnel protocol ซึ่งเป็นการสื่อสารระหว่างเครื่องที่ติดเชื้อกับเซิร์ฟเวอร์ควบคุมจากระยะไกล |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_038  (source: SolarWinds Compromise C0024)

**AUTO-FLAGS: step 3: described cue names the technique (Account Discovery)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบ web application ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีใช้ประโยชน์จากช่องโหว่ในส่วน authentication module ของแอปพลิเคชันเพื่อเข้าสู่ระบบ ต่อมาจากการวิเคราะห์ browser history และ cookie storage พบว่าผู้โจมตีได้ทำการ steal web session cookie ของผู้ดูแลระบบ จากนั้นใช้ cookie ที่ขโมยมาเพื่อเข้าถึงบัญชีผู้ดูแลระบบ และทำการ account discovery โดยค้นหาบัญชีผู้ใช้อื่นๆ ในระบบ directory service

*EN:* On 22 February 2569, a financial services company in Bangkok reported unauthorized access to its web application. Log analysis revealed that the attacker exploited a vulnerability in the authentication module to gain initial access. Subsequently, analysis of browser history and cookie storage showed that the attacker had stolen the web session cookie of a system administrator. The attacker then used the stolen cookie to access the administrator's account and conducted account discovery by searching for other user accounts in the system's directory service.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ผู้โจมตีใช้ประโยชน์จากช่องโหว่ในส่วน authentication module ของแอปพลิเคชันเพื่อเข้าสู่ระบบ |
| 2 | named | T1539 Steal Web Session Cookie | ผู้โจมตีได้ทำการ steal web session cookie ของผู้ดูแลระบบ |
| 3 | described | T1087 Account Discovery | ทำการ account discovery โดยค้นหาบัญชีผู้ใช้อื่นๆ ในระบบ directory service |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_039  (source: 2016 Ukraine Electric Power Attack C0025)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในกรุงเทพมหานคร ได้รับแจ้งเบาะแสจากฝ่ายเทคนิคว่าพบกิจกรรมที่ผิดปกติบนเซิร์ฟเวอร์ Windows จากการตรวจสอบ Event Viewer พบว่าระบบได้ประมวลผลคำสั่งผ่าน WMI Command-line Utility ซึ่งไม่ตรงกับการใช้งานปกติของผู้ใช้ ต่อมาจากการตรวจสอบ Active Directory พบว่ามีบัญชีผู้ใช้ใหม่ชื่อ "svc_backup_2569" ถูกสร้างขึ้นในเวลาเดียวกัน จากนั้นการวิเคราะห์ log authentication แสดงว่าระบบถูกทำการทดสอบรหัสผ่านซ้ำๆ ต่อเนื่องกว่า 2,000 ครั้งในระยะเวลา 6 ชั่วโมง เพื่อเข้าถึงบัญชีผู้ดูแลระบบ สุดท้าย log เซิร์ฟเวอร์ Domain Controller บันทึกว่ามีการสอบถามข้อมูลเครื่องคอมพิวเตอร์อื่นๆ ในเครือข่าย และพบการถ่ายโอนไฟล์เครื่องมือสอบสวนจากเซิร์ฟเวอร์ต้นทางไปยังสถานีงานหลายเครื่องผ่าน SMB share ในช่วงเวลา 03:15-04:45 น.

*EN:* On 22 February 2569, an information technology services company in Bangkok received notification from the technical department of unusual activity on a Windows server. Upon examination of the Event Viewer, the system was found to have processed commands via WMI Command-line Utility inconsistent with normal user operations. Subsequently, examination of Active Directory revealed that a new user account named "svc_backup_2569" had been created at the same time. Analysis of authentication logs then showed the system had undergone repeated password testing over 2,000 times within a 6-hour period to access administrator accounts. Finally, Domain Controller server logs recorded queries of other computers in the network, and file transfers of investigation tools from the source server to multiple workstations via SMB share were observed between 03:15-04:45.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1047 Windows Management Instrumentation | ระบบได้ประมวลผลคำสั่งผ่าน WMI Command-line Utility ซึ่งไม่ตรงกับการใช้งานปกติของผู้ใช้ |
| 2 | described | T1136 Create Account | มีบัญชีผู้ใช้ใหม่ชื่อ "svc_backup_2569" ถูกสร้างขึ้นในเวลาเดียวกัน |
| 3 | described | T1110 Brute Force | ระบบถูกทำการทดสอบรหัสผ่านซ้ำๆ ต่อเนื่องกว่า 2,000 ครั้งในระยะเวลา 6 ชั่วโมง เพื่อเข้าถึงบัญชีผู้ดูแลระบบ |
| 4 | described | T1018 Remote System Discovery | มีการสอบถามข้อมูลเครื่องคอมพิวเตอร์อื่นๆ ในเครือข่าย |
| 5 | described | T1570 Lateral Tool Transfer | พบการถ่ายโอนไฟล์เครื่องมือสอบสวนจากเซิร์ฟเวอร์ต้นทางไปยังสถานีงานหลายเครื่องผ่าน SMB share |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_040  (source: 3CX Supply Chain Attack C0057)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการโทรคมนาคมแห่งหนึ่งในจังหวัดกรุงเทพมหานครได้รับแจ้งจากแผนกเทคโนโลยีสารสนเทศว่าพบกิจกรรมที่ผิดปกติในระบบ email server ของเขต IT operations จากการตรวจสอบ log authentication พบว่าผู้โจมตีใช้ Valid Accounts ของพนักงานระดับเจ้าหน้าที่ที่เกษียณอายุแล้วเพื่อเข้าสู่ระบบในเวลา 03:47 น. ต่อมา จากการวิเคราะห์ process execution logs พบว่ามีการ inject code เข้าไปในโปรแกรม svchost.exe เพื่อให้ได้สิทธิ์ระดับสูงในการเข้าถึงทรัพยากรของระบบ จากนั้น จากการตรวจสอบ browser history และ cache files บนเครื่องคอมพิวเตอร์ที่เสียหายพบว่าผู้โจมตีได้ทำการค้นหาและเก็บข้อมูลเกี่ยวกับการกำหนดค่า network infrastructure รวมถึงรายการ VPN endpoints และ internal domain names ของบริษัท

*EN:* On 22 February 2569, a telecommunications service provider in Bangkok reported suspicious activity detected by the IT operations team on their email server. Log examination revealed that the attacker used Valid Accounts belonging to a retired staff member to authenticate at 03:47. Subsequently, analysis of process execution logs showed code injection into svchost.exe to escalate privileges and access system resources. Investigation of browser history and cache files on the compromised machine indicated the attacker searched for and collected information about network infrastructure configuration, including VPN endpoints and internal domain names of the company.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1078 Valid Accounts | ผู้โจมตีใช้ Valid Accounts ของพนักงานระดับเจ้าหน้าที่ที่เกษียณอายุแล้ว |
| 2 | described | T1055 Process Injection | มีการ inject code เข้าไปในโปรแกรม svchost.exe เพื่อให้ได้สิทธิ์ระดับสูง |
| 3 | described | T1217 Browser Information Discovery | จากการตรวจสอบ browser history และ cache files บนเครื่องคอมพิวเตอร์ที่เสียหายพบว่าผู้โจมตีได้ทำการค้นหาและเก็บข้อมูลเกี่ยวกับการกำหนดค่า network infrastructure |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_041  (source: C0015 C0015)

> เมื่อวันที่ 12 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกบุกรุก จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ Windows Management Instrumentation เพื่อรันคำสั่งบนเครื่องเซิร์ฟเวอร์ที่ได้เข้าถึงแล้ว ต่อมาผู้โจมตีทำการตรวจสอบเวลาระบบและข้อมูลการซิงโครไนซ์เพื่อวางแผนการทำงานต่อไป จากนั้นพบหลักฐานว่าผู้โจมตีได้ทำการโอนเครื่องมือและสคริปต์ที่ใช้ในการโจมตีไปยังเครื่องคอมพิวเตอร์อื่นๆ ในเครือข่ายภายในองค์กรผ่านทางเชื่อมต่อเครือข่ายที่มีอยู่ สุดท้ายข้อมูลทั้งหมดในเซิร์ฟเวอร์และสถานีงานต่างๆ ถูกเข้ารหัสด้วยอัลกอริทึมการเข้ารหัสแบบแข็งแกร่ง และผู้โจมตีได้ฝากข้อความเรียกค่าไถ่พร้อมคำขู่เมื่อเดือนกุมภาพันธ์ 2569

*EN:* On 12 February 2569, a private logistics management company in Samut Prakan Province reported a breach of its primary server system. Upon examination of system logs, investigators found that the attacker had used Windows Management Instrumentation to execute commands on the compromised server. Subsequently, the attacker performed reconnaissance of system time and synchronization data to plan further operations. Evidence then showed that the attacker transferred attack tools and scripts to other computers within the organization's internal network via existing network connections. Finally, all data on servers and workstations was encrypted using strong encryption algorithms, and the attacker left a ransom message with threats in February 2569.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1047 Windows Management Instrumentation | ผู้โจมตีได้ใช้ Windows Management Instrumentation เพื่อรันคำสั่งบนเครื่องเซิร์ฟเวอร์ |
| 2 | named | T1124 System Time Discovery | ผู้โจมตีทำการตรวจสอบเวลาระบบและข้อมูลการซิงโครไนซ์ |
| 3 | described | T1570 Lateral Tool Transfer | ผู้โจมตีได้ทำการโอนเครื่องมือและสคริปต์ที่ใช้ในการโจมตีไปยังเครื่องคอมพิวเตอร์อื่นๆ ในเครือข่ายภายในองค์กรผ่านทางเชื่อมต่อเครือข่ายที่มีอยู่ |
| 4 | described | T1486 Data Encrypted for Impact | ข้อมูลทั้งหมดในเซิร์ฟเวอร์และสถานีงานต่างๆ ถูกเข้ารหัสด้วยอัลกอริทึมการเข้ารหัสแบบแข็งแกร่ง |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_042  (source: Frankenstein C0001)

**AUTO-FLAGS: step 1: cue not found verbatim in narrative**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบคอมพิวเตอร์ของพนักงานหลายคนได้รับความเสียหาย โดยพบว่ามีไฟล์ที่น่าสงสัยถูกเรียกใช้งานจากอีเมลที่มาจากผู้ส่งที่ไม่รู้จัก ซึ่งเป็นการโจมตี Exploitation for Client Execution ที่ทำให้โค้ดอันตรายทำงานบนเครื่องของเหยื่อ จากการตรวจสอบ log และหน่วยความจำของเครื่องที่ติดเชื้อพบว่า ระบบปฏิบัติการและการกำหนดค่าฮาร์ดแวร์ได้ถูกสอบถามผ่านคำสั่ง systeminfo และ wmic เพื่อรวบรวมข้อมูลเกี่ยวกับสภาพแวดล้อมของเครื่องเป้าหมาย ต่อมาพบหลักฐานว่ามีการดาวน์โหลดเครื่องมือเพิ่มเติมจากเซิร์ฟเวอร์ที่ควบคุมโดยผู้โจมตี ซึ่งถูกเก็บไว้ในโฟลเดอร์ temp และ AppData ของระบบ สุดท้าย จากการวิเคราะห์ network traffic และ event log พบว่ามีการส่งข้อมูลขนาดใหญ่ออกจากเครื่องไปยังเซิร์ฟเวอร์ภายนอกอย่างสม่ำเสมอ โดยไฟล์ฐานข้อมูลลูกค้าและเอกสารสัญญาจำนวน 847 ไฟล์ถูกส่งออกไปโดยกระบวนการอัตโนมัติในช่วงเวลา 2 สัปดาห์

*EN:* On 22 February 2569, a private logistics management company in Samut Prakan Province reported that computer systems of multiple employees were compromised. It was found that a suspicious file was executed from an email sent by an unknown sender, which was an Exploitation for Client Execution attack that caused malicious code to run on the victim's machine. From examination of logs and memory of the infected machine, it was found that the operating system and hardware configuration were queried through systeminfo and wmic commands to gather information about the target machine environment. Subsequently, evidence was found of downloading additional tools from a server controlled by the attacker, which were stored in the system's temp and AppData folders. Finally, from analysis of network traffic and event logs, it was found that large amounts of data were being sent from the machine to an external server on a regular basis, with 847 customer database files and contract documents being automatically exfiltrated over a 2-week period.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1203 Exploitation for Client Execution | มีไฟล์ที่น่าสงสัยถูกเรียกใช้งานจากอีเมลที่มาจากผู้ส่งที่ไม่รู้จัก ซึ่งเป็นการโจมตีที่ทำให้โค้ดอันตรายทำงานบนเครื่องของเหยื่อ |
| 2 | described | T1082 System Information Discovery | ระบบปฏิบัติการและการกำหนดค่าฮาร์ดแวร์ได้ถูกสอบถามผ่านคำสั่ง systeminfo และ wmic เพื่อรวบรวมข้อมูลเกี่ยวกับสภาพแวดล้อมของเครื่องเป้าหมาย |
| 3 | described | T1105 Ingress Tool Transfer | มีการดาวน์โหลดเครื่องมือเพิ่มเติมจากเซิร์ฟเวอร์ที่ควบคุมโดยผู้โจมตี ซึ่งถูกเก็บไว้ในโฟลเดอร์ temp และ AppData |
| 4 | described | T1020 Automated Exfiltration | มีการส่งข้อมูลขนาดใหญ่ออกจากเครื่องไปยังเซิร์ฟเวอร์ภายนอกอย่างสม่ำเสมอ โดยไฟล์ฐานข้อมูลลูกค้าและเอกสารสัญญาจำนวน 847 ไฟล์ถูกส่งออกไปโดยกระบวนการอัตโนมัติ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_043  (source: Leviathan Australian Intrusions C0049)

**AUTO-FLAGS: step 4: cue not found verbatim in narrative**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานคร ได้แจ้งความว่าระบบเซิร์ฟเวอร์ของฝ่ายบัญชีถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ระบบ Active Directory พบว่าบัญชีผู้ใช้งานของพนักงานฝ่ายไอทีชื่อ Somchai.Niran ได้ถูกใช้เข้าสู่ระบบในเวลา 02:47 น. ซึ่งไม่ตรงกับช่วงเวลาการทำงานปกติ ต่อมา จากการตรวจสอบพยานหลักฐานดิจิทัลบนเซิร์ฟเวอร์ พบร่องรอยการรันคำสั่ง whoami และ systeminfo เพื่อเพิ่มสิทธิ์ผู้ใช้งาน รวมถึงการแก้ไข User Access Control settings ด้วยเครื่องมือ UAC bypass จากนั้น ผู้โจมตีได้ทำการค้นหาและเรียกดูไฟล์ Group Policy Objects ที่เก็บไว้ในโฟลเดอร์ SYSVOL เพื่อรวบรวมข้อมูลเกี่ยวกับนโยบายความปลอดภัยขององค์กร สุดท้าย ข้อมูลที่ได้รวบรวมจำนวนประมาณ 2.3 GB ซึ่งประกอบด้วยไฟล์ Excel ใบแจ้งหนี้ และเอกสารข้อตกลงลูกค้า ได้ถูกส่งออกผ่าน Exfiltration over C2 channel ไปยังเซิร์ฟเวอร์ภายนอกที่อยู่ในสหพันธ์รัสเซีย โดยการส่งข้อมูลดังกล่าวเสร็จสิ้นในเวลา 04:22 น.

*EN:* On 22 February 2569, a private financial services company in Bangkok province reported unauthorized access to its accounting department server. Log examination of the Active Directory system revealed that the IT staff member's user account named Somchai.Niran was used to log in at 02:47 AM, inconsistent with normal working hours. Subsequently, digital forensic examination of the server discovered traces of commands such as whoami and systeminfo being executed to elevate user privileges, including modifications to User Access Control settings using UAC bypass tools. The attacker then searched for and accessed Group Policy Objects stored in the SYSVOL folder to gather information about the organization's security policies. Finally, approximately 2.3 GB of collected data, consisting of Excel files containing invoices and customer agreement documents, was exfiltrated over a C2 channel to a server located in the Russian Federation, with the data transfer completed at 04:22 AM.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | บัญชีผู้ใช้งานของพนักงานฝ่ายไอทีชื่อ Somchai.Niran ได้ถูกใช้เข้าสู่ระบบในเวลา 02:47 น. |
| 2 | described | T1068 Exploitation for Privilege Escalation | การรันคำสั่ง whoami และ systeminfo เพื่อเพิ่มสิทธิ์ผู้ใช้งาน รวมถึงการแก้ไข User Access Control settings ด้วยเครื่องมือ UAC bypass |
| 3 | described | T1615 Group Policy Discovery | ผู้โจมตีได้ทำการค้นหาและเรียกดูไฟล์ Group Policy Objects ที่เก็บไว้ในโฟลเดอร์ SYSVOL เพื่อรวบรวมข้อมูลเกี่ยวกับนโยบายความปลอดภัยขององค์กร |
| 4 | named | T1041 Exfiltration Over C2 Channel | ข้อมูลที่ได้รวบรวมจำนวนประมาณ 2.3 GB ได้ถูกส่งออกผ่าน Exfiltration over C2 channel ไปยังเซิร์ฟเวอร์ภายนอกที่อยู่ในสหพันธ์รัสเซีย |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_044  (source: Operation Wocao C0014)

**AUTO-FLAGS: step 3: described cue names the technique (Query Registry)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทบริหารจัดการสินทรัพย์ดิจิทัลแห่งหนึ่งในจังหวัดกรุงเทพฯ ได้แจ้งความเข้าถึงระบบโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ช่องโหว่ในเว็บแอปพลิเคชันสาธารณะเพื่อเจาะระบบเซิร์ฟเวอร์หลัก ต่อมาผู้โจมตีได้ฉีด malicious code เข้าไปในโปรเซสระบบปฏิบัติการเพื่อยกระดับสิทธิ์การเข้าถึงจากผู้ใช้ทั่วไปเป็นผู้ดูแลระบบ จากนั้นทำการ Query registry เพื่อสำรวจการตั้งค่าระบบและรวบรวมข้อมูลจาก Local System อันได้แก่ รหัสผ่าน SSH keys และข้อมูลการตั้งค่าบัญชีผู้ใช้ สุดท้ายผู้โจมตีได้สร้างการเชื่อมต่อ command-and-control ผ่านพอร์ตที่ไม่ใช่พอร์ตมาตรฐาน (port 8847) เพื่อรักษาการควบคุมระบบและทำการส่งข้อมูลออกจากเครือข่าย

*EN:* On 22 February 2569, a digital asset management company in Bangkok reported unauthorized system access. Log examination revealed that the attacker exploited a vulnerability in the public-facing web application to compromise the main server. Subsequently, the attacker injected malicious code into an operating system process to escalate privileges from standard user to administrator. The attacker then queried registry settings to survey system configuration and collected data from the local system including SSH keys, passwords, and user account settings. Finally, the attacker established command-and-control communication over non-standard port 8847 to maintain system control and exfiltrate data from the network.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ใช้ช่องโหว่ในเว็บแอปพลิเคชันสาธารณะเพื่อเจาะระบบเซิร์ฟเวอร์หลัก |
| 2 | described | T1055 Process Injection | ผู้โจมตีได้ฉีด malicious code เข้าไปในโปรเซสระบบปฏิบัติการเพื่อยกระดับสิทธิ์การเข้าถึง |
| 3 | described | T1012 Query Registry | ทำการ Query registry เพื่อสำรวจการตั้งค่าระบบ |
| 4 | named | T1005 Data from Local System | รวบรวมข้อมูลจาก Local System อันได้แก่ รหัสผ่าน SSH keys และข้อมูลการตั้งค่าบัญชีผู้ใช้ |
| 5 | described | T1571 Non-Standard Port | ผู้โจมตีได้สร้างการเชื่อมต่อ command-and-control ผ่านพอร์ตที่ไม่ใช่พอร์ตมาตรฐาน (port 8847) |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_045  (source: ShadowRay C0045)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการขนส่งและโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบ web application ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีใช้ Exploit Public-Facing Application ผ่านช่องโหว่ในหน้า login เพื่อเข้าสู่ระบบด้วยสิทธิผู้ใช้ทั่วไป ต่อมาจากการวิเคราะห์ไฟล์ระบบและ privilege escalation log พบร่องรอยการเปลี่ยนแปลงการตั้งค่าไฟล์ kernel module และการแก้ไข sudoers file ซึ่งแสดงให้เห็นว่าผู้โจมตีได้ยกระดับสิทธิเข้าถึงเป็น root จากนั้นในระยะเวลา 4 ชั่วโมงต่อมา ตรวจพบการโหลด payload ขนาด 2.3 MB จากเซิร์ฟเวอร์ภายนอก IP 103.145.xxx.xxx ผ่าน curl command ไปยังไดเรกทอรี่ /tmp/ และการสร้าง reverse shell connection ไปยังที่อยู่ IP เดียวกันบนพอร์ต 4444 ซึ่งเป็นช่องทางสำหรับส่งคำสั่งและควบคุมระบบต่อไป

*EN:* On 22 February 2569, a transport and logistics services company in Samut Prakan Province reported unauthorized access to its web application system. Log analysis revealed that the attacker used Exploit Public-Facing Application through a vulnerability in the login page to gain initial user-level access. Subsequently, examination of system files and privilege escalation logs showed traces of kernel module configuration changes and sudoers file modifications, indicating the attacker escalated privileges to root level. Within 4 hours, evidence of a 2.3 MB payload being downloaded from external server IP 103.145.xxx.xxx via curl command to the /tmp/ directory was detected, followed by establishment of a reverse shell connection to the same IP address on port 4444, establishing a command and control channel.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1190 Exploit Public-Facing Application | ผู้โจมตีใช้ Exploit Public-Facing Application ผ่านช่องโหว่ในหน้า login |
| 2 | described | T1068 Exploitation for Privilege Escalation | ร่องรอยการเปลี่ยนแปลงการตั้งค่าไฟล์ kernel module และการแก้ไข sudoers file ซึ่งแสดงให้เห็นว่าผู้โจมตีได้ยกระดับสิทธิเข้าถึงเป็น root |
| 3 | described | T1105 Ingress Tool Transfer | การโหลด payload ขนาด 2.3 MB จากเซิร์ฟเวอร์ภายนอก IP 103.145.xxx.xxx ผ่าน curl command ไปยังไดเรกทอรี่ /tmp/ และการสร้าง reverse shell connection |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_046  (source: ArcaneDoor C0046)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานครแจ้งความว่า ระบบ Windows Server ของแผนกบัญชีถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่า ผู้โจมตีได้เข้าใช้ External Remote Services ผ่านการเชื่อมต่อ RDP ที่มีข้อมูลประจำตัวที่อ่อนแอ และทำการรันคำสั่ง Command and Scripting Interpreter โดยใช้ PowerShell script เพื่อปรับแต่ง Power Settings ของระบบ เพื่อให้เครื่องไม่เข้าสู่ sleep mode ในระหว่างการโจมตี ต่อมา จากการวิเคราะห์ traffic พบการเชื่อมต่อ network ที่ผิดปกติซึ่งบ่งชี้ว่ามีการสกัดข้อมูล credential ระหว่างการสื่อสาร และผู้โจมตีได้ทำการสกัดข้อมูลไฟล์บัญชีรายชื่อลูกค้าและรายการธุรกรรมทางการเงินอย่างเป็นระบบ จากนั้นข้อมูลดังกล่าวถูกส่งออกจากระบบผ่าน C2 channel ไปยังเซิร์ฟเวอร์ที่อยู่ต่างประเทศ

*EN:* On 22 February 2569, a financial services company in Bangkok reported unauthorized access to a Windows Server in the accounting department. Log analysis revealed that the attacker gained access via External Remote Services using RDP with weak credentials, then executed commands using Command and Scripting Interpreter with PowerShell scripts to adjust Power Settings to prevent the machine from entering sleep mode during the attack. Subsequently, network traffic analysis indicated abnormal connections suggesting credential interception during communications, and the attacker systematically extracted customer account files and financial transaction records. The data was then exfiltrated over the C2 Channel to a foreign server.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1133 External Remote Services | เข้าใช้ External Remote Services ผ่านการเชื่อมต่อ RDP |
| 2 | named | T1059 Command and Scripting Interpreter | รันคำสั่ง Command and Scripting Interpreter โดยใช้ PowerShell script |
| 3 | named | T1653 Power Settings | ปรับแต่ง Power Settings ของระบบ เพื่อให้เครื่องไม่เข้าสู่ sleep mode |
| 4 | described | T1557 Adversary-in-the-Middle | มีการสกัดข้อมูล credential ระหว่างการสื่อสาร |
| 5 | described | T1119 Automated Collection | ทำการสกัดข้อมูลไฟล์บัญชีรายชื่อลูกค้าและรายการธุรกรรมทางการเงินอย่างเป็นระบบ |
| 6 | named | T1041 Exfiltration Over C2 Channel | ส่งออกจากระบบผ่าน C2 channel ไปยังเซิร์ฟเวอร์ที่อยู่ต่างประเทศ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_047  (source: KV Botnet Activity C0035)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพได้แจ้งความว่าระบบเซิร์ฟเวอร์หลักของบริษัทมีการทำงานผิดปกติ จากการตรวจสอบ log ระบบพบว่ามีการสร้างไฟล์ batch script ในโฟลเดอร์ Startup ของระบบ ซึ่งไฟล์ดังกล่าวจะถูกเรียกทำงานโดยอัตโนมัติทุกครั้งที่ระบบปฏิบัติการเริ่มต้น ต่อมาจากการวิเคราะห์เนื้อหาของ malware พบว่ามีการใช้ Process Discovery เพื่อสำรวจและรวบรวมรายชื่อกระบวนการที่กำลังทำงานในระบบเป้าหมาย จากนั้นผู้โจมตีได้ใช้ Non-Application Layer Protocol ในการสื่อสารกับเซิร์ฟเวอร์ควบคุมโดยข้ามชั้น application layer ที่มีการป้องกันตัวอักษร ทำให้สามารถส่งคำสั่งและรับข้อมูลกลับมาได้อย่างสำเร็จ

*EN:* On 22 February 2569, a private sector information technology company in Bangkok reported abnormal behavior on its primary server system. Upon examining system logs, investigators found that a batch script file had been created in the system's Startup folder, which would be automatically executed every time the operating system started. Subsequently, analysis of the malware revealed the use of Process Discovery to enumerate and collect information about running processes on the target system. The attacker then used Non-Application Layer Protocol to communicate with the command-and-control server, bypassing application layer protections with character filtering, enabling successful command delivery and data exfiltration.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1546 Event Triggered Execution | มีการสร้างไฟล์ batch script ในโฟลเดอร์ Startup ของระบบ ซึ่งไฟล์ดังกล่าวจะถูกเรียกทำงานโดยอัตโนมัติทุกครั้งที่ระบบปฏิบัติการเริ่มต้น |
| 2 | named | T1057 Process Discovery | มีการใช้ Process Discovery เพื่อสำรวจและรวบรวมรายชื่อกระบวนการที่กำลังทำงานในระบบเป้าหมาย |
| 3 | named | T1095 Non-Application Layer Protocol | ผู้โจมตีได้ใช้ Non-Application Layer Protocol ในการสื่อสารกับเซิร์ฟเวอร์ควบคุม |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_048  (source: FunnyDream C0007)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์สำนักงานใหญ่ถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ระบบ Windows ของเซิร์ฟเวอร์ที่ได้รับผลกระทบพบว่าผู้โจมตีได้ทำการเรียกใช้คำสั่ง WMI ผ่านทางสคริปต์เพื่อดำเนินการโค้ดตามต้องการบนเครื่องเป้าหมาย ต่อมาจากการวิเคราะห์ประวัติการเชื่อมต่อเครือข่ายพบว่าผู้โจมตีได้ทำการค้นหาและรวบรวมข้อมูลเกี่ยวกับการเชื่อมต่อเครือข่ายภายในของระบบเพื่อเตรียมการเคลื่อนไหวต่อไป จากนั้นผู้โจมตีได้ใช้เทคนิค Ingress Tool Transfer เพื่อส่งเครื่องมือโจมตีเพิ่มเติมจากเซิร์ฟเวอร์ที่ควบคุมจากระยะไกลมายังเครื่องเป้าหมาย เพื่อเพิ่มความสามารถในการควบคุมและเก็บรวบรวมข้อมูลต่อไป

*EN:* On 22 February 2569, a logistics service company in Samut Prakan Province reported unauthorized access to its headquarters server system. Digital forensic examination of the affected Windows server logs revealed that the attacker executed WMI commands via script to run arbitrary code on the target machine. Subsequently, analysis of network connection history showed the attacker discovered and collected information about internal network connections within the system to prepare for lateral movement. The attacker then employed Ingress Tool Transfer technique to deliver additional attack tools from a remote-controlled server to the target machine in order to enhance control capabilities and facilitate data collection.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1047 Windows Management Instrumentation | ผู้โจมตีได้ทำการเรียกใช้คำสั่ง WMI ผ่านทางสคริปต์เพื่อดำเนินการโค้ดตามต้องการบนเครื่องเป้าหมาย |
| 2 | described | T1049 System Network Connections Discovery | ผู้โจมตีได้ทำการค้นหาและรวบรวมข้อมูลเกี่ยวกับการเชื่อมต่อเครือข่ายภายในของระบบ |
| 3 | named | T1105 Ingress Tool Transfer | ผู้โจมตีได้ใช้เทคนิค Ingress Tool Transfer เพื่อส่งเครื่องมือโจมตีเพิ่มเติมจากเซิร์ฟเวอร์ที่ควบคุมจากระยะไกลมายังเครื่องเป้าหมาย |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_049  (source: Cutting Edge C0029)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการเงินดิจิทัลแห่งหนึ่งในจังหวัดกรุงเทพได้แจ้งความว่าระบบเว็บแอปพลิเคชันของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log server พบว่าผู้โจมตีได้ส่งคำขอ HTTP ที่มีข้อมูล malicious payload ไปยังฟังก์ชัน payment gateway ซึ่งมีช่องโหว่ที่ยังไม่ได้แก้ไข ทำให้ได้รับการยืนยันตัวตนบนระบบ ต่อมาผู้โจมตีทำการ Process Injection เพื่อฉีดโค้ดอันตรายเข้าไปในกระบวนการ system service ที่มีสิทธิ์ระดับสูง เพื่อให้ได้สิทธิ์การเข้าถึงระดับ administrator จากนั้นผู้โจมตีได้สร้างการเชื่อมต่อ reverse tunnel ผ่านการห่อหุ้มข้อมูลสั่งการภายในโปรโตคอล HTTPS ปกติ ทำให้สามารถส่งคำสั่งและรับข้อมูลกลับมาได้โดยไม่ถูกตรวจจับจากระบบ firewall และ intrusion detection system

*EN:* On 22 February 2569, a financial services company in Bangkok reported unauthorized access to its web application system. Log analysis revealed that the attacker sent HTTP requests containing malicious payloads to an unpatched vulnerability in the payment gateway function, gaining authentication on the system. Subsequently, the attacker performed Process Injection to inject malicious code into a high-privilege system service process in order to obtain administrator-level access. The attacker then established a reverse tunnel by encapsulating command-and-control traffic within standard HTTPS protocol, allowing command transmission and data exfiltration without detection by the firewall and intrusion detection system.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ส่งคำขอ HTTP ที่มีข้อมูล malicious payload ไปยังฟังก์ชัน payment gateway ซึ่งมีช่องโหว่ที่ยังไม่ได้แก้ไข |
| 2 | named | T1055 Process Injection | ผู้โจมตีทำการ Process Injection เพื่อฉีดโค้ดอันตรายเข้าไปในกระบวนการ system service ที่มีสิทธิ์ระดับสูง |
| 3 | described | T1572 Protocol Tunneling | ผู้โจมตีได้สร้างการเชื่อมต่อ reverse tunnel ผ่านการห่อหุ้มข้อมูลสั่งการภายในโปรโตคอล HTTPS ปกติ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_050  (source: CostaRicto C0004)

**AUTO-FLAGS: step 3: cue not found verbatim in narrative**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการโทรคมนาคมแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบเซิร์ฟเวอร์ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ External Remote Services ผ่านทาง VPN gateway ของบริษัทที่เปิดให้บริการสาธารณะเพื่อเข้าสู่เครือข่าย ต่อมาผู้โจมตีได้ทำการสแกนและระบุตำแหน่งของบริการเครือข่ายต่างๆ ที่ทำงานอยู่บนพอร์ตต่างๆ เช่น HTTP, SMTP, DNS และ SSH เพื่อหาจุดอ่อนที่สามารถใช้ประโยชน์ได้ จากนั้นผู้โจมตีได้ทำการ Data from Local System โดยดึงข้อมูลไฟล์การกำหนดค่า (configuration files) และข้อมูลผู้ใช้งานจากระบบปฏิบัติการลินุกซ์ รวมถึงการเข้าถึงไฟล์ประวัติการเข้าสู่ระบบ (log files) และข้อมูลประจำตัวที่เก็บไว้ในหน่วยความจำของเซิร์ฟเวอร์

*EN:* On 22 February 2569, a telecommunications service company in Bangkok reported unauthorized access to its server systems. Digital evidence examination revealed that the attacker utilized External Remote Services through the company's publicly exposed VPN gateway to gain network access. Subsequently, the attacker conducted network reconnaissance by identifying and mapping network services running on various ports including HTTP, SMTP, DNS, and SSH to identify exploitable weaknesses. The attacker then performed Data from Local System by extracting configuration files, user account data from the Linux operating system, and accessing login history files and credentials stored in server memory.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1133 External Remote Services | ใช้ External Remote Services ผ่านทาง VPN gateway ของบริษัท |
| 2 | described | T1046 Network Service Discovery | ได้ทำการสแกนและระบุตำแหน่งของบริการเครือข่ายต่างๆ ที่ทำงานอยู่บนพอร์ตต่างๆ เช่น HTTP, SMTP, DNS และ SSH |
| 3 | named | T1005 Data from Local System | ทำการ Data from Local System โดยดึงข้อมูลไฟล์การกำหนดค่า และข้อมูลผู้ใช้งานจากระบบปฏิบัติการลินุกซ์ |

- [ ] ผ่าน / แก้แล้ว
