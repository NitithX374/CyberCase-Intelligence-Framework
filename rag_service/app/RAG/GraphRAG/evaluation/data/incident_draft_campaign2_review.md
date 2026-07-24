# Incident Draft Review Sheet

ตรวจแต่ละข้อ: (1) สำนวนเหมือนสำนวนคดีจริงไหม (2) cue ตรงกับ technique จริงไหม
(3) step แบบ described ไม่เผลอบอกชื่อเทคนิค — แก้ไขในไฟล์ incident_draft.json
แล้วลบข้อที่ใช้ไม่ได้ทิ้ง

## inc_camp2_001  (source: CostaRicto C0004)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log และเครื่องคอมพิวเตอร์ที่ได้รับผลกระทบพบว่า ผู้โจมตีสามารถเชื่อมต่อเข้าสู่ระบบผ่านทาง VPN gateway ของบริษัทที่เปิด port สาธารณะบนอินเทอร์เน็ต ต่อมาผู้โจมตีได้ทำการ network service discovery เพื่อค้นหาเซิร์ฟเวอร์และเซอร์วิสอื่นๆ ที่เชื่อมต่ออยู่ในเครือข่ายภายใน จากนั้นผู้โจมตีได้ทำการเก็บข้อมูลสำคัญจากระบบเครื่องสถานีงาน รวมถึงไฟล์การเงิน ข้อมูลพนักงาน และข้อมูลประจำตัวของผู้ใช้งานจากฮาร์ดดิสก์ของคอมพิวเตอร์ที่ได้เข้าถึงแล้ว

*EN:* On 22 February 2569, a private logistics management company in Samut Prakan Province reported that its server systems had been accessed without authorization. Upon examination of logs and affected computers, investigators found that the attacker was able to connect to the system via the company's VPN gateway, which exposed a public port on the internet. Subsequently, the attacker performed network service discovery to identify servers and other services connected within the internal network. The attacker then collected sensitive data from workstations, including financial records, employee information, and user credentials stored on the compromised computers' hard drives.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1133 External Remote Services | ผู้โจมตีสามารถเชื่อมต่อเข้าสู่ระบบผ่านทาง VPN gateway ของบริษัทที่เปิด port สาธารณะบนอินเทอร์เน็ต |
| 2 | named | T1046 Network Service Discovery | ผู้โจมตีได้ทำการ network service discovery เพื่อค้นหาเซิร์ฟเวอร์และเซอร์วิสอื่นๆ ที่เชื่อมต่ออยู่ในเครือข่ายภายใน |
| 3 | described | T1005 Data from Local System | ผู้โจมตีได้ทำการเก็บข้อมูลสำคัญจากระบบเครื่องสถานีงาน รวมถึงไฟล์การเงิน ข้อมูลพนักงาน และข้อมูลประจำตัวของผู้ใช้งานจากฮาร์ดดิสก์ของคอมพิวเตอร์ที่ได้เข้าถึงแล้ว |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_002  (source: KV Botnet Activity C0035)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพได้แจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกบุกรุก จากการตรวจสอบ log พบว่าผู้โจมตีใช้ Event Triggered Execution เพื่อเพิ่มสิทธิ์ในระบบ โดยทำให้โปรแกรมที่เก็บไว้ในไดเรกทอรี่ Startup ทำงานโดยอัตโนมัติเมื่อเปิดระบบ ต่อมาผู้โจมตีทำการ Process Discovery เพื่อเรียนรู้กระบวนการที่ทำงานอยู่ในเครื่องเป้าหมาย และค้นหาแอปพลิเคชันสำคัญที่กำลังทำงาน จากนั้นจากการตรวจสอบพบว่าผู้โจมตีได้สร้างช่องทางสื่อสารไปยังเซิร์ฟเวอร์ด้านนอกโดยใช้โปรโตคอลระดับต่ำกว่า Application Layer ผ่านการส่งข้อมูล DNS queries และการสร้าง tunnel ด้วยวิธีการที่หลีกเลี่ยงการตรวจสอบของระบบ firewall ทั่วไป

*EN:* On 22 February 2569, an information technology private company in Bangkok reported that the main server system had been breached. From examination of system logs, it was found that the attacker used Event Triggered Execution to escalate privileges by placing a malicious program in the Startup directory to execute automatically upon system boot. Subsequently, the attacker performed Process Discovery to enumerate running processes on the target machine and identify critical applications in operation. Later, investigation revealed that the attacker established a command channel to an external server using a Non-Application Layer Protocol, specifically via DNS queries and tunnel creation methods designed to evade standard firewall inspection mechanisms.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1546 Event Triggered Execution | ผู้โจมตีใช้ Event Triggered Execution เพื่อเพิ่มสิทธิ์ในระบบ โดยทำให้โปรแกรมที่เก็บไว้ในไดเรกทอรี่ Startup ทำงานโดยอัตโนมัติเมื่อเปิดระบบ |
| 2 | named | T1057 Process Discovery | ผู้โจมตีทำการ Process Discovery เพื่อเรียนรู้กระบวนการที่ทำงานอยู่ในเครื่องเป้าหมาย และค้นหาแอปพลิเคชันสำคัญที่กำลังทำงาน |
| 3 | described | T1095 Non-Application Layer Protocol | ผู้โจมตีได้สร้างช่องทางสื่อสารไปยังเซิร์ฟเวอร์ด้านนอกโดยใช้โปรโตคอลระดับต่ำกว่า Application Layer ผ่านการส่งข้อมูล DNS queries และการสร้าง tunnel ด้วยวิธีการที่หลีกเลี่ยงการตรวจสอบของระบบ firewall ทั่วไป |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_003  (source: 2025 Poland Wiper Attacks C0063)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบ Active Directory ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้สร้างงาน scheduled task ชื่อ "SystemUpdate" ที่ทำการรันสคริปต์ PowerShell ทุกวันเวลา 02:00 น. เพื่อรักษาการเข้าถึงระบบ ต่อมาผู้โจมตีใช้เทคนิค Steal Kerberos Tickets เพื่อขโมยบัตร TGT จากเซสชันของผู้ใช้งานสิทธิสูง จากนั้นทำการ Lateral Tool Transfer โดยคัดลอกเครื่องมือ Mimikatz และ PsExec ไปยังเซิร์ฟเวอร์อื่นๆ ในเครือข่าย สุดท้าย ผู้โจมตีได้ทำการบันทึกภาพหน้าจอของเครื่องสำนักงานจำนวนหลายครั้ง เพื่อเก็บข้อมูลรหัสผ่านและข้อมูลลับทางการเงิน

*EN:* On 22 February 2569, a financial services company in Bangkok reported unauthorized access to its Active Directory system. Upon examination of logs, investigators found that the attacker had created a scheduled task named "SystemUpdate" that executed a PowerShell script daily at 02:00 to maintain system persistence. Subsequently, the attacker employed Steal Kerberos Tickets technique to extract TGT tickets from high-privilege user sessions. The attacker then performed Lateral Tool Transfer by copying tools such as Mimikatz and PsExec to other servers within the network. Finally, the attacker conducted Screen Capture operations multiple times on office workstations to collect passwords and sensitive financial data.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1053 Scheduled Task/Job | สร้างงาน scheduled task ชื่อ "SystemUpdate" ที่ทำการรันสคริปต์ PowerShell ทุกวันเวลา 02:00 น. |
| 2 | named | T1558 Steal or Forge Kerberos Tickets | ผู้โจมตีใช้เทคนิค Steal Kerberos Tickets เพื่อขโมยบัตร TGT จากเซสชันของผู้ใช้งานสิทธิสูง |
| 3 | named | T1570 Lateral Tool Transfer | ทำการ Lateral Tool Transfer โดยคัดลอกเครื่องมือ Mimikatz และ PsExec ไปยังเซิร์ฟเวอร์อื่นๆ ในเครือข่าย |
| 4 | described | T1113 Screen Capture | ทำการบันทึกภาพหน้าจอของเครื่องสำนักงานจำนวนหลายครั้ง เพื่อเก็บข้อมูลรหัสผ่านและข้อมูลลับทางการเงิน |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_004  (source: SolarWinds Compromise C0024)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบเซิร์ฟเวอร์ของหน่วยงานประสบความเสียหายจากการโจมตี จากการตรวจสอบ log ระบบพบว่าผู้โจมตีได้ใช้ Windows Management Instrumentation เพื่อดำเนินการสั่งการบนเซิร์ฟเวอร์ที่มี Windows Server 2016 ต่อมาจากการตรวจสอบพยานหลักฐานดิจิทัลพบว่ามีการสร้างบัญชีผู้ใช้งานใหม่ขึ้นมา 2 บัญชี และบัญชีเหล่านี้ถูกใช้งานอย่างต่อเนื่องเพื่อเข้าถึงระบบในเวลาต่างๆ ของวัน จากนั้นผู้โจมตีได้ทำการสำรวจความสัมพันธ์ของโดเมนภายในเครือข่ายองค์กร โดยสืบค้นข้อมูลเกี่ยวกับการเชื่อมต่อระหว่างโดเมนหลักและโดเมนย่อยต่างๆ ผ่านทางคำสั่ง nltest และการตรวจสอบ Active Directory objects

*EN:* On 22 February 2569, an information technology private company in Bangkok reported damage to its server systems from an attack. From system log examination, the attacker was found to have used Windows Management Instrumentation to execute commands on a Windows Server 2016 server. Subsequently, from digital evidence examination, two new user accounts were discovered and these accounts were used continuously to access the system at various times of day. The attacker then conducted reconnaissance of domain relationships within the organization's network, querying information about connections between the primary domain and various subdomains via nltest commands and Active Directory object examination.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1047 Windows Management Instrumentation | ผู้โจมตีได้ใช้ Windows Management Instrumentation เพื่อดำเนินการสั่งการบนเซิร์ฟเวอร์ |
| 2 | described | T1078 Valid Accounts | มีการสร้างบัญชีผู้ใช้งานใหม่ขึ้นมา 2 บัญชี และบัญชีเหล่านี้ถูกใช้งานอย่างต่อเนื่องเพื่อเข้าถึงระบบในเวลาต่างๆ ของวัน |
| 3 | described | T1482 Domain Trust Discovery | ผู้โจมตีได้ทำการสำรวจความสัมพันธ์ของโดเมนภายในเครือข่ายองค์กร โดยสืบค้นข้อมูลเกี่ยวกับการเชื่อมต่อระหว่างโดเมนหลักและโดเมนย่อยต่างๆ ผ่านทางคำสั่ง nltest และการตรวจสอบ Active Directory objects |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_005  (source: C0015 C0015)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการได้แจ้งความว่าระบบเครื่องแม่ข่ายของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ Windows Management Instrumentation เพื่อรันคำสั่งที่เป็นอันตรายบนเครื่องสำนักงานของพนักงานหลายคน ต่อมาจากการวิเคราะห์ activity log บนเซิร์ฟเวอร์พบร่องรอยการโอนไฟล์เครื่องมือ hacking จากเครื่องหนึ่งไปยังเครื่องอื่นในเครือข่ายภายใน จากนั้นผู้โจมตีได้เข้าถึงข้อมูลจากเครื่องแบ่งปันไฟล์เครือข่าย (Network Shared Drive) ซึ่งเก็บเอกสารสัญญาจ้างเหมาและข้อมูลลูกค้า สุดท้าย จากการตรวจสอบ firewall log พบว่าข้อมูลจำนวนมากถูกส่งออกไปนอกเครือข่ายในหลายครั้งเล็กน้อย โดยแต่ละครั้งมีขนาดไฟล์ที่ถูกจำกัดไว้เพื่อหลีกเลี่ยงการตรวจจับ (Data Transfer Size Limits)

