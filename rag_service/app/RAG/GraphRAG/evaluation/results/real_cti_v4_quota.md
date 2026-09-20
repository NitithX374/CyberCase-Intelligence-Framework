[EVAL] Loaded 100 evaluation samples from CTI_dataset.json
[EVAL] Samples for evaluation: 100

[EVAL] Running retriever evaluation (100 samples with ground truth)
[EVAL] Loading embedding model BAAI/bge-m3...
[EVAL] Arms: quota
[EVAL] Sub-technique -> parent map: 522 entries

════════════════════════════════════════════════════════════
  Evaluating: Vector Retriever (ChromaDB)
════════════════════════════════════════════════════════════
  [SKIP] not selected in --arms

════════════════════════════════════════════════════════════
  Evaluating: Graph Retriever (Neo4j)
════════════════════════════════════════════════════════════
  [SKIP] not selected in --arms

════════════════════════════════════════════════════════════
  Evaluating: Hybrid Retriever (Vector + Graph)
════════════════════════════════════════════════════════════
  [SKIP] not selected in --arms

════════════════════════════════════════════════════════════
  Evaluating: Hybrid + Quota (decompose + per-query quota)
════════════════════════════════════════════════════════════
[VECTOR] Using Qdrant Cloud at https://840f3e20-49f1-4f47-bd34-c20996e34b9c.us-east-2-0.aws.cloud.qdrant.io
[VECTOR] Entity collection: 2195 docs
[VECTOR] Relationship collection: 21347 docs
[GRAPH] Connected to neo4j+s://71750b02.databases.neo4j.io
[RERANKER] Loading BAAI/bge-reranker-v2-m3 on cuda...
[RERANKER] Ready
[HYBRID] GraphRAG retriever initialized
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่งในจังหวัดนนทบุรีแจ้งความว่าระบบร...
[RETRIEVE] Query: เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่งในจังหวัดนนทบุรีแจ้งความว่าระบบร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.097), ShimRat (0.078), Exploit Public-Facing Application (0.007), Application Shimming (0.003), Clambling (0.001), Application Layer Protocol (0.000), Email Forwarding Rule (0.000), Exploitation for Client Execution (0.000), File Transfer Protocols (0.000), Re-opened Applications (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → ShimRat (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 2/9: ส่งคำสั่งฐานข้อมูลแทรกผ่านช่องกรอกข้อมูลบนเว็บสาธารณะ (SQL Injection)...
[RETRIEVE] Query: ส่งคำสั่งฐานข้อมูลแทรกผ่านช่องกรอกข้อมูลบนเว็บสาธารณะ (SQL Injection)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Havij (0.137), Axiom (0.128), Havij (0.034), Content Injection (0.009), Template Injection (0.006), HTRAN (0.005), Dynamic-link Library Injection (0.002), Cardinal RAT (0.002), Process Injection (0.002), SQL Stored Procedures (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Havij (2 neighbors, 2 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Axiom (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 3/9: วางไฟล์สคริปต์สำหรับสั่งการระยะไกลบนเว็บเซิร์ฟเวอร์...
[RETRIEVE] Query: วางไฟล์สคริปต์สำหรับสั่งการระยะไกลบนเว็บเซิร์ฟเวอร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Web Shell (0.194), RemoteCMD (0.011), xCmd (0.008), Terminal Services DLL (0.006), CrackMapExec (0.005), Cobalt Strike (0.003), Visual Basic (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Web Shell (71 neighbors, 71 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 4/9: ใช้ Application Shimming ให้โปรแกรมของผู้โจมตีทำงานทุกครั้งที่เครื่องเริ่มระบบ...
[RETRIEVE] Query: ใช้ Application Shimming ให้โปรแกรมของผู้โจมตีทำงานทุกครั้งที่เครื่องเริ่มระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SDBbot (0.534), ShimRat (0.372), Application Shimming (0.348), Pillowmint (0.329), FIN7 (0.176), Create or Modify System Process (0.024), BOOKWORM (0.024), System Services (0.006), Re-opened Applications (0.005), Launch Daemon (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SDBbot (25 neighbors, 25 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → Pillowmint (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 5/9: เข้าถึงเครื่องแม่ข่ายที่ทำหน้าที่ควบคุมบัญชีผู้ใช้ขององค์กร...
[RETRIEVE] Query: เข้าถึงเครื่องแม่ข่ายที่ทำหน้าที่ควบคุมบัญชีผู้ใช้ขององค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cloud Account (0.038), DCSync (0.008), Net (0.002), Pacu (0.002), User Account Control (0.002), AADInternals (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Cloud Account (11 neighbors, 11 edges)
           → DCSync (14 neighbors, 14 edges)
           → Pacu (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 6/9: ค้นหารายชื่อเครื่องลูกข่ายอื่นในวงเครือข่าย...
[RETRIEVE] Query: ค้นหารายชื่อเครื่องลูกข่ายอื่นในวงเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pod Enumeration (0.047), Remote System Discovery (0.027), FIVEHANDS (0.010), APT3 (0.007), Cyclops Blink (0.005), Network Service Discovery (0.003), Kwampirs (0.003), System Network Connections Discovery (0.002), Domain Account (0.001), Internet Connection Discovery (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Pod Enumeration (0 neighbors, 0 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
           → FIVEHANDS (8 neighbors, 8 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
[RETRIEVE-QUOTA] Query 7/9: รวบรวมรายละเอียดของเครื่องคอมพิวเตอร์พนักงาน...
[RETRIEVE] Query: รวบรวมรายละเอียดของเครื่องคอมพิวเตอร์พนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Systeminfo (0.077), Malteiro (0.012), ZxShell (0.005), Peripheral Device Discovery (0.005), OSInfo (0.000), Cobian RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Systeminfo (14 neighbors, 14 edges)
           → Malteiro (13 neighbors, 13 edges)
           → System Information Discovery (426 neighbors, 426 edges)
[RETRIEVE-QUOTA] Query 8/9: บันทึกภาพหน้าจอเครื่องคอมพิวเตอร์พนักงาน...
[RETRIEVE] Query: บันทึกภาพหน้าจอเครื่องคอมพิวเตอร์พนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Screen Capture (0.054), Mandrake (0.018), AsyncRAT (0.016), Video Capture (0.005), Cobian RAT (0.000), Image Deletion (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Screen Capture (173 neighbors, 173 edges)
           → Mandrake (25 neighbors, 25 edges)
           → Screen Capture (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 9/9: ส่งรายละเอียดเครื่องและภาพหน้าจอไปยังเครื่องปลายทางของคนร้าย...
[RETRIEVE] Query: ส่งรายละเอียดเครื่องและภาพหน้าจอไปยังเครื่องปลายทางของคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NKAbuse (0.019), Ingress Tool Transfer (0.010), Phishing (0.007), Communication Through Removable Media (0.007), zwShell (0.007), USBStealer (0.005), Manjusaka (0.005), Spearphishing Voice (0.003), Input Injection (0.002), Content Injection (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → NKAbuse (8 neighbors, 8 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [1/100] retrieved=227 relevant=4 latency=38661ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 3 ตุลาคม 2565 โรงพยาบาลเอกชนแห่งหนึ่งในจังหวัดเชียงใหม่แจ้งว่าระบบเว...
[RETRIEVE] Query: เมื่อวันที่ 3 ตุลาคม 2565 โรงพยาบาลเอกชนแห่งหนึ่งในจังหวัดเชียงใหม่แจ้งว่าระบบเว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.126), Windows Credential Editor (0.024), Ember Bear (0.010), Mustang Panda (0.008), OS Credential Dumping (0.007), Password Cracking (0.002), Credential Access Protection (0.001), IceApple (0.000), Credential Stuffing (0.000), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 2/9: ทำ Credential Dumping ดึงค่าแฮชรหัสผ่านจากหน่วยความจำของเครื่องแม่ข่าย...
[RETRIEVE] Query: ทำ Credential Dumping ดึงค่าแฮชรหัสผ่านจากหน่วยความจำของเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OS Credential Dumping (0.784), Cachedump (0.448), Cachedump (0.167), Credentials In Files (0.141), Windows Credential Editor (0.140), Password Cracking (0.121), Axiom (0.110), Credential Access Protection (0.082), Credential Access (0.061), Security Account Manager (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Cachedump (2 neighbors, 2 edges)
           → Cached Domain Credentials (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 3/9: นำค่าแฮชรหัสผ่านไปทำ Pass the Hash เข้าสู่บัญชีสิทธิ์ผู้ดูแลระบบ...
[RETRIEVE] Query: นำค่าแฮชรหัสผ่านไปทำ Pass the Hash เข้าสู่บัญชีสิทธิ์ผู้ดูแลระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pass the Hash (0.775), Pass-The-Hash Toolkit (0.660), Pass-The-Hash Toolkit (0.173), Update Software (0.138), HOPLIGHT (0.022), Password Cracking (0.015), Cached Domain Credentials (0.014), Pass the Ticket (0.008), Modify Authentication Process (0.001), Dynamic API Resolution (0.000)
[RETRIEVE] Graph expansion: 2 subgraphs
           → Pass the Hash (29 neighbors, 29 edges)
           → Pass-The-Hash Toolkit (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 4/9: ใช้บัญชีผู้ดูแลระบบเข้าถึงระบบบริหารจัดการเครื่องเสมือนของโรงพยาบาล...
[RETRIEVE] Query: ใช้บัญชีผู้ดูแลระบบเข้าถึงระบบบริหารจัดการเครื่องเสมือนของโรงพยาบาล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: User Account Management (0.024), Privileged Account Management (0.004), Cloud Account (0.001), AADInternals (0.000), Security Account Manager (0.000), Cloud Administration Command (0.000), Windows Remote Management (0.000), SVCReady (0.000), Direct Cloud VM Connections (0.000), UACMe (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → User Account Management (119 neighbors, 119 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Privileged Account Management (112 neighbors, 112 edges)
           → Cloud Administration Command (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/9: เปลี่ยนรหัสผ่านบัญชีผู้ดูแลเครื่องแม่ข่ายเสมือนเพื่อป้องกันเจ้าหน้าที่เข้าใช้งาน...
[RETRIEVE] Query: เปลี่ยนรหัสผ่านบัญชีผู้ดูแลเครื่องแม่ข่ายเสมือนเพื่อป้องกันเจ้าหน้าที่เข้าใช้งาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Password Policies (0.003), Account Access Removal (0.002), User Account Control (0.001), Modify Authentication Process (0.001), Update Software (0.001), Reversible Encryption (0.001), Domain or Tenant Policy Modification (0.000), SSH (0.000), Active Directory Configuration (0.000), Windows Host Firewall (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Password Policies (47 neighbors, 47 edges)
           → Remote Services (23 neighbors, 23 edges)
           → Account Access Removal (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 6/9: ติดตั้งโปรแกรมสร้างช่องทางเชื่อมต่อออกสู่ภายนอกผ่านผู้ให้บริการรายหนึ่ง...
[RETRIEVE] Query: ติดตั้งโปรแกรมสร้างช่องทางเชื่อมต่อออกสู่ภายนอกผ่านผู้ให้บริการรายหนึ่ง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Proxy (0.006), Impacket (0.003), RemoteUtilities (0.003), Cobian RAT (0.002), PsExec (0.001), CrossRAT (0.001), Visual Basic (0.000), PsExec (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → External Proxy (27 neighbors, 27 edges)
           → RemoteUtilities (5 neighbors, 5 edges)
           → Msiexec (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 7/9: ลำเลียงข้อมูลของโรงพยาบาลออกไปผ่านช่องทางเชื่อมต่อภายนอก...
[RETRIEVE] Query: ลำเลียงข้อมูลของโรงพยาบาลออกไปผ่านช่องทางเชื่อมต่อภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Out-of-Band Communications Channel (0.009), Out-of-Band Communications Channel (0.004), BlackByte (0.004), External Proxy (0.002), Communication Through Removable Media (0.001), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Out-of-Band Communications Channel (7 neighbors, 7 edges)
           → Data from Information Repositories (19 neighbors, 19 edges)
           → BlackByte (56 neighbors, 56 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
[RETRIEVE-QUOTA] Query 8/9: เชื่อมต่อเข้าเครื่องแม่ข่ายเสมือนทุกเครื่องผ่าน SSH...
[RETRIEVE] Query: เชื่อมต่อเข้าเครื่องแม่ข่ายเสมือนทุกเครื่องผ่าน SSH...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH Hijacking (0.081), SSH (0.041), FIN7 (0.005), reGeorg (0.005), Cobalt Strike (0.004), Leviathan (0.002), SSH Authorized Keys (0.002), Remote Services (0.001), Kessel (0.001), SMB/Windows Admin Shares (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SSH Hijacking (8 neighbors, 8 edges)
           → SSH (33 neighbors, 33 edges)
           → FIN7 (86 neighbors, 86 edges)
[RETRIEVE-QUOTA] Query 9/9: สั่งเข้ารหัสลับข้อมูลทั้งหมดบนเครื่องแม่ข่ายเสมือนจนระบบหยุดให้บริการ...
[RETRIEVE] Query: สั่งเข้ารหัสลับข้อมูลทั้งหมดบนเครื่องแม่ข่ายเสมือนจนระบบหยุดให้บริการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Royal (0.006), Wizard Spider (0.006), Encrypt Sensitive Information (0.002), Disable Crypto Hardware (0.001), SSH (0.000), Process Hollowing (0.000), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Royal (15 neighbors, 15 edges)
           → Service Stop (61 neighbors, 61 edges)
           → Wizard Spider (86 neighbors, 86 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [2/100] retrieved=144 relevant=5 latency=37110ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 18 พฤศจิกายน 2565 สหกรณ์แห่งหนึ่งในจังหวัดขอนแก่นได้รับแจ้งเบาะแสจาก...
[RETRIEVE] Query: เมื่อวันที่ 18 พฤศจิกายน 2565 สหกรณ์แห่งหนึ่งในจังหวัดขอนแก่นได้รับแจ้งเบาะแสจาก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: KGH_SPY (0.037), Maze (0.010), TianySpy (0.008), H1N1 (0.001), Lokibot (0.001), Magic Hound (0.000), Threat Group-3390 (0.000), ShadowPad (0.000), Clear Windows Event Logs (0.000), Clear Linux or Mac System Logs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → KGH_SPY (21 neighbors, 21 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Maze (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 2/9: ล็อกอินจากภายนอกผ่านช่องทางเชื่อมต่อระยะไกลด้วยชื่อผู้ใช้และรหัสผ่านชั้นเดียว (V...
[RETRIEVE] Query: ล็อกอินจากภายนอกผ่านช่องทางเชื่อมต่อระยะไกลด้วยชื่อผู้ใช้และรหัสผ่านชั้นเดียว (V...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT18 (0.518), Remote Services (0.515), External Remote Services (0.462), APT18 (0.306), Remote Service Session Hijacking (0.200), Valid Accounts (0.182), Remote Desktop Protocol (0.060), Windows Remote Management (0.046), User Account Management (0.031), Privileged Account Management (0.014)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Remote Services (23 neighbors, 23 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → APT18 (17 neighbors, 17 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] Query 3/9: ส่งอีเมลแนบไฟล์อันตรายถึงพนักงาน (Phishing: Spearphishing Attachment)...
[RETRIEVE] Query: ส่งอีเมลแนบไฟล์อันตรายถึงพนักงาน (Phishing: Spearphishing Attachment)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT12 (0.930), Spearphishing Attachment (0.927), admin@338 (0.920), Saint Bear (0.780), Spearphishing Attachment (0.767), Spearphishing Link (0.733), Phishing (0.702), CURIUM (0.666), Phishing for Information (0.024), Internal Spearphishing (0.023)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → APT12 (8 neighbors, 8 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/9: ยิงคำสั่งโจมตีช่องโหว่ที่ยังไม่ได้ปรับปรุงบนเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ (...
[RETRIEVE] Query: ยิงคำสั่งโจมตีช่องโหว่ที่ยังไม่ได้ปรับปรุงบนเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ (...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.383), Sandworm Team (0.351), Leviathan (0.204), Havij (0.177), Network Segmentation (0.142), Exploitation for Client Execution (0.004), Exploitation for Credential Access (0.002), Exploit Protection (0.001), Exploits (0.001), Multi-factor Authentication (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Sandworm Team (113 neighbors, 113 edges)
           → Leviathan (68 neighbors, 68 edges)
[RETRIEVE-QUOTA] Query 5/9: ตรวจหารายการโปรแกรมที่กำลังทำงานอยู่บนเครื่องแม่ข่าย (Process Discovery)...
[RETRIEVE] Query: ตรวจหารายการโปรแกรมที่กำลังทำงานอยู่บนเครื่องแม่ข่าย (Process Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Process Discovery (0.635), Tasklist (0.407), KillDisk (0.288), DRATzarus (0.222), Taidoor (0.146), Tasklist (0.122), Internet Connection Discovery (0.003), System Owner/User Discovery (0.002), System Network Connections Discovery (0.002), Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Process Discovery (320 neighbors, 320 edges)
           → Tasklist (19 neighbors, 19 edges)
           → KillDisk (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 6/9: ตรวจหาโปรแกรมสำรองข้อมูลและโปรแกรมป้องกันไวรัสที่กำลังทำงานอยู่ (Software Discov...
[RETRIEVE] Query: ตรวจหาโปรแกรมสำรองข้อมูลและโปรแกรมป้องกันไวรัสที่กำลังทำงานอยู่ (Software Discov...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DustySky (0.666), Security Software Discovery (0.605), Backup Software Discovery (0.587), Software Discovery (0.412), S.O.V.A. (0.401), OSInfo (0.047), Process Discovery (0.016), HOPLIGHT (0.004), Discovery (0.001), Exploitation for Defense Impairment (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Security Software Discovery (144 neighbors, 144 edges)
           → Backup Software Discovery (4 neighbors, 4 edges)
           → DustySky (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 7/9: สั่งหยุดโปรแกรมสำรองข้อมูลทีละรายการเพื่อขัดขวางการกู้คืนระบบ (Inhibit System Re...
[RETRIEVE] Query: สั่งหยุดโปรแกรมสำรองข้อมูลทีละรายการเพื่อขัดขวางการกู้คืนระบบ (Inhibit System Re...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Conficker (0.859), Inhibit System Recovery (0.742), EKANS (0.690), Execution Prevention (0.623), Operating System Configuration (0.539), Backup Software Discovery (0.079), System Shutdown/Reboot (0.018), Service Stop (0.006), Systemd Service (0.002), Limit Hardware Installation (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → Conficker (13 neighbors, 13 edges)
           → EKANS (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 8/9: สั่งหยุดโปรแกรมป้องกันไวรัสเพื่อทำให้การป้องกันระบบลดลง (Impair Defenses)...
[RETRIEVE] Query: สั่งหยุดโปรแกรมป้องกันไวรัสเพื่อทำให้การป้องกันระบบลดลง (Impair Defenses)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Defense Impairment (0.133), User Guidance (0.059), Exploitation for Defense Impairment (0.041), System Partition Integrity (0.031), Pysa (0.017), Disable or Remove Feature or Program (0.002), Execution Prevention (0.002), System Shutdown/Reboot (0.001), Execution Prevention (0.001), Local Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Defense Impairment (56 neighbors, 56 edges)
           → User Guidance (49 neighbors, 49 edges)
           → Impair Defenses (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 9/9: เข้ารหัสลับข้อมูลสมาชิกทั้งหมดบนเครื่องแม่ข่าย (Data Encrypted for Impact)...
[RETRIEVE] Query: เข้ารหัสลับข้อมูลสมาชิกทั้งหมดบนเครื่องแม่ข่าย (Data Encrypted for Impact)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Encrypted for Impact (0.655), SynAck (0.566), Avaddon (0.403), S.O.V.A. (0.322), ProLock (0.279), Encrypt Sensitive Information (0.017), Impact (0.005), Reversible Encryption (0.002), Backup Software Discovery (0.002), Account Access Removal (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → SynAck (14 neighbors, 14 edges)
           → Avaddon (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [3/100] retrieved=459 relevant=3 latency=40673ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 9 ตุลาคม 2563 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Query: เมื่อวันที่ 9 ตุลาคม 2563 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Storm-1811 (0.033), LockBit 2.0 (0.030), MuddyWater (0.016), Ryuk (0.002), Registry Run Keys / Startup Folder (0.000), Query Registry (0.000), Modify Registry (0.000), Office Test (0.000), Windows Registry Key Modification (0.000), Windows Registry Key Access (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Storm-1811 (38 neighbors, 38 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 2/7: อีเมล Phishing แอบอ้างเป็นหนังสือเชิญประชุมพร้อมลิงก์และไฟล์เอกสารแนบ...
[RETRIEVE] Query: อีเมล Phishing แอบอ้างเป็นหนังสือเชิญประชุมพร้อมลิงก์และไฟล์เอกสารแนบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Molerats (0.825), Spearphishing Link (0.517), Spearphishing Attachment (0.121), Spearphishing Attachment (0.092), AADInternals (0.050), Phishing (0.043), Spearphishing Link (0.036), VOID MANTICORE (0.007), Phishing for Information (0.005), Kimsuky (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Molerats (22 neighbors, 22 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Spearphishing Link (93 neighbors, 93 edges)
[RETRIEVE-QUOTA] Query 3/7: เปิดไฟล์เอกสารแนบเพื่อเรียกใช้สคริปต์บนเครื่อง...
[RETRIEVE] Query: เปิดไฟล์เอกสารแนบเพื่อเรียกใช้สคริปต์บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Malicious File (0.041), TAINTEDSCRIBE (0.005), Forfiles (0.005), Re-opened Applications (0.002), Spica (0.002), BackConfig (0.001), Expand (0.001), Expand (0.001), Change Default File Association (0.001), xCmd (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Malicious File (202 neighbors, 202 edges)
           → TAINTEDSCRIBE (17 neighbors, 17 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 4/7: สคริปต์สร้าง Registry Run Key เพื่อให้ทำงานทุกครั้งที่เปิดเครื่อง...
[RETRIEVE] Query: สคริปต์สร้าง Registry Run Key เพื่อให้ทำงานทุกครั้งที่เปิดเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NanoCore (0.978), Ursnif (0.694), Registry Run Keys / Startup Folder (0.666), LockBit 2.0 (0.521), Ryuk (0.411), Office Test (0.176), Boot or Logon Autostart Execution (0.022), Active Setup (0.020), Windows Registry Key Modification (0.003), Windows Registry Key Access (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → NanoCore (17 neighbors, 17 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → Ursnif (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 5/7: เก็บรวบรวมชื่อเครื่องและรุ่นของระบบปฏิบัติการ...
[RETRIEVE] Query: เก็บรวบรวมชื่อเครื่องและรุ่นของระบบปฏิบัติการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Malteiro (0.706), Kwampirs (0.335), Systeminfo (0.209), nbtstat (0.012), Nltest (0.003), Wevtutil (0.002), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Malteiro (13 neighbors, 13 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Kwampirs (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 6/7: เก็บรวบรวมรายการซอฟต์แวร์ที่ติดตั้งบนเครื่อง...
[RETRIEVE] Query: เก็บรวบรวมรายการซอฟต์แวร์ที่ติดตั้งบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: GPlayed (0.903), BOULDSPY (0.597), Systeminfo (0.181), Tasklist (0.125), ifconfig (0.052), spwebmember (0.035), CrossRAT (0.001), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → GPlayed (18 neighbors, 18 edges)
           → Software Discovery (56 neighbors, 56 edges)
           → BOULDSPY (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งข้อมูลรายละเอียดเครื่องไปยังเครื่องสั่งการของคนร้ายเพื่อรอรับคำสั่งต่อไป...
[RETRIEVE] Query: ส่งข้อมูลรายละเอียดเครื่องไปยังเครื่องสั่งการของคนร้ายเพื่อรอรับคำสั่งต่อไป...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MobileOrder (0.036), Gustuff (0.024), POWRUNER (0.009), Pisloader (0.008), ECCENTRICBANDWAGON (0.005), Command and Control (0.003), Trap (0.001), Input Injection (0.001), System Services (0.001), KernelCallbackTable (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → MobileOrder (8 neighbors, 8 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Gustuff (15 neighbors, 15 edges)
           → System Network Configuration Discovery (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [4/100] retrieved=455 relevant=3 latency=33694ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 22 กุมภาพันธ์ 2567 บริษัทรับเหมาก่อสร้างแห่งหนึ่งในจังหวัดระยองแจ้งว...
[RETRIEVE] Query: เมื่อวันที่ 22 กุมภาพันธ์ 2567 บริษัทรับเหมาก่อสร้างแห่งหนึ่งในจังหวัดระยองแจ้งว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: menuPass (0.001), XLoader (0.000), Darkhotel (0.000), FIN8 (0.000), System Script Proxy Execution (0.000), Password Managers (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Pikabot (0.000), Filter Network Traffic (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → menuPass (71 neighbors, 71 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Darkhotel (24 neighbors, 24 edges)
           → Process Discovery (320 neighbors, 320 edges)
[RETRIEVE-QUOTA] Query 2/8: นำไฟล์โปรแกรมจากเครื่องภายนอกเข้ามาเก็บไว้บนดิสก์ของเครื่องที่ยึดครองได้ (Ingres...
[RETRIEVE] Query: นำไฟล์โปรแกรมจากเครื่องภายนอกเข้ามาเก็บไว้บนดิสก์ของเครื่องที่ยึดครองได้ (Ingres...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.618), Ingress Tool Transfer (0.597), Lateral Tool Transfer (0.379), Industroyer (0.226), Upload Malware (0.059), ftp (0.016), File Deletion (0.013), PsExec (0.011), BITS Jobs (0.002), Upload Tool (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → cmd (13 neighbors, 13 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 3/8: สั่งโปรแกรมที่ดาวน์โหลดมาให้ทำงานบนเครื่องที่ยึดครองได้...
[RETRIEVE] Query: สั่งโปรแกรมที่ดาวน์โหลดมาให้ทำงานบนเครื่องที่ยึดครองได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackConfig (0.316), PsExec (0.014), APT3 (0.002), cmd (0.002), Installer Packages (0.001), Cardinal RAT (0.001), CrossRAT (0.001), Executable Installer File Permissions Weakness (0.001), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BackConfig (17 neighbors, 17 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → PsExec (49 neighbors, 49 edges)
[RETRIEVE-QUOTA] Query 4/8: อ่านแฟ้มที่โปรแกรมท่องเว็บใช้เก็บรหัสผ่านของผู้ใช้...
[RETRIEVE] Query: อ่านแฟ้มที่โปรแกรมท่องเว็บใช้เก็บรหัสผ่านของผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.683), TrickBot (0.421), TrickBot (0.240), APT3 (0.206), Empire (0.117), Password Managers (0.032), Credentials in Registry (0.012), Cachedump (0.006), gsecdump (0.005), Windows Credential Manager (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → TrickBot (57 neighbors, 57 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 5/8: ถอดข้อมูลบัญชีและรหัสผ่านที่บันทึกไว้ในเบราว์เซอร์ออกมา...
[RETRIEVE] Query: ถอดข้อมูลบัญชีและรหัสผ่านที่บันทึกไว้ในเบราว์เซอร์ออกมา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.406), PLEAD (0.110), Cachedump (0.046), Lslsass (0.017), Neoichor (0.014), CrossRAT (0.001), Windows Credential Manager (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → PLEAD (16 neighbors, 16 edges)
           → Cachedump (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 6/8: ดาวน์โหลดไฟล์โปรแกรมอีกตัวหนึ่งเข้ามาไว้บนเครื่องเดียวกัน (Ingress Tool Transfer...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมอีกตัวหนึ่งเข้ามาไว้บนเครื่องเดียวกัน (Ingress Tool Transfer...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TYPEFRAME (0.743), Lateral Tool Transfer (0.657), Ingress Tool Transfer (0.597), cmd (0.508), Industroyer (0.369), ftp (0.098), Upload Malware (0.093), PsExec (0.044), Upload Tool (0.008), BITS Jobs (0.006)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → TYPEFRAME (16 neighbors, 16 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 7/8: สั่งโปรแกรมดักบันทึกแป้นพิมพ์ให้ทำงานเบื้องหลัง...
[RETRIEVE] Query: สั่งโปรแกรมดักบันทึกแป้นพิมพ์ให้ทำงานเบื้องหลัง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AsyncRAT (0.008), DCRAT (0.005), Duqu (0.004), DarkWatchman (0.004), BUBBLEWRAP (0.002), PsExec (0.001), Print Processors (0.001), schtasks (0.001), Port Monitors (0.000), Scheduled Task (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → AsyncRAT (23 neighbors, 23 edges)
           → Keylogging (160 neighbors, 160 edges)
           → DCRAT (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 8/8: ดักบันทึกทุกปุ่มที่ผู้ใช้กดบนแป้นพิมพ์ลงไฟล์ข้อความที่ซ่อนไว้ในเครื่อง (Input Ca...
[RETRIEVE] Query: ดักบันทึกทุกปุ่มที่ผู้ใช้กดบนแป้นพิมพ์ลงไฟล์ข้อความที่ซ่อนไว้ในเครื่อง (Input Ca...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MacMa (0.654), Keylogging (0.292), BOOKWORM (0.125), Input Capture (0.098), Fysbis (0.043), Input Injection (0.039), Empire (0.037), Web Portal Capture (0.005), Video Capture (0.001), Audio Capture (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → MacMa (28 neighbors, 28 edges)
           → Keylogging (160 neighbors, 160 edges)
           → BOOKWORM (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [5/100] retrieved=758 relevant=3 latency=30883ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 24 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่า...
[RETRIEVE] Query: เมื่อวันที่ 24 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dok (0.008), AutoIt backdoor (0.002), PipeMon (0.001), System Script Proxy Execution (0.000), PipeMon (0.000), Adversary-in-the-Middle (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), ARP Cache Poisoning (0.000), Evil Twin (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Dok (11 neighbors, 11 edges)
           → AutoIt backdoor (6 neighbors, 6 edges)
           → PipeMon (24 neighbors, 24 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
[RETRIEVE-QUOTA] Query 2/7: ตัวติดตั้งโปรแกรมไม่พึงประสงค์วางไฟล์ประตูหลังที่เขียนด้วยภาษาไพทอนลงในเครื่อง...
[RETRIEVE] Query: ตัวติดตั้งโปรแกรมไม่พึงประสงค์วางไฟล์ประตูหลังที่เขียนด้วยภาษาไพทอนลงในเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DropBook (0.418), Heyoka Backdoor (0.045), Pteranodon (0.039), Pasam (0.022), TINYTYPHON (0.015), AutoIt backdoor (0.015), Pteranodon (0.014), PHOREAL (0.008), PipeMon (0.001), PoisonIvy (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DropBook (10 neighbors, 10 edges)
           → Heyoka Backdoor (16 neighbors, 16 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] Query 3/7: เพิ่มรายการเรียกใช้งานไฟล์ประตูหลังใน Windows Registry ให้ทำงานทุกครั้งที่เปิดเค...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานไฟล์ประตูหลังใน Windows Registry ให้ทำงานทุกครั้งที่เปิดเค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.818), DarkComet (0.720), LockBit 2.0 (0.387), Modify Registry (0.007), Active Setup (0.006), Windows Registry Key Modification (0.005), Windows Registry Key Access (0.004), Reg (0.003), Services Registry Permissions Weakness (0.002), Query Registry (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → DarkComet (21 neighbors, 21 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 4/7: ตั้งชื่อไฟล์ประตูหลังเลียนแบบชื่อผู้ผลิตซอฟต์แวร์รายใหญ่และโปรแกรมรับส่งอีเมลโดย...
[RETRIEVE] Query: ตั้งชื่อไฟล์ประตูหลังเลียนแบบชื่อผู้ผลิตซอฟต์แวร์รายใหญ่และโปรแกรมรับส่งอีเมลโดย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Masquerading (0.205), UPSTYLE (0.135), Masquerade File Type (0.066), Execution Prevention (0.030), SombRAT (0.013), User Training (0.006), Email Spoofing (0.004), Masquerade Account Name (0.001), Malicious File (0.001), Runtime Data Manipulation (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Masquerading (81 neighbors, 81 edges)
           → UPSTYLE (13 neighbors, 13 edges)
           → Masquerade File Type (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 5/7: ติดต่อกลับและรับคำสั่งจากคนร้ายผ่านแอปพลิเคชันสนทนายอดนิยมโดยใช้โพรโทคอลเว็บ (Ap...
[RETRIEVE] Query: ติดต่อกลับและรับคำสั่งจากคนร้ายผ่านแอปพลิเคชันสนทนายอดนิยมโดยใช้โพรโทคอลเว็บ (Ap...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Web Protocols (0.685), Application Layer Protocol (0.517), Mail Protocols (0.133), File Transfer Protocols (0.072), ShrinkLocker (0.060), SpeakUp (0.035), Non-Application Layer Protocol (0.026), PHOREAL (0.021), FRP (0.011), Protocol Tunneling (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Web Protocols (424 neighbors, 424 edges)
           → Application Layer Protocol (25 neighbors, 25 edges)
           → Mail Protocols (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 6/7: เข้ารหัสช่องทางสื่อสารกับคนร้ายผ่านโพรโทคอลเว็บ (Encrypted Channel)...
[RETRIEVE] Query: เข้ารหัสช่องทางสื่อสารกับคนร้ายผ่านโพรโทคอลเว็บ (Encrypted Channel)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Encrypted Channel (0.762), NETWIRE (0.214), Network Intrusion Prevention (0.163), Protocol Tunneling (0.086), Chaes (0.078), Exfiltration Over C2 Channel (0.025), ShrinkLocker (0.011), Data Encrypted for Impact (0.007), Out-of-Band Communications Channel (0.004), Encrypted/Encoded File (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Encrypted Channel (23 neighbors, 23 edges)
           → NETWIRE (49 neighbors, 49 edges)
           → Network Intrusion Prevention (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 7/7: แปลงข้อมูลด้วยการสลับตำแหน่งไบต์และเข้ารหัสข้อความเพื่อหลบเลี่ยงการตรวจจับ (Obfu...
[RETRIEVE] Query: แปลงข้อมูลด้วยการสลับตำแหน่งไบต์และเข้ารหัสข้อความเพื่อหลบเลี่ยงการตรวจจับ (Obfu...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Obfuscated Files or Information (0.931), Encrypted/Encoded File (0.843), Windshift (0.784), APT3 (0.740), Deobfuscate/Decode Files or Information (0.670), OBAD (0.600), PUBLOAD (0.240), Polymorphic Code (0.146), Compression (0.030), Malicious File (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [6/100] retrieved=540 relevant=4 latency=29918ms
[RETRIEVE-QUOTA] Query 1/4: เมื่อวันที่ 7 มีนาคม 2567 บริษัทโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งว่าเค...
[RETRIEVE] Query: เมื่อวันที่ 7 มีนาคม 2567 บริษัทโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งว่าเค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Comnie (0.009), Proxysvc (0.001), Lokibot (0.000), FIN8 (0.000), Hijack Execution Flow (0.000), Reg (0.000), CrossRAT (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Comnie (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Proxysvc (16 neighbors, 16 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 2/4: เพิ่มคีย์ใน Windows Registry ให้โปรแกรมของคนร้ายทำงานทุกครั้งที่ผู้ใช้ล็อกอินเข้...
[RETRIEVE] Query: เพิ่มคีย์ใน Windows Registry ให้โปรแกรมของคนร้ายทำงานทุกครั้งที่ผู้ใช้ล็อกอินเข้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: xCaon (0.975), Registry Run Keys / Startup Folder (0.899), Active Setup (0.768), DarkComet (0.273), Credentials in Registry (0.088), Modify Registry (0.045), CHOPSTICK (0.011), Reg (0.008), Query Registry (0.007), Reg (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → xCaon (12 neighbors, 12 edges)
           → Boot or Logon Autostart Execution (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 3/4: เรียกดูรุ่นและเวอร์ชันของระบบปฏิบัติการ ชื่อเครื่อง และรายละเอียดฮาร์ดแวร์...
[RETRIEVE] Query: เรียกดูรุ่นและเวอร์ชันของระบบปฏิบัติการ ชื่อเครื่อง และรายละเอียดฮาร์ดแวร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remsec (0.733), DarkWatchman (0.428), System Information Discovery (0.251), Systeminfo (0.105), ipconfig (0.004), nbtstat (0.001), Visual Basic (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Remsec (31 neighbors, 31 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → DarkWatchman (34 neighbors, 34 edges)
[RETRIEVE-QUOTA] Query 4/4: ไล่แจกแจงรายการโปรแกรมหรือกระบวนการที่กำลังทำงานอยู่ทั้งหมดบนเครื่อง...
[RETRIEVE] Query: ไล่แจกแจงรายการโปรแกรมหรือกระบวนการที่กำลังทำงานอยู่ทั้งหมดบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.440), Socksbot (0.250), Ryuk (0.163), Process Discovery (0.056), Forfiles (0.015), Cobian RAT (0.001), CrossRAT (0.001), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → Socksbot (5 neighbors, 5 edges)
           → Process Discovery (320 neighbors, 320 edges)
[RETRIEVE-QUOTA] 12 vectors (quota 3/query), 8 subgraphs from 4 queries
  [7/100] retrieved=594 relevant=3 latency=20833ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 15 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความว่ามีการเข้าถึงข้...
[RETRIEVE] Query: เมื่อวันที่ 15 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความว่ามีการเข้าถึงข้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OS Credential Dumping (0.475), Windows Credential Editor (0.439), Axiom (0.409), Credential Access (0.354), Mustang Panda (0.346), HOMEFRY (0.284), Suckfly (0.171), Credential Access Protection (0.029), Credential Stuffing (0.011), Credentials In Files (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Axiom (24 neighbors, 24 edges)
           → Credential Access (67 neighbors, 67 edges)
[RETRIEVE-QUOTA] Query 2/5: ใช้ Credential Dumping แทรกเข้าไปในหน่วยความจำของกระบวนการยืนยันตัวตนเพื่อดึงค่า...
[RETRIEVE] Query: ใช้ Credential Dumping แทรกเข้าไปในหน่วยความจำของกระบวนการยืนยันตัวตนเพื่อดึงค่า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OS Credential Dumping (0.768), Credential Access (0.503), IceApple (0.494), Mustang Panda (0.195), Credential Access Protection (0.161), Axiom (0.087), Poseidon Group (0.077), pwdump (0.053), Credentials In Files (0.051), Windows Credential Editor (0.051)
[RETRIEVE] Graph expansion: 4 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Credential Access (67 neighbors, 67 edges)
           → IceApple (19 neighbors, 19 edges)
           → Security Account Manager (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 3/5: แก้ไขไฟล์ทางลัดบนเดสก์ท็อปให้ชี้ไปยังโปรแกรมที่ผู้โจมตีวางไว้เพื่อให้ถูกเรียกทำง...
[RETRIEVE] Query: แก้ไขไฟล์ทางลัดบนเดสก์ท็อปให้ชี้ไปยังโปรแกรมที่ผู้โจมตีวางไว้เพื่อให้ถูกเรียกทำง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Re-opened Applications (0.059), IMAPLoader (0.013), KernelCallbackTable (0.009), Cardinal RAT (0.009), Change Default File Association (0.007), Visual Basic (0.001), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Re-opened Applications (7 neighbors, 7 edges)
           → IMAPLoader (10 neighbors, 10 edges)
           → Create or Modify System Process (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 4/5: รันสคริปต์เพื่อขโมยสิทธิ์ประจำตัวจากกระบวนการของผู้ใช้รายอื่นที่เปิดค้างอยู่...
[RETRIEVE] Query: รันสคริปต์เพื่อขโมยสิทธิ์ประจำตัวจากกระบวนการของผู้ใช้รายอื่นที่เปิดค้างอยู่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.455), Create Process with Token (0.085), Access Token Manipulation (0.081), Token Impersonation/Theft (0.056), ZxShell (0.038), RDFSNIFFER (0.003), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Create Process with Token (19 neighbors, 19 edges)
           → Access Token Manipulation (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 5/5: สวมสิทธิ์สิทธิ์ประจำตัวของผู้ใช้รายอื่นเพื่อสั่งงานในนามของผู้ใช้ดังกล่าว...
[RETRIEVE] Query: สวมสิทธิ์สิทธิ์ประจำตัวของผู้ใช้รายอื่นเพื่อสั่งงานในนามของผู้ใช้ดังกล่าว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Token Impersonation/Theft (0.502), Okrum (0.159), Make and Impersonate Token (0.086), GUI Input Capture (0.014), APT28 (0.009), CrossRAT (0.000), Visual Basic (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Token Impersonation/Theft (26 neighbors, 26 edges)
           → Okrum (35 neighbors, 35 edges)
           → Make and Impersonate Token (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] 13 vectors (quota 3/query), 8 subgraphs from 5 queries
  [8/100] retrieved=147 relevant=3 latency=23870ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 11 เมษายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความว่ามีการเข้าถึงเครื่องแ...
[RETRIEVE] Query: เมื่อวันที่ 11 เมษายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความว่ามีการเข้าถึงเครื่องแ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Credential Editor (0.258), Axiom (0.249), Suckfly (0.139), OS Credential Dumping (0.138), Ember Bear (0.116), Mimikatz (0.028), Credential Access Protection (0.027), Credential Access (0.024), Credentials In Files (0.003), Credential Stuffing (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 2/8: อัปโหลดสคริปต์เพื่อข้ามการขออนุญาตยกระดับสิทธิ์ไปยังเครื่องที่ยึดครองได้...
[RETRIEVE] Query: อัปโหลดสคริปต์เพื่อข้ามการขออนุญาตยกระดับสิทธิ์ไปยังเครื่องที่ยึดครองได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: UPPERCUT (0.043), AppCert DLLs (0.013), Exploitation for Privilege Escalation (0.010), BackConfig (0.007), Elevated Execution with Prompt (0.007), Bypass User Account Control (0.005), OSX/Shlayer (0.002), Privilege Escalation (0.002), AppleSeed (0.001), Temporary Elevated Cloud Access (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → UPPERCUT (18 neighbors, 18 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → AppCert DLLs (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 3/8: สั่งให้สคริปต์ข้ามการขออนุญาตยกระดับสิทธิ์ทำงานบนเครื่องที่ยึดครองได้...
[RETRIEVE] Query: สั่งให้สคริปต์ข้ามการขออนุญาตยกระดับสิทธิ์ทำงานบนเครื่องที่ยึดครองได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LockBit 3.0 (0.575), RCSession (0.041), Bypass User Account Control (0.037), Elevated Execution with Prompt (0.025), Downdelph (0.022), Exploitation for Privilege Escalation (0.016), Setuid and Setgid (0.009), AppCert DLLs (0.004), PsExec (0.002), Ptrace System Calls (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → LockBit 3.0 (34 neighbors, 34 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
           → RCSession (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 4/8: อัปโหลดเครื่องมือ Credential Dumping ที่ถูกดัดแปลงไปยังเครื่องที่ยึดครองได้...
[RETRIEVE] Query: อัปโหลดเครื่องมือ Credential Dumping ที่ถูกดัดแปลงไปยังเครื่องที่ยึดครองได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OS Credential Dumping (0.043), MimiPenguin (0.041), Suckfly (0.025), MgBot (0.025), Windows Credential Editor (0.017), pwdump (0.013), Credentials In Files (0.011), Axiom (0.009), Credential Access Protection (0.004), Credential Stuffing (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → MimiPenguin (2 neighbors, 2 edges)
           → Suckfly (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 5/8: สั่งเครื่องมือ Credential Dumping ที่ถูกดัดแปลงให้ทำงานเพื่อดึงรหัสผ่านผู้ดูแลระ...
[RETRIEVE] Query: สั่งเครื่องมือ Credential Dumping ที่ถูกดัดแปลงให้ทำงานเพื่อดึงรหัสผ่านผู้ดูแลระ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: menuPass (0.252), Windows Credential Editor (0.159), OS Credential Dumping (0.140), Suckfly (0.139), pwdump (0.077), Poseidon Group (0.066), Credential Access (0.063), Axiom (0.044), Credentials In Files (0.041), Credential Access Protection (0.019)
[RETRIEVE] Graph expansion: 3 subgraphs
           → menuPass (71 neighbors, 71 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 6/8: นำไฟล์เครื่องมือชุดใหม่จากเครื่องภายนอกเข้ามาเก็บในโฟลเดอร์ที่เตรียมไว้บนเครื่อง...
[RETRIEVE] Query: นำไฟล์เครื่องมือชุดใหม่จากเครื่องภายนอกเข้ามาเก็บในโฟลเดอร์ที่เตรียมไว้บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ingress Tool Transfer (0.032), cmd (0.010), Lateral Tool Transfer (0.007), APT3 (0.006), RogueRobin (0.004), File Deletion (0.001), Local Data Staging (0.001), Credentials In Files (0.000), Archive via Utility (0.000), Automated Collection (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → cmd (13 neighbors, 13 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 7/8: คัดลอกเครื่องมือจากเครื่องที่ยึดครองได้ไปยังเครื่องแม่ข่ายเก็บเอกสารอีกเครื่องภา...
[RETRIEVE] Query: คัดลอกเครื่องมือจากเครื่องที่ยึดครองได้ไปยังเครื่องแม่ข่ายเก็บเอกสารอีกเครื่องภา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ingress Tool Transfer (0.266), Lateral Tool Transfer (0.145), Havoc (0.069), APT3 (0.055), Communication Through Removable Media (0.003), Cobian RAT (0.001), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Havoc (30 neighbors, 30 edges)
[RETRIEVE-QUOTA] Query 8/8: เชื่อมต่อผ่าน SSH เข้าเครื่องแม่ข่ายเก็บเอกสารโดยใช้รหัสผ่านผู้ดูแลระบบที่ได้มา...
[RETRIEVE] Query: เชื่อมต่อผ่าน SSH เข้าเครื่องแม่ข่ายเก็บเอกสารโดยใช้รหัสผ่านผู้ดูแลระบบที่ได้มา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH Hijacking (0.046), SSH (0.013), SSH Authorized Keys (0.012), Skidmap (0.010), Kobalos (0.007), Password Managers (0.001), Ebury (0.001), Cobalt Strike (0.001), Leviathan (0.001), Kessel (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SSH Hijacking (8 neighbors, 8 edges)
           → SSH (33 neighbors, 33 edges)
           → SSH Authorized Keys (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [9/100] retrieved=625 relevant=4 latency=37191ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 20 ตุลาคม 2563 หน่วยงานปกครองส่วนท้องถิ่นหลายแห่งแจ้งความว่าระบบสารส...
[RETRIEVE] Query: เมื่อวันที่ 20 ตุลาคม 2563 หน่วยงานปกครองส่วนท้องถิ่นหลายแห่งแจ้งความว่าระบบสารส...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.220), FIN13 (0.203), UNC3886 (0.090), SoreFang (0.051), External Remote Services (0.048), SharePoint ToolShell Exploitation (0.004), Brute Force (0.002), Valid Accounts (0.002), Web Portal Capture (0.001), Internal Spearphishing (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → FIN13 (57 neighbors, 57 edges)
           → External Remote Services (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] Query 2/7: โจมตีช่องโหว่ของ Public-Facing Application บนเว็บเซิร์ฟเวอร์ที่เปิดให้เข้าถึงจาก...
[RETRIEVE] Query: โจมตีช่องโหว่ของ Public-Facing Application บนเว็บเซิร์ฟเวอร์ที่เปิดให้เข้าถึงจาก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.886), FrostyGoop Incident (0.577), SharePoint ToolShell Exploitation (0.512), Network Segmentation (0.343), Havij (0.304), P.A.S. Webshell (0.009), Exploitation for Client Execution (0.001), Query Public AI Services (0.001), MirrorFace (0.001), Multi-factor Authentication (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → FrostyGoop Incident (5 neighbors, 5 edges)
           → SharePoint ToolShell Exploitation (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 3/7: ติดตั้งโปรแกรมลงเครื่องผู้ใช้ทันทีเมื่อเปิดหน้าเว็บที่ถูกดัดแปลงโดยไม่ต้องดาวน์โ...
[RETRIEVE] Query: ติดตั้งโปรแกรมลงเครื่องผู้ใช้ทันทีเมื่อเปิดหน้าเว็บที่ถูกดัดแปลงโดยไม่ต้องดาวน์โ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Drive-by Compromise (0.169), Drive-by Target (0.066), CURIUM (0.049), KARAE (0.036), Elderwood (0.034), Windigo (0.034), ClickOnce (0.013), Browser Extensions (0.002), Server (0.002), Supply Chain Compromise (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Drive-by Compromise (51 neighbors, 51 edges)
           → Drive-by Target (12 neighbors, 12 edges)
           → CURIUM (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 4/7: ใช้ Brute Force เดารหัสผ่านซ้ำ ๆ ของบัญชีผู้ใช้...
[RETRIEVE] Query: ใช้ Brute Force เดารหัสผ่านซ้ำ ๆ ของบัญชีผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Brute Force (0.934), APT28 (0.438), APT38 (0.362), User Account Management (0.171), Password Guessing (0.142), CrackMapExec (0.079), Password Policy Discovery (0.016), Forced Authentication (0.010), Wordlist Scanning (0.004), Brute Ratel C4 (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Brute Force (34 neighbors, 34 edges)
           → APT28 (124 neighbors, 124 edges)
           → Password Guessing (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 5/7: ส่งคำสั่งฐานข้อมูลแทรกผ่านหน้าเว็บของหน่วยงาน (SQL Injection)...
[RETRIEVE] Query: ส่งคำสั่งฐานข้อมูลแทรกผ่านหน้าเว็บของหน่วยงาน (SQL Injection)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Havij (0.025), Content Injection (0.006), Template Injection (0.005), Thread Local Storage (0.003), Carbon (0.003), SQLRat (0.002), Cardinal RAT (0.001), Dynamic-link Library Injection (0.001), Process Injection (0.001), HTRAN (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Havij (2 neighbors, 2 edges)
           → Content Injection (8 neighbors, 8 edges)
           → Template Injection (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 6/7: เข้าถึงเครือข่ายภายในจากระยะไกลผ่าน External Remote Services ประเภท SSL VPN...
[RETRIEVE] Query: เข้าถึงเครือข่ายภายในจากระยะไกลผ่าน External Remote Services ประเภท SSL VPN...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Remote Services (0.930), Limit Access to Resource Over Network (0.635), Operation Wocao (0.343), C0032 (0.326), Web Portal Capture (0.247), Volt Typhoon (0.177), Remote Services (0.028), Limit Access to Resource Over Network (0.003), SSH (0.003), Terminal Services DLL (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → External Remote Services (52 neighbors, 52 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Operation Wocao (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] Query 7/7: ใช้ Valid Accounts ยืนยันตัวตนเข้าสู่เครื่องแม่ข่ายควบคุมบัญชีผู้ใช้และระบบจดหมา...
[RETRIEVE] Query: ใช้ Valid Accounts ยืนยันตัวตนเข้าสู่เครื่องแม่ข่ายควบคุมบัญชีผู้ใช้และระบบจดหมา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cloud Accounts (0.302), VOID MANTICORE (0.242), Account Discovery (0.036), 2015 Ukraine Electric Power Attack (0.036), Valid Accounts (0.030), Application Developer Guidance (0.026), User Account Management (0.021), Modify Authentication Process (0.003), User Account Modification (0.000), Establish Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Cloud Accounts (33 neighbors, 33 edges)
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [10/100] retrieved=223 relevant=5 latency=30910ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 5 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งในจังหวัดชลบุรีแจ้งความว่าข้อ...
[RETRIEVE] Query: เมื่อวันที่ 5 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งในจังหวัดชลบุรีแจ้งความว่าข้อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.026), SDBbot (0.021), PUNCHTRACK (0.009), ShimRat (0.008), FrameworkPOS (0.004), Pillowmint (0.002), Pillowmint (0.001), Pillowmint (0.000), RawPOS (0.000), Application Shimming (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → SDBbot (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 2/8: รันคำสั่งบรรทัดเดียวผ่านหน้าต่างคำสั่งของระบบโดยเข้ารหัสและย่อคำสั่งเพื่อหลบเลี่...
[RETRIEVE] Query: รันคำสั่งบรรทัดเดียวผ่านหน้าต่างคำสั่งของระบบโดยเข้ารหัสและย่อคำสั่งเพื่อหลบเลี่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Command Obfuscation (0.199), Process Injection (0.025), Execution Prevention (0.016), Ptrace System Calls (0.004), Execution Prevention (0.004), Execution Prevention (0.002), Visual Basic (0.001), Cardinal RAT (0.001), CrossRAT (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Command Obfuscation (74 neighbors, 74 edges)
           → Process Injection (104 neighbors, 104 edges)
           → Execution Prevention (79 neighbors, 79 edges)
           → Escape to Host (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/8: ติดตั้งกลไก Application Shimming เพื่อให้โปรแกรมของคนร้ายทำงานอีกครั้งหลังเครื่อ...
[RETRIEVE] Query: ติดตั้งกลไก Application Shimming เพื่อให้โปรแกรมของคนร้ายทำงานอีกครั้งหลังเครื่อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SDBbot (0.221), Application Shimming (0.161), ShimRat (0.142), Pillowmint (0.112), FIN7 (0.052), Create or Modify System Process (0.005), Re-opened Applications (0.003), Launch Agent (0.002), Apostle (0.001), Input Injection (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SDBbot (25 neighbors, 25 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → ShimRat (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 4/8: อัปโหลดโปรแกรมที่ตั้งชื่อเลียนแบบเครื่องมือตรวจสอบข้อผิดพลาดของระบบขึ้นบนเครื่อง...
[RETRIEVE] Query: อัปโหลดโปรแกรมที่ตั้งชื่อเลียนแบบเครื่องมือตรวจสอบข้อผิดพลาดของระบบขึ้นบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: XCSSET (0.293), Masquerading (0.142), Sandworm Team (0.084), UPSTYLE (0.080), Execution Prevention (0.032), FakeM (0.006), GUI Input Capture (0.004), xCmd (0.004), Malicious File (0.000), Runtime Data Manipulation (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → XCSSET (33 neighbors, 33 edges)
           → Masquerading (81 neighbors, 81 edges)
           → Sandworm Team (113 neighbors, 113 edges)
[RETRIEVE-QUOTA] Query 5/8: ตรวจสอบรายการโปรแกรมและกระบวนการที่กำลังทำงานอยู่เพื่อค้นหากระบวนการของซอฟต์แวร์...
[RETRIEVE] Query: ตรวจสอบรายการโปรแกรมและกระบวนการที่กำลังทำงานอยู่เพื่อค้นหากระบวนการของซอฟต์แวร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Meteor (0.047), Tasklist (0.014), Process Discovery (0.012), VERMIN (0.009), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), 4H RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Meteor (20 neighbors, 20 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Tasklist (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 6/8: ดึงข้อมูลบัตรเครดิตออกจากหน่วยความจำของซอฟต์แวร์รับชำระเงิน (Memory Scraping)...
[RETRIEVE] Query: ดึงข้อมูลบัตรเครดิตออกจากหน่วยความจำของซอฟต์แวร์รับชำระเงิน (Memory Scraping)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PUNCHTRACK (0.574), PUNCHTRACK (0.333), RawPOS (0.182), Cherry Picker (0.010), Privileged Account Management (0.001), Social Media (0.000), Woody RAT (0.000), Disable or Remove Feature or Program (0.000), UACMe (0.000), Ping (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PUNCHTRACK (4 neighbors, 4 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → RawPOS (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 7/8: บีบอัดข้อมูลบัตรเครดิตที่รวบรวมได้รวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดไฟล์ทั่วไป...
[RETRIEVE] Query: บีบอัดข้อมูลบัตรเครดิตที่รวบรวมได้รวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดไฟล์ทั่วไป...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PoshC2 (0.008), FoggyWeb (0.006), Compression (0.003), FrameworkPOS (0.002), BADFLICK (0.001), Expand (0.001), Archive via Library (0.000), Encrypted/Encoded File (0.000), Standard Encoding (0.000), Masquerade File Type (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → PoshC2 (35 neighbors, 35 edges)
           → Automated Collection (77 neighbors, 77 edges)
           → FoggyWeb (22 neighbors, 22 edges)
           → Archive via Library (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 8/8: นำไฟล์ข้อมูลบัตรเครดิตที่บีบอัดออกจากเครื่อง (Exfiltration)...
[RETRIEVE] Query: นำไฟล์ข้อมูลบัตรเครดิตที่บีบอัดออกจากเครื่อง (Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FrameworkPOS (0.047), Exfiltration (0.044), Exfiltration Over Physical Medium (0.030), Sliver (0.011), Exbyte (0.010), Automated Exfiltration (0.010), Exfiltration Over Alternative Protocol (0.006), Exbyte (0.004), Archive Collected Data (0.004), Empire (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration (19 neighbors, 19 edges)
           → FrameworkPOS (6 neighbors, 6 edges)
           → Archive via Custom Method (42 neighbors, 42 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [11/100] retrieved=261 relevant=4 latency=35455ms
[RETRIEVE-QUOTA] Query 1/4: เมื่อวันที่ 28 สิงหาคม 2566 บริษัทที่ปรึกษาด้านวิศวกรรมแห่งหนึ่งแจ้งความว่าเอกสา...
[RETRIEVE] Query: เมื่อวันที่ 28 สิงหาคม 2566 บริษัทที่ปรึกษาด้านวิศวกรรมแห่งหนึ่งแจ้งความว่าเอกสา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: schtasks (0.005), Ursnif (0.002), APT-C-36 (0.001), Operation Honeybee (0.001), Koadic (0.001), Scheduled Task/Job (0.001), System Script Proxy Execution (0.000), APT-C-36 (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → schtasks (4 neighbors, 4 edges)
           → Ursnif (36 neighbors, 36 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/4: อัปโหลดไฟล์เอกสารโครงการของลูกค้าจำนวนมากไปยังบัญชีบริการรับฝากข้อมูลออนไลน์ที่ไ...
[RETRIEVE] Query: อัปโหลดไฟล์เอกสารโครงการของลูกค้าจำนวนมากไปยังบัญชีบริการรับฝากข้อมูลออนไลน์ที่ไ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OilCheck (0.204), SampleCheck5000 (0.030), Exfiltration to Cloud Storage (0.013), Salesforce Data Exfiltration (0.010), Exfiltration Over Alternative Protocol (0.009), Exfiltration Over Other Network Medium (0.007), Exfiltration to Code Repository (0.005), APT28 Nearest Neighbor Campaign (0.005), Exfiltration (0.003), Empire (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OilCheck (4 neighbors, 4 edges)
           → Exfiltration Over Web Service (23 neighbors, 23 edges)
           → SampleCheck5000 (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/4: ใช้กลไกบริหารจัดการเครื่องระยะไกลของ Windows สั่งให้สคริปต์ทำงานบนเครื่องปลายทาง...
[RETRIEVE] Query: ใช้กลไกบริหารจัดการเครื่องระยะไกลของ Windows สั่งให้สคริปต์ทำงานบนเครื่องปลายทาง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HermeticWizard (0.086), PsExec (0.062), Windows Remote Management (0.047), RemoteCMD (0.021), Windows Command Shell (0.009), WindTail (0.003), Scheduled Task (0.001), cmd (0.001), Cobalt Group (0.000), Samurai (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → HermeticWizard (16 neighbors, 16 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Windows Remote Management (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/4: ตั้งงานที่กำหนดเวลาไว้ให้เรียกโปรแกรมของคนร้ายทำงานซ้ำตามช่วงเวลาที่กำหนดเพื่อคง...
[RETRIEVE] Query: ตั้งงานที่กำหนดเวลาไว้ให้เรียกโปรแกรมของคนร้ายทำงานซ้ำตามช่วงเวลาที่กำหนดเพื่อคง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Scheduled Task/Job (0.493), Goopy (0.459), schtasks (0.133), yty (0.128), at (0.114), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Scheduled Task/Job (18 neighbors, 18 edges)
           → Goopy (19 neighbors, 19 edges)
           → Scheduled Task (201 neighbors, 201 edges)
[RETRIEVE-QUOTA] 12 vectors (quota 3/query), 8 subgraphs from 4 queries
  [12/100] retrieved=116 relevant=3 latency=18700ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 14 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Query: เมื่อวันที่ 14 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ursnif (0.035), LockBit 2.0 (0.016), APT29 (0.010), PsExec (0.006), REvil (0.001), Reg (0.000), Registry Run Keys / Startup Folder (0.000), Active Setup (0.000), Windows Registry Key Modification (0.000), Windows Registry Key Access (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ursnif (36 neighbors, 36 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 2/7: ใช้บัญชีผู้ใช้ที่ได้มาก่อนหน้าเพื่อเข้าถึงเครื่องปลายทาง (Valid Accounts)...
[RETRIEVE] Query: ใช้บัญชีผู้ใช้ที่ได้มาก่อนหน้าเพื่อเข้าถึงเครื่องปลายทาง (Valid Accounts)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT33 (0.381), Valid Accounts (0.218), Windows Remote Management (0.098), Remote Services (0.039), Account Discovery (0.028), Cloud Accounts (0.028), Modify Authentication Process (0.001), Account Manipulation (0.001), VajraSpy (0.001), Valak (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT33 (47 neighbors, 47 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Windows Remote Management (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 3/7: ผลักไฟล์โปรแกรมของผู้โจมตีไปยังเครื่องปลายทางผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบ...
[RETRIEVE] Query: ผลักไฟล์โปรแกรมของผู้โจมตีไปยังเครื่องปลายทางผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT3 (0.488), SMB/Windows Admin Shares (0.227), APT32 (0.170), PsExec (0.136), 2016 Ukraine Electric Power Attack (0.067), Taint Shared Content (0.040), Lateral Tool Transfer (0.026), Network Share Connection Removal (0.010), Net (0.009), Shared Modules (0.008)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT3 (50 neighbors, 50 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → APT32 (93 neighbors, 93 edges)
[RETRIEVE-QUOTA] Query 4/7: สร้างบริการของระบบใหม่บนเครื่องปลายทาง...
[RETRIEVE] Query: สร้างบริการของระบบใหม่บนเครื่องปลายทาง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Service Creation (0.053), ZxShell (0.035), ZxShell (0.014), Terminal Services DLL (0.012), Okrum (0.011), Create or Modify System Process (0.011), Anchor (0.008), Systemd Service (0.006), Container Service (0.003), User Account Creation (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Service Creation (0 neighbors, 0 edges)
           → ZxShell (37 neighbors, 37 edges)
           → Windows Service (150 neighbors, 150 edges)
[RETRIEVE-QUOTA] Query 5/7: สั่งให้บริการของระบบเริ่มทำงานเพื่อเรียกใช้ไฟล์โปรแกรมของผู้โจมตีด้วยสิทธิ์ระดับ...
[RETRIEVE] Query: สั่งให้บริการของระบบเริ่มทำงานเพื่อเรียกใช้ไฟล์โปรแกรมของผู้โจมตีด้วยสิทธิ์ระดับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Create or Modify System Process (0.062), System Services (0.048), Services File Permissions Weakness (0.028), APT3 (0.020), Systemd Service (0.005), Emissary (0.003), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → System Services (9 neighbors, 9 edges)
           → Services File Permissions Weakness (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 6/7: เพิ่มรายการเรียกใช้โปรแกรมของผู้โจมตีใน Registry Run Key ของบัญชีผู้ใช้เป้าหมาย...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้โปรแกรมของผู้โจมตีใน Registry Run Key ของบัญชีผู้ใช้เป้าหมาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.580), APT37 (0.175), Storm-1811 (0.131), LockBit 2.0 (0.066), Active Setup (0.060), Ursnif (0.058), Modify Registry (0.019), Query Registry (0.005), Windows Registry Key Access (0.001), Windows Registry Key Modification (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → APT37 (42 neighbors, 42 edges)
           → Storm-1811 (38 neighbors, 38 edges)
[RETRIEVE-QUOTA] Query 7/7: เข้าใช้งานเครื่องผ่านเดสก์ท็อประยะไกล (RDP) เพื่อกระตุ้น Registry Run Keyให้ทำงา...
[RETRIEVE] Query: เข้าใช้งานเครื่องผ่านเดสก์ท็อประยะไกล (RDP) เพื่อกระตุ้น Registry Run Keyให้ทำงา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SILENTTRINITY (0.295), RDP Hijacking (0.188), Remote Desktop Protocol (0.098), Registry Run Keys / Startup Folder (0.063), RCSession (0.032), StrongPity (0.016), CORESHELL (0.012), Modify Registry (0.010), Windows Registry Key Access (0.003), Windows Registry Key Modification (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [13/100] retrieved=448 relevant=3 latency=31820ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 8 กันยายน 2565 โรงเรียนมัธยมแห่งหนึ่งในจังหวัดสงขลาแจ้งความว่าระบบทะ...
[RETRIEVE] Query: เมื่อวันที่ 8 กันยายน 2565 โรงเรียนมัธยมแห่งหนึ่งในจังหวัดสงขลาแจ้งความว่าระบบทะ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Medusa Group (0.157), APT29 (0.142), Koadic (0.013), Windows Management Instrumentation (0.007), Windows Management Instrumentation Event Subscription (0.000), Unsecured Credentials (0.000), Query Registry (0.000), Windows Remote Management (0.000), Security Account Manager (0.000), Password Managers (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Medusa Group (62 neighbors, 62 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → APT29 (117 neighbors, 117 edges)
[RETRIEVE-QUOTA] Query 2/6: เข้าสู่แอปพลิเคชันของโรงเรียนที่เปิดให้เข้าถึงจากอินเทอร์เน็ตด้วยชื่อผู้ใช้และรห...
[RETRIEVE] Query: เข้าสู่แอปพลิเคชันของโรงเรียนที่เปิดให้เข้าถึงจากอินเทอร์เน็ตด้วยชื่อผู้ใช้และรห...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AADInternals (0.002), DRYHOOK (0.002), LAPSUS$ (0.001), Valid Accounts (0.001), Web Credential Usage (0.000), Cobian RAT (0.000), The White Company (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → AADInternals (26 neighbors, 26 edges)
           → Steal Application Access Token (13 neighbors, 13 edges)
           → DRYHOOK (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 3/6: เรียกใช้ Windows Management Instrumentation (WMI) ซึ่งเป็นเครื่องมือที่มีอยู่ในร...
[RETRIEVE] Query: เรียกใช้ Windows Management Instrumentation (WMI) ซึ่งเป็นเครื่องมือที่มีอยู่ในร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: EKANS (0.833), Windows Management Instrumentation (0.767), Windows Management Instrumentation Event Subscription (0.584), Koadic (0.497), POWRUNER (0.493), PoshC2 (0.452), cmd (0.008), Wevtutil (0.001), Windows Remote Management (0.001), Scheduled Task (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → EKANS (9 neighbors, 9 edges)
           → Windows Management Instrumentation Event Subscription (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 4/6: แทรกไฟล์อันตรายลงในโฟลเดอร์ที่ใช้แบ่งปันร่วมกันภายในองค์กร...
[RETRIEVE] Query: แทรกไฟล์อันตรายลงในโฟลเดอร์ที่ใช้แบ่งปันร่วมกันภายในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Taint Shared Content (0.365), Gamaredon Group (0.056), Gamaredon Group (0.047), Restrict File and Directory Permissions (0.004), Lateral Tool Transfer (0.004), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Taint Shared Content (18 neighbors, 18 edges)
           → Gamaredon Group (76 neighbors, 76 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] Query 5/6: โจมตีช่องโหว่ของบริการจัดการเครื่องพิมพ์บนเครื่องแม่ข่ายเพื่อยกระดับสิทธิ์จากผู้...
[RETRIEVE] Query: โจมตีช่องโหว่ของบริการจัดการเครื่องพิมพ์บนเครื่องแม่ข่ายเพื่อยกระดับสิทธิ์จากผู้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploitation for Privilege Escalation (0.091), APT1 (0.060), Gelsemium (0.035), Privilege Escalation (0.031), Exploitation for Credential Access (0.006), Cobian RAT (0.001), CrossRAT (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → APT1 (40 neighbors, 40 edges)
           → Malware (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 6/6: เข้ารหัสระบบทะเบียนนักเรียนและแสดงข้อความเรียกค่าไถ่บนหน้าจอ...
[RETRIEVE] Query: เข้ารหัสระบบทะเบียนนักเรียนและแสดงข้อความเรียกค่าไถ่บนหน้าจอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Charger (0.008), Black Basta (0.005), KernelCallbackTable (0.000), Pay2Key (0.000), Black Basta (0.000), MegaCortex (0.000), Ferocious (0.000), Moneybird (0.000), Avaddon (0.000), Network Provider DLL (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Charger (4 neighbors, 4 edges)
           → Endpoint Denial of Service (8 neighbors, 8 edges)
           → Black Basta (27 neighbors, 27 edges)
           → Internal Defacement (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [14/100] retrieved=322 relevant=4 latency=29763ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 3 ธันวาคม 2566 สำนักงานกฎหมายแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่ามีผู...
[RETRIEVE] Query: เมื่อวันที่ 3 ธันวาคม 2566 สำนักงานกฎหมายแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่ามีผู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.114), SSH Hijacking (0.015), Cobalt Strike (0.015), LP-Notes (0.008), Kessel (0.004), Ramsay (0.004), File Deletion (0.002), DarkWatchman (0.002), SSH (0.001), GlassWorm (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → SSH (33 neighbors, 33 edges)
           → SSH Hijacking (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 2/6: โปรแกรมฝังตัวลบไฟล์โปรแกรมดักบันทึกแป้นพิมพ์และไฟล์บันทึกผลออกจากเครื่องเพื่อทำล...
[RETRIEVE] Query: โปรแกรมฝังตัวลบไฟล์โปรแกรมดักบันทึกแป้นพิมพ์และไฟล์บันทึกผลออกจากเครื่องเพื่อทำล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SDelete (0.026), File Deletion (0.010), MacMa (0.007), MegaCortex (0.005), FunnyDream (0.004), Lslsass (0.002), Cachedump (0.002), Inhibit System Recovery (0.001), DarkWatchman (0.001), Windows Registry Key Deletion (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → SDelete (7 neighbors, 7 edges)
           → File Deletion (310 neighbors, 310 edges)
           → MacMa (28 neighbors, 28 edges)
           → Clear Linux or Mac System Logs (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 3/6: โปรแกรมฝังตัวดาวน์โหลดไฟล์โปรแกรมชุดใหม่จากเครื่องสั่งการภายนอกมาเก็บไว้บนเครื่อ...
[RETRIEVE] Query: โปรแกรมฝังตัวดาวน์โหลดไฟล์โปรแกรมชุดใหม่จากเครื่องสั่งการภายนอกมาเก็บไว้บนเครื่อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Volgmer (0.022), TrickBot (0.021), Embedded Payloads (0.004), Havoc (0.002), Impacket (0.002), PsExec (0.001), Portable Executable Injection (0.000), Reflective Code Loading (0.000), Cachedump (0.000), Extra Window Memory Injection (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Volgmer (20 neighbors, 20 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → TrickBot (57 neighbors, 57 edges)
[RETRIEVE-QUOTA] Query 4/6: ตั้งชื่อไฟล์โปรแกรมที่ดาวน์โหลดให้ดูเหมือนไฟล์ชั่วคราวของระบบ (Masquerading)...
[RETRIEVE] Query: ตั้งชื่อไฟล์โปรแกรมที่ดาวน์โหลดให้ดูเหมือนไฟล์ชั่วคราวของระบบ (Masquerading)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: UPSTYLE (0.569), Masquerading (0.462), Execution Prevention (0.350), Ramsay (0.288), Masquerade File Type (0.101), Sandworm Team (0.089), Software Packing (0.004), Malicious File (0.003), Match Legitimate Resource Name or Location (0.002), Runtime Data Manipulation (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → UPSTYLE (13 neighbors, 13 edges)
           → Masquerading (81 neighbors, 81 edges)
           → Execution Prevention (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] Query 5/6: คัดลอกไฟล์โปรแกรมไปยังเครื่องแม่ข่ายเว็บของสำนักงานผ่าน SSH...
[RETRIEVE] Query: คัดลอกไฟล์โปรแกรมไปยังเครื่องแม่ข่ายเว็บของสำนักงานผ่าน SSH...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH Hijacking (0.018), cmd (0.015), SSH (0.012), SSH Authorized Keys (0.007), Kobalos (0.006), Cobalt Strike (0.004), Leviathan (0.002), Kessel (0.001), SMB/Windows Admin Shares (0.001), netsh (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SSH Hijacking (8 neighbors, 8 edges)
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 6/6: เชื่อมต่อเครื่องแม่ข่ายเว็บผ่าน SSH โดยใช้รหัสผ่านของผู้ใช้รายที่สาม (Valid Acco...
[RETRIEVE] Query: เชื่อมต่อเครื่องแม่ข่ายเว็บผ่าน SSH โดยใช้รหัสผ่านของผู้ใช้รายที่สาม (Valid Acco...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH (0.212), Kinsing (0.159), UNC3886 (0.123), Remote Services (0.083), SSH Hijacking (0.078), Linux Rabbit (0.049), Remote Service Session Hijacking (0.031), SSH Authorized Keys (0.024), Direct Cloud VM Connections (0.002), Modify Authentication Process (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SSH (33 neighbors, 33 edges)
           → Kinsing (17 neighbors, 17 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [15/100] retrieved=411 relevant=3 latency=24854ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 19 พฤษภาคม 2567 บริษัทหลักทรัพย์แห่งหนึ่งแจ้งความว่าหน้าจอการทำงานขอ...
[RETRIEVE] Query: เมื่อวันที่ 19 พฤษภาคม 2567 บริษัทหลักทรัพย์แห่งหนึ่งแจ้งความว่าหน้าจอการทำงานขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VERMIN (0.018), RogueRobin (0.003), Screen Capture (0.000), Exfiltration Over C2 Channel (0.000), FIN8 (0.000), Video Capture (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), CrossRAT (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → VERMIN (17 neighbors, 17 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → RogueRobin (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 2/9: ดาวน์โหลดสคริปต์มายังเครื่องเป้าหมาย...
[RETRIEVE] Query: ดาวน์โหลดสคริปต์มายังเครื่องเป้าหมาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: reGeorg (0.278), Cyclops Blink (0.230), PsExec (0.037), OilBooster (0.025), Ingress Tool Transfer (0.005), Revenge RAT (0.003), Visual Basic (0.002), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → reGeorg (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Cyclops Blink (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 3/9: สั่งให้สคริปต์ที่ดาวน์โหลดมาทำงาน...
[RETRIEVE] Query: สั่งให้สคริปต์ที่ดาวน์โหลดมาทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: schtasks (0.033), BackConfig (0.015), CSPY Downloader (0.009), Get2 (0.005), PsExec (0.004), KernelCallbackTable (0.003), Visual Basic (0.001), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → schtasks (4 neighbors, 4 edges)
           → BackConfig (17 neighbors, 17 edges)
           → Native API (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 4/9: ถ่ายภาพหน้าจอผู้ใช้เป็นระยะ (Screen Capture)...
[RETRIEVE] Query: ถ่ายภาพหน้าจอผู้ใช้เป็นระยะ (Screen Capture)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerSploit (0.427), Screen Capture (0.325), TangleBot (0.160), AsyncRAT (0.154), Video Capture (0.122), Input Capture (0.042), GUI Input Capture (0.018), Web Portal Capture (0.014), HenBox (0.006), Audio Capture (0.004)
[RETRIEVE] Graph expansion: 4 subgraphs
           → PowerSploit (39 neighbors, 39 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → TangleBot (12 neighbors, 12 edges)
           → Screen Capture (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 5/9: ส่งภาพหน้าจอออกไปภายนอก (Exfiltration)...
[RETRIEVE] Query: ส่งภาพหน้าจอออกไปภายนอก (Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Physical Medium (0.154), Exfiltration over USB (0.070), eSurv (0.062), Exfiltration Over Other Network Medium (0.054), Automated Exfiltration (0.037), Exfiltration (0.031), Exfiltration Over Alternative Protocol (0.024), Exbyte (0.008), Exbyte (0.008), Empire (0.004)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over Physical Medium (6 neighbors, 6 edges)
           → Exfiltration over USB (13 neighbors, 13 edges)
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 6/9: เขียนชุดข้อมูลคำสั่งของโปรแกรมควบคุมระยะไกลขั้นที่สองลงในทะเบียนระบบแทนการเก็บเป...
[RETRIEVE] Query: เขียนชุดข้อมูลคำสั่งของโปรแกรมควบคุมระยะไกลขั้นที่สองลงในทะเบียนระบบแทนการเก็บเป...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RCSession (0.057), Modify Registry (0.004), HeartCrypt (0.001), Proc Memory (0.000), Cobian RAT (0.000), Visual Basic (0.000), Ptrace System Calls (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → RCSession (24 neighbors, 24 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → HeartCrypt (12 neighbors, 12 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 7/9: อ่านชุดข้อมูลของโปรแกรมควบคุมระยะไกลขั้นที่สองจากทะเบียนระบบ...
[RETRIEVE] Query: อ่านชุดข้อมูลของโปรแกรมควบคุมระยะไกลขั้นที่สองจากทะเบียนระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mori (0.028), Reg (0.026), njRAT (0.003), Query Registry (0.003), Windows Remote Management (0.002), Modify Registry (0.002), Remote System Discovery (0.001), QakBot (0.001), Security Account Manager (0.000), POWRUNER (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Mori (10 neighbors, 10 edges)
           → Query Registry (121 neighbors, 121 edges)
           → Reg (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 8/9: แปลงชุดข้อมูลที่ซ่อนไว้กลับให้อยู่ในรูปที่ประมวลผลได้ (Deobfuscate/Decode Files ...
[RETRIEVE] Query: แปลงชุดข้อมูลที่ซ่อนไว้กลับให้อยู่ในรูปที่ประมวลผลได้ (Deobfuscate/Decode Files ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FRAMESTING (0.785), Deobfuscate/Decode Files or Information (0.736), WhisperGate (0.679), NOKKI (0.580), MacMa (0.279), Obfuscated Files or Information (0.111), Encrypted/Encoded File (0.034), Dynamic API Resolution (0.007), HTML Smuggling (0.002), Polymorphic Code (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → FRAMESTING (8 neighbors, 8 edges)
           → WhisperGate (29 neighbors, 29 edges)
[RETRIEVE-QUOTA] Query 9/9: สั่งให้โปรแกรมควบคุมระยะไกลขั้นที่สองทำงานในหน่วยความจำ (Reflective Code Loading...
[RETRIEVE] Query: สั่งให้โปรแกรมควบคุมระยะไกลขั้นที่สองทำงานในหน่วยความจำ (Reflective Code Loading...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Uroburos (0.544), Reflective Code Loading (0.354), ThiefQuest (0.136), FIN7 (0.047), SharePoint ToolShell Exploitation (0.019), Proc Memory (0.017), Restrict Library Loading (0.002), KernelCallbackTable (0.001), Dynamic-link Library Injection (0.001), Driver Load (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Uroburos (37 neighbors, 37 edges)
           → Reflective Code Loading (33 neighbors, 33 edges)
           → ThiefQuest (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [16/100] retrieved=625 relevant=3 latency=30740ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 26 ตุลาคม 2565 คลินิกเวชกรรมเครือข่ายแห่งหนึ่งแจ้งความว่าข้อมูลคนไข้...
[RETRIEVE] Query: เมื่อวันที่ 26 ตุลาคม 2565 คลินิกเวชกรรมเครือข่ายแห่งหนึ่งแจ้งความว่าข้อมูลคนไข้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.131), Cobalt Strike (0.006), DCHSpy (0.004), DRYHOOK (0.004), SSH Hijacking (0.000), Remote Service Session Hijacking (0.000), SSH (0.000), Kessel (0.000), Valid Accounts (0.000), POSHSPY (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → SSH (33 neighbors, 33 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] Query 2/6: โจมตีช่องโหว่ที่ยังไม่ได้ติดตั้งชุดแก้ไขบนอุปกรณ์เชื่อมต่อเครือข่ายส่วนตัวเสมือน...
[RETRIEVE] Query: โจมตีช่องโหว่ที่ยังไม่ได้ติดตั้งชุดแก้ไขบนอุปกรณ์เชื่อมต่อเครือข่ายส่วนตัวเสมือน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Network Device Authentication (0.008), DRYHOOK (0.005), Sandworm Team (0.002), Cobian RAT (0.001), SharePoint ToolShell Exploitation (0.001), Threat Group-1314 (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Network Device Authentication (11 neighbors, 11 edges)
           → DRYHOOK (11 neighbors, 11 edges)
           → Sandworm Team (113 neighbors, 113 edges)
           → Supply Chain Compromise (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 3/6: ใช้ชื่อผู้ใช้และรหัสผ่านที่รั่วไหลล็อกอินเข้าอุปกรณ์เชื่อมต่อระยะไกลรุ่นเก่าที่ไ...
[RETRIEVE] Query: ใช้ชื่อผู้ใช้และรหัสผ่านที่รั่วไหลล็อกอินเข้าอุปกรณ์เชื่อมต่อระยะไกลรุ่นเก่าที่ไ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Threat Group-1314 (0.090), Remote Service Session Hijacking (0.033), LAPSUS$ (0.028), DRYHOOK (0.028), DRYHOOK (0.010), Valid Accounts (0.008), DRYHOOK (0.004), Modify Authentication Process (0.002), Pass-The-Hash Toolkit (0.001), Password Guessing (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Threat Group-1314 (6 neighbors, 6 edges)
           → Remote Service Session Hijacking (9 neighbors, 9 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] Query 4/6: เข้าถึงข้อมูลคนไข้ในระบบโดยไม่ได้รับอนุญาต...
[RETRIEVE] Query: เข้าถึงข้อมูลคนไข้ในระบบโดยไม่ได้รับอนุญาต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: H1N1 (0.008), TCC Manipulation (0.005), Valid Accounts (0.002), RCSession (0.002), Threat Group-1314 (0.002), Domain Controller Authentication (0.000), Cardinal RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → H1N1 (13 neighbors, 13 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
           → TCC Manipulation (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/6: เชื่อมต่อผ่าน SSH ไปยังเครื่องอื่นในเครือข่ายภายในเพื่อขยายการเข้าถึง...
[RETRIEVE] Query: เชื่อมต่อผ่าน SSH ไปยังเครื่องอื่นในเครือข่ายภายในเพื่อขยายการเข้าถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH Hijacking (0.438), SSH (0.056), Leviathan (0.018), XCSSET (0.015), Cobalt Strike (0.007), FIN7 (0.004), Internal Spearphishing (0.004), SSH Authorized Keys (0.004), Remote Service Session Hijacking (0.003), SMB/Windows Admin Shares (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SSH Hijacking (8 neighbors, 8 edges)
           → SSH (33 neighbors, 33 edges)
           → Leviathan (68 neighbors, 68 edges)
[RETRIEVE-QUOTA] Query 6/6: เชื่อมต่อผ่านเดสก์ท็อประยะไกลไปยังเครื่องอื่นในเครือข่ายภายในเพื่อขยายการเข้าถึง...
[RETRIEVE] Query: เชื่อมต่อผ่านเดสก์ท็อประยะไกลไปยังเครื่องอื่นในเครือข่ายภายในเพื่อขยายการเข้าถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Network Segmentation (0.019), RDP Hijacking (0.017), Remote Desktop Protocol (0.008), Hardware Additions (0.004), CrossRAT (0.001), cmd (0.001), Network Share Discovery (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → Network Segmentation (37 neighbors, 37 edges)
           → External Remote Services (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [17/100] retrieved=236 relevant=3 latency=24619ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 2 กันยายน 2567 บริษัทประกันภัยแห่งหนึ่งแจ้งความว่าบัญชีผู้ดูแลระบบขอ...
[RETRIEVE] Query: เมื่อวันที่ 2 กันยายน 2567 บริษัทประกันภัยแห่งหนึ่งแจ้งความว่าบัญชีผู้ดูแลระบบขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN6 (0.003), Security Account Manager (0.000), Unsecured Credentials (0.000), Valid Accounts (0.000), FIN8 (0.000), Daggerfly (0.000), Clear Windows Event Logs (0.000), Exploitation for Credential Access (0.000), Clear Linux or Mac System Logs (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → FIN6 (52 neighbors, 52 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Security Account Manager (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/7: ร้องขอตั๋วยืนยันสิทธิ์ของบัญชีบริการจำนวนมากจากระบบยืนยันตัวตนองค์กร (Kerberoast...
[RETRIEVE] Query: ร้องขอตั๋วยืนยันสิทธิ์ของบัญชีบริการจำนวนมากจากระบบยืนยันตัวตนองค์กร (Kerberoast...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Active Directory Credential Request (0.648), Rubeus (0.489), Operation Wocao (0.327), Kerberoasting (0.075), Steal or Forge Kerberos Tickets (0.067), Silver Ticket (0.030), FIN7 (0.017), AS-REP Roasting (0.014), Ccache Files (0.007), Domain Trust Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Active Directory Credential Request (0 neighbors, 0 edges)
           → Rubeus (8 neighbors, 8 edges)
           → Kerberoasting (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 3/7: ถอดรหัสตั๋วยืนยันสิทธิ์แบบออฟไลน์เพื่อค้นหารหัสผ่านบัญชีบริการ...
[RETRIEVE] Query: ถอดรหัสตั๋วยืนยันสิทธิ์แบบออฟไลน์เพื่อค้นหารหัสผ่านบัญชีบริการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerSploit (0.192), Silver Ticket (0.044), Mimikatz (0.009), Steal or Forge Kerberos Tickets (0.002), Active Directory Credential Request (0.001), Cobalt Strike (0.001), Reversible Encryption (0.001), Security Account Manager (0.000), TrickBot (0.000), Credentials from Web Browsers (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PowerSploit (39 neighbors, 39 edges)
           → Kerberoasting (18 neighbors, 18 edges)
           → Silver Ticket (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 4/7: เปิดการเชื่อมต่อหน้าจอระยะไกล RDP ไปยังเครื่องเป้าหมายเครื่องที่สองภายในองค์กร...
[RETRIEVE] Query: เปิดการเชื่อมต่อหน้าจอระยะไกล RDP ไปยังเครื่องเป้าหมายเครื่องที่สองภายในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.026), Limit Access to Resource Over Network (0.014), RDP Hijacking (0.011), Remote Desktop Protocol (0.008), Terminal Services DLL (0.006), Axiom (0.006), Remote Service Session Hijacking (0.002), Remote Access Tools (0.001), Application Layer Protocol (0.000), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Accessibility Features (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 5/7: ปิดการเชื่อมต่อหน้าจอระยะไกล RDP หลังดำเนินการเสร็จ...
[RETRIEVE] Query: ปิดการเชื่อมต่อหน้าจอระยะไกล RDP หลังดำเนินการเสร็จ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Disable or Remove Feature or Program (0.229), Disable or Remove Feature or Program (0.015), RDP Hijacking (0.014), Remote Service Session Hijacking (0.004), Remote Desktop Protocol (0.004), Terminal Services DLL (0.002), Limit Access to Resource Over Network (0.001), Axiom (0.001), Chimera (0.001), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 6/7: เตรียมโฟลเดอร์บนเครื่องต้นทางที่บรรจุไฟล์สคริปต์และไฟล์โปรแกรมเรียกค่าไถ่...
[RETRIEVE] Query: เตรียมโฟลเดอร์บนเครื่องต้นทางที่บรรจุไฟล์สคริปต์และไฟล์โปรแกรมเรียกค่าไถ่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Path Interception by PATH Environment Variable (0.008), Compile After Delivery (0.005), KernelCallbackTable (0.001), Qilin (0.001), LNK Icon Smuggling (0.000), Visual Basic (0.000), Kwampirs (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Path Interception by PATH Environment Variable (11 neighbors, 11 edges)
           → Compile After Delivery (12 neighbors, 12 edges)
           → KernelCallbackTable (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งไฟล์สคริปต์และไฟล์โปรแกรมเรียกค่าไถ่ผ่านการแบ่งปันไดรฟ์ RDP ไปยังเครื่องของผู...
[RETRIEVE] Query: ส่งไฟล์สคริปต์และไฟล์โปรแกรมเรียกค่าไถ่ผ่านการแบ่งปันไดรฟ์ RDP ไปยังเครื่องของผู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Taint Shared Content (0.212), FIN10 (0.045), RDP Hijacking (0.037), FIN7 (0.018), Lateral Tool Transfer (0.016), Terminal Services DLL (0.010), Remote Desktop Protocol (0.008), Axiom (0.005), Remote Service Session Hijacking (0.001), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Taint Shared Content (18 neighbors, 18 edges)
           → FIN10 (12 neighbors, 12 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [18/100] retrieved=180 relevant=3 latency=28211ms
[RETRIEVE-QUOTA] Query 1/10: เมื่อวันที่ 14 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Query: เมื่อวันที่ 14 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.003), DRYHOOK (0.001), Threat Group-3390 (0.000), Magic Hound (0.000), Unsecured Credentials (0.000), Internal Spearphishing (0.000), Clear Windows Event Logs (0.000), Wevtutil (0.000), Password Managers (0.000), Clear Linux or Mac System Logs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Keylogging (160 neighbors, 160 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
[RETRIEVE-QUOTA] Query 2/10: โจมตีช่องโหว่เว็บเซิร์ฟเวอร์เพื่อสั่งรันคำสั่งจากระยะไกล (Exploit Public-Facing ...
[RETRIEVE] Query: โจมตีช่องโหว่เว็บเซิร์ฟเวอร์เพื่อสั่งรันคำสั่งจากระยะไกล (Exploit Public-Facing ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.784), Network Segmentation (0.452), Sandworm Team (0.352), P.A.S. Webshell (0.345), P.A.S. Webshell (0.325), Havij (0.225), Exploitation for Client Execution (0.057), PowerSploit (0.011), Exploits (0.003), Exploit Protection (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Network Segmentation (37 neighbors, 37 edges)
           → Sandworm Team (113 neighbors, 113 edges)
[RETRIEVE-QUOTA] Query 3/10: อัปโหลดไฟล์โปรแกรมและสคริปต์สั่งการผ่านหน้าเว็บเพื่อรันบนเครื่องแม่ข่าย...
[RETRIEVE] Query: อัปโหลดไฟล์โปรแกรมและสคริปต์สั่งการผ่านหน้าเว็บเพื่อรันบนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Caterpillar WebShell (0.083), ClickOnce (0.059), NavRAT (0.042), BackConfig (0.012), Web Shell (0.012), P.A.S. Webshell (0.011), Visual Basic (0.002), CrossRAT (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Caterpillar WebShell (16 neighbors, 16 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → ClickOnce (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 4/10: ฝัง Web Shell และสคริปต์ไว้บนเครื่องเพื่อกลับเข้ามาใช้งานภายหลัง...
[RETRIEVE] Query: ฝัง Web Shell และสคริปต์ไว้บนเครื่องเพื่อกลับเข้ามาใช้งานภายหลัง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Web Shell (0.091), China Chopper (0.015), Netsh Helper DLL (0.007), P.A.S. Webshell (0.002), BUSHWALK (0.002), SSH Hijacking (0.001), Caterpillar WebShell (0.000), SUPERNOVA (0.000), Gelsemium (0.000), Shell History (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Web Shell (71 neighbors, 71 edges)
           → China Chopper (19 neighbors, 19 edges)
           → Netsh Helper DLL (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 5/10: แก้ไขไฟล์บันทึกเหตุการณ์ของระบบให้ย้อนกลับไปก่อนถูกบุกรุก (Indicator Removal)...
[RETRIEVE] Query: แก้ไขไฟล์บันทึกเหตุการณ์ของระบบให้ย้อนกลับไปก่อนถูกบุกรุก (Indicator Removal)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Indicator Removal (0.261), Remote Data Storage (0.203), Indicator Removal from Tools (0.044), Remcos (0.020), File Deletion (0.011), Inhibit System Recovery (0.001), Account Access Removal (0.000), Disable or Modify Tools (0.000), Prevent Command History Logging (0.000), Operating System Configuration (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Indicator Removal (45 neighbors, 45 edges)
           → Remote Data Storage (11 neighbors, 11 edges)
           → Indicator Removal from Tools (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 6/10: ลบไฟล์โปรแกรมและสคริปต์ที่สร้างขึ้นเพื่อกลบร่องรอยการเข้าถึง...
[RETRIEVE] Query: ลบไฟล์โปรแกรมและสคริปต์ที่สร้างขึ้นเพื่อกลบร่องรอยการเข้าถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PyDCrypt (0.131), File Deletion (0.126), Disable or Remove Feature or Program (0.018), MacSpy (0.009), Execution Prevention (0.003), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → PyDCrypt (12 neighbors, 12 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
[RETRIEVE-QUOTA] Query 7/10: รวบรวมรายชื่อผู้ใช้และรหัสผ่านของระบบ...
[RETRIEVE] Query: รวบรวมรายชื่อผู้ใช้และรหัสผ่านของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SILENTTRINITY (0.431), Epic (0.246), gsecdump (0.020), Mimikatz (0.018), Nltest (0.010), Lslsass (0.008), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → SILENTTRINITY (53 neighbors, 53 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Epic (23 neighbors, 23 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] Query 8/10: รวบรวมกุญแจหลักของระบบ...
[RETRIEVE] Query: รวบรวมกุญแจหลักของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Keychain (0.113), Koadic (0.019), Koadic (0.017), Cachedump (0.007), Credential API Hooking (0.004), Firewall Enumeration (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Keychain (16 neighbors, 16 edges)
           → Koadic (31 neighbors, 31 edges)
           → NTDS (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 9/10: รวบรวมกฎของไฟร์วอลล์...
[RETRIEVE] Query: รวบรวมกฎของไฟร์วอลล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Firewall Enumeration (0.905), Firewall Metadata (0.480), Firewall Rule Modification (0.465), Cloud Firewall (0.203), Firewall Disable (0.013), OilRig (0.000), FIN7 (0.000), admin@338 (0.000), POWERTON (0.000), Local Storage Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Firewall Enumeration (0 neighbors, 0 edges)
           → Firewall Metadata (0 neighbors, 0 edges)
           → Firewall Rule Modification (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 10/10: รวมและบีบอัดไฟล์สำคัญที่รวบรวมได้เป็นไฟล์เดียวเพื่อเตรียมนำออก...
[RETRIEVE] Query: รวมและบีบอัดไฟล์สำคัญที่รวบรวมได้เป็นไฟล์เดียวเพื่อเตรียมนำออก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Compression (0.112), Data Staged (0.078), TajMahal (0.040), Archive Collected Data (0.029), Archive via Library (0.022), Ramsay (0.016), Archive via Utility (0.013), Remote Data Staging (0.004), InvisiMole (0.002), WindTail (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Compression (38 neighbors, 38 edges)
           → Data Staged (13 neighbors, 13 edges)
           → TajMahal (24 neighbors, 24 edges)
           → Automated Collection (77 neighbors, 77 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 10 queries
  [19/100] retrieved=805 relevant=3 latency=38772ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 21 ตุลาคม 2567 บริษัทผู้ผลิตชิ้นส่วนยานยนต์แห่งหนึ่งในจังหวัดปทุมธาน...
[RETRIEVE] Query: เมื่อวันที่ 21 ตุลาคม 2567 บริษัทผู้ผลิตชิ้นส่วนยานยนต์แห่งหนึ่งในจังหวัดปทุมธาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FlawedAmmyy (0.009), LookBack (0.003), Stuxnet (0.003), FIN8 (0.000), Software (0.000), CrossRAT (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Visual Basic (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → FlawedAmmyy (24 neighbors, 24 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → LookBack (16 neighbors, 16 edges)
           → System Service Discovery (71 neighbors, 71 edges)
[RETRIEVE-QUOTA] Query 2/6: ติดตั้งโปรแกรมไม่พึงประสงค์บนเครื่องคอมพิวเตอร์สำนักงานเป็นวงกว้าง...
[RETRIEVE] Query: ติดตั้งโปรแกรมไม่พึงประสงค์บนเครื่องคอมพิวเตอร์สำนักงานเป็นวงกว้าง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: EvilGrab (0.278), Limit Software Installation (0.023), Behavior Prevention on Endpoint (0.006), Empire (0.004), PsExec (0.002), Cobian RAT (0.002), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → EvilGrab (6 neighbors, 6 edges)
           → Limit Software Installation (17 neighbors, 17 edges)
           → Behavior Prevention on Endpoint (51 neighbors, 51 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] Query 3/6: เรียกดูรายการการเชื่อมต่อเครือข่ายที่เปิดค้างอยู่ หมายเลขปลายทาง และพอร์ตที่ใช้ต...
[RETRIEVE] Query: เรียกดูรายการการเชื่อมต่อเครือข่ายที่เปิดค้างอยู่ หมายเลขปลายทาง และพอร์ตที่ใช้ต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remsec (0.934), netstat (0.498), Net (0.432), OSInfo (0.417), System Network Configuration Discovery (0.356), System Network Connections Discovery (0.282), netstat (0.214), ipconfig (0.109), Internet Connection Discovery (0.040), System Owner/User Discovery (0.016)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Remsec (31 neighbors, 31 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → netstat (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/6: เก็บรวบรวมชื่อเครื่อง รุ่นระบบปฏิบัติการ และรายละเอียดการตั้งค่าของเครื่องลูกข่า...
[RETRIEVE] Query: เก็บรวบรวมชื่อเครื่อง รุ่นระบบปฏิบัติการ และรายละเอียดการตั้งค่าของเครื่องลูกข่า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SysUpdate (0.728), RATANKBA (0.647), Systeminfo (0.489), System Information Discovery (0.434), System Network Configuration Discovery (0.281), SYSCON (0.146), System Owner/User Discovery (0.063), System Service Discovery (0.043), Device Driver Discovery (0.003), Process Discovery (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SysUpdate (32 neighbors, 32 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → RATANKBA (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 5/6: สอบถามความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนขององค์กรกับโดเมนอื่น (Permission G...
[RETRIEVE] Query: สอบถามความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนขององค์กรกับโดเมนอื่น (Permission G...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.545), Domain Trust Discovery (0.365), Domain Groups (0.185), dsquery (0.177), Permission Groups Discovery (0.153), Group Policy Discovery (0.102), TrickBot (0.038), MURKYTOP (0.033), Cloud Groups (0.007), Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → Domain Groups (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] Query 6/6: ตรวจสอบว่าบัญชีผู้ใช้บนเครื่องเป็นสมาชิกของกลุ่มสิทธิ์ใดบ้างในระบบ (Account Disc...
[RETRIEVE] Query: ตรวจสอบว่าบัญชีผู้ใช้บนเครื่องเป็นสมาชิกของกลุ่มสิทธิ์ใดบ้างในระบบ (Account Disc...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TrickBot (0.314), LitePower (0.269), Account Discovery (0.260), System Owner/User Discovery (0.256), Domain Account (0.030), Cloud Groups (0.023), Wi-Fi Discovery (0.017), OSInfo (0.003), Discovery (0.001), TAINTEDSCRIBE (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → TrickBot (57 neighbors, 57 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Account Discovery (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [20/100] retrieved=596 relevant=4 latency=20890ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 17 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งซึ่งประกอบธุรกิจซื้อขายสินทรัพย...
[RETRIEVE] Query: เมื่อวันที่ 17 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งซึ่งประกอบธุรกิจซื้อขายสินทรัพย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Fakecalls (0.176), MacMa (0.131), APT39 (0.065), CURIUM (0.061), Exfiltration Over C2 Channel (0.045), Automated Exfiltration (0.014), Scheduled Transfer (0.012), Exfiltration Over Alternative Protocol (0.001), Exfiltration Over Unencrypted Non-C2 Protocol (0.000), Installer Packages (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Fakecalls (11 neighbors, 11 edges)
           → Exfiltration Over C2 Channel (31 neighbors, 31 edges)
           → MacMa (28 neighbors, 28 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
[RETRIEVE-QUOTA] Query 2/7: หลอกให้ผู้เสียหายติดตั้งโปรแกรมซื้อขายสินทรัพย์ดิจิทัลปลอมบนเครื่อง macOS...
[RETRIEVE] Query: หลอกให้ผู้เสียหายติดตั้งโปรแกรมซื้อขายสินทรัพย์ดิจิทัลปลอมบนเครื่อง macOS...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CoinTicker (0.206), macOS.OSAMiner (0.089), Operating System Configuration (0.035), Calisto (0.014), iKitten (0.014), XCSSET (0.013), Daggerfly (0.005), Proton (0.005), MacMa (0.004), Keychain (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → CoinTicker (9 neighbors, 9 edges)
           → macOS.OSAMiner (11 neighbors, 11 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → Dynamic Linker Hijacking (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 3/7: ชุดคำสั่งหลังติดตั้งทำงานผ่านตัวแปลคำสั่งของระบบ...
[RETRIEVE] Query: ชุดคำสั่งหลังติดตั้งทำงานผ่านตัวแปลคำสั่งของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Command and Scripting Interpreter (0.027), Installer Packages (0.024), cmd (0.014), Network Device CLI (0.010), FIN5 (0.008), Script Execution (0.005), Whitefly (0.005), PoshC2 (0.003), PipeMon (0.002), BONDUPDATER (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Command and Scripting Interpreter (68 neighbors, 68 edges)
           → Installer Packages (8 neighbors, 8 edges)
           → Network Device CLI (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 4/7: วางไฟล์ตั้งค่าใน Scheduled Task/Job: Launchd เพื่อให้โปรแกรมคนร้ายทำงานทุกครั้งท...
[RETRIEVE] Query: วางไฟล์ตั้งค่าใน Scheduled Task/Job: Launchd เพื่อให้โปรแกรมคนร้ายทำงานทุกครั้งท...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bad Rabbit (0.265), Launch Daemon (0.167), Operating System Configuration (0.167), Launch Agent (0.137), Scheduled Task/Job (0.079), Create or Modify System Process (0.076), At (0.024), Scheduled Task (0.012), User Account Management (0.005), Masquerade Task or Service (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bad Rabbit (16 neighbors, 16 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Launch Daemon (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 5/7: เก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่กำลังใช้งาน (System Owner/User Dis...
[RETRIEVE] Query: เก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่กำลังใช้งาน (System Owner/User Dis...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Owner/User Discovery (0.964), Epic (0.911), Micropsia (0.909), T9000 (0.890), Kimsuky (0.856), System Service Discovery (0.085), System Information Discovery (0.080), System Location Discovery (0.055), System Network Connections Discovery (0.036), Device Driver Discovery (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Epic (23 neighbors, 23 edges)
           → Micropsia (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 6/7: เข้ารหัสข้อมูลที่รวบรวมได้ด้วยกุญแจที่ฝังไว้ในตัวโปรแกรม...
[RETRIEVE] Query: เข้ารหัสข้อมูลที่รวบรวมได้ด้วยกุญแจที่ฝังไว้ในตัวโปรแกรม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Fooder (0.095), RegDuke (0.035), CorKLOG (0.027), DUSTPAN (0.015), DRYHOOK (0.010), Cachedump (0.010), Credential API Hooking (0.009), gsecdump (0.004), Password Managers (0.002), Encrypted/Encoded File (0.002)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Fooder (8 neighbors, 8 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → RegDuke (11 neighbors, 11 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งข้อมูลที่เข้ารหัสออกไปยังเว็บไซต์สั่งการของคนร้ายผ่านช่องทางเดียวกับที่ใช้รับ...
[RETRIEVE] Query: ส่งข้อมูลที่เข้ารหัสออกไปยังเว็บไซต์สั่งการของคนร้ายผ่านช่องทางเดียวกับที่ใช้รับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over C2 Channel (0.977), BlackByte (0.918), Kevin (0.874), Okrum (0.841), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.747), APT39 (0.738), Automated Exfiltration (0.670), Exfiltration Over Unencrypted Non-C2 Protocol (0.560), Scheduled Transfer (0.548), Data Staged (0.017)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → BlackByte (56 neighbors, 56 edges)
           → Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [21/100] retrieved=307 relevant=4 latency=30578ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 6 พฤศจิกายน 2566 สถานเอกอัครราชทูตแห่งหนึ่งแจ้งว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Query: เมื่อวันที่ 6 พฤศจิกายน 2566 สถานเอกอัครราชทูตแห่งหนึ่งแจ้งว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackdoorDiplomacy (0.044), BackdoorDiplomacy (0.009), File Deletion (0.003), APT-C-36 (0.002), Ursnif (0.001), APT-C-36 (0.000), Internal Spearphishing (0.000), Password Managers (0.000), Data Encrypted for Impact (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BackdoorDiplomacy (20 neighbors, 20 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Peripheral Device Discovery (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] Query 2/5: ลบไฟล์เครื่องมือสั่งงานเครื่องระยะไกล ไฟล์ตัวติดตั้งโปรแกรมฝังตัว และไฟล์เครื่อง...
[RETRIEVE] Query: ลบไฟล์เครื่องมือสั่งงานเครื่องระยะไกล ไฟล์ตัวติดตั้งโปรแกรมฝังตัว และไฟล์เครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ODAgent (0.154), WhisperGate (0.098), ROADSWEEP (0.066), File Deletion (0.050), SDelete (0.011), Cachedump (0.002), Lslsass (0.001), Security Account Manager (0.001), MgBot (0.000), gsecdump (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → ODAgent (10 neighbors, 10 edges)
           → File Deletion (310 neighbors, 310 edges)
           → WhisperGate (29 neighbors, 29 edges)
[RETRIEVE-QUOTA] Query 3/5: โปรแกรมฝังตัวสั่งแจกแจงรายการโปรแกรมและกระบวนการที่กำลังทำงานอยู่บนเครื่อง...
[RETRIEVE] Query: โปรแกรมฝังตัวสั่งแจกแจงรายการโปรแกรมและกระบวนการที่กำลังทำงานอยู่บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.432), Rising Sun (0.369), VERMIN (0.215), schtasks (0.083), 4H RAT (0.004), Cobian RAT (0.004), Cardinal RAT (0.003), CrossRAT (0.002), Visual Basic (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Rising Sun (21 neighbors, 21 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Tasklist (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 4/5: ค้นหากระบวนการที่ทำงานภายใต้สิทธิ์ของผู้ดูแลโดเมน...
[RETRIEVE] Query: ค้นหากระบวนการที่ทำงานภายใต้สิทธิ์ของผู้ดูแลโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BISCUIT (0.067), Domain Groups (0.066), Nltest (0.058), OSInfo (0.044), Latrodectus (0.033), BADHATCH (0.018), Domain Accounts (0.016), NTDS (0.016), Domain Account (0.012), Domain Account (0.010)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Domain Groups (41 neighbors, 41 edges)
           → BISCUIT (11 neighbors, 11 edges)
           → Process Discovery (320 neighbors, 320 edges)
[RETRIEVE-QUOTA] Query 5/5: สร้างบัญชีผู้ใช้ใหม่ในโดเมนขององค์กรและกำหนดสิทธิ์ระดับผู้ดูแลเพื่อคงช่องทางกลับ...
[RETRIEVE] Query: สร้างบัญชีผู้ใช้ใหม่ในโดเมนขององค์กรและกำหนดสิทธิ์ระดับผู้ดูแลเพื่อคงช่องทางกลับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: User Account Management (0.261), Active Directory Object Creation (0.141), Empire (0.100), Domain Account (0.079), Create Account (0.059), Local Account (0.010), User Account Creation (0.008), Network Segmentation (0.006), Operating System Configuration (0.006), Cloud Account (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → User Account Management (119 neighbors, 119 edges)
           → Create Cloud Instance (7 neighbors, 7 edges)
           → Active Directory Object Creation (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [22/100] retrieved=763 relevant=3 latency=26443ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 30 มิถุนายน 2565 บริษัทขนส่งแห่งหนึ่งในจังหวัดพระนครศรีอยุธยาแจ้งควา...
[RETRIEVE] Query: เมื่อวันที่ 30 มิถุนายน 2565 บริษัทขนส่งแห่งหนึ่งในจังหวัดพระนครศรีอยุธยาแจ้งควา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.005), Data Encrypted for Impact (0.003), BlackByte (0.001), Deobfuscate/Decode Files or Information (0.001), Adversary-in-the-Middle (0.000), Evil Twin (0.000), Magic Hound (0.000), ARP Cache Poisoning (0.000), Threat Group-3390 (0.000), Anthropic AI-orchestrated Campaign (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] Query 2/6: สั่งเครื่องแม่ข่ายและเครื่องลูกข่ายเริ่มระบบใหม่เข้าสู่โหมดปลอดภัยเพื่อไม่ให้โปร...
[RETRIEVE] Query: สั่งเครื่องแม่ข่ายและเครื่องลูกข่ายเริ่มระบบใหม่เข้าสู่โหมดปลอดภัยเพื่อไม่ให้โปร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Safe Mode Boot (0.097), System Partition Integrity (0.070), Defense Impairment (0.046), User Guidance (0.042), Exploitation for Defense Impairment (0.014), System Shutdown/Reboot (0.003), Power Settings (0.002), Parent PID Spoofing (0.000), Execution Prevention (0.000), STEADYPULSE (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Safe Mode Boot (10 neighbors, 10 edges)
           → System Partition Integrity (7 neighbors, 7 edges)
           → Impair Defenses (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 3/6: เข้ารหัสไฟล์งานของผู้เสียหายด้วยอัลกอริทึมสมมาตร 256 บิตและเข้ารหัสกุญแจซ้ำด้วยก...
[RETRIEVE] Query: เข้ารหัสไฟล์งานของผู้เสียหายด้วยอัลกอริทึมสมมาตร 256 บิตและเข้ารหัสกุญแจซ้ำด้วยก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NotPetya (0.919), LockBit 3.0 (0.880), Data Encrypted for Impact (0.801), Avaddon (0.675), BitPaymer (0.420), Encrypted/Encoded File (0.259), Asymmetric Cryptography (0.091), Impact (0.007), Backup Software Discovery (0.005), Account Access Removal (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → NotPetya (15 neighbors, 15 edges)
           → LockBit 3.0 (34 neighbors, 34 edges)
[RETRIEVE-QUOTA] Query 4/6: ลบข้อมูลสำรองที่เก็บไว้ในเครื่องเพื่อขัดขวางการกู้คืนข้อมูล (Inhibit System Reco...
[RETRIEVE] Query: ลบข้อมูลสำรองที่เก็บไว้ในเครื่องเพื่อขัดขวางการกู้คืนข้อมูล (Inhibit System Reco...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Inhibit System Recovery (0.940), Conficker (0.933), EKANS (0.902), Operating System Configuration (0.569), SDelete (0.069), Backup Software Discovery (0.048), System Shutdown/Reboot (0.003), Disable or Remove Feature or Program (0.001), Systemd Service (0.001), Limit Hardware Installation (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → Conficker (13 neighbors, 13 edges)
           → EKANS (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 5/6: ปิดตัวเลือกการกู้คืนระบบตอนเริ่มเครื่อง (Inhibit System Recovery)...
[RETRIEVE] Query: ปิดตัวเลือกการกู้คืนระบบตอนเริ่มเครื่อง (Inhibit System Recovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Inhibit System Recovery (0.774), Operating System Configuration (0.447), H1N1 (0.363), Embargo (0.261), Conficker (0.242), System Shutdown/Reboot (0.011), Backup Software Discovery (0.008), Systemd Service (0.003), Limit Hardware Installation (0.000), Disable or Remove Feature or Program (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → H1N1 (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 6/6: ลบสำเนาเงาของไฟล์ทั้งหมดเพื่อป้องกันการกู้คืนข้อมูล (Inhibit System Recovery)...
[RETRIEVE] Query: ลบสำเนาเงาของไฟล์ทั้งหมดเพื่อป้องกันการกู้คืนข้อมูล (Inhibit System Recovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: EKANS (0.903), Inhibit System Recovery (0.850), ROADSWEEP (0.710), Operating System Configuration (0.441), Conficker (0.304), SDelete (0.018), Backup Software Discovery (0.007), System Shutdown/Reboot (0.001), Disable or Remove Feature or Program (0.000), Revert Cloud Instance (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → EKANS (9 neighbors, 9 edges)
           → ROADSWEEP (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] 14 vectors (quota 3/query), 8 subgraphs from 6 queries
  [23/100] retrieved=375 relevant=2 latency=27584ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 25 มกราคม 2567 โรงแรมแห่งหนึ่งในจังหวัดภูเก็ตแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Query: เมื่อวันที่ 25 มกราคม 2567 โรงแรมแห่งหนึ่งในจังหวัดภูเก็ตแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Denis (0.001), Darkhotel (0.001), RDP Hijacking (0.000), FIN8 (0.000), Reg (0.000), Scheduled Task/Job (0.000), Windows Remote Management (0.000), Right-to-Left Override (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Denis (21 neighbors, 21 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Darkhotel (24 neighbors, 24 edges)
           → Process Discovery (320 neighbors, 320 edges)
[RETRIEVE-QUOTA] Query 2/5: ควบคุมเครื่องคอมพิวเตอร์แผนกต้อนรับจากระยะไกล (Remote Access)...
[RETRIEVE] Query: ควบคุมเครื่องคอมพิวเตอร์แผนกต้อนรับจากระยะไกล (Remote Access)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Access Tools (0.051), Execution Prevention (0.035), Remote Desktop Software (0.030), RemoteUtilities (0.030), RemoteCMD (0.026), Remote Desktop Protocol (0.024), RemoteCMD (0.006), Windows Remote Management (0.005), Quick Assist (0.005), Drive Access (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Remote Access Tools (31 neighbors, 31 edges)
           → Remote Desktop Software (21 neighbors, 21 edges)
           → Execution Prevention (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] Query 3/5: โปรแกรมแปลกปลอมบันทึกภาพสิ่งที่ปรากฏบนหน้าจอพนักงานเป็นระยะ (Screen Capture)...
[RETRIEVE] Query: โปรแกรมแปลกปลอมบันทึกภาพสิ่งที่ปรากฏบนหน้าจอพนักงานเป็นระยะ (Screen Capture)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: POORAIM (0.399), PowerSploit (0.348), AsyncRAT (0.100), Screen Capture (0.091), Video Capture (0.017), GUI Input Capture (0.012), Input Capture (0.006), Keydnap (0.003), HenBox (0.002), Audio Capture (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → POORAIM (7 neighbors, 7 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → PowerSploit (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 4/5: สั่งให้ไฟล์โปรแกรมที่วางไว้บนเครื่องเริ่มทำงานผ่านหน้าต่างพิมพ์คำสั่งของ Windows...
[RETRIEVE] Query: สั่งให้ไฟล์โปรแกรมที่วางไว้บนเครื่องเริ่มทำงานผ่านหน้าต่างพิมพ์คำสั่งของ Windows...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.153), Windows Command Shell (0.066), Forfiles (0.041), HOPLIGHT (0.037), cmd (0.029), PowerShell (0.021), CozyCar (0.021), Indirect Command Execution (0.013), Command and Scripting Interpreter (0.006), Shell History (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → cmd (13 neighbors, 13 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → HOPLIGHT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 5/5: ไล่ตรวจสอบรายการกระบวนการที่กำลังทำงานอยู่ทั้งหมดบนเครื่อง (Process Discovery)...
[RETRIEVE] Query: ไล่ตรวจสอบรายการกระบวนการที่กำลังทำงานอยู่ทั้งหมดบนเครื่อง (Process Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Socksbot (0.733), Tasklist (0.692), Process Discovery (0.255), Taidoor (0.171), Tasklist (0.160), KillDisk (0.157), System Owner/User Discovery (0.008), System Information Discovery (0.005), System Network Connections Discovery (0.002), Discovery (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Socksbot (5 neighbors, 5 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Tasklist (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [24/100] retrieved=616 relevant=3 latency=20701ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 12 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งว่าเครื่องคอมพิวเต...
[RETRIEVE] Query: เมื่อวันที่ 12 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งว่าเครื่องคอมพิวเต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.048), APT29 (0.040), Password Spraying (0.025), CrackMapExec (0.003), Password Cracking (0.001), Password Guessing (0.000), Password Managers (0.000), Active Setup (0.000), Subvert Trust Controls (0.000), Password Policies (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Password Spraying (23 neighbors, 23 edges)
           → APT29 (117 neighbors, 117 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมควบคุมระยะไกลถูกฝังบนเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ระดับบริหาร...
[RETRIEVE] Query: โปรแกรมควบคุมระยะไกลถูกฝังบนเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ระดับบริหาร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteUtilities (0.040), PsExec (0.017), PsExec (0.010), RemoteCMD (0.008), PsExec (0.006), Cobian RAT (0.001), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteUtilities (5 neighbors, 5 edges)
           → PsExec (49 neighbors, 49 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
[RETRIEVE-QUOTA] Query 3/8: โปรแกรมฝังตัวที่ทำงานด้วยสิทธิ์ระดับระบบเรียกตัวติดตั้งโปรแกรมฝังตัวรุ่นถัดไป...
[RETRIEVE] Query: โปรแกรมฝังตัวที่ทำงานด้วยสิทธิ์ระดับระบบเรียกตัวติดตั้งโปรแกรมฝังตัวรุ่นถัดไป...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Elevated Execution with Prompt (0.010), Installer Packages (0.006), APT3 (0.005), MegaCortex (0.004), AppCert DLLs (0.002), OldBoot (0.001), Active Setup (0.001), Credential API Hooking (0.001), Ptrace System Calls (0.001), IMAPLoader (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Elevated Execution with Prompt (5 neighbors, 5 edges)
           → Installer Packages (8 neighbors, 8 edges)
           → APT3 (50 neighbors, 50 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
[RETRIEVE-QUOTA] Query 4/8: ตัวติดตั้งโปรแกรมฝังตัวแก้ไขค่าในทะเบียนระบบเพื่อวางการตั้งค่าของตนเอง...
[RETRIEVE] Query: ตัวติดตั้งโปรแกรมฝังตัวแก้ไขค่าในทะเบียนระบบเพื่อวางการตั้งค่าของตนเอง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BitPaymer (0.055), Conficker (0.048), WastedLocker (0.009), AADInternals (0.008), Modify Registry (0.004), Windows Registry Key Modification (0.003), Active Setup (0.003), Modify System Image (0.001), Plist File Modification (0.000), XDG Autostart Entries (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BitPaymer (19 neighbors, 19 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → Conficker (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 5/8: โปรแกรมฝังตัวตรวจสอบชื่อบัญชีผู้ใช้ที่กำลังใช้งานบนระบบ...
[RETRIEVE] Query: โปรแกรมฝังตัวตรวจสอบชื่อบัญชีผู้ใช้ที่กำลังใช้งานบนระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QakBot (0.293), System Owner/User Discovery (0.112), StrongPity (0.066), UACMe (0.036), CrossRAT (0.008), sqlmap (0.003), Nltest (0.001), Cardinal RAT (0.001), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → QakBot (74 neighbors, 74 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → StrongPity (28 neighbors, 28 edges)
           → Process Discovery (320 neighbors, 320 edges)
[RETRIEVE-QUOTA] Query 6/8: โปรแกรมดาวน์โหลดสคริปต์เข้ามายังเครื่อง...
[RETRIEVE] Query: โปรแกรมดาวน์โหลดสคริปต์เข้ามายังเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: KOCTOPUS (0.486), OilBooster (0.097), Bandook (0.096), Get2 (0.088), PsExec (0.044), Cobian RAT (0.002), Visual Basic (0.002), CrossRAT (0.002), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → KOCTOPUS (21 neighbors, 21 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Bandook (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] Query 7/8: ทำ Password Spraying โดยลองรหัสผ่านที่คาดเดาง่ายกับบัญชีผู้ดูแลโดเมนหลายบัญชี...
[RETRIEVE] Query: ทำ Password Spraying โดยลองรหัสผ่านที่คาดเดาง่ายกับบัญชีผู้ดูแลโดเมนหลายบัญชี...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Password Spraying (0.897), Chimera (0.250), Multi-factor Authentication (0.036), Password Guessing (0.013), CrackMapExec (0.013), Credential Stuffing (0.003), Password Policy Discovery (0.001), Password Cracking (0.001), Password Policies (0.000), Password Managers (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Password Spraying (23 neighbors, 23 edges)
           → Chimera (65 neighbors, 65 edges)
           → Multi-factor Authentication (48 neighbors, 48 edges)
[RETRIEVE-QUOTA] Query 8/8: พยายามเชื่อมต่อไดรฟ์ของเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: พยายามเชื่อมต่อไดรฟ์ของเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DCSync (0.012), Volt Typhoon (0.002), Rogue Domain Controller (0.001), Domain Controller Authentication (0.001), DNS (0.000), CrossRAT (0.000), Software Configuration (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DCSync (14 neighbors, 14 edges)
           → Volt Typhoon (100 neighbors, 100 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [25/100] retrieved=252 relevant=3 latency=29915ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 21 กุมภาพันธ์ 2565 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าตรวจพบโปรแกรมไม...
[RETRIEVE] Query: เมื่อวันที่ 21 กุมภาพันธ์ 2565 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าตรวจพบโปรแกรมไม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CLAIMLOADER (0.252), DLL (0.172), PowGoop (0.112), POWERSOURCE (0.052), POWERSOURCE (0.011), Netwalker (0.006), StrelaStealer (0.005), PowerShell (0.001), PowerShell Profile (0.000), Rundll32 (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DLL (123 neighbors, 123 edges)
           → CLAIMLOADER (12 neighbors, 12 edges)
           → PowGoop (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 2/6: วางไฟล์สคริปต์ PowerShell ที่อำพรางนามสกุลเป็นไฟล์ข้อมูลธรรมดาบนเครื่องแม่ข่าย...
[RETRIEVE] Query: วางไฟล์สคริปต์ PowerShell ที่อำพรางนามสกุลเป็นไฟล์ข้อมูลธรรมดาบนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: POWERSOURCE (0.107), POWERSOURCE (0.019), Invoke-PSImage (0.013), PureCrypter (0.008), POWERSTATS (0.005), PowerSploit (0.004), Netwalker (0.003), PowerShell (0.003), PowerShell Profile (0.002), Disable or Remove Feature or Program (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → POWERSOURCE (7 neighbors, 7 edges)
           → NTFS File Attributes (19 neighbors, 19 edges)
           → Invoke-PSImage (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] Query 3/6: สคริปต์ PowerShell ถอดรหัสและเรียกใช้สคริปต์ PowerShell อีกชั้นที่ถูกอำพราง...
[RETRIEVE] Query: สคริปต์ PowerShell ถอดรหัสและเรียกใช้สคริปต์ PowerShell อีกชั้นที่ถูกอำพราง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Netwalker (0.942), Chimera (0.565), PowerShell (0.091), POWERSTATS (0.080), PowerSploit (0.077), PowerShower (0.029), PowerShell Profile (0.024), POWERSTATS (0.007), Invoke-PSImage (0.007), Disable or Remove Feature or Program (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Netwalker (18 neighbors, 18 edges)
           → Command Obfuscation (74 neighbors, 74 edges)
           → Chimera (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 4/6: ใช้ DLL Side-Loading หลอกโปรแกรมที่ถูกต้องให้เรียกไฟล์ DLL ของคนร้ายขึ้นมาทำงาน...
[RETRIEVE] Query: ใช้ DLL Side-Loading หลอกโปรแกรมที่ถูกต้องให้เรียกไฟล์ DLL ของคนร้ายขึ้นมาทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Javali (0.920), Sidewinder (0.870), PAKLOG (0.857), DLL (0.736), Pandora (0.699), AppCert DLLs (0.023), Print Processors (0.018), Dynamic Linker Hijacking (0.012), Rundll32 (0.010), Dynamic-link Library Injection (0.006)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Javali (12 neighbors, 12 edges)
           → DLL (123 neighbors, 123 edges)
           → Sidewinder (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 5/6: อำพรางเนื้อหาสคริปต์ PowerShell เพื่อซ่อนคำสั่งติดต่อเครื่องสั่งการ...
[RETRIEVE] Query: อำพรางเนื้อหาสคริปต์ PowerShell เพื่อซ่อนคำสั่งติดต่อเครื่องสั่งการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Empire (0.934), Command Obfuscation (0.871), Sardonic (0.858), POWERSOURCE (0.244), POWERSTATS (0.040), PowerShell (0.016), POWRUNER (0.012), PowerShell Profile (0.009), Disable or Remove Feature or Program (0.003), POWERSTATS (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Command Obfuscation (74 neighbors, 74 edges)
           → Empire (91 neighbors, 91 edges)
           → Sardonic (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 6/6: เปลี่ยนชื่อไฟล์ DLL ของคนร้ายให้ตรงกับชื่อไฟล์ของโปรแกรมที่ถูกต้องเพื่อให้ DLL S...
[RETRIEVE] Query: เปลี่ยนชื่อไฟล์ DLL ของคนร้ายให้ตรงกับชื่อไฟล์ของโปรแกรมที่ถูกต้องเพื่อให้ DLL S...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Javali (0.137), PAKLOG (0.127), Sidewinder (0.121), DLL (0.116), Pandora (0.087), Rundll32 (0.009), AppCert DLLs (0.006), Dynamic-link Library Injection (0.002), Dynamic Linker Hijacking (0.001), Authentication Package (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → DLL (123 neighbors, 123 edges)
           → Javali (12 neighbors, 12 edges)
           → PAKLOG (11 neighbors, 11 edges)
           → Code Signing (90 neighbors, 90 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [26/100] retrieved=222 relevant=3 latency=27700ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 27 ตุลาคม 2563 หน่วยงานวิจัยแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Query: เมื่อวันที่ 27 ตุลาคม 2563 หน่วยงานวิจัยแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NanHaiShu (0.073), APT32 (0.032), FIN7 (0.027), Mshta (0.001), SideCopy (0.001), Maze (0.000), Ingress Tool Transfer (0.000), Winexe (0.000), Msiexec (0.000), cmd (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → NanHaiShu (13 neighbors, 13 edges)
           → Mshta (34 neighbors, 34 edges)
           → APT32 (93 neighbors, 93 edges)
[RETRIEVE-QUOTA] Query 2/8: อีเมล Spearphishing Attachment แนบไฟล์เอกสารอันตรายหลอกนักวิจัยให้เปิด...
[RETRIEVE] Query: อีเมล Spearphishing Attachment แนบไฟล์เอกสารอันตรายหลอกนักวิจัยให้เปิด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.958), Chaes (0.923), Spearphishing Attachment (0.849), Malicious File (0.838), Spearphishing Attachment (0.694), Spearphishing Link (0.649), CURIUM (0.528), RTM (0.446), Spearphishing Service (0.038), Internal Spearphishing (0.007)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Leviathan (68 neighbors, 68 edges)
[RETRIEVE-QUOTA] Query 3/8: อีเมล Spearphishing Link อ้างแจ้งเตือนความปลอดภัยของบัญชีพร้อมลิงก์...
[RETRIEVE] Query: อีเมล Spearphishing Link อ้างแจ้งเตือนความปลอดภัยของบัญชีพร้อมลิงก์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Spearphishing Link (0.660), AADInternals (0.326), OilRig (0.290), Spearphishing Link (0.203), Operation Spalax (0.179), Link Target (0.072), Audit (0.034), Spearphishing Attachment (0.030), Spearphishing Service (0.016), Internal Spearphishing (0.011)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Spearphishing Link (93 neighbors, 93 edges)
           → AADInternals (26 neighbors, 26 edges)
           → Spearphishing Link (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 4/8: ดัดแปลงเว็บไซต์ที่กลุ่มเป้าหมายเข้าใช้ประจำให้ติดตั้งโปรแกรมลงเครื่องผู้เข้าชม (...
[RETRIEVE] Query: ดัดแปลงเว็บไซต์ที่กลุ่มเป้าหมายเข้าใช้ประจำให้ติดตั้งโปรแกรมลงเครื่องผู้เข้าชม (...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Drive-by Compromise (0.377), Drive-by Target (0.194), Elderwood (0.173), CURIUM (0.091), KARAE (0.083), Content Injection (0.054), User Training (0.024), SEO Poisoning (0.013), Server (0.010), Supply Chain Compromise (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Drive-by Compromise (51 neighbors, 51 edges)
           → Drive-by Target (12 neighbors, 12 edges)
           → Elderwood (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 5/8: แจกจ่ายโปรแกรมอันตรายผ่านเว็บแบ่งปันไฟล์...
[RETRIEVE] Query: แจกจ่ายโปรแกรมอันตรายผ่านเว็บแบ่งปันไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AshTag (0.922), Taint Shared Content (0.791), Chameleon (0.584), StreamEx (0.107), EvilGrab (0.039), CrossRAT (0.002), Cobian RAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Taint Shared Content (18 neighbors, 18 edges)
           → AshTag (20 neighbors, 20 edges)
           → Web Service (56 neighbors, 56 edges)
[RETRIEVE-QUOTA] Query 6/8: หลอกผู้เสียหายให้ติดตั้งส่วนขยายเว็บเบราว์เซอร์ที่คนร้ายสร้างขึ้นเพื่อแทรกกลางกา...
[RETRIEVE] Query: หลอกผู้เสียหายให้ติดตั้งส่วนขยายเว็บเบราว์เซอร์ที่คนร้ายสร้างขึ้นเพื่อแทรกกลางกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bundlore (0.515), Software Extensions (0.250), Browser Extensions (0.212), SimBad (0.066), TRANSLATEXT (0.060), HALFBAKED (0.002), Visual Basic (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bundlore (23 neighbors, 23 edges)
           → Browser Extensions (15 neighbors, 15 edges)
           → Software Extensions (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 7/8: ใช้ mshta.exe ดาวน์โหลดไฟล์ HTML Application จากเครื่องปลายทางภายนอก...
[RETRIEVE] Query: ใช้ mshta.exe ดาวน์โหลดไฟล์ HTML Application จากเครื่องปลายทางภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BabyShark (0.897), Lazarus Group (0.672), Pteranodon (0.576), Mshta (0.286), APT38 (0.276), Mavinject (0.002), P.A.S. Webshell (0.001), Compiled HTML File (0.000), Electron Applications (0.000), Application Isolation and Sandboxing (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BabyShark (17 neighbors, 17 edges)
           → Mshta (34 neighbors, 34 edges)
           → Lazarus Group (120 neighbors, 120 edges)
[RETRIEVE-QUOTA] Query 8/8: ใช้ mshta.exe สั่งรันไฟล์ HTML Application ที่ดาวน์โหลดมา...
[RETRIEVE] Query: ใช้ mshta.exe สั่งรันไฟล์ HTML Application ที่ดาวน์โหลดมา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lazarus Group (0.976), APT38 (0.831), Mshta (0.670), BabyShark (0.555), MSBuild (0.010), Msiexec (0.002), Mavinject (0.001), Compiled HTML File (0.001), Electron Applications (0.000), JavaScript (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Lazarus Group (120 neighbors, 120 edges)
           → Mshta (34 neighbors, 34 edges)
           → APT38 (62 neighbors, 62 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [27/100] retrieved=357 relevant=4 latency=32489ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 12 กรกฎาคม 2565 บริษัทรับจ้างผลิตแห่งหนึ่งในจังหวัดสมุทรสาครแจ้งความ...
[RETRIEVE] Query: เมื่อวันที่ 12 กรกฎาคม 2565 บริษัทรับจ้างผลิตแห่งหนึ่งในจังหวัดสมุทรสาครแจ้งความ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Daggerfly (0.084), C0021 (0.067), Netwalker (0.067), POWERSTATS (0.032), POWERSTATS (0.010), POWERSOURCE (0.009), PowerShell Profile (0.000), PowerShell (0.000), ServHelper (0.000), Disable or Remove Feature or Program (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Daggerfly (23 neighbors, 23 edges)
           → PowerShell (241 neighbors, 241 edges)
           → C0021 (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 2/7: เข้าถึงเครื่องแม่ข่ายผ่านบริการเดสก์ท็อประยะไกล (RDP) ที่เปิดจากอินเทอร์เน็ตและใ...
[RETRIEVE] Query: เข้าถึงเครื่องแม่ข่ายผ่านบริการเดสก์ท็อประยะไกล (RDP) ที่เปิดจากอินเทอร์เน็ตและใ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RDP Hijacking (0.149), Remote Desktop Protocol (0.062), BlackByte (0.052), Play (0.050), SILENTTRINITY (0.007), Carbanak (0.005), Remote Services (0.002), PingPull (0.002), FRP (0.001), DUSTTRAP (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → BlackByte (56 neighbors, 56 edges)
[RETRIEVE-QUOTA] Query 3/7: ส่งอีเมลหลอกลวงและอีเมลขยะจำนวนมากพร้อมแนบไฟล์โปรแกรมเรียกค่าไถ่ให้พนักงาน...
[RETRIEVE] Query: ส่งอีเมลหลอกลวงและอีเมลขยะจำนวนมากพร้อมแนบไฟล์โปรแกรมเรียกค่าไถ่ให้พนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: menuPass (0.497), FIN7 (0.399), Gallmaker (0.327), Squirrelwaffle (0.146), Spearphishing Attachment (0.129), Squirrelwaffle (0.023), Email Accounts (0.006), Email Bombing (0.004), EvilGrab (0.004), Financial Theft (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → menuPass (71 neighbors, 71 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → FIN7 (86 neighbors, 86 edges)
[RETRIEVE-QUOTA] Query 4/7: ใช้ไฟล์แบตช์เรียกสคริปต์ PowerShell ให้ทำงาน...
[RETRIEVE] Query: ใช้ไฟล์แบตช์เรียกสคริปต์ PowerShell ให้ทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Invoke-PSImage (0.031), PowerShell (0.023), PowerPunch (0.009), PowerShell Profile (0.007), POWRUNER (0.005), POWERSOURCE (0.003), POWERSTATS (0.001), BONDUPDATER (0.001), POWERSTATS (0.000), Disable or Remove Feature or Program (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PowerShell (241 neighbors, 241 edges)
           → Invoke-PSImage (3 neighbors, 3 edges)
           → PowerPunch (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 5/7: ใช้ PowerShell โหลดโปรแกรมเรียกค่าไถ่เข้าไปทำงานในหน่วยความจำโดยไม่เขียนไฟล์ลงดิ...
[RETRIEVE] Query: ใช้ PowerShell โหลดโปรแกรมเรียกค่าไถ่เข้าไปทำงานในหน่วยความจำโดยไม่เขียนไฟล์ลงดิ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Deep Panda (0.975), Netwalker (0.927), PowerShower (0.141), PowerLess (0.044), PowerShell (0.013), POWERSTATS (0.012), Disable or Remove Feature or Program (0.004), PowerShell Profile (0.002), POWERSTATS (0.002), Invoke-PSImage (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Deep Panda (17 neighbors, 17 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Netwalker (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 6/7: เข้ารหัสลับไฟล์งานในเครื่องแม่ข่ายเพื่อเรียกค่าไถ่...
[RETRIEVE] Query: เข้ารหัสลับไฟล์งานในเครื่องแม่ข่ายเพื่อเรียกค่าไถ่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Black Basta (0.085), Data Encrypted for Impact (0.071), Encrypted/Encoded File (0.050), Deobfuscate/Decode Files or Information (0.011), ThiefQuest (0.005), KernelCallbackTable (0.005), REvil (0.002), FIN13 (0.001), UNC3886 (0.001), Archive via Utility (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → Black Basta (27 neighbors, 27 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
[RETRIEVE-QUOTA] Query 7/7: แสดงข้อความเรียกค่าไถ่หลังเข้ารหัสไฟล์งานของผู้เสียหาย...
[RETRIEVE] Query: แสดงข้อความเรียกค่าไถ่หลังเข้ารหัสไฟล์งานของผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ShrinkLocker (0.034), REvil (0.022), Black Basta (0.015), KernelCallbackTable (0.002), ISMInjector (0.001), Deobfuscate/Decode Files or Information (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → ShrinkLocker (21 neighbors, 21 edges)
           → REvil (37 neighbors, 37 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [28/100] retrieved=445 relevant=3 latency=35334ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 13 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบยูนิกซ์...
[RETRIEVE] Query: เมื่อวันที่ 13 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบยูนิกซ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Indrik Spider (0.016), PlugX (0.013), Unsecured Credentials (0.002), Ingress Tool Transfer (0.001), OS Credential Dumping (0.000), Valid Accounts (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), Clear Linux or Mac System Logs (0.000), Clear Windows Event Logs (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Indrik Spider (41 neighbors, 41 edges)
           → Credentials In Files (44 neighbors, 44 edges)
           → PlugX (65 neighbors, 65 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 2/7: ส่งคำสั่งระบบยูนิกซ์จากหมายเลขไอพีเดียวกันมายังเครื่องแม่ข่ายระยะไกล...
[RETRIEVE] Query: ส่งคำสั่งระบบยูนิกซ์จากหมายเลขไอพีเดียวกันมายังเครื่องแม่ข่ายระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.022), RemoteCMD (0.005), xCmd (0.004), xCmd (0.003), Siloscape (0.002), Command and Scripting Interpreter (0.002), Inter-Process Communication (0.002), ROADSWEEP (0.001), Non-Application Layer Protocol (0.001), XPC Services (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → xCmd (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 3/7: เปิดอ่านไฟล์รายชื่อบัญชีผู้ใช้ของระบบ...
[RETRIEVE] Query: เปิดอ่านไฟล์รายชื่อบัญชีผู้ใช้ของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remsec (0.085), CrackMapExec (0.040), Local Account (0.035), System Owner/User Discovery (0.019), Account Discovery (0.017), PoshC2 (0.012), Cloud Account (0.006), UACMe (0.005), InvisiMole (0.002), Nltest (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Remsec (31 neighbors, 31 edges)
           → Local Account (69 neighbors, 69 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 4/7: เปิดอ่านไฟล์ที่เก็บค่ารหัสผ่านของระบบ...
[RETRIEVE] Query: เปิดอ่านไฟล์ที่เก็บค่ารหัสผ่านของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials In Files (0.849), Emotet (0.443), Empire (0.225), /etc/passwd and /etc/shadow (0.190), Cachedump (0.159), Credentials in Registry (0.122), Credentials from Password Stores (0.085), PoshC2 (0.072), PoshC2 (0.061), Password Managers (0.024)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials In Files (44 neighbors, 44 edges)
           → Emotet (48 neighbors, 48 edges)
           → /etc/passwd and /etc/shadow (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/7: เปลี่ยนสิทธิ์การเข้าถึงไฟล์ที่ซ่อนไว้ในโฟลเดอร์ไฟล์ชั่วคราว...
[RETRIEVE] Query: เปลี่ยนสิทธิ์การเข้าถึงไฟล์ที่ซ่อนไว้ในโฟลเดอร์ไฟล์ชั่วคราว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File and Directory Permissions Modification (0.030), Windows Permissions (0.015), BackConfig (0.011), Hidden Files and Directories (0.010), Restrict File and Directory Permissions (0.008), Restrict File and Directory Permissions (0.007), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → File and Directory Permissions Modification (6 neighbors, 6 edges)
           → Windows Permissions (16 neighbors, 16 edges)
           → Hidden Files and Directories (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] Query 6/7: เข้ารหัสคำสั่งและผลลัพธ์ที่รับส่งด้วยกุญแจลับเพื่อหลบเลี่ยงการตรวจจับ...
[RETRIEVE] Query: เข้ารหัสคำสั่งและผลลัพธ์ที่รับส่งด้วยกุญแจลับเพื่อหลบเลี่ยงการตรวจจับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Command Obfuscation (0.581), Data Obfuscation (0.365), Encrypted Channel (0.319), Obfuscated Files or Information (0.124), Encrypt Sensitive Information (0.072), Sardonic (0.046), Ixeshe (0.042), Encrypted/Encoded File (0.038), Encrypt Sensitive Information (0.034), Exfiltration Over Unencrypted Non-C2 Protocol (0.008)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Command Obfuscation (74 neighbors, 74 edges)
           → Data Obfuscation (21 neighbors, 21 edges)
           → Encrypted Channel (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 7/7: ดาวน์โหลดโปรแกรมเปิดช่องทางส่งต่อการเชื่อมต่อแบบย้อนกลับเพื่อเข้าถึงเครือข่ายภาย...
[RETRIEVE] Query: ดาวน์โหลดโปรแกรมเปิดช่องทางส่งต่อการเชื่อมต่อแบบย้อนกลับเพื่อเข้าถึงเครือข่ายภาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gomir (0.461), FRP (0.070), REPTILE (0.046), Internal Proxy (0.012), Expand (0.005), LookBack (0.003), cmd (0.003), Net Crawler (0.002), cmd (0.000), route (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Gomir (15 neighbors, 15 edges)
           → Internal Proxy (39 neighbors, 39 edges)
           → FRP (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [29/100] retrieved=655 relevant=5 latency=33951ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 4 สิงหาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความว่าฐานข้อมูลสำรองของระบ...
[RETRIEVE] Query: เมื่อวันที่ 4 สิงหาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความว่าฐานข้อมูลสำรองของระบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.003), File Deletion (0.002), FIN8 (0.000), RAPIDPULSE (0.000), POWERSOURCE (0.000), 4H RAT (0.000), KernelCallbackTable (0.000), Network Boundary Bridging (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Local Email Collection (25 neighbors, 25 edges)
           → File Deletion (310 neighbors, 310 edges)
[RETRIEVE-QUOTA] Query 2/7: สั่งรันคำสั่งสำรวจรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่ายเพื่อค้นหาข้อมูลสำคัญ...
[RETRIEVE] Query: สั่งรันคำสั่งสำรวจรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่ายเพื่อค้นหาข้อมูลสำคัญ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: KEYMARBLE (0.163), cmd (0.071), File and Directory Discovery (0.055), dsquery (0.022), Forfiles (0.019), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → KEYMARBLE (12 neighbors, 12 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 3/7: สร้างโฟลเดอร์ใหม่เพื่อพักข้อมูลที่รวบรวมได้...
[RETRIEVE] Query: สร้างโฟลเดอร์ใหม่เพื่อพักข้อมูลที่รวบรวมได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Carbon (0.042), Cloud Storage Creation (0.011), Local Data Staging (0.009), Data Staged (0.008), Micropsia (0.005), Create Cloud Instance (0.002), InvisiMole (0.002), Remote Data Staging (0.001), Archive via Library (0.001), Forfiles (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Carbon (19 neighbors, 19 edges)
           → Local Data Staging (138 neighbors, 138 edges)
           → Cloud Storage Creation (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 4/7: อ่านไฟล์ฐานข้อมูลสำรองออกเป็นชิ้นเล็ก ๆ เพื่อเตรียมส่งข้อมูล...
[RETRIEVE] Query: อ่านไฟล์ฐานข้อมูลสำรองออกเป็นชิ้นเล็ก ๆ เพื่อเตรียมส่งข้อมูล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Transfer Size Limits (0.016), Comnie (0.003), Forfiles (0.001), Local Data Staging (0.001), SNMP (MIB Dump) (0.001), Data Backup (0.000), SLIGHTPULSE (0.000), Catchamas (0.000), PAKLOG (0.000), Local Email Collection (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Data Transfer Size Limits (24 neighbors, 24 edges)
           → Comnie (19 neighbors, 19 edges)
           → Automated Collection (77 neighbors, 77 edges)
[RETRIEVE-QUOTA] Query 5/7: ส่งไฟล์ฐานข้อมูลสำรองที่แบ่งเป็นชิ้นไปยังบัญชีจดหมายอิเล็กทรอนิกส์ของคนร้ายผ่านบ...
[RETRIEVE] Query: ส่งไฟล์ฐานข้อมูลสำรองที่แบ่งเป็นชิ้นไปยังบัญชีจดหมายอิเล็กทรอนิกส์ของคนร้ายผ่านบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Email Forwarding Rule (0.017), Spearphishing Attachment (0.007), BusyGasper (0.007), Email Accounts (0.001), Email Accounts (0.001), StrelaStealer (0.001), Storm-1811 (0.001), Scattered Spider (0.001), Email Bombing (0.000), Email Spoofing (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Email Forwarding Rule (12 neighbors, 12 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → BusyGasper (18 neighbors, 18 edges)
           → Exfiltration Over Unencrypted Non-C2 Protocol (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 6/7: ลบไฟล์เครื่องมือทั้งหมดที่นำเข้ามาออกจากเครื่อง...
[RETRIEVE] Query: ลบไฟล์เครื่องมือทั้งหมดที่นำเข้ามาออกจากเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File Deletion (0.082), POWERSTATS (0.039), Mandrake (0.032), SDelete (0.029), Limit Hardware Installation (0.001), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → Mandrake (25 neighbors, 25 edges)
           → File Deletion (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 7/7: สั่งให้โปรแกรมฝังตัวหยุดทำงานและลบตัวเองทิ้ง...
[RETRIEVE] Query: สั่งให้โปรแกรมฝังตัวหยุดทำงานและลบตัวเองทิ้ง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HTTPTroy (0.459), Gelsemium (0.155), SDelete (0.004), Disable or Remove Feature or Program (0.004), Process Hollowing (0.003), Cardinal RAT (0.001), Cobian RAT (0.001), CrossRAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → HTTPTroy (14 neighbors, 14 edges)
           → File Deletion (310 neighbors, 310 edges)
           → Gelsemium (33 neighbors, 33 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [30/100] retrieved=623 relevant=3 latency=31484ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 16 กันยายน 2567 บริษัทนำเข้าส่งออกแห่งหนึ่งแจ้งความว่าบัญชีผู้ใช้งาน...
[RETRIEVE] Query: เมื่อวันที่ 16 กันยายน 2567 บริษัทนำเข้าส่งออกแห่งหนึ่งแจ้งความว่าบัญชีผู้ใช้งาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.010), POWRUNER (0.003), Password Managers (0.001), FIN8 (0.001), Unsecured Credentials (0.000), Reversible Encryption (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Credentials in Registry (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Keylogging (160 neighbors, 160 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
[RETRIEVE-QUOTA] Query 2/6: สวมรอยบัญชีผู้ใช้งานระบบภายในของบริษัท...
[RETRIEVE] Query: สวมรอยบัญชีผู้ใช้งานระบบภายในของบริษัท...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Internal Spearphishing (0.693), Masquerade Account Name (0.002), SystemBC (0.001), Compromise Accounts (0.001), DUSTTRAP (0.000), CrossRAT (0.000), Cobian RAT (0.000), The White Company (0.000), Visual Basic (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Internal Spearphishing (10 neighbors, 10 edges)
           → Masquerade Account Name (11 neighbors, 11 edges)
           → SystemBC (24 neighbors, 24 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] Query 3/6: อ่านคลังเก็บรหัสผ่านของ Windows ที่โปรแกรมท่องเว็บบันทึกชื่อผู้ใช้และรหัสผ่านไว้...
[RETRIEVE] Query: อ่านคลังเก็บรหัสผ่านของ Windows ที่โปรแกรมท่องเว็บบันทึกชื่อผู้ใช้และรหัสผ่านไว้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.145), Credentials in Registry (0.066), PowerSploit (0.065), Windows Credential Manager (0.019), TrickBot (0.017), cmd (0.001), Samurai (0.001), Windows Command Shell (0.000), Cobalt Group (0.000), Scheduled Task (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
           → PowerSploit (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 4/6: เขียนชื่อผู้ใช้และรหัสผ่านที่ขโมยได้ลงในไฟล์ฐานข้อมูลขนาดเล็กบนเครื่อง...
[RETRIEVE] Query: เขียนชื่อผู้ใช้และรหัสผ่านที่ขโมยได้ลงในไฟล์ฐานข้อมูลขนาดเล็กบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AuTo Stealer (0.020), Security Account Manager (0.010), APT28 (0.007), Credentials In Files (0.005), Password Managers (0.003), Unsecured Credentials (0.003), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → AuTo Stealer (11 neighbors, 11 edges)
           → Local Data Staging (138 neighbors, 138 edges)
           → Security Account Manager (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 5/6: ส่งไฟล์ฐานข้อมูลที่เก็บรหัสผ่านออกไปยังเครื่องสั่งการภายนอกผ่านช่องทาง C2...
[RETRIEVE] Query: ส่งไฟล์ฐานข้อมูลที่เก็บรหัสผ่านออกไปยังเครื่องสั่งการภายนอกผ่านช่องทาง C2...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pupy (0.648), One-Way Communication (0.445), WARPWIRE (0.442), Exfiltration Over C2 Channel (0.315), Web Service (0.078), POWRUNER (0.076), Exfiltration Over Unencrypted Non-C2 Protocol (0.042), Penquin (0.012), Javali (0.005), Hide Infrastructure (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Pupy (43 neighbors, 43 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → One-Way Communication (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 6/6: ดาวน์โหลดไฟล์ชุดคำสั่งเพิ่มเติมจากเครื่องภายนอกมาเก็บไว้บนเครื่องผู้เสียหาย...
[RETRIEVE] Query: ดาวน์โหลดไฟล์ชุดคำสั่งเพิ่มเติมจากเครื่องภายนอกมาเก็บไว้บนเครื่องผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Machete (0.377), Chaes (0.207), Ingress Tool Transfer (0.082), Data from Local System (0.004), Exfiltration Over Alternative Protocol (0.001), Visual Basic (0.001), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Machete (42 neighbors, 42 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Chaes (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [31/100] retrieved=414 relevant=3 latency=24375ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 14 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ได้รับอีเมลต้...
[RETRIEVE] Query: เมื่อวันที่ 14 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ได้รับอีเมลต้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Frankenstein (0.210), BlackTech (0.051), Covenant (0.010), Windows Command Shell (0.007), EvilGrab (0.005), cmd (0.005), XLoader (0.003), Masquerade File Type (0.002), Chaos (0.001), Command and Scripting Interpreter (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Frankenstein (28 neighbors, 28 edges)
           → Malicious File (202 neighbors, 202 edges)
           → BlackTech (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 2/7: อีเมลหลอกลวงแบบ Phishing พร้อมไฟล์เอกสาร Word ที่ฝังมาโครอันตราย...
[RETRIEVE] Query: อีเมลหลอกลวงแบบ Phishing พร้อมไฟล์เอกสาร Word ที่ฝังมาโครอันตราย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MuddyWater (0.932), Molerats (0.926), ThreatNeedle (0.852), Spearphishing Attachment (0.159), Spearphishing Link (0.121), Malicious File (0.071), Phishing (0.041), Spearphishing Attachment (0.026), Phishing for Information (0.006), Kimsuky (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → MuddyWater (89 neighbors, 89 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Molerats (22 neighbors, 22 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
[RETRIEVE-QUOTA] Query 3/7: เปลี่ยนสีตัวอักษรในเอกสารเพื่อหลอกให้ผู้ใช้กดอนุญาตให้มาโครทำงาน...
[RETRIEVE] Query: เปลี่ยนสีตัวอักษรในเอกสารเพื่อหลอกให้ผู้ใช้กดอนุญาตให้มาโครทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Patchwork (0.082), C0015 (0.043), Right-to-Left Override (0.003), Office Template Macros (0.001), Malicious Copy and Paste (0.001), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Patchwork (50 neighbors, 50 edges)
           → Malicious File (202 neighbors, 202 edges)
           → C0015 (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 4/7: ตรวจสอบรุ่นสถาปัตยกรรมระบบปฏิบัติการว่าเป็น 32-bit หรือ 64-bit (System Informati...
[RETRIEVE] Query: ตรวจสอบรุ่นสถาปัตยกรรมระบบปฏิบัติการว่าเป็น 32-bit หรือ 64-bit (System Informati...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gelsemium (0.993), FinFisher (0.986), Kerrdown (0.985), Wingbird (0.975), Client Configurations (0.150), System Information Discovery (0.124), RotaJakiro (0.082), TDTESS (0.017), UPPERCUT (0.013), Process Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Gelsemium (33 neighbors, 33 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → FinFisher (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 5/7: ประกอบบรรทัดคำสั่งและสั่งงานผ่าน Windows Command Shell...
[RETRIEVE] Query: ประกอบบรรทัดคำสั่งและสั่งงานผ่าน Windows Command Shell...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Covenant (0.584), cmd (0.328), Windows Command Shell (0.276), KEYMARBLE (0.087), cmd (0.031), PowerShell (0.031), Indirect Command Execution (0.014), Command and Scripting Interpreter (0.013), Unix Shell (0.004), Shell History (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Covenant (11 neighbors, 11 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 6/7: ดาวน์โหลดไฟล์เพิ่มเติมเข้ามาในเครื่อง (Ingress Tool Transfer)...
[RETRIEVE] Query: ดาวน์โหลดไฟล์เพิ่มเติมเข้ามาในเครื่อง (Ingress Tool Transfer)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TONESHELL (0.934), Kasidet (0.863), Ingress Tool Transfer (0.458), Industroyer (0.427), Lateral Tool Transfer (0.382), cmd (0.256), Upload Malware (0.047), ftp (0.018), Upload Tool (0.005), BITS Jobs (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → TONESHELL (44 neighbors, 44 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Kasidet (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งข้อมูลที่รวบรวมจากเครื่องผู้เสียหายออกทาง FTP ที่ไม่ได้เข้ารหัส (Exfiltration...
[RETRIEVE] Query: ส่งข้อมูลที่รวบรวมจากเครื่องผู้เสียหายออกทาง FTP ที่ไม่ได้เข้ารหัส (Exfiltration...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Unencrypted Non-C2 Protocol (0.944), ftp (0.925), FIN8 (0.901), Exfiltration Over Alternative Protocol (0.874), PUBLOAD (0.862), APT33 (0.761), Automated Exfiltration (0.575), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.483), ftp (0.383), Exfiltration Over Web Service (0.045)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → ftp (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [32/100] retrieved=333 relevant=3 latency=36229ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 30 พฤศจิกายน 2566 บริษัทผู้ให้บริการด้านเทคโนโลยีสารสนเทศแห่งหนึ่งแจ...
[RETRIEVE] Query: เมื่อวันที่ 30 พฤศจิกายน 2566 บริษัทผู้ให้บริการด้านเทคโนโลยีสารสนเทศแห่งหนึ่งแจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.436), pwdump (0.279), OS Credential Dumping (0.259), Windows Credential Editor (0.210), BlackByte (0.189), Sowbug (0.175), Suckfly (0.157), Credentials In Files (0.002), Credential Access (0.002), Credential Access Protection (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → pwdump (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 2/6: ทำ Credential Dumping ดึงรหัสผ่านจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่องท...
[RETRIEVE] Query: ทำ Credential Dumping ดึงรหัสผ่านจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่องท...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MgBot (0.768), OS Credential Dumping (0.500), pwdump (0.367), Credentials In Files (0.305), pwdump (0.290), Windows Credential Editor (0.270), Poseidon Group (0.205), Axiom (0.178), Credential Access (0.174), Credential Access Protection (0.061)
[RETRIEVE] Graph expansion: 3 subgraphs
           → MgBot (18 neighbors, 18 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 3/6: สร้างบริการของระบบบนเครื่องปลายทางเพื่อสั่งรันคำสั่งจากระยะไกล (Service Executio...
[RETRIEVE] Query: สร้างบริการของระบบบนเครื่องปลายทางเพื่อสั่งรันคำสั่งจากระยะไกล (Service Executio...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.915), xCmd (0.576), HermeticWizard (0.392), RemoteCMD (0.192), Service Execution (0.105), xCmd (0.029), Execution (0.022), LAPSUS$ (0.007), Thread Execution Hijacking (0.001), User Execution (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → xCmd (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 4/6: รวบรวมไฟล์ข้อมูลลูกค้าและบีบอัดรวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดทั่วไป (Archive ...
[RETRIEVE] Query: รวบรวมไฟล์ข้อมูลลูกค้าและบีบอัดรวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดทั่วไป (Archive ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Local Data Staging (0.338), Data Staged (0.293), Archive Collected Data (0.255), LightSpy (0.202), Remote Data Staging (0.059), FoggyWeb (0.058), Compression (0.015), Automated Collection (0.002), Collection (0.001), Response Metadata (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Local Data Staging (138 neighbors, 138 edges)
           → Data Staged (13 neighbors, 13 edges)
           → Archive Collected Data (62 neighbors, 62 edges)
[RETRIEVE-QUOTA] Query 5/6: นำไฟล์ข้อมูลลูกค้าที่บีบอัดแล้วไปพักไว้ในถังขยะของเครื่อง (Data Staged)...
[RETRIEVE] Query: นำไฟล์ข้อมูลลูกค้าที่บีบอัดแล้วไปพักไว้ในถังขยะของเครื่อง (Data Staged)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Staged (0.042), menuPass (0.014), Local Data Staging (0.011), QUIETCANARY (0.009), Kevin (0.004), Scattered Spider (0.003), Remote Data Staging (0.002), Stored Data Manipulation (0.001), Stage Capabilities (0.000), Systemd Service (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Data Staged (13 neighbors, 13 edges)
           → menuPass (71 neighbors, 71 edges)
           → Local Data Staging (138 neighbors, 138 edges)
[RETRIEVE-QUOTA] Query 6/6: ส่งไฟล์ข้อมูลลูกค้าที่บีบอัดออกไปภายนอก (Exfiltration)...
[RETRIEVE] Query: ส่งไฟล์ข้อมูลลูกค้าที่บีบอัดออกไปภายนอก (Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Physical Medium (0.245), Exfiltration (0.229), Automated Exfiltration (0.159), PUBLOAD (0.069), Exbyte (0.066), Exfiltration Over Alternative Protocol (0.066), Exbyte (0.060), Machete (0.040), Archive Collected Data (0.029), Empire (0.010)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over Physical Medium (6 neighbors, 6 edges)
           → Exfiltration (19 neighbors, 19 edges)
           → Automated Exfiltration (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [33/100] retrieved=182 relevant=4 latency=25372ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 8 ธันวาคม 2566 บริษัทที่ปรึกษาแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใ...
[RETRIEVE] Query: เมื่อวันที่ 8 ธันวาคม 2566 บริษัทที่ปรึกษาแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ShadowPad (0.006), APT-C-36 (0.002), POWRUNER (0.001), APT-C-36 (0.000), Account Discovery (0.000), Domains (0.000), Ursnif (0.000), System Network Connections Discovery (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → ShadowPad (31 neighbors, 31 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/7: ผลักไฟล์เครื่องมือของคนร้ายเข้าไปเก็บไว้บนเครื่องที่ยึดครองได้ (Ingress Tool Tra...
[RETRIEVE] Query: ผลักไฟล์เครื่องมือของคนร้ายเข้าไปเก็บไว้บนเครื่องที่ยึดครองได้ (Ingress Tool Tra...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ingress Tool Transfer (0.812), Lateral Tool Transfer (0.769), TrickBot (0.641), TONESHELL (0.368), cmd (0.302), Upload Malware (0.256), Industroyer (0.234), File Deletion (0.056), Upload Tool (0.007), Content Injection (0.004)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → TrickBot (57 neighbors, 57 edges)
[RETRIEVE-QUOTA] Query 3/7: สั่งแสดงรายการโฟลเดอร์ที่เปิดแบ่งปันบนเครือข่ายภายใน (Network Share Discovery)...
[RETRIEVE] Query: สั่งแสดงรายการโฟลเดอร์ที่เปิดแบ่งปันบนเครือข่ายภายใน (Network Share Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.691), Net (0.665), Network Share Discovery (0.391), Cuba (0.091), Network Share Access (0.031), Net (0.007), System Network Connections Discovery (0.003), System Network Configuration Discovery (0.003), Discovery (0.002), Process Discovery (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
           → Net (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 4/7: ค้นหารายชื่อเครื่องอื่นที่อยู่ในวงเครือข่ายเดียวกันด้วยคำสั่งระบบและสคริปต์ที่เข...
[RETRIEVE] Query: ค้นหารายชื่อเครื่องอื่นที่อยู่ในวงเครือข่ายเดียวกันด้วยคำสั่งระบบและสคริปต์ที่เข...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Network Configuration Discovery (0.488), Net (0.228), OSInfo (0.223), System Network Connections Discovery (0.198), cd00r (0.113), System Service Discovery (0.059), System Information Discovery (0.028), System Owner/User Discovery (0.018), ipconfig (0.012), Network Share Discovery (0.010)
[RETRIEVE] Graph expansion: 3 subgraphs
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → Net (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 5/7: ตรวจสอบพอร์ตและบริการที่เปิดอยู่บนเครื่องปลายทางแต่ละเครื่อง (Network Service Sc...
[RETRIEVE] Query: ตรวจสอบพอร์ตและบริการที่เปิดอยู่บนเครื่องปลายทางแต่ละเครื่อง (Network Service Sc...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Response Metadata (0.516), Koadic (0.483), PoshC2 (0.129), netstat (0.038), OilRig (0.020), C0018 (0.017), Active Scanning (0.004), Vulnerability Scanning (0.003), Vulnerability Scanning (0.003), Scanning IP Blocks (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Response Metadata (0 neighbors, 0 edges)
           → Koadic (31 neighbors, 31 edges)
           → Network Service Discovery (78 neighbors, 78 edges)
[RETRIEVE-QUOTA] Query 6/7: สอบถามรายการเครื่องแม่ข่ายที่ทำหน้าที่แปลงชื่อโดเมน (DNS)...
[RETRIEVE] Query: สอบถามรายการเครื่องแม่ข่ายที่ทำหน้าที่แปลงชื่อโดเมน (DNS)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DEADEYE (0.037), Active DNS (0.036), Passive DNS (0.021), DNS (0.020), Software Configuration (0.008), DNS Server (0.007), DNS (0.007), BITTER (0.005), Ke3chang (0.003), Name Resolution Poisoning and SMB Relay (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DEADEYE (13 neighbors, 13 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → Active DNS (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 7/7: แจกแจงการเชื่อมต่อเครือข่ายที่ค้างอยู่ระหว่างเครื่องในเครือข่าย (Network Connect...
[RETRIEVE] Query: แจกแจงการเชื่อมต่อเครือข่ายที่ค้างอยู่ระหว่างเครื่องในเครือข่าย (Network Connect...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Network Connections Discovery (0.375), Net (0.375), KOPILUWAK (0.236), Internet Connection Discovery (0.098), System Network Configuration Discovery (0.061), WastedLocker (0.053), FIVEHANDS (0.039), Wi-Fi Discovery (0.006), Discovery (0.004), System Owner/User Discovery (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → Net (50 neighbors, 50 edges)
           → KOPILUWAK (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [34/100] retrieved=732 relevant=5 latency=32004ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 19 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Query: เมื่อวันที่ 19 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.008), Clambling (0.002), APT-C-36 (0.001), Ursnif (0.000), Conficker (0.000), File Deletion (0.000), Hidden File System (0.000), Pre-OS Boot (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Clambling (35 neighbors, 35 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] Query 2/7: โปรแกรมฝังตัวเดิมดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดใหม่ลงบนเครื่องแม่ข่ายเก็บไฟ...
[RETRIEVE] Query: โปรแกรมฝังตัวเดิมดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดใหม่ลงบนเครื่องแม่ข่ายเก็บไฟ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Smoke Loader (0.023), Bundlore (0.014), Downgrade System Image (0.003), PUNCHBUGGY (0.002), Carbanak (0.001), cipher.exe (0.001), Executable Installer File Permissions Weakness (0.001), OLDBAIT (0.000), Patch System Image (0.000), Change Default File Association (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Smoke Loader (14 neighbors, 14 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Bundlore (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 3/7: สั่งรันตัวติดตั้งโปรแกรมฝังตัวพร้อมตัวเลือกยกระดับสิทธิ์...
[RETRIEVE] Query: สั่งรันตัวติดตั้งโปรแกรมฝังตัวพร้อมตัวเลือกยกระดับสิทธิ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Elevated Execution with Prompt (0.287), Installer Packages (0.140), OSX/Shlayer (0.108), User Account Control (0.059), Launch Daemon (0.028), Registry Run Keys / Startup Folder (0.001), Visual Basic (0.001), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Elevated Execution with Prompt (5 neighbors, 5 edges)
           → Installer Packages (8 neighbors, 8 edges)
           → OSX/Shlayer (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 4/7: ติดตั้งโปรแกรมฝังตัวระดับแกนกลางของระบบปฏิบัติการเพื่อซ่อนตัวจากรายการไฟล์และกระ...
[RETRIEVE] Query: ติดตั้งโปรแกรมฝังตัวระดับแกนกลางของระบบปฏิบัติการเพื่อซ่อนตัวจากรายการไฟล์และกระ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Rootkit (0.444), Umbreon (0.053), Hidden Files and Directories (0.047), MCMD (0.010), BackConfig (0.010), Cobian RAT (0.001), Visual Basic (0.001), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Rootkit (33 neighbors, 33 edges)
           → Hidden Files and Directories (60 neighbors, 60 edges)
           → Umbreon (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 5/7: แจกแจงรายการกระบวนการที่กำลังทำงานอยู่บนเครื่องแม่ข่ายเก็บไฟล์...
[RETRIEVE] Query: แจกแจงรายการกระบวนการที่กำลังทำงานอยู่บนเครื่องแม่ข่ายเก็บไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mafalda (0.018), Tasklist (0.015), BBSRAT (0.015), APT1 (0.008), VERMIN (0.007), Container Enumeration (0.002), Instance Enumeration (0.002), Process Discovery (0.002), Cloud Storage Enumeration (0.001), Forfiles (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Mafalda (37 neighbors, 37 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → BBSRAT (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 6/7: ตรวจสอบว่าบัญชีผู้ใช้ปัจจุบันเป็นสมาชิกกลุ่มผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์ในโดเมน...
[RETRIEVE] Query: ตรวจสอบว่าบัญชีผู้ใช้ปัจจุบันเป็นสมาชิกกลุ่มผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์ในโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cobalt Strike (0.781), WellMess (0.659), Domain Groups (0.143), Domain Account (0.017), Additional Local or Domain Groups (0.003), Nltest (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Cobalt Strike (109 neighbors, 109 edges)
           → Domain Account (65 neighbors, 65 edges)
           → WellMess (16 neighbors, 16 edges)
           → Domain Groups (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] Query 7/7: แจกแจงรายการการเชื่อมต่อเครือข่ายที่ค้างอยู่ไปยังไดรฟ์ที่เชื่อมต่อกับเครื่องแม่ข...
[RETRIEVE] Query: แจกแจงรายการการเชื่อมต่อเครือข่ายที่ค้างอยู่ไปยังไดรฟ์ที่เชื่อมต่อกับเครื่องแม่ข...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ShimRat (0.014), Network Share Discovery (0.004), WastedLocker (0.002), netstat (0.001), Clear Network Connection History and Configurations (0.001), CrackMapExec (0.001), Industroyer (0.001), System Network Connections Discovery (0.001), Network Share Access (0.000), Cloud Storage Object Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → ShimRat (22 neighbors, 22 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
           → WastedLocker (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [35/100] retrieved=662 relevant=5 latency=28536ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 22 กุมภาพันธ์ 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ถูกหลอกให้...
[RETRIEVE] Query: เมื่อวันที่ 22 กุมภาพันธ์ 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ถูกหลอกให้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Frankenstein (0.651), Malicious File (0.435), Rancor (0.176), Deobfuscate/Decode Files or Information (0.006), Adversary-in-the-Middle (0.001), Evil Twin (0.001), Outlook Forms (0.001), Magic Hound (0.000), Threat Group-3390 (0.000), ARP Cache Poisoning (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Frankenstein (28 neighbors, 28 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Rancor (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 2/5: ส่งอีเมล Spearphishing Attachment เป็นไฟล์เอกสารตารางคำนวณที่จัดทำขึ้นเจาะจงเจ้า...
[RETRIEVE] Query: ส่งอีเมล Spearphishing Attachment เป็นไฟล์เอกสารตารางคำนวณที่จัดทำขึ้นเจาะจงเจ้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BITTER (0.860), admin@338 (0.719), Spearphishing Attachment (0.542), Spearphishing Attachment (0.211), Spearphishing Link (0.062), RTM (0.046), CURIUM (0.041), Spearphishing Link (0.014), Spearphishing Service (0.013), Internal Spearphishing (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BITTER (18 neighbors, 18 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → admin@338 (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 3/5: หลอกให้ผู้เสียหายเปิดไฟล์เอกสารอันตรายและกดอนุญาตให้ชุดคำสั่งมาโครทำงาน (User Ex...
[RETRIEVE] Query: หลอกให้ผู้เสียหายเปิดไฟล์เอกสารอันตรายและกดอนุญาตให้ชุดคำสั่งมาโครทำงาน (User Ex...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Malicious File (0.904), User Execution (0.862), C0015 (0.639), Rancor (0.612), Malicious Copy and Paste (0.055), User Account Control (0.039), Exploitation for Client Execution (0.021), Indirect Command Execution (0.012), LAPSUS$ (0.010), Execution (0.010)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Malicious File (202 neighbors, 202 edges)
           → User Execution (18 neighbors, 18 edges)
           → C0015 (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 4/5: สั่งให้ชุดคำสั่งมาโครเริ่มทำงานบนเครื่องผ่านไฟล์ตารางคำนวณ...
[RETRIEVE] Query: สั่งให้ชุดคำสั่งมาโครเริ่มทำงานบนเครื่องผ่านไฟล์ตารางคำนวณ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CALENDAR (0.002), MMC (0.001), KernelCallbackTable (0.001), MCMD (0.000), Forfiles (0.000), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), Cobian RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → CALENDAR (3 neighbors, 3 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → MMC (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 5/5: วางไฟล์สคริปต์ไว้ในโฟลเดอร์เริ่มต้นระบบของบัญชีผู้ใช้เพื่อให้ทำงานซ้ำเมื่อผู้ใช้...
[RETRIEVE] Query: วางไฟล์สคริปต์ไว้ในโฟลเดอร์เริ่มต้นระบบของบัญชีผู้ใช้เพื่อให้ทำงานซ้ำเมื่อผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Login Items (0.491), Startup Items (0.471), Registry Run Keys / Startup Folder (0.260), Restrict File and Directory Permissions (0.127), Okrum (0.099), Confucius (0.064), Re-opened Applications (0.035), Active Setup (0.004), Keychain (0.000), Rundll32 (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Login Items (8 neighbors, 8 edges)
           → Startup Items (7 neighbors, 7 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
[RETRIEVE-QUOTA] 14 vectors (quota 3/query), 8 subgraphs from 5 queries
  [36/100] retrieved=292 relevant=3 latency=30497ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 27 มิถุนายน 2567 บริษัทโลจิสติกส์ข้ามชาติสาขาประเทศไทยแจ้งความว่าเคร...
[RETRIEVE] Query: เมื่อวันที่ 27 มิถุนายน 2567 บริษัทโลจิสติกส์ข้ามชาติสาขาประเทศไทยแจ้งความว่าเคร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: admin@338 (0.001), admin@338 (0.001), Ingress Tool Transfer (0.000), FIN8 (0.000), Exploitation of Remote Services (0.000), Data Encrypted for Impact (0.000), Pikabot (0.000), Exfiltration to Text Storage Sites (0.000), Setuid and Setgid (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → admin@338 (19 neighbors, 19 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] Query 2/9: เชื่อมต่อ RDP จากเครื่องภายนอกเข้าสู่เครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: เชื่อมต่อ RDP จากเครื่องภายนอกเข้าสู่เครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.012), RDP Hijacking (0.007), Terminal Services DLL (0.006), Remote Desktop Protocol (0.006), Axiom (0.003), Remote Service Session Hijacking (0.003), Network Segmentation (0.003), Limit Access to Resource Over Network (0.003), Application Layer Protocol (0.001), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/9: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่มายังเครื่องแม่ข่ายควบคุมโดเมน (Ingress Tool Transfer...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่มายังเครื่องแม่ข่ายควบคุมโดเมน (Ingress Tool Transfer...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: down_new (0.644), Ingress Tool Transfer (0.493), TYPEFRAME (0.463), cmd (0.305), Industroyer (0.263), Lateral Tool Transfer (0.211), Upload Malware (0.073), Upload Tool (0.009), BITS Jobs (0.001), Impacket (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → down_new (11 neighbors, 11 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → TYPEFRAME (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/9: สั่งให้ไฟล์โปรแกรมที่ดาวน์โหลดมาทำงานผ่านการเชื่อมต่อ RDP...
[RETRIEVE] Query: สั่งให้ไฟล์โปรแกรมที่ดาวน์โหลดมาทำงานผ่านการเชื่อมต่อ RDP...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pupy (0.045), Terminal Services DLL (0.031), RDP Hijacking (0.011), ServHelper (0.011), Remote Service Session Hijacking (0.008), Chimera (0.007), Axiom (0.006), Remote Desktop Protocol (0.006), Application Layer Protocol (0.002), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Pupy (43 neighbors, 43 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 5/9: สร้างงานตั้งเวลาเพื่อรีสตาร์ตเครื่อง...
[RETRIEVE] Query: สร้างงานตั้งเวลาเพื่อรีสตาร์ตเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NotPetya (0.785), SVCReady (0.500), AsyncRAT (0.496), Disco (0.076), Boot or Logon Autostart Execution (0.011), schtasks (0.010), at (0.009), Cron (0.007), Systemd Timers (0.004), System Shutdown/Reboot (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → NotPetya (15 neighbors, 15 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → SVCReady (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 6/9: เข้ารหัสลับไฟล์ทั้งหมดในโฟลเดอร์ผู้ใช้...
[RETRIEVE] Query: เข้ารหัสลับไฟล์ทั้งหมดในโฟลเดอร์ผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cipher.exe (0.221), Dok (0.071), WannaCry (0.039), Encrypted/Encoded File (0.039), Kobalos (0.027), Hidden Files and Directories (0.022), /etc/passwd and /etc/shadow (0.012), APT32 (0.007), Reversible Encryption (0.003), Group Policy Preferences (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → cipher.exe (3 neighbors, 3 edges)
           → Dok (11 neighbors, 11 edges)
           → Sudo and Sudo Caching (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 7/9: วางไฟล์ข้อความเรียกค่าไถ่ไว้ที่ไดรฟ์หลัก...
[RETRIEVE] Query: วางไฟล์ข้อความเรียกค่าไถ่ไว้ที่ไดรฟ์หลัก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CHIMNEYSWEEP (0.007), FIN5 (0.001), KernelCallbackTable (0.001), Overwrite Process Arguments (0.000), Visual Basic (0.000), Dynamic-link Library Injection (0.000), Terminal Services DLL (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → CHIMNEYSWEEP (32 neighbors, 32 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → FIN5 (17 neighbors, 17 edges)
           → Local Data Staging (138 neighbors, 138 edges)
[RETRIEVE-QUOTA] Query 8/9: คัดลอกโปรแกรมไปทำงานต่อบนเครื่องอื่นในเครือข่าย...
[RETRIEVE] Query: คัดลอกโปรแกรมไปทำงานต่อบนเครื่องอื่นในเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.373), PsExec (0.279), Havoc (0.143), Lateral Tool Transfer (0.073), SMB/Windows Admin Shares (0.007), CrossRAT (0.006), Visual Basic (0.003), Cobian RAT (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → PsExec (49 neighbors, 49 edges)
[RETRIEVE-QUOTA] Query 9/9: ปิดการเชื่อมต่อ RDP ที่เปิดค้างไว้กับเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: ปิดการเชื่อมต่อ RDP ที่เปิดค้างไว้กับเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Disable or Remove Feature or Program (0.226), Network Segmentation (0.076), RDP Hijacking (0.003), Remote Service Session Hijacking (0.002), Terminal Services DLL (0.002), Limit Access to Resource Over Network (0.002), Remote Desktop Protocol (0.001), Chimera (0.001), Axiom (0.001), Clear Network Connection History and Configurations (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Network Segmentation (37 neighbors, 37 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [37/100] retrieved=716 relevant=3 latency=42458ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 18 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ระ...
[RETRIEVE] Query: เมื่อวันที่ 18 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ระ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Create or Modify System Process (0.644), APT3 (0.458), Pallas (0.433), PUNCHTRACK (0.219), Deobfuscate/Decode Files or Information (0.147), VERMIN (0.099), Hide Artifacts (0.041), Obfuscated Files or Information (0.021), Encrypted/Encoded File (0.018), Hidden Files and Directories (0.011)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → APT3 (50 neighbors, 50 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] Query 2/8: ดาวน์โหลดแอปพลิเคชันซื้อขายจากเว็บไซต์ปลอมเพื่อติดตั้งโปรแกรมไม่พึงประสงค์...
[RETRIEVE] Query: ดาวน์โหลดแอปพลิเคชันซื้อขายจากเว็บไซต์ปลอมเพื่อติดตั้งโปรแกรมไม่พึงประสงค์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RatMilad (0.040), CoinTicker (0.040), CSPY Downloader (0.030), GuLoader (0.005), 4H RAT (0.001), Cobian RAT (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RatMilad (18 neighbors, 18 edges)
           → Download New Code at Runtime (42 neighbors, 42 edges)
           → CoinTicker (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 3/8: ชุดคำสั่งหลังการติดตั้งเรียกโปรแกรมของคนร้ายให้ทำงานเบื้องหลังทันที...
[RETRIEVE] Query: ชุดคำสั่งหลังการติดตั้งเรียกโปรแกรมของคนร้ายให้ทำงานเบื้องหลังทันที...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Installer Packages (0.076), BACKSPACE (0.069), Create or Modify System Process (0.015), Megazord (0.010), BackConfig (0.008), Launch Daemon (0.007), BUBBLEWRAP (0.003), Active Setup (0.001), Proxysvc (0.001), Print Processors (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Installer Packages (8 neighbors, 8 edges)
           → BACKSPACE (15 neighbors, 15 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 4/8: Create or Modify System Process: Launch Daemon เพื่อให้โปรแกรมทำงานเป็นกระบวนการ...
[RETRIEVE] Query: Create or Modify System Process: Launch Daemon เพื่อให้โปรแกรมทำงานเป็นกระบวนการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LITTLELAMB.WOOLTEA (0.942), Create or Modify System Process (0.907), Launch Daemon (0.886), Systemd Service (0.400), IMAPLoader (0.236), System Services (0.153), REPTILE (0.133), Service Modification (0.022), Service Creation (0.014), Process Modification (0.007)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → Launch Daemon (18 neighbors, 18 edges)
           → LITTLELAMB.WOOLTEA (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 5/8: ตั้งชื่อไฟล์ให้ขึ้นต้นด้วยจุดเพื่อซ่อนไฟล์จากหน้าต่างจัดการไฟล์และรายการไฟล์ปกติ...
[RETRIEVE] Query: ตั้งชื่อไฟล์ให้ขึ้นต้นด้วยจุดเพื่อซ่อนไฟล์จากหน้าต่างจัดการไฟล์และรายการไฟล์ปกติ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Hide Artifacts (0.596), Hidden Files and Directories (0.380), Space after Filename (0.171), RedCurl (0.169), Antivirus/Antimalware (0.116), Attor (0.100), Hidden File System (0.072), File/Path Exclusions (0.071), Restrict File and Directory Permissions (0.032), Hidden Users (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Hide Artifacts (26 neighbors, 26 edges)
           → Hidden Files and Directories (60 neighbors, 60 edges)
           → Space after Filename (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/8: ดาวน์โหลดไฟล์โปรแกรมที่ถูกเข้ารหัสลับและอำพรางไว้ (Obfuscated Files or Informati...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมที่ถูกเข้ารหัสลับและอำพรางไว้ (Obfuscated Files or Informati...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CoinTicker (0.986), PUBLOAD (0.935), APT3 (0.884), Obfuscated Files or Information (0.882), MOPSLED (0.830), Encrypted/Encoded File (0.718), Deobfuscate/Decode Files or Information (0.705), Compression (0.168), Malicious File (0.085), Artificial Intelligence (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → CoinTicker (9 neighbors, 9 edges)
           → PUBLOAD (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 7/8: วางโปรแกรมควบคุมระยะไกลลงบนเครื่อง...
[RETRIEVE] Query: วางโปรแกรมควบคุมระยะไกลลงบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: xCmd (0.181), RemoteCMD (0.175), Execution Prevention (0.047), PsExec (0.038), CrackMapExec (0.021), Cobian RAT (0.020), CrossRAT (0.003), Visual Basic (0.002), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → xCmd (2 neighbors, 2 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → Execution Prevention (79 neighbors, 79 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 8/8: ติดตั้งโปรแกรมควบคุมระยะไกลให้ทำงานเป็นบริการของระบบเพื่อคงการเข้าถึง...
[RETRIEVE] Query: ติดตั้งโปรแกรมควบคุมระยะไกลให้ทำงานเป็นบริการของระบบเพื่อคงการเข้าถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Execution Prevention (0.131), Execution Prevention (0.111), Terminal Services DLL (0.022), Remote Access Tools (0.012), Windows Remote Management (0.006), Cobian RAT (0.003), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Execution Prevention (79 neighbors, 79 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
           → Remote Desktop Software (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [38/100] retrieved=293 relevant=3 latency=31125ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 21 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Query: เมื่อวันที่ 21 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Credential Editor (0.276), Axiom (0.202), HOMEFRY (0.154), OS Credential Dumping (0.116), Suckfly (0.055), gsecdump (0.020), Password Cracking (0.007), Credential Access (0.006), Credential Access Protection (0.001), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Windows Credential Editor (8 neighbors, 8 edges)
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 2/9: ยึดครองเครื่องแม่ข่ายควบคุมโดเมนขององค์กร...
[RETRIEVE] Query: ยึดครองเครื่องแม่ข่ายควบคุมโดเมนขององค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DCSync (0.002), Domain or Tenant Policy Modification (0.001), Domain Accounts (0.001), Net (0.001), CrossRAT (0.000), Net (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000), Visual Basic (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DCSync (14 neighbors, 14 edges)
           → Domain or Tenant Policy Modification (8 neighbors, 8 edges)
           → Domain Accounts (47 neighbors, 47 edges)
[RETRIEVE-QUOTA] Query 3/9: โปรแกรมฝังตัวดาวน์โหลดเครื่องมือทำ Credential Dumping ลงบนเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Query: โปรแกรมฝังตัวดาวน์โหลดเครื่องมือทำ Credential Dumping ลงบนเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HOMEFRY (0.846), Windows Credential Editor (0.569), pwdump (0.549), MimiPenguin (0.528), MgBot (0.510), Poseidon Group (0.190), Axiom (0.100), OS Credential Dumping (0.043), Credentials In Files (0.012), Credential Access Protection (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → HOMEFRY (4 neighbors, 4 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → MgBot (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 4/9: เรียกใช้เครื่องมือ Credential Dumping เพื่อดึงค่าความลับบัญชีผู้ใช้ออกจากฐานข้อม...
[RETRIEVE] Query: เรียกใช้เครื่องมือ Credential Dumping เพื่อดึงค่าความลับบัญชีผู้ใช้ออกจากฐานข้อม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: pwdump (0.816), IceApple (0.799), OS Credential Dumping (0.617), Poseidon Group (0.420), pwdump (0.393), Windows Credential Editor (0.359), Credential Access (0.340), Axiom (0.305), Credentials In Files (0.183), Credential Access Protection (0.051)
[RETRIEVE] Graph expansion: 3 subgraphs
           → pwdump (7 neighbors, 7 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → IceApple (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 5/9: โปรแกรมฝังตัวดาวน์โหลดเครื่องมือสำหรับสั่งงานเครื่องระยะไกล...
[RETRIEVE] Query: โปรแกรมฝังตัวดาวน์โหลดเครื่องมือสำหรับสั่งงานเครื่องระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.275), MCMD (0.223), RemoteUtilities (0.213), xCmd (0.173), RemoteUtilities (0.085), cmd (0.076), cmd (0.041), RemoteUtilities (0.029), Remote Access Tools (0.017), dsquery (0.015)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → RemoteUtilities (5 neighbors, 5 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 6/9: โปรแกรมฝังตัวดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวสำเนาที่สามและเก็บไว้บนเครื่องแม่ข่...
[RETRIEVE] Query: โปรแกรมฝังตัวดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวสำเนาที่สามและเก็บไว้บนเครื่องแม่ข่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: USBferry (0.037), BadPatch (0.005), PUNCHBUGGY (0.004), APT3 (0.003), Compromise Host Software Binary (0.001), Keydnap (0.001), cipher.exe (0.001), Archive via Utility (0.000), Password Managers (0.000), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → USBferry (12 neighbors, 12 edges)
           → Replication Through Removable Media (35 neighbors, 35 edges)
           → BadPatch (12 neighbors, 12 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 7/9: นำค่าแฮชรหัสผ่านที่ขโมยได้ไปยืนยันตัวตนกับเครื่องปลายทางโดยไม่ใช้รหัสผ่านจริง (P...
[RETRIEVE] Query: นำค่าแฮชรหัสผ่านที่ขโมยได้ไปยืนยันตัวตนกับเครื่องปลายทางโดยไม่ใช้รหัสผ่านจริง (P...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pass the Hash (0.979), Pass-The-Hash Toolkit (0.928), GALLIUM (0.521), Pass-The-Hash Toolkit (0.497), Chimera (0.383), HOPLIGHT (0.170), Pass the Ticket (0.139), Password Cracking (0.055), menuPass (0.000), Privileged Account Management (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Pass the Hash (29 neighbors, 29 edges)
           → Pass-The-Hash Toolkit (2 neighbors, 2 edges)
           → GALLIUM (47 neighbors, 47 edges)
[RETRIEVE-QUOTA] Query 8/9: คัดลอกตัวติดตั้งโปรแกรมฝังตัวไปยังเครื่องคอมพิวเตอร์ของพนักงาน (ลateral movement...
[RETRIEVE] Query: คัดลอกตัวติดตั้งโปรแกรมฝังตัวไปยังเครื่องคอมพิวเตอร์ของพนักงาน (ลateral movement...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Replication Through Removable Media (0.347), Lateral Tool Transfer (0.184), Lateral Movement (0.066), hcdLoader (0.051), cmd (0.029), Net (0.024), APT18 (0.008), FluBot (0.001), Volt Typhoon (0.001), Stealth (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Replication Through Removable Media (35 neighbors, 35 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Lateral Movement (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 9/9: สั่งให้โปรแกรมฝังตัวทำงานบนเครื่องคอมพิวเตอร์ของพนักงานผ่านเครื่องมือสั่งงานเครื...
[RETRIEVE] Query: สั่งให้โปรแกรมฝังตัวทำงานบนเครื่องคอมพิวเตอร์ของพนักงานผ่านเครื่องมือสั่งงานเครื...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.068), xCmd (0.020), RemoteCMD (0.017), HermeticWizard (0.017), Scheduled Task/Job (0.016), CrossRAT (0.000), Portable Executable Injection (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Scheduled Task/Job (18 neighbors, 18 edges)
           → Scheduled Task (201 neighbors, 201 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [39/100] retrieved=132 relevant=3 latency=36024ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 19 กุมภาพันธ์ 2564 ผู้เสียหายอีกรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Query: เมื่อวันที่ 19 กุมภาพันธ์ 2564 ผู้เสียหายอีกรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: JHUHUGIT (0.828), ccf32 (0.641), Solar (0.407), CURIUM (0.300), Exfiltration Over C2 Channel (0.085), Scheduled Transfer (0.079), Automated Exfiltration (0.047), Scheduled Task/Job (0.026), Scheduled Task (0.005), Exfiltration Over Unencrypted Non-C2 Protocol (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → JHUHUGIT (21 neighbors, 21 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → ccf32 (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 2/7: สร้าง Scheduled Task/Job: Scheduled Task ให้ทำงานด้วยสิทธิ์ระดับระบบทุกครั้งที่ผ...
[RETRIEVE] Query: สร้าง Scheduled Task/Job: Scheduled Task ให้ทำงานด้วยสิทธิ์ระดับระบบทุกครั้งที่ผ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: JHUHUGIT (0.880), Operating System Configuration (0.660), User Account Management (0.401), Scheduled Task/Job (0.250), At (0.029), Scheduled Task (0.012), Logon Script (Windows) (0.011), Network Logon Script (0.005), Scheduled Job Modification (0.003), Masquerade Task or Service (0.002)
[RETRIEVE] Graph expansion: 4 subgraphs
           → JHUHUGIT (21 neighbors, 21 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → Scheduled Task/Job (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 3/7: เรียกใช้ไฟล์ที่อ้างว่าเป็นตัวรายงานข้อผิดพลาดโดยอัตโนมัติเมื่อผู้ใช้ล็อกอิน...
[RETRIEVE] Query: เรียกใช้ไฟล์ที่อ้างว่าเป็นตัวรายงานข้อผิดพลาดโดยอัตโนมัติเมื่อผู้ใช้ล็อกอิน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Re-opened Applications (0.336), XDG Autostart Entries (0.060), Logon Script (Windows) (0.038), xCaon (0.024), Authentication Package (0.018), DarkComet (0.001), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Re-opened Applications (7 neighbors, 7 edges)
           → XDG Autostart Entries (15 neighbors, 15 edges)
           → Logon Script (Windows) (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 4/7: รวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่ล็อกอินอยู่ (System Owner/User Discove...
[RETRIEVE] Query: รวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่ล็อกอินอยู่ (System Owner/User Discove...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sys10 (0.968), System Owner/User Discovery (0.966), T9000 (0.945), Kimsuky (0.823), APT3 (0.073), System Information Discovery (0.051), System Service Discovery (0.050), System Location Discovery (0.037), System Network Connections Discovery (0.019), Device Driver Discovery (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Sys10 (7 neighbors, 7 edges)
           → T9000 (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 5/7: รวบรวมข้อมูลประจำเครื่องของผู้เสียหาย (System Information Discovery)...
[RETRIEVE] Query: รวบรวมข้อมูลประจำเครื่องของผู้เสียหาย (System Information Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SLOTHFULMEDIA (0.892), Industroyer (0.768), System Information Discovery (0.355), System Location Discovery (0.191), Systeminfo (0.167), OSInfo (0.160), System Owner/User Discovery (0.112), System Service Discovery (0.081), Device Driver Discovery (0.060), SYSCON (0.054)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SLOTHFULMEDIA (24 neighbors, 24 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Industroyer (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 6/7: เข้ารหัสข้อมูลด้วยกุญแจที่ฝังไว้ในโปรแกรมก่อนส่งออก...
[RETRIEVE] Query: เข้ารหัสข้อมูลด้วยกุญแจที่ฝังไว้ในโปรแกรมก่อนส่งออก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: GolfSpy (0.363), KONNI (0.230), Fooder (0.051), OwaAuth (0.027), Credential API Hooking (0.006), KEYPLUG (0.004), Software Packing (0.002), Extra Window Memory Injection (0.002), Process Injection (0.001), Deobfuscate/Decode Files or Information (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → GolfSpy (18 neighbors, 18 edges)
           → Archive Collected Data (15 neighbors, 15 edges)
           → KONNI (40 neighbors, 40 edges)
           → Standard Encoding (129 neighbors, 129 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งข้อมูลที่เข้ารหัสไปยังเว็บไซต์สั่งการผ่านช่องทางเดิม (Exfiltration Over C2 Ch...
[RETRIEVE] Query: ส่งข้อมูลที่เข้ารหัสไปยังเว็บไซต์สั่งการผ่านช่องทางเดิม (Exfiltration Over C2 Ch...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over C2 Channel (0.975), Okrum (0.808), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.759), Industroyer (0.732), APT39 (0.682), Fakecalls (0.665), Scheduled Transfer (0.635), Exfiltration Over Unencrypted Non-C2 Protocol (0.603), Automated Exfiltration (0.542), Exfiltration Over Alternative Protocol (0.491)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Exfiltration Over Symmetric Encrypted Non-C2 Protocol (6 neighbors, 6 edges)
           → Okrum (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [40/100] retrieved=266 relevant=3 latency=32583ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 11 ตุลาคม 2567 บริษัทวิศวกรรมแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใน...
[RETRIEVE] Query: เมื่อวันที่ 11 ตุลาคม 2567 บริษัทวิศวกรรมแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lucifer (0.031), Operation Honeybee (0.005), FIN8 (0.001), File Deletion (0.000), Deobfuscate/Decode Files or Information (0.000), Windows Management Instrumentation (0.000), Browser Extensions (0.000), Video Capture (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Lucifer (24 neighbors, 24 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Operation Honeybee (33 neighbors, 33 edges)
           → File Deletion (310 neighbors, 310 edges)
[RETRIEVE-QUOTA] Query 2/6: ใช้เครื่องแม่ข่ายภายในเป็นทางผ่านเชื่อมต่อจากภายนอก (Proxy)...
[RETRIEVE] Query: ใช้เครื่องแม่ข่ายภายในเป็นทางผ่านเชื่อมต่อจากภายนอก (Proxy)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Internal Proxy (0.769), StarProxy (0.594), External Proxy (0.201), Network Segmentation (0.117), Proxy (0.079), reGeorg (0.017), StarProxy (0.012), Proxysvc (0.006), Multi-hop Proxy (0.006), StarProxy (0.004)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Internal Proxy (39 neighbors, 39 edges)
           → StarProxy (10 neighbors, 10 edges)
           → External Proxy (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] Query 3/6: ลบไฟล์โปรแกรมและไฟล์ผลลัพธ์ที่วางไว้เพื่อเก็บกวาดร่องรอย (File and Directory Dis...
[RETRIEVE] Query: ลบไฟล์โปรแกรมและไฟล์ผลลัพธ์ที่วางไว้เพื่อเก็บกวาดร่องรอย (File and Directory Dis...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chameleon (0.394), Indicator Removal (0.268), Indicator Removal from Tools (0.114), File and Directory Discovery (0.073), File Deletion (0.069), BPFDoor (0.041), Disable or Remove Feature or Program (0.021), Cloud Storage Object Discovery (0.020), Log Enumeration (0.003), Windows Registry Key Deletion (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chameleon (26 neighbors, 26 edges)
           → Indicator Removal on Host (10 neighbors, 10 edges)
           → Indicator Removal (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] Query 4/6: ดาวน์โหลดโปรแกรมเชื่อมต่อระยะไกลขนาดเล็กมาเก็บไว้บนเครื่อง (Ingress Tool Transfe...
[RETRIEVE] Query: ดาวน์โหลดโปรแกรมเชื่อมต่อระยะไกลขนาดเล็กมาเก็บไว้บนเครื่อง (Ingress Tool Transfe...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteUtilities (0.561), Industroyer (0.406), cmd (0.326), Ingress Tool Transfer (0.124), Upload Malware (0.028), Lateral Tool Transfer (0.025), NavRAT (0.020), ftp (0.006), Upload Tool (0.001), BITS Jobs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteUtilities (5 neighbors, 5 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Industroyer (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 5/6: สั่งโปรแกรมเชื่อมต่อระยะไกลให้ทำงานเพื่อเปิดทางเข้าใช้งานหน้าจอระยะไกล...
[RETRIEVE] Query: สั่งโปรแกรมเชื่อมต่อระยะไกลให้ทำงานเพื่อเปิดทางเข้าใช้งานหน้าจอระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Koadic (0.112), RemoteCMD (0.059), Operating System Configuration (0.014), Remote Access Tools (0.011), Cobian RAT (0.008), Windows Remote Management (0.004), CrossRAT (0.001), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Koadic (31 neighbors, 31 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RemoteCMD (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/6: ห่อหุ้มการเชื่อมต่อหน้าจอระยะไกลไว้ภายในช่องทางเชื่อมต่ออีกชั้นหนึ่งเพื่อหลบเลี่...
[RETRIEVE] Query: ห่อหุ้มการเชื่อมต่อหน้าจอระยะไกลไว้ภายในช่องทางเชื่อมต่ออีกชั้นหนึ่งเพื่อหลบเลี่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Protocol Tunneling (0.859), Leviathan (0.095), Duqu (0.059), FLIPSIDE (0.030), Cobalt Strike (0.019), Application Layer Protocol (0.017), IDE Tunneling (0.013), DNS (0.006), Ping (0.000), Tonto Team (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Protocol Tunneling (46 neighbors, 46 edges)
           → Leviathan (68 neighbors, 68 edges)
           → Duqu (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [41/100] retrieved=574 relevant=3 latency=21188ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 29 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Query: เมื่อวันที่ 29 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dragonfly (0.021), APT-C-36 (0.011), APT-C-36 (0.005), BADHATCH (0.001), Domain Accounts (0.000), Ursnif (0.000), Domains (0.000), Internal Spearphishing (0.000), Domain Account (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Dragonfly (66 neighbors, 66 edges)
           → Domain Account (65 neighbors, 65 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/7: ใช้รหัสผ่านผู้ดูแลโดเมนที่ได้มาก่อนหน้าเพื่อเข้าถึงเครื่องแม่ข่ายควบคุมโดเมนจากร...
[RETRIEVE] Query: ใช้รหัสผ่านผู้ดูแลโดเมนที่ได้มาก่อนหน้าเพื่อเข้าถึงเครื่องแม่ข่ายควบคุมโดเมนจากร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VOID MANTICORE (0.676), Valid Accounts (0.228), Remote Services (0.072), Windows Remote Management (0.048), Account Discovery (0.008), Domain Account (0.008), Valak (0.001), Account Manipulation (0.001), Modify Authentication Process (0.001), Valak (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Domain Accounts (47 neighbors, 47 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] Query 3/7: แก้ไขงานตั้งเวลาที่มีอยู่เดิมบนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล (Scheduled Ta...
[RETRIEVE] Query: แก้ไขงานตั้งเวลาที่มีอยู่เดิมบนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล (Scheduled Ta...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Scheduled Task/Job (0.297), Operating System Configuration (0.291), Empire (0.218), Scheduled Job Modification (0.210), Operating System Configuration (0.074), PowerSploit (0.071), At (0.017), Container Orchestration Job (0.006), Scheduled Task (0.005), Tasklist (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Scheduled Task/Job (18 neighbors, 18 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → Empire (91 neighbors, 91 edges)
           → Group Policy Modification (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 4/7: สั่งให้งานตั้งเวลาที่แก้ไขแล้วเริ่มทำงานทันที...
[RETRIEVE] Query: สั่งให้งานตั้งเวลาที่แก้ไขแล้วเริ่มทำงานทันที...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: schtasks (0.004), yty (0.004), at (0.003), at (0.003), Visual Basic (0.000), 4H RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Cobian RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → yty (15 neighbors, 15 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → schtasks (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 5/7: ติดตั้งโปรแกรมฝังตัวใหม่บนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: ติดตั้งโปรแกรมฝังตัวใหม่บนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RegDuke (0.050), Mimikatz (0.006), Regsvr32 (0.004), PipeMon (0.004), AppDomainManager (0.003), Pandora (0.003), Domain Controller Authentication (0.003), Rogue Domain Controller (0.002), TYPEFRAME (0.001), Additional Local or Domain Groups (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RegDuke (11 neighbors, 11 edges)
           → Mimikatz (77 neighbors, 77 edges)
           → Rogue Domain Controller (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 6/7: แจกแจงรายชื่อสมาชิกของกลุ่มสิทธิ์ในโดเมนหลายกลุ่มเพื่อค้นหาบัญชีผู้มีสิทธิ์สูง (...
[RETRIEVE] Query: แจกแจงรายชื่อสมาชิกของกลุ่มสิทธิ์ในโดเมนหลายกลุ่มเพื่อค้นหาบัญชีผู้มีสิทธิ์สูง (...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Permission Groups Discovery (0.896), Domain Groups (0.684), Ke3chang (0.433), TrickBot (0.217), APT41 (0.179), MURKYTOP (0.126), Domain Account (0.100), Group Policy Discovery (0.086), System Owner/User Discovery (0.012), Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Permission Groups Discovery (18 neighbors, 18 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → Ke3chang (58 neighbors, 58 edges)
[RETRIEVE-QUOTA] Query 7/7: แจกแจงรายชื่อเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนอยู่ในระบบทะเบียนโดเมนขององค์ก...
[RETRIEVE] Query: แจกแจงรายชื่อเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนอยู่ในระบบทะเบียนโดเมนขององค์ก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Network Configuration Discovery (0.125), OSInfo (0.113), nbtstat (0.067), ifconfig (0.031), dsquery (0.013), System Network Connections Discovery (0.009), Nltest (0.002), System Owner/User Discovery (0.002), ipconfig (0.000), Data from Configuration Repository (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → OSInfo (11 neighbors, 11 edges)
           → nbtstat (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [42/100] retrieved=265 relevant=3 latency=33752ms
[RETRIEVE-QUOTA] Query 1/10: เมื่อวันที่ 15 พฤศจิกายน 2566 มหาวิทยาลัยแห่งหนึ่งแจ้งความว่าระบบสารสนเทศของมหาว...
[RETRIEVE] Query: เมื่อวันที่ 15 พฤศจิกายน 2566 มหาวิทยาลัยแห่งหนึ่งแจ้งความว่าระบบสารสนเทศของมหาว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ZxShell (0.006), zwShell (0.001), LAPSUS$ (0.000), RDP Hijacking (0.000), POWERSOURCE (0.000), Remote Desktop Protocol (0.000), Duqu (0.000), Valid Accounts (0.000), PowerShell (0.000), Modify Authentication Process (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → ZxShell (37 neighbors, 37 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → zwShell (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 2/10: ส่งอีเมลหลอกลวง Phishing ถึงบุคลากรเพื่อให้หลงเชื่อ...
[RETRIEVE] Query: ส่งอีเมลหลอกลวง Phishing ถึงบุคลากรเพื่อให้หลงเชื่อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Phishing (0.162), Spearphishing Attachment (0.109), AADInternals (0.093), Spearphishing Attachment (0.055), Spearphishing Link (0.034), Spearphishing Service (0.031), Phishing for Information (0.024), Email Accounts (0.011), Kimsuky (0.001), Email Bombing (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Phishing (23 neighbors, 23 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → AADInternals (26 neighbors, 26 edges)
           → Spearphishing Link (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 3/10: โจมตีช่องโหว่ร้ายแรงของโพรโทคอลยืนยันตัวตนระหว่างเครื่องลูกข่ายกับเครื่องแม่ข่าย...
[RETRIEVE] Query: โจมตีช่องโหว่ร้ายแรงของโพรโทคอลยืนยันตัวตนระหว่างเครื่องลูกข่ายกับเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain Controller Authentication (0.119), Volt Typhoon (0.017), POWERSOURCE (0.005), Volt Typhoon (0.005), DCSync (0.002), Domains (0.002), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Domain Controller Authentication (12 neighbors, 12 edges)
           → Volt Typhoon (100 neighbors, 100 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
[RETRIEVE-QUOTA] Query 4/10: ยกระดับสิทธิ์เป็นผู้ดูแลระบบของโดเมน...
[RETRIEVE] Query: ยกระดับสิทธิ์เป็นผู้ดูแลระบบของโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain or Tenant Policy Modification (0.017), Operating System Configuration (0.008), User Account Management (0.005), Domain Account (0.002), Additional Local or Domain Groups (0.001), Cardinal RAT (0.000), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Domain or Tenant Policy Modification (8 neighbors, 8 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → Create Account (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 5/10: ใช้ชื่อผู้ใช้และรหัสผ่านที่ยังใช้งานได้ยืนยันตัวตนเข้าสู่จุดเชื่อมต่อ VPN ของมหา...
[RETRIEVE] Query: ใช้ชื่อผู้ใช้และรหัสผ่านที่ยังใช้งานได้ยืนยันตัวตนเข้าสู่จุดเชื่อมต่อ VPN ของมหา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operation Wocao (0.003), Valid Accounts (0.002), Web Portal Capture (0.002), FIN5 (0.001), External Remote Services (0.001), C0032 (0.000), PITSTOP (0.000), XTunnel (0.000), VPNFilter (0.000), Cutting Edge (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Operation Wocao (79 neighbors, 79 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Web Portal Capture (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 6/10: เปิดช่องทาง VPN ค้างไว้เพื่อคงการเข้าถึงเครือข่าย...
[RETRIEVE] Query: เปิดช่องทาง VPN ค้างไว้เพื่อคงการเข้าถึงเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: C0032 (0.077), Web Portal Capture (0.012), External Remote Services (0.009), PITSTOP (0.004), Persistence (0.003), XTunnel (0.001), Filter Network Traffic (0.001), Cutting Edge (0.001), VPNFilter (0.000), APT-C-36 (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → C0032 (19 neighbors, 19 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → Web Portal Capture (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 7/10: เปิดการเชื่อมต่อ Remote Desktop Protocol (RDP) ไปยังเครื่องอื่นเพื่อขยายการเข้าถ...
[RETRIEVE] Query: เปิดการเชื่อมต่อ Remote Desktop Protocol (RDP) ไปยังเครื่องอื่นเพื่อขยายการเข้าถ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Limit Access to Resource Over Network (0.360), Network Segmentation (0.116), Terminal Services DLL (0.111), Remote Desktop Protocol (0.089), RDP Hijacking (0.084), SILENTTRINITY (0.067), Remote Access Tools (0.059), Carbanak (0.048), Remote Desktop Software (0.012), Remote Services (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Accessibility Features (15 neighbors, 15 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 8/10: สั่งงานบนระบบด้วย PowerShell...
[RETRIEVE] Query: สั่งงานบนระบบด้วย PowerShell...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerShell (0.664), PowerExchange (0.387), ConnectWise (0.329), POWRUNER (0.247), Disable or Remove Feature or Program (0.150), POWERSTATS (0.132), PowerSploit (0.056), PowerShell Profile (0.038), POWERSTATS (0.024), POWERSOURCE (0.021)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PowerShell (241 neighbors, 241 edges)
           → PowerExchange (6 neighbors, 6 edges)
           → ConnectWise (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 9/10: ใช้เครื่องมือที่ติดมากับระบบปฏิบัติการเพื่อดำเนินการโจมตี...
[RETRIEVE] Query: ใช้เครื่องมือที่ติดมากับระบบปฏิบัติการเพื่อดำเนินการโจมตี...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BOOTRASH (0.089), Shamoon (0.039), System Services (0.028), PHASEJAM (0.026), Shared Modules (0.015), Ingress Tool Transfer (0.014), NETEAGLE (0.013), Credential API Hooking (0.012), OopsIE (0.012), Input Injection (0.010)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BOOTRASH (2 neighbors, 2 edges)
           → Shamoon (24 neighbors, 24 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 10/10: เข้ารหัสข้อมูลนักศึกษาของมหาวิทยาลัยเพื่อทำให้ไม่สามารถใช้งานได้...
[RETRIEVE] Query: เข้ารหัสข้อมูลนักศึกษาของมหาวิทยาลัยเพื่อทำให้ไม่สามารถใช้งานได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Encrypted for Impact (0.009), Data Encoding (0.001), SLOTHFULMEDIA (0.001), Credential Access Protection (0.000), HexEval Loader (0.000), DEADWOOD (0.000), Forced Authentication (0.000), Network Device Authentication (0.000), AADInternals (0.000), Sakula (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → Data Encoding (13 neighbors, 13 edges)
           → Credential Access Protection (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 10 queries
  [43/100] retrieved=287 relevant=5 latency=38882ms
[RETRIEVE-QUOTA] Query 1/4: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความว่าข้อมูลลูกค้าถูกนำออ...
[RETRIEVE] Query: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความว่าข้อมูลลูกค้าถูกนำออ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.204), INC Ransom (0.127), Pay2Key (0.014), Data Encrypted for Impact (0.013), Ursnif (0.004), Exfiltration (0.003), APT-C-36 (0.000), Internal Spearphishing (0.000), Social Engineering (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → INC Ransom (33 neighbors, 33 edges)
           → Financial Theft (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] Query 2/4: ลำเลียงข้อมูลออกจากเครือข่ายผู้เสียหายด้วยโปรแกรมรับส่งไฟล์ไปยังบัญชีปลายทางที่ค...
[RETRIEVE] Query: ลำเลียงข้อมูลออกจากเครือข่ายผู้เสียหายด้วยโปรแกรมรับส่งไฟล์ไปยังบัญชีปลายทางที่ค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ingress Tool Transfer (0.076), Exfiltration (0.048), Koadic (0.030), Drovorub (0.021), Execution (0.009), Cobian RAT (0.003), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Exfiltration (19 neighbors, 19 edges)
           → Koadic (31 neighbors, 31 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 3/4: เข้ารหัสไฟล์ในระบบแบบผสมระหว่างการเข้ารหัสสมมาตรและกุญแจสาธารณะ โดยเข้ารหัสเพียง...
[RETRIEVE] Query: เข้ารหัสไฟล์ในระบบแบบผสมระหว่างการเข้ารหัสสมมาตรและกุญแจสาธารณะ โดยเข้ารหัสเพียง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Asymmetric Cryptography (0.211), BitPaymer (0.090), Encrypted/Encoded File (0.059), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.029), InvisiMole (0.011), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.010), Patchwork (0.009), PHPsert (0.005), Standard Encoding (0.005), Data Encoding (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Asymmetric Cryptography (100 neighbors, 100 edges)
           → BitPaymer (19 neighbors, 19 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] Query 4/4: ข่มขู่เปิดเผยข้อมูลลูกค้าที่ขโมยออกไปต่อสาธารณะหากไม่ยอมจ่ายเงิน (double extorti...
[RETRIEVE] Query: ข่มขู่เปิดเผยข้อมูลลูกค้าที่ขโมยออกไปต่อสาธารณะหากไม่ยอมจ่ายเงิน (double extorti...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Embargo (0.715), Akira (0.189), Embargo (0.171), Medusa Ransomware (0.135), Black Basta (0.135), Salesforce Data Exfiltration (0.010), Financial Theft (0.008), Impersonation (0.001), Akira (0.000), Compromise Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Embargo (23 neighbors, 23 edges)
           → Akira (25 neighbors, 25 edges)
           → Financial Theft (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] 12 vectors (quota 3/query), 8 subgraphs from 4 queries
  [44/100] retrieved=687 relevant=3 latency=25434ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 1 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าแม้จะล้างเครื่องและติดตั้...
[RETRIEVE] Query: เมื่อวันที่ 1 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าแม้จะล้างเครื่องและติดตั้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Create or Modify System Process (0.011), MoonWind (0.005), BackConfig (0.002), Active Setup (0.001), ZxShell (0.000), APT28 (0.000), Event Triggered Execution (0.000), Network Denial of Service (0.000), Lazarus Group (0.000), Password Policies (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → MoonWind (15 neighbors, 15 edges)
           → Windows Service (150 neighbors, 150 edges)
[RETRIEVE-QUOTA] Query 2/5: กำหนดสคริปต์ให้ระบบเรียกโปรแกรมคนร้ายอัตโนมัติเมื่อผู้ใช้ล็อกอินเข้าสู่ระบบ...
[RETRIEVE] Query: กำหนดสคริปต์ให้ระบบเรียกโปรแกรมคนร้ายอัตโนมัติเมื่อผู้ใช้ล็อกอินเข้าสู่ระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Logon Script (Windows) (0.587), Boot or Logon Autostart Execution (0.239), KGH_SPY (0.135), Re-opened Applications (0.061), Active Setup (0.029), DarkComet (0.009), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Logon Script (Windows) (12 neighbors, 12 edges)
           → Boot or Logon Autostart Execution (24 neighbors, 24 edges)
           → KGH_SPY (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 3/5: ลงทะเบียน WMI event subscription ให้เรียกคำสั่งคนร้ายตามเงื่อนไขเวลาที่กำหนดโดยไ...
[RETRIEVE] Query: ลงทะเบียน WMI event subscription ให้เรียกคำสั่งคนร้ายตามเงื่อนไขเวลาที่กำหนดโดยไ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Management Instrumentation Event Subscription (0.127), Sardonic (0.062), BADHATCH (0.037), APT29 (0.030), HOPLIGHT (0.023), Windows Management Instrumentation (0.006), At (0.001), WMI Creation (0.001), Event Triggered Execution (0.000), Extra Window Memory Injection (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Windows Management Instrumentation Event Subscription (33 neighbors, 33 edges)
           → Sardonic (26 neighbors, 26 edges)
           → BADHATCH (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 4/5: เพิ่มรายการเรียกใช้งานโปรแกรมคนร้ายใน Registry Run Keys...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานโปรแกรมคนร้ายใน Registry Run Keys...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: EvilGrab (0.452), Registry Run Keys / Startup Folder (0.358), Hancitor (0.309), LockBit 2.0 (0.114), MCMD (0.062), Active Setup (0.015), Services Registry Permissions Weakness (0.007), Modify Registry (0.006), Windows Registry Key Modification (0.001), Windows Registry Key Access (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → EvilGrab (6 neighbors, 6 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → Hancitor (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 5/5: เพิ่มโปรแกรมคนร้ายไว้ใน Startup Folder เพื่อให้ทำงานทุกครั้งที่เปิดเครื่อง...
[RETRIEVE] Query: เพิ่มโปรแกรมคนร้ายไว้ใน Startup Folder เพื่อให้ทำงานทุกครั้งที่เปิดเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DarkComet (0.848), MarkiRAT (0.749), Registry Run Keys / Startup Folder (0.713), APT33 (0.388), InvisiMole (0.187), Startup Items (0.012), Create or Modify System Process (0.011), Launch Agent (0.007), Re-opened Applications (0.002), Python Startup Hooks (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → DarkComet (21 neighbors, 21 edges)
           → MarkiRAT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] 14 vectors (quota 3/query), 8 subgraphs from 5 queries
  [45/100] retrieved=231 relevant=3 latency=21891ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 23 มิถุนายน 2565 บริษัทเทคโนโลยีแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายขอ...
[RETRIEVE] Query: เมื่อวันที่ 23 มิถุนายน 2565 บริษัทเทคโนโลยีแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QUADAGENT (0.135), Confucius (0.108), BackConfig (0.010), Scheduled Task/Job (0.006), schtasks (0.004), Seth-Locker (0.003), schtasks (0.002), Scheduled Task (0.002), Scheduled Transfer (0.000), Masquerade Task or Service (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → QUADAGENT (18 neighbors, 18 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Confucius (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 2/8: ไฟล์โปรแกรมของคนร้ายถูกเรียกทำงานครั้งแรกบนเครื่องแม่ข่าย...
[RETRIEVE] Query: ไฟล์โปรแกรมของคนร้ายถูกเรียกทำงานครั้งแรกบนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NETWIRE (0.013), Chaes (0.010), EvilGrab (0.005), Netwalker (0.002), Path Interception by PATH Environment Variable (0.002), Cobian RAT (0.000), Cardinal RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → NETWIRE (49 neighbors, 49 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Chaes (28 neighbors, 28 edges)
           → Msiexec (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 3/8: สร้าง Scheduled Task ชื่อเลียนแบบงานปรับปรุงเซสชันของวินโดวส์เพื่อคงอยู่ในระบบ...
[RETRIEVE] Query: สร้าง Scheduled Task ชื่อเลียนแบบงานปรับปรุงเซสชันของวินโดวส์เพื่อคงอยู่ในระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AsyncRAT (0.502), Masquerade Task or Service (0.230), Confucius (0.143), schtasks (0.060), Scheduled Task/Job (0.030), schtasks (0.024), at (0.012), Scheduled Task (0.007), Scheduled Job Modification (0.002), Scheduled Job Metadata (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → AsyncRAT (23 neighbors, 23 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Masquerade Task or Service (94 neighbors, 94 edges)
[RETRIEVE-QUOTA] Query 4/8: กำหนด Scheduled Task ให้เรียกโปรแกรมของคนร้ายทำงานซ้ำทุกหนึ่งชั่วโมง...
[RETRIEVE] Query: กำหนด Scheduled Task ให้เรียกโปรแกรมของคนร้ายทำงานซ้ำทุกหนึ่งชั่วโมง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OopsIE (0.335), CLAIMLOADER (0.266), At (0.256), Scheduled Task/Job (0.139), Scheduled Task (0.048), schtasks (0.022), Confucius (0.006), schtasks (0.005), KernelCallbackTable (0.001), Masquerade Task or Service (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OopsIE (20 neighbors, 20 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → At (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 5/8: โปรแกรมควบคุมระยะไกลทำหน้าที่เป็นจุดพักส่งต่อการเชื่อมต่อจากคนร้ายภายนอก...
[RETRIEVE] Query: โปรแกรมควบคุมระยะไกลทำหน้าที่เป็นจุดพักส่งต่อการเชื่อมต่อจากคนร้ายภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cobian RAT (0.010), HTRAN (0.006), Remote Access Tools (0.005), Execution Prevention (0.004), Execution (0.003), Execution Prevention (0.002), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Cobian RAT (8 neighbors, 8 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
           → HTRAN (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 6/8: ใช้เครื่องแม่ข่ายเป็น Proxy เพื่อกระโดดเข้าไปยังเครื่องอื่นในเครือข่ายภายใน...
[RETRIEVE] Query: ใช้เครื่องแม่ข่ายเป็น Proxy เพื่อกระโดดเข้าไปยังเครื่องอื่นในเครือข่ายภายใน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MiniDuke (0.169), Internal Proxy (0.141), StarProxy (0.104), Multi-hop Proxy (0.022), Proxy (0.021), reGeorg (0.020), External Proxy (0.013), FRP (0.004), FRP (0.004), Network Boundary Bridging (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Internal Proxy (39 neighbors, 39 edges)
           → MiniDuke (11 neighbors, 11 edges)
           → StarProxy (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 7/8: เจาะลึกและเคลื่อนที่ต่อไปยังเครื่องอื่นในเครือข่ายภายใน...
[RETRIEVE] Query: เจาะลึกและเคลื่อนที่ต่อไปยังเครื่องอื่นในเครือข่ายภายใน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lateral Movement (0.205), Remote System Discovery (0.102), Internal Proxy (0.027), Network Share Discovery (0.019), Ping (0.005), CrossRAT (0.001), Deep Panda (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Lateral Movement (23 neighbors, 23 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
           → Internal Proxy (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 8/8: เข้ารหัสการติดต่อขาเข้าและขาออกของโปรแกรมด้วยกุญแจลับขนาด 128 บิต (Encrypted Cha...
[RETRIEVE] Query: เข้ารหัสการติดต่อขาเข้าและขาออกของโปรแกรมด้วยกุญแจลับขนาด 128 บิต (Encrypted Cha...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Encrypted Channel (0.360), NETWIRE (0.075), PowerLess (0.045), PowGoop (0.042), Chaes (0.037), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.004), Encrypted/Encoded File (0.004), Out-of-Band Communications Channel (0.002), Exfiltration Over C2 Channel (0.002), Data Encrypted for Impact (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Encrypted Channel (23 neighbors, 23 edges)
           → NETWIRE (49 neighbors, 49 edges)
           → PowerLess (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [46/100] retrieved=401 relevant=3 latency=31065ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 9 กรกฎาคม 2567 บริษัทปิโตรเคมีแห่งหนึ่งในจังหวัดระยองแจ้งความว่าเครื...
[RETRIEVE] Query: เมื่อวันที่ 9 กรกฎาคม 2567 บริษัทปิโตรเคมีแห่งหนึ่งในจังหวัดระยองแจ้งความว่าเครื...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Carbon (0.001), POWRUNER (0.000), FIN8 (0.000), Password Policy Discovery (0.000), Account Discovery (0.000), Exfiltration to Text Storage Sites (0.000), CrossRAT (0.000), Pikabot (0.000), Query Registry (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Carbon (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 2/8: เรียกดูชื่อเครื่องคอมพิวเตอร์ของผู้เสียหาย (System Name Discovery)...
[RETRIEVE] Query: เรียกดูชื่อเครื่องคอมพิวเตอร์ของผู้เสียหาย (System Name Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WINDSHIELD (0.887), EVILNUM (0.863), OSInfo (0.336), DnsSystem (0.059), System Owner/User Discovery (0.042), System Location Discovery (0.032), System Information Discovery (0.031), Device Driver Discovery (0.017), System Service Discovery (0.017), Systeminfo (0.013)
[RETRIEVE] Graph expansion: 3 subgraphs
           → WINDSHIELD (6 neighbors, 6 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → EVILNUM (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 3/8: เรียกดูชื่อบัญชีผู้ใช้ที่กำลังใช้งานอยู่ (System Owner/User Discovery)...
[RETRIEVE] Query: เรียกดูชื่อบัญชีผู้ใช้ที่กำลังใช้งานอยู่ (System Owner/User Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Owner/User Discovery (0.912), PowerDuke (0.842), T9000 (0.658), Kimsuky (0.636), Account Discovery (0.099), APT3 (0.098), Local Account (0.010), System Information Discovery (0.005), System Location Discovery (0.002), Device Driver Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → PowerDuke (16 neighbors, 16 edges)
           → T9000 (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 4/8: เรียกดูชื่อเครื่องเป้าหมายอีกเครื่องเพื่อยืนยันระบบที่เข้าถึง (System Name Disco...
[RETRIEVE] Query: เรียกดูชื่อเครื่องเป้าหมายอีกเครื่องเพื่อยืนยันระบบที่เข้าถึง (System Name Disco...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackConfig (0.169), Remote System Discovery (0.117), Rising Sun (0.103), System Network Connections Discovery (0.088), System Information Discovery (0.048), System Location Discovery (0.044), System Owner/User Discovery (0.025), Systeminfo (0.017), DnsSystem (0.016), Process Discovery (0.004)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BackConfig (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
[RETRIEVE-QUOTA] Query 5/8: เรียกดูการตั้งค่าเครือข่าย ได้แก่ หมายเลขไอพี เกตเวย์ และเครื่องแม่ข่าย DNS (Sys...
[RETRIEVE] Query: เรียกดูการตั้งค่าเครือข่าย ได้แก่ หมายเลขไอพี เกตเวย์ และเครื่องแม่ข่าย DNS (Sys...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ifconfig (0.898), ipconfig (0.892), System Network Configuration Discovery (0.805), ipconfig (0.626), CrackMapExec (0.605), DEADEYE (0.450), System Network Connections Discovery (0.060), Network Device Configuration Dump (0.046), DnsSystem (0.018), System Owner/User Discovery (0.004)
[RETRIEVE] Graph expansion: 3 subgraphs
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → ifconfig (1 neighbors, 1 edges)
           → ipconfig (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 6/8: ใช้คำสั่งพื้นฐานผ่านหน้าต่างคำสั่งเพื่อแจกแจงบัญชีผู้ใช้ทั้งหมดในโดเมน (Domain T...
[RETRIEVE] Query: ใช้คำสั่งพื้นฐานผ่านหน้าต่างคำสั่งเพื่อแจกแจงบัญชีผู้ใช้ทั้งหมดในโดเมน (Domain T...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: C0015 (0.791), Nltest (0.613), Domain Account (0.346), dsquery (0.239), Domain Trust Discovery (0.156), Audit (0.032), Account Discovery (0.019), System Owner/User Discovery (0.008), Network Trust Dependencies (0.001), Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → C0015 (39 neighbors, 39 edges)
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → Nltest (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 7/8: แจกแจงกลุ่มสิทธิ์ในโดเมนและสมาชิกของกลุ่มผู้ดูแลโดเมนกับกลุ่มผู้ดูแลระบบจดหมายอิ...
[RETRIEVE] Query: แจกแจงกลุ่มสิทธิ์ในโดเมนและสมาชิกของกลุ่มผู้ดูแลโดเมนกับกลุ่มผู้ดูแลระบบจดหมายอิ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Permission Groups Discovery (0.468), Ke3chang (0.403), Domain Groups (0.282), Group Policy Discovery (0.119), TrickBot (0.079), MURKYTOP (0.054), BADHATCH (0.012), Additional Email Delegate Permissions (0.009), Domain Account (0.004), Discovery (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Permission Groups Discovery (18 neighbors, 18 edges)
           → Ke3chang (58 neighbors, 58 edges)
           → Domain Groups (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] Query 8/8: เรียกดูนโยบายรหัสผ่านของโดเมน ได้แก่ ความยาวขั้นต่ำและจำนวนครั้งที่อนุญาตให้ล็อก...
[RETRIEVE] Query: เรียกดูนโยบายรหัสผ่านของโดเมน ได้แก่ ความยาวขั้นต่ำและจำนวนครั้งที่อนุญาตให้ล็อก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PoshC2 (0.387), Password Policy Discovery (0.233), Account Discovery (0.041), Wi-Fi Discovery (0.008), Domain Trust Discovery (0.008), System Owner/User Discovery (0.007), Account Use Policies (0.003), down_new (0.000), Discovery (0.000), OSInfo (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PoshC2 (35 neighbors, 35 edges)
           → Password Policy Discovery (11 neighbors, 11 edges)
           → Account Discovery (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [47/100] retrieved=612 relevant=6 latency=34090ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 20 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความว่าเจ้า...
[RETRIEVE] Query: เมื่อวันที่ 20 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความว่าเจ้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA2541 (0.017), POWERSTATS (0.014), POWERSOURCE (0.007), POWERSTATS (0.007), POWRUNER (0.003), POWERSOURCE (0.002), PowerShell (0.001), PowerShell Profile (0.000), Disable or Remove Feature or Program (0.000), ZxShell (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → TA2541 (37 neighbors, 37 edges)
           → PowerShell (241 neighbors, 241 edges)
           → POWERSTATS (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 2/6: อีเมลพร้อมไฟล์แนบที่ใช้การแทรกอักขระพิเศษให้แสดงนามสกุลไฟล์กลับด้านเพื่อหลอกว่าเ...
[RETRIEVE] Query: อีเมลพร้อมไฟล์แนบที่ใช้การแทรกอักขระพิเศษให้แสดงนามสกุลไฟล์กลับด้านเพื่อหลอกว่าเ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mofang (0.482), XLoader (0.309), Masquerade File Type (0.055), Spearphishing Attachment (0.019), Double File Extension (0.014), Dok (0.011), CrossRAT (0.000), Visual Basic (0.000), The White Company (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Mofang (8 neighbors, 8 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → XLoader (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 3/6: ไฟล์โปรแกรมที่รันได้ถูกเปิดเพื่อยึดครองเครื่อง...
[RETRIEVE] Query: ไฟล์โปรแกรมที่รันได้ถูกเปิดเพื่อยึดครองเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WastedLocker (0.023), Firmware Corruption (0.003), PsExec (0.002), Diskpart (0.001), ccf32 (0.001), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → WastedLocker (21 neighbors, 21 edges)
           → Windows Permissions (16 neighbors, 16 edges)
           → Firmware Corruption (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/6: เรียกใช้ PowerShell ต่อจากหน้าต่างคำสั่งของระบบ...
[RETRIEVE] Query: เรียกใช้ PowerShell ต่อจากหน้าต่างคำสั่งของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerShell (0.175), POWRUNER (0.127), PowerExchange (0.102), POWERSTATS (0.010), PowerShower (0.008), POWERSOURCE (0.005), PowerSploit (0.004), PowerShell Profile (0.004), POWERSTATS (0.002), Invoke-PSImage (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PowerShell (241 neighbors, 241 edges)
           → PowerExchange (6 neighbors, 6 edges)
           → POWRUNER (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 5/6: ใช้หน้าต่างคำสั่งสั่งสคริปต์ค้นหาและรวบรวมไฟล์ตามนามสกุลที่กำหนดในเครื่อง...
[RETRIEVE] Query: ใช้หน้าต่างคำสั่งสั่งสคริปต์ค้นหาและรวบรวมไฟล์ตามนามสกุลที่กำหนดในเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Forfiles (0.055), cmd (0.041), TAINTEDSCRIBE (0.031), cmd (0.017), File and Directory Discovery (0.013), dsquery (0.007), DropBook (0.003), Pupy (0.002), Path Interception by Search Order Hijacking (0.002), Proc Filesystem (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Forfiles (4 neighbors, 4 edges)
           → cmd (13 neighbors, 13 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
[RETRIEVE-QUOTA] Query 6/6: บีบอัดไฟล์ที่รวบรวมได้รวมเป็นไฟล์เดียวเพื่อเตรียมนำออก...
[RETRIEVE] Query: บีบอัดไฟล์ที่รวบรวมได้รวมเป็นไฟล์เดียวเพื่อเตรียมนำออก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Compression (0.100), BloodHound (0.043), Archive Collected Data (0.012), Remote Data Staging (0.010), APT1 (0.007), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Compression (38 neighbors, 38 edges)
           → BloodHound (18 neighbors, 18 edges)
           → Archive Collected Data (62 neighbors, 62 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [48/100] retrieved=395 relevant=3 latency=34941ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 6 มิถุนายน 2567 บริษัทมหาชนแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของ...
[RETRIEVE] Query: เมื่อวันที่ 6 มิถุนายน 2567 บริษัทมหาชนแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Net Crawler (0.000), WannaCry (0.000), FIN8 (0.000), Darkhotel (0.000), EvilGrab (0.000), Lokibot (0.000), Password Policy Discovery (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → WannaCry (17 neighbors, 17 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Net Crawler (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 2/9: เพิ่มรายการเรียกใช้งานสคริปต์ในทะเบียนระบบของบัญชีผู้บริหารเพื่อให้ทำงานทุกครั้ง...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานสคริปต์ในทะเบียนระบบของบัญชีผู้บริหารเพื่อให้ทำงานทุกครั้ง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.900), DarkComet (0.388), Logon Script (Windows) (0.312), LockBit 2.0 (0.293), RunningRAT (0.128), Operation Dream Job (0.075), Boot or Logon Autostart Execution (0.014), Boot or Logon Initialization Scripts (0.006), Startup Items (0.001), ClickOnce (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → DarkComet (21 neighbors, 21 edges)
           → Logon Script (Windows) (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/9: อัปโหลดโปรแกรมดักบันทึกแป้นพิมพ์ขึ้นเครื่อง...
[RETRIEVE] Query: อัปโหลดโปรแกรมดักบันทึกแป้นพิมพ์ขึ้นเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AsyncRAT (0.085), BOULDSPY (0.044), PAKLOG (0.025), Duqu (0.024), gsecdump (0.008), Fgdump (0.007), DropBook (0.004), Cherry Picker (0.002), PsExec (0.002), PUNCHTRACK (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → AsyncRAT (23 neighbors, 23 edges)
           → Keylogging (160 neighbors, 160 edges)
           → BOULDSPY (25 neighbors, 25 edges)
           → Keylogging (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 4/9: สั่งให้โปรแกรมดักบันทึกแป้นพิมพ์ทำงานภายใต้สิทธิ์ของผู้บริหาร (Input Capture: Ke...
[RETRIEVE] Query: สั่งให้โปรแกรมดักบันทึกแป้นพิมพ์ทำงานภายใต้สิทธิ์ของผู้บริหาร (Input Capture: Ke...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: S.O.V.A. (0.171), Clambling (0.045), Keylogging (0.025), Empire (0.023), Fysbis (0.022), Input Capture (0.013), Credential API Hooking (0.006), Wevtutil (0.005), Web Portal Capture (0.002), Access Token Manipulation (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → S.O.V.A. (19 neighbors, 19 edges)
           → Keylogging (25 neighbors, 25 edges)
           → Clambling (35 neighbors, 35 edges)
           → Keylogging (160 neighbors, 160 edges)
[RETRIEVE-QUOTA] Query 5/9: เปิดอ่านไฟล์ผลลัพธ์การบันทึกแป้นพิมพ์...
[RETRIEVE] Query: เปิดอ่านไฟล์ผลลัพธ์การบันทึกแป้นพิมพ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MacMa (0.009), Forfiles (0.002), Clipboard Data (0.001), Wevtutil (0.001), njRAT (0.001), TAINTEDSCRIBE (0.001), Shell History (0.001), TAINTEDSCRIBE (0.000), Windows Registry Key Access (0.000), Cachedump (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → MacMa (28 neighbors, 28 edges)
           → Keylogging (160 neighbors, 160 edges)
           → Forfiles (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/9: อัปโหลดโปรแกรมดึงชื่อผู้ใช้และรหัสผ่านที่เว็บเบราว์เซอร์บันทึกไว้ขึ้นเครื่อง...
[RETRIEVE] Query: อัปโหลดโปรแกรมดึงชื่อผู้ใช้และรหัสผ่านที่เว็บเบราว์เซอร์บันทึกไว้ขึ้นเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TrickBot (0.390), Credentials from Web Browsers (0.356), Prikormka (0.264), Password Managers (0.004), Cobian RAT (0.003), Windows Credential Manager (0.002), Visual Basic (0.001), CrossRAT (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → TrickBot (57 neighbors, 57 edges)
           → Prikormka (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 7/9: สั่งให้โปรแกรมดึงข้อมูลรหัสผ่านที่เว็บเบราว์เซอร์บันทึกไว้ทำงาน (Credentials fro...
[RETRIEVE] Query: สั่งให้โปรแกรมดึงข้อมูลรหัสผ่านที่เว็บเบราว์เซอร์บันทึกไว้ทำงาน (Credentials fro...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TrickBot (0.871), PLEAD (0.868), Credentials from Web Browsers (0.771), RedCurl (0.770), LaZagne (0.636), Windows Credential Manager (0.041), Password Managers (0.035), Forge Web Credentials (0.015), Web Credential Usage (0.011), Browser Information Discovery (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → TrickBot (57 neighbors, 57 edges)
           → PLEAD (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 8/9: สั่งหยุดโปรแกรมดักบันทึกแป้นพิมพ์...
[RETRIEVE] Query: สั่งหยุดโปรแกรมดักบันทึกแป้นพิมพ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OwaAuth (0.004), LazyWiper (0.001), Cardinal RAT (0.000), Ignore Process Interrupts (0.000), Prevent Command History Logging (0.000), CrossRAT (0.000), Visual Basic (0.000), Execution Prevention (0.000), Limit Software Installation (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → OwaAuth (8 neighbors, 8 edges)
           → Timestomp (60 neighbors, 60 edges)
           → LazyWiper (9 neighbors, 9 edges)
           → Disable or Modify Tools (142 neighbors, 142 edges)
[RETRIEVE-QUOTA] Query 9/9: ลบโปรแกรมและไฟล์ที่เกี่ยวข้องในโฟลเดอร์ไฟล์ชั่วคราวเพื่อทำลายร่องรอย (File and D...
[RETRIEVE] Query: ลบโปรแกรมและไฟล์ที่เกี่ยวข้องในโฟลเดอร์ไฟล์ชั่วคราวเพื่อทำลายร่องรอย (File and D...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File and Directory Discovery (0.112), KillDisk (0.103), SILENTTRINITY (0.028), Disable or Remove Feature or Program (0.015), File Deletion (0.011), Cloud Storage Object Discovery (0.011), BBSRAT (0.011), Data Destruction (0.002), System Information Discovery (0.001), System Owner/User Discovery (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → File and Directory Discovery (371 neighbors, 371 edges)
           → KillDisk (18 neighbors, 18 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [49/100] retrieved=416 relevant=4 latency=49338ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 2 มิถุนายน 2566 บริษัทแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Query: เมื่อวันที่ 2 มิถุนายน 2566 บริษัทแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Duqu (0.040), APT-C-36 (0.038), Pasam (0.025), Ursnif (0.021), APT-C-36 (0.007), POSHSPY (0.003), Internal Spearphishing (0.000), Lateral Tool Transfer (0.000), System Script Proxy Execution (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Duqu (21 neighbors, 21 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/9: โปรแกรมไม่พึงประสงค์แพร่กระจายจากเครื่องหนึ่งไปยังเครื่องอื่นในองค์กร...
[RETRIEVE] Query: โปรแกรมไม่พึงประสงค์แพร่กระจายจากเครื่องหนึ่งไปยังเครื่องอื่นในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NotPetya (0.051), Ramsay (0.031), Agent.btz (0.018), Taint Shared Content (0.011), PsExec (0.005), Cobian RAT (0.001), CrossRAT (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → NotPetya (15 neighbors, 15 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Ramsay (39 neighbors, 39 edges)
           → Taint Shared Content (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 3/9: โปรแกรมประตูหลังเปิดทางให้คนร้ายส่งคำสั่งเข้ามาสั่งงานบนเครื่องที่ยึดครองได้...
[RETRIEVE] Query: โปรแกรมประตูหลังเปิดทางให้คนร้ายส่งคำสั่งเข้ามาสั่งงานบนเครื่องที่ยึดครองได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RGDoor (0.070), BACKSPACE (0.042), Cobian RAT (0.029), Input Injection (0.002), Cardinal RAT (0.001), Ingress Tool Transfer (0.001), CrossRAT (0.001), KernelCallbackTable (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RGDoor (8 neighbors, 8 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → BACKSPACE (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 4/9: โปรแกรมควบคุมระยะไกลเก็บรวบรวมข้อมูลของเครื่อง...
[RETRIEVE] Query: โปรแกรมควบคุมระยะไกลเก็บรวบรวมข้อมูลของเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Reg (0.127), ifconfig (0.039), Cobian RAT (0.018), Systeminfo (0.015), ViperRAT (0.010), CrossRAT (0.009), Audio Capture (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Reg (12 neighbors, 12 edges)
           → Query Registry (121 neighbors, 121 edges)
           → ifconfig (1 neighbors, 1 edges)
[RETRIEVE-QUOTA] Query 5/9: โปรแกรมควบคุมระยะไกลติดต่อกลับไปยังเครื่องสั่งการของคนร้าย (Command and Control)...
[RETRIEVE] Query: โปรแกรมควบคุมระยะไกลติดต่อกลับไปยังเครื่องสั่งการของคนร้าย (Command and Control)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BISCUIT (0.328), MCMD (0.275), Command and Control (0.223), RemoteCMD (0.214), BACKSPACE (0.011), Execution (0.007), Anubis (0.002), Bypass User Account Control (0.001), WolfRAT (0.001), User Account Control (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BISCUIT (11 neighbors, 11 edges)
           → Fallback Channels (58 neighbors, 58 edges)
           → Command and Control (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] Query 6/9: ดาวน์โหลดส่วนประกอบเพิ่มเติมของโปรแกรมอันตรายจากเครื่องสั่งการเข้ามาติดตั้ง (Ing...
[RETRIEVE] Query: ดาวน์โหลดส่วนประกอบเพิ่มเติมของโปรแกรมอันตรายจากเครื่องสั่งการเข้ามาติดตั้ง (Ing...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chaes (0.839), Machete (0.749), Upload Malware (0.488), Ingress Tool Transfer (0.487), Industroyer (0.313), Lateral Tool Transfer (0.175), cmd (0.092), Upload Tool (0.009), Software Extensions (0.003), PsExec (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chaes (28 neighbors, 28 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Machete (42 neighbors, 42 edges)
[RETRIEVE-QUOTA] Query 7/9: โปรแกรมประตูหลังแพร่กระจายตัวเองโดยอาศัยช่องโหว่ของเครื่องอื่น (Exploitation of ...
[RETRIEVE] Query: โปรแกรมประตูหลังแพร่กระจายตัวเองโดยอาศัยช่องโหว่ของเครื่องอื่น (Exploitation of ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploitation of Remote Services (0.158), Exploitation for Privilege Escalation (0.139), Ramsay (0.068), Exploitation for Client Execution (0.041), APT32 (0.017), Vulnerabilities (0.008), Leviathan (0.005), Vulnerability Scanning (0.003), Vulnerability Scanning (0.002), Vulnerability Scanning (0.002)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Exploitation of Remote Services (34 neighbors, 34 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → Ramsay (39 neighbors, 39 edges)
           → Replication Through Removable Media (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 8/9: คัดลอกสำเนาโปรแกรมประตูหลังไปยังสื่อบันทึกแบบถอดได้ (Replication Through Removab...
[RETRIEVE] Query: คัดลอกสำเนาโปรแกรมประตูหลังไปยังสื่อบันทึกแบบถอดได้ (Replication Through Removab...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Replication Through Removable Media (0.750), Crimson (0.666), njRAT (0.522), USBferry (0.361), Disable or Remove Feature or Program (0.128), Communication Through Removable Media (0.095), DropBook (0.055), Hardware Additions (0.035), Data from Removable Media (0.016), Traffic Duplication (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Replication Through Removable Media (35 neighbors, 35 edges)
           → Crimson (32 neighbors, 32 edges)
           → njRAT (40 neighbors, 40 edges)
[RETRIEVE-QUOTA] Query 9/9: คัดลอกสำเนาโปรแกรมประตูหลังไปยังโฟลเดอร์ที่เปิดแบ่งปันบนเครือข่าย...
[RETRIEVE] Query: คัดลอกสำเนาโปรแกรมประตูหลังไปยังโฟลเดอร์ที่เปิดแบ่งปันบนเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: esentutl (0.083), Expand (0.034), cmd (0.015), Taint Shared Content (0.010), Lateral Tool Transfer (0.009), Network Share Discovery (0.005), RIFLESPINE (0.005), TDTESS (0.002), APT32 (0.001), LaZagne (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → esentutl (9 neighbors, 9 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Expand (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [50/100] retrieved=387 relevant=3 latency=40965ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 12 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าจดหมายอิเล็กทรอนิก...
[RETRIEVE] Query: เมื่อวันที่ 12 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าจดหมายอิเล็กทรอนิก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackdoorDiplomacy (0.008), APT-C-36 (0.004), Ursnif (0.001), XLoader (0.001), APT-C-36 (0.001), AADInternals (0.000), System Script Proxy Execution (0.000), File Deletion (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → BackdoorDiplomacy (20 neighbors, 20 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมฝังตัวดาวน์โหลดไฟล์โปรแกรมหลัก ไฟล์ประกอบ สคริปต์ติดตั้ง ไฟล์กฎคัดกรองจดห...
[RETRIEVE] Query: โปรแกรมฝังตัวดาวน์โหลดไฟล์โปรแกรมหลัก ไฟล์ประกอบ สคริปต์ติดตั้ง ไฟล์กฎคัดกรองจดห...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RTM (0.008), TYPEFRAME (0.005), CrossRAT (0.003), Installer Packages (0.002), Local Email Collection (0.001), Visual Basic (0.000), File Deletion (0.000), Credentials in Registry (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → RTM (39 neighbors, 39 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → TYPEFRAME (16 neighbors, 16 edges)
           → Fileless Storage (34 neighbors, 34 edges)
[RETRIEVE-QUOTA] Query 3/8: สวมสิทธิ์บัญชีผู้ดูแลโดเมนเพื่อเข้าถึงระบบ (Valid Accounts)...
[RETRIEVE] Query: สวมสิทธิ์บัญชีผู้ดูแลโดเมนเพื่อเข้าถึงระบบ (Valid Accounts)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT3 (0.612), Domain Account (0.494), Valid Accounts (0.397), Domain Accounts (0.385), Remote Services (0.049), Windows Remote Management (0.029), Account Discovery (0.023), Account Manipulation (0.016), Modify Authentication Process (0.002), Valak (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT3 (50 neighbors, 50 edges)
           → Domain Accounts (47 neighbors, 47 edges)
           → Domain Account (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 4/8: คัดลอกชุดไฟล์จากเครื่องที่ยึดครองไปยังเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์...
[RETRIEVE] Query: คัดลอกชุดไฟล์จากเครื่องที่ยึดครองไปยังเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.019), Ingress Tool Transfer (0.009), APT1 (0.005), Clipboard Data (0.001), Exfiltration Over Alternative Protocol (0.001), Remote Email Collection (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Local Email Collection (25 neighbors, 25 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 5/8: สั่งติดตั้งโปรแกรมบนเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์จากระยะไกล...
[RETRIEVE] Query: สั่งติดตั้งโปรแกรมบนเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์จากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteUtilities (0.025), RemoteCMD (0.023), xCmd (0.013), Emissary (0.006), MCMD (0.006), Koadic (0.005), CrackMapExec (0.004), Impacket (0.004), dsquery (0.002), NavRAT (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteUtilities (5 neighbors, 5 edges)
           → Msiexec (35 neighbors, 35 edges)
           → RemoteCMD (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/8: ติดตั้งโปรแกรมเป็นส่วนต่อขยายแทรกในขั้นตอนรับส่งจดหมายของเครื่องแม่ข่าย...
[RETRIEVE] Query: ติดตั้งโปรแกรมเป็นส่วนต่อขยายแทรกในขั้นตอนรับส่งจดหมายของเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PipeMon (0.010), Impacket (0.005), Software Extensions (0.002), Portable Executable Injection (0.002), Anchor (0.001), Installer Packages (0.001), IPsec Helper (0.001), Additional Email Delegate Permissions (0.000), POSHSPY (0.000), Hardware Additions (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PipeMon (24 neighbors, 24 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Impacket (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 7/8: ลักลอบอ่านจดหมายอิเล็กทรอนิกส์ของผู้บริหาร...
[RETRIEVE] Query: ลักลอบอ่านจดหมายอิเล็กทรอนิกส์ของผู้บริหาร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT28 (0.004), XLoader (0.002), Remote Email Collection (0.001), TA505 (0.000), Email Bombing (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT28 (124 neighbors, 124 edges)
           → Cloud Accounts (33 neighbors, 33 edges)
           → XLoader (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 8/8: ส่งต่อจดหมายอิเล็กทรอนิกส์ของผู้บริหารออกไปยังภายนอก (exfiltration)...
[RETRIEVE] Query: ส่งต่อจดหมายอิเล็กทรอนิกส์ของผู้บริหารออกไปยังภายนอก (exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OilCheck (0.028), Exfiltration Over Alternative Protocol (0.022), Exfiltration Over Other Network Medium (0.011), PowerExchange (0.008), Exfiltration (0.008), Exfiltration Over Physical Medium (0.006), Email Forwarding Rule (0.002), Empire (0.001), Salesforce Data Exfiltration (0.001), APT28 Nearest Neighbor Campaign (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OilCheck (4 neighbors, 4 edges)
           → Exfiltration Over Web Service (23 neighbors, 23 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [51/100] retrieved=630 relevant=3 latency=45450ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 8 พฤษภาคม 2567 ผู้ให้บริการโครงข่ายแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่า...
[RETRIEVE] Query: เมื่อวันที่ 8 พฤษภาคม 2567 ผู้ให้บริการโครงข่ายแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dragonfly (0.001), LAPSUS$ (0.001), System Time Discovery (0.000), FIN8 (0.000), AppInit DLLs (0.000), Lokibot (0.000), Scheduled Task/Job (0.000), Password Policy Discovery (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Dragonfly (66 neighbors, 66 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
           → Password Managers (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 2/6: เพิ่มงานตามเวลาใน Linux cron เพื่อเรียกโปรแกรมของคนร้ายทำงานซ้ำตามรอบเวลา...
[RETRIEVE] Query: เพิ่มงานตามเวลาใน Linux cron เพื่อเรียกโปรแกรมของคนร้ายทำงานซ้ำตามรอบเวลา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT38 (0.371), Cron (0.220), Xbash (0.187), Systemd Timers (0.107), Penquin (0.050), Container Orchestration Job (0.041), at (0.010), KernelCallbackTable (0.003), Linux Rabbit (0.000), /etc/passwd and /etc/shadow (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT38 (62 neighbors, 62 edges)
           → Cron (25 neighbors, 25 edges)
           → Xbash (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 3/6: สร้างหน่วยบริการเบื้องหลังของ Linux เพื่อให้โปรแกรมของคนร้ายทำงานทุกครั้งที่เครื...
[RETRIEVE] Query: สร้างหน่วยบริการเบื้องหลังของ Linux เพื่อให้โปรแกรมของคนร้ายทำงานทุกครั้งที่เครื...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Create or Modify System Process (0.377), Systemd Service (0.282), LITTLELAMB.WOOLTEA (0.022), Gomir (0.009), Linux Rabbit (0.003), Umbreon (0.003), /etc/passwd and /etc/shadow (0.001), at (0.001), at (0.001), Cyclops Blink (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → Systemd Service (22 neighbors, 22 edges)
           → LITTLELAMB.WOOLTEA (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/6: เปิดอ่านไฟล์ /etc/shadow ที่เก็บค่ารหัสผ่านของบัญชีผู้ใช้ทั้งหมดบน Linux...
[RETRIEVE] Query: เปิดอ่านไฟล์ /etc/shadow ที่เก็บค่ารหัสผ่านของบัญชีผู้ใช้ทั้งหมดบน Linux...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: /etc/passwd and /etc/shadow (0.955), LaZagne (0.508), Password Policies (0.125), ShadowRay (0.115), TruffleHog (0.003), gsecdump (0.001), SSH (0.001), Udev Rules (0.000), Behavior Prevention on Endpoint (0.000), Rogue Domain Controller (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → /etc/passwd and /etc/shadow (7 neighbors, 7 edges)
           → LaZagne (22 neighbors, 22 edges)
           → Password Policies (47 neighbors, 47 edges)
[RETRIEVE-QUOTA] Query 5/6: เปิดอ่านไฟล์ประวัติคำสั่งของผู้ดูแลระบบเพื่อขโมยคำสั่งที่เคยพิมพ์...
[RETRIEVE] Query: เปิดอ่านไฟล์ประวัติคำสั่งของผู้ดูแลระบบเพื่อขโมยคำสั่งที่เคยพิมพ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Clear Command History (0.095), Shell History (0.074), Prevent Command History Logging (0.069), BADHATCH (0.005), Unsecured Credentials (0.004), KONNI (0.004), Kobalos (0.003), PACEMAKER (0.002), Proc Filesystem (0.001), Access Token Manipulation (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Clear Command History (16 neighbors, 16 edges)
           → Shell History (5 neighbors, 5 edges)
           → Prevent Command History Logging (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 6/6: เปิดอ่านไฟล์กุญแจ SSH สำหรับการเชื่อมต่อระยะไกลในโฟลเดอร์ส่วนตัวของผู้ใช้...
[RETRIEVE] Query: เปิดอ่านไฟล์กุญแจ SSH สำหรับการเชื่อมต่อระยะไกลในโฟลเดอร์ส่วนตัวของผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH Authorized Keys (0.301), XCSSET (0.230), Private Keys (0.067), SSH Hijacking (0.036), SSH (0.015), PoshC2 (0.007), Cobalt Strike (0.005), Remote Services (0.003), Leviathan (0.000), Kessel (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SSH Authorized Keys (15 neighbors, 15 edges)
           → XCSSET (33 neighbors, 33 edges)
           → Private Keys (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [52/100] retrieved=338 relevant=4 latency=34003ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 12 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Query: เมื่อวันที่ 12 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DCHSpy (0.001), Exploit Public-Facing Application (0.001), Cardinal RAT (0.000), Ingress Tool Transfer (0.000), Exploitation for Client Execution (0.000), ThiefQuest (0.000), OwaAuth (0.000), Wevtutil (0.000), Clear Linux or Mac System Logs (0.000), Clear Windows Event Logs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DCHSpy (13 neighbors, 13 edges)
           → Call Log (44 neighbors, 44 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
[RETRIEVE-QUOTA] Query 2/6: โจมตีช่องโหว่ของซอฟต์แวร์บนเครื่องแม่ข่ายจากภายนอก (Exploit Public-Facing Applic...
[RETRIEVE] Query: โจมตีช่องโหว่ของซอฟต์แวร์บนเครื่องแม่ข่ายจากภายนอก (Exploit Public-Facing Applic...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.909), Sandworm Team (0.636), Leviathan (0.597), Network Segmentation (0.542), Exploitation of Remote Services (0.085), Exploitation for Client Execution (0.064), Exploit Protection (0.040), PowerSploit (0.029), Exploits (0.009), Multi-factor Authentication (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Sandworm Team (113 neighbors, 113 edges)
           → Leviathan (68 neighbors, 68 edges)
[RETRIEVE-QUOTA] Query 3/6: สั่งให้เครื่องแม่ข่ายดาวน์โหลดไฟล์สคริปต์อันตรายจากเว็บไซต์ภายนอก (Ingress Tool ...
[RETRIEVE] Query: สั่งให้เครื่องแม่ข่ายดาวน์โหลดไฟล์สคริปต์อันตรายจากเว็บไซต์ภายนอก (Ingress Tool ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Industroyer (0.650), Xbash (0.638), Ingress Tool Transfer (0.597), Conficker (0.502), cmd (0.437), Upload Malware (0.414), Lateral Tool Transfer (0.366), Upload Tool (0.008), BITS Jobs (0.003), Exfiltration Over Alternative Protocol (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Industroyer (21 neighbors, 21 edges)
           → Xbash (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/6: สั่งให้ไฟล์สคริปต์อันตรายทำงานบนเครื่องแม่ข่าย (Command and Scripting Interprete...
[RETRIEVE] Query: สั่งให้ไฟล์สคริปต์อันตรายทำงานบนเครื่องแม่ข่าย (Command and Scripting Interprete...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DarkComet (0.707), Network Device CLI (0.593), Saint Bear (0.447), Command and Scripting Interpreter (0.294), CHOPSTICK (0.263), System Script Proxy Execution (0.125), Empire (0.095), Data from Local System (0.093), Indirect Command Execution (0.015), Native API (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Network Device CLI (11 neighbors, 11 edges)
           → DarkComet (21 neighbors, 21 edges)
           → Command and Scripting Interpreter (68 neighbors, 68 edges)
[RETRIEVE-QUOTA] Query 5/6: ใช้ช่องโหว่อีกรายการเพื่อยกระดับสิทธิ์ให้สคริปต์ทำงานด้วยสิทธิ์สูงสุดของระบบ (Ex...
[RETRIEVE] Query: ใช้ช่องโหว่อีกรายการเพื่อยกระดับสิทธิ์ให้สคริปต์ทำงานด้วยสิทธิ์สูงสุดของระบบ (Ex...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploitation for Privilege Escalation (0.777), Zox (0.633), ZIRCONIUM (0.628), Exodus (0.607), APT32 (0.606), Privilege Escalation (0.432), Elevated Execution with Prompt (0.068), Exploitation for Credential Access (0.040), Exploitation of Remote Services (0.003), Exploit Protection (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → Zox (10 neighbors, 10 edges)
           → ZIRCONIUM (29 neighbors, 29 edges)
[RETRIEVE-QUOTA] Query 6/6: ใช้ส่วนประกอบสร้างข้อความแจ้งเตือนของซอฟต์แวร์ที่ติดตั้งอยู่แล้วเพื่อส่งคำขอสั่ง...
[RETRIEVE] Query: ใช้ส่วนประกอบสร้างข้อความแจ้งเตือนของซอฟต์แวร์ที่ติดตั้งอยู่แล้วเพื่อส่งคำขอสั่ง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Web Protocols (0.237), Application Layer Protocol (0.083), Duqu (0.061), P.A.S. Webshell (0.046), Mail Protocols (0.014), File Transfer Protocols (0.009), Non-Application Layer Protocol (0.007), Mythic (0.002), Industroyer (0.001), Protocol Tunneling (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Web Protocols (424 neighbors, 424 edges)
           → Application Layer Protocol (25 neighbors, 25 edges)
           → Duqu (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [53/100] retrieved=723 relevant=5 latency=29527ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 14 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Query: เมื่อวันที่ 14 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.006), Bankshot (0.002), Pikabot (0.000), FIN8 (0.000), Domains (0.000), Domain Account (0.000), Domain Accounts (0.000), Windows Registry Key Modification (0.000), Access Token Manipulation (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] Query 2/7: ใช้คำสั่งสอบถามชื่อโดเมนเพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายควบคุมโดเมนเป้าหมา...
[RETRIEVE] Query: ใช้คำสั่งสอบถามชื่อโดเมนเพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายควบคุมโดเมนเป้าหมา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain Generation Algorithms (0.113), PowerDuke (0.050), LazyWiper (0.039), Active DNS (0.039), Caterpillar WebShell (0.033), Domain Account (0.018), SHOTPUT (0.012), ipconfig (0.003), Domain Groups (0.002), route (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Domain Generation Algorithms (29 neighbors, 29 edges)
           → PowerDuke (16 neighbors, 16 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] Query 3/7: สร้างบริการของระบบบนเครื่องแม่ข่ายควบคุมโดเมนเพื่อสั่งรันคำสั่งจากเครื่องแม่ข่าย...
[RETRIEVE] Query: สร้างบริการของระบบบนเครื่องแม่ข่ายควบคุมโดเมนเพื่อสั่งรันคำสั่งจากเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackConfig (0.021), Container Administration Command (0.004), Domain Account (0.003), AppDomainManager (0.003), Container Service (0.002), CrackMapExec (0.002), Rogue Domain Controller (0.001), Service Execution (0.001), PsExec (0.001), PsExec (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BackConfig (17 neighbors, 17 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Container Administration Command (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 4/7: สั่งรันคำสั่งข้ามจากเครื่องแม่ข่ายเก็บเอกสารไปยังเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: สั่งรันคำสั่งข้ามจากเครื่องแม่ข่ายเก็บเอกสารไปยังเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Peirates (0.082), Pacu (0.014), POWRUNER (0.014), BackConfig (0.006), Container Administration Command (0.004), AppDomainManager (0.002), DCSync (0.002), BONDUPDATER (0.001), Rogue Domain Controller (0.001), Dynamic Data Exchange (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Peirates (13 neighbors, 13 edges)
           → Container Administration Command (12 neighbors, 12 edges)
           → Pacu (21 neighbors, 21 edges)
           → Cloud Administration Command (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/7: อัปโหลดและเรียกใช้ไฟล์โปรแกรมขนาดเล็กบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: อัปโหลดและเรียกใช้ไฟล์โปรแกรมขนาดเล็กบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Small Sieve (0.066), AppDomainManager (0.025), BackConfig (0.016), DCSync (0.007), Winexe (0.005), Visual Basic (0.000), Impacket (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Small Sieve (14 neighbors, 14 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → AppDomainManager (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 6/7: ให้โปรแกรมติดต่อกลับไปยังเครื่องสั่งการภายนอกผ่านพอร์ตที่ไม่ใช่พอร์ตมาตรฐานเพื่อ...
[RETRIEVE] Query: ให้โปรแกรมติดต่อกลับไปยังเครื่องสั่งการภายนอกผ่านพอร์ตที่ไม่ใช่พอร์ตมาตรฐานเพื่อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exodus (0.412), Covenant (0.233), QuasarRAT (0.215), Pikabot (0.128), Non-Standard Port (0.096), External Proxy (0.047), Exfiltration Over Alternative Protocol (0.017), Exfiltration Over Unencrypted Non-C2 Protocol (0.002), Non-Application Layer Protocol (0.001), Ptrace System Calls (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Exodus (19 neighbors, 19 edges)
           → Non-Standard Port (9 neighbors, 9 edges)
           → Covenant (11 neighbors, 11 edges)
           → Non-Standard Port (70 neighbors, 70 edges)
[RETRIEVE-QUOTA] Query 7/7: เรียกดูรายละเอียดเครื่องคอมพิวเตอร์ของผู้บริหารฝ่ายการเงินจากระบบทะเบียนโดเมน...
[RETRIEVE] Query: เรียกดูรายละเอียดเครื่องคอมพิวเตอร์ของผู้บริหารฝ่ายการเงินจากระบบทะเบียนโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Valak (0.000), dsquery (0.000), Latrodectus (0.000), NTDS (0.000), Nltest (0.000), Domain Account (0.000), SoreFang (0.000), Bazar (0.000), Domain Accounts (0.000), Domain or Tenant Policy Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Valak (35 neighbors, 35 edges)
           → Domain Account (65 neighbors, 65 edges)
           → NTDS (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [54/100] retrieved=606 relevant=3 latency=33930ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 27 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความว่าอุปกรณ์เ...
[RETRIEVE] Query: เมื่อวันที่ 27 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความว่าอุปกรณ์เ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.002), BlackByte (0.001), APT-C-36 (0.001), Component Firmware (0.000), DRYHOOK (0.000), Ursnif (0.000), Internal Spearphishing (0.000), Compromise Host Software Binary (0.000), Shortcut Modification (0.000), Social Engineering (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → BlackByte (56 neighbors, 56 edges)
           → Disable or Modify System Firewall (38 neighbors, 38 edges)
[RETRIEVE-QUOTA] Query 2/6: แก้ไขซอฟต์แวร์ระดับเฟิร์มแวร์ของอุปกรณ์เราเตอร์หลายเครื่อง...
[RETRIEVE] Query: แก้ไขซอฟต์แวร์ระดับเฟิร์มแวร์ของอุปกรณ์เราเตอร์หลายเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Update Software (0.008), Update Software (0.007), Component Firmware (0.004), Update Software (0.002), Visual Basic (0.001), CrossRAT (0.000), nbtstat (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Update Software (42 neighbors, 42 edges)
           → System Firmware (10 neighbors, 10 edges)
           → Firmware Corruption (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/6: ฝังชุดคำสั่งของคนร้ายในเฟิร์มแวร์เพื่อคงอยู่หลังรีสตาร์ตหรือการปรับปรุงระบบ...
[RETRIEVE] Query: ฝังชุดคำสั่งของคนร้ายในเฟิร์มแวร์เพื่อคงอยู่หลังรีสตาร์ตหรือการปรับปรุงระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Frankenstein (0.151), Create or Modify System Process (0.023), Unix Shell Configuration Modification (0.022), Active Setup (0.003), BackConfig (0.001), Cardinal RAT (0.001), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Frankenstein (28 neighbors, 28 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Create or Modify System Process (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 4/6: เปิดช่องทางเชื่อมต่อระยะไกลลับในเฟิร์มแวร์ที่ถูกดัดแปลงเพื่อเข้าถึงเราเตอร์...
[RETRIEVE] Query: เปิดช่องทางเชื่อมต่อระยะไกลลับในเฟิร์มแวร์ที่ถูกดัดแปลงเพื่อเข้าถึงเราเตอร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PyDCrypt (0.047), FRP (0.009), FatDuke (0.008), RDFSNIFFER (0.006), BlackByte (0.006), HTRAN (0.005), SSH (0.003), FRP (0.003), SHOTPUT (0.001), Exfiltration Over Alternative Protocol (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → PyDCrypt (12 neighbors, 12 edges)
           → Disable or Modify System Firewall (38 neighbors, 38 edges)
           → FatDuke (23 neighbors, 23 edges)
           → Internal Proxy (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 5/6: ทำให้การเชื่อมต่อระยะไกลของคนร้ายไม่ถูกบันทึกในไฟล์บันทึกเหตุการณ์ของเราเตอร์...
[RETRIEVE] Query: ทำให้การเชื่อมต่อระยะไกลของคนร้ายไม่ถูกบันทึกในไฟล์บันทึกเหตุการณ์ของเราเตอร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Data Storage (0.027), Remote Data Storage (0.011), Remote Data Storage (0.008), Clear Network Connection History and Configurations (0.005), DarkWatchman (0.002), Encrypt Sensitive Information (0.000), Selective Exclusion (0.000), FIN5 (0.000), Create Snapshot (0.000), Transfer Data to Cloud Account (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Remote Data Storage (11 neighbors, 11 edges)
           → Clear Network Connection History and Configurations (8 neighbors, 8 edges)
           → Clear Windows Event Logs (47 neighbors, 47 edges)
[RETRIEVE-QUOTA] Query 6/6: ส่งแพ็กเก็ตที่ประกอบขึ้นเป็นพิเศษเพื่อสั่งเปิดและปิดช่องทางลับของเราเตอร์ (Port ...
[RETRIEVE] Query: ส่งแพ็กเก็ตที่ประกอบขึ้นเป็นพิเศษเพื่อสั่งเปิดและปิดช่องทางลับของเราเตอร์ (Port ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Port Knocking (0.628), cd00r (0.371), Traffic Signaling (0.232), REPTILE (0.050), Mafalda (0.040), PROMETHIUM (0.036), Impacket (0.001), Compute Hijacking (0.000), Thread Execution Hijacking (0.000), VDSO Hijacking (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Port Knocking (13 neighbors, 13 edges)
           → cd00r (4 neighbors, 4 edges)
           → Traffic Signaling (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [55/100] retrieved=174 relevant=3 latency=26286ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 28 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความว่าเครือข่ายของสำนักง...
[RETRIEVE] Query: เมื่อวันที่ 28 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความว่าเครือข่ายของสำนักง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.025), ServHelper (0.016), HomeLand Justice (0.000), RDP Hijacking (0.000), Network Intrusion Prevention (0.000), File Deletion (0.000), Remote Services (0.000), Remote Desktop Protocol (0.000), Terminal Services DLL (0.000), Data Encrypted for Impact (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → ServHelper (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 2/7: สั่งปิดการบันทึกเหตุการณ์ของระบบเพื่อไม่ให้เหลือหลักฐาน...
[RETRIEVE] Query: สั่งปิดการบันทึกเหตุการณ์ของระบบเพื่อไม่ให้เหลือหลักฐาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Clear Windows Event Logs (0.034), Wevtutil (0.023), Disable or Modify Windows Event Log (0.012), VIRTUALPITA (0.006), Prevent Command History Logging (0.002), Ignore Process Interrupts (0.000), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Wevtutil (10 neighbors, 10 edges)
           → Disable or Modify Windows Event Log (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/7: ใช้ความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนบริษัทลูกกับสำนักงานใหญ่เพื่อกระโดดข้า...
[RETRIEVE] Query: ใช้ความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนบริษัทลูกกับสำนักงานใหญ่เพื่อกระโดดข้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Trust Modification (0.002), Trusted Relationship (0.002), Break Process Trees (0.001), Domain or Tenant Policy Modification (0.001), Privileged Account Management (0.000), Network Segmentation (0.000), AADInternals (0.000), DCSync (0.000), Domain Controller Authentication (0.000), Privileged Account Management (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Trust Modification (10 neighbors, 10 edges)
           → Trusted Relationship (18 neighbors, 18 edges)
           → Break Process Trees (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 4/7: ใช้ใบรับรองสำหรับลงลายมือชื่อโปรแกรมที่ขโมมาเซ็นกำกับไฟล์โปรแกรมอันตราย...
[RETRIEVE] Query: ใช้ใบรับรองสำหรับลงลายมือชื่อโปรแกรมที่ขโมมาเซ็นกำกับไฟล์โปรแกรมอันตราย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Daggerfly (0.804), PROMETHIUM (0.767), Daggerfly (0.371), Code Signing (0.292), System Script Proxy Execution (0.202), Code Signing Certificates (0.173), Code Signing Certificates (0.167), Code Signing (0.055), Invalid Code Signature (0.033), System Binary Proxy Execution (0.023)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Daggerfly (23 neighbors, 23 edges)
           → Code Signing Certificates (7 neighbors, 7 edges)
           → PROMETHIUM (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 5/7: เปิดเชลล์รับการเชื่อมต่อค้างไว้เพื่อคงอยู่ในเครื่องผู้เสียหาย...
[RETRIEVE] Query: เปิดเชลล์รับการเชื่อมต่อค้างไว้เพื่อคงอยู่ในเครื่องผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Green Lambert (0.007), Gazer (0.007), SSH (0.004), Netsh Helper DLL (0.003), TONESHELL (0.002), ADVSTORESHELL (0.001), FLIPSIDE (0.000), CallMe (0.000), Network Device CLI (0.000), Network Provider DLL (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Green Lambert (18 neighbors, 18 edges)
           → Unix Shell Configuration Modification (13 neighbors, 13 edges)
           → Gazer (19 neighbors, 19 edges)
           → Winlogon Helper DLL (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 6/7: แก้ไขทะเบียนระบบเพื่อเปิดใช้งาน Remote Desktop Protocol...
[RETRIEVE] Query: แก้ไขทะเบียนระบบเพื่อเปิดใช้งาน Remote Desktop Protocol...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SILENTTRINITY (0.937), Modify Registry (0.227), Remote Desktop Protocol (0.018), RDP Hijacking (0.006), Koadic (0.006), Axiom (0.002), Terminal Services DLL (0.002), APT28 Nearest Neighbor Campaign (0.001), Remote Access Tools (0.000), Remote Services (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
[RETRIEVE-QUOTA] Query 7/7: เข้าใช้งานเครื่องผู้เสียหายผ่าน SSH...
[RETRIEVE] Query: เข้าใช้งานเครื่องผู้เสียหายผ่าน SSH...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH (0.580), SSH Hijacking (0.336), FIN7 (0.209), SSH Authorized Keys (0.097), Remote Service Session Hijacking (0.020), Cobalt Strike (0.010), Remote Services (0.008), Leviathan (0.006), Kessel (0.003), Shamoon (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SSH (33 neighbors, 33 edges)
           → SSH Hijacking (8 neighbors, 8 edges)
           → FIN7 (86 neighbors, 86 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [56/100] retrieved=165 relevant=4 latency=30702ms
[RETRIEVE-QUOTA] Query 1/11: เมื่อวันที่ 16 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความว่าระบบงานทั้งหมดถูกเข้า...
[RETRIEVE] Query: เมื่อวันที่ 16 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความว่าระบบงานทั้งหมดถูกเข้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: REvil (0.005), POWERSTATS (0.004), Pay2Key (0.001), BitPaymer (0.001), Data Encrypted for Impact (0.000), POWERSOURCE (0.000), Disable or Remove Feature or Program (0.000), PowerSploit (0.000), PowerShell (0.000), PowerShell Profile (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → REvil (37 neighbors, 37 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → PowerShell (241 neighbors, 241 edges)
[RETRIEVE-QUOTA] Query 2/11: แทรกชุดคำสั่งของโปรแกรมเรียกค่าไถ่เข้าไปในหน่วยความจำของกระบวนการที่กำลังทำงาน (...
[RETRIEVE] Query: แทรกชุดคำสั่งของโปรแกรมเรียกค่าไถ่เข้าไปในหน่วยความจำของกระบวนการที่กำลังทำงาน (...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Proc Memory (0.939), Process Injection (0.887), Mispadu (0.643), HTRAN (0.430), Extra Window Memory Injection (0.251), Ptrace System Calls (0.211), Dynamic-link Library Injection (0.170), metaMain (0.118), Portable Executable Injection (0.095), Donut (0.022)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Proc Memory (7 neighbors, 7 edges)
           → Process Injection (104 neighbors, 104 edges)
           → Mispadu (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] Query 3/11: รันคำสั่งแก้ไขทะเบียนระบบผ่านหน้าต่างคำสั่งของวินโดวส์ (Windows Registry และ Win...
[RETRIEVE] Query: รันคำสั่งแก้ไขทะเบียนระบบผ่านหน้าต่างคำสั่งของวินโดวส์ (Windows Registry และ Win...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HeartCrypt (0.693), Pisloader (0.548), Ryuk (0.303), Reg (0.243), Modify Registry (0.184), Windows Command Shell (0.041), Windows Registry Key Modification (0.041), Registry Run Keys / Startup Folder (0.024), Query Registry (0.009), Command and Scripting Interpreter (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → HeartCrypt (12 neighbors, 12 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Pisloader (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 4/11: เปลี่ยนนามสกุลของไฟล์ที่เข้ารหัสแล้วทุกไฟล์เป็นนามสกุลเฉพาะของโปรแกรมเรียกค่าไถ่...
[RETRIEVE] Query: เปลี่ยนนามสกุลของไฟล์ที่เข้ารหัสแล้วทุกไฟล์เป็นนามสกุลเฉพาะของโปรแกรมเรียกค่าไถ่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Black Basta (0.027), Space after Filename (0.009), Change Default File Association (0.007), KernelCallbackTable (0.001), BADCALL (0.001), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Black Basta (27 neighbors, 27 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → Space after Filename (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 5/11: ใช้ PowerShell ลบไฟล์โปรแกรมของตนออกจากเครือข่าย (File Deletion)...
[RETRIEVE] Query: ใช้ PowerShell ลบไฟล์โปรแกรมของตนออกจากเครือข่าย (File Deletion)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BADHATCH (0.681), PureCrypter (0.597), POWERSTATS (0.525), Netwalker (0.023), Network Share Connection Removal (0.010), CHIMNEYSWEEP (0.007), PowerShell (0.006), PowerShell Profile (0.004), POWERSTATS (0.003), SDelete (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BADHATCH (36 neighbors, 36 edges)
           → File Deletion (310 neighbors, 310 edges)
           → PureCrypter (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] Query 6/11: เรียกใช้หน้าต่างคำสั่งที่ถูกซ่อนเพื่อไม่ให้ผู้ใช้มองเห็น...
[RETRIEVE] Query: เรียกใช้หน้าต่างคำสั่งที่ถูกซ่อนเพื่อไม่ให้ผู้ใช้มองเห็น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lumma Stealer (0.869), Hidden Window (0.746), QuasarRAT (0.702), MCMD (0.550), WindTail (0.116), Hidden Files and Directories (0.081), Command Obfuscation (0.076), Hidden Users (0.030), Ignore Process Interrupts (0.007), Process Hollowing (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Hidden Window (65 neighbors, 65 edges)
           → Lumma Stealer (35 neighbors, 35 edges)
           → QuasarRAT (32 neighbors, 32 edges)
[RETRIEVE-QUOTA] Query 7/11: สำรวจเครือข่ายของโรงพยาบาล (Network Discovery)...
[RETRIEVE] Query: สำรวจเครือข่ายของโรงพยาบาล (Network Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AdFind (0.255), System Network Connections Discovery (0.022), LODEINFO (0.012), Internet Connection Discovery (0.005), System Network Configuration Discovery (0.005), Net (0.001), Remote System Discovery (0.001), Patchwork (0.000), Patchwork (0.000), Scan Databases (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → AdFind (19 neighbors, 19 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
[RETRIEVE-QUOTA] Query 8/11: เข้ารหัสข้อมูลของโรงพยาบาลด้วยกุญแจสาธารณะขนาด 4096 บิตร่วมกับอัลกอริทึมเข้ารหัส...
[RETRIEVE] Query: เข้ารหัสข้อมูลของโรงพยาบาลด้วยกุญแจสาธารณะขนาด 4096 บิตร่วมกับอัลกอริทึมเข้ารหัส...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Conti (0.397), Data Encrypted for Impact (0.327), Qilin (0.279), Avaddon (0.173), BitPaymer (0.094), Asymmetric Cryptography (0.029), BitPaymer (0.008), Backup Software Discovery (0.001), Impact (0.001), Account Access Removal (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Conti (18 neighbors, 18 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → Qilin (54 neighbors, 54 edges)
[RETRIEVE-QUOTA] Query 9/11: นำข้อมูลอ่อนไหวของโรงพยาบาลออกไปเพื่อข่มขู่ว่าจะเผยแพร่ (Exfiltration)...
[RETRIEVE] Query: นำข้อมูลอ่อนไหวของโรงพยาบาลออกไปเพื่อข่มขู่ว่าจะเผยแพร่ (Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration (0.020), Salesforce Data Exfiltration (0.011), Exfiltration Over Other Network Medium (0.011), Exfiltration Over Physical Medium (0.007), Contagious Interview (0.005), Exfiltration Over Alternative Protocol (0.003), Empire (0.002), Data from Network Shared Drive (0.001), Exbyte (0.001), Exbyte (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Exfiltration (19 neighbors, 19 edges)
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
           → Salesforce Data Exfiltration (19 neighbors, 19 edges)
           → Spearphishing Voice (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 10/11: เรียกค่าไถ่สองชั้นโดยขู่เผยแพร่ข้อมูลอ่อนไหวที่นำออกไปหากไม่ชำระเงิน...
[RETRIEVE] Query: เรียกค่าไถ่สองชั้นโดยขู่เผยแพร่ข้อมูลอ่อนไหวที่นำออกไปหากไม่ชำระเงิน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Storm-0501 (0.552), Black Basta (0.174), Play (0.159), Spearphishing Service (0.006), SMS Pumping (0.000), Cobian RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Storm-0501 (50 neighbors, 50 edges)
           → Financial Theft (27 neighbors, 27 edges)
           → Play (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 11/11: เรียกเงินค่าถอดรหัสข้อมูลโดยให้โอนเงินสกุลเงินดิจิทัลไปยังกระเป๋าเงินที่กำหนด...
[RETRIEVE] Query: เรียกเงินค่าถอดรหัสข้อมูลโดยให้โอนเงินสกุลเงินดิจิทัลไปยังกระเป๋าเงินที่กำหนด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WannaCry (0.116), BitPaymer (0.011), Pay2Key (0.007), ShrinkLocker (0.002), Ptrace System Calls (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), Cobian RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → WannaCry (17 neighbors, 17 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → BitPaymer (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 11 queries
  [57/100] retrieved=407 relevant=6 latency=59430ms
[RETRIEVE-QUOTA] Query 1/10: เมื่อวันที่ 17 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความว่าลูกค้าหลายรายถูกโอนเงินออกจ...
[RETRIEVE] Query: เมื่อวันที่ 17 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความว่าลูกค้าหลายรายถูกโอนเงินออกจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.282), Frankenstein (0.252), Exfiltration Over C2 Channel (0.150), Octopus (0.147), AuTo Stealer (0.143), Resource Hijacking (0.140), Automated Exfiltration (0.040), Scheduled Transfer (0.008), Exfiltration Over Unencrypted Non-C2 Protocol (0.001), Financial Theft (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Frankenstein (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 2/10: โปรแกรมไม่พึงประสงค์แทรกตัวอยู่ในโปรแกรมท่องเว็บของผู้ใช้ (Browser Extensions)...
[RETRIEVE] Query: โปรแกรมไม่พึงประสงค์แทรกตัวอยู่ในโปรแกรมท่องเว็บของผู้ใช้ (Browser Extensions)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bundlore (0.790), Browser Extensions (0.260), Audit (0.204), Software Extensions (0.139), HTTPBrowser (0.126), Dok (0.032), Audit (0.022), Audit (0.018), IDE Extensions (0.016), Double File Extension (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bundlore (23 neighbors, 23 edges)
           → Browser Extensions (15 neighbors, 15 edges)
           → Audit (110 neighbors, 110 edges)
[RETRIEVE-QUOTA] Query 3/10: ดักจับและแก้ไขข้อมูลที่ผู้ใช้กรอกบนหน้าเว็บธนาคาร (Web Inject)...
[RETRIEVE] Query: ดักจับและแก้ไขข้อมูลที่ผู้ใช้กรอกบนหน้าเว็บธนาคาร (Web Inject)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QakBot (0.661), SharkBot (0.135), gh0st RAT (0.002), Input Injection (0.001), Credential API Hooking (0.001), Mavinject (0.001), Social Media (0.000), Ptrace System Calls (0.000), Empire (0.000), Active Directory Object Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → QakBot (74 neighbors, 74 edges)
           → JavaScript (76 neighbors, 76 edges)
           → SharkBot (18 neighbors, 18 edges)
           → GUI Input Capture (34 neighbors, 34 edges)
[RETRIEVE-QUOTA] Query 4/10: ขโมยชื่อผู้ใช้และรหัสผ่านของผู้เสียหาย...
[RETRIEVE] Query: ขโมยชื่อผู้ใช้และรหัสผ่านของผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Unknown Logger (0.822), Credential Access (0.756), FIN6 (0.500), Lokibot (0.347), MirrorStealer (0.134), Neoichor (0.124), WINDSHIELD (0.117), Exploitation for Credential Access (0.054), Mimikatz (0.048), Threat Group-1314 (0.031)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credential Access (67 neighbors, 67 edges)
           → Unknown Logger (9 neighbors, 9 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
[RETRIEVE-QUOTA] Query 5/10: ดึงไฟล์โปรแกรมอันตรายจากเครื่องภายนอกเข้ามาติดตั้งเพิ่ม (ดาวน์โหลดมัลแวร์)...
[RETRIEVE] Query: ดึงไฟล์โปรแกรมอันตรายจากเครื่องภายนอกเข้ามาติดตั้งเพิ่ม (ดาวน์โหลดมัลแวร์)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Phenakite (0.166), OopsIE (0.036), Kerrdown (0.035), BadPatch (0.023), Software Extensions (0.008), Cobian RAT (0.002), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Phenakite (11 neighbors, 11 edges)
           → Ingress Tool Transfer (18 neighbors, 18 edges)
           → OopsIE (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 6/10: ส่งข้อมูลที่รวบรวมได้ไปยังเครื่องสั่งการผ่าน Exfiltration Over C2 Channel...
[RETRIEVE] Query: ส่งข้อมูลที่รวบรวมได้ไปยังเครื่องสั่งการผ่าน Exfiltration Over C2 Channel...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SVCReady (0.982), Industroyer (0.974), Exfiltration Over C2 Channel (0.908), Automated Exfiltration (0.821), APT39 (0.777), Manjusaka (0.574), Scheduled Transfer (0.552), Exfiltration Over Unencrypted Non-C2 Protocol (0.519), Data Staged (0.025), Remote Data Staging (0.007)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Automated Exfiltration (33 neighbors, 33 edges)
           → SVCReady (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 7/10: แอบใช้ทรัพยากรเครื่องผู้เสียหายขุดเหรียญสกุลเงินดิจิทัล (Resource Hijacking)...
[RETRIEVE] Query: แอบใช้ทรัพยากรเครื่องผู้เสียหายขุดเหรียญสกุลเงินดิจิทัล (Resource Hijacking)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Resource Hijacking (0.944), Compute Hijacking (0.826), LoudMiner (0.814), DarkGate (0.681), BBSRAT (0.033), Dynamic Linker Hijacking (0.020), VDSO Hijacking (0.012), Bandwidth Hijacking (0.007), Use Recent OS Version (0.007), Thread Execution Hijacking (0.007)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Resource Hijacking (6 neighbors, 6 edges)
           → Compute Hijacking (17 neighbors, 17 edges)
           → LoudMiner (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 8/10: เรียกดูข้อมูลของเครื่องผู้เสียหาย (System Information Discovery)...
[RETRIEVE] Query: เรียกดูข้อมูลของเครื่องผู้เสียหาย (System Information Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: IMAPLoader (0.741), System Information Discovery (0.473), Sowbug (0.459), Systeminfo (0.150), SYSCON (0.148), Device Driver Discovery (0.113), Search Open Technical Databases (0.112), System Service Discovery (0.067), System Owner/User Discovery (0.031), Process Discovery (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → IMAPLoader (10 neighbors, 10 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Sowbug (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 9/10: เรียกดูข้อมูลเฟิร์มแวร์ระดับล่างของเครื่องผู้เสียหาย...
[RETRIEVE] Query: เรียกดูข้อมูลเฟิร์มแวร์ระดับล่างของเครื่องผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Firmware (0.312), FALLCHILL (0.104), zwShell (0.032), Search Open Technical Databases (0.008), Vulnerability Scanning (0.006), Backup Software Discovery (0.005), Visual Basic (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Firmware (3 neighbors, 3 edges)
           → FALLCHILL (10 neighbors, 10 edges)
           → System Information Discovery (426 neighbors, 426 edges)
[RETRIEVE-QUOTA] Query 10/10: โอนเงินออกจากบัญชีลูกค้าโดยไม่ได้รับอนุญาต...
[RETRIEVE] Query: โอนเงินออกจากบัญชีลูกค้าโดยไม่ได้รับอนุญาต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Account Use Policies (0.004), User Account Management (0.004), FIN6 (0.000), 4H RAT (0.000), Woody RAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Account Use Policies (11 neighbors, 11 edges)
           → User Account Management (119 neighbors, 119 edges)
           → Financial Theft (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 10 queries
  [58/100] retrieved=369 relevant=4 latency=43036ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 1 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครือข่ายภายในถูกบุกรุกผ...
[RETRIEVE] Query: เมื่อวันที่ 1 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครือข่ายภายในถูกบุกรุกผ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NETWIRE (0.007), Network Device Firewall (0.006), SharePoint ToolShell Exploitation (0.002), Internal Spearphishing (0.001), Magic Hound (0.001), Threat Group-3390 (0.000), Valid Accounts (0.000), Trusted Relationship (0.000), Clear Windows Event Logs (0.000), Clear Linux or Mac System Logs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Network Device Firewall (9 neighbors, 9 edges)
           → NETWIRE (49 neighbors, 49 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
[RETRIEVE-QUOTA] Query 2/5: โจมตีอุปกรณ์ SSL VPN รุ่นเก่าที่ยังไม่ได้ปรับปรุงซอฟต์แวร์ผ่านช่องโหว่ที่เปิดให้...
[RETRIEVE] Query: โจมตีอุปกรณ์ SSL VPN รุ่นเก่าที่ยังไม่ได้ปรับปรุงซอฟต์แวร์ผ่านช่องโหว่ที่เปิดให้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SoreFang (0.910), UNC3886 (0.754), Exploit Public-Facing Application (0.642), menuPass (0.604), Web Portal Capture (0.006), Exploitation for Client Execution (0.005), Exploit Protection (0.004), Exploits (0.003), Valid Accounts (0.002), Multi-factor Authentication (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SoreFang (15 neighbors, 15 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → UNC3886 (58 neighbors, 58 edges)
[RETRIEVE-QUOTA] Query 3/5: โจมตีอุปกรณ์ไฟร์วอลล์และอุปกรณ์เชื่อมต่อระยะไกลที่ยังไม่ได้ปรับปรุงผ่านช่องโหว่จ...
[RETRIEVE] Query: โจมตีอุปกรณ์ไฟร์วอลล์และอุปกรณ์เชื่อมต่อระยะไกลที่ยังไม่ได้ปรับปรุงผ่านช่องโหว่จ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.725), FrostyGoop Incident (0.604), Sandworm Team (0.381), Network Segmentation (0.311), Leviathan (0.283), PowerSploit (0.006), P.A.S. Webshell (0.005), Exploitation for Client Execution (0.004), Exploits (0.003), Exploit Protection (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → FrostyGoop Incident (5 neighbors, 5 edges)
           → Sandworm Team (113 neighbors, 113 edges)
[RETRIEVE-QUOTA] Query 4/5: ใช้ชื่อผู้ใช้และรหัสผ่าน SSL VPN ที่ถูกขโมยเพื่อเข้าสู่เครือข่ายของหน่วยงาน (Val...
[RETRIEVE] Query: ใช้ชื่อผู้ใช้และรหัสผ่าน SSL VPN ที่ถูกขโมยเพื่อเข้าสู่เครือข่ายของหน่วยงาน (Val...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operation Wocao (0.927), LAPSUS$ (0.527), Valid Accounts (0.526), External Remote Services (0.337), Web Portal Capture (0.167), Remote Service Session Hijacking (0.166), Remote Services (0.163), Volt Typhoon (0.058), Windows Remote Management (0.015), Remote Desktop Protocol (0.004)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Operation Wocao (79 neighbors, 79 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] Query 5/5: ใช้ชื่อผู้ใช้และรหัสผ่านหน้าจอระยะไกลที่ถูกขโมยเพื่อล็อกอินเข้าสู่ระบบของหน่วยงา...
[RETRIEVE] Query: ใช้ชื่อผู้ใช้และรหัสผ่านหน้าจอระยะไกลที่ถูกขโมยเพื่อล็อกอินเข้าสู่ระบบของหน่วยงา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Service Session Hijacking (0.553), APT18 (0.306), Remote Services (0.295), Valid Accounts (0.194), LAPSUS$ (0.185), Remote Desktop Protocol (0.120), Windows Remote Management (0.084), User Account Management (0.026), External Remote Services (0.025), Privileged Account Management (0.015)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Remote Service Session Hijacking (9 neighbors, 9 edges)
           → Remote Services (23 neighbors, 23 edges)
           → APT18 (17 neighbors, 17 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] 14 vectors (quota 3/query), 8 subgraphs from 5 queries
  [59/100] retrieved=308 relevant=3 latency=29271ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 3 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์หลาย...
[RETRIEVE] Query: เมื่อวันที่ 3 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์หลาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WINDSHIELD (0.009), njRAT (0.003), 3CX Supply Chain Attack (0.000), FIN8 (0.000), Software Discovery (0.000), 3PARA RAT (0.000), Software (0.000), Process Discovery (0.000), Pikabot (0.000), APT1 (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → WINDSHIELD (6 neighbors, 6 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → njRAT (40 neighbors, 40 edges)
[RETRIEVE-QUOTA] Query 2/9: ปิดการเชื่อมต่อหน้าจอระยะไกลที่เปิดค้างไว้บนเครื่องเป้าหมายแรก...
[RETRIEVE] Query: ปิดการเชื่อมต่อหน้าจอระยะไกลที่เปิดค้างไว้บนเครื่องเป้าหมายแรก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exobot (0.002), Disable or Remove Feature or Program (0.001), Woody RAT (0.000), Cobian RAT (0.000), CrossRAT (0.000), Disable or Remove Feature or Program (0.000), Visual Basic (0.000), 4H RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Exobot (15 neighbors, 15 edges)
           → Endpoint Denial of Service (8 neighbors, 8 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → Re-opened Applications (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 3/9: ใช้ชื่อผู้ใช้และรหัสผ่านที่ค้นพบเพื่อเชื่อมต่อ RDP จากเครื่องหนึ่งเข้าสู่เครื่อง...
[RETRIEVE] Query: ใช้ชื่อผู้ใช้และรหัสผ่านที่ค้นพบเพื่อเชื่อมต่อ RDP จากเครื่องหนึ่งเข้าสู่เครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SDBbot (0.055), TrickBot (0.026), Chimera (0.022), Remote Desktop Protocol (0.022), Remote Service Session Hijacking (0.015), RDP Hijacking (0.013), Terminal Services DLL (0.005), Axiom (0.002), Application Layer Protocol (0.001), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → SDBbot (25 neighbors, 25 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → TrickBot (57 neighbors, 57 edges)
           → Credential API Hooking (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 4/9: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่มาไว้บนเครื่องเป้าหมาย (Ingress Tool Transfer)...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่มาไว้บนเครื่องเป้าหมาย (Ingress Tool Transfer)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Neo-reGeorg (0.898), TYPEFRAME (0.583), Ingress Tool Transfer (0.469), Lateral Tool Transfer (0.288), Industroyer (0.234), cmd (0.203), Upload Malware (0.177), Upload Tool (0.021), ftp (0.007), BITS Jobs (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Neo-reGeorg (9 neighbors, 9 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → TYPEFRAME (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 5/9: สั่งให้โปรแกรมที่ดาวน์โหลดมาทำงานผ่านการเชื่อมต่อ RDP...
[RETRIEVE] Query: สั่งให้โปรแกรมที่ดาวน์โหลดมาทำงานผ่านการเชื่อมต่อ RDP...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pupy (0.183), ServHelper (0.068), Terminal Services DLL (0.034), Chimera (0.024), Axiom (0.016), Remote Service Session Hijacking (0.013), RDP Hijacking (0.012), Remote Desktop Protocol (0.006), Application Layer Protocol (0.002), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Pupy (43 neighbors, 43 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → ServHelper (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 6/9: รวบรวมข้อมูลระบบ ได้แก่ รุ่นระบบปฏิบัติการ ชื่อเครื่อง ชนิดหน่วยประมวลผล ขนาดหน่...
[RETRIEVE] Query: รวบรวมข้อมูลระบบ ได้แก่ รุ่นระบบปฏิบัติการ ชื่อเครื่อง ชนิดหน่วยประมวลผล ขนาดหน่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Azorult (0.685), Corona Updates (0.533), Systeminfo (0.510), ipconfig (0.006), Visual Basic (0.002), CrossRAT (0.001), Cobian RAT (0.001), The White Company (0.000), Cardinal RAT (0.000), 4H RAT (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Azorult (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Corona Updates (15 neighbors, 15 edges)
           → System Information Discovery (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 7/9: เรียกดูรายการโปรแกรมและบริการทั้งหมดที่ติดตั้งอยู่บนเครื่อง...
[RETRIEVE] Query: เรียกดูรายการโปรแกรมและบริการทั้งหมดที่ติดตั้งอยู่บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.742), Pallas (0.427), AbstractEmu (0.278), ipconfig (0.006), netstat (0.004), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → Pallas (15 neighbors, 15 edges)
           → Software Discovery (56 neighbors, 56 edges)
[RETRIEVE-QUOTA] Query 8/9: รวบรวมรายชื่อบัญชีผู้ใช้ภายในเครื่องและบัญชีผู้ใช้ในโดเมนขององค์กร...
[RETRIEVE] Query: รวบรวมรายชื่อบัญชีผู้ใช้ภายในเครื่องและบัญชีผู้ใช้ในโดเมนขององค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PoshC2 (0.312), PoshC2 (0.303), Cloud Account (0.032), Nltest (0.022), Local Account (0.013), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PoshC2 (35 neighbors, 35 edges)
           → Local Account (69 neighbors, 69 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 9/9: เรียกดูหมายเลขไอพี ตำแหน่งที่ตั้ง และรายละเอียดการตั้งค่าเครือข่ายของเครื่องผู้เ...
[RETRIEVE] Query: เรียกดูหมายเลขไอพี ตำแหน่งที่ตั้ง และรายละเอียดการตั้งค่าเครือข่ายของเครื่องผู้เ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ixeshe (0.763), Grandoreiro (0.568), Gather Victim Network Information (0.247), IP Addresses (0.224), Network Security Appliances (0.018), Cobian RAT (0.003), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ixeshe (16 neighbors, 16 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → Grandoreiro (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [60/100] retrieved=523 relevant=6 latency=43189ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 20 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบเดสก์...
[RETRIEVE] Query: เมื่อวันที่ 20 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบเดสก์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OSInfo (0.001), VOID MANTICORE (0.001), Wiarp (0.001), Adversary-in-the-Middle (0.000), Evil Twin (0.000), Ingress Tool Transfer (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), Input Injection (0.000), ARP Cache Poisoning (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OSInfo (11 neighbors, 11 edges)
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
[RETRIEVE-QUOTA] Query 2/7: ใช้ช่องโหว่ของไลบรารีบันทึกเหตุการณ์ที่ยังไม่ได้ติดตั้งแพตช์บนเครื่องแม่ข่ายที่เ...
[RETRIEVE] Query: ใช้ช่องโหว่ของไลบรารีบันทึกเหตุการณ์ที่ยังไม่ได้ติดตั้งแพตช์บนเครื่องแม่ข่ายที่เ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Initial Access (0.017), Exploit Public-Facing Application (0.009), Network Device Authentication (0.001), Socket Filters (0.001), NETWIRE (0.000), APT3 (0.000), Versa Director Zero Day Exploitation (0.000), Inception (0.000), Pass the Hash (0.000), Pass-The-Hash Toolkit (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Initial Access (22 neighbors, 22 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Network Device Authentication (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 3/7: วางไฟล์โปรแกรมที่ปลอมชื่อและรายละเอียดให้เหมือนบริการที่ถูกต้องของ Windows (Masq...
[RETRIEVE] Query: วางไฟล์โปรแกรมที่ปลอมชื่อและรายละเอียดให้เหมือนบริการที่ถูกต้องของ Windows (Masq...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT32 (0.776), Masquerading (0.753), Remsec (0.612), Masquerade Task or Service (0.411), RTM (0.393), Masquerade File Type (0.176), Sandworm Team (0.143), Match Legitimate Resource Name or Location (0.024), Malicious File (0.004), Active Setup (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Masquerading (81 neighbors, 81 edges)
           → APT32 (93 neighbors, 93 edges)
           → Masquerade Task or Service (94 neighbors, 94 edges)
[RETRIEVE-QUOTA] Query 4/7: ดัดแปลงเครื่องมือตรวจสอบเซสชันการล็อกอินแล้วฝังชุดคำสั่งอันตรายที่ถูกบีบอัดไว้ภา...
[RETRIEVE] Query: ดัดแปลงเครื่องมือตรวจสอบเซสชันการล็อกอินแล้วฝังชุดคำสั่งอันตรายที่ถูกบีบอัดไว้ภา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Skidmap (0.019), BUSHWALK (0.004), Credential API Hooking (0.002), Modify Authentication Process (0.002), Indrik Spider (0.002), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Skidmap (16 neighbors, 16 edges)
           → Pluggable Authentication Modules (10 neighbors, 10 edges)
           → BUSHWALK (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/7: ใช้เครื่องมือควบคุมเครื่องระยะไกลเพื่อดักบันทึกทุกปุ่มที่ผู้ใช้กดบนแป้นพิมพ์ (In...
[RETRIEVE] Query: ใช้เครื่องมือควบคุมเครื่องระยะไกลเพื่อดักบันทึกทุกปุ่มที่ผู้ใช้กดบนแป้นพิมพ์ (In...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ZxShell (0.879), Keylogging (0.359), PlugX (0.264), Fysbis (0.224), Input Capture (0.154), Empire (0.113), Screen Capture (0.110), Web Portal Capture (0.029), Video Capture (0.004), Audio Capture (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → ZxShell (37 neighbors, 37 edges)
           → Keylogging (160 neighbors, 160 edges)
           → PlugX (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 6/7: อัปโหลดไฟล์เพิ่มเติมเข้ามาบนเครื่องเป้าหมายและสั่งรันไฟล์เหล่านั้น...
[RETRIEVE] Query: อัปโหลดไฟล์เพิ่มเติมเข้ามาบนเครื่องเป้าหมายและสั่งรันไฟล์เหล่านั้น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DanBot (0.524), Lucifer (0.145), Forfiles (0.022), PsExec (0.016), Visual Basic (0.007), Create or Modify System Process (0.002), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → DanBot (15 neighbors, 15 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Lucifer (24 neighbors, 24 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 7/7: เปิดให้คนร้ายมองเห็นและควบคุมหน้าจอของเครื่องเป้าหมายจากระยะไกล (Remote Access S...
[RETRIEVE] Query: เปิดให้คนร้ายมองเห็นและควบคุมหน้าจอของเครื่องเป้าหมายจากระยะไกล (Remote Access S...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: gh0st RAT (0.649), Escobar (0.528), BRATA (0.366), Remote Access Tools (0.220), RemoteUtilities (0.215), User Guidance (0.195), RDFSNIFFER (0.115), Medusa Group (0.109), RemoteCMD (0.055), Machete (0.022)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Escobar (16 neighbors, 16 edges)
           → Remote Access Software (5 neighbors, 5 edges)
           → gh0st RAT (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [61/100] retrieved=372 relevant=4 latency=44661ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 5 เมษายน 2567 บริษัทผู้ให้บริการระบบสารสนเทศแห่งหนึ่งแจ้งความว่าเครื...
[RETRIEVE] Query: เมื่อวันที่ 5 เมษายน 2567 บริษัทผู้ให้บริการระบบสารสนเทศแห่งหนึ่งแจ้งความว่าเครื...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.045), Cobalt Strike (0.003), ServHelper (0.001), SSH Hijacking (0.000), SSH Authorized Keys (0.000), DCHSpy (0.000), SSH (0.000), P.A.S. Webshell (0.000), Forced Authentication (0.000), Internal Spearphishing (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → SSH (33 neighbors, 33 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] Query 2/8: ล็อกอินเข้าเครื่องแม่ข่ายเว็บผ่าน SSH ด้วยบัญชีที่ถูกต้อง (Valid Accounts)...
[RETRIEVE] Query: ล็อกอินเข้าเครื่องแม่ข่ายเว็บผ่าน SSH ด้วยบัญชีที่ถูกต้อง (Valid Accounts)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH (0.654), UNC3886 (0.578), Linux Rabbit (0.362), Kinsing (0.304), Remote Services (0.175), SSH Authorized Keys (0.104), SSH Hijacking (0.042), Remote Service Session Hijacking (0.035), Direct Cloud VM Connections (0.005), Modify Authentication Process (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SSH (33 neighbors, 33 edges)
           → UNC3886 (58 neighbors, 58 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] Query 3/8: ส่งไฟล์สคริปต์ภาษา PHP จากเครื่องภายนอกเข้ามาวางบนเครื่องแม่ข่าย (Ingress Tool T...
[RETRIEVE] Query: ส่งไฟล์สคริปต์ภาษา PHP จากเครื่องภายนอกเข้ามาวางบนเครื่องแม่ข่าย (Ingress Tool T...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ingress Tool Transfer (0.549), PHPsert (0.454), cmd (0.414), Lateral Tool Transfer (0.269), Industroyer (0.268), ftp (0.024), Upload Malware (0.017), Upload Tool (0.004), BITS Jobs (0.002), Impacket (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → PHPsert (7 neighbors, 7 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 4/8: ติดตั้งสคริปต์ PHP เป็นหน้าเว็บรับคำสั่งเพื่อคงการเข้าถึงเครื่อง (Web Shell)...
[RETRIEVE] Query: ติดตั้งสคริปต์ PHP เป็นหน้าเว็บรับคำสั่งเพื่อคงการเข้าถึงเครื่อง (Web Shell)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Web Shell (0.750), Operation Digital Eye (0.561), PHPsert (0.395), PHPsert (0.218), P.A.S. Webshell (0.207), P.A.S. Webshell (0.053), China Chopper (0.009), Netsh Helper DLL (0.008), Unix Shell Configuration Modification (0.002), SSH Hijacking (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Web Shell (71 neighbors, 71 edges)
           → Operation Digital Eye (26 neighbors, 26 edges)
           → PHPsert (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/8: ส่งคำสั่งผ่านหน้าเว็บเพื่อสั่งงานเครื่องแม่ข่ายจากระยะไกล (Command and Scripting...
[RETRIEVE] Query: ส่งคำสั่งผ่านหน้าเว็บเพื่อสั่งงานเครื่องแม่ข่ายจากระยะไกล (Command and Scripting...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CHOPSTICK (0.824), gh0st RAT (0.711), Network Device CLI (0.198), Mustang Panda (0.178), Command and Scripting Interpreter (0.158), Empire (0.117), netsh (0.061), Data from Local System (0.018), Indirect Command Execution (0.018), Native API (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → CHOPSTICK (20 neighbors, 20 edges)
           → Command and Scripting Interpreter (68 neighbors, 68 edges)
           → gh0st RAT (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 6/8: เรียกดูชื่อบัญชีผู้ใช้ที่สคริปต์กำลังทำงานอยู่ (System Owner/User Discovery)...
[RETRIEVE] Query: เรียกดูชื่อบัญชีผู้ใช้ที่สคริปต์กำลังทำงานอยู่ (System Owner/User Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Owner/User Discovery (0.613), HAPPYWORK (0.479), PowerDuke (0.469), Kimsuky (0.312), APT3 (0.096), Account Discovery (0.033), Local Account (0.003), Process Discovery (0.003), System Information Discovery (0.003), System Location Discovery (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → HAPPYWORK (4 neighbors, 4 edges)
           → PowerDuke (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 7/8: เรียกดูรายละเอียดระบบปฏิบัติการที่ติดตั้งบนเครื่องแม่ข่าย (System Information Di...
[RETRIEVE] Query: เรียกดูรายละเอียดระบบปฏิบัติการที่ติดตั้งบนเครื่องแม่ข่าย (System Information Di...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Systeminfo (0.469), OSInfo (0.440), cmd (0.338), RATANKBA (0.300), System Information Discovery (0.184), System Network Configuration Discovery (0.030), System Owner/User Discovery (0.005), System Network Connections Discovery (0.005), Process Discovery (0.002), Device Driver Discovery (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Systeminfo (14 neighbors, 14 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → OSInfo (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 8/8: ไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่าย (File and Directory Discovery)...
[RETRIEVE] Query: ไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่าย (File and Directory Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DynoWiper (0.795), File and Directory Discovery (0.602), SILENTTRINITY (0.531), Forfiles (0.236), FLASHFLOOD (0.189), Network Share Discovery (0.116), Cloud Storage Object Discovery (0.085), dsquery (0.011), System Information Discovery (0.004), System Owner/User Discovery (0.004)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DynoWiper (10 neighbors, 10 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [62/100] retrieved=680 relevant=5 latency=33575ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 30 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเอกสารราชการในเครื่องคอมพ...
[RETRIEVE] Query: เมื่อวันที่ 30 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเอกสารราชการในเครื่องคอมพ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.112), Koadic (0.036), P.A.S. Webshell (0.002), RDP Hijacking (0.002), Remote Desktop Protocol (0.001), ZxShell (0.001), File Deletion (0.000), Ingress Tool Transfer (0.000), System Script Proxy Execution (0.000), Remote Services (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Koadic (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 2/8: ลักลอบคัดลอกเอกสารราชการออกจากเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ (Data Exfiltratio...
[RETRIEVE] Query: ลักลอบคัดลอกเอกสารราชการออกจากเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ (Data Exfiltratio...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Goopy (0.034), Exfiltration Over Alternative Protocol (0.033), Exfiltration (0.027), InnaputRAT (0.021), Exfiltration Over Physical Medium (0.019), Manjusaka (0.018), Data from Network Shared Drive (0.015), Octopus (0.011), Empire (0.006), Exbyte (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → Goopy (19 neighbors, 19 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 3/8: แก้ไขค่าในทะเบียนระบบเพื่อเปลี่ยนโปรแกรมเริ่มต้นที่เปิดไฟล์เอกสาร (File and Dire...
[RETRIEVE] Query: แก้ไขค่าในทะเบียนระบบเพื่อเปลี่ยนโปรแกรมเริ่มต้นที่เปิดไฟล์เอกสาร (File and Dire...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kimsuky (0.389), Change Default File Association (0.113), File and Directory Discovery (0.014), DynoWiper (0.005), SILENTTRINITY (0.004), Registry Run Keys / Startup Folder (0.003), Cloud Storage Object Discovery (0.001), System Information Discovery (0.000), Hidden Files and Directories (0.000), Container and Resource Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Kimsuky (150 neighbors, 150 edges)
           → Change Default File Association (7 neighbors, 7 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
[RETRIEVE-QUOTA] Query 4/8: อัปโหลด Web Shell ที่ดัดแปลงจากโครงการโอเพนซอร์ซไปยังเครื่องแม่ข่ายเพื่อคงการเข้...
[RETRIEVE] Query: อัปโหลด Web Shell ที่ดัดแปลงจากโครงการโอเพนซอร์ซไปยังเครื่องแม่ข่ายเพื่อคงการเข้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT28 (0.315), Web Shell (0.040), APT32 (0.034), P.A.S. Webshell (0.012), P.A.S. Webshell (0.006), China Chopper (0.002), Netsh Helper DLL (0.002), Caterpillar WebShell (0.001), SUPERNOVA (0.000), SSH Hijacking (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT28 (124 neighbors, 124 edges)
           → Web Shell (71 neighbors, 71 edges)
           → APT32 (93 neighbors, 93 edges)
[RETRIEVE-QUOTA] Query 5/8: ใช้ Web Shell อัปโหลด ดาวน์โหลด และลบไฟล์กับโฟลเดอร์บนเว็บไซต์...
[RETRIEVE] Query: ใช้ Web Shell อัปโหลด ดาวน์โหลด และลบไฟล์กับโฟลเดอร์บนเว็บไซต์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: P.A.S. Webshell (0.824), RAPIDPULSE (0.402), Web Shell (0.386), BUSHWALK (0.269), P.A.S. Webshell (0.193), Caterpillar WebShell (0.069), Netsh Helper DLL (0.063), China Chopper (0.053), SUPERNOVA (0.042), SSH Hijacking (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Web Shell (71 neighbors, 71 edges)
[RETRIEVE-QUOTA] Query 6/8: เพิ่มบัญชีผู้ดูแลระบบ Windows ใหม่ (Create Account)...
[RETRIEVE] Query: เพิ่มบัญชีผู้ดูแลระบบ Windows ใหม่ (Create Account)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: User Account Creation (0.024), Local Account (0.022), Carbanak (0.021), Cloud Account (0.008), User Account Control (0.006), AADInternals (0.002), Bypass User Account Control (0.001), User Account Management (0.001), UACMe (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Local Account (35 neighbors, 35 edges)
           → User Account Creation (0 neighbors, 0 edges)
           → Carbanak (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 7/8: เปิดใช้งาน Remote Desktop Protocol (RDP) เพื่อเข้าถึงเครื่องจากระยะไกล...
[RETRIEVE] Query: เปิดใช้งาน Remote Desktop Protocol (RDP) เพื่อเข้าถึงเครื่องจากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Desktop Protocol (0.630), RDP Hijacking (0.566), Carbanak (0.363), Koadic (0.328), SILENTTRINITY (0.292), Terminal Services DLL (0.226), Remote Desktop Software (0.098), Network Segmentation (0.059), Remote Access Tools (0.053), Remote Services (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Carbanak (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 8/8: หลบเลี่ยงกฎไฟร์วอลล์โดยแก้ไขการตั้งค่าไฟร์วอลล์ (Impair Defenses)...
[RETRIEVE] Query: หลบเลี่ยงกฎไฟร์วอลล์โดยแก้ไขการตั้งค่าไฟร์วอลล์ (Impair Defenses)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Disable or Modify System Firewall (0.149), Windows Host Firewall (0.095), User Guidance (0.053), Restrict Registry Permissions (0.036), System Partition Integrity (0.034), User Account Management (0.018), Network Device Firewall (0.017), Defense Impairment (0.008), Exploitation for Defense Impairment (0.003), Multi-Factor Authentication (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Disable or Modify System Firewall (38 neighbors, 38 edges)
           → Windows Host Firewall (23 neighbors, 23 edges)
           → User Guidance (49 neighbors, 49 edges)
           → Impair Defenses (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [63/100] retrieved=411 relevant=3 latency=40705ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 18 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกลุก...
[RETRIEVE] Query: เมื่อวันที่ 18 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกลุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN8 (0.002), POWRUNER (0.001), POWRUNER (0.000), Ingress Tool Transfer (0.000), Gamaredon Group (0.000), Winlogon Helper DLL (0.000), Named Pipe Metadata (0.000), Exploitation for Privilege Escalation (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 2/6: นำชื่อผู้ใช้และรหัสผ่านที่ค้นพบมาใช้เชื่อมต่อหน้าจอระยะไกลเข้าสู่เครื่องแม่ข่ายค...
[RETRIEVE] Query: นำชื่อผู้ใช้และรหัสผ่านที่ค้นพบมาใช้เชื่อมต่อหน้าจอระยะไกลเข้าสู่เครื่องแม่ข่ายค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RDP Hijacking (0.163), Remote Desktop Protocol (0.096), SDBbot (0.028), SILENTTRINITY (0.013), Play (0.007), Carbanak (0.006), Remote Access Tools (0.002), FRP (0.001), Rogue Domain Controller (0.000), DUSTTRAP (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → SDBbot (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 3/6: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่มาไว้บนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่มาไว้บนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AppDomainManager (0.021), BackConfig (0.009), BONDUPDATER (0.004), dsquery (0.002), BoomBox (0.001), Impacket (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → AppDomainManager (6 neighbors, 6 edges)
           → BackConfig (17 neighbors, 17 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 4/6: สั่งให้ไฟล์โปรแกรมที่ดาวน์โหลดทำงานบนเครื่องแม่ข่ายควบคุมโดเมนผ่านการเชื่อมต่อระ...
[RETRIEVE] Query: สั่งให้ไฟล์โปรแกรมที่ดาวน์โหลดทำงานบนเครื่องแม่ข่ายควบคุมโดเมนผ่านการเชื่อมต่อระ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT3 (0.036), BackConfig (0.010), RemoteCMD (0.010), Cobian RAT (0.004), dsquery (0.003), AppDomainManager (0.001), CrossRAT (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT3 (50 neighbors, 50 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → BackConfig (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 5/6: แก้ไขค่าใน Windows Registry ที่ควบคุมกระบวนการล็อกอินของ Windows...
[RETRIEVE] Query: แก้ไขค่าใน Windows Registry ที่ควบคุมกระบวนการล็อกอินของ Windows...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Registry Key Modification (0.179), LockBit 3.0 (0.073), Modify Registry (0.053), Credentials in Registry (0.035), Reg (0.021), WastedLocker (0.018), Active Setup (0.018), Registry Run Keys / Startup Folder (0.012), Query Registry (0.001), CHOPSTICK (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Windows Registry Key Modification (0 neighbors, 0 edges)
           → LockBit 3.0 (34 neighbors, 34 edges)
           → Modify Registry (177 neighbors, 177 edges)
[RETRIEVE-QUOTA] Query 6/6: เพิ่มชื่อไฟล์โปรแกรมของคนร้ายในค่า Windows Registry ให้ถูกเรียกทำงานทุกครั้งที่ผ...
[RETRIEVE] Query: เพิ่มชื่อไฟล์โปรแกรมของคนร้ายในค่า Windows Registry ให้ถูกเรียกทำงานทุกครั้งที่ผ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.969), RogueRobin (0.887), DarkComet (0.720), MuddyViper (0.521), Confucius (0.497), Logon Script (Windows) (0.150), Active Setup (0.059), Reg (0.012), Services Registry Permissions Weakness (0.006), Query Registry (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → RogueRobin (19 neighbors, 19 edges)
           → DarkComet (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [64/100] retrieved=223 relevant=3 latency=30740ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 24 กรกฎาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการสำรวจ...
[RETRIEVE] Query: เมื่อวันที่ 24 กรกฎาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการสำรวจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Net (0.018), menuPass (0.007), Remote System Discovery (0.004), System Network Connections Discovery (0.002), Process Discovery (0.000), FIN8 (0.000), Cloud Accounts (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Password Policies (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Net (50 neighbors, 50 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → menuPass (71 neighbors, 71 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
[RETRIEVE-QUOTA] Query 2/6: เปิดอ่านค่าในทะเบียนระบบของโปรแกรมเชื่อมต่อหน้าจอระยะไกลเพื่อค้นหาเครื่องปลายทาง...
[RETRIEVE] Query: เปิดอ่านค่าในทะเบียนระบบของโปรแกรมเชื่อมต่อหน้าจอระยะไกลเพื่อค้นหาเครื่องปลายทาง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: njRAT (0.361), Remote System Discovery (0.246), BitPaymer (0.185), System Network Connections Discovery (0.056), System Location Discovery (0.012), Wi-Fi Discovery (0.011), System Information Discovery (0.009), System Owner/User Discovery (0.008), Emotet (0.008), Machete (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → njRAT (40 neighbors, 40 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
           → BitPaymer (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 3/6: ใช้คำสั่งพื้นฐานของระบบผ่านหน้าต่างคำสั่ง (Command and Scripting Interpreter)...
[RETRIEVE] Query: ใช้คำสั่งพื้นฐานของระบบผ่านหน้าต่างคำสั่ง (Command and Scripting Interpreter)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Command and Scripting Interpreter (0.500), Empire (0.468), cmd (0.176), Mustang Panda (0.170), Systemctl (0.118), Data from Local System (0.073), Indirect Command Execution (0.037), Script Execution (0.031), MCMD (0.011), Native API (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Command and Scripting Interpreter (68 neighbors, 68 edges)
           → Empire (91 neighbors, 91 edges)
           → Mustang Panda (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] Query 4/6: เรียกดูรายละเอียดบัญชีผู้ใช้รายหนึ่งในโดเมนขององค์กร (Account Discovery)...
[RETRIEVE] Query: เรียกดูรายละเอียดบัญชีผู้ใช้รายหนึ่งในโดเมนขององค์กร (Account Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.036), Account Discovery (0.034), Domain Account (0.020), System Owner/User Discovery (0.011), Wi-Fi Discovery (0.008), Bazar (0.004), Domain Trust Discovery (0.002), TAINTEDSCRIBE (0.000), Discovery (0.000), OSInfo (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Account Discovery (18 neighbors, 18 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 5/6: เรียกดูรายชื่อสมาชิกของกลุ่มสิทธิ์ผู้ดูแลระบบฐานข้อมูลขององค์กร (Permission Grou...
[RETRIEVE] Query: เรียกดูรายชื่อสมาชิกของกลุ่มสิทธิ์ผู้ดูแลระบบฐานข้อมูลขององค์กร (Permission Grou...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Permission Groups Discovery (0.564), IcedID (0.555), APT3 (0.312), TrickBot (0.065), Local Groups (0.032), Cloud Groups (0.021), Domain Groups (0.014), Group Policy Discovery (0.007), System Owner/User Discovery (0.004), Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Permission Groups Discovery (18 neighbors, 18 edges)
           → IcedID (34 neighbors, 34 edges)
           → APT3 (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 6/6: สอบถามชื่อโดเมนเพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายเป้าหมาย (System Network Co...
[RETRIEVE] Query: สอบถามชื่อโดเมนเพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายเป้าหมาย (System Network Co...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DEADEYE (0.889), OSInfo (0.433), nbtstat (0.411), System Network Configuration Discovery (0.345), ifconfig (0.160), System Network Connections Discovery (0.034), System Location Discovery (0.022), ipconfig (0.020), System Owner/User Discovery (0.005), Data from Configuration Repository (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DEADEYE (13 neighbors, 13 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → OSInfo (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [65/100] retrieved=336 relevant=4 latency=27161ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 21 พฤศจิกายน 2565 บริษัทแห่งหนึ่งแจ้งความว่าข้อมูลในระบบถูกเข้ารหัสล...
[RETRIEVE] Query: เมื่อวันที่ 21 พฤศจิกายน 2565 บริษัทแห่งหนึ่งแจ้งความว่าข้อมูลในระบบถูกเข้ารหัสล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: INC Ransomware (0.034), ThiefQuest (0.018), Data Encrypted for Impact (0.003), Inhibit System Recovery (0.002), Evil Twin (0.000), ARP Cache Poisoning (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), Adversary-in-the-Middle (0.000), Clear Windows Event Logs (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → INC Ransomware (16 neighbors, 16 edges)
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → ThiefQuest (18 neighbors, 18 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] Query 2/9: เข้ารหัสข้อมูลทั้งหมดในระบบเพื่อทำให้ไม่สามารถกู้คืนได้ (Data Encrypted for Impa...
[RETRIEVE] Query: เข้ารหัสข้อมูลทั้งหมดในระบบเพื่อทำให้ไม่สามารถกู้คืนได้ (Data Encrypted for Impa...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Encrypted for Impact (0.959), Avaddon (0.694), SynAck (0.427), S.O.V.A. (0.333), Encrypt Sensitive Information (0.068), SDelete (0.039), Impact (0.038), Backup Software Discovery (0.038), Encrypted/Encoded File (0.015), Account Access Removal (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → Avaddon (17 neighbors, 17 edges)
           → SynAck (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 3/9: สั่งหยุดบริการ Volume Shadow Copy และลบสำเนาเงาของไฟล์ทั้งหมดเพื่อขัดขวางการกู้ค...
[RETRIEVE] Query: สั่งหยุดบริการ Volume Shadow Copy และลบสำเนาเงาของไฟล์ทั้งหมดเพื่อขัดขวางการกู้ค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HermeticWiper (0.748), Inhibit System Recovery (0.733), ROADSWEEP (0.231), Clop (0.204), Volume Deletion (0.002), /etc/passwd and /etc/shadow (0.001), Direct Volume Access (0.001), NTDS (0.000), Volume Creation (0.000), Volume Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → HermeticWiper (26 neighbors, 26 edges)
           → Service Stop (61 neighbors, 61 edges)
[RETRIEVE-QUOTA] Query 4/9: ลบไฟล์บันทึกเหตุการณ์ Windows ของระบบ ความปลอดภัย และแอปพลิเคชันผ่านหน้าต่างคำสั...
[RETRIEVE] Query: ลบไฟล์บันทึกเหตุการณ์ Windows ของระบบ ความปลอดภัย และแอปพลิเคชันผ่านหน้าต่างคำสั...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RansomHub (0.586), Clear Windows Event Logs (0.585), Mafalda (0.045), Wevtutil (0.015), cmd (0.010), Windows Registry Key Deletion (0.004), Windows Command Shell (0.001), Visual Basic (0.000), Samurai (0.000), Cobalt Group (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → RansomHub (21 neighbors, 21 edges)
           → Mafalda (37 neighbors, 37 edges)
[RETRIEVE-QUOTA] Query 5/9: แก้ไขค่า Windows Registry เพื่อลบฐานข้อมูลลายเซ็นไวรัส...
[RETRIEVE] Query: แก้ไขค่า Windows Registry เพื่อลบฐานข้อมูลลายเซ็นไวรัส...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WastedLocker (0.013), Windows Registry Key Modification (0.012), Modify Registry (0.011), ThreatNeedle (0.008), Reg (0.004), Reg (0.004), Credentials in Registry (0.003), Windows Registry Key Deletion (0.001), Query Registry (0.000), CHOPSTICK (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Modify Registry (177 neighbors, 177 edges)
           → WastedLocker (21 neighbors, 21 edges)
           → Windows Registry Key Modification (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 6/9: แก้ไขค่า Windows Registry เพื่อปิดการทำงานของโปรแกรมป้องกันไวรัสทั้งหมด...
[RETRIEVE] Query: แก้ไขค่า Windows Registry เพื่อปิดการทำงานของโปรแกรมป้องกันไวรัสทั้งหมด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LockBit 3.0 (0.101), MuddyViper (0.027), Modify Registry (0.013), Windows Registry Key Modification (0.009), Reg (0.004), Restrict Registry Permissions (0.001), Credentials in Registry (0.001), Query Registry (0.001), Windows Host Firewall (0.000), CHOPSTICK (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → LockBit 3.0 (34 neighbors, 34 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → MuddyViper (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 7/9: ลำเลียงข้อมูลบริษัทไปเก็บไว้ยังบริการรับฝากข้อมูลออนไลน์ (Exfiltration to Cloud ...
[RETRIEVE] Query: ลำเลียงข้อมูลบริษัทไปเก็บไว้ยังบริการรับฝากข้อมูลออนไลน์ (Exfiltration to Cloud ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration to Cloud Storage (0.799), ROKRAT (0.478), HAMMERTOSS (0.464), Transfer Data to Cloud Account (0.307), Empire (0.261), Data Staged (0.063), Exfiltration to Text Storage Sites (0.021), Exfiltration (0.015), Cloud Storage Creation (0.014), Archive Collected Data (0.013)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration to Cloud Storage (48 neighbors, 48 edges)
           → ROKRAT (31 neighbors, 31 edges)
           → HAMMERTOSS (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 8/9: นำโปรแกรมคัดลอกไฟล์เข้ามาในเครื่องเพื่อใช้ส่งข้อมูลไปยังบริการรับฝากข้อมูลออนไลน...
[RETRIEVE] Query: นำโปรแกรมคัดลอกไฟล์เข้ามาในเครื่องเพื่อใช้ส่งข้อมูลไปยังบริการรับฝากข้อมูลออนไลน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ftp (0.039), Ingress Tool Transfer (0.007), VERMIN (0.007), Lateral Tool Transfer (0.005), TYPEFRAME (0.004), Pupy (0.003), PsExec (0.002), Empire (0.002), Cherry Picker (0.001), Customer Relationship Management Software (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → ftp (10 neighbors, 10 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → VERMIN (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 9/9: วางไฟล์ข้อความเรียกค่าไถ่ในทุกโฟลเดอร์ที่ได้รับผลกระทบเพื่อข่มขู่ไม่ให้แก้ไข เปล...
[RETRIEVE] Query: วางไฟล์ข้อความเรียกค่าไถ่ในทุกโฟลเดอร์ที่ได้รับผลกระทบเพื่อข่มขู่ไม่ให้แก้ไข เปล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BlackByte (0.031), ThiefQuest (0.005), Data Encrypted for Impact (0.004), KernelCallbackTable (0.003), Template Injection (0.002), Change Default File Association (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → BlackByte (56 neighbors, 56 edges)
           → Internal Defacement (18 neighbors, 18 edges)
           → ThiefQuest (18 neighbors, 18 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [66/100] retrieved=170 relevant=6 latency=51613ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 21 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้...
[RETRIEVE] Query: เมื่อวันที่ 21 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Crimson (0.344), KeyBoy (0.155), PowerSploit (0.038), LaZagne (0.023), Unsecured Credentials (0.018), Password Managers (0.006), Registry Run Keys / Startup Folder (0.004), Credentials from Web Browsers (0.003), Credentials in Registry (0.002), Windows Credential Manager (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Crimson (32 neighbors, 32 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → KeyBoy (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 2/7: ฝังโปรแกรมขโมยรหัสผ่านลงในเครื่องคอมพิวเตอร์ของเจ้าหน้าที่...
[RETRIEVE] Query: ฝังโปรแกรมขโมยรหัสผ่านลงในเครื่องคอมพิวเตอร์ของเจ้าหน้าที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AuTo Stealer (0.165), Skeleton Key (0.035), Trojan.Karagany (0.026), Net Crawler (0.016), gsecdump (0.006), Prikormka (0.003), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → AuTo Stealer (11 neighbors, 11 edges)
           → Skeleton Key (2 neighbors, 2 edges)
           → Trojan.Karagany (23 neighbors, 23 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 3/7: เพิ่มรายการเรียกใช้งานโปรแกรมใน Registry Run Key เพื่อให้โปรแกรมทำงานทุกครั้งที่...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานโปรแกรมใน Registry Run Key เพื่อให้โปรแกรมทำงานทุกครั้งที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.935), DarkComet (0.462), Boot or Logon Autostart Execution (0.337), RunningRAT (0.223), LockBit 2.0 (0.200), Active Setup (0.195), Ursnif (0.170), Office Test (0.076), Windows Registry Key Modification (0.005), Windows Registry Key Access (0.004)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → DarkComet (21 neighbors, 21 edges)
           → Boot or Logon Autostart Execution (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 4/7: วางโปรแกรมไว้ในโฟลเดอร์เริ่มต้นระบบเพื่อให้โปรแกรมทำงานอัตโนมัติเมื่อผู้ใช้ล็อกอ...
[RETRIEVE] Query: วางโปรแกรมไว้ในโฟลเดอร์เริ่มต้นระบบเพื่อให้โปรแกรมทำงานอัตโนมัติเมื่อผู้ใช้ล็อกอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.889), XDG Autostart Entries (0.660), MarkiRAT (0.627), Boot or Logon Autostart Execution (0.280), DarkComet (0.252), Visual Basic (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → XDG Autostart Entries (15 neighbors, 15 edges)
           → MarkiRAT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 5/7: หลบเลี่ยงกลไกยืนยันก่อนยกระดับสิทธิ์ (UAC Bypass) เพื่อให้โปรแกรมทำงานด้วยสิทธิ์...
[RETRIEVE] Query: หลบเลี่ยงกลไกยืนยันก่อนยกระดับสิทธิ์ (UAC Bypass) เพื่อให้โปรแกรมทำงานด้วยสิทธิ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bypass User Account Control (0.885), User Account Control (0.290), Abuse Elevation Control Mechanism (0.200), RCSession (0.144), Sliver (0.107), Elevated Execution with Prompt (0.062), Pass the Hash (0.007), UACMe (0.006), Multi-Factor Authentication (0.001), Mark-of-the-Web Bypass (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bypass User Account Control (70 neighbors, 70 edges)
           → User Account Control (7 neighbors, 7 edges)
           → Abuse Elevation Control Mechanism (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 6/7: อ่าน Credentials from Web Browsers ซึ่งเป็นชื่อผู้ใช้และรหัสผ่านที่เว็บเบราว์เซอ...
[RETRIEVE] Query: อ่าน Credentials from Web Browsers ซึ่งเป็นชื่อผู้ใช้และรหัสผ่านที่เว็บเบราว์เซอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.981), PLEAD (0.764), LaZagne (0.508), SUGARDUMP (0.357), XLoader (0.330), Windows Credential Manager (0.025), Credentials from Password Stores (0.020), Web Credential Usage (0.019), Forge Web Credentials (0.016), Browser Information Discovery (0.014)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → PLEAD (16 neighbors, 16 edges)
           → LaZagne (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งชื่อผู้ใช้และรหัสผ่านที่ขโมยได้ออกไปยังคนร้าย (exfiltration)...
[RETRIEVE] Query: ส่งชื่อผู้ใช้และรหัสผ่านที่ขโมยได้ออกไปยังคนร้าย (exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration (0.171), Exfiltration Over Other Network Medium (0.093), Exfiltration Over Unencrypted Non-C2 Protocol (0.083), Exfiltration Over Alternative Protocol (0.082), Exfiltration Over C2 Channel (0.076), Exfiltration Over Physical Medium (0.051), HAMMERTOSS (0.047), Empire (0.011), APT28 Nearest Neighbor Campaign (0.009), Exodus (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration (19 neighbors, 19 edges)
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [67/100] retrieved=385 relevant=3 latency=34643ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 11 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าข้อมูลที่รวบ...
[RETRIEVE] Query: เมื่อวันที่ 11 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าข้อมูลที่รวบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MobileOrder (0.002), WellMail (0.002), Ingress Tool Transfer (0.001), Data from Local System (0.000), Windows Management Instrumentation (0.000), FIN8 (0.000), Exploitation of Remote Services (0.000), Pikabot (0.000), Cloud Accounts (0.000), Browser Extensions (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → MobileOrder (8 neighbors, 8 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 2/5: เปิดการเชื่อมต่อแบบโต้ตอบไปยังเครื่องแม่ข่ายภายนอกองค์กร...
[RETRIEVE] Query: เปิดการเชื่อมต่อแบบโต้ตอบไปยังเครื่องแม่ข่ายภายนอกองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Proxy (0.001), SSH (0.001), metaMain (0.001), Hikit (0.001), Responder (0.001), Non-Application Layer Protocol (0.000), Out-of-Band Communications Channel (0.000), Cobalt Strike (0.000), Cobalt Strike (0.000), Out1 (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → External Proxy (27 neighbors, 27 edges)
           → SSH (33 neighbors, 33 edges)
           → metaMain (29 neighbors, 29 edges)
           → Non-Application Layer Protocol (114 neighbors, 114 edges)
[RETRIEVE-QUOTA] Query 3/5: คัดลอกข้อมูลที่รวบรวมไว้ผ่านช่องทางเข้ารหัสไปเก็บบนเครื่องปลายทางภายนอกองค์กร...
[RETRIEVE] Query: คัดลอกข้อมูลที่รวบรวมไว้ผ่านช่องทางเข้ารหัสไปเก็บบนเครื่องปลายทางภายนอกองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over C2 Channel (0.004), Exfiltration Over Alternative Protocol (0.004), AADInternals (0.003), Dok (0.001), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), 4H RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → AADInternals (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 4/5: ใช้เครื่องมือสั่งงานระยะไกลสร้างบริการของระบบบนเครื่องปลายทางในเครือข่าย...
[RETRIEVE] Query: ใช้เครื่องมือสั่งงานระยะไกลสร้างบริการของระบบบนเครื่องปลายทางในเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Access Hardware (0.498), RemoteCMD (0.403), RemoteCMD (0.240), Remote Access Tools (0.173), QakBot (0.138), xCmd (0.113), netsh (0.015), Emissary (0.011), Software Deployment Tools (0.007), Network Device CLI (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Remote Access Hardware (4 neighbors, 4 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
[RETRIEVE-QUOTA] Query 5/5: ใช้ Windows Management Instrumentation (WMI) สั่งให้กระบวนการทำงานบนเครื่องปลายท...
[RETRIEVE] Query: ใช้ Windows Management Instrumentation (WMI) สั่งให้กระบวนการทำงานบนเครื่องปลายท...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: EKANS (0.576), Empire (0.479), Windows Management Instrumentation (0.389), Koadic (0.200), Windows Management Instrumentation Event Subscription (0.044), Windows Remote Management (0.011), Windows Command Shell (0.004), WMI Creation (0.002), Service Execution (0.001), Scheduled Task (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → EKANS (9 neighbors, 9 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Empire (91 neighbors, 91 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [68/100] retrieved=696 relevant=3 latency=28005ms
[RETRIEVE-QUOTA] Query 1/4: เมื่อวันที่ 17 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดเค...
[RETRIEVE] Query: เมื่อวันที่ 17 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดเค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.054), Bankshot (0.049), APT-C-36 (0.030), Data Encrypted for Impact (0.014), APT-C-36 (0.011), Ursnif (0.008), Ingress Tool Transfer (0.000), Input Injection (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
[RETRIEVE-QUOTA] Query 2/4: ใช้ไฟล์แบตช์นำไฟล์สคริปต์ไปวางบนเครื่องของผู้เสียหายหลายเครื่อง...
[RETRIEVE] Query: ใช้ไฟล์แบตช์นำไฟล์สคริปต์ไปวางบนเครื่องของผู้เสียหายหลายเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.014), TONESHELL (0.013), Lateral Tool Transfer (0.008), Hannotog (0.006), Ingress Tool Transfer (0.005), Pupy (0.004), Data Encrypted for Impact (0.003), Input Injection (0.002), Code Repositories (0.001), Compromise Host Software Binary (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → TONESHELL (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 3/4: ลบ Windows Event Logs จำนวนมากทั้งบันทึกเหตุการณ์ระบบ แอปพลิเคชัน และความปลอดภัย...
[RETRIEVE] Query: ลบ Windows Event Logs จำนวนมากทั้งบันทึกเหตุการณ์ระบบ แอปพลิเคชัน และความปลอดภัย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Clear Windows Event Logs (0.947), RansomHub (0.919), Mafalda (0.656), Disable or Modify Windows Event Log (0.624), BlackCat (0.612), Qilin (0.405), Windows Registry Key Deletion (0.057), Windows Registry Key Modification (0.014), Service Creation (0.006), Active Directory Object Deletion (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → RansomHub (21 neighbors, 21 edges)
           → Disable or Modify Windows Event Log (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 4/4: ติดตั้งซอฟต์แวร์ควบคุมเครื่องระยะไกลที่มีจำหน่ายทั่วไปเพื่อเข้าถึงเครื่องและคงกา...
[RETRIEVE] Query: ติดตั้งซอฟต์แวร์ควบคุมเครื่องระยะไกลที่มีจำหน่ายทั่วไปเพื่อเข้าถึงเครื่องและคงกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Execution Prevention (0.147), Execution Prevention (0.078), Remote Access Hardware (0.029), Cobian RAT (0.023), Remote Desktop Software (0.013), Remote Access Tools (0.012), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Execution Prevention (79 neighbors, 79 edges)
           → Remote Desktop Software (21 neighbors, 21 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] 11 vectors (quota 3/query), 8 subgraphs from 4 queries
  [69/100] retrieved=759 relevant=3 latency=26563ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 20 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการเชื่...
[RETRIEVE] Query: เมื่อวันที่ 20 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการเชื่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.007), Bankshot (0.003), FIN8 (0.001), Salesforce Data Exfiltration (0.000), DNS (0.000), FrostyGoop Incident (0.000), Valid Accounts (0.000), Domain Accounts (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] Query 2/5: ใช้ DNS Tunneling ห่อหุ้มข้อมูลคำสั่งสั่งการผ่านการสอบถามชื่อโดเมน...
[RETRIEVE] Query: ใช้ DNS Tunneling ห่อหุ้มข้อมูลคำสั่งสั่งการผ่านการสอบถามชื่อโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BONDUPDATER (0.356), Cobalt Strike (0.326), DNS (0.132), Kevin (0.025), DNS Server (0.019), Domain Fronting (0.014), DNS Server (0.011), DNS/Passive DNS (0.007), Protocol Tunneling (0.005), IDE Tunneling (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → BONDUPDATER (8 neighbors, 8 edges)
           → DNS (60 neighbors, 60 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
           → Protocol Tunneling (46 neighbors, 46 edges)
[RETRIEVE-QUOTA] Query 3/5: รันคำสั่งตรวจสอบสถานะเซสชันบนเครื่องปลายทางเพื่อดูว่าผู้บริหารฝ่ายการเงินล็อกอิน...
[RETRIEVE] Query: รันคำสั่งตรวจสอบสถานะเซสชันบนเครื่องปลายทางเพื่อดูว่าผู้บริหารฝ่ายการเงินล็อกอิน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: StrongPity (0.019), FIN8 (0.012), AsyncRAT (0.002), Boot or Logon Initialization Scripts (0.001), Qilin (0.001), RCSession (0.001), System Owner/User Discovery (0.000), KernelCallbackTable (0.000), RDP Hijacking (0.000), User Account Control (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → StrongPity (28 neighbors, 28 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → FIN8 (47 neighbors, 47 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
[RETRIEVE-QUOTA] Query 4/5: อัปโหลดไฟล์โปรแกรมและไฟล์สคริปต์ไปวางบนเครื่องของผู้บริหาร (Ingress Tool Transfe...
[RETRIEVE] Query: อัปโหลดไฟล์โปรแกรมและไฟล์สคริปต์ไปวางบนเครื่องของผู้บริหาร (Ingress Tool Transfe...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteUtilities (0.589), Ingress Tool Transfer (0.355), Industroyer (0.279), Lateral Tool Transfer (0.249), cmd (0.204), Upload Malware (0.118), PsExec (0.013), ftp (0.012), Upload Tool (0.011), BITS Jobs (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteUtilities (5 neighbors, 5 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 5/5: ตั้งชื่อไฟล์โปรแกรมและสคริปต์ให้ดูเหมือนตัวปรับปรุงซอฟต์แวร์ทั่วไป (Masquerading...
[RETRIEVE] Query: ตั้งชื่อไฟล์โปรแกรมและสคริปต์ให้ดูเหมือนตัวปรับปรุงซอฟต์แวร์ทั่วไป (Masquerading...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: UPSTYLE (0.804), Masquerading (0.599), Execution Prevention (0.463), Sandworm Team (0.236), Masquerade File Type (0.108), User Training (0.013), Software Packing (0.008), Masquerade Account Name (0.004), Malicious File (0.003), Runtime Data Manipulation (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → UPSTYLE (13 neighbors, 13 edges)
           → Masquerading (81 neighbors, 81 edges)
           → Execution Prevention (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [70/100] retrieved=260 relevant=3 latency=24941ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 19 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Query: เมื่อวันที่ 19 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PUNCHTRACK (0.035), RawPOS (0.001), Exfiltration to Text Storage Sites (0.000), FIN8 (0.000), Hijack Execution Flow (0.000), Event Triggered Execution (0.000), Password Managers (0.000), Pikabot (0.000), Process Injection (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PUNCHTRACK (4 neighbors, 4 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → RawPOS (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 2/5: สั่งคำสั่งผ่านหน้าต่างคำสั่งเพื่อเพิ่มโปรแกรมของคนร้ายใน Registry Run Keys ให้ทำ...
[RETRIEVE] Query: สั่งคำสั่งผ่านหน้าต่างคำสั่งเพื่อเพิ่มโปรแกรมของคนร้ายใน Registry Run Keys ให้ทำ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DarkComet (0.692), Registry Run Keys / Startup Folder (0.358), Ursnif (0.209), LockBit 2.0 (0.097), Logon Script (Windows) (0.041), Boot or Logon Autostart Execution (0.032), Active Setup (0.011), Windows Registry Key Modification (0.001), Windows Registry Key Access (0.001), Port Monitors (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DarkComet (21 neighbors, 21 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → Ursnif (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 3/5: สั่งคำสั่งผ่านหน้าต่างคำสั่งเพื่อสร้าง Scheduled Task เรียกโปรแกรมของคนร้ายเป็นก...
[RETRIEVE] Query: สั่งคำสั่งผ่านหน้าต่างคำสั่งเพื่อสร้าง Scheduled Task เรียกโปรแกรมของคนร้ายเป็นก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: POWERSTATS (0.453), Tarrask (0.195), Confucius (0.097), Scheduled Task (0.035), Scheduled Task/Job (0.027), schtasks (0.014), Trap (0.012), schtasks (0.010), KernelCallbackTable (0.002), Masquerade Task or Service (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → POWERSTATS (28 neighbors, 28 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Tarrask (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/5: รวบรวมข้อมูลบัตรชำระเงินจากเครื่องรับชำระเงิน...
[RETRIEVE] Query: รวบรวมข้อมูลบัตรชำระเงินจากเครื่องรับชำระเงิน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FrameworkPOS (0.094), RawPOS (0.079), FrameworkPOS (0.053), FluBot (0.016), FIN6 (0.009), Response Metadata (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → FrameworkPOS (6 neighbors, 6 edges)
           → RawPOS (6 neighbors, 6 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 5/5: ใช้สคริปต์ลำเลียงข้อมูลบัตรออกไปภายนอกโดยซุกไว้ในคำขอ DNS ที่ทยอยส่งออกทีละน้อย ...
[RETRIEVE] Query: ใช้สคริปต์ลำเลียงข้อมูลบัตรออกไปภายนอกโดยซุกไว้ในคำขอ DNS ที่ทยอยส่งออกทีละน้อย ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FrameworkPOS (0.336), Exfiltration Over Alternative Protocol (0.164), C0017 (0.132), Exfiltration Over Other Network Medium (0.108), Exfiltration (0.096), Exfiltration Over Unencrypted Non-C2 Protocol (0.084), APT32 (0.083), Exfiltration Over Web Service (0.029), Exfiltration to Code Repository (0.012), DNS (0.003)
[RETRIEVE] Graph expansion: 4 subgraphs
           → FrameworkPOS (6 neighbors, 6 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → C0017 (36 neighbors, 36 edges)
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [71/100] retrieved=549 relevant=3 latency=22607ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 4 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Query: เมื่อวันที่ 4 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.272), Suckfly (0.088), pwdump (0.087), Windows Credential Editor (0.069), OS Credential Dumping (0.053), BlackByte (0.036), Credential Access Protection (0.012), Credential Access Protection (0.004), Credentials In Files (0.001), Credential Access (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Suckfly (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 2/6: สั่งลบไฟล์ที่รวบรวมพักไว้บนเครื่องอย่างถาวรโดยเขียนทับพื้นที่บนดิสก์เพื่อป้องกัน...
[RETRIEVE] Query: สั่งลบไฟล์ที่รวบรวมพักไว้บนเครื่องอย่างถาวรโดยเขียนทับพื้นที่บนดิสก์เพื่อป้องกัน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SDelete (0.074), Volume Deletion (0.019), POWERSTATS (0.006), LiteDuke (0.006), Disk Wipe (0.003), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → SDelete (7 neighbors, 7 edges)
           → Volume Deletion (0 neighbors, 0 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → File Deletion (310 neighbors, 310 edges)
[RETRIEVE-QUOTA] Query 3/6: รันเครื่องมือ Credential Dumping เพื่อเก็บรวบรวมรหัสผ่านของบัญชีผู้ใช้บนเครื่อง...
[RETRIEVE] Query: รันเครื่องมือ Credential Dumping เพื่อเก็บรวบรวมรหัสผ่านของบัญชีผู้ใช้บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OS Credential Dumping (0.506), MgBot (0.459), Windows Credential Editor (0.438), Axiom (0.224), Poseidon Group (0.215), pwdump (0.212), pwdump (0.181), Credential Access (0.156), Credentials In Files (0.114), Credential Access Protection (0.048)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → MgBot (18 neighbors, 18 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/6: สั่งรีสตาร์ตเครื่องเพื่อกระตุ้นรายการที่ฝังไว้ใน Windows Registry ให้ทำงาน...
[RETRIEVE] Query: สั่งรีสตาร์ตเครื่องเพื่อกระตุ้นรายการที่ฝังไว้ใน Windows Registry ให้ทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Winnti for Windows (0.030), Registry Run Keys / Startup Folder (0.020), Seasalt (0.006), Credentials in Registry (0.006), Reg (0.005), Modify Registry (0.005), Active Setup (0.005), Query Registry (0.003), Logon Script (Windows) (0.003), Reg (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Winnti for Windows (24 neighbors, 24 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 5/6: ฝังรายการใน Windows Registry เพื่อคงการทำงานและเรียกไฟล์ของคนร้าย...
[RETRIEVE] Query: ฝังรายการใน Windows Registry เพื่อคงการทำงานและเรียกไฟล์ของคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ryuk (0.117), Windows Service (0.065), Gazer (0.044), Modify Registry (0.040), Registry Run Keys / Startup Folder (0.036), Active Setup (0.023), Query Registry (0.015), CHOPSTICK (0.010), Credentials in Registry (0.004), Reg (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ryuk (24 neighbors, 24 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Windows Service (150 neighbors, 150 edges)
[RETRIEVE-QUOTA] Query 6/6: ใช้โปรแกรมช่วยเรียกไลบรารีที่มีลายเซ็นถูกต้องของ Windows เพื่อเรียกไฟล์ของคนร้าย...
[RETRIEVE] Query: ใช้โปรแกรมช่วยเรียกไลบรารีที่มีลายเซ็นถูกต้องของ Windows เพื่อเรียกไฟล์ของคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: EnvyScout (0.735), Rundll32 (0.571), System Binary Proxy Execution (0.510), APT38 (0.469), System Script Proxy Execution (0.358), Regsvr32 (0.299), Lazarus Group (0.156), Trusted Developer Utilities Proxy Execution (0.025), Privileged Account Management (0.020), Verclsid (0.008)
[RETRIEVE] Graph expansion: 3 subgraphs
           → EnvyScout (15 neighbors, 15 edges)
           → Rundll32 (106 neighbors, 106 edges)
           → System Binary Proxy Execution (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [72/100] retrieved=391 relevant=3 latency=35232ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 26 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเต...
[RETRIEVE] Query: เมื่อวันที่ 26 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WINDSHIELD (0.012), BackConfig (0.001), Query Registry (0.001), FIN8 (0.000), Process Discovery (0.000), Password Guessing (0.000), Exfiltration to Text Storage Sites (0.000), System Language Discovery (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → WINDSHIELD (6 neighbors, 6 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → BackConfig (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 2/8: เรียกดูรายการโปรแกรมหรือโพรเซสที่กำลังทำงานบนเครื่องผ่านฟังก์ชันระบบและคำสั่งในห...
[RETRIEVE] Query: เรียกดูรายการโปรแกรมหรือโพรเซสที่กำลังทำงานบนเครื่องผ่านฟังก์ชันระบบและคำสั่งในห...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.845), VERMIN (0.715), Process Discovery (0.550), Tasklist (0.364), Taidoor (0.317), KillDisk (0.152), System Information Discovery (0.022), System Owner/User Discovery (0.018), System Network Connections Discovery (0.011), Discovery (0.009)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → VERMIN (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 3/8: เรียกดูรายการบริการเบื้องหลังที่กำลังทำงานบนเครื่อง (System Services Discovery)...
[RETRIEVE] Query: เรียกดูรายการบริการเบื้องหลังที่กำลังทำงานบนเครื่อง (System Services Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.611), System Service Discovery (0.261), Ixeshe (0.134), SharkBot (0.026), Network Service Discovery (0.010), System Information Discovery (0.005), System Owner/User Discovery (0.004), Process Discovery (0.004), System Location Discovery (0.002), DnsSystem (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → System Service Discovery (71 neighbors, 71 edges)
           → Ixeshe (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/8: เรียกดูรายละเอียดการตั้งค่าของระบบปฏิบัติการที่ติดตั้งอยู่ (System Information D...
[RETRIEVE] Query: เรียกดูรายละเอียดการตั้งค่าของระบบปฏิบัติการที่ติดตั้งอยู่ (System Information D...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Systeminfo (0.587), System Network Configuration Discovery (0.480), cmd (0.399), RATANKBA (0.320), SYSCON (0.317), System Information Discovery (0.203), System Time Discovery (0.042), System Owner/User Discovery (0.007), Process Discovery (0.001), Device Driver Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Systeminfo (14 neighbors, 14 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] Query 5/8: แจกแจงรายชื่อสมาชิกกลุ่มผู้ดูแลระบบบนเครื่องเป้าหมาย (Permission Groups Discover...
[RETRIEVE] Query: แจกแจงรายชื่อสมาชิกกลุ่มผู้ดูแลระบบบนเครื่องเป้าหมาย (Permission Groups Discover...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Permission Groups Discovery (0.370), APT3 (0.219), MURKYTOP (0.129), APT41 (0.127), TrickBot (0.104), Local Groups (0.047), Domain Groups (0.038), System Owner/User Discovery (0.012), Group Policy Discovery (0.009), Discovery (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Permission Groups Discovery (18 neighbors, 18 edges)
           → APT3 (50 neighbors, 50 edges)
           → MURKYTOP (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 6/8: แจกแจงรายชื่อสมาชิกกลุ่มผู้ดูแลระบบบนเครื่องแม่ข่ายควบคุมโดเมนและในระดับโดเมนองค...
[RETRIEVE] Query: แจกแจงรายชื่อสมาชิกกลุ่มผู้ดูแลระบบบนเครื่องแม่ข่ายควบคุมโดเมนและในระดับโดเมนองค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HAFNIUM (0.444), Domain Groups (0.313), Group Policy Discovery (0.069), Permission Groups Discovery (0.066), BADHATCH (0.050), Poseidon Group (0.049), Domain Trust Discovery (0.017), Poseidon Group (0.013), Domain Account (0.012), System Owner/User Discovery (0.008)
[RETRIEVE] Graph expansion: 3 subgraphs
           → HAFNIUM (50 neighbors, 50 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
           → Domain Groups (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] Query 7/8: แจกแจงรายชื่อบัญชีผู้ใช้ในโดเมนและเรียกดูรายละเอียดบัญชีที่สนใจ (Account Discove...
[RETRIEVE] Query: แจกแจงรายชื่อบัญชีผู้ใช้ในโดเมนและเรียกดูรายละเอียดบัญชีที่สนใจ (Account Discove...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Account Discovery (0.341), CrackMapExec (0.318), Domain Account (0.224), PoshC2 (0.184), System Owner/User Discovery (0.054), Wi-Fi Discovery (0.010), Domain Trust Discovery (0.009), Discovery (0.000), TAINTEDSCRIBE (0.000), OSInfo (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Account Discovery (18 neighbors, 18 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 8/8: เปิดอ่านค่า Registry ที่กำหนดนโยบายความปลอดภัยของเครื่องเพื่อตรวจสอบการแสดงหน้าต...
[RETRIEVE] Query: เปิดอ่านค่า Registry ที่กำหนดนโยบายความปลอดภัยของเครื่องเพื่อตรวจสอบการแสดงหน้าต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: User Account Control (0.382), Windows Registry Key Access (0.103), Operating System Configuration (0.077), Operating System Configuration (0.070), Operating System Configuration (0.063), Bypass User Account Control (0.036), Query Registry (0.032), Credentials in Registry (0.022), LockBit 2.0 (0.022), Modify Registry (0.004)
[RETRIEVE] Graph expansion: 4 subgraphs
           → User Account Control (7 neighbors, 7 edges)
           → Windows Registry Key Access (0 neighbors, 0 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → Account Discovery (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [73/100] retrieved=581 relevant=6 latency=32796ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 4 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ข...
[RETRIEVE] Query: เมื่อวันที่ 4 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ข...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ursnif (0.038), NetTraveler (0.014), TrickBot (0.012), APT-C-36 (0.006), Malicious File (0.005), APT-C-36 (0.004), BADNEWS (0.002), External Defacement (0.001), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ursnif (36 neighbors, 36 edges)
           → TrickBot (57 neighbors, 57 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] Query 2/8: เปลี่ยนเส้นทางจากเว็บไซต์ข่าวไปยังเว็บไซต์ปลอมชื่อคล้ายกันเพื่อหลอกให้ดาวน์โหลดไ...
[RETRIEVE] Query: เปลี่ยนเส้นทางจากเว็บไซต์ข่าวไปยังเว็บไซต์ปลอมชื่อคล้ายกันเพื่อหลอกให้ดาวน์โหลดไ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SocGholish (0.286), Machete (0.174), Drive-by Compromise (0.169), KARAE (0.159), Content Injection (0.089), CURIUM (0.076), Drive-by Target (0.038), Compromise Software Dependencies and Development Tools (0.000), Supply Chain Compromise (0.000), Malicious Copy and Paste (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SocGholish (20 neighbors, 20 edges)
           → Drive-by Compromise (51 neighbors, 51 edges)
           → Machete (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/8: ดาวน์โหลดไฟล์ปรับปรุงโปรแกรมปลอมจากเว็บไซต์ของคนร้าย...
[RETRIEVE] Query: ดาวน์โหลดไฟล์ปรับปรุงโปรแกรมปลอมจากเว็บไซต์ของคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bundlore (0.074), RatMilad (0.040), Hancitor (0.010), Kerrdown (0.006), TRANSLATEXT (0.004), Cobian RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Bundlore (23 neighbors, 23 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
           → RatMilad (18 neighbors, 18 edges)
           → Download New Code at Runtime (42 neighbors, 42 edges)
[RETRIEVE-QUOTA] Query 4/8: เจ้าหน้าที่เปิดไฟล์ที่ดาวน์โหลดผ่านช่องสั่งเรียกโปรแกรมของระบบ ทำให้มัลแวร์เริ่ม...
[RETRIEVE] Query: เจ้าหน้าที่เปิดไฟล์ที่ดาวน์โหลดผ่านช่องสั่งเรียกโปรแกรมของระบบ ทำให้มัลแวร์เริ่ม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: User Execution (0.276), Gorgon Group (0.071), LAPSUS$ (0.013), Execution (0.005), User Account Control (0.003), PsExec (0.003), Script Execution (0.002), Exploitation for Client Execution (0.002), Indirect Command Execution (0.002), UPPERCUT (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → User Execution (18 neighbors, 18 edges)
           → Gorgon Group (20 neighbors, 20 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 5/8: มัลแวร์ติดต่อกลับเครื่องสั่งการของคนร้ายผ่านเครื่องพักสัญญาณ (Proxy และ Command ...
[RETRIEVE] Query: มัลแวร์ติดต่อกลับเครื่องสั่งการของคนร้ายผ่านเครื่องพักสัญญาณ (Proxy และ Command ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BISCUIT (0.455), Proxy (0.256), External Proxy (0.164), Internal Proxy (0.116), Command and Control (0.073), GreyEnergy (0.064), StarProxy (0.032), StarProxy (0.008), Proxysvc (0.007), Serverless (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BISCUIT (11 neighbors, 11 edges)
           → Fallback Channels (58 neighbors, 58 edges)
           → Proxy (84 neighbors, 84 edges)
[RETRIEVE-QUOTA] Query 6/8: เก็บรวบรวมข้อมูลรายละเอียดของเครื่องคอมพิวเตอร์เป้าหมาย (System Information Disc...
[RETRIEVE] Query: เก็บรวบรวมข้อมูลรายละเอียดของเครื่องคอมพิวเตอร์เป้าหมาย (System Information Disc...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SideTwist (0.898), SVCReady (0.692), System Information Discovery (0.626), Systeminfo (0.490), Systeminfo (0.347), System Owner/User Discovery (0.252), SYSCON (0.148), System Service Discovery (0.095), Device Driver Discovery (0.011), Process Discovery (0.008)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SideTwist (16 neighbors, 16 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → SVCReady (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 7/8: ค้นหารายชื่อเครื่องคอมพิวเตอร์อื่นในโดเมนขององค์กร (Remote System Discovery)...
[RETRIEVE] Query: ค้นหารายชื่อเครื่องคอมพิวเตอร์อื่นในโดเมนขององค์กร (Remote System Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Turla (0.944), Remote System Discovery (0.401), Industroyer (0.386), System Network Connections Discovery (0.023), Network Service Discovery (0.006), Wi-Fi Discovery (0.004), System Owner/User Discovery (0.003), System Information Discovery (0.002), Emotet (0.000), RDP Hijacking (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Turla (98 neighbors, 98 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
           → Industroyer (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 8/8: ส่งข้อมูลรายละเอียดเครื่องเป้าหมายและรายชื่อเครื่องในโดเมนกลับไปยังคนร้าย (Exfil...
[RETRIEVE] Query: ส่งข้อมูลรายละเอียดเครื่องเป้าหมายและรายชื่อเครื่องในโดเมนกลับไปยังคนร้าย (Exfil...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Industroyer (0.449), Exfiltration (0.247), Empire (0.233), Data from Local System (0.089), Exfiltration Over Alternative Protocol (0.049), Data from Network Shared Drive (0.031), Exfiltration Over C2 Channel (0.016), Empire (0.010), Exbyte (0.010), Exbyte (0.008)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Industroyer (21 neighbors, 21 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Exfiltration (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [74/100] retrieved=427 relevant=3 latency=36545ms
[RETRIEVE-QUOTA] Query 1/4: เมื่อวันที่ 1 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Query: เมื่อวันที่ 1 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploitation for Privilege Escalation (0.039), Modify Registry (0.005), UPPERCUT (0.004), FIN8 (0.003), BackConfig (0.001), Valid Accounts (0.000), Exfiltration to Text Storage Sites (0.000), Lazarus Group (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → UPPERCUT (18 neighbors, 18 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] Query 2/4: นำไฟล์สำหรับขยายการเข้าถึงไปไว้ในตำแหน่งและตั้งชื่อให้เหมือนไฟล์ระบบที่ถูกต้องเพ...
[RETRIEVE] Query: นำไฟล์สำหรับขยายการเข้าถึงไปไว้ในตำแหน่งและตั้งชื่อให้เหมือนไฟล์ระบบที่ถูกต้องเพ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Masquerading (0.884), Masquerade File Type (0.458), UPSTYLE (0.376), Execution Prevention (0.333), Restrict File and Directory Permissions (0.291), Deobfuscate/Decode Files or Information (0.043), Encrypted/Encoded File (0.035), Match Legitimate Resource Name or Location (0.029), Malicious File (0.005), Runtime Data Manipulation (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Masquerading (81 neighbors, 81 edges)
           → Masquerade File Type (25 neighbors, 25 edges)
           → UPSTYLE (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 3/4: รันคำสั่งขโมยสิทธิ์ประจำตัวจากกระบวนการที่มีสิทธิ์สูง แล้วใช้สิทธิ์นั้นเปิดโปรแก...
[RETRIEVE] Query: รันคำสั่งขโมยสิทธิ์ประจำตัวจากกระบวนการที่มีสิทธิ์สูง แล้วใช้สิทธิ์นั้นเปิดโปรแก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cobalt Strike (0.322), Qilin (0.222), Steal or Forge Authentication Certificates (0.104), Create Process with Token (0.048), Audit (0.027), Forge Web Credentials (0.023), Access Token Manipulation (0.017), AADInternals (0.015), Token Impersonation/Theft (0.015), SAML Tokens (0.007)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Cobalt Strike (109 neighbors, 109 edges)
           → Token Impersonation/Theft (26 neighbors, 26 edges)
           → Qilin (54 neighbors, 54 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
[RETRIEVE-QUOTA] Query 4/4: แก้ไขค่า Registry ของเครื่องมือ Windows Backup and Restore เพื่อหลบเลี่ยง UAC แล...
[RETRIEVE] Query: แก้ไขค่า Registry ของเครื่องมือ Windows Backup and Restore เพื่อหลบเลี่ยง UAC แล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bypass User Account Control (0.726), LockBit 2.0 (0.706), User Account Control (0.468), Update Software (0.355), Pupy (0.328), Operating System Configuration (0.293), Modify Registry (0.248), UACMe (0.216), Credentials in Registry (0.002), Security Account Manager (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bypass User Account Control (70 neighbors, 70 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
           → User Account Control (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] 12 vectors (quota 3/query), 8 subgraphs from 4 queries
  [75/100] retrieved=553 relevant=3 latency=21752ms
[RETRIEVE-QUOTA] Query 1/10: เมื่อวันที่ 19 กรกฎาคม 2564 หน่วยงานแห่งหนึ่งแจ้งความว่าถูกลักลอบเข้าถึงข้อมูลภา...
[RETRIEVE] Query: เมื่อวันที่ 19 กรกฎาคม 2564 หน่วยงานแห่งหนึ่งแจ้งความว่าถูกลักลอบเข้าถึงข้อมูลภา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN13 (0.309), External Remote Services (0.063), Duqu (0.011), FLIPSIDE (0.008), FakeSpy (0.001), Protocol or Service Impersonation (0.001), RDP Hijacking (0.001), Exfiltration Over Alternative Protocol (0.000), Protocol Tunneling (0.000), Remote Desktop Protocol (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → FIN13 (57 neighbors, 57 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → Duqu (21 neighbors, 21 edges)
           → Protocol Tunneling (46 neighbors, 46 edges)
[RETRIEVE-QUOTA] Query 2/10: เข้าถึงเครือข่ายองค์กรผ่าน External Remote Services เช่น บริการ VPN ที่เปิดให้พน...
[RETRIEVE] Query: เข้าถึงเครือข่ายองค์กรผ่าน External Remote Services เช่น บริการ VPN ที่เปิดให้พน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Remote Services (0.971), Limit Access to Resource Over Network (0.722), Operation Wocao (0.213), Web Portal Capture (0.178), Volt Typhoon (0.165), Exploitation of Remote Services (0.012), Trusted Relationship (0.008), Limit Access to Resource Over Network (0.005), Terminal Services DLL (0.002), Remote Desktop Protocol (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → External Remote Services (52 neighbors, 52 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Web Portal Capture (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/10: ส่งเอกสารล่อลวงถึงเจ้าหน้าที่เพื่อให้เปิดไฟล์แนบ (Spearphishing Attachment)...
[RETRIEVE] Query: ส่งเอกสารล่อลวงถึงเจ้าหน้าที่เพื่อให้เปิดไฟล์แนบ (Spearphishing Attachment)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mofang (0.918), Saint Bear (0.773), Spearphishing Attachment (0.716), Spearphishing Attachment (0.684), Malicious File (0.442), Spearphishing Link (0.382), Phishing (0.366), CURIUM (0.358), Gorgon Group (0.086), Internal Spearphishing (0.008)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Mofang (8 neighbors, 8 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/10: ใช้ช่องโหว่ของโปรแกรมอ่านเอกสารบนเครื่องผู้ใช้เพื่อสั่งรันชุดคำสั่ง (Exploitatio...
[RETRIEVE] Query: ใช้ช่องโหว่ของโปรแกรมอ่านเอกสารบนเครื่องผู้ใช้เพื่อสั่งรันชุดคำสั่ง (Exploitatio...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT29 (0.792), Exploitation for Client Execution (0.726), admin@338 (0.697), Frankenstein (0.525), Confucius (0.403), Indirect Command Execution (0.027), User Execution (0.020), Exploitation for Credential Access (0.012), Exploit Public-Facing Application (0.005), Exploit Protection (0.004)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploitation for Client Execution (65 neighbors, 65 edges)
           → APT29 (117 neighbors, 117 edges)
           → admin@338 (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 5/10: สั่งรันชุดคำสั่งและวางโปรแกรมอันตรายลงบนเครื่องผู้ใช้...
[RETRIEVE] Query: สั่งรันชุดคำสั่งและวางโปรแกรมอันตรายลงบนเครื่องผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gorgon Group (0.058), PsExec (0.048), RansomHub (0.026), Indirect Command Execution (0.014), Windows Command Shell (0.008), Visual Basic (0.003), Cardinal RAT (0.002), Cobian RAT (0.002), CrossRAT (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Gorgon Group (20 neighbors, 20 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → PsExec (49 neighbors, 49 edges)
[RETRIEVE-QUOTA] Query 6/10: ซ่อนข้อมูลที่ขโมยไว้ภายในไฟล์อื่นที่ดูเหมือนไฟล์ปกติ (Data Obfuscation)...
[RETRIEVE] Query: ซ่อนข้อมูลที่ขโมยไว้ภายในไฟล์อื่นที่ดูเหมือนไฟล์ปกติ (Data Obfuscation)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Obfuscated Files or Information (0.373), Encrypted/Encoded File (0.217), Deobfuscate/Decode Files or Information (0.200), Data Obfuscation (0.126), Pisloader (0.103), OopsIE (0.048), RegDuke (0.024), Command Obfuscation (0.016), Empire (0.004), Polymorphic Code (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
[RETRIEVE-QUOTA] Query 7/10: นำข้อมูลที่ขโมยไปฝากไว้บนบริการเก็บซอร์สโค้ดสาธารณะ (Exfiltration Over Web Servi...
[RETRIEVE] Query: นำข้อมูลที่ขโมยไปฝากไว้บนบริการเก็บซอร์สโค้ดสาธารณะ (Exfiltration Over Web Servi...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Web Service (0.488), Exfiltration to Code Repository (0.229), Exbyte (0.199), AppleSeed (0.110), Exfiltration to Text Storage Sites (0.096), Exfiltration Over Alternative Protocol (0.056), Exfiltration to Cloud Storage (0.054), HAMMERTOSS (0.036), Exfiltration Over Physical Medium (0.026), Web Services (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over Web Service (23 neighbors, 23 edges)
           → Exfiltration to Code Repository (6 neighbors, 6 edges)
           → Exbyte (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 8/10: ปลอมรูปแบบการติดต่อให้เหมือนการใช้งานปกติโดยใช้กุญแจเรียกใช้บริการของผู้ให้บริกา...
[RETRIEVE] Query: ปลอมรูปแบบการติดต่อให้เหมือนการใช้งานปกติโดยใช้กุญแจเรียกใช้บริการของผู้ให้บริกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: KeyBoy (0.577), Protocol or Service Impersonation (0.508), Token Impersonation/Theft (0.196), InvisiMole (0.177), GUI Input Capture (0.025), Impersonation (0.007), Access Token Manipulation (0.005), C0027 (0.003), Operation Dream Job (0.001), Temporary Elevated Cloud Access (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Protocol or Service Impersonation (26 neighbors, 26 edges)
           → KeyBoy (19 neighbors, 19 edges)
           → Token Impersonation/Theft (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 9/10: ห่อหุ้มการติดต่อไว้ภายในโพรโทคอลอื่น (Protocol Tunneling)...
[RETRIEVE] Query: ห่อหุ้มการติดต่อไว้ภายในโพรโทคอลอื่น (Protocol Tunneling)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Protocol Tunneling (0.994), Duqu (0.716), Cobalt Strike (0.662), Mythic (0.511), FRP (0.272), DNS (0.095), Web Protocols (0.026), IDE Tunneling (0.015), Ping (0.000), Tonto Team (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Protocol Tunneling (46 neighbors, 46 edges)
           → Duqu (21 neighbors, 21 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] Query 10/10: ส่งต่อการเชื่อมต่อผ่านเครื่องพักสัญญาณหลายทอดและเครือข่ายนิรนาม (Proxy)...
[RETRIEVE] Query: ส่งต่อการเชื่อมต่อผ่านเครื่องพักสัญญาณหลายทอดและเครือข่ายนิรนาม (Proxy)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SPACEHOP Activity (0.151), Inception (0.067), Multi-hop Proxy (0.052), Proxy (0.052), External Proxy (0.021), StarProxy (0.010), StarProxy (0.010), Internal Proxy (0.008), Proxysvc (0.002), StarProxy (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SPACEHOP Activity (6 neighbors, 6 edges)
           → Multi-hop Proxy (45 neighbors, 45 edges)
           → Inception (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 10 queries
  [76/100] retrieved=302 relevant=6 latency=46756ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 25 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Query: เมื่อวันที่ 25 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.047), File Deletion (0.041), Bankshot (0.019), APT-C-36 (0.002), Ingress Tool Transfer (0.002), Ursnif (0.001), USBStealer (0.001), Internal Spearphishing (0.000), Right-to-Left Override (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมฝังตัวบนเครื่องแรกดาวน์โหลดเครื่องมือสำหรับสั่งงานเครื่องระยะไกล...
[RETRIEVE] Query: โปรแกรมฝังตัวบนเครื่องแรกดาวน์โหลดเครื่องมือสำหรับสั่งงานเครื่องระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteUtilities (0.077), RemoteCMD (0.060), xCmd (0.058), RemoteUtilities (0.020), CrackMapExec (0.014), NavRAT (0.009), gh0st RAT (0.005), RemoteUtilities (0.005), Remote Access Tools (0.003), Micropsia (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteUtilities (5 neighbors, 5 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → RemoteCMD (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 3/8: โปรแกรมฝังตัวบนเครื่องแรกดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดที่สองมาเก็บไว้...
[RETRIEVE] Query: โปรแกรมฝังตัวบนเครื่องแรกดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดที่สองมาเก็บไว้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BADHATCH (0.017), Grandoreiro (0.006), DownPaper (0.005), PowerShower (0.002), SoreFang (0.001), Installer Packages (0.001), BUBBLEWRAP (0.001), PipeMon (0.000), GoldenSpy (0.000), Cherry Picker (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → BADHATCH (36 neighbors, 36 edges)
           → Embedded Payloads (27 neighbors, 27 edges)
           → Grandoreiro (43 neighbors, 43 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 4/8: คนร้ายสั่งรันเครื่องมือบนเครื่องแม่ข่ายเก็บไฟล์โดยใช้บัญชีผู้ดูแลระบบ...
[RETRIEVE] Query: คนร้ายสั่งรันเครื่องมือบนเครื่องแม่ข่ายเก็บไฟล์โดยใช้บัญชีผู้ดูแลระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: admin@338 (0.047), Cinnamon Tempest (0.027), Ember Bear (0.012), Ingress Tool Transfer (0.005), BlackByte (0.005), Input Injection (0.001), BBSRAT (0.001), Domain Controller Authentication (0.000), Exploitation for Credential Access (0.000), Threat Group-1314 (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → admin@338 (19 neighbors, 19 edges)
           → Local Account (69 neighbors, 69 edges)
           → Cinnamon Tempest (27 neighbors, 27 edges)
           → Domain Accounts (47 neighbors, 47 edges)
[RETRIEVE-QUOTA] Query 5/8: คนร้ายย้ายการบุกรุกจากเครื่องแรกไปยังเครื่องแม่ข่ายเก็บไฟล์ด้วยการสั่งงานระยะไกล...
[RETRIEVE] Query: คนร้ายย้ายการบุกรุกจากเครื่องแรกไปยังเครื่องแม่ข่ายเก็บไฟล์ด้วยการสั่งงานระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Replication Through Removable Media (0.010), USBStealer (0.010), Ingress Tool Transfer (0.009), Bankshot (0.007), Taint Shared Content (0.007), Lateral Tool Transfer (0.007), Communication Through Removable Media (0.005), Darkhotel (0.005), Transfer Data to Cloud Account (0.001), APT1 (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Replication Through Removable Media (35 neighbors, 35 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → USBStealer (15 neighbors, 15 edges)
           → Communication Through Removable Media (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 6/8: ตัวติดตั้งโปรแกรมฝังตัวถูกเรียกทำงานบนเครื่องแม่ข่ายเก็บไฟล์ผ่านการสร้างบริการขอ...
[RETRIEVE] Query: ตัวติดตั้งโปรแกรมฝังตัวถูกเรียกทำงานบนเครื่องแม่ข่ายเก็บไฟล์ผ่านการสร้างบริการขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Service (0.010), Create or Modify System Process (0.007), Systemd Service (0.006), STARWHALE (0.003), Conficker (0.001), Services File Permissions Weakness (0.001), Installer Packages (0.001), IMAPLoader (0.000), AppDomainManager (0.000), Active Setup (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Windows Service (150 neighbors, 150 edges)
           → Create or Modify System Process (25 neighbors, 25 edges)
           → Systemd Service (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 7/8: โปรแกรมฝังตัวบนเครื่องแม่ข่ายเก็บไฟล์ติดต่อกลับไปยังคนร้าย...
[RETRIEVE] Query: โปรแกรมฝังตัวบนเครื่องแม่ข่ายเก็บไฟล์ติดต่อกลับไปยังคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TrickBot (0.198), Ramsay (0.022), HALFBAKED (0.018), Netwalker (0.014), CrossRAT (0.008), Cobian RAT (0.007), Trojan.Karagany (0.005), Cardinal RAT (0.001), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → TrickBot (57 neighbors, 57 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Ramsay (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 8/8: คนร้ายสั่งลบไฟล์ที่นำไปวางไว้บนเครื่องแรกเพื่อเก็บกวาดร่องรอย...
[RETRIEVE] Query: คนร้ายสั่งลบไฟล์ที่นำไปวางไว้บนเครื่องแรกเพื่อเก็บกวาดร่องรอย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: USBStealer (0.019), File Deletion (0.011), USBStealer (0.009), Reaver (0.009), EvilBunny (0.005), Clear Persistence (0.002), Data Destruction (0.002), Disk Wipe (0.001), Patch System Image (0.000), SoreFang (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → USBStealer (15 neighbors, 15 edges)
           → Communication Through Removable Media (7 neighbors, 7 edges)
           → File Deletion (310 neighbors, 310 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [77/100] retrieved=714 relevant=3 latency=31584ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 29 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความเพิ่มเติมถึงเส้นทางที...
[RETRIEVE] Query: เมื่อวันที่ 29 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความเพิ่มเติมถึงเส้นทางที...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sandworm Team (0.831), Sea Turtle (0.700), Trusted Relationship (0.229), TeamTNT (0.004), Business Relationships (0.001), Ingress Tool Transfer (0.001), Network Trust Dependencies (0.000), Network Security Appliances (0.000), Domain Trust Discovery (0.000), Customer Relationship Management Software (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Sandworm Team (113 neighbors, 113 edges)
           → Trusted Relationship (18 neighbors, 18 edges)
           → Sea Turtle (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 2/6: ใช้ความสัมพันธ์ความน่าเชื่อถือของเราเตอร์ประจำสาขาเพื่อเข้าสู่เครือข่ายองค์กรเป้...
[RETRIEVE] Query: ใช้ความสัมพันธ์ความน่าเชื่อถือของเราเตอร์ประจำสาขาเพื่อเข้าสู่เครือข่ายองค์กรเป้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sea Turtle (0.339), LAPSUS$ (0.240), Trusted Relationship (0.074), RedCurl (0.051), Network Trust Dependencies (0.017), APT29 (0.017), Business Relationships (0.014), Customer Relationship Management Software (0.000), Acquire Access (0.000), Search Victim-Owned Websites (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Sea Turtle (28 neighbors, 28 edges)
           → Trusted Relationship (18 neighbors, 18 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] Query 3/6: ใช้เครื่องมือสแกนสำรวจเครือข่ายภายในองค์กร (Network Service Scanning)...
[RETRIEVE] Query: ใช้เครื่องมือสแกนสำรวจเครือข่ายภายในองค์กร (Network Service Scanning)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: C0018 (0.729), Vulnerability Scanning (0.619), NBTscan (0.604), Network Service Discovery (0.208), Active Scanning (0.020), Scanning IP Blocks (0.018), Vulnerability Scanning (0.007), Response Metadata (0.005), Scan Databases (0.005), Vulnerability Scanning (0.004)
[RETRIEVE] Graph expansion: 4 subgraphs
           → C0018 (25 neighbors, 25 edges)
           → Network Service Discovery (78 neighbors, 78 edges)
           → Vulnerability Scanning (5 neighbors, 5 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
[RETRIEVE-QUOTA] Query 4/6: ตั้งเครื่องแม่ข่ายรับส่งไฟล์ภายในเครือข่ายผู้เสียหายเพื่อถ่ายโอนข้อมูลระหว่างเคร...
[RETRIEVE] Query: ตั้งเครื่องแม่ข่ายรับส่งไฟล์ภายในเครือข่ายผู้เสียหายเพื่อถ่ายโอนข้อมูลระหว่างเคร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File and Directory Discovery (0.189), Lateral Tool Transfer (0.124), Ingress Tool Transfer (0.120), NETEAGLE (0.085), XAgentOSX (0.019), Cloud Storage Object Discovery (0.011), DynoWiper (0.009), System Information Discovery (0.003), BackConfig (0.002), System Owner/User Discovery (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → File and Directory Discovery (371 neighbors, 371 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 5/6: ใช้เราเตอร์ประจำสาขาที่ถูกยึดครองเป็นโครงสร้างพื้นฐานเพื่อส่งต่อการเชื่อมต่อให้ก...
[RETRIEVE] Query: ใช้เราเตอร์ประจำสาขาที่ถูกยึดครองเป็นโครงสร้างพื้นฐานเพื่อส่งต่อการเชื่อมต่อให้ก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Proxy (0.008), External Proxy (0.004), Internal Proxy (0.002), StarProxy (0.001), Proxysvc (0.000), Application Layer Protocol (0.000), Restrict Web-Based Content (0.000), Restrict Web-Based Content (0.000), StarProxy (0.000), StarProxy (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Proxy (84 neighbors, 84 edges)
           → External Proxy (27 neighbors, 27 edges)
           → Internal Proxy (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 6/6: ใช้เราเตอร์ประจำสาขาที่ถูกยึดครองเป็นทางผ่านไปยังผู้เสียหายรายอื่นในเครือข่ายเดี...
[RETRIEVE] Query: ใช้เราเตอร์ประจำสาขาที่ถูกยึดครองเป็นทางผ่านไปยังผู้เสียหายรายอื่นในเครือข่ายเดี...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Proxy (0.033), StarProxy (0.021), Drovorub (0.020), Gomir (0.019), External Proxy (0.011), Internal Proxy (0.010), StarProxy (0.007), Multi-hop Proxy (0.005), Proxysvc (0.001), StarProxy (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Proxy (84 neighbors, 84 edges)
           → Drovorub (13 neighbors, 13 edges)
           → Internal Proxy (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [78/100] retrieved=231 relevant=3 latency=30525ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 30 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความเพิ่มเติมถึ...
[RETRIEVE] Query: เมื่อวันที่ 30 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความเพิ่มเติมถึ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.006), APT-C-36 (0.001), Attestation (0.000), Network Intrusion Prevention (0.000), Ursnif (0.000), Compromise Host Software Binary (0.000), Internal Spearphishing (0.000), Subvert Trust Controls (0.000), Social Engineering (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → AsyncRAT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 2/8: ดัดแปลงอุปกรณ์เครือข่ายโดยแก้ไขซอฟต์แวร์ที่ติดตั้งอยู่ในหน่วยความจำ...
[RETRIEVE] Query: ดัดแปลงอุปกรณ์เครือข่ายโดยแก้ไขซอฟต์แวร์ที่ติดตั้งอยู่ในหน่วยความจำ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Modify System Image (0.120), Patch System Image (0.029), Network Device Authentication (0.010), Compromise Host Software Binary (0.009), NETWIRE (0.004), IMAPLoader (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Modify System Image (10 neighbors, 10 edges)
           → Patch System Image (9 neighbors, 9 edges)
           → Network Device Authentication (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 3/8: ติดตั้งซอฟต์แวร์รุ่นเก่าที่มีลายเซ็นถูกต้องเพื่อหลบเลี่ยงการตรวจสอบความถูกต้องขอ...
[RETRIEVE] Query: ติดตั้งซอฟต์แวร์รุ่นเก่าที่มีลายเซ็นถูกต้องเพื่อหลบเลี่ยงการตรวจสอบความถูกต้องขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QakBot (0.026), Code Signing (0.020), Invalid Code Signature (0.016), Code Signing Policy Modification (0.005), Code Signing (0.004), Disable or Remove Feature or Program (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → QakBot (74 neighbors, 74 edges)
           → Code Signing (90 neighbors, 90 edges)
           → Code Signing (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 4/8: ติดตั้งตัวโหลดระบบที่ถูกดัดแปลงลงในอุปกรณ์เครือข่าย...
[RETRIEVE] Query: ติดตั้งตัวโหลดระบบที่ถูกดัดแปลงลงในอุปกรณ์เครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Network Device Authentication (0.099), Patch System Image (0.063), TFTP Boot (0.057), Modify System Image (0.017), Neo-reGeorg (0.002), BendyBear (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Network Device Authentication (11 neighbors, 11 edges)
           → Patch System Image (9 neighbors, 9 edges)
           → TFTP Boot (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 5/8: ติดตั้งซอฟต์แวร์ที่ไม่มีลายเซ็นและถูกคนร้ายดัดแปลงเอง...
[RETRIEVE] Query: ติดตั้งซอฟต์แวร์ที่ไม่มีลายเซ็นและถูกคนร้ายดัดแปลงเอง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Patchwork (0.149), Janicab (0.072), Kerrdown (0.023), Netwalker (0.005), ZeroCleare (0.005), Cobian RAT (0.001), Visual Basic (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Patchwork (50 neighbors, 50 edges)
           → Code Signing (90 neighbors, 90 edges)
           → Janicab (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/8: ใช้ตัวโหลดระบบที่ถูกดัดแปลงเพื่อให้ซอฟต์แวร์ดัดแปลงยังคงผ่านการตรวจสอบและไม่ถูกต...
[RETRIEVE] Query: ใช้ตัวโหลดระบบที่ถูกดัดแปลงเพื่อให้ซอฟต์แวร์ดัดแปลงยังคงผ่านการตรวจสอบและไม่ถูกต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Polymorphic Code (0.014), Lock Bootloader (0.013), Attestation (0.009), Execution Prevention (0.005), AbstractEmu (0.002), Application Shimming (0.002), Restrict Library Loading (0.001), Reflective Code Loading (0.001), LC_LOAD_DYLIB Addition (0.001), Execution Prevention (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Polymorphic Code (5 neighbors, 5 edges)
           → Lock Bootloader (3 neighbors, 3 edges)
           → Compromise Client Software Binary (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 7/8: วางกฎอัตโนมัติเพื่อตัดบรรทัดที่มีข้อความบางคำออกจากผลลัพธ์คำสั่งตรวจสอบของผู้ดูแ...
[RETRIEVE] Query: วางกฎอัตโนมัติเพื่อตัดบรรทัดที่มีข้อความบางคำออกจากผลลัพธ์คำสั่งตรวจสอบของผู้ดูแ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Audit (0.006), Ruler (0.002), Audit (0.001), Active Directory Object Deletion (0.000), Execution Prevention (0.000), Firewall Rule Modification (0.000), Active Directory Configuration (0.000), Password Policies (0.000), Clear Mailbox Data (0.000), Firewall Disable (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Audit (110 neighbors, 110 edges)
           → Email Forwarding Rule (12 neighbors, 12 edges)
           → Ruler (5 neighbors, 5 edges)
           → Outlook Rules (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 8/8: ขัดขวางคำสั่งคัดลอก เปลี่ยนชื่อ และย้ายไฟล์ทำงานเพื่อกีดกันการตรวจพิสูจน์พยานหลั...
[RETRIEVE] Query: ขัดขวางคำสั่งคัดลอก เปลี่ยนชื่อ และย้ายไฟล์ทำงานเพื่อกีดกันการตรวจพิสูจน์พยานหลั...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Restrict File and Directory Permissions (0.102), Indicator Removal (0.034), Restrict Registry Permissions (0.024), Execution Prevention (0.006), Execution Prevention (0.004), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Restrict File and Directory Permissions (60 neighbors, 60 edges)
           → Runtime Data Manipulation (6 neighbors, 6 edges)
           → Indicator Removal (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [79/100] retrieved=204 relevant=2 latency=45980ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 6 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Query: เมื่อวันที่ 6 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA505 (0.023), KeyBoy (0.016), NotPetya (0.015), LaZagne (0.004), Credentials from Web Browsers (0.004), Unsecured Credentials (0.001), Web Credential Usage (0.000), Credentials in Registry (0.000), Query Registry (0.000), Windows Credential Manager (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → TA505 (50 neighbors, 50 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → KeyBoy (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 2/5: เพิ่มรายการเรียกใช้งานโปรแกรมใน Registry Run Keys / Startup Folder เพื่อให้โปรแก...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานโปรแกรมใน Registry Run Keys / Startup Folder เพื่อให้โปรแก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.942), DarkComet (0.914), Ursnif (0.608), LockBit 2.0 (0.570), Office Test (0.111), Boot or Logon Autostart Execution (0.053), Active Setup (0.012), Windows Registry Key Modification (0.003), Re-opened Applications (0.003), Windows Registry Key Access (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → DarkComet (21 neighbors, 21 edges)
           → Ursnif (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 3/5: อ่าน Credentials from Web Browsers ได้แก่ชื่อผู้ใช้และรหัสผ่านที่บันทึกไว้ในโปรแ...
[RETRIEVE] Query: อ่าน Credentials from Web Browsers ได้แก่ชื่อผู้ใช้และรหัสผ่านที่บันทึกไว้ในโปรแ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.949), LaZagne (0.302), SUGARDUMP (0.225), Password Policies (0.177), Credentials in Registry (0.016), Windows Credential Manager (0.012), Forge Web Credentials (0.011), Browser Information Discovery (0.011), Web Credential Usage (0.010), Credentials from Password Stores (0.010)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → LaZagne (22 neighbors, 22 edges)
           → SUGARDUMP (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 4/5: ใช้ชุดเครื่องมือโจมตีช่องโหว่ของบริการแบ่งปันไฟล์ Windows ผ่านพอร์ต SMB เพื่อขยา...
[RETRIEVE] Query: ใช้ชุดเครื่องมือโจมตีช่องโหว่ของบริการแบ่งปันไฟล์ Windows ผ่านพอร์ต SMB เพื่อขยา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT32 (0.604), Cobalt Strike (0.458), BlackByte (0.448), SMB/Windows Admin Shares (0.420), Network Share Discovery (0.092), Forced Authentication (0.055), Lateral Tool Transfer (0.019), Exfiltration Over Alternative Protocol (0.009), Name Resolution Poisoning and SMB Relay (0.006), Taint Shared Content (0.003)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT32 (93 neighbors, 93 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
           → File Transfer Protocols (32 neighbors, 32 edges)
[RETRIEVE-QUOTA] Query 5/5: ติดต่อกลับเครื่องสั่งการผ่านโพรโทคอลเว็บโดยใช้เส้นทางคำขอเป็นชื่อโฟลเดอร์ตัวอักษ...
[RETRIEVE] Query: ติดต่อกลับเครื่องสั่งการผ่านโพรโทคอลเว็บโดยใช้เส้นทางคำขอเป็นชื่อโฟลเดอร์ตัวอักษ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Rotexy (0.026), P.A.S. Webshell (0.006), Bidirectional Communication (0.004), BlackMould (0.002), FRP (0.002), One-Way Communication (0.002), POWRUNER (0.001), KernelCallbackTable (0.001), HTTPTroy (0.000), RemoteCMD (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Rotexy (16 neighbors, 16 edges)
           → Web Protocols (52 neighbors, 52 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Web Protocols (424 neighbors, 424 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [80/100] retrieved=395 relevant=4 latency=27182ms
[RETRIEVE-QUOTA] Query 1/4: เมื่อวันที่ 2 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายหลบ...
[RETRIEVE] Query: เมื่อวันที่ 2 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายหลบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operation Wocao (0.476), APT3 (0.285), Indicator Removal (0.021), Indicator Removal from Tools (0.020), Bypass User Account Control (0.001), Disable or Modify Tools (0.000), User Account Control (0.000), Clear Windows Event Logs (0.000), User Account Control (0.000), Multi-factor Authentication (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Operation Wocao (79 neighbors, 79 edges)
           → Indicator Removal from Tools (20 neighbors, 20 edges)
           → APT3 (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/4: หลบเลี่ยงกลไกยืนยันก่อนยกระดับสิทธิ์เพื่อให้โปรแกรมได้สิทธิ์ผู้ดูแลระบบโดยไม่แสด...
[RETRIEVE] Query: หลบเลี่ยงกลไกยืนยันก่อนยกระดับสิทธิ์เพื่อให้โปรแกรมได้สิทธิ์ผู้ดูแลระบบโดยไม่แสด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bypass User Account Control (0.978), RCSession (0.734), User Account Control (0.660), User Account Control (0.637), Abuse Elevation Control Mechanism (0.488), GUI Input Capture (0.370), LockBit 2.0 (0.348), UACMe (0.213), UACMe (0.154), User Account Management (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bypass User Account Control (70 neighbors, 70 edges)
           → RCSession (24 neighbors, 24 edges)
           → User Account Control (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 3/4: ปรับแต่งเครื่องมือโดยลบข้อความและค่าเฉพาะที่โปรแกรมป้องกันใช้ตรวจจับออกจากไฟล์ (...
[RETRIEVE] Query: ปรับแต่งเครื่องมือโดยลบข้อความและค่าเฉพาะที่โปรแกรมป้องกันใช้ตรวจจับออกจากไฟล์ (...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Indicator Removal from Tools (0.936), Operation Wocao (0.597), Indicator Removal (0.594), APT3 (0.492), Penquin (0.488), IPsec Helper (0.089), Disable or Modify Tools (0.069), Tool (0.001), Ccache Files (0.000), Multi-factor Authentication (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Indicator Removal from Tools (20 neighbors, 20 edges)
           → Indicator Removal (45 neighbors, 45 edges)
           → Operation Wocao (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] Query 4/4: ล้างไฟล์บันทึกเหตุการณ์ของ Windows ทั้งหมดเพื่อลบร่องรอยการเข้าถึง (Indicator Re...
[RETRIEVE] Query: ล้างไฟล์บันทึกเหตุการณ์ของ Windows ทั้งหมดเพื่อลบร่องรอยการเข้าถึง (Indicator Re...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chameleon (0.231), Indicator Removal (0.157), SILENTTRINITY (0.153), Attestation (0.132), Clear Windows Event Logs (0.122), Neoichor (0.117), Windows Registry Key Deletion (0.004), Account Access Removal (0.001), Koadic (0.000), Attor (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chameleon (26 neighbors, 26 edges)
           → Indicator Removal on Host (10 neighbors, 10 edges)
           → Indicator Removal (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] 9 vectors (quota 3/query), 8 subgraphs from 4 queries
  [81/100] retrieved=229 relevant=3 latency=25278ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 19 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร...
[RETRIEVE] Query: เมื่อวันที่ 19 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gamaredon Group (0.064), POWRUNER (0.062), APT-C-36 (0.016), Ursnif (0.002), APT-C-36 (0.002), Ingress Tool Transfer (0.001), Exfiltration (0.000), Internal Spearphishing (0.000), Archive via Utility (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Gamaredon Group (76 neighbors, 76 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Groups (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] Query 2/6: ใช้ระบบนโยบายกลุ่มของโดเมนส่งไฟล์โปรแกรมของคนร้ายไปติดตั้งบนเครื่องลูกข่ายทั้งหม...
[RETRIEVE] Query: ใช้ระบบนโยบายกลุ่มของโดเมนส่งไฟล์โปรแกรมของคนร้ายไปติดตั้งบนเครื่องลูกข่ายทั้งหม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cinnamon Tempest (0.100), HermeticWiper (0.056), Group Policy Modification (0.032), Group Policy Discovery (0.028), APT41 (0.026), POWRUNER (0.007), AppDomainManager (0.002), Shared Modules (0.002), Ingress Tool Transfer (0.002), Additional Local or Domain Groups (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Cinnamon Tempest (27 neighbors, 27 edges)
           → Group Policy Modification (22 neighbors, 22 edges)
           → HermeticWiper (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 3/6: แบ่งข้อมูลที่รวบรวมได้ออกเป็นส่วนย่อยหลายส่วนเพื่อเตรียมนำออก...
[RETRIEVE] Query: แบ่งข้อมูลที่รวบรวมได้ออกเป็นส่วนย่อยหลายส่วนเพื่อเตรียมนำออก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ObliqueRAT (0.414), Data Staged (0.034), Local Data Staging (0.026), menuPass (0.013), Remote Data Staging (0.005), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), The White Company (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → ObliqueRAT (15 neighbors, 15 edges)
           → Data Transfer Size Limits (24 neighbors, 24 edges)
           → Data Staged (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 4/6: ใช้โปรแกรมบีบอัดไฟล์ทั่วไปบีบอัดข้อมูลแต่ละส่วน...
[RETRIEVE] Query: ใช้โปรแกรมบีบอัดไฟล์ทั่วไปบีบอัดข้อมูลแต่ละส่วน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Compression (0.165), FoggyWeb (0.148), BADFLICK (0.022), Expand (0.014), BADHATCH (0.011), Archive via Utility (0.003), Archive via Library (0.002), Fgdump (0.001), Standard Encoding (0.000), Masquerade File Type (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Compression (38 neighbors, 38 edges)
           → FoggyWeb (22 neighbors, 22 edges)
           → Archive via Library (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 5/6: ใช้โปรแกรมรับส่งไฟล์ลำเลียงข้อมูลที่บีบอัดออกจากเครือข่ายไปยังบัญชีปลายทางที่คนร...
[RETRIEVE] Query: ใช้โปรแกรมรับส่งไฟล์ลำเลียงข้อมูลที่บีบอัดออกจากเครือข่ายไปยังบัญชีปลายทางที่คนร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CASTLETAP (0.199), Ingress Tool Transfer (0.063), Taint Shared Content (0.052), Koadic (0.048), ftp (0.047), CASTLETAP (0.026), Net Crawler (0.011), Impacket (0.008), PsExec (0.003), LNK Icon Smuggling (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → CASTLETAP (9 neighbors, 9 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Taint Shared Content (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 6/6: ส่งข้อมูลออกผ่านช่องทางที่แยกจากช่องทางรับคำสั่ง (Exfiltration Over Alternative ...
[RETRIEVE] Query: ส่งข้อมูลออกผ่านช่องทางที่แยกจากช่องทางรับคำสั่ง (Exfiltration Over Alternative ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Alternative Protocol (0.982), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.936), Exfiltration Over Unencrypted Non-C2 Protocol (0.910), ftp (0.877), Automated Exfiltration (0.783), Scheduled Transfer (0.755), Exfiltration Over C2 Channel (0.567), Kobalos (0.503), BRUSHFIRE (0.473), Chaes (0.443)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (15 neighbors, 15 edges)
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [82/100] retrieved=542 relevant=4 latency=27675ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 24 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนที่คนร...
[RETRIEVE] Query: เมื่อวันที่ 24 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนที่คนร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.044), VERMIN (0.027), VERMIN (0.011), APT-C-36 (0.005), Ursnif (0.001), File Deletion (0.000), Internal Spearphishing (0.000), Password Managers (0.000), Credentials In Files (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → VERMIN (17 neighbors, 17 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
[RETRIEVE-QUOTA] Query 2/6: ลบไฟล์สคริปต์ที่ใช้ลองรหัสผ่านบัญชีผู้ดูแลหลังใช้งานเสร็จ (File and Directory Di...
[RETRIEVE] Query: ลบไฟล์สคริปต์ที่ใช้ลองรหัสผ่านบัญชีผู้ดูแลหลังใช้งานเสร็จ (File and Directory Di...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File Deletion (0.036), User Account Deletion (0.023), File and Directory Discovery (0.020), IPsec Helper (0.010), Attor (0.006), Active Directory Object Deletion (0.005), InvisiMole (0.004), Instance Deletion (0.002), Volume Deletion (0.001), Windows Registry Key Deletion (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → User Account Deletion (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 3/6: ดาวน์โหลดตัวติดตั้งสำเนาที่สองของโปรแกรมฝังตัวเข้ามาในเครื่อง (Ingress Tool Tran...
[RETRIEVE] Query: ดาวน์โหลดตัวติดตั้งสำเนาที่สองของโปรแกรมฝังตัวเข้ามาในเครื่อง (Ingress Tool Tran...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ixeshe (0.195), RTM (0.161), Industroyer (0.144), Ingress Tool Transfer (0.118), Lateral Tool Transfer (0.108), cmd (0.035), Get2 (0.003), PsExec (0.001), Upload Tool (0.001), BITS Jobs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ixeshe (16 neighbors, 16 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → RTM (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 4/6: คัดลอกไฟล์ตัวติดตั้งไปยังโฟลเดอร์ระบบของเครื่องแม่ข่ายควบคุมโดเมนผ่านไดรฟ์ที่เชื...
[RETRIEVE] Query: คัดลอกไฟล์ตัวติดตั้งไปยังโฟลเดอร์ระบบของเครื่องแม่ข่ายควบคุมโดเมนผ่านไดรฟ์ที่เชื...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.734), Lateral Tool Transfer (0.638), Ingress Tool Transfer (0.401), Expand (0.168), PsExec (0.151), ftp (0.013), Upload Malware (0.004), File Deletion (0.002), Upload Tool (0.001), Tool (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 5/6: ใช้รหัสผ่านผู้ดูแลโดเมนที่ได้มาเพื่อเข้าถึงเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล (...
[RETRIEVE] Query: ใช้รหัสผ่านผู้ดูแลโดเมนที่ได้มาเพื่อเข้าถึงเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล (...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VOID MANTICORE (0.227), Remote Services (0.108), Windows Remote Management (0.073), Domain Accounts (0.050), Domain Account (0.013), Network Segmentation (0.005), Valak (0.001), Modify Authentication Process (0.001), Account Manipulation (0.001), Valak (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Domain Accounts (47 neighbors, 47 edges)
           → Remote Services (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 6/6: แจกแจงรายการงานตั้งเวลาบนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกลเพื่อหาช่องทางเรียกไ...
[RETRIEVE] Query: แจกแจงรายการงานตั้งเวลาบนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกลเพื่อหาช่องทางเรียกไ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Scheduled Task/Job (0.409), PowerSploit (0.033), CrackMapExec (0.030), At (0.019), Scheduled Task (0.016), Tasklist (0.005), Tasklist (0.003), Scheduled Job Metadata (0.003), Process Discovery (0.001), System Network Connections Discovery (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Scheduled Task/Job (18 neighbors, 18 edges)
           → PowerSploit (39 neighbors, 39 edges)
           → Scheduled Task (201 neighbors, 201 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [83/100] retrieved=653 relevant=3 latency=37632ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 15 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุ...
[RETRIEVE] Query: เมื่อวันที่ 15 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.045), Bankshot (0.017), Data from Local System (0.009), FIN8 (0.001), Password Managers (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Software Discovery (0.000), Account Use Policies (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
[RETRIEVE-QUOTA] Query 2/6: รันเครื่องมือดึงค่ารหัสผ่านจากฐานข้อมูลบัญชีผู้ใช้ที่เก็บอยู่ในเครื่องที่ยึดครอง...
[RETRIEVE] Query: รันเครื่องมือดึงค่ารหัสผ่านจากฐานข้อมูลบัญชีผู้ใช้ที่เก็บอยู่ในเครื่องที่ยึดครอง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MgBot (0.766), OS Credential Dumping (0.635), Windows Credential Editor (0.502), gsecdump (0.498), pwdump (0.392), Poseidon Group (0.312), Axiom (0.300), Credentials In Files (0.267), Password Cracking (0.166), Domain Accounts (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → MgBot (18 neighbors, 18 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/6: คัดลอกไฟล์โปรแกรมของคนร้ายจากเครื่องที่ยึดครองไปยังเครื่องคอมพิวเตอร์ของเจ้าหน้า...
[RETRIEVE] Query: คัดลอกไฟล์โปรแกรมของคนร้ายจากเครื่องที่ยึดครองไปยังเครื่องคอมพิวเตอร์ของเจ้าหน้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ingress Tool Transfer (0.865), Lateral Tool Transfer (0.819), cmd (0.712), TYPEFRAME (0.411), TONESHELL (0.298), Industroyer (0.155), File Deletion (0.054), PsExec (0.018), Upload Tool (0.004), BITS Jobs (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 4/6: ใช้เครื่องมือสั่งงานเครื่องระยะไกลเพื่อข้ามไปยังเครื่องคอมพิวเตอร์ของฝ่ายเทคโนโล...
[RETRIEVE] Query: ใช้เครื่องมือสั่งงานเครื่องระยะไกลเพื่อข้ามไปยังเครื่องคอมพิวเตอร์ของฝ่ายเทคโนโล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.330), RemoteCMD (0.268), RemoteUtilities (0.087), Remote Service Session Hijacking (0.068), Stuxnet (0.063), Terminal Services DLL (0.026), Remote Services (0.025), RDP Hijacking (0.023), Remote Access Tools (0.018), Remote Desktop Software (0.007)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Remote Service Session Hijacking (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 5/6: วางไฟล์ไลบรารีของคนร้ายไว้ในตำแหน่งที่ระบบค้นหาก่อนตำแหน่งจริงเพื่อให้โปรแกรมที่...
[RETRIEVE] Query: วางไฟล์ไลบรารีของคนร้ายไว้ในตำแหน่งที่ระบบค้นหาก่อนตำแหน่งจริงเพื่อให้โปรแกรมที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Path Interception by Search Order Hijacking (0.819), Dylib Hijacking (0.790), DLL (0.743), FoggyWeb (0.711), Chaes (0.440), Dynamic Linker Hijacking (0.386), Astaroth (0.290), Audit (0.061), VDSO Hijacking (0.056), Thread Execution Hijacking (0.050)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Path Interception by Search Order Hijacking (9 neighbors, 9 edges)
           → Dylib Hijacking (6 neighbors, 6 edges)
           → DLL (123 neighbors, 123 edges)
[RETRIEVE-QUOTA] Query 6/6: ได้สิทธิ์สูงขึ้นตามสิทธิ์ของโปรแกรมที่ถูกหลอกให้โหลดไฟล์ไลบรารีของคนร้าย (Privil...
[RETRIEVE] Query: ได้สิทธิ์สูงขึ้นตามสิทธิ์ของโปรแกรมที่ถูกหลอกให้โหลดไฟล์ไลบรารีของคนร้าย (Privil...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MacMa (0.699), Exploitation for Privilege Escalation (0.479), ProLock (0.385), Privilege Escalation (0.335), Elevated Execution with Prompt (0.046), Abuse Elevation Control Mechanism (0.037), MegaCortex (0.001), Software Discovery (0.001), User Account Management (0.000), Kerberoasting (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → MacMa (28 neighbors, 28 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [84/100] retrieved=747 relevant=3 latency=29616ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 19 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งความเพิ่มเติมว่าพบกา...
[RETRIEVE] Query: เมื่อวันที่ 19 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งความเพิ่มเติมว่าพบกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackConfig (0.013), APT37 (0.010), Data from Local System (0.006), Remote System Discovery (0.003), Data from Network Shared Drive (0.002), FIN8 (0.000), System Network Connections Discovery (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → BackConfig (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → APT37 (42 neighbors, 42 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 2/5: เรียกดูชื่อบัญชีผู้ใช้ที่กำลังทำงานอยู่บนเครื่องที่ยึดครองได้ (System Owner/User...
[RETRIEVE] Query: เรียกดูชื่อบัญชีผู้ใช้ที่กำลังทำงานอยู่บนเครื่องที่ยึดครองได้ (System Owner/User...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Owner/User Discovery (0.675), UPPERCUT (0.623), Get2 (0.449), Kimsuky (0.330), Account Discovery (0.100), APT3 (0.061), System Information Discovery (0.005), System Location Discovery (0.004), System Network Connections Discovery (0.004), Device Driver Discovery (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → UPPERCUT (18 neighbors, 18 edges)
           → Get2 (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 3/5: เรียกดูรายละเอียดระบบปฏิบัติการที่ติดตั้งอยู่บนเครื่อง (System Information Disco...
[RETRIEVE] Query: เรียกดูรายละเอียดระบบปฏิบัติการที่ติดตั้งอยู่บนเครื่อง (System Information Disco...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Systeminfo (0.727), cmd (0.637), SYSCON (0.396), System Information Discovery (0.308), Systeminfo (0.115), System Network Configuration Discovery (0.057), System Time Discovery (0.015), System Owner/User Discovery (0.012), Device Driver Discovery (0.003), Process Discovery (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Systeminfo (14 neighbors, 14 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 4/5: ไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์บนเครื่องเพื่อค้นหาข้อมูลที่ต้องการ (File and Dir...
[RETRIEVE] Query: ไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์บนเครื่องเพื่อค้นหาข้อมูลที่ต้องการ (File and Dir...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DynoWiper (0.875), File and Directory Discovery (0.671), BoomBox (0.412), Kimsuky (0.325), Forfiles (0.308), Cloud Storage Object Discovery (0.074), Network Share Discovery (0.069), Forfiles (0.044), System Information Discovery (0.014), System Owner/User Discovery (0.009)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DynoWiper (10 neighbors, 10 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → BoomBox (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 5/5: เก็บรวบรวมข้อมูลเซสชันการเชื่อมต่อหน้าจอระยะไกลที่ค้างอยู่ ทั้งชื่อผู้ใช้ หมายเล...
[RETRIEVE] Query: เก็บรวบรวมข้อมูลเซสชันการเชื่อมต่อหน้าจอระยะไกลที่ค้างอยู่ ทั้งชื่อผู้ใช้ หมายเล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote System Discovery (0.507), System Network Configuration Discovery (0.220), Wi-Fi Discovery (0.179), Ping (0.139), njRAT (0.117), System Owner/User Discovery (0.045), System Network Connections Discovery (0.032), System Information Discovery (0.020), Machete (0.015), Emotet (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Remote System Discovery (104 neighbors, 104 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → Wi-Fi Discovery (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [85/100] retrieved=594 relevant=4 latency=27947ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 20 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าถูกหลอกให้ติดตั้งโปร...
[RETRIEVE] Query: เมื่อวันที่ 20 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าถูกหลอกให้ติดตั้งโปร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pikabot (0.021), Clambling (0.018), CoinTicker (0.015), EventBot (0.008), Encrypted/Encoded File (0.004), Symmetric Cryptography (0.003), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.003), Lucifer (0.002), Deobfuscate/Decode Files or Information (0.002), Subvert Trust Controls (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Pikabot (24 neighbors, 24 edges)
           → Symmetric Cryptography (188 neighbors, 188 edges)
           → Clambling (35 neighbors, 35 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] Query 2/5: หลอกผู้เสียหายให้ติดตั้งโปรแกรมซื้อขายสินทรัพย์ดิจิทัลปลอมบนเครื่อง Windows (Use...
[RETRIEVE] Query: หลอกผู้เสียหายให้ติดตั้งโปรแกรมซื้อขายสินทรัพย์ดิจิทัลปลอมบนเครื่อง Windows (Use...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Malicious File (0.475), User Execution (0.250), TA505 (0.166), KOPILUWAK (0.088), System Script Proxy Execution (0.069), Malicious Link (0.036), Execution Prevention (0.030), Lucifer (0.013), INC Ransom (0.012), Execution (0.006)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Malicious File (202 neighbors, 202 edges)
           → User Execution (18 neighbors, 18 edges)
           → TA505 (50 neighbors, 50 edges)
           → Msiexec (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 3/5: ตัวติดตั้งโปรแกรมปลอมขอสิทธิ์ผู้ดูแลระบบและให้ผู้เสียหายกดอนุญาตเพื่อดำเนินการติ...
[RETRIEVE] Query: ตัวติดตั้งโปรแกรมปลอมขอสิทธิ์ผู้ดูแลระบบและให้ผู้เสียหายกดอนุญาตเพื่อดำเนินการติ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RatMilad (0.417), GUI Input Capture (0.055), Installer Packages (0.029), GoBear (0.026), Sandworm Team (0.012), Executable Installer File Permissions Weakness (0.009), Software Extensions (0.005), Audit (0.003), RDFSNIFFER (0.002), Malicious Copy and Paste (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RatMilad (18 neighbors, 18 edges)
           → Download New Code at Runtime (42 neighbors, 42 edges)
           → GUI Input Capture (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 4/5: อำพรางเนื้อหาไฟล์โปรแกรมอย่างหนักด้วยไลบรารีเพื่อบิดเบือนโครงสร้างและขัดขวางการว...
[RETRIEVE] Query: อำพรางเนื้อหาไฟล์โปรแกรมอย่างหนักด้วยไลบรารีเพื่อบิดเบือนโครงสร้างและขัดขวางการว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Obfuscated Files or Information (0.981), OBAD (0.962), SynAck (0.960), APT3 (0.946), Deobfuscate/Decode Files or Information (0.878), PUBLOAD (0.826), Encrypted/Encoded File (0.300), Malicious File (0.043), Compression (0.023), Environmental Keying (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → OBAD (2 neighbors, 2 edges)
           → Obfuscated Files or Information (51 neighbors, 51 edges)
[RETRIEVE-QUOTA] Query 5/5: โปรแกรมปกปิดเนื้อหาการรับส่งกับเครื่องสั่งการด้วยการเข้ารหัสแบบสตรีมและกุญแจขนาด...
[RETRIEVE] Query: โปรแกรมปกปิดเนื้อหาการรับส่งกับเครื่องสั่งการด้วยการเข้ารหัสแบบสตรีมและกุญแจขนาด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CORESHELL (0.708), Encrypted Channel (0.273), Symmetric Cryptography (0.178), Torisma (0.157), StarProxy (0.125), ZIPLINE (0.098), Asymmetric Cryptography (0.078), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.043), Encrypted/Encoded File (0.030), Playcrypt (0.009)
[RETRIEVE] Graph expansion: 3 subgraphs
           → CORESHELL (12 neighbors, 12 edges)
           → Symmetric Cryptography (188 neighbors, 188 edges)
           → Encrypted Channel (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [86/100] retrieved=524 relevant=3 latency=35822ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 17 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงช่องทางที่...
[RETRIEVE] Query: เมื่อวันที่ 17 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงช่องทางที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan Australian Intrusions (0.311), Threat Group-3390 (0.111), External Remote Services (0.052), Valid Accounts (0.031), Remote Services (0.017), Remote Desktop Protocol (0.005), User Account Management (0.000), Exploitation of Remote Services (0.000), Remote Service Session Hijacking (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Leviathan Australian Intrusions (27 neighbors, 27 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Threat Group-3390 (81 neighbors, 81 edges)
           → External Remote Services (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] Query 2/9: เข้าถึงเครือข่ายผ่านบริการเชื่อมต่อหน้าจอระยะไกลจากภายนอก (External Remote Servi...
[RETRIEVE] Query: เข้าถึงเครือข่ายผ่านบริการเชื่อมต่อหน้าจอระยะไกลจากภายนอก (External Remote Servi...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Remote Services (0.935), Limit Access to Resource Over Network (0.818), Network Segmentation (0.569), Exploitation of Remote Services (0.245), Remote Access Tools (0.135), Remote Services (0.096), Terminal Services DLL (0.092), Remote Desktop Protocol (0.016), Ember Bear (0.010), Audit (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → External Remote Services (52 neighbors, 52 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Network Segmentation (37 neighbors, 37 edges)
[RETRIEVE-QUOTA] Query 3/9: เข้าถึงเครือข่ายผ่านบริการเครือข่ายส่วนตัวเสมือนจากภายนอก (VPN)...
[RETRIEVE] Query: เข้าถึงเครือข่ายผ่านบริการเครือข่ายส่วนตัวเสมือนจากภายนอก (VPN)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.843), FIN13 (0.773), LAPSUS$ (0.684), External Remote Services (0.567), Web Portal Capture (0.206), Virtual Private Server (0.006), VNC (0.005), LAPSUS$ (0.005), Virtual Private Server (0.005), Kerberoasting (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → FIN13 (57 neighbors, 57 edges)
[RETRIEVE-QUOTA] Query 4/9: ใช้บัญชีผู้ใช้ที่ยังใช้งานได้ซึ่งได้มาก่อนหน้า (Valid Accounts)...
[RETRIEVE] Query: ใช้บัญชีผู้ใช้ที่ยังใช้งานได้ซึ่งได้มาก่อนหน้า (Valid Accounts)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.417), GALLIUM (0.377), Valid Accounts (0.139), Account Discovery (0.067), Compromise Accounts (0.044), Distributed Component Object Model (0.027), Cloud Accounts (0.019), Windows Remote Management (0.019), VajraSpy (0.001), Modify Authentication Process (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → GALLIUM (47 neighbors, 47 edges)
[RETRIEVE-QUOTA] Query 5/9: โจมตีช่องโหว่ของแอปพลิเคชันที่เปิดให้บริการต่อสาธารณะ...
[RETRIEVE] Query: โจมตีช่องโหว่ของแอปพลิเคชันที่เปิดให้บริการต่อสาธารณะ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.696), Leviathan (0.613), Agrius (0.592), Exploitation for Client Execution (0.008), Cobian RAT (0.003), Code Repositories (0.001), Visual Basic (0.001), CrossRAT (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Leviathan (68 neighbors, 68 edges)
           → Agrius (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 6/9: โจมตีช่องโหว่ของอุปกรณ์ไฟร์วอลล์ที่ยังไม่ได้ปรับปรุง...
[RETRIEVE] Query: โจมตีช่องโหว่ของอุปกรณ์ไฟร์วอลล์ที่ยังไม่ได้ปรับปรุง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BONDUPDATER (0.014), SharePoint ToolShell Exploitation (0.004), SysUpdate (0.002), FIN6 (0.001), Cobian RAT (0.001), Visual Basic (0.000), FIN7 (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BONDUPDATER (8 neighbors, 8 edges)
           → SharePoint ToolShell Exploitation (39 neighbors, 39 edges)
           → SysUpdate (32 neighbors, 32 edges)
[RETRIEVE-QUOTA] Query 7/9: โจมตีช่องโหว่ของเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ที่ยังไม่ได้ปรับปรุง...
[RETRIEVE] Query: โจมตีช่องโหว่ของเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ที่ยังไม่ได้ปรับปรุง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BONDUPDATER (0.032), SharePoint ToolShell Exploitation (0.007), TA551 (0.005), APT28 (0.004), SysUpdate (0.001), Email Accounts (0.001), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → BONDUPDATER (8 neighbors, 8 edges)
           → SharePoint ToolShell Exploitation (39 neighbors, 39 edges)
           → TA551 (19 neighbors, 19 edges)
           → Email Addresses (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 8/9: สอบถามข้อมูลจากระบบทะเบียนโดเมนเพื่อรวบรวมรายละเอียดของเครือข่าย...
[RETRIEVE] Query: สอบถามข้อมูลจากระบบทะเบียนโดเมนเพื่อรวบรวมรายละเอียดของเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gather Victim Network Information (0.176), Domain Registration (0.110), Active DNS (0.062), Reg (0.020), Remsec (0.013), Passive DNS (0.006), CrossRAT (0.000), Visual Basic (0.000), The White Company (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Gather Victim Network Information (11 neighbors, 11 edges)
           → Domain Registration (0 neighbors, 0 edges)
           → Active DNS (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 9/9: ตรวจสอบว่าเครื่องแต่ละเครื่องติดตั้งโปรแกรมป้องกันไวรัสยี่ห้อใด (Security Softwa...
[RETRIEVE] Query: ตรวจสอบว่าเครื่องแต่ละเครื่องติดตั้งโปรแกรมป้องกันไวรัสยี่ห้อใด (Security Softwa...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kasidet (0.650), DEFENSOR ID (0.270), Security Software Discovery (0.260), down_new (0.188), PUBLOAD (0.082), Software Discovery (0.058), Device Driver Discovery (0.047), Application Window Discovery (0.015), Backup Software Discovery (0.014), System Information Discovery (0.002)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Kasidet (10 neighbors, 10 edges)
           → Security Software Discovery (144 neighbors, 144 edges)
           → DEFENSOR ID (5 neighbors, 5 edges)
           → Software Discovery (56 neighbors, 56 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [87/100] retrieved=239 relevant=5 latency=38632ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 16 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความเพิ่มเติมถึงจุดเริ่มต้นที่ลูกค...
[RETRIEVE] Query: เมื่อวันที่ 16 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความเพิ่มเติมถึงจุดเริ่มต้นที่ลูกค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pony (0.403), SYSCON (0.110), User Training (0.073), User Execution (0.049), Malicious File (0.046), User Training (0.033), Malicious Link (0.013), Spearphishing Link (0.008), Maze (0.007), Exploitation for Client Execution (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Pony (16 neighbors, 16 edges)
           → Malicious Link (93 neighbors, 93 edges)
           → SYSCON (6 neighbors, 6 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] Query 2/9: อีเมลหลอกลวงแบบ Spearphishing เจาะจงเนื้อหาให้ตรงกับผู้รับแต่ละราย...
[RETRIEVE] Query: อีเมลหลอกลวงแบบ Spearphishing เจาะจงเนื้อหาให้ตรงกับผู้รับแต่ละราย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Phishing (0.354), Spearphishing Attachment (0.220), Spearphishing Attachment (0.176), Spearphishing Service (0.134), Spearphishing Link (0.124), Spearphishing Voice (0.070), LODEINFO (0.045), Spearphishing Voice (0.026), Saint Bear (0.012), Operation Dream Job (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Phishing (23 neighbors, 23 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/9: อีเมลแนบไฟล์อันตรายและลิงก์มุ่งให้ผู้รับเปิดใช้งาน...
[RETRIEVE] Query: อีเมลแนบไฟล์อันตรายและลิงก์มุ่งให้ผู้รับเปิดใช้งาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ZxxZ (0.585), Lokibot (0.560), Spearphishing Attachment (0.324), GLOOXMAIL (0.004), IMAPLoader (0.003), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → ZxxZ (15 neighbors, 15 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Lokibot (29 neighbors, 29 edges)
[RETRIEVE-QUOTA] Query 4/9: ผู้เสียหายกดเปิดลิงก์ตามเทคนิค User Execution: Malicious Link...
[RETRIEVE] Query: ผู้เสียหายกดเปิดลิงก์ตามเทคนิค User Execution: Malicious Link...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Malicious Link (0.956), Kerrdown (0.871), User Execution (0.559), Link Target (0.557), Malicious File (0.541), Execution (0.276), User Training (0.162), Spearphishing Link (0.102), Exploitation for Client Execution (0.013), Water Curupira Pikabot Distribution (0.011)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Malicious Link (93 neighbors, 93 edges)
           → Kerrdown (12 neighbors, 12 edges)
           → User Execution (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 5/9: ผู้เสียหายเปิดไฟล์แนบอันตรายตามเทคนิค User Execution: Malicious File...
[RETRIEVE] Query: ผู้เสียหายเปิดไฟล์แนบอันตรายตามเทคนิค User Execution: Malicious File...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Malicious File (0.967), RTM (0.899), Kerrdown (0.825), User Execution (0.761), Execution (0.455), Malicious Link (0.349), User Training (0.139), Executable Installer File Permissions Weakness (0.121), Execution Prevention (0.100), Exploitation for Client Execution (0.068)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Malicious File (202 neighbors, 202 edges)
           → User Execution (18 neighbors, 18 edges)
           → RTM (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 6/9: หน้าเว็บหลอกให้ผู้เสียหายกดภาพเพื่อดาวน์โหลดไฟล์สคริปต์ JavaScript โดยไม่ทราบ...
[RETRIEVE] Query: หน้าเว็บหลอกให้ผู้เสียหายกดภาพเพื่อดาวน์โหลดไฟล์สคริปต์ JavaScript โดยไม่ทราบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Contagious Interview (0.070), BeaverTail (0.056), Avaddon (0.055), HTML Smuggling (0.027), SocGholish (0.023), JavaScript (0.014), Drive-by Compromise (0.013), Malicious Copy and Paste (0.005), APT32 (0.004), KOPILUWAK (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Contagious Interview (58 neighbors, 58 edges)
           → JavaScript (76 neighbors, 76 edges)
           → Avaddon (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 7/9: ไฟล์สคริปต์ JavaScript ถูกเปิดและเริ่มทำงานบนเครื่องผู้เสียหาย...
[RETRIEVE] Query: ไฟล์สคริปต์ JavaScript ถูกเปิดและเริ่มทำงานบนเครื่องผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NanHaiShu (0.343), FIN7 (0.233), JavaScript (0.034), Malicious File (0.014), BeaverTail (0.008), User Execution (0.005), HTML Smuggling (0.002), KOPILUWAK (0.001), APT32 (0.001), TA505 (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → NanHaiShu (13 neighbors, 13 edges)
           → JavaScript (76 neighbors, 76 edges)
           → FIN7 (86 neighbors, 86 edges)
[RETRIEVE-QUOTA] Query 8/9: สคริปต์ JavaScript ติดต่อเครื่องสั่งการของคนร้ายเพื่อดาวน์โหลดโปรแกรมม้าโทรจัน...
[RETRIEVE] Query: สคริปต์ JavaScript ติดต่อเครื่องสั่งการของคนร้ายเพื่อดาวน์โหลดโปรแกรมม้าโทรจัน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BeaverTail (0.093), APT32 (0.010), Agent Tesla (0.007), KOPILUWAK (0.005), JavaScript (0.003), OopsIE (0.002), Trojan.Karagany (0.001), Shamoon (0.001), HTML Smuggling (0.000), TA505 (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BeaverTail (24 neighbors, 24 edges)
           → APT32 (93 neighbors, 93 edges)
           → JavaScript (76 neighbors, 76 edges)
[RETRIEVE-QUOTA] Query 9/9: ดาวน์โหลดและติดตั้งโปรแกรมม้าโทรจันจากเครื่องสั่งการของคนร้ายบนเครื่องผู้เสียหาย...
[RETRIEVE] Query: ดาวน์โหลดและติดตั้งโปรแกรมม้าโทรจันจากเครื่องสั่งการของคนร้ายบนเครื่องผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Machete (0.203), Pony (0.073), OopsIE (0.032), Hancitor (0.031), Shamoon (0.028), Cardinal RAT (0.001), CrossRAT (0.001), PUNCHTRACK (0.001), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Machete (42 neighbors, 42 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Pony (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [88/100] retrieved=265 relevant=3 latency=41705ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 13 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Query: เมื่อวันที่ 13 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Storm-1811 (0.045), POWERSTATS (0.033), POWERSTATS (0.030), FIN7 (0.007), PowerShell Profile (0.006), POWERSOURCE (0.003), Forced Authentication (0.000), PowerShell (0.000), Disable or Remove Feature or Program (0.000), Input Injection (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Storm-1811 (38 neighbors, 38 edges)
           → Input Capture (20 neighbors, 20 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → PowerShell (241 neighbors, 241 edges)
[RETRIEVE-QUOTA] Query 2/7: สร้างช่องทางสื่อสารระหว่างกระบวนการเพื่อหลอกบริการระบบและสวมสิทธิ์โทเคนของบริการ...
[RETRIEVE] Query: สร้างช่องทางสื่อสารระหว่างกระบวนการเพื่อหลอกบริการระบบและสวมสิทธิ์โทเคนของบริการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PipeMon (0.481), FIN6 (0.278), APT28 (0.206), Protocol or Service Impersonation (0.181), Token Impersonation/Theft (0.112), Access Token Manipulation (0.079), Named Pipe Metadata (0.033), Impersonation (0.014), Temporary Elevated Cloud Access (0.002), C0027 (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → PipeMon (24 neighbors, 24 edges)
           → Create Process with Token (19 neighbors, 19 edges)
           → FIN6 (52 neighbors, 52 edges)
           → Access Token Manipulation (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 3/7: เรียกใช้สคริปต์จากเครื่องภายนอกผ่าน PowerShell...
[RETRIEVE] Query: เรียกใช้สคริปต์จากเครื่องภายนอกผ่าน PowerShell...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: POWRUNER (0.285), PowerShell (0.160), PowerSploit (0.031), AADInternals (0.029), POWERSOURCE (0.022), PowerShell Profile (0.020), PowerExchange (0.016), Invoke-PSImage (0.010), POWERSTATS (0.004), Disable or Remove Feature or Program (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → POWRUNER (21 neighbors, 21 edges)
           → PowerShell (241 neighbors, 241 edges)
           → AADInternals (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 4/7: ดึงค่ารหัสผ่านจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่อง (LSASS Memory)...
[RETRIEVE] Query: ดึงค่ารหัสผ่านจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่อง (LSASS Memory)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lslsass (0.819), LaZagne (0.768), LSASS Memory (0.463), LSA Secrets (0.046), Modify Authentication Process (0.022), 2016 Ukraine Electric Power Attack (0.014), LSASS Driver (0.008), Security Account Manager (0.006), Credential Access Protection (0.001), Privileged Process Integrity (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → LaZagne (22 neighbors, 22 edges)
           → LSASS Memory (89 neighbors, 89 edges)
           → Lslsass (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 5/7: รวบรวมไฟล์ข้อความที่มีข้อมูลจากเครื่อง...
[RETRIEVE] Query: รวบรวมไฟล์ข้อความที่มีข้อมูลจากเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MESSAGETAP (0.241), Ramsay (0.201), Data from Network Shared Drive (0.057), Systeminfo (0.040), spwebmember (0.008), Wevtutil (0.004), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → MESSAGETAP (9 neighbors, 9 edges)
           → Automated Collection (77 neighbors, 77 edges)
           → Ramsay (39 neighbors, 39 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 6/7: บีบอัดไฟล์ข้อความที่รวบรวมไว้รวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดที่เปลี่ยนชื่อไฟล์...
[RETRIEVE] Query: บีบอัดไฟล์ข้อความที่รวบรวมไว้รวมเป็นไฟล์เดียวด้วยโปรแกรมบีบอัดที่เปลี่ยนชื่อไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Software Packing (0.032), Compression (0.031), TAINTEDSCRIBE (0.026), Space after Filename (0.006), TAINTEDSCRIBE (0.003), Compiled HTML File (0.003), TAINTEDSCRIBE (0.002), admin@338 (0.002), Change Default File Association (0.001), Masquerade File Type (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Software Packing (106 neighbors, 106 edges)
           → Compression (38 neighbors, 38 edges)
           → TAINTEDSCRIBE (17 neighbors, 17 edges)
           → Archive Collected Data (62 neighbors, 62 edges)
[RETRIEVE-QUOTA] Query 7/7: พักเก็บไฟล์บีบอัดที่รวบรวมไว้เพื่อเตรียมนำออกจากองค์กร (Data Staged)...
[RETRIEVE] Query: พักเก็บไฟล์บีบอัดที่รวบรวมไว้เพื่อเตรียมนำออกจากองค์กร (Data Staged)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Staged (0.207), QUIETCANARY (0.096), Local Data Staging (0.038), Scattered Spider (0.014), Kevin (0.010), menuPass (0.010), Remote Data Staging (0.006), Stage Capabilities (0.000), Systemd Service (0.000), cmd (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Data Staged (13 neighbors, 13 edges)
           → QUIETCANARY (10 neighbors, 10 edges)
           → Local Data Staging (138 neighbors, 138 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [89/100] retrieved=353 relevant=3 latency=33022ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงเครื่องมือ...
[RETRIEVE] Query: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงเครื่องมือ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.461), HOMEFRY (0.405), Suckfly (0.318), OS Credential Dumping (0.221), BlackByte (0.218), Windows Credential Editor (0.205), Credential Access (0.014), Credential Access Protection (0.004), Credential Stuffing (0.001), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → HOMEFRY (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 2/8: รันชุดสคริปต์สำเร็จรูปบนเครื่องที่ยึดครองได้...
[RETRIEVE] Query: รันชุดสคริปต์สำเร็จรูปบนเครื่องที่ยึดครองได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PsExec (0.020), SILENTTRINITY (0.016), Get2 (0.015), Portable Executable Injection (0.004), Pupy (0.003), Visual Basic (0.001), CrossRAT (0.001), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PsExec (49 neighbors, 49 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Reflective Code Loading (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 3/8: ตรวจสอบหาช่องทางยกระดับสิทธิ์บนเครือข่าย...
[RETRIEVE] Query: ตรวจสอบหาช่องทางยกระดับสิทธิ์บนเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Privilege Escalation (0.383), SILENTTRINITY (0.029), APT33 (0.022), Internet Connection Discovery (0.008), Abuse Elevation Control Mechanism (0.004), Cobian RAT (0.002), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Privilege Escalation (96 neighbors, 96 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
           → System Service Discovery (71 neighbors, 71 edges)
[RETRIEVE-QUOTA] Query 4/8: ปิดการทำงานของโปรแกรมป้องกันไวรัส...
[RETRIEVE] Query: ปิดการทำงานของโปรแกรมป้องกันไวรัส...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pysa (0.246), BRATA (0.029), Disable or Remove Feature or Program (0.004), Execution Prevention (0.003), Limit Software Installation (0.002), Inhibit System Recovery (0.001), Cardinal RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Pysa (16 neighbors, 16 edges)
           → Disable or Modify Tools (142 neighbors, 142 edges)
           → BRATA (27 neighbors, 27 edges)
           → Disable or Modify Tools (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 5/8: ลบไฟล์บันทึกเหตุการณ์ของระบบ...
[RETRIEVE] Query: ลบไฟล์บันทึกเหตุการณ์ของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Clear Windows Event Logs (0.364), RansomHub (0.352), gh0st RAT (0.141), Windows Registry Key Deletion (0.018), Snapshot Deletion (0.005), Active Directory Object Deletion (0.001), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → RansomHub (21 neighbors, 21 edges)
           → gh0st RAT (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 6/8: ค้นหาข้อมูลรับรองตัวตนที่เก็บไว้โดยไม่ได้ป้องกันในระบบ...
[RETRIEVE] Query: ค้นหาข้อมูลรับรองตัวตนที่เก็บไว้โดยไม่ได้ป้องกันในระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Unsecured Credentials (0.871), Credentials in Registry (0.522), Audit (0.499), Credentials In Files (0.444), Pacu (0.308), PowerSploit (0.032), Modify Authentication Process (0.007), AS-REP Roasting (0.003), Windows Credential Manager (0.002), DEFENSOR ID (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Unsecured Credentials (27 neighbors, 27 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 7/8: ใช้เครื่องมือ Credential Dumping ดึงค่ารหัสผ่านออกจากหน่วยความจำ...
[RETRIEVE] Query: ใช้เครื่องมือ Credential Dumping ดึงค่ารหัสผ่านออกจากหน่วยความจำ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LaZagne (0.937), OS Credential Dumping (0.713), Windows Credential Editor (0.511), Axiom (0.373), Credentials In Files (0.351), pwdump (0.348), pwdump (0.319), Credential Access (0.214), Poseidon Group (0.203), Credential Access Protection (0.119)
[RETRIEVE] Graph expansion: 3 subgraphs
           → LaZagne (22 neighbors, 22 edges)
           → LSASS Memory (89 neighbors, 89 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 8/8: ยกระดับสิทธิ์จนได้บัญชีผู้ดูแลโดเมนขององค์กร...
[RETRIEVE] Query: ยกระดับสิทธิ์จนได้บัญชีผู้ดูแลโดเมนขององค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operating System Configuration (0.144), Privileged Account Management (0.105), Domain Accounts (0.074), Domain Account (0.024), Additional Local or Domain Groups (0.001), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Operating System Configuration (39 neighbors, 39 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Privileged Account Management (112 neighbors, 112 edges)
           → Domain Accounts (47 neighbors, 47 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [90/100] retrieved=234 relevant=4 latency=35232ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 6 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Query: เมื่อวันที่ 6 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.014), Seth-Locker (0.013), Clambling (0.012), Clambling (0.009), Ursnif (0.005), APT-C-36 (0.002), Subvert Trust Controls (0.000), Internal Spearphishing (0.000), Data Encrypted for Impact (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Clambling (35 neighbors, 35 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] Query 2/7: อีเมล Spearphishing เขียนถึงเจ้าหน้าที่โดยเฉพาะพร้อมลิงก์อันตราย...
[RETRIEVE] Query: อีเมล Spearphishing เขียนถึงเจ้าหน้าที่โดยเฉพาะพร้อมลิงก์อันตราย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Spearphishing Link (0.834), Spearphishing Link (0.428), admin@338 (0.343), Spearphishing Attachment (0.291), BITTER (0.136), Spearphishing Attachment (0.092), Spearphishing Service (0.016), Operation Dream Job (0.004), Spearphishing Voice (0.003), Spearphishing Voice (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Spearphishing Link (93 neighbors, 93 edges)
           → Spearphishing Link (22 neighbors, 22 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
[RETRIEVE-QUOTA] Query 3/7: ดาวน์โหลดไฟล์ตัวปล่อยโปรแกรมอันตรายลงในเครื่อง...
[RETRIEVE] Query: ดาวน์โหลดไฟล์ตัวปล่อยโปรแกรมอันตรายลงในเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: GuLoader (0.377), Hancitor (0.172), BadPatch (0.071), Xbash (0.056), P8RAT (0.047), CrossRAT (0.002), Cobian RAT (0.002), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → GuLoader (12 neighbors, 12 edges)
           → Hancitor (14 neighbors, 14 edges)
           → BadPatch (12 neighbors, 12 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 4/7: เจ้าหน้าที่เปิดไฟล์ที่ดาวน์โหลดมาด้วยตนเองเพื่อให้โปรแกรมทำงาน (User Execution)...
[RETRIEVE] Query: เจ้าหน้าที่เปิดไฟล์ที่ดาวน์โหลดมาด้วยตนเองเพื่อให้โปรแกรมทำงาน (User Execution)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: User Execution (0.117), LAPSUS$ (0.011), BackConfig (0.011), Executable Installer File Permissions Weakness (0.011), Script Execution (0.005), PsExec (0.002), User Account Control (0.002), APT3 (0.001), cmd (0.001), Execution (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → User Execution (18 neighbors, 18 edges)
           → Executable Installer File Permissions Weakness (8 neighbors, 8 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] Query 5/7: วางโปรแกรมควบคุมระยะไกลฝังตัวลงบนเครื่อง...
[RETRIEVE] Query: วางโปรแกรมควบคุมระยะไกลฝังตัวลงบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HermeticWizard (0.050), RemoteCMD (0.044), xCmd (0.036), Regsvr32 (0.020), CrackMapExec (0.012), Cobian RAT (0.007), CrossRAT (0.002), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → HermeticWizard (16 neighbors, 16 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → RemoteCMD (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/7: เรียกดูรายชื่อกลุ่มสิทธิ์ในโดเมนขององค์กร...
[RETRIEVE] Query: เรียกดูรายชื่อกลุ่มสิทธิ์ในโดเมนขององค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: dsquery (0.555), Domain Groups (0.337), Nltest (0.265), C0015 (0.262), Domain Account (0.128), Group Metadata (0.112), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → dsquery (9 neighbors, 9 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → C0015 (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 7/7: เรียกดูรายการบริการที่กำลังทำงานอยู่บนเครื่อง (System Services Discovery)...
[RETRIEVE] Query: เรียกดูรายการบริการที่กำลังทำงานอยู่บนเครื่อง (System Services Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.845), Ixeshe (0.446), System Service Discovery (0.444), System Information Discovery (0.015), System Network Connections Discovery (0.014), Process Discovery (0.013), System Owner/User Discovery (0.008), System Location Discovery (0.004), DnsSystem (0.003), SharkBot (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → System Service Discovery (71 neighbors, 71 edges)
           → Ixeshe (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [91/100] retrieved=308 relevant=3 latency=27096ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 3 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายได้...
[RETRIEVE] Query: เมื่อวันที่ 3 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT38 (0.513), APT28 (0.454), Password Spraying (0.288), CrackMapExec (0.233), APT3 (0.222), Brute Force (0.095), Password Cracking (0.042), Password Managers (0.003), Credentials from Web Browsers (0.002), Password Policy Discovery (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT38 (62 neighbors, 62 edges)
           → Brute Force (34 neighbors, 34 edges)
           → APT28 (124 neighbors, 124 edges)
           → Password Spraying (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 2/6: หลบเลี่ยงกลไกยืนยันก่อนยกระดับสิทธิ์เพื่อให้โปรแกรมทำงานด้วยสิทธิ์ผู้ดูแลระบบโดย...
[RETRIEVE] Query: หลบเลี่ยงกลไกยืนยันก่อนยกระดับสิทธิ์เพื่อให้โปรแกรมทำงานด้วยสิทธิ์ผู้ดูแลระบบโดย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bypass User Account Control (0.975), RCSession (0.680), User Account Control (0.654), User Account Control (0.640), Abuse Elevation Control Mechanism (0.350), GUI Input Capture (0.350), LockBit 2.0 (0.307), UACMe (0.222), UACMe (0.177), User Account Management (0.006)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bypass User Account Control (70 neighbors, 70 edges)
           → RCSession (24 neighbors, 24 edges)
           → User Account Control (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 3/6: Brute Force: Password Cracking ถอดรหัสค่าแฮชรหัสผ่านที่ได้มานอกระบบ...
[RETRIEVE] Query: Brute Force: Password Cracking ถอดรหัสค่าแฮชรหัสผ่านที่ได้มานอกระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT3 (0.313), Brute Force (0.257), Password Cracking (0.163), Cachedump (0.054), Net Crawler (0.025), Password Policy Discovery (0.025), Password Policies (0.017), Cachedump (0.011), Compute Hijacking (0.004), Password Managers (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT3 (50 neighbors, 50 edges)
           → Password Cracking (12 neighbors, 12 edges)
           → Brute Force (34 neighbors, 34 edges)
[RETRIEVE-QUOTA] Query 4/6: Brute Force: Password Spraying นำรหัสผ่านที่คาดเดาง่ายไปลองล็อกอินกับบัญชีจำนวนม...
[RETRIEVE] Query: Brute Force: Password Spraying นำรหัสผ่านที่คาดเดาง่ายไปลองล็อกอินกับบัญชีจำนวนม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Password Spraying (0.969), APT28 (0.826), APT28 (0.640), Account Use Policies (0.457), Brute Force (0.354), Password Guessing (0.278), Password Policy Discovery (0.076), CrackMapExec (0.058), Password Cracking (0.004), Password Policies (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Password Spraying (23 neighbors, 23 edges)
           → APT28 (124 neighbors, 124 edges)
           → Password Guessing (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 5/6: Credentials from Web Browsers อ่านชื่อผู้ใช้และรหัสผ่านที่เว็บเบราว์เซอร์บันทึกไ...
[RETRIEVE] Query: Credentials from Web Browsers อ่านชื่อผู้ใช้และรหัสผ่านที่เว็บเบราว์เซอร์บันทึกไ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.988), Lizar (0.926), LaZagne (0.628), XLoader (0.513), SUGARDUMP (0.472), Web Credential Usage (0.042), Credentials from Password Stores (0.038), Forge Web Credentials (0.028), Windows Credential Manager (0.027), Browser Information Discovery (0.021)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → Lizar (29 neighbors, 29 edges)
           → LaZagne (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 6/6: ส่งข้อมูลที่รวบรวมได้ออกไปผ่านโพรโทคอลรับส่งไฟล์ที่ไม่ได้เข้ารหัสลับ (Exfiltrati...
[RETRIEVE] Query: ส่งข้อมูลที่รวบรวมได้ออกไปผ่านโพรโทคอลรับส่งไฟล์ที่ไม่ได้เข้ารหัสลับ (Exfiltrati...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Unencrypted Non-C2 Protocol (0.966), Exfiltration Over Alternative Protocol (0.964), ftp (0.930), Chaes (0.916), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.894), Automated Exfiltration (0.875), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.608), Kobalos (0.605), Scheduled Transfer (0.603), AADInternals (0.522)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [92/100] retrieved=254 relevant=4 latency=32331ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 18 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความเพิ่มเติมถึงข้อมู...
[RETRIEVE] Query: เมื่อวันที่ 18 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความเพิ่มเติมถึงข้อมู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.144), MuddyWater (0.115), njRAT (0.080), Lokibot (0.004), Unsecured Credentials (0.003), FIN8 (0.000), Gamaredon Group (0.000), Named Pipe Metadata (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → MuddyWater (89 neighbors, 89 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 2/6: ดึงชื่อผู้ใช้และรหัสผ่านที่เว็บเบราว์เซอร์บันทึกไว้ในเครื่อง (Credentials from W...
[RETRIEVE] Query: ดึงชื่อผู้ใช้และรหัสผ่านที่เว็บเบราว์เซอร์บันทึกไว้ในเครื่อง (Credentials from W...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.979), PLEAD (0.834), TrickBot (0.827), LaZagne (0.539), SUGARDUMP (0.506), Credentials In Files (0.058), Forge Web Credentials (0.052), Web Credential Usage (0.028), Windows Credential Manager (0.021), Browser Information Discovery (0.016)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → PLEAD (16 neighbors, 16 edges)
           → TrickBot (57 neighbors, 57 edges)
[RETRIEVE-QUOTA] Query 3/6: ขโมยโทเค็นสิทธิ์จากกระบวนการของผู้ใช้รายอื่น (Access Token Manipulation)...
[RETRIEVE] Query: ขโมยโทเค็นสิทธิ์จากกระบวนการของผู้ใช้รายอื่น (Access Token Manipulation)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Access Token Manipulation (0.956), Duqu (0.872), Application Access Token (0.828), Token Impersonation/Theft (0.706), SslMM (0.691), KillDisk (0.650), Steal Application Access Token (0.614), Create Process with Token (0.307), Account Manipulation (0.068), Transmitted Data Manipulation (0.011)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Access Token Manipulation (33 neighbors, 33 edges)
           → Application Access Token (14 neighbors, 14 edges)
           → Duqu (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 4/6: สวมสิทธิ์โทเค็นเพื่อสั่งงานในนามของผู้ใช้รายอื่น (Token Impersonation/Theft)...
[RETRIEVE] Query: สวมสิทธิ์โทเค็นเพื่อสั่งงานในนามของผู้ใช้รายอื่น (Token Impersonation/Theft)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Token Impersonation/Theft (0.979), Shamoon (0.925), SILENTTRINITY (0.921), Havoc (0.780), Access Token Manipulation (0.722), Create Process with Token (0.588), Make and Impersonate Token (0.550), Protocol or Service Impersonation (0.065), Impersonation (0.028), Temporary Elevated Cloud Access (0.017)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Token Impersonation/Theft (26 neighbors, 26 edges)
           → Shamoon (24 neighbors, 24 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
[RETRIEVE-QUOTA] Query 5/6: ค้นหาไฟล์กุญแจส่วนตัวสำหรับยืนยันตัวตนในเครื่อง (Unsecured Credentials: Private ...
[RETRIEVE] Query: ค้นหาไฟล์กุญแจส่วนตัวสำหรับยืนยันตัวตนในเครื่อง (Unsecured Credentials: Private ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Private Keys (0.828), Unsecured Credentials (0.714), Credentials In Files (0.269), AADInternals (0.133), Pacu (0.065), Chat Messages (0.033), Keychain (0.019), PowerSploit (0.014), Windows Credential Manager (0.007), Forge Web Credentials (0.003)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Private Keys (26 neighbors, 26 edges)
           → Unsecured Credentials (27 neighbors, 27 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 6/6: คัดลอกไฟล์กุญแจส่วนตัวที่ไม่มีรหัสผ่านป้องกันออกจากเครื่อง (Data from Local Syst...
[RETRIEVE] Query: คัดลอกไฟล์กุญแจส่วนตัวที่ไม่มีรหัสผ่านป้องกันออกจากเครื่อง (Data from Local Syst...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data from Local System (0.259), Octopus (0.180), PowerSploit (0.111), Bandook (0.090), Keychain (0.007), LSASS Memory (0.006), Lslsass (0.004), LSA Secrets (0.003), Local Account (0.001), Systemctl (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Data from Local System (232 neighbors, 232 edges)
           → Octopus (20 neighbors, 20 edges)
           → PowerSploit (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [93/100] retrieved=246 relevant=3 latency=33987ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 14 ตุลาคม 2564 การประปาส่วนภูมิภาคสาขาหนึ่งแจ้งความว่าระบบควบคุมการผ...
[RETRIEVE] Query: เมื่อวันที่ 14 ตุลาคม 2564 การประปาส่วนภูมิภาคสาขาหนึ่งแจ้งความว่าระบบควบคุมการผ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MuddyWater (0.002), SMS Pumping (0.000), CharmPower (0.000), ccf32 (0.000), BendyBear (0.000), Fysbis (0.000), Samurai (0.000), Supply Chain Compromise (0.000), Data Encoding (0.000), Standard Encoding (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → MuddyWater (89 neighbors, 89 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → SMS Pumping (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 2/9: อีเมล Phishing ที่เขียนถึงเจ้าหน้าที่เป็นรายบุคคลพร้อมไฟล์แนบหลอกลวง...
[RETRIEVE] Query: อีเมล Phishing ที่เขียนถึงเจ้าหน้าที่เป็นรายบุคคลพร้อมไฟล์แนบหลอกลวง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chaes (0.352), Molerats (0.337), Spearphishing Attachment (0.231), Spearphishing Attachment (0.109), Phishing (0.099), VOID MANTICORE (0.021), Written Content (0.008), Phishing for Information (0.004), Spearphishing Service (0.004), Kimsuky (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chaes (28 neighbors, 28 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Molerats (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 3/9: เปิดไฟล์แนบเพื่อติดตั้งโปรแกรมอันตรายและโปรแกรมเรียกค่าไถ่บนเครื่อง...
[RETRIEVE] Query: เปิดไฟล์แนบเพื่อติดตั้งโปรแกรมอันตรายและโปรแกรมเรียกค่าไถ่บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CLAIMLOADER (0.687), Pony (0.238), Flagpro (0.030), CLAIMLOADER (0.020), Latrodectus (0.010), EvilGrab (0.009), BadPatch (0.006), OopsIE (0.003), P8RAT (0.003), Hancitor (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → CLAIMLOADER (12 neighbors, 12 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Pony (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/9: อาศัยช่องโหว่ของบริการและแอปพลิเคชันที่เปิดให้เข้าถึงจากอินเทอร์เน็ต...
[RETRIEVE] Query: อาศัยช่องโหว่ของบริการและแอปพลิเคชันที่เปิดให้เข้าถึงจากอินเทอร์เน็ต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.249), Web Services (0.004), Cobian RAT (0.003), P.A.S. Webshell (0.001), Inception (0.001), Visual Basic (0.000), CrossRAT (0.000), 4H RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Web Services (9 neighbors, 9 edges)
           → Cobian RAT (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 5/9: เข้าใช้งานเครือข่ายของหน่วยงานจากระยะไกล...
[RETRIEVE] Query: เข้าใช้งานเครือข่ายของหน่วยงานจากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Remote Services (0.468), Network Segmentation (0.189), Limit Access to Resource Over Network (0.062), VERMIN (0.019), Remote Services (0.019), Net (0.017), Net (0.016), Remote Service Session Hijacking (0.011), Windows Remote Management (0.006), Koadic (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → External Remote Services (52 neighbors, 52 edges)
           → Network Segmentation (37 neighbors, 37 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 6/9: ขยายการเข้าถึงไปยังเครื่องอื่นในเครือข่ายควบคุม...
[RETRIEVE] Query: ขยายการเข้าถึงไปยังเครื่องอื่นในเครือข่ายควบคุม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Other Network Medium (0.093), Limit Access to Resource Over Network (0.033), Network Device CLI (0.018), Limit Access to Resource Over Network (0.015), Additional Local or Domain Groups (0.008), IPsec Helper (0.002), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Hardware Additions (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 7/9: เข้าถึงอุปกรณ์ควบคุมจนหน่วยงานอาจสูญเสียการควบคุมกระบวนการผลิต...
[RETRIEVE] Query: เข้าถึงอุปกรณ์ควบคุมจนหน่วยงานอาจสูญเสียการควบคุมกระบวนการผลิต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Compromise Hardware Supply Chain (0.001), User Guidance (0.001), Supply Chain Compromise (0.001), FIN7 (0.000), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), 4H RAT (0.000), The White Company (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Compromise Hardware Supply Chain (4 neighbors, 4 edges)
           → User Guidance (49 neighbors, 49 edges)
           → Remote Access Software (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 8/9: ทำให้ระบบควบคุมการผลิตน้ำประปาอาจหยุดให้บริการ...
[RETRIEVE] Query: ทำให้ระบบควบคุมการผลิตน้ำประปาอาจหยุดให้บริการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Service Stop (0.003), Pysa (0.001), ROADSWEEP (0.000), Application or System Exploitation (0.000), Do Not Mitigate (0.000), OS Exhaustion Flood (0.000), Netwalker (0.000), Application Exhaustion Flood (0.000), Clop (0.000), System Shutdown/Reboot (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Service Stop (61 neighbors, 61 edges)
           → Pysa (16 neighbors, 16 edges)
           → Application or System Exploitation (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 9/9: ทำให้ข้อมูลอ่อนไหวของหน่วยงานอาจรั่วไหลออกไป...
[RETRIEVE] Query: ทำให้ข้อมูลอ่อนไหวของหน่วยงานอาจรั่วไหลออกไป...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Transmitted Data Manipulation (0.004), Stored Data Manipulation (0.002), Runtime Data Manipulation (0.002), Trusted Relationship (0.001), Data from Information Repositories (0.001), FoggyWeb (0.000), Business Relationships (0.000), Clambling (0.000), Conti (0.000), CharmPower (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Transmitted Data Manipulation (9 neighbors, 9 edges)
           → Stored Data Manipulation (9 neighbors, 9 edges)
           → Runtime Data Manipulation (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [94/100] retrieved=682 relevant=2 latency=41337ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 20 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนสุ...
[RETRIEVE] Query: เมื่อวันที่ 20 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนสุ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.070), admin@338 (0.008), APT-C-36 (0.007), File Deletion (0.004), Wingbird (0.004), Ursnif (0.002), Ingress Tool Transfer (0.001), System Script Proxy Execution (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → admin@338 (19 neighbors, 19 edges)
           → System Information Discovery (426 neighbors, 426 edges)
[RETRIEVE-QUOTA] Query 2/5: สั่งโปรแกรมฝังตัวเปิดอ่านไฟล์บันทึกผลการติดตั้งผ่าน Windows Command Shell เพื่อต...
[RETRIEVE] Query: สั่งโปรแกรมฝังตัวเปิดอ่านไฟล์บันทึกผลการติดตั้งผ่าน Windows Command Shell เพื่อต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BONDUPDATER (0.125), LookBack (0.090), Windows Command Shell (0.007), cmd (0.006), cmd (0.004), SUGARUSH (0.003), Command and Scripting Interpreter (0.003), Indirect Command Execution (0.003), Shell History (0.001), Clear Command History (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BONDUPDATER (8 neighbors, 8 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → LookBack (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 3/5: สั่งลบไฟล์และร่องรอยที่ทิ้งไว้บนเครื่องเป้าหมายเครื่องที่สี่ทั้งหมด (Indicator R...
[RETRIEVE] Query: สั่งลบไฟล์และร่องรอยที่ทิ้งไว้บนเครื่องเป้าหมายเครื่องที่สี่ทั้งหมด (Indicator R...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Indicator Removal (0.279), Bankshot (0.189), Donut (0.135), Indicator Removal from Tools (0.099), BPFDoor (0.078), Remote Data Storage (0.035), File Deletion (0.008), Image Deletion (0.001), Account Access Removal (0.000), Lifecycle-Triggered Deletion (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Indicator Removal (45 neighbors, 45 edges)
           → Bankshot (26 neighbors, 26 edges)
           → Donut (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 4/5: สั่งโปรแกรมฝังตัวเรียกดูรายละเอียดการตั้งค่าเครือข่ายของเครื่องแม่ข่ายจดหมาย...
[RETRIEVE] Query: สั่งโปรแกรมฝังตัวเรียกดูรายละเอียดการตั้งค่าเครือข่ายของเครื่องแม่ข่ายจดหมาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Emissary (0.029), CreepySnail (0.023), CharmPower (0.017), ifconfig (0.006), Milan (0.006), Network Device Configuration Dump (0.005), ipconfig (0.004), KernelCallbackTable (0.001), Ptrace System Calls (0.000), route (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Emissary (16 neighbors, 16 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → CreepySnail (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 5/5: ส่งไฟล์บันทึกจดหมายอิเล็กทรอนิกส์ที่ดักเก็บไว้ออกไปยังคนร้ายผ่านช่องทางเดียวกับ ...
[RETRIEVE] Query: ส่งไฟล์บันทึกจดหมายอิเล็กทรอนิกส์ที่ดักเก็บไว้ออกไปยังคนร้ายผ่านช่องทางเดียวกับ ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ROKRAT (0.969), Exfiltration Over C2 Channel (0.911), Kevin (0.874), Automated Exfiltration (0.806), Okrum (0.785), APT39 (0.762), Scheduled Transfer (0.614), Exfiltration Over Unencrypted Non-C2 Protocol (0.137), Exfiltration Over Alternative Protocol (0.083), Data Staged (0.017)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → ROKRAT (31 neighbors, 31 edges)
           → Automated Exfiltration (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [95/100] retrieved=678 relevant=4 latency=22045ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 25 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งแจ้งความเพิ่มเติมถึงพฤติกร...
[RETRIEVE] Query: เมื่อวันที่ 25 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งแจ้งความเพิ่มเติมถึงพฤติกร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT18 (0.135), Obfuscated Files or Information (0.009), Adversary-in-the-Middle (0.004), Masquerade File Type (0.003), ARP Cache Poisoning (0.002), Evil Twin (0.001), Magic Hound (0.001), Threat Group-3390 (0.000), Right-to-Left Override (0.000), BackConfig (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT18 (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] Query 2/7: ไฟล์อันตรายซ่อนข้อความด้วยการแปลงเป็นค่าฐานสิบหกและสลับตำแหน่งข้อมูล (Obfuscated...
[RETRIEVE] Query: ไฟล์อันตรายซ่อนข้อความด้วยการแปลงเป็นค่าฐานสิบหกและสลับตำแหน่งข้อมูล (Obfuscated...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Obfuscated Files or Information (0.734), Pisloader (0.719), Gustuff (0.617), Deobfuscate/Decode Files or Information (0.613), APT3 (0.546), PUBLOAD (0.319), Encrypted/Encoded File (0.235), Malicious File (0.046), Masquerade File Type (0.044), Compression (0.015)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → Pisloader (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 3/7: โปรแกรมเก็บรวบรวมหมายเลขไอพีของเครื่องผู้เสียหาย...
[RETRIEVE] Query: โปรแกรมเก็บรวบรวมหมายเลขไอพีของเครื่องผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Reaver (0.806), BADFLICK (0.750), ifconfig (0.193), ipconfig (0.035), Cherry Picker (0.011), CrossRAT (0.006), Cobian RAT (0.003), Cardinal RAT (0.001), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Reaver (14 neighbors, 14 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → BADFLICK (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 4/7: โปรแกรมเก็บรวบรวมชื่อเครื่องของผู้เสียหาย...
[RETRIEVE] Query: โปรแกรมเก็บรวบรวมชื่อเครื่องของผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: EVILNUM (0.571), RedLine Stealer (0.227), Cherry Picker (0.008), LP-Notes (0.003), PUNCHTRACK (0.003), LaZagne (0.002), CrossRAT (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → EVILNUM (15 neighbors, 15 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → RedLine Stealer (35 neighbors, 35 edges)
           → Software Discovery (56 neighbors, 56 edges)
[RETRIEVE-QUOTA] Query 5/7: โปรแกรมเก็บรวบรวมชื่อบัญชีผู้ใช้ที่ล็อกอินอยู่...
[RETRIEVE] Query: โปรแกรมเก็บรวบรวมชื่อบัญชีผู้ใช้ที่ล็อกอินอยู่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SILENTTRINITY (0.960), Epic (0.887), LaZagne (0.070), gsecdump (0.044), Cachedump (0.029), CrossRAT (0.004), Cobian RAT (0.002), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → SILENTTRINITY (53 neighbors, 53 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Epic (23 neighbors, 23 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] Query 6/7: แปลงข้อมูลที่เก็บรวบรวมได้เป็นค่าฐานสิบหกก่อนส่งออก...
[RETRIEVE] Query: แปลงข้อมูลที่เก็บรวบรวมได้เป็นค่าฐานสิบหกก่อนส่งออก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN6 (0.014), Data Staged (0.004), SampleCheck5000 (0.002), Remote Data Staging (0.002), DNS Calculation (0.001), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → FIN6 (52 neighbors, 52 edges)
           → Archive via Custom Method (42 neighbors, 42 edges)
           → Data Staged (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งข้อมูลที่ขโมยออกไปยังหมายเลขไอพีที่ผู้โจมตีควบคุมผ่านคำขอ HTTP POST (Exfiltra...
[RETRIEVE] Query: ส่งข้อมูลที่ขโมยออกไปยังหมายเลขไอพีที่ผู้โจมตีควบคุมผ่านคำขอ HTTP POST (Exfiltra...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over C2 Channel (0.947), Rising Sun (0.937), BlackByte (0.912), CharmPower (0.896), Exfiltration Over Unencrypted Non-C2 Protocol (0.600), Automated Exfiltration (0.536), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.531), Scheduled Transfer (0.470), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.429), Exfiltration Over Alternative Protocol (0.407)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Rising Sun (21 neighbors, 21 edges)
           → BlackByte (56 neighbors, 56 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [96/100] retrieved=699 relevant=3 latency=32460ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 25 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดการเ...
[RETRIEVE] Query: เมื่อวันที่ 25 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดการเ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA505 (0.040), Daggerfly (0.018), zwShell (0.011), ZxShell (0.011), Netwalker (0.002), RDP Hijacking (0.001), Remote Desktop Protocol (0.001), POWERSOURCE (0.000), Forced Authentication (0.000), PowerShell (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → TA505 (50 neighbors, 50 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Daggerfly (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 2/9: ใช้ PowerShell ติดต่อหมายเลขไอพีภายนอกผ่านโพรโทคอลเว็บเพื่อดึงสคริปต์ชุดถัดไปมาท...
[RETRIEVE] Query: ใช้ PowerShell ติดต่อหมายเลขไอพีภายนอกผ่านโพรโทคอลเว็บเพื่อดึงสคริปต์ชุดถัดไปมาท...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerShell (0.046), IPsec Helper (0.022), Storm-1811 (0.017), POWRUNER (0.006), PowerSploit (0.005), POWERSTATS (0.004), P.A.S. Webshell (0.004), Disable or Remove Feature or Program (0.002), PowerShell Profile (0.002), POWERSTATS (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PowerShell (241 neighbors, 241 edges)
           → IPsec Helper (16 neighbors, 16 edges)
           → Storm-1811 (38 neighbors, 38 edges)
[RETRIEVE-QUOTA] Query 3/9: เคลื่อนย้ายภายในเครือข่ายผ่าน Remote Desktop Protocol ไปยังเครื่องแม่ข่ายบริหารจ...
[RETRIEVE] Query: เคลื่อนย้ายภายในเครือข่ายผ่าน Remote Desktop Protocol ไปยังเครื่องแม่ข่ายบริหารจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VOID MANTICORE (0.299), RDP Hijacking (0.107), BlackByte (0.041), Remote Access Tools (0.017), Axiom (0.007), Koadic (0.006), VNC (0.006), Remote Desktop Protocol (0.005), Terminal Services DLL (0.004), Remote Services (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 4/9: เคลื่อนย้ายภายในเครือข่ายผ่าน Remote Desktop Protocol ไปยังเครื่องออกใบรับรอง...
[RETRIEVE] Query: เคลื่อนย้ายภายในเครือข่ายผ่าน Remote Desktop Protocol ไปยังเครื่องออกใบรับรอง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RDP Hijacking (0.123), Remote Desktop Protocol (0.016), VNC (0.015), ServHelper (0.012), Koadic (0.008), Remote Desktop Software (0.005), Remote Access Tools (0.003), Axiom (0.003), Terminal Services DLL (0.002), Remote Services (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → VNC (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 5/9: เคลื่อนย้ายภายในเครือข่ายผ่าน Remote Desktop Protocol ไปยังฐานข้อมูลข้อมูลการสืบ...
[RETRIEVE] Query: เคลื่อนย้ายภายในเครือข่ายผ่าน Remote Desktop Protocol ไปยังฐานข้อมูลข้อมูลการสืบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: menuPass (0.243), FIN7 (0.084), RDP Hijacking (0.046), Axiom (0.007), Koadic (0.003), Remote Desktop Protocol (0.002), Remote System Discovery (0.002), VNC (0.001), Terminal Services DLL (0.001), Remote Services (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → menuPass (71 neighbors, 71 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → FIN7 (86 neighbors, 86 edges)
[RETRIEVE-QUOTA] Query 6/9: เคลื่อนย้ายภายในเครือข่ายผ่าน Remote Desktop Protocol ไปยังเครื่องส่งต่อจดหมายอิ...
[RETRIEVE] Query: เคลื่อนย้ายภายในเครือข่ายผ่าน Remote Desktop Protocol ไปยังเครื่องส่งต่อจดหมายอิ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RDP Hijacking (0.057), Mail Protocols (0.046), FIN7 (0.037), Koadic (0.007), APT28 Nearest Neighbor Campaign (0.007), Axiom (0.006), Remote Desktop Protocol (0.004), Terminal Services DLL (0.004), Remote Access Tools (0.003), Remote Services (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → Mail Protocols (31 neighbors, 31 edges)
           → FIN7 (86 neighbors, 86 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
[RETRIEVE-QUOTA] Query 7/9: สร้างไฟล์บีบอัดที่บรรจุข้อมูลการสืบสวนคดีอ่อนไหวภายใต้บัญชีผู้ดูแลระบบที่ถูกยึดค...
[RETRIEVE] Query: สร้างไฟล์บีบอัดที่บรรจุข้อมูลการสืบสวนคดีอ่อนไหวภายใต้บัญชีผู้ดูแลระบบที่ถูกยึดค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: UNC3886 (0.002), Security Account Manager (0.001), Data from Removable Media (0.000), BloodHound (0.000), Prikormka (0.000), LSASS Memory (0.000), DCSync (0.000), Credentials In Files (0.000), QakBot (0.000), AADInternals (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → UNC3886 (58 neighbors, 58 edges)
           → Archive via Utility (88 neighbors, 88 edges)
           → Security Account Manager (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 8/9: ดาวน์โหลดไฟล์อันตรายจากหมายเลขไอพีภายนอกเข้ามาสั่งให้ทำงานบนเครื่อง...
[RETRIEVE] Query: ดาวน์โหลดไฟล์อันตรายจากหมายเลขไอพีภายนอกเข้ามาสั่งให้ทำงานบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OopsIE (0.028), LNK Icon Smuggling (0.015), Conficker (0.009), IMAPLoader (0.007), Cobian RAT (0.002), ccf32 (0.001), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → OopsIE (20 neighbors, 20 edges)
           → LNK Icon Smuggling (8 neighbors, 8 edges)
           → Conficker (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 9/9: แปลงการติดต่อไฟล์ทั้งขาเข้าและขาออกด้วยกุญแจลับเพื่อปกปิดเนื้อหา (Encrypted Chan...
[RETRIEVE] Query: แปลงการติดต่อไฟล์ทั้งขาเข้าและขาออกด้วยกุญแจลับเพื่อปกปิดเนื้อหา (Encrypted Chan...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Encrypted Channel (0.697), Encrypted/Encoded File (0.046), NETWIRE (0.032), Chaes (0.018), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.014), Data Encrypted for Impact (0.009), Protocol Tunneling (0.004), Small Sieve (0.003), Out-of-Band Communications Channel (0.002), WhisperGate (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Encrypted Channel (23 neighbors, 23 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → NETWIRE (49 neighbors, 49 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [97/100] retrieved=369 relevant=6 latency=52326ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 22 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าโปรแกรมเรียก...
[RETRIEVE] Query: เมื่อวันที่ 22 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าโปรแกรมเรียก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NotPetya (0.008), Wizard Spider (0.000), FIN8 (0.000), Exploitation of Remote Services (0.000), Pikabot (0.000), Hijack Execution Flow (0.000), Scheduled Task/Job (0.000), Filter Network Traffic (0.000), Process Discovery (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → NotPetya (15 neighbors, 15 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Wizard Spider (86 neighbors, 86 edges)
           → Windows Remote Management (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 2/7: ใช้ Windows Management Instrumentation (WMI) กระจายโปรแกรมเรียกค่าไถ่ไปยังเครื่อ...
[RETRIEVE] Query: ใช้ Windows Management Instrumentation (WMI) กระจายโปรแกรมเรียกค่าไถ่ไปยังเครื่อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lucifer (0.812), EKANS (0.418), Windows Management Instrumentation (0.415), Koadic (0.201), Windows Management Instrumentation Event Subscription (0.178), Windows Remote Management (0.002), At (0.001), Scheduled Task (0.001), Extra Window Memory Injection (0.001), Virtual Machine Discovery (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Lucifer (24 neighbors, 24 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → EKANS (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 3/7: สั่งคำสั่งผ่านหน้าต่างคำสั่งเพื่อคัดลอกไฟล์โปรแกรมเรียกค่าไถ่และไฟล์สคริปต์ไปยัง...
[RETRIEVE] Query: สั่งคำสั่งผ่านหน้าต่างคำสั่งเพื่อคัดลอกไฟล์โปรแกรมเรียกค่าไถ่และไฟล์สคริปต์ไปยัง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lucifer (0.016), Forfiles (0.011), RansomHub (0.007), Indirect Command Execution (0.006), APT3 (0.002), BackConfig (0.002), Windows Command Shell (0.002), KernelCallbackTable (0.001), xCmd (0.001), Ptrace System Calls (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Lucifer (24 neighbors, 24 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Forfiles (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 4/7: ส่งไฟล์โปรแกรมเรียกค่าไถ่และไฟล์สคริปต์ผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบบ (SMB...
[RETRIEVE] Query: ส่งไฟล์โปรแกรมเรียกค่าไถ่และไฟล์สคริปต์ผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบบ (SMB...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BlackByte Ransomware (0.663), SMB/Windows Admin Shares (0.437), Anchor (0.218), PsExec (0.210), Aquatic Panda (0.073), Network Share Discovery (0.021), Network Share Connection Removal (0.007), Forced Authentication (0.006), Net (0.005), Lateral Tool Transfer (0.005)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BlackByte Ransomware (22 neighbors, 22 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → Anchor (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 5/7: ใช้ WMI สั่งให้สคริปต์หยุดการทำงานของโปรแกรมอื่นบนเครื่องเป้าหมายทั้งหมด...
[RETRIEVE] Query: ใช้ WMI สั่งให้สคริปต์หยุดการทำงานของโปรแกรมอื่นบนเครื่องเป้าหมายทั้งหมด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Behavior Prevention on Endpoint (0.079), Koadic (0.065), Windows Management Instrumentation Event Subscription (0.057), Windows Management Instrumentation (0.057), HermeticWizard (0.048), Empire (0.014), System Shutdown/Reboot (0.003), WMI Creation (0.001), At (0.000), SNMP (MIB Dump) (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Behavior Prevention on Endpoint (51 neighbors, 51 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Windows Management Instrumentation Event Subscription (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 6/7: ใช้ WMI สั่งให้โปรแกรมเรียกค่าไถ่ทำงานบนเครื่องเป้าหมายทั้งหมด...
[RETRIEVE] Query: ใช้ WMI สั่งให้โปรแกรมเรียกค่าไถ่ทำงานบนเครื่องเป้าหมายทั้งหมด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Empire (0.111), Windows Management Instrumentation (0.066), Koadic (0.027), MoleNet (0.019), Remexi (0.010), Windows Management Instrumentation Event Subscription (0.010), KernelCallbackTable (0.001), At (0.000), WMI Creation (0.000), Scheduled Task (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Empire (91 neighbors, 91 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Koadic (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 7/7: ใช้เครื่องมือสั่งงานเครื่องระยะไกลสร้างบริการของระบบบนเครื่องเป้าหมายเพื่อรันสคร...
[RETRIEVE] Query: ใช้เครื่องมือสั่งงานเครื่องระยะไกลสร้างบริการของระบบบนเครื่องเป้าหมายเพื่อรันสคร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.903), xCmd (0.594), RemoteCMD (0.287), Execution (0.268), HermeticWizard (0.255), Service Execution (0.137), LAPSUS$ (0.021), Event Triggered Execution (0.003), User Execution (0.002), Thread Execution Hijacking (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → xCmd (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [98/100] retrieved=529 relevant=3 latency=38340ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 22 กันยายน 2563 ผู้เสียหายหลายรายแจ้งความว่าบัญชีผู้ใช้งานออนไลน์ของ...
[RETRIEVE] Query: เมื่อวันที่ 22 กันยายน 2563 ผู้เสียหายหลายรายแจ้งความว่าบัญชีผู้ใช้งานออนไลน์ของ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Crimson (0.259), njRAT (0.200), LAPSUS$ (0.072), Malicious File (0.069), User Execution (0.046), Execution Prevention (0.013), Lokibot (0.009), Malicious Link (0.003), Exploitation for Client Execution (0.000), Compromise Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Crimson (32 neighbors, 32 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → njRAT (40 neighbors, 40 edges)
[RETRIEVE-QUOTA] Query 2/8: กระจายโปรแกรมขโมยรหัสผ่านผ่านอีเมล เว็บไซต์อันตราย ข้อความสั้น และข้อความส่วนตัว...
[RETRIEVE] Query: กระจายโปรแกรมขโมยรหัสผ่านผ่านอีเมล เว็บไซต์อันตราย ข้อความสั้น และข้อความส่วนตัว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QakBot (0.180), QakBot (0.171), Lokibot (0.090), XLoader (0.060), Email Accounts (0.002), Cobian RAT (0.001), CrossRAT (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → QakBot (74 neighbors, 74 edges)
           → Spearphishing Link (93 neighbors, 93 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
[RETRIEVE-QUOTA] Query 3/8: ผู้เสียหายเปิดไฟล์มัลแวร์ที่ได้รับด้วยตนเอง (User Execution: Malicious File)...
[RETRIEVE] Query: ผู้เสียหายเปิดไฟล์มัลแวร์ที่ได้รับด้วยตนเอง (User Execution: Malicious File)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kerrdown (0.896), Clambling (0.871), Malicious File (0.842), User Execution (0.678), Executable Installer File Permissions Weakness (0.357), KOPILUWAK (0.342), Execution (0.055), Malicious Link (0.050), Execution Prevention (0.024), Exploitation for Client Execution (0.015)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Malicious File (202 neighbors, 202 edges)
           → Kerrdown (12 neighbors, 12 edges)
           → Clambling (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 4/8: สร้างช่องทางลับโดยเรียกใช้ฟีเจอร์ช่วยการเข้าถึงของระบบปฏิบัติการ (Event Triggere...
[RETRIEVE] Query: สร้างช่องทางลับโดยเรียกใช้ฟีเจอร์ช่วยการเข้าถึงของระบบปฏิบัติการ (Event Triggere...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Accessibility Features (0.448), Event Triggered Execution (0.252), Execution Prevention (0.078), Update Software (0.013), DarkGate (0.005), User Execution (0.003), Credential API Hooking (0.002), Elevated Execution with Prompt (0.002), Native API (0.001), Chaes (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Accessibility Features (15 neighbors, 15 edges)
           → Event Triggered Execution (28 neighbors, 28 edges)
           → Execution Prevention (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] Query 5/8: ดักบันทึกแป้นพิมพ์เพื่อขโมยข้อมูลรับรองตัวตน (Input Capture: Keylogging)...
[RETRIEVE] Query: ดักบันทึกแป้นพิมพ์เพื่อขโมยข้อมูลรับรองตัวตน (Input Capture: Keylogging)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Keylogging (0.570), S.O.V.A. (0.550), Lokibot (0.522), Input Capture (0.315), Credential Access (0.126), Fysbis (0.035), GUI Input Capture (0.026), Empire (0.022), Web Portal Capture (0.010), Private Keys (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Keylogging (160 neighbors, 160 edges)
           → S.O.V.A. (19 neighbors, 19 edges)
           → Keylogging (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 6/8: เฝ้าดูการใช้งานบนโปรแกรมท่องเว็บและหน้าจอทั่วไปเพื่อเก็บข้อมูล (Screen Capture)...
[RETRIEVE] Query: เฝ้าดูการใช้งานบนโปรแกรมท่องเว็บและหน้าจอทั่วไปเพื่อเก็บข้อมูล (Screen Capture)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Screen Capture (0.214), AsyncRAT (0.044), TangleBot (0.039), PowerSploit (0.037), Input Capture (0.021), XAgentOSX (0.017), Video Capture (0.010), Web Portal Capture (0.009), Social Media (0.003), Audio Capture (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Screen Capture (173 neighbors, 173 edges)
           → AsyncRAT (23 neighbors, 23 edges)
           → Video Capture (37 neighbors, 37 edges)
[RETRIEVE-QUOTA] Query 7/8: อ่านชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บบันทึกไว้ในเครื่อง (Credentials from ...
[RETRIEVE] Query: อ่านชื่อผู้ใช้และรหัสผ่านที่โปรแกรมท่องเว็บบันทึกไว้ในเครื่อง (Credentials from ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.769), Credentials from Password Stores (0.341), XLoader (0.217), KGH_SPY (0.126), Credentials in Registry (0.108), Password Managers (0.043), Credentials In Files (0.027), PowerSploit (0.025), Windows Credential Manager (0.017), Unsecured Credentials (0.012)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → Credentials from Password Stores (50 neighbors, 50 edges)
           → XLoader (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 8/8: ติดตั้งโปรแกรมเพิ่มเติมภายหลังผ่านช่องทางลับที่สร้างไว้ (Persistence)...
[RETRIEVE] Query: ติดตั้งโปรแกรมเพิ่มเติมภายหลังผ่านช่องทางลับที่สร้างไว้ (Persistence)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerSploit (0.049), Spica (0.021), Create or Modify System Process (0.014), PowerSploit (0.013), Active Setup (0.013), RC Scripts (0.011), Disable or Remove Feature or Program (0.003), Re-opened Applications (0.000), Confluence (0.000), Silence (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → PowerSploit (39 neighbors, 39 edges)
           → Security Support Provider (9 neighbors, 9 edges)
           → Spica (10 neighbors, 10 edges)
           → PowerShell (241 neighbors, 241 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [99/100] retrieved=350 relevant=3 latency=52586ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 7 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าก่อนเกิดเหตุม...
[RETRIEVE] Query: เมื่อวันที่ 7 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าก่อนเกิดเหตุม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.014), POWRUNER (0.001), Domain Properties (0.000), FIN8 (0.000), Search Victim-Owned Websites (0.000), Domain Registration (0.000), Exfiltration to Text Storage Sites (0.000), Scan Databases (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → POWRUNER (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 2/8: สำรวจข้อมูลทะเบียนโดเมนขององค์กรอย่างเป็นระบบ...
[RETRIEVE] Query: สำรวจข้อมูลทะเบียนโดเมนขององค์กรอย่างเป็นระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AdFind (0.143), Domain Registration (0.066), Active DNS (0.052), Passive DNS (0.009), Empire (0.002), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → AdFind (19 neighbors, 19 edges)
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → Domain Registration (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 3/8: ไล่ค้นหารายการบัญชีบุคคลทั้งหมดในโดเมนและบันทึกผลลงไฟล์ข้อความ...
[RETRIEVE] Query: ไล่ค้นหารายการบัญชีบุคคลทั้งหมดในโดเมนและบันทึกผลลงไฟล์ข้อความ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.251), SoreFang (0.145), PoshC2 (0.041), Domain Account (0.030), Nltest (0.023), BoomBox (0.016), Account Discovery (0.004), Local Account (0.002), Domain Registration (0.001), Active DNS (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → SoreFang (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 4/8: ไล่ค้นหารายการเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนอยู่ในโดเมนและบันทึกผลลงไฟล์...
[RETRIEVE] Query: ไล่ค้นหารายการเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนอยู่ในโดเมนและบันทึกผลลงไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.088), Nltest (0.054), SHOTPUT (0.041), Domain Account (0.036), Active DNS (0.005), Cobian RAT (0.002), CrossRAT (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Nltest (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 5/8: แจกแจงหน่วยจัดการภายในโดเมนที่ผู้ใช้สังกัดอยู่...
[RETRIEVE] Query: แจกแจงหน่วยจัดการภายในโดเมนที่ผู้ใช้สังกัดอยู่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OSInfo (0.104), Nltest (0.034), Domain Groups (0.012), Sykipot (0.011), APT41 (0.007), BADHATCH (0.006), Domain Account (0.003), Domain Account (0.002), Additional Local or Domain Groups (0.002), Local Account (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OSInfo (11 neighbors, 11 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → Nltest (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 6/8: ค้นหาความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนทั้งหมดในโครงสร้างองค์กรและเก็บผลลัพ...
[RETRIEVE] Query: ค้นหาความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนทั้งหมดในโครงสร้างองค์กรและเก็บผลลัพ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BADHATCH (0.289), MirrorFace (0.255), Magic Hound (0.202), Chimera (0.164), Domain Trust Discovery (0.071), Business Relationships (0.025), Active DNS (0.004), Passive DNS (0.001), Domain Registration (0.001), Certificate Registration (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BADHATCH (36 neighbors, 36 edges)
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → MirrorFace (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] Query 7/8: เรียกดูช่วงหมายเลขเครือข่ายย่อยที่องค์กรใช้งานอยู่...
[RETRIEVE] Query: เรียกดูช่วงหมายเลขเครือข่ายย่อยที่องค์กรใช้งานอยู่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Scanning IP Blocks (0.041), netstat (0.008), netstat (0.005), Net (0.004), Net (0.001), System Network Connections Discovery (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Scanning IP Blocks (6 neighbors, 6 edges)
           → netstat (16 neighbors, 16 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
[RETRIEVE-QUOTA] Query 8/8: แจกแจงรายชื่อกลุ่มสิทธิ์ทั้งหมดในโดเมนและบันทึกผลลงไฟล์ข้อความ...
[RETRIEVE] Query: แจกแจงรายชื่อกลุ่มสิทธิ์ทั้งหมดในโดเมนและบันทึกผลลงไฟล์ข้อความ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SoreFang (0.120), Nltest (0.088), FIN7 (0.029), C0015 (0.020), Dragonfly (0.018), Group Metadata (0.013), Domain Account (0.007), Group Enumeration (0.004), Group Policy Preferences (0.001), Email Account (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → SoreFang (15 neighbors, 15 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → Nltest (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [100/100] retrieved=129 relevant=5 latency=35859ms

============================================================
  Retriever: Hybrid+Quota (decompose)  (100 samples)
============================================================
  Metric                    @1      @3      @5     @10     @15     @20     @50
  ────────────────────────────────────────────────────────────────────────────
  Hit                    0.780   0.960   0.990   1.000   1.000   1.000   1.000
  Recall (capped)        0.780   0.672   0.718   0.847   0.856   0.856   0.882
  Precision              0.780   0.663   0.502   0.302   0.204   0.153   0.063
  NDCG                   0.780   0.698   0.719   0.782   0.785   0.785   0.793

  Attack-chain samples: 100 (343 scoreable steps, 4 unscoreable)
  StepCoverage           0.250   0.595   0.721   0.857   0.867   0.867   0.888
  StepCoverage strict    0.195   0.551   0.683   0.835   0.845   0.845   0.873
    by cue: described    0.202   0.538   0.667   0.832   0.843   0.843   0.869
    by cue: named        0.498   0.865   0.991   1.000   1.000   1.000   1.000

  MRR                    0.871
  MAP                    0.677
  Avg Latency (ms)     33038.1


════════════════════════════════════════════════════════════
  EVALUATION COMPLETE
════════════════════════════════════════════════════════════