*EN:* On 22 February 2569, a private logistics management company in Samut Prakan Province reported unauthorized access to its server system. From log analysis, investigators found that the attacker used Windows Management Instrumentation to execute malicious commands on multiple office workstations. Subsequently, server activity logs revealed traces of hacking tools being transferred from one machine to other machines within the internal network. The attacker then accessed data from the Network Shared Drive containing employment contract documents and customer information. Finally, firewall log examination showed that large amounts of data were exfiltrated outside the network in multiple small transfers, with each file transfer size limited to evade detection.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1047 Windows Management Instrumentation | ผู้โจมตีได้ใช้ Windows Management Instrumentation เพื่อรันคำสั่งที่เป็นอันตรายบนเครื่องสำนักงาน |
| 2 | described | T1570 Lateral Tool Transfer | การโอนไฟล์เครื่องมือ hacking จากเครื่องหนึ่งไปยังเครื่องอื่นในเครือข่ายภายใน |
| 3 | named | T1039 Data from Network Shared Drive | ผู้โจมตีได้เข้าถึงข้อมูลจากเครื่องแบ่งปันไฟล์เครือข่าย (Network Shared Drive) |
| 4 | named | T1030 Data Transfer Size Limits | แต่ละครั้งมีขนาดไฟล์ที่ถูกจำกัดไว้เพื่อหลีกเลี่ยงการตรวจจับ (Data Transfer Size Limits) |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_006  (source: Operation Wocao C0014)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานครแจ้งความว่าระบบเซิร์ฟเวอร์ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีใช้ Native API เพื่อดำเนินการคำสั่งระบบบนเครื่องของเหยื่อ ต่อมาจากการวิเคราะห์พยานหลักฐานดิจิทัล พบร่องรอยการส่งข้อความแจ้งเตือนเข้าสู่อุปกรณ์มือถือของผู้ใช้งาน แล้วหลังจากนั้นการยืนยันตัวตนแบบหลายชั้นของผู้ใช้งานถูกบัญชาการทำให้ไม่สำเร็จ และผู้โจมตีได้เข้าถึงบัญชีผู้ใช้งานสำเร็จ จากนั้นจากการสอบสวนพบว่าผู้โจมตีทำการค้นหาอุปกรณ์ต่อพ่วงที่เชื่อมต่ออยู่กับเครือข่ายภายในของบริษัท เช่น USB storage device และ network printer ที่มีความสามารถในการเก็บข้อมูล สุดท้ายจากการตรวจสอบ log ของเซิร์ฟเวอร์พบว่าผู้โจมตีทำการคัดลอกเครื่องมือการโจมตีไปยังเครื่องอื่นภายในเครือข่าย และใช้เครื่องมือเหล่านั้นในการเก็บรวบรวมข้อมูลลูกค้าและบัญชีการเงินจำนวนมากมายอย่างเป็นระบบ

*EN:* On 22 February 2569, a private financial services company in Bangkok reported unauthorized access to its server systems. Digital forensic examination of logs revealed that the attacker used Native API to execute system commands on the victim's machine. Subsequently, analysis of digital evidence showed traces of alert notifications sent to the user's mobile device, after which the user's multi-factor authentication failed and the attacker successfully gained account access. Investigation then discovered that the attacker searched for peripheral devices connected to the company's internal network, such as USB storage devices and network printers with data storage capabilities. Finally, server log analysis revealed that the attacker copied attack tools to other machines within the network and used those tools to systematically collect large volumes of customer data and financial account information.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1106 Native API | ผู้โจมตีใช้ Native API เพื่อดำเนินการคำสั่งระบบบนเครื่องของเหยื่อ |
| 2 | described | T1111 Multi-Factor Authentication Interception | พบร่องรอยการส่งข้อความแจ้งเตือนเข้าสู่อุปกรณ์มือถือของผู้ใช้งาน แล้วหลังจากนั้นการยืนยันตัวตนแบบหลายชั้นของผู้ใช้งานถูกบัญชาการทำให้ไม่สำเร็จ และผู้โจมตีได้เข้าถึงบัญชีผู้ใช้งานสำเร็จ |
| 3 | described | T1120 Peripheral Device Discovery | ผู้โจมตีทำการค้นหาอุปกรณ์ต่อพ่วงที่เชื่อมต่ออยู่กับเครือข่ายภายในของบริษัท เช่น USB storage device และ network printer ที่มีความสามารถในการเก็บข้อมูล |
| 4 | described | T1570 Lateral Tool Transfer | ผู้โจมตีทำการคัดลอกเครื่องมือการโจมตีไปยังเครื่องอื่นภายในเครือข่าย |
| 5 | described | T1119 Automated Collection | ใช้เครื่องมือเหล่านั้นในการเก็บรวบรวมข้อมูลลูกค้าและบัญชีการเงินจำนวนมากมายอย่างเป็นระบบ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_007  (source: ArcaneDoor C0046)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนแห่งหนึ่งในจังหวัดสมุทรปราการที่ประกอบธุรกิจเกี่ยวกับการจัดการสินค้าคลังสินค้า แจ้งความว่าระบบเซิร์ฟเวอร์หลักของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ส่งคำสั่งผ่าน PowerShell script เพื่อดำเนินการต่างๆ บนระบบ ต่อมาจากการวิเคราะห์พยานหลักฐานดิจิทัลพบว่าผู้โจมตีได้ทำการ Modify Authentication Process โดยเพิ่มบัญชีผู้ใช้ลับและแก้ไขการตั้งค่า SSH key เพื่อรักษาการเข้าถึงระยะยาว จากนั้นผู้โจมตีได้ฉีดโค้ดเนื้อหาลงในกระบวนการ svchost.exe เพื่อให้ได้สิทธิ์ระดับสูงและหลีกเลี่ยงการตรวจจับ สุดท้ายผู้โจมตีได้ดำเนินการสอบสวนข้อมูลระบบ ได้แก่ รายชื่อผู้ใช้ที่มีสิทธิ์ เวอร์ชันระบบปฏิบัติการ และการกำหนดค่าเครือข่าย ผู้โจมตีได้วางตัวอยู่ระหว่างการสื่อสารระหว่างเซิร์ฟเวอร์ฐานข้อมูลและเซิร์ฟเวอร์แอปพลิเคชัน เพื่อจับภาพการรับส่งข้อมูลลูกค้าและข้อมูลการสั่งซื้อ และทำการส่งข้อมูลที่ขโมยได้ออกจากระบบผ่านการเชื่อมต่อ HTTPS ที่เข้ารหัสไปยังเซิร์ฟเวอร์ภายนอกโดยอัตโนมัติทุกชั่วโมง

*EN:* On 22 February 2569, a private company engaged in warehouse inventory management in Samut Prakan Province reported unauthorized access to its primary server system. Log examination revealed that the attacker had sent commands via PowerShell script to execute various operations on the system. Subsequent digital forensic analysis discovered that the attacker had performed Modify Authentication Process by adding a hidden user account and altering SSH key configurations to maintain persistent access. The attacker then injected code into the svchost.exe process to obtain elevated privileges and evade detection. Finally, the attacker conducted System Information Discovery including user account lists with elevated permissions, operating system version, and network configuration details. The attacker positioned itself between communications of the database server and application server to capture customer data and purchase order information, and exfiltrated the stolen data through an encrypted HTTPS connection to an external server automatically every hour.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1059 Command and Scripting Interpreter | ผู้โจมตีได้ส่งคำสั่งผ่าน PowerShell script เพื่อดำเนินการต่างๆ บนระบบ |
| 2 | named | T1556 Modify Authentication Process | ผู้โจมตีได้ทำการ Modify Authentication Process โดยเพิ่มบัญชีผู้ใช้ลับและแก้ไขการตั้งค่า SSH key |
| 3 | described | T1055 Process Injection | ผู้โจมตีได้ฉีดโค้ดเนื้อหาลงในกระบวนการ svchost.exe เพื่อให้ได้สิทธิ์ระดับสูง |
| 4 | named | T1082 System Information Discovery | ผู้โจมตีได้ดำเนินการสอบสวนข้อมูลระบบ ได้แก่ รายชื่อผู้ใช้ที่มีสิทธิ์ เวอร์ชันระบบปฏิบัติการ และการกำหนดค่าเครือข่าย |
| 5 | described | T1557 Adversary-in-the-Middle | ผู้โจมตีได้วางตัวอยู่ระหว่างการสื่อสารระหว่างเซิร์ฟเวอร์ฐานข้อมูลและเซิร์ฟเวอร์แอปพลิเคชัน เพื่อจับภาพการรับส่งข้อมูลลูกค้าและข้อมูลการสั่งซื้อ |
| 6 | described | T1020 Automated Exfiltration | ทำการส่งข้อมูลที่ขโมยได้ออกจากระบบผ่านการเชื่อมต่อ HTTPS ที่เข้ารหัสไปยังเซิร์ฟเวอร์ภายนอกโดยอัตโนมัติทุกชั่วโมง |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_008  (source: C0027 C0027)

**AUTO-FLAGS: step 6: described cue names the technique (Proxy)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบ Windows server ของแผนกบัญชีถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีใช้ Windows Management Instrumentation เพื่อดำเนินการคำสั่งจากระยะไกลบนเครื่องเซิร์ฟเวอร์ ต่อมา ผู้โจมตีได้สร้างการเชื่อมต่อผ่านบริการ VPN ที่มีอยู่ในระบบเพื่อรักษาการเข้าถึงและหลีกเลี่ยงการตรวจสอบ จากนั้น ผู้โจมตีได้ส่งคำขอ multi-factor authentication ปลอมไปยังอุปกรณ์มือถือของพนักงานหลายคน เพื่อให้ได้รับข้อมูลประจำตัว สุดท้าย ผู้โจมตีใช้เครื่องมือ network scanning เพื่อค้นหาเซิร์ฟเวอร์ cloud storage ที่เชื่อมต่อในเครือข่ายภายใน และดึงข้อมูลบัญชีรายงานจำนวนมากจากระบบ Google Drive ที่บริษัทใช้งาน ข้อมูลที่ดึงออกมาได้ถูกส่งออกผ่าน proxy server ที่อยู่นอกประเทศ เพื่อซ่อนแหล่งที่มาของการโจมตี

*EN:* On 22 February 2569, a financial services company in Bangkok reported unauthorized access to the accounting department's Windows server. Digital forensic examination of logs revealed that the attacker used Windows Management Instrumentation to execute remote commands on the server. Subsequently, the attacker established persistence by configuring the existing VPN service to maintain access and evade monitoring. The attacker then sent fraudulent multi-factor authentication prompts to the mobile devices of multiple employees to obtain their credentials. Finally, the attacker deployed network scanning tools to discover cloud storage servers connected to the internal network and extracted a large volume of accounting records from the Google Drive system used by the company. The extracted data was exfiltrated through an overseas proxy server to conceal the origin of the attack.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1047 Windows Management Instrumentation | ผู้โจมตีใช้ Windows Management Instrumentation เพื่อดำเนินการคำสั่งจากระยะไกล |
| 2 | described | T1133 External Remote Services | ผู้โจมตีได้สร้างการเชื่อมต่อผ่านบริการ VPN ที่มีอยู่ในระบบเพื่อรักษาการเข้าถึงและหลีกเลี่ยงการตรวจสอบ |
| 3 | described | T1621 Multi-Factor Authentication Request Generation | ผู้โจมตีได้ส่งคำขอ multi-factor authentication ปลอมไปยังอุปกรณ์มือถือของพนักงานหลายคน เพื่อให้ได้รับข้อมูลประจำตัว |
| 4 | named | T1046 Network Service Discovery | ผู้โจมตีใช้เครื่องมือ network scanning เพื่อค้นหาเซิร์ฟเวอร์ cloud storage |
| 5 | named | T1530 Data from Cloud Storage | ดึงข้อมูลบัญชีรายงานจำนวนมากจากระบบ Google Drive |
| 6 | described | T1090 Proxy | ข้อมูลที่ดึงออกมาได้ถูกส่งออกผ่าน proxy server ที่อยู่นอกประเทศ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_009  (source: Operation Dust Storm C0016)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพฯ ได้แจ้งความว่าพบการเข้าถึงระบบเซิร์ฟเวอร์โดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าเริ่มแรกพนักงานของบริษัทได้เข้าชมเว็บไซต์ที่ผ่าน drive-by compromise ซึ่งเป็นเว็บไซต์ที่ดูเหมือนถูกต้องทั่วไป จากนั้นเบราว์เซอร์ของพนักงานเกิดการทำงานผิดปกติและมีการดาวน์โหลดไฟล์ที่มีรหัสที่ถูกออกแบบมาเพื่อใช้ประโยชน์จากช่องโหว่ในแอปพลิเคชันไคลเอนต์ ส่งผลให้มีการ execute code ที่ไม่ได้อนุญาต ต่อมาจากการวิเคราะห์ memory dump และ registry พบว่าระบบถูกใช้เพื่อทำ Software discovery โดยการสแกนโปรแกรมที่ติดตั้งและเวอร์ชันต่างๆ บนเครื่องเพื่อหาจุดอ่อน สุดท้าย log network ระบุว่าระบบคอมพิวเตอร์ที่ติดเชื้อได้ทำการ Dynamic resolution เพื่อเชื่อมต่อกับ command-and-control server โดยใช้การแปลงชื่อโดเมนแบบไดนามิก

*EN:* On 22 February 2569, a private information technology company in Bangkok reported unauthorized access to its server system. Analysis of logs revealed that an employee initially visited a website that had undergone drive-by compromise, appearing legitimate at first glance. Subsequently, the employee's browser malfunctioned and downloaded a file containing code specifically designed to exploit vulnerabilities in client applications, resulting in unauthorized code execution. Later, analysis of memory dumps and registry entries indicated the system was used to conduct Software discovery by scanning installed programs and their versions to identify weaknesses. Finally, network logs confirmed that the infected computer performed Dynamic resolution to connect to a command-and-control server using dynamic domain name translation.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1189 Drive-by Compromise | เข้าชมเว็บไซต์ที่ผ่าน drive-by compromise |
| 2 | described | T1203 Exploitation for Client Execution | มีการดาวน์โหลดไฟล์ที่มีรหัสที่ถูกออกแบบมาเพื่อใช้ประโยชน์จากช่องโหว่ในแอปพลิเคชันไคลเอนต์ ส่งผลให้มีการ execute code ที่ไม่ได้อนุญาต |
| 3 | named | T1518 Software Discovery | ทำ Software discovery โดยการสแกนโปรแกรมที่ติดตั้งและเวอร์ชันต่างๆ |
| 4 | named | T1568 Dynamic Resolution | ทำการ Dynamic resolution เพื่อเชื่อมต่อกับ command-and-control server |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_010  (source: SharePoint ToolShell Exploitation C0058)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทผู้ให้บริการเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพมหานคร ได้รับแจ้งจากทีมความปลอดภัยว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ทั้งระบบพบว่าผู้โจมตีได้ใช้ Exploit Public-Facing Application ผ่านช่องโหว่ใน web portal ที่เปิดให้บริการสาธารณะ เพื่อทำการบุกรุกเข้าสู่เซิร์ฟเวอร์ Windows ของหน่วยงาน ต่อมาจากการวิเคราะห์ event log พบร่องรอยการเรียกใช้ WMI objects ผ่านทาง PowerShell ที่มีการสร้างและรันคำสั่งระยะไกลเพื่อติดตั้งเครื่องมือเพิ่มเติม จากนั้นผู้โจมตีได้ทำการ Modify Registry ในส่วน Run keys และ Startup folders เพื่อให้เครื่องมือโจมตีทำงานอยู่ตลอดเวลาแม้ว่าระบบจะถูกรีสตาร์ท สุดท้ายผู้เสียหายค้นพบว่าผู้โจมตีได้ใช้ System Owner/User Discovery เพื่อรวบรวมข้อมูลบัญชีผู้ใช้ในระบบ และจากการติดตามเพิ่มเติมพบร่องรอยการ copy เครื่องมือโจมตีไปยังเซิร์ฟเวอร์อื่นๆ ในเครือข่ายเพื่อลดความสามารถในการตรวจจับและขยายการควบคุมในสภาพแวดล้อมเครือข่ายโดยรวม

*EN:* On 22 February 2569, an information technology service company in Bangkok received notification from its security team that the primary server system had been accessed without authorization. Upon examination of system logs, investigators found that the attacker had exploited a Public-Facing Application vulnerability in the publicly accessible web portal to gain initial entry to the organization's Windows server. Subsequently, analysis of event logs revealed traces of WMI object invocation through PowerShell with remote command execution and installation of additional tools. The attacker then modified Registry entries in Run keys and Startup folders to ensure persistence of the attack tools across system restarts. Further investigation disclosed that the attacker had conducted System Owner/User Discovery to enumerate user accounts within the system, and follow-up analysis identified evidence of tool transfer to other servers within the network to reduce detection and expand control across the broader network environment.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ใช้ Exploit Public-Facing Application ผ่านช่องโหว่ใน web portal ที่เปิดให้บริการสาธารณะ |
| 2 | described | T1047 Windows Management Instrumentation | จากการวิเคราะห์ event log พบร่องรอยการเรียกใช้ WMI objects ผ่านทาง PowerShell ที่มีการสร้างและรันคำสั่งระยะไกล |
| 3 | named | T1112 Modify Registry | ผู้โจมตีได้ทำการ Modify Registry ในส่วน Run keys และ Startup folders |
| 4 | named | T1033 System Owner/User Discovery | ผู้โจมตีได้ใช้ System Owner/User Discovery เพื่อรวบรวมข้อมูลบัญชีผู้ใช้ในระบบ |
| 5 | described | T1570 Lateral Tool Transfer | พบร่องรอยการ copy เครื่องมือโจมตีไปยังเซิร์ฟเวอร์อื่นๆ ในเครือข่าย |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_011  (source: Operation Dream Job C0022)

**AUTO-FLAGS: step 6: described cue names the technique (Exfiltration Over C2 Channel)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการขนส่งแห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้เรียกใช้ Windows API function โดยตรงเพื่อสร้างกระบวนการใหม่ในระบบเป้าหมาย ต่อมาผู้โจมตีทำการ Brute Force บัญชีผู้ใช้งาน โดยพยายามลองชุดรหัสผ่านหลายชุดจนกว่าจะเข้าสู่ระบบได้สำเร็จ จากนั้นผู้โจมตีได้ค้นหาและแสดงรายการไฟล์และโฟลเดอร์ในไดรเวอร์ C: และ D: เพื่อค้นหาข้อมูลที่มีค่า ต่อมาผู้โจมตีส่งอีเมลหลอกลวงไปยังพนักงานคนอื่นในองค์กร โดยใช้ที่อยู่อีเมลของผู้ดูแลระบบที่แท้จริงเพื่อให้พนักงานคนอื่นเปิดไฟล์แนบที่มีมัลแวร์ ซึ่งส่งผลให้ผู้โจมตีสามารถเข้าถึงบัญชีเพิ่มเติมได้ สุดท้ายผู้โจมตีทำการ Data from Local System โดยคัดลอกฐานข้อมูลลูกค้าและเอกสารสัญญาไปยังโฟลเดอร์ชั่วคราว จากนั้นส่งข้อมูลดังกล่าวออกจากเครือข่ายผ่าน Exfiltration Over C2 Channel ไปยังเซิร์ฟเวอร์ที่ผู้โจมตีควบคุมอยู่

*EN:* On 22 February 2569, a private transportation company in Samut Prakan Province reported unauthorized access to its server system. Upon examination of the logs, investigators found that the attacker invoked Windows API functions directly to create new processes on the target system. Subsequently, the attacker conducted Brute Force attacks on user accounts by attempting multiple password combinations until gaining successful access. The attacker then enumerated files and directories on drives C: and D: to locate valuable data. Later, the attacker sent Internal Spearphishing emails to other employees using the genuine administrator's email address, causing them to open malware-laden attachments, which enabled the attacker to compromise additional accounts. Finally, the attacker performed Data from Local System by copying customer databases and contract documents to a temporary folder, then exfiltrated this data over an Exfiltration Over C2 Channel to a server under the attacker's control.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1106 Native API | ผู้โจมตีได้เรียกใช้ Windows API function โดยตรงเพื่อสร้างกระบวนการใหม่ในระบบเป้าหมาย |
| 2 | named | T1110 Brute Force | ผู้โจมตีทำการ Brute Force บัญชีผู้ใช้งาน โดยพยายามลองชุดรหัสผ่านหลายชุดจนกว่าจะเข้าสู่ระบบได้สำเร็จ |
| 3 | described | T1083 File and Directory Discovery | ผู้โจมตีได้ค้นหาและแสดงรายการไฟล์และโฟลเดอร์ในไดรเวอร์ C: และ D: เพื่อค้นหาข้อมูลที่มีค่า |
| 4 | named | T1534 Internal Spearphishing | ผู้โจมตีส่งอีเมลหลอกลวงไปยังพนักงานคนอื่นในองค์กร โดยใช้ที่อยู่อีเมลของผู้ดูแลระบบที่แท้จริง |
| 5 | named | T1005 Data from Local System | ผู้โจมตีทำการ Data from Local System โดยคัดลอกฐานข้อมูลลูกค้าและเอกสารสัญญาไปยังโฟลเดอร์ชั่วคราว |
| 6 | described | T1041 Exfiltration Over C2 Channel | ส่งข้อมูลดังกล่าวออกจากเครือข่ายผ่าน Exfiltration Over C2 Channel ไปยังเซิร์ฟเวอร์ที่ผู้โจมตีควบคุมอยู่ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_012  (source: Salesforce Data Exfiltration C0059)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการท่องเที่ยวแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบ CRM ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ทำการตั้งค่าการเชื่อมต่อกับ Google Workspace และ Slack API เพื่อให้สามารถเข้าถึงระบบได้อย่างต่อเนื่องแม้ว่าจะมีการเปลี่ยนรหัสผ่านก็ตาม ต่อมาจากการสอบสวนพบร่องรอยของการค้นหาไฟล์และโฟลเดอร์ในเซิร์ฟเวอร์ โดยมีการสแกน directory ทั้งหมดเพื่อค้นหาไฟล์ที่มีข้อมูลลูกค้าและสัญญาทางการค้า จากนั้นผู้โจมตีได้ทำการส่งออกข้อมูลจำนวนมากโดยใช้ Automated Exfiltration ผ่านทาง cloud storage ที่ตั้งค่าไว้ โดยข้อมูลที่ถูกส่งออกรวมถึงรายชื่อลูกค้า 8,500 รายและรายละเอียดการจองทั้งหมด

*EN:* On 22 February 2569, a tourism services company in Bangkok province reported unauthorized access to its CRM system. Log examination revealed that the attacker had configured integration with Google Workspace and Slack API to maintain persistent access despite password changes. Subsequently, investigation found traces of file and directory scanning on the server, with comprehensive directory traversal to locate customer data files and commercial contracts. The attacker then performed automated exfiltration of large volumes of data via configured cloud storage, resulting in the extraction of 8,500 customer records and complete booking details.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1671 Cloud Application Integration | ทำการตั้งค่าการเชื่อมต่อกับ Google Workspace และ Slack API เพื่อให้สามารถเข้าถึงระบบได้อย่างต่อเนื่อง |
| 2 | described | T1083 File and Directory Discovery | การค้นหาไฟล์และโฟลเดอร์ในเซิร์ฟเวอร์ โดยมีการสแกน directory ทั้งหมด |
| 3 | named | T1020 Automated Exfiltration | ใช้ Automated Exfiltration ผ่านทาง cloud storage ที่ตั้งค่าไว้ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_013  (source: FunnyDream C0007)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log และหลักฐานดิจิทัลพบว่าผู้โจมตีได้ใช้ Windows Management Instrumentation ในการเรียกใช้คำสั่งระบบอย่างผิดปกติบนเซิร์ฟเวอร์หลัก ต่อมาจากการวิเคราะห์ traffic และ event log พบร่องรอยของการสแกนและการเชื่อมต่อไปยังอุปกรณ์อื่นๆ ในเครือข่ายภายในเพื่อรวบรวมข้อมูลเกี่ยวกับโครงสร้างระบบและเครื่องมือที่มีอยู่ จากนั้นระบบตรวจจับการดาวน์โหลดไฟล์ executable ขนาดใหญ่จากแหล่งภายนอกไปยังเซิร์ฟเวอร์ผ่านช่องทางการสื่อสารที่ไม่ปกติ ซึ่งถูกระบุว่าเป็นเครื่องมือสำหรับการควบคุมระบบจากระยะไกล

*EN:* On 22 February 2569, a private logistics management company in Samut Prakan Province reported unauthorized access to its server system. Digital forensic examination and log analysis revealed that the attacker executed system commands using Windows Management Instrumentation on the primary server in an anomalous manner. Subsequently, analysis of traffic and event logs identified traces of scanning and connections to other devices within the internal network to gather information about system architecture and available tools. The system then detected the download of a large executable file from an external source to the server through an unusual communication channel, identified as a remote control tool.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1047 Windows Management Instrumentation | ผู้โจมตีได้ใช้ Windows Management Instrumentation ในการเรียกใช้คำสั่งระบบอย่างผิดปกติบนเซิร์ฟเวอร์หลัก |
| 2 | described | T1018 Remote System Discovery | พบร่องรอยของการสแกนและการเชื่อมต่อไปยังอุปกรณ์อื่นๆ ในเครือข่ายภายในเพื่อรวบรวมข้อมูลเกี่ยวกับโครงสร้างระบบและเครื่องมือที่มีอยู่ |
| 3 | described | T1105 Ingress Tool Transfer | ระบบตรวจจับการดาวน์โหลดไฟล์ executable ขนาดใหญ่จากแหล่งภายนอกไปยังเซิร์ฟเวอร์ผ่านช่องทางการสื่อสารที่ไม่ปกติ ซึ่งถูกระบุว่าเป็นเครื่องมือสำหรับการควบคุมระบบจากระยะไกล |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_014  (source: C0018 C0018)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทผลิตชิ้นส่วนอิเล็กทรอนิกส์แห่งหนึ่งในจังหวัดระยอง แจ้งความว่าระบบเซิร์ฟเวอร์ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ประโยชน์จากช่องโหว่ในแอปพลิเคชันเว็บสาธารณะของบริษัท (Portal HR ที่เปิดให้บริหารจัดการเอกสารพนักงาน) เพื่อเข้าสู่ระบบเครือข่ายภายใน ต่อมาจากการวิเคราะห์ memory dump และ process logs พบหลักฐานการรันคำสั่ง PowerShell ผ่าน WMI ที่ดำเนินการสแกนการเชื่อมต่อเครือข่าย ค้นหาเซิร์ฟเวอร์อื่นๆ และระบุบริการที่ทำงานอยู่ในสภาพแวดล้อมภายใน จากนั้นผู้โจมตีได้ทำการถ่ายโอน executable file ของเครื่องมือ port scanner และ credential harvester ไปยังเครื่องคอมพิวเตอร์เซิร์ฟเวอร์ฐานข้อมูลอื่นๆ ผ่านทาง SMB share ที่ไม่ได้รักษาความปลอดภัย สุดท้ายจากการตรวจสอบพบว่าผู้โจมตีได้สร้างการเชื่อมต่อ command-and-control ผ่าน non-standard port 8834 ไปยังเซิร์ฟเวอร์ที่อยู่นอกประเทศ และดำเนินการเข้ารหัสไฟล์ข้อมูลทั้งหมดในโฟลเดอร์ shared drive และไฟล์ฐานข้อมูล SAP ของบริษัท ทำให้ระบบหยุดทำงาน

*EN:* On 22 February 2569, an electronics component manufacturing company in Rayong Province reported unauthorized access to its server system. Log analysis revealed the attacker exploited a vulnerability in the company's public-facing web application (HR Portal used for employee document management) to gain initial network access. Subsequently, memory dumps and process logs showed evidence of PowerShell commands executed via WMI that performed network scanning, identified other servers, and enumerated running services within the internal environment. The attacker then transferred executable tools for port scanning and credential harvesting to other database server computers via unprotected SMB shares. Finally, investigation confirmed the attacker established command-and-control communication through non-standard port 8834 to an overseas server and encrypted all data files in the company's shared drives and SAP database files, causing system outage.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ใช้ประโยชน์จากช่องโหว่ในแอปพลิเคชันเว็บสาธารณะของบริษัท (Portal HR ที่เปิดให้บริหารจัดการเอกสารพนักงาน) เพื่อเข้าสู่ระบบเครือข่ายภายใน |
| 2 | described | T1047 Windows Management Instrumentation | จากการวิเคราะห์ memory dump และ process logs พบหลักฐานการรันคำสั่ง PowerShell ผ่าน WMI ที่ดำเนินการสแกนการเชื่อมต่อเครือข่าย |
| 3 | described | T1046 Network Service Discovery | ค้นหาเซิร์ฟเวอร์อื่นๆ และระบุบริการที่ทำงานอยู่ในสภาพแวดล้อมภายใน |
| 4 | described | T1570 Lateral Tool Transfer | ผู้โจมตีได้ทำการถ่ายโอน executable file ของเครื่องมือ port scanner และ credential harvester ไปยังเครื่องคอมพิวเตอร์เซิร์ฟเวอร์ฐานข้อมูลอื่นๆ ผ่านทาง SMB share ที่ไม่ได้รักษาความปลอดภัย |
| 5 | named | T1571 Non-Standard Port | ผู้โจมตีได้สร้างการเชื่อมต่อ command-and-control ผ่าน non-standard port 8834 ไปยังเซิร์ฟเวอร์ที่อยู่นอกประเทศ |
| 6 | described | T1486 Data Encrypted for Impact | ดำเนินการเข้ารหัสไฟล์ข้อมูลทั้งหมดในโฟลเดอร์ shared drive และไฟล์ฐานข้อมูล SAP ของบริษัท ทำให้ระบบหยุดทำงาน |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_015  (source: Cutting Edge C0029)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบเซิร์ฟเวอร์หลักของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ Command and Scripting Interpreter เพื่อดำเนินการคำสั่งบนระบบปฏิบัติการ ต่อมาผู้โจมตีได้สร้างกลไกการติดต่อกลับไปยังเซิร์ฟเวอร์ภายนอกโดยใช้ Traffic Signaling เพื่อรักษาการเข้าถึงอย่างต่อเนื่อง จากนั้นจากการวิเคราะห์หน่วยความจำและ process list พบหลักฐานว่าโปรแกรมอันชอบธรรมได้ถูกแทรกด้วยโค้ดเนื้อหาอันตรายเข้าไปทำงานในบริบทสิทธิ์สูง สุดท้ายผู้โจมตีได้ดำเนินการคิวรี่ข้อมูลเกี่ยวกับสถาปัตยกรรมระบบและโครงสร้างเครือข่าย รวมถึงการสำรวจและสกัดข้อมูลบัญชีผู้ใช้และไฟล์ที่เก็บข้อมูลสำคัญจากฮาร์ดดิสก์ เพื่อส่งไปยังเซิร์ฟเวอร์ควบคุมภายนอกผ่านโปรโตคอลระดับเครือข่ายที่ไม่ใช่ application layer ตามปกติ

*EN:* On 22 February 2569, a logistics services company in Samut Prakan Province reported that its primary server system was accessed without authorization. From log analysis, it was found that the attacker used Command and Scripting Interpreter to execute commands on the operating system. Subsequently, the attacker established a callback mechanism to an external server using Traffic Signaling to maintain persistent access. Analysis of memory and process lists then revealed evidence that a legitimate program had been injected with malicious code executing in elevated privilege context. Finally, the attacker conducted queries on system architecture and network structure information, and extracted user account data and files containing sensitive information from the hard disk, transmitting them to an external control server via non-standard network layer protocol.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1059 Command and Scripting Interpreter | ใช้ Command and Scripting Interpreter เพื่อดำเนินการคำสั่งบนระบบปฏิบัติการ |
| 2 | named | T1205 Traffic Signaling | สร้างกลไกการติดต่อกลับไปยังเซิร์ฟเวอร์ภายนอกโดยใช้ Traffic Signaling เพื่อรักษาการเข้าถึงอย่างต่อเนื่อง |
| 3 | described | T1055 Process Injection | โปรแกรมอันชอบธรรมได้ถูกแทรกด้วยโค้ดเนื้อหาอันตรายเข้าไปทำงานในบริบทสิทธิ์สูง |
| 4 | described | T1082 System Information Discovery | ดำเนินการคิวรี่ข้อมูลเกี่ยวกับสถาปัตยกรรมระบบและโครงสร้างเครือข่าย |
| 5 | described | T1005 Data from Local System | สกัดข้อมูลบัญชีผู้ใช้และไฟล์ที่เก็บข้อมูลสำคัญจากฮาร์ดดิสก์ |
| 6 | named | T1095 Non-Application Layer Protocol | ส่งไปยังเซิร์ฟเวอร์ควบคุมภายนอกผ่านโปรโตคอลระดับเครือข่ายที่ไม่ใช่ application layer ตามปกติ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_016  (source: RedPenguin C0056)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนแห่งหนึ่งในจังหวัดสมุทรปราการ ซึ่งประกอบธุรกิจด้านเทคโนโลยีสารสนเทศ ได้รับแจ้งเบาะแสจากผู้เสียหายว่ามีกิจกรรมที่ผิดปกติเกิดขึ้นบนเซิร์ฟเวอร์ระบบบัญชีผู้ใช้งาน จากการตรวจสอบ log พบว่าบัญชีพนักงานชื่อ Somchai.Pattana ซึ่งเป็นพนักงานสายสนับสนุนเทคนิค ถูกใช้งานเข้าสู่ระบบจากที่ตั้งหลายแห่งในช่วงเวลาที่ผิดปกติ ต่อมาจากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าผู้โจมตีได้ทำการ Process Injection เข้าไปในโปรเซสของ Windows Service เพื่อยกระดับสิทธิการเข้าถึงระบบ จากนั้นผู้โจมตีได้ติดตั้งเครื่องมือ Network Sniffing บนเซิร์ฟเวอร์เพื่อจับแพ็กเก็ตข้อมูลและเก็บรวบรวมข้อมูลการเข้าสู่ระบบของผู้ใช้งานอื่น ๆ ที่ผ่านไปบนเครือข่ายภายใน

*EN:* On 22 February 2569, a private information technology company in Samut Prakan Province received a tip from the victim reporting unusual activity on the user account management server. From log examination, the employee account Somchai.Pattana, a technical support staff member, was found to be accessed from multiple locations at unusual times. Subsequently, from digital forensic examination, the attacker was found to have performed Process Injection into a Windows Service process in order to escalate system access privileges. Thereafter, the attacker installed a Network Sniffing tool on the server to capture packet data and harvest login credentials of other users passing through the internal network.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | บัญชีพนักงานชื่อ Somchai.Pattana ซึ่งเป็นพนักงานสายสนับสนุนเทคนิค ถูกใช้งานเข้าสู่ระบบจากที่ตั้งหลายแห่งในช่วงเวลาที่ผิดปกติ |
| 2 | named | T1055 Process Injection | ผู้โจมตีได้ทำการ Process Injection เข้าไปในโปรเซสของ Windows Service เพื่อยกระดับสิทธิการเข้าถึงระบบ |
| 3 | named | T1040 Network Sniffing | ผู้โจมตีได้ติดตั้งเครื่องมือ Network Sniffing บนเซิร์ฟเวอร์เพื่อจับแพ็กเก็ตข้อมูลและเก็บรวบรวมข้อมูลการเข้าสู่ระบบของผู้ใช้งานอื่น ๆ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_017  (source: RedDelta Modified PlugX Infection Chain Operations C0047)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนแห่งหนึ่งในจังหวัดสมุทรปราการที่ประกอบธุรกิจด้านการออกแบบกราฟิกส์ แจ้งความเสียหายต่อสำนักงานตำรวจ โดยพบว่าระบบคอมพิวเตอร์ของพนักงานถูกติดตั้ง malware หลังจากเปิดไฟล์เอกสาร PDF ที่ได้รับมาทางอีเมล ซึ่งไฟล์ดังกล่าวใช้ Exploitation for Client Execution เพื่อให้โค้ดอันตรายทำงานในระบบของผู้เสียหาย จากการตรวจสอบ log พบว่า ต่อมาโปรแกรมร้ายได้ทำการเรียกคำสั่งเพื่อสอบถามข้อมูลเกี่ยวกับเวอร์ชัน Windows ชื่อเครื่องคอมพิวเตอร์ ชื่อผู้ใช้งาน และรายชื่อซอฟต์แวร์ที่ติดตั้งในระบบ จากนั้นเครื่องดังกล่าวได้ส่งข้อมูลกลับไปยังเซิร์ฟเวอร์ควบคุมผ่านการเชื่อมต่อ raw socket protocol ที่ไม่ใช่ HTTP หรือ HTTPS ซึ่งแตกต่างจากการสื่อสารแบบปกติของแอปพลิเคชัน

*EN:* On 22 February 2569, a private company engaged in graphic design services in Samut Prakan Province reported damage to the police. The company discovered that an employee's computer system had been infected with malware after opening a PDF document received via email. The file exploited Exploitation for Client Execution to run malicious code on the victim's system. Log examination revealed that the malware subsequently issued commands to query information about Windows version, computer name, username, and installed software on the system. The affected machine then transmitted this data back to a control server using a raw socket protocol connection that was not HTTP or HTTPS, differing from normal application-level communication.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1203 Exploitation for Client Execution | ใช้ Exploitation for Client Execution เพื่อให้โค้ดอันตรายทำงานในระบบของผู้เสียหาย |
| 2 | described | T1082 System Information Discovery | โปรแกรมร้ายได้ทำการเรียกคำสั่งเพื่อสอบถามข้อมูลเกี่ยวกับเวอร์ชัน Windows ชื่อเครื่องคอมพิวเตอร์ ชื่อผู้ใช้งาน และรายชื่อซอฟต์แวร์ที่ติดตั้งในระบบ |
| 3 | described | T1095 Non-Application Layer Protocol | ส่งข้อมูลกลับไปยังเซิร์ฟเวอร์ควบคุมผ่านการเชื่อมต่อ raw socket protocol ที่ไม่ใช่ HTTP หรือ HTTPS ซึ่งแตกต่างจากการสื่อสารแบบปกติของแอปพลิเคชัน |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_018  (source: 2016 Ukraine Electric Power Attack C0025)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการจัดการลอจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งความว่าระบบ VPN gateway ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าบัญชีผู้ใช้งาน admin ได้ถูกเข้าสู่ระบบซ้ำแล้วซ้ำเล่าด้วยรหัสผ่านที่ต่างกันหลายครั้งในช่วงเวลาสั้น ๆ จนกระทั่งสำเร็จการเข้าสู่ระบบในครั้งสุดท้าย ต่อมาผู้โจมตีได้ทำการ Remote System Discovery เพื่อค้นหาเซิร์ฟเวอร์และอุปกรณ์เครือข่ายอื่น ๆ ที่เชื่อมต่ออยู่ในโครงข่ายภายใน จากนั้นผู้โจมตีได้ทำการ Lateral Tool Transfer โดยส่งโปรแกรมช่วยในการทำงานจำนวนหลายตัวไปยังเครื่องคอมพิวเตอร์เซิร์ฟเวอร์อื่นภายในเครือข่ายเพื่อขยายการควบคุมและเข้าถึงระบบต่าง ๆ ต่อไป

*EN:* On 22 February 2569, a private logistics management company in Samut Prakan Province reported unauthorized access to its VPN gateway. Digital log examination revealed that the admin user account was repeatedly accessed with different passwords multiple times in a short period until successful login on the final attempt. Subsequently, the attacker performed Remote System Discovery to identify servers and other network devices connected within the internal network. The attacker then conducted Lateral Tool Transfer by deploying multiple auxiliary programs to other server computers within the network to expand control and gain further system access.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1110 Brute Force | บัญชีผู้ใช้งาน admin ได้ถูกเข้าสู่ระบบซ้ำแล้วซ้ำเล่าด้วยรหัสผ่านที่ต่างกันหลายครั้งในช่วงเวลาสั้น ๆ จนกระทั่งสำเร็จการเข้าสู่ระบบในครั้งสุดท้าย |
| 2 | named | T1018 Remote System Discovery | ผู้โจมตีได้ทำการ Remote System Discovery เพื่อค้นหาเซิร์ฟเวอร์และอุปกรณ์เครือข่ายอื่น ๆ ที่เชื่อมต่ออยู่ในโครงข่ายภายใน |
| 3 | named | T1570 Lateral Tool Transfer | ผู้โจมตีได้ทำการ Lateral Tool Transfer โดยส่งโปรแกรมช่วยในการทำงานจำนวนหลายตัวไปยังเครื่องคอมพิวเตอร์เซิร์ฟเวอร์อื่นภายในเครือข่าย |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_019  (source: Operation Digital Eye C0061)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนจัดการระบบสารสนเหมศ แห่งหนึ่งในจังหวัดนนทบุรี ได้แจ้งความว่าระบบ web application ของบริษัท ถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ของเซิร์ฟเวอร์พบว่า ผู้โจมตีได้เข้าสู่ระบบผ่านช่องโหว่ที่ยังไม่ได้ปรับปรุง (unpatched vulnerability) ในโมดูล authentication ของแอปพลิเคชัน ต่อมา จากการวิเคราะห์ activity ของบัญชีที่ถูกบุกรุก พบว่า ผู้โจมตีได้ทำการค้นหาและรวบรวมข้อมูลเกี่ยวกับบัญชีผู้ดูแลระบบ รวมถึงชื่อผู้ใช้งาน และรายชื่อเจ้าหน้าที่ที่มีสิทธิ์เข้าถึงข้อมูลสำคัญ จากนั้น จากการตรวจสอบ DNS query และ network traffic พบว่า ผู้โจมตีได้ตั้งค่า infrastructure เพื่อซ่อนตัวตนและการเชื่อมต่อของตนเอง โดยใช้ proxy server และ domain ที่ลงทะเบียนแบบ anonymized เพื่อป้องกันการติดตามและตรวจสอบจากฝ่ายเจ้าหน้าที่

*EN:* On 22 February 2569, a private company managing information systems in Nonthaburi Province reported that its web application was accessed without authorization. Upon examination of server logs, investigators found that the attacker gained entry through an unpatched vulnerability in the authentication module of the application. Subsequently, analysis of activity on the compromised account revealed that the attacker conducted searches and collected information about system administrator accounts, including usernames and a roster of personnel with access to critical data. Following this, examination of DNS queries and network traffic showed that the attacker configured infrastructure to conceal their identity and connections by employing a proxy server and anonymously registered domains to prevent tracking and investigation by authorities.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ผู้โจมตีได้เข้าสู่ระบบผ่านช่องโหว่ที่ยังไม่ได้ปรับปรุง (unpatched vulnerability) ในโมดูล authentication ของแอปพลิเคชัน |
| 2 | described | T1033 System Owner/User Discovery | ผู้โจมตีได้ทำการค้นหาและรวบรวมข้อมูลเกี่ยวกับบัญชีผู้ดูแลระบบ รวมถึงชื่อผู้ใช้งาน และรายชื่อเจ้าหน้าที่ที่มีสิทธิ์เข้าถึงข้อมูลสำคัญ |
| 3 | described | T1665 Hide Infrastructure | ผู้โจมตีได้ตั้งค่า infrastructure เพื่อซ่อนตัวตนและการเชื่อมต่อของตนเอง โดยใช้ proxy server และ domain ที่ลงทะเบียนแบบ anonymized |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_020  (source: Night Dragon C0002)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพได้แจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยบุคคลที่ไม่ได้รับอนุญาต จากการตรวจสอบ log ระบบพบว่าผู้โจมตีได้ใช้ข้อมูลประจำตัวของพนักงานที่ยังคงมีสิทธิ์การเข้าถึงอยู่ เพื่อเข้าสู่เครื่องแม่ข่ายผ่านการยืนยันตัวตนปกติ ต่อมาจากการตรวจสอบพยานหลักฐานดิจิทัลพบว่าผู้โจมตีได้ค้นหาข้อมูลเกี่ยวกับชื่อผู้ดูแลระบบและบัญชีผู้ใช้ที่มีสิทธิ์สูงผ่านคำสั่ง net user และการดูรายชื่อจากไฟล์ระบบต่างๆ จากนั้นผู้โจมตีได้ทำการสกัดข้อมูลจากเครื่องคอมพิวเตอร์เฉพาะที่ เช่น ไฟล์ประวัติการเข้าถึง เอกสารสำคัญ และข้อมูลการกำหนดค่าระบบเก็บไว้ในเครื่องท้องถิ่น สุดท้ายผู้โจมตีได้ทำการ Ingress Tool Transfer โดยดาวน์โหลดเครื่องมือ remote access ชื่อ Anydesk ลงในระบบเพื่อรักษาการเข้าถึงและควบคุมระบบต่อไป

*EN:* On 22 February 2569, an information technology private company in Bangkok reported unauthorized access to its primary server system. From log system inspection, it was found that the attacker used valid employee credentials that retained active access rights to authenticate to the host server through normal authentication procedures. Subsequently, from digital evidence examination, the attacker was found to have searched for information about system administrator names and high-privilege user accounts through net user commands and examination of various system files. The attacker then extracted data from the local computer, including access history files, sensitive documents, and system configuration information stored locally. Finally, the attacker performed Ingress Tool Transfer by downloading a remote access tool called Anydesk onto the system to maintain access and control over the system.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | ผู้โจมตีได้ใช้ข้อมูลประจำตัวของพนักงานที่ยังคงมีสิทธิ์การเข้าถึงอยู่ เพื่อเข้าสู่เครื่องแม่ข่ายผ่านการยืนยันตัวตนปกติ |
| 2 | described | T1033 System Owner/User Discovery | ผู้โจมตีได้ค้นหาข้อมูลเกี่ยวกับชื่อผู้ดูแลระบบและบัญชีผู้ใช้ที่มีสิทธิ์สูงผ่านคำสั่ง net user และการดูรายชื่อจากไฟล์ระบบต่างๆ |
| 3 | described | T1005 Data from Local System | ผู้โจมตีได้ทำการสกัดข้อมูลจากเครื่องคอมพิวเตอร์เฉพาะที่ เช่น ไฟล์ประวัติการเข้าถึง เอกสารสำคัญ และข้อมูลการกำหนดค่าระบบเก็บไว้ในเครื่องท้องถิ่น |
| 4 | named | T1105 Ingress Tool Transfer | ผู้โจมตีได้ทำการ Ingress Tool Transfer โดยดาวน์โหลดเครื่องมือ remote access ชื่อ Anydesk ลงในระบบ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_021  (source: 3CX Supply Chain Attack C0057)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านสื่อสารแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบเซิร์ฟเวอร์ของหน่วยงานถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ Valid Accounts ของพนักงานระดับ IT Support ที่ได้รับการสารภาพตัวอักษรผ่านช่องทางโซเชียลมีเดีย เพื่อเข้าสู่ระบบ RDP ในวันที่ 20 กุมภาพันธ์เวลา 14:35 น. ต่อมาผู้โจมตีได้ทำการ Inter-Process Communication ผ่านเครื่องมือ named pipes เพื่อติดต่อสื่อสารระหว่างกระบวนการต่างๆ บนเซิร์ฟเวอร์ Windows จากนั้นได้ทำการ Process Injection โดยการฉีดโค้ดอันตรายเข้าไปในกระบวนการ svchost.exe ด้วยเทคนิค CreateRemoteThread เพื่อให้ได้สิทธิ์ SYSTEM ในระบบ สุดท้าย จากการตรวจสอบ memory artifacts และ registry พบร่องรอยการเข้าถึงข้อมูลเบราว์เซอร์ที่บันทึกไว้ เช่น cookies, cached credentials และประวัติการท่องเว็บของพนักงานผู้บริหาร ซึ่งบ่งชี้ว่าผู้โจมตีได้ดำเนินการสำรวจข้อมูลที่เก็บไว้ในเบราว์เซอร์เพื่อหาข้อมูลลับเพิ่มเติม

*EN:* On 22 February 2569, a private telecommunications company in Bangkok reported unauthorized access to its server system. Log examination revealed that the attacker used Valid Accounts belonging to an IT Support employee whose credentials were obtained through social media to access the RDP system on 20 February at 14:35. Subsequently, the attacker performed Inter-Process Communication via named pipes to facilitate communication between different processes on the Windows server. The attacker then executed Process Injection by injecting malicious code into the svchost.exe process using CreateRemoteThread technique to obtain SYSTEM privileges on the system. Finally, examination of memory artifacts and registry revealed traces of browser data access including cookies, cached credentials, and web browsing history of executive staff, indicating that the attacker had conducted reconnaissance of stored browser information to identify additional sensitive data.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1078 Valid Accounts | ผู้โจมตีได้ใช้ Valid Accounts ของพนักงานระดับ IT Support |
| 2 | named | T1559 Inter-Process Communication | ผู้โจมตีได้ทำการ Inter-Process Communication ผ่านเครื่องมือ named pipes |
| 3 | named | T1055 Process Injection | ได้ทำการ Process Injection โดยการฉีดโค้ดอันตรายเข้าไปในกระบวนการ svchost.exe |
| 4 | described | T1217 Browser Information Discovery | พบร่องรอยการเข้าถึงข้อมูลเบราว์เซอร์ที่บันทึกไว้ เช่น cookies, cached credentials และประวัติการท่องเว็บ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_022  (source: Frankenstein C0001)

**AUTO-FLAGS: step 3: described cue names the technique (Exfiltration Over C2 Channel)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานคร ได้รับแจ้งเบาะแสจากผู้ใช้งานว่าพบไฟล์แนบในอีเมลที่ดูเหมือนเป็นใบแจ้งหนี้ แต่เมื่อเปิดไฟล์ดังกล่าวพบว่าระบบถูกเรียกใช้คำสั่งที่ไม่ปกติ และกระบวนการที่ไม่รู้จักเริ่มทำงานในพื้นหลัง จากการตรวจสอบ log พบว่าต่อมาระบบเริ่มดำเนินการ Automated Collection โดยการสแกนและรวบรวมไฟล์เอกสารที่สำคัญจากเครื่องคอมพิวเตอร์ของผู้ใช้งาน รวมถึงข้อมูลการเข้าถึงระบบและไฟล์ประวัติการทำงาน จากนั้นจากการวิเคราะห์ traffic ระบบเครือข่ายพบว่าข้อมูลที่รวบรวมได้ถูกส่งออกไปยังเซิร์ฟเวอร์ที่อยู่ต่างประเทศผ่านทาง Exfiltration Over C2 Channel โดยใช้การเข้ารหัสและซ่อนข้อมูลการสื่อสารไว้ท่ามกลาง traffic ปกติ

*EN:* On 22 February 2569, a private financial services company in Bangkok received a report from a user that they had opened an email attachment appearing to be an invoice, but upon opening the file the system executed unusual commands and unfamiliar processes began running in the background. Upon examination of system logs, it was found that the system subsequently performed Automated Collection by scanning and gathering important documents from the user's computer, including system access credentials and work history files. Network traffic analysis then revealed that the collected data was exfiltrated to a foreign server through an Exfiltration Over C2 Channel, using encryption and concealment of communications within normal traffic patterns.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1203 Exploitation for Client Execution | เมื่อเปิดไฟล์ดังกล่าวพบว่าระบบถูกเรียกใช้คำสั่งที่ไม่ปกติ และกระบวนการที่ไม่รู้จักเริ่มทำงานในพื้นหลัง |
| 2 | named | T1119 Automated Collection | ต่อมาระบบเริ่มดำเนินการ Automated Collection โดยการสแกนและรวบรวมไฟล์เอกสารที่สำคัญจากเครื่องคอมพิวเตอร์ของผู้ใช้งาน |
| 3 | described | T1041 Exfiltration Over C2 Channel | ข้อมูลที่รวบรวมได้ถูกส่งออกไปยังเซิร์ฟเวอร์ที่อยู่ต่างประเทศผ่านทาง Exfiltration Over C2 Channel |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_023  (source: Operation Honeybee C0006)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพฯ ได้แจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ทำการอ่านและคัดลอกไฟล์ข้อมูลลูกค้า ไฟล์ config ของระบบ และเอกสาร Excel ที่เก็บข้อมูลการเงินจากเครื่องคอมพิวเตอร์เซิร์ฟเวอร์ภายในเครือข่าย ต่อมาจากการสืบสวน พบว่าผู้โจมตีได้ใช้ Ingress Tool Transfer เพื่อส่งเครื่องมือ reverse shell และ data compression utility เข้ามาในระบบผ่านทาง HTTP request จากเซิร์ฟเวอร์ C2 ที่ตั้งอยู่ในต่างประเทศ สุดท้าย จากการตรวจสอบ network traffic พบว่าข้อมูลที่ถูกเก็บรวบรวมได้ถูกส่งออกไปยังเซิร์ฟเวอร์ C2 เดียวกันผ่าน HTTPS encrypted channel ในหลายครั้งระหว่างวันที่ 20-22 กุมภาพันธ์

*EN:* On 22 February 2569, a private financial services company in Bangkok reported that its primary server system had been accessed without authorization. From examination of system logs, it was found that the attacker had read and copied customer data files, system configuration files, and Excel documents containing financial records from the server computer on the internal network. Subsequently, from investigation, it was discovered that the attacker had used Ingress Tool Transfer to send reverse shell tools and data compression utilities into the system via HTTP request from a C2 server located overseas. Finally, from examination of network traffic, it was found that the collected data had been transmitted to the same C2 server through an HTTPS encrypted channel multiple times between 20-22 February.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1005 Data from Local System | ผู้โจมตีได้ทำการอ่านและคัดลอกไฟล์ข้อมูลลูกค้า ไฟล์ config ของระบบ และเอกสาร Excel ที่เก็บข้อมูลการเงินจากเครื่องคอมพิวเตอร์เซิร์ฟเวอร์ภายในเครือข่าย |
| 2 | named | T1105 Ingress Tool Transfer | ผู้โจมตีได้ใช้ Ingress Tool Transfer เพื่อส่งเครื่องมือ reverse shell และ data compression utility เข้ามาในระบบผ่านทาง HTTP request จากเซิร์ฟเวอร์ C2 |
| 3 | described | T1041 Exfiltration Over C2 Channel | ข้อมูลที่ถูกเก็บรวบรวมได้ถูกส่งออกไปยังเซิร์ฟเวอร์ C2 เดียวกันผ่าน HTTPS encrypted channel |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_024  (source: C0026 C0026)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพมหานครแจ้งความว่าระบบเซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log และหลักฐานดิจิทัลพบว่าผู้โจมตีได้ทำการสำเร็จการเข้าถึงเครื่องคอมพิวเตอร์ของพนักงานและดำเนินการสำเร็จการเก็บรวบรวมข้อมูลจำนวนมากจากระบบภายในรวมถึงไฟล์ฐานข้อมูลลูกค้า และไฟล์เอกสารการทำธุรกรรมต่างๆ ต่อมาผู้โจมตีได้ใช้ Ingress Tool Transfer เพื่อนำเข้าเครื่องมือที่จำเป็นสำหรับการทำงานต่อเนื่องลงในระบบเป้าหมาย จากนั้นจากการวิเคราะห์ traffic ออกไปจากเครื่องเซิร์ฟเวอร์พบว่าผู้โจมตีได้ทำการส่งข้อมูลออกไปนอกเครือข่ายเป็นจำนวนเล็กน้อยในแต่ละครั้ง โดยแบ่งแยกการส่งข้อมูลออกไปเป็นหลายช่วงเวลาเพื่อหลีกเลี่ยงการตรวจจับจากระบบ IDS

*EN:* On 22 February 2569, a financial services company in Bangkok reported unauthorized access to its primary server. Digital forensics and log analysis revealed that the attacker successfully gained access to an employee workstation and conducted extensive collection of data from internal systems, including customer database files and transaction documents. Subsequently, the attacker deployed Ingress Tool Transfer to introduce necessary tools into the target system for continued operations. Analysis of outbound traffic showed the attacker exfiltrated data in small increments across multiple time intervals to evade IDS detection.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1005 Data from Local System | สำเร็จการเก็บรวบรวมข้อมูลจำนวนมากจากระบบภายในรวมถึงไฟล์ฐานข้อมูลลูกค้า และไฟล์เอกสารการทำธุรกรรมต่างๆ |
| 2 | named | T1105 Ingress Tool Transfer | ผู้โจมตีได้ใช้ Ingress Tool Transfer เพื่อนำเข้าเครื่องมือที่จำเป็นสำหรับการทำงานต่อเนื่องลงในระบบเป้าหมาย |
| 3 | described | T1030 Data Transfer Size Limits | ผู้โจมตีได้ทำการส่งข้อมูลออกไปนอกเครือข่ายเป็นจำนวนเล็กน้อยในแต่ละครั้ง โดยแบ่งแยกการส่งข้อมูลออกไปเป็นหลายช่วงเวลา |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_025  (source: Operation AkaiRyū C0060)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบคอมพิวเตอร์เซิร์ฟเวอร์หลักถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้รันคำสั่ง WMI ผ่านทาง PowerShell เพื่อให้สามารถดำเนินการคำสั่งระยะไกลบนระบบ ต่อมาจากการวิเคราะห์ไฟล์ log บราวเซอร์พบการเข้าถึงไฟล์ cookies และ password stored ในโปรแกรม Chrome และ Firefox ของเครื่องเหยื่อ จากนั้นผู้โจมตีได้ติดตั้ง Remote Access Tools เพื่อรักษาการเข้าถึงระบบอย่างต่อเนื่อง สุดท้ายทีมตรวจสอบพบการเชื่อมต่อไปยังเซิร์ฟเวอร์ควบคุมระยะไกลในต่างประเทศ

*EN:* On 22 February 2569, a private financial services company in Bangkok reported unauthorized access to its main server system. Log analysis revealed that the attacker executed WMI commands via PowerShell to enable remote command execution on the system. Subsequent browser log analysis identified access to stored credentials and cookies from Chrome and Firefox on the victim machine. The attacker then installed Remote Access Tools to maintain persistent system access. Finally, the investigation team identified ongoing connections to a command-and-control server located overseas.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1047 Windows Management Instrumentation | ผู้โจมตีได้รันคำสั่ง WMI ผ่านทาง PowerShell เพื่อให้สามารถดำเนินการคำสั่งระยะไกลบนระบบ |
| 2 | described | T1217 Browser Information Discovery | จากการวิเคราะห์ไฟล์ log บราวเซอร์พบการเข้าถึงไฟล์ cookies และ password stored ในโปรแกรม Chrome และ Firefox ของเครื่องเหยื่อ |
| 3 | named | T1219 Remote Access Tools | ผู้โจมตีได้ติดตั้ง Remote Access Tools เพื่อรักษาการเข้าถึงระบบอย่างต่อเนื่อง |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_026  (source: HomeLand Justice C0038)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนจัดการโครงการก่อสร้างแห่งหนึ่งในจังหวัดสมุทรปราการได้แจ้งความว่าระบบเซิร์ฟเวอร์ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีสามารถเจาะเข้าระบบผ่านช่องโหว่ในแอปพลิเคชันที่เปิดให้บริการต่อสาธารณชนบนอินเทอร์เน็ต ต่อมาจากการวิเคราะห์กิจกรรมในระบบพบว่าผู้โจมตีใช้ Windows Management Instrumentation เพื่อดำเนินการคำสั่งต่างๆ บนเซิร์ฟเวอร์ จากนั้นผู้โจมตีทำการสแกนและตรวจสอบเพื่อค้นหาเซิร์ฟเวอร์อื่นๆ และบริการที่เปิดอยู่ในเครือข่ายภายในของบริษัท สุดท้ายผู้โจมตีดำเนินการเข้ารหัสข้อมูลสำคัญของบริษัททั้งหมด ทำให้ผู้บริหารไม่สามารถเข้าถึงและใช้งานข้อมูลได้

*EN:* On 22 February 2569, a private construction management company in Samut Prakan Province reported unauthorized access to its server system. From log analysis, investigators found that the attacker gained entry through a vulnerability in a public-facing web application. Subsequently, analysis of system activity revealed the attacker used Windows Management Instrumentation to execute commands on the server. The attacker then performed scanning and enumeration to identify other servers and open services within the company's internal network. Finally, the attacker encrypted all critical company data, rendering it inaccessible and unusable by management.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | เจาะเข้าระบบผ่านช่องโหว่ในแอปพลิเคชันที่เปิดให้บริการต่อสาธารณชนบนอินเทอร์เน็ต |
| 2 | named | T1047 Windows Management Instrumentation | ใช้ Windows Management Instrumentation เพื่อดำเนินการคำสั่งต่างๆ บนเซิร์ฟเวอร์ |
| 3 | described | T1046 Network Service Discovery | ทำการสแกนและตรวจสอบเพื่อค้นหาเซิร์ฟเวอร์อื่นๆ และบริการที่เปิดอยู่ในเครือข่ายภายในของบริษัท |
| 4 | described | T1486 Data Encrypted for Impact | ดำเนินการเข้ารหัสข้อมูลสำคัญของบริษัททั้งหมด ทำให้ผู้บริหารไม่สามารถเข้าถึงและใช้งานข้อมูลได้ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_027  (source: 2022 Ukraine Electric Power Attack C0034)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทบริการด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพได้แจ้งความว่าระบบ server หลักถูกบุกรุก จากการตรวจสอบ log และอุปกรณ์ที่ได้รับผลกระทบพบว่า ผู้โจมตีได้ใช้ประโยชน์จากเครื่องมือจัดการระบบที่มีอยู่แล้วในสภาพแวดล้อมเครือข่าย เช่น PowerShell และ WinRM เพื่อเคลื่อนย้ายข้อมูลประจำตัวและเครื่องมือเพิ่มเติมไปยังเซิร์ฟเวอร์อื่น ๆ ในโครงสร้างพื้นฐาน ต่อมาผู้โจมตีได้สร้างการสื่อสารแบบ Non-Application Layer Protocol ผ่านช่องทาง DNS tunneling เพื่อควบคุมระบบที่ถูกบุกรุกจากระยะไกล สุดท้าย ผู้โจมตีได้ดำเนินการลบไฟล์ฐานข้อมูลขนาดใหญ่ และเขียนทับข้อมูลสำคัญด้วยข้อมูลสุ่มหลายครั้ง ทำให้ข้อมูลบันทึกธุรกรรมของลูกค้าประมาณ 450,000 รายการสูญหาย

*EN:* On 22 February 2569, a financial services company in Bangkok reported that its primary server had been compromised. Upon examination of logs and affected devices, investigators found that the attacker had leveraged existing system administration tools within the network environment, such as PowerShell and WinRM, to transfer credentials and additional tools to other servers in the infrastructure. Subsequently, the attacker established communication via DNS tunneling, a Non-Application Layer Protocol, to remotely control the compromised systems. Finally, the attacker deleted large database files and overwrote critical data with random information multiple times, resulting in the loss of approximately 450,000 customer transaction records.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1570 Lateral Tool Transfer | ผู้โจมตีได้ใช้ประโยชน์จากเครื่องมือจัดการระบบที่มีอยู่แล้วในสภาพแวดล้อมเครือข่าย เช่น PowerShell และ WinRM เพื่อเคลื่อนย้ายข้อมูลประจำตัวและเครื่องมือเพิ่มเติมไปยังเซิร์ฟเวอร์อื่น ๆ ในโครงสร้างพื้นฐาน |
| 2 | named | T1095 Non-Application Layer Protocol | ผู้โจมตีได้สร้างการสื่อสารแบบ Non-Application Layer Protocol ผ่านช่องทาง DNS tunneling เพื่อควบคุมระบบที่ถูกบุกรุกจากระยะไกล |
| 3 | described | T1485 Data Destruction | ผู้โจมตีได้ดำเนินการลบไฟล์ฐานข้อมูลขนาดใหญ่ และเขียนทับข้อมูลสำคัญด้วยข้อมูลสุ่มหลายครั้ง |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_028  (source: 2015 Ukraine Electric Power Attack C0028)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพมหานคร ได้แจ้งความว่าระบบเซิร์ฟเวอร์หลักของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต โดยผู้โจมตีได้สร้าง External Remote Services account เพื่อรักษาการเข้าถึงระบบอย่างต่อเนื่อง จากการตรวจสอบ log และข้อมูลเครือข่ายพบว่า ผู้โจมตีได้ติดตั้งเครื่องมือสำหรับดักจับแพ็กเก็ตข้อมูลบนเซ็กเมนต์เครือข่ายภายในและได้บันทึกการสื่อสารระหว่างเซิร์ฟเวอร์กับอุปกรณ์ไคลเอนต์เพื่อเก็บข้อมูลสำหรับการเข้าถึง จากนั้น ผู้โจมตีได้ทำการค้นหาและแสดงรายการเซิร์ฟเวอร์อื่น ๆ ที่เชื่อมต่ออยู่ในโครงข่ายภายในองค์กรเพื่อเตรียมการโจมตีต่อขยาย

*EN:* On 22 February 2569, a private information technology company in Bangkok reported that its primary server system was accessed without authorization. The attacker had created an External Remote Services account to maintain persistent access to the system. Upon examination of logs and network data, the investigator found that the attacker had deployed packet capture tools on an internal network segment and recorded communications between servers and client devices to harvest credentials. Subsequently, the attacker performed enumeration of other servers connected to the organization's internal network in preparation for lateral movement.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1133 External Remote Services | ผู้โจมตีได้สร้าง External Remote Services account เพื่อรักษาการเข้าถึงระบบอย่างต่อเนื่อง |
| 2 | described | T1040 Network Sniffing | ผู้โจมตีได้ติดตั้งเครื่องมือสำหรับดักจับแพ็กเก็ตข้อมูลบนเซ็กเมนต์เครือข่ายภายในและได้บันทึกการสื่อสารระหว่างเซิร์ฟเวอร์กับอุปกรณ์ไคลเอนต์เพื่อเก็บข้อมูลสำหรับการเข้าถึง |
| 3 | described | T1018 Remote System Discovery | ผู้โจมตีได้ทำการค้นหาและแสดงรายการเซิร์ฟเวอร์อื่น ๆ ที่เชื่อมต่ออยู่ในโครงข่ายภายในองค์กร |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_029  (source: Operation MidnightEclipse C0048)

**AUTO-FLAGS: step 1: described cue names the technique (Inter-Process Communication)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพได้แจ้งความว่าระบบ Windows Server ของฝ่ายบัญชีถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้ใช้ Inter-Process Communication ผ่านการสร้าง named pipe เพื่อรันคำสั่งบน process ที่มีสิทธิ์สูงกว่า ต่อมาพบหลักฐานว่าบัญชี ldap_service ซึ่งเป็น Valid Accounts ของระบบได้ถูกนำมาใช้งานจากที่ไม่ใช่ IP address ปกติ และทำการ login ซ้ำๆ ในช่วงเวลากลางคืน จากนั้นผู้โจมตีได้ทำการสแกนและดึงข้อมูลจากไฟล์ local system เช่น SAM hive และ NTDS.dit ที่เก็บรักษาในโฟลเดอร์ System32 สุดท้ายพบร่องรอยการ download tools จากเซิร์ฟเวอร์ภายนอก โดยมีการ transfer ไฟล์ executable ขนาด 4.2 MB ผ่าน HTTPS port 443 ไปยัง directory ชั่วคราวของระบบ

*EN:* On 22 February 2569, a private financial services company in Bangkok reported unauthorized access to its accounting department Windows Server. Log examination revealed the attacker used Inter-Process Communication via named pipe creation to execute commands under higher-privilege processes. Subsequently, evidence showed that the ldap_service Valid Accounts had been accessed from non-standard IP addresses with repeated logins during night hours. The attacker then extracted data from local system files including SAM hive and NTDS.dit stored in the System32 folder. Finally, traces of tool transfer were discovered, with a 4.2 MB executable file downloaded from an external server via HTTPS port 443 to a system temporary directory.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1559 Inter-Process Communication | ใช้ Inter-Process Communication ผ่านการสร้าง named pipe เพื่อรันคำสั่งบน process ที่มีสิทธิ์สูงกว่า |
| 2 | named | T1078 Valid Accounts | บัญชี ldap_service ซึ่งเป็น Valid Accounts ของระบบได้ถูกนำมาใช้งาน |
| 3 | described | T1005 Data from Local System | ทำการสแกนและดึงข้อมูลจากไฟล์ local system เช่น SAM hive และ NTDS.dit ที่เก็บรักษาในโฟลเดอร์ System32 |
| 4 | described | T1105 Ingress Tool Transfer | มีการ transfer ไฟล์ executable ขนาด 4.2 MB ผ่าน HTTPS port 443 ไปยัง directory ชั่วคราวของระบบ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_030  (source: Anthropic AI-orchestrated Campaign C0062)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทบริการด้านเทคโนโลยีสารสนเทศแห่งหนึ่งในจังหวัดกรุงเทพ แจ้งความว่าระบบเซิร์ฟเวอร์ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log ของระบบพบว่าบัญชีผู้ใช้งานชื่อ "admin_backup" ซึ่งเป็นบัญชีของพนักงานที่ลาออกแล้ว ได้ถูกใช้เพื่อเข้าสู่ระบบเซิร์ฟเวอร์ในวันที่ 18 กุมภาพันธ์ เวลา 02:47 น. ต่อมา จากการสืบสวนหลักฐานดิจิทัลพบว่า ผู้โจมตีได้ทำการค้นหาและสำเนาไฟล์ข้อมูลที่เก็บในไดรฟ์ท้องถิ่นของเซิร์ฟเวอร์ ได้แก่ ไฟล์ฐานข้อมูล customer database และไฟล์เอกสารที่มีข้อมูลส่วนบุคคลของลูกค้าจำนวน 1,247 รายการ จากนั้น ข้อมูลดังกล่าวถูกส่งออกไปยังบริการ cloud storage ของบุคคลที่สามผ่าน HTTP request ไปยัง endpoint ของแพลตฟอร์มเก็บข้อมูลออนไลน์ในวันที่ 19 กุมภาพันธ์ สุดท้าย ข้อมูลที่ถูกขโมยนี้ได้ปรากฏบนเว็บไซต์ดาร์กเว็บในวันที่ 21 กุมภาพันธ์

*EN:* On 22 February 2569, an information technology services company in Bangkok reported unauthorized access to its server system. Log examination revealed that a user account named "admin_backup" belonging to a former employee was used to access the server on 18 February at 02:47. Subsequently, digital forensic investigation found that the attacker had located and copied data files stored in the server's local drive, including customer database files and documents containing personal information of 1,247 customers. The data was then transmitted to a third-party cloud storage service via HTTP requests to an online data storage platform endpoint on 19 February. Finally, the stolen data appeared on a dark web website on 21 February.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | บัญชีผู้ใช้งานชื่อ "admin_backup" ซึ่งเป็นบัญชีของพนักงานที่ลาออกแล้ว ได้ถูกใช้เพื่อเข้าสู่ระบบเซิร์ฟเวอร์ |
| 2 | described | T1005 Data from Local System | ผู้โจมตีได้ทำการค้นหาและสำเนาไฟล์ข้อมูลที่เก็บในไดรฟ์ท้องถิ่นของเซิร์ฟเวอร์ ได้แก่ ไฟล์ฐานข้อมูล customer database และไฟล์เอกสารที่มีข้อมูลส่วนบุคคล |
| 3 | described | T1567 Exfiltration Over Web Service | ข้อมูลดังกล่าวถูกส่งออกไปยังบริการ cloud storage ของบุคคลที่สามผ่าน HTTP request ไปยัง endpoint ของแพลตฟอร์มเก็บข้อมูลออนไลน์ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_031  (source: C0017 C0017)

**AUTO-FLAGS: step 3: described cue names the technique (Proxy)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพฯ แจ้งความว่าระบบเว็บแอปพลิเคชันของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log server พบว่าผู้โจมตีส่งคำขอ HTTP ที่มีข้อมูลพารามิเตอร์ที่ผิดปกติไปยัง endpoint สาธารณะ ซึ่งทำให้ได้รับการเข้าถึงระบบด้านหลัง ต่อมา จากการวิเคราะห์ token authentication พบร่องรอยการแก้ไขค่า session ID และ JWT payload ในหน้าความจำของแอปพลิเคชัน เพื่อให้ได้สิทธิ์การเข้าถึงระดับผู้ดูแลระบบ จากนั้น จากการติดตามการเชื่อมต่อเครือข่าย พบว่าเซิร์ฟเวอร์ของบริษัทส่งข้อมูล outbound ผ่านช่องทางที่ผ่านเซิร์ฟเวอร์กลางหลายตัวในต่างประเทศ ซึ่งใช้เป็น proxy สำหรับซ่อนแหล่งที่มาของการสื่อสารควบคุมและส่งคำสั่ง

*EN:* On 22 February 2026, a financial services company in Bangkok reported unauthorized access to its web application system. Log analysis revealed that the attacker sent malformed HTTP requests with abnormal parameters to a public-facing endpoint, gaining backend access. Subsequently, examination of authentication tokens showed evidence of session ID and JWT payload modification in application memory to obtain administrator-level privileges. Later, network connection analysis identified outbound traffic from the company's server being routed through multiple intermediate servers overseas, used as a proxy to conceal the origin of command-and-control communications.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1190 Exploit Public-Facing Application | ผู้โจมตีส่งคำขอ HTTP ที่มีข้อมูลพารามิเตอร์ที่ผิดปกติไปยัง endpoint สาธารณะ ซึ่งทำให้ได้รับการเข้าถึงระบบด้านหลัง |
| 2 | described | T1134 Access Token Manipulation | จากการวิเคราะห์ token authentication พบร่องรอยการแก้ไขค่า session ID และ JWT payload ในหน้าความจำของแอปพลิเคชัน เพื่อให้ได้สิทธิ์การเข้าถึงระดับผู้ดูแลระบบ |
| 3 | described | T1090 Proxy | เซิร์ฟเวอร์ของบริษัทส่งข้อมูล outbound ผ่านช่องทางที่ผ่านเซิร์ฟเวอร์กลางหลายตัวในต่างประเทศ ซึ่งใช้เป็น proxy สำหรับซ่อนแหล่งที่มาของการสื่อสารควบคุมและส่งคำสั่ง |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_032  (source: Leviathan Australian Intrusions C0049)

**AUTO-FLAGS: step 1: described cue names the technique (Valid Accounts)**

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพ แจ้งความว่าระบบ CRM ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีใช้ Valid Accounts ของพนักงานฝ่ายขายชื่อ สมชาย ก. ซึ่งมีสิทธิการเข้าถึงฐานข้อมูลลูกค้า ต่อมาผู้โจมตีทำการ Steal Application Access Token โดยดึง OAuth token จากเบราว์เซอร์ที่ cache ไว้ในเครื่องคอมพิวเตอร์ของเหยื่อ จากนั้นใช้ token ดังกล่าวเพื่อสำรวจเซิร์ฟเวอร์อื่นๆ ในเครือข่ายภายใน และตรวจสอบขอบเขตของระบบ API ที่เชื่อมต่อกับแอปพลิเคชันหลัก สุดท้ายผู้โจมตีติดตั้งโปรแกรมจับคีย์บอร์ดเพื่อบันทึกการพิมพ์รหัสผ่านและข้อมูลการเข้าสู่ระบบของผู้ใช้คนอื่น และส่งข้อมูลที่รวบรวมได้ผ่าน Command and Control server ในต่างประเทศ

*EN:* On 22 February 2569, a financial services company in Bangkok reported unauthorized access to its CRM system. Log analysis revealed that the attacker used valid credentials belonging to a sales employee named Somchai K., who had access to the customer database. Subsequently, the attacker stole an application access token by extracting an OAuth token cached in the victim's browser. The attacker then used that token to discover other servers within the internal network and probe the scope of APIs connected to the main application. Finally, the attacker deployed a keystroke logger to capture password entries and login credentials from other users, and exfiltrated the collected data through a Command and Control server overseas.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1078 Valid Accounts | ผู้โจมตีใช้ Valid Accounts ของพนักงานฝ่ายขายชื่อ สมชาย ก. ซึ่งมีสิทธิการเข้าถึงฐานข้อมูลลูกค้า |
| 2 | named | T1528 Steal Application Access Token | ผู้โจมตีทำการ Steal Application Access Token โดยดึง OAuth token จากเบราว์เซอร์ที่ cache ไว้ในเครื่องคอมพิวเตอร์ของเหยื่อ |
| 3 | described | T1018 Remote System Discovery | ใช้ token ดังกล่าวเพื่อสำรวจเซิร์ฟเวอร์อื่นๆ ในเครือข่ายภายใน และตรวจสอบขอบเขตของระบบ API ที่เชื่อมต่อกับแอปพลิเคชันหลัก |
| 4 | described | T1056 Input Capture | ผู้โจมตีติดตั้งโปรแกรมจับคีย์บอร์ดเพื่อบันทึกการพิมพ์รหัสผ่านและข้อมูลการเข้าสู่ระบบของผู้ใช้คนอื่น |
| 5 | described | T1041 Exfiltration Over C2 Channel | ส่งข้อมูลที่รวบรวมได้ผ่าน Command and Control server ในต่างประเทศ |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_033  (source: Operation CuckooBees C0012)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทเอกชนแห่งหนึ่งในจังหวัดสมุทรปราการที่ประกอบธุรกิจด้านการจัดการสินค้าคงคลังแจ้งความว่าระบบเซิร์ฟเวอร์ของพวกเขาถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log พบว่าผู้โจมตีได้เข้าสู่ระบบผ่านการใช้ประโยชน์จากบริการ Remote Desktop Protocol ที่เปิดให้บนอินเทอร์เน็ตสาธารณะโดยไม่มีการป้องกันที่เพียงพอ ต่อมาผู้โจมตีทำการ System Owner/User Discovery เพื่อระบุตัวตนของผู้ใช้งานในระบบและสิทธิการเข้าถึงของแต่ละบัญชี จากนั้นผู้โจมตีดำเนินการเก็บรวบรวมข้อมูลจากระบบท้องถิ่นโดยการสแกนและคัดลอกไฟล์ที่สำคัญ รวมถึงไฟล์คำตั้งค่าเซิร์ฟเวอร์และฐานข้อมูลลูกค้า ซึ่งสิ่งเหล่านี้ถูกตรวจพบในเครื่องเก็บข้อมูลชั่วคราวของระบบปฏิบัติการ

*EN:* On 22 February 2569, a private company in Samut Prakan Province engaged in inventory management services reported unauthorized access to their server system. Log analysis revealed that the attacker gained access to the system through exploitation of Remote Desktop Protocol service exposed on the public internet without adequate protection. Subsequently, the attacker performed System Owner/User Discovery to identify user identities in the system and access privileges of each account. The attacker then collected data from the local system by scanning and copying critical files, including server configuration files and customer database, which were discovered in the temporary storage area of the operating system.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1133 External Remote Services | เข้าสู่ระบบผ่านการใช้ประโยชน์จากบริการ Remote Desktop Protocol ที่เปิดให้บนอินเทอร์เน็ตสาธารณะโดยไม่มีการป้องกันที่เพียงพอ |
| 2 | named | T1033 System Owner/User Discovery | ผู้โจมตีทำการ System Owner/User Discovery เพื่อระบุตัวตนของผู้ใช้งานในระบบและสิทธิการเข้าถึงของแต่ละบัญชี |
| 3 | described | T1005 Data from Local System | ผู้โจมตีดำเนินการเก็บรวบรวมข้อมูลจากระบบท้องถิ่นโดยการสแกนและคัดลอกไฟล์ที่สำคัญ รวมถึงไฟล์คำตั้งค่าเซิร์ฟเวอร์และฐานข้อมูลลูกค้า |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_034  (source: ShadowRay C0045)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการเงินรายหนึ่งในจังหวัดกรุงเทพมหานคร แจ้งความต่อสำนักงานสอบสวนว่าระบบ web portal ของบริษัทถูกเข้าถึงโดยไม่ได้รับอนุญาต จากการตรวจสอบ log เซิร์ฟเวอร์พบว่าผู้โจมตีได้ใช้ Exploit Public-Facing Application ผ่านช่องโหว่ SQL injection ในหน้า login เพื่อเข้าสู่ระบบ ต่อมาจากการวิเคราะห์ไฟล์ log ระบบปฏิบัติการพบการเรียกใช้คำสั่ง kernel exploit ที่เพิ่มสิทธิ์ผู้ใช้จากระดับ www-data เป็น root ซึ่งผู้โจมตีได้ดำเนินการทำให้สำเร็จภายในเวลา 47 นาที จากนั้นพบการเชื่อมต่อ outbound ไปยังเซิร์ฟเวอร์ต่างประเทศ พร้อมกับการดาวน์โหลด malware ชื่อ Ingress Tool Transfer ขนาด 2.3 MB ซึ่งมีชื่อไฟล์ว่า sysmon.exe ไปยังไดเรกทอรี่ /tmp เพื่อใช้ในการควบคุมระบบต่อไป

*EN:* On 22 February 2569, a financial services company in Bangkok reported to the investigation office that its web portal system had been accessed without authorization. From server log analysis, it was found that the attacker used Exploit Public-Facing Application through an SQL injection vulnerability on the login page to gain initial access. Subsequently, from analysis of the operating system log files, execution of a kernel exploit command was detected that escalated user privileges from www-data to root, which the attacker accomplished within 47 minutes. Thereafter, outbound connections to foreign servers were identified, accompanied by the download of malware named Ingress Tool Transfer sized 2.3 MB with the filename sysmon.exe into the /tmp directory for subsequent system control.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | named | T1190 Exploit Public-Facing Application | ผู้โจมตีได้ใช้ Exploit Public-Facing Application ผ่านช่องโหว่ SQL injection ในหน้า login |
| 2 | described | T1068 Exploitation for Privilege Escalation | จากการวิเคราะห์ไฟล์ log ระบบปฏิบัติการพบการเรียกใช้คำสั่ง kernel exploit ที่เพิ่มสิทธิ์ผู้ใช้จากระดับ www-data เป็น root |
| 3 | named | T1105 Ingress Tool Transfer | พบการเชื่อมต่อ outbound ไปยังเซิร์ฟเวอร์ต่างประเทศ พร้อมกับการดาวน์โหลด malware ชื่อ Ingress Tool Transfer ขนาด 2.3 MB |

- [ ] ผ่าน / แก้แล้ว

## inc_camp2_035  (source: C0015 C0015)

> เมื่อวันที่ 22 กุมภาพันธ์ 2569 บริษัทให้บริการด้านการเงินแห่งหนึ่งในจังหวัดกรุงเทพ ได้รับแจ้งเบาะแสจากฝ่ายเทคโนโลยีสารสนเทศว่าพบกิจกรรมที่น่าสงสัยบนเซิร์ฟเวอร์ระบบบัญชีลูกค้า จากการตรวจสอบ log พบว่าผู้โจมตีได้ทำการค้นหาและแสดงรายชื่อของกระบวนการที่กำลังทำงาน (running processes) บนเครื่องที่ถูกประนีประนวม เพื่อระบุว่าเครื่องมือหรือบริการใดที่มีอยู่ในระบบ ต่อมา ผู้โจมตีได้ทำการ Lateral Tool Transfer โดยส่งเครื่องมือ penetration testing ชื่อ Mimikatz ไปยังเซิร์ฟเวอร์อื่นภายในเครือข่ายภายในองค์กร เพื่อให้สามารถเข้าถึงระบบอื่น ๆ ได้ สุดท้าย จากการวิเคราะห์พยานหลักฐานพบว่าผู้โจมตีได้ทำการแบ่งข้อมูลลูกค้าที่ละเอียดอ่อนออกเป็นส่วน ๆ ขนาดเล็ก โดยแต่ละครั้งการส่งข้อมูลมีขนาดไม่เกิน 50 megabytes เพื่อหลีกเลี่ยงการตรวจจับจากระบบ Data Loss Prevention

*EN:* On 22 February 2569, a financial services company in Bangkok received an alert from its information technology department regarding suspicious activity on the customer accounting server. Analysis of system logs revealed that the attacker enumerated running processes on the compromised machine to identify what tools or services were available in the system. Subsequently, the attacker performed Lateral Tool Transfer by deploying the penetration testing tool Mimikatz to other servers within the organization's internal network to access additional systems. Finally, forensic examination showed that the attacker segmented sensitive customer data into small portions, with each data transfer not exceeding 50 megabytes, to evade detection by the Data Loss Prevention system.

| # | cue_type | technique | cue |
|---|----------|-----------|-----|
| 1 | described | T1057 Process Discovery | ผู้โจมตีได้ทำการค้นหาและแสดงรายชื่อของกระบวนการที่กำลังทำงาน (running processes) บนเครื่องที่ถูกประนีประนวม เพื่อระบุว่าเครื่องมือหรือบริการใดที่มีอยู่ในระบบ |
| 2 | named | T1570 Lateral Tool Transfer | ผู้โจมตีได้ทำการ Lateral Tool Transfer โดยส่งเครื่องมือ penetration testing ชื่อ Mimikatz ไปยังเซิร์ฟเวอร์อื่นภายในเครือข่ายภายในองค์กร |
| 3 | described | T1030 Data Transfer Size Limits | ผู้โจมตีได้ทำการแบ่งข้อมูลลูกค้าที่ละเอียดอ่อนออกเป็นส่วน ๆ ขนาดเล็ก โดยแต่ละครั้งการส่งข้อมูลมีขนาดไม่เกิน 50 megabytes เพื่อหลีกเลี่ยงการตรวจจับจากระบบ Data Loss Prevention |

- [ ] ผ่าน / แก้แล้ว
