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
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่งในจังหวัดนนทบุรีแจ้งความว่าระบบร...
[RETRIEVE] Query: เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่งในจังหวัดนนทบุรีแจ้งความว่าระบบร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.097), ShimRat (0.078), Exploit Public-Facing Application (0.007), Application Shimming (0.003), Clambling (0.001), Application Layer Protocol (0.000), Email Forwarding Rule (0.000), Exploitation for Client Execution (0.000), File Transfer Protocols (0.000), Re-opened Applications (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → ShimRat (22 neighbors, 22 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Clambling (35 neighbors, 35 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 2/7: SQL Injection ผ่านช่องกรอกข้อมูลบนหน้าเว็บสาธารณะ...
[RETRIEVE] Query: SQL Injection ผ่านช่องกรอกข้อมูลบนหน้าเว็บสาธารณะ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Havij (0.333), Axiom (0.301), Havij (0.027), sqlmap (0.007), Content Injection (0.005), HTRAN (0.001), Process Injection (0.001), Dynamic-link Library Injection (0.001), Cardinal RAT (0.000), Template Injection (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Havij (2 neighbors, 2 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Axiom (24 neighbors, 24 edges)
           → Content Injection (8 neighbors, 8 edges)
           → sqlmap (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 3/7: วางไฟล์สคริปต์สั่งการระยะไกล (webshell) บนเซิร์ฟเวอร์...
[RETRIEVE] Query: วางไฟล์สคริปต์สั่งการระยะไกล (webshell) บนเซิร์ฟเวอร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Web Shell (0.854), P.A.S. Webshell (0.663), P.A.S. Webshell (0.429), Netsh Helper DLL (0.066), PHPsert (0.036), ADVSTORESHELL (0.010), ZxShell (0.010), Terminal Services DLL (0.010), Windows Command Shell (0.004), TONESHELL (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Web Shell (71 neighbors, 71 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Netsh Helper DLL (6 neighbors, 6 edges)
           → PHPsert (7 neighbors, 7 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 4/7: Application Shimming เพื่อให้โปรแกรมทำงานทุกครั้งที่เริ่มระบบ...
[RETRIEVE] Query: Application Shimming เพื่อให้โปรแกรมทำงานทุกครั้งที่เริ่มระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Application Shimming (0.499), SDBbot (0.335), ShimRat (0.158), Update Software (0.068), FIN7 (0.055), Boot or Logon Autostart Execution (0.028), Create or Modify System Process (0.009), Re-opened Applications (0.008), schtasks (0.005), Launch Daemon (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Application Shimming (11 neighbors, 11 edges)
           → SDBbot (25 neighbors, 25 edges)
           → ShimRat (22 neighbors, 22 edges)
           → Update Software (42 neighbors, 42 edges)
           → FIN7 (86 neighbors, 86 edges)
[RETRIEVE-QUOTA] Query 5/7: ค้นหารายชื่อเครื่องลูกข่ายในวงเครือข่าย (network enumeration)...
[RETRIEVE] Query: ค้นหารายชื่อเครื่องลูกข่ายในวงเครือข่าย (network enumeration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pod Enumeration (0.204), Instance Enumeration (0.110), BRONZE BUTLER (0.038), Clambling (0.030), spwebmember (0.011), Log Enumeration (0.009), Virtual Machine Discovery (0.005), ROADTools (0.003), Snapshot Enumeration (0.003), System Network Connections Discovery (0.002)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Pod Enumeration (0 neighbors, 0 edges)
           → Instance Enumeration (0 neighbors, 0 edges)
           → BRONZE BUTLER (54 neighbors, 54 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
           → Clambling (35 neighbors, 35 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
[RETRIEVE-QUOTA] Query 6/7: รวบรวมรายละเอียดเครื่องคอมพิวเตอร์พนักงาน...
[RETRIEVE] Query: รวบรวมรายละเอียดเครื่องคอมพิวเตอร์พนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Systeminfo (0.039), Malteiro (0.005), Employee Names (0.003), ZxShell (0.002), OSInfo (0.000), Cobian RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Systeminfo (14 neighbors, 14 edges)
           → Malteiro (13 neighbors, 13 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Employee Names (6 neighbors, 6 edges)
           → ZxShell (37 neighbors, 37 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
[RETRIEVE-QUOTA] Query 7/7: บันทึกภาพหน้าจอและส่งออกไปยังเครื่องปลายทางของคนร้าย (screen capture exfiltratio...
[RETRIEVE] Query: บันทึกภาพหน้าจอและส่งออกไปยังเครื่องปลายทางของคนร้าย (screen capture exfiltratio...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Rover (0.422), BOULDSPY (0.335), Screen Capture (0.237), Exfiltration Over Physical Medium (0.202), Exfiltration Over Other Network Medium (0.115), Exfiltration (0.076), Video Capture (0.058), SharkBot (0.020), Exbyte (0.018), Empire (0.007)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Rover (10 neighbors, 10 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → BOULDSPY (25 neighbors, 25 edges)
           → Screen Capture (31 neighbors, 31 edges)
           → Exfiltration Over Physical Medium (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [1/100] retrieved=392 relevant=4 latency=15882ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 3 ตุลาคม 2565 โรงพยาบาลเอกชนแห่งหนึ่งในจังหวัดเชียงใหม่แจ้งว่าระบบเว...
[RETRIEVE] Query: เมื่อวันที่ 3 ตุลาคม 2565 โรงพยาบาลเอกชนแห่งหนึ่งในจังหวัดเชียงใหม่แจ้งว่าระบบเว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.126), Windows Credential Editor (0.024), Ember Bear (0.010), Mustang Panda (0.008), OS Credential Dumping (0.007), Password Cracking (0.002), Credential Access Protection (0.001), IceApple (0.000), Credential Stuffing (0.000), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
           → Ember Bear (58 neighbors, 58 edges)
           → Mustang Panda (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] Query 2/9: Credential Dumping ดึงค่าแฮชรหัสผ่านจากหน่วยความจำเครื่องแม่ข่าย...
[RETRIEVE] Query: Credential Dumping ดึงค่าแฮชรหัสผ่านจากหน่วยความจำเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cachedump (0.772), OS Credential Dumping (0.733), MgBot (0.449), Cachedump (0.315), Credentials In Files (0.208), Credential Access Protection (0.149), Windows Credential Editor (0.117), Credential Access (0.108), Password Cracking (0.103), Axiom (0.096)
[RETRIEVE] Graph expansion: 5 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Cachedump (2 neighbors, 2 edges)
           → Cached Domain Credentials (16 neighbors, 16 edges)
           → MgBot (18 neighbors, 18 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 3/9: Pass the Hash เข้าสู่บัญชีผู้ดูแลระบบโดยไม่ต้องทราบรหัสผ่านจริง...
[RETRIEVE] Query: Pass the Hash เข้าสู่บัญชีผู้ดูแลระบบโดยไม่ต้องทราบรหัสผ่านจริง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pass-The-Hash Toolkit (0.973), Pass the Hash (0.860), Pass the Ticket (0.330), User Account Management (0.105), Pass-The-Hash Toolkit (0.027), Cached Domain Credentials (0.026), Password Cracking (0.009), HOPLIGHT (0.008), Hybrid Identity (0.000), Dynamic API Resolution (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pass the Hash (29 neighbors, 29 edges)
           → Pass-The-Hash Toolkit (2 neighbors, 2 edges)
           → Pass the Ticket (13 neighbors, 13 edges)
           → User Account Management (119 neighbors, 119 edges)
           → Cached Domain Credentials (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/9: เข้าถึงระบบบริหารจัดการเครื่องเสมือน (Virtual Machine Management System)...
[RETRIEVE] Query: เข้าถึงระบบบริหารจัดการเครื่องเสมือน (Virtual Machine Management System)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cloud Administration Command (0.097), SVCReady (0.055), Windows Management Instrumentation (0.046), Direct Cloud VM Connections (0.035), Virtual Machine Discovery (0.016), PureCrypter (0.012), User Account Management (0.012), System Checks (0.006), Windows Remote Management (0.002), User Account Management (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Cloud Administration Command (7 neighbors, 7 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → SVCReady (24 neighbors, 24 edges)
           → Direct Cloud VM Connections (5 neighbors, 5 edges)
           → Virtual Machine Discovery (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/9: ตั้งรหัสผ่านบัญชีผู้ดูแลเครื่องแม่ข่ายเสมือนขึ้นใหม่เพื่อปฏิเสธการเข้าถึง...
[RETRIEVE] Query: ตั้งรหัสผ่านบัญชีผู้ดูแลเครื่องแม่ข่ายเสมือนขึ้นใหม่เพื่อปฏิเสธการเข้าถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Active Directory Configuration (0.002), Active Directory Configuration (0.002), Active Directory Configuration (0.002), Password Policies (0.001), Account Access Removal (0.001), Modify Authentication Process (0.001), Password Policies (0.001), Reversible Encryption (0.000), Active Directory Configuration (0.000), Windows Host Firewall (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Active Directory Configuration (15 neighbors, 15 edges)
           → Steal or Forge Kerberos Tickets (15 neighbors, 15 edges)
           → Pass the Ticket (13 neighbors, 13 edges)
           → Password Policies (47 neighbors, 47 edges)
           → Account Access Removal (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 6/9: ติดตั้งโปรแกรมสร้างช่องทางเชื่อมต่อออกสู่ภายนอก (Backdoor/C2)...
[RETRIEVE] Query: ติดตั้งโปรแกรมสร้างช่องทางเชื่อมต่อออกสู่ภายนอก (Backdoor/C2)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RARSTONE (0.149), MuddyViper (0.114), BPFDoor (0.061), WEBC2 (0.041), Backdoor.Oldrea (0.033), LunarMail (0.004), Rifdoor (0.004), Komplex (0.003), Backdoor.Oldrea (0.000), BackdoorDiplomacy (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RARSTONE (5 neighbors, 5 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → MuddyViper (19 neighbors, 19 edges)
           → BPFDoor (13 neighbors, 13 edges)
           → Backdoor.Oldrea (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 7/9: ลำเลียงข้อมูลของโรงพยาบาลออกไปทางช่องทางเชื่อมต่อภายนอก (Data Exfiltration)...
[RETRIEVE] Query: ลำเลียงข้อมูลของโรงพยาบาลออกไปทางช่องทางเชื่อมต่อภายนอก (Data Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Manjusaka (0.275), Exfiltration Over Other Network Medium (0.264), Exfiltration (0.100), Exfiltration Over Physical Medium (0.059), Exfiltration Over Alternative Protocol (0.044), RDAT (0.041), Exfiltration Over Web Service (0.037), Exbyte (0.005), Empire (0.004), Exbyte (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
           → Manjusaka (10 neighbors, 10 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Exfiltration (19 neighbors, 19 edges)
           → Exfiltration Over Physical Medium (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 8/9: เชื่อมต่อเข้าเครื่องแม่ข่ายเสมือนทุกเครื่องผ่าน SSH...
[RETRIEVE] Query: เชื่อมต่อเข้าเครื่องแม่ข่ายเสมือนทุกเครื่องผ่าน SSH...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH Hijacking (0.081), SSH (0.041), FIN7 (0.005), reGeorg (0.005), Cobalt Strike (0.004), Leviathan (0.002), SSH Authorized Keys (0.002), Remote Services (0.001), Kessel (0.001), SMB/Windows Admin Shares (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SSH Hijacking (8 neighbors, 8 edges)
           → SSH (33 neighbors, 33 edges)
           → FIN7 (86 neighbors, 86 edges)
           → reGeorg (13 neighbors, 13 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] Query 9/9: เข้ารหัสลับข้อมูลทั้งหมดบนระบบจนหยุดให้บริการ (Ransomware/Encryption)...
[RETRIEVE] Query: เข้ารหัสลับข้อมูลทั้งหมดบนระบบจนหยุดให้บริการ (Ransomware/Encryption)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Encrypted for Impact (0.592), INC Ransomware (0.203), Maze (0.101), Play (0.059), ShrinkLocker (0.051), INC Ransom (0.038), Cheerscrypt (0.019), Playcrypt (0.019), Akira (0.019), Avaddon (0.016)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → INC Ransomware (16 neighbors, 16 edges)
           → Maze (25 neighbors, 25 edges)
           → Play (35 neighbors, 35 edges)
           → ShrinkLocker (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [2/100] retrieved=189 relevant=5 latency=19249ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 18 พฤศจิกายน 2565 สหกรณ์แห่งหนึ่งในจังหวัดขอนแก่นได้รับแจ้งเบาะแสจาก...
[RETRIEVE] Query: เมื่อวันที่ 18 พฤศจิกายน 2565 สหกรณ์แห่งหนึ่งในจังหวัดขอนแก่นได้รับแจ้งเบาะแสจาก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: KGH_SPY (0.037), Maze (0.010), TianySpy (0.008), H1N1 (0.001), Lokibot (0.001), Magic Hound (0.000), Threat Group-3390 (0.000), ShadowPad (0.000), Clear Windows Event Logs (0.000), Clear Linux or Mac System Logs (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → KGH_SPY (21 neighbors, 21 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Maze (25 neighbors, 25 edges)
           → TianySpy (9 neighbors, 9 edges)
           → Obfuscated Files or Information (51 neighbors, 51 edges)
[RETRIEVE-QUOTA] Query 2/7: Phishing อีเมลแนบไฟล์อันตรายส่งถึงพนักงาน...
[RETRIEVE] Query: Phishing อีเมลแนบไฟล์อันตรายส่งถึงพนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chaes (0.733), Spearphishing Attachment (0.672), FIN4 (0.542), Spearphishing Link (0.384), Spearphishing Attachment (0.339), Phishing (0.235), Spearphishing Link (0.014), Phishing for Information (0.011), BITTER (0.010), Kimsuky (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Chaes (28 neighbors, 28 edges)
           → FIN4 (12 neighbors, 12 edges)
           → Spearphishing Link (93 neighbors, 93 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/7: ล็อกอินระยะไกลผ่านช่องทางเชื่อมต่อระยะไกล (RDP/VPN) โดยใช้ชื่อผู้ใช้และรหัสผ่านเ...
[RETRIEVE] Query: ล็อกอินระยะไกลผ่านช่องทางเชื่อมต่อระยะไกล (RDP/VPN) โดยใช้ชื่อผู้ใช้และรหัสผ่านเ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Service Session Hijacking (0.059), Remote Desktop Protocol (0.044), RDP Hijacking (0.027), User Account Management (0.024), Play (0.019), Remote Services (0.019), Limit Access to Resource Over Network (0.008), LAPSUS$ (0.007), FRP (0.001), SPACEHOP Activity (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Remote Service Session Hijacking (9 neighbors, 9 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → User Account Management (119 neighbors, 119 edges)
           → Remote Services (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 4/7: ยิงคำสั่งโจมตีช่องโหว่ที่ยังไม่ได้ปรับปรุงบนเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์...
[RETRIEVE] Query: ยิงคำสั่งโจมตีช่องโหว่ที่ยังไม่ได้ปรับปรุงบนเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BONDUPDATER (0.013), BOULDSPY (0.005), Operation Triangulation (0.004), STEADYPULSE (0.004), SysUpdate (0.000), Thread Execution Hijacking (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BONDUPDATER (8 neighbors, 8 edges)
           → BOULDSPY (25 neighbors, 25 edges)
           → Out of Band Data (20 neighbors, 20 edges)
           → Operation Triangulation (22 neighbors, 22 edges)
           → Exploitation for Client Execution (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 5/7: ค้นหารายการโปรแกรมที่ทำงานอยู่เกี่ยวกับการสำรองข้อมูลและการป้องกันไวรัส...
[RETRIEVE] Query: ค้นหารายการโปรแกรมที่ทำงานอยู่เกี่ยวกับการสำรองข้อมูลและการป้องกันไวรัส...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Clop (0.160), EVILNUM (0.069), Backup Software Discovery (0.053), PowerSploit (0.025), Tasklist (0.013), Tasklist (0.006), LaZagne (0.005), VERMIN (0.004), Data Backup (0.004), Umbreon (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Clop (18 neighbors, 18 edges)
           → Security Software Discovery (144 neighbors, 144 edges)
           → EVILNUM (15 neighbors, 15 edges)
           → Backup Software Discovery (4 neighbors, 4 edges)
           → PowerSploit (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 6/7: สั่งหยุดการทำงานของโปรแกรมสำรองข้อมูลและการป้องกันไวรัส...
[RETRIEVE] Query: สั่งหยุดการทำงานของโปรแกรมสำรองข้อมูลและการป้องกันไวรัส...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Babuk (0.103), Babuk (0.051), Inhibit System Recovery (0.005), Execution Prevention (0.002), Disable or Remove Feature or Program (0.000), Cardinal RAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Babuk (14 neighbors, 14 edges)
           → Service Stop (61 neighbors, 61 edges)
           → Disable or Modify Tools (142 neighbors, 142 edges)
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → Execution Prevention (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] Query 7/7: เข้ารหัสลับข้อมูลสมาชิกในเครื่องแม่ข่ายทั้งหมด (Ransomware)...
[RETRIEVE] Query: เข้ารหัสลับข้อมูลสมาชิกในเครื่องแม่ข่ายทั้งหมด (Ransomware)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BlackByte Ransomware (0.153), BlackByte (0.040), RansomHub (0.030), BlackByte Ransomware (0.027), Avaddon (0.022), INC Ransom (0.019), Akira (0.012), BlackByte Ransomware (0.007), Netwalker (0.006), IcedID (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BlackByte Ransomware (22 neighbors, 22 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → BlackByte (56 neighbors, 56 edges)
           → RansomHub (21 neighbors, 21 edges)
           → Avaddon (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [3/100] retrieved=463 relevant=3 latency=13174ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 9 ตุลาคม 2563 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Query: เมื่อวันที่ 9 ตุลาคม 2563 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Storm-1811 (0.033), LockBit 2.0 (0.030), MuddyWater (0.016), Ryuk (0.002), Registry Run Keys / Startup Folder (0.000), Query Registry (0.000), Modify Registry (0.000), Office Test (0.000), Windows Registry Key Modification (0.000), Windows Registry Key Access (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Storm-1811 (38 neighbors, 38 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
           → MuddyWater (89 neighbors, 89 edges)
           → Ryuk (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 2/6: Phishing จดหมายอิเล็กทรอนิกส์แอบอ้างเป็นหนังสือเชิญประชุมจากหน่วยงานคู่ความร่วมม...
[RETRIEVE] Query: Phishing จดหมายอิเล็กทรอนิกส์แอบอ้างเป็นหนังสือเชิญประชุมจากหน่วยงานคู่ความร่วมม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT32 (0.130), Phishing for Information (0.013), DocSwap (0.013), Phishing (0.008), Spearphishing Attachment (0.005), Spearphishing Service (0.004), Spearphishing Attachment (0.004), Spearphishing Link (0.003), Kimsuky (0.000), BITTER (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT32 (93 neighbors, 93 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Phishing for Information (12 neighbors, 12 edges)
           → DocSwap (27 neighbors, 27 edges)
           → Phishing (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 3/6: ไฟล์เอกสารแนบในอีเมล Phishing ที่มีสคริปต์ทำงาน...
[RETRIEVE] Query: ไฟล์เอกสารแนบในอีเมล Phishing ที่มีสคริปต์ทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chaes (0.774), FIN4 (0.544), Spearphishing Link (0.098), Spearphishing Attachment (0.084), Spearphishing Attachment (0.021), Phishing (0.011), Phishing for Information (0.004), BITTER (0.002), Spearphishing Link (0.001), Kimsuky (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Chaes (28 neighbors, 28 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → FIN4 (12 neighbors, 12 edges)
           → Spearphishing Link (93 neighbors, 93 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/6: สคริปต์สร้าง Registry Run Key เพื่อคงการทำงานเมื่อเปิดเครื่อง...
[RETRIEVE] Query: สคริปต์สร้าง Registry Run Key เพื่อคงการทำงานเมื่อเปิดเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NavRAT (0.906), LockBit 2.0 (0.851), Ryuk (0.699), Ursnif (0.600), Registry Run Keys / Startup Folder (0.597), Active Setup (0.034), Boot or Logon Autostart Execution (0.027), Office Test (0.014), Windows Registry Key Modification (0.002), Windows Registry Key Access (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → NavRAT (10 neighbors, 10 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
           → Ryuk (24 neighbors, 24 edges)
           → Ursnif (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 5/6: เก็บรวบรวมรายละเอียดเครื่อง ชื่อเครื่อง รุ่นระบบปฏิบัติการ และรายการซอฟต์แวร์ที่...
[RETRIEVE] Query: เก็บรวบรวมรายละเอียดเครื่อง ชื่อเครื่อง รุ่นระบบปฏิบัติการ และรายการซอฟต์แวร์ที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Azorult (0.762), Malteiro (0.632), Systeminfo (0.468), ifconfig (0.019), ipconfig (0.006), Visual Basic (0.001), Cobian RAT (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Azorult (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Malteiro (13 neighbors, 13 edges)
           → Systeminfo (14 neighbors, 14 edges)
           → ifconfig (1 neighbors, 1 edges)
[RETRIEVE-QUOTA] Query 6/6: ส่งข้อมูลเครื่องออกไปยังเครื่องสั่งการของคนร้าย...
[RETRIEVE] Query: ส่งข้อมูลเครื่องออกไปยังเครื่องสั่งการของคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PsExec (0.015), ECCENTRICBANDWAGON (0.013), POWRUNER (0.010), OopsIE (0.009), ROADSWEEP (0.007), Execution (0.007), USBStealer (0.006), Exfiltration Over C2 Channel (0.005), Input Injection (0.003), OSInfo (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → ECCENTRICBANDWAGON (8 neighbors, 8 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → PsExec (49 neighbors, 49 edges)
           → OopsIE (20 neighbors, 20 edges)
           → POWRUNER (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [4/100] retrieved=479 relevant=3 latency=11744ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 22 กุมภาพันธ์ 2567 บริษัทรับเหมาก่อสร้างแห่งหนึ่งในจังหวัดระยองแจ้งว...
[RETRIEVE] Query: เมื่อวันที่ 22 กุมภาพันธ์ 2567 บริษัทรับเหมาก่อสร้างแห่งหนึ่งในจังหวัดระยองแจ้งว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: menuPass (0.001), XLoader (0.000), Darkhotel (0.000), FIN8 (0.000), System Script Proxy Execution (0.000), Password Managers (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Pikabot (0.000), Filter Network Traffic (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → menuPass (71 neighbors, 71 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Darkhotel (24 neighbors, 24 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → XLoader (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 2/8: ดาวน์โหลดไฟล์โปรแกรมจากเครื่องภายนอกเข้ามาเก็บไว้บนดิสก์ของเครื่องที่ยึดครอง...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมจากเครื่องภายนอกเข้ามาเก็บไว้บนดิสก์ของเครื่องที่ยึดครอง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.076), cmd (0.022), PsExec (0.021), NavRAT (0.006), Cobian RAT (0.002), Archive via Utility (0.001), Visual Basic (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → PsExec (49 neighbors, 49 edges)
           → NavRAT (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 3/8: สั่งโปรแกรมที่ดาวน์โหลดมาทำงานบนเครื่องแม่ข่าย...
[RETRIEVE] Query: สั่งโปรแกรมที่ดาวน์โหลดมาทำงานบนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackConfig (0.073), PsExec (0.025), CrackMapExec (0.004), CrossRAT (0.003), Cardinal RAT (0.003), Cobian RAT (0.002), Net (0.002), Impacket (0.001), Visual Basic (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BackConfig (17 neighbors, 17 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → PsExec (49 neighbors, 49 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → At (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 4/8: อ่านแฟ้มที่โปรแกรมท่องเว็บใช้เก็บรหัสผ่านของผู้ใช้...
[RETRIEVE] Query: อ่านแฟ้มที่โปรแกรมท่องเว็บใช้เก็บรหัสผ่านของผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.683), TrickBot (0.421), TrickBot (0.240), APT3 (0.206), Empire (0.117), Password Managers (0.032), Credentials in Registry (0.012), Cachedump (0.006), gsecdump (0.005), Windows Credential Manager (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → TrickBot (57 neighbors, 57 edges)
           → Credentials In Files (44 neighbors, 44 edges)
           → APT3 (50 neighbors, 50 edges)
           → Empire (91 neighbors, 91 edges)
[RETRIEVE-QUOTA] Query 5/8: ถอดข้อมูลบัญชีและรหัสผ่านที่บันทึกไว้ในโปรแกรมท่องเว็บ...
[RETRIEVE] Query: ถอดข้อมูลบัญชีและรหัสผ่านที่บันทึกไว้ในโปรแกรมท่องเว็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cachedump (0.037), CrackMapExec (0.013), User Account Deletion (0.013), Lslsass (0.007), Neoichor (0.004), CrossRAT (0.001), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Cachedump (2 neighbors, 2 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → User Account Deletion (0 neighbors, 0 edges)
           → Lslsass (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 6/8: ดาวน์โหลดไฟล์โปรแกรมตัวที่สองเข้ามาไว้บนเครื่องเดียวกัน...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมตัวที่สองเข้ามาไว้บนเครื่องเดียวกัน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DanBot (0.128), PsExec (0.058), Get2 (0.024), Lateral Tool Transfer (0.017), WEBC2 (0.008), CrossRAT (0.003), Visual Basic (0.001), Cobian RAT (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DanBot (15 neighbors, 15 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → PsExec (49 neighbors, 49 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Get2 (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 7/8: สั่งให้โปรแกรมทำงานเบื้องหลังเพื่อดักบันทึกการกดแป้นพิมพ์ (Keylogging)...
[RETRIEVE] Query: สั่งให้โปรแกรมทำงานเบื้องหลังเพื่อดักบันทึกการกดแป้นพิมพ์ (Keylogging)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Duqu (0.680), BOULDSPY (0.665), KGH_SPY (0.421), Cuba (0.375), Keylogging (0.132), Credential API Hooking (0.031), Input Injection (0.020), Winlogon Helper DLL (0.009), Psylo (0.006), schtasks (0.006)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Duqu (21 neighbors, 21 edges)
           → Keylogging (160 neighbors, 160 edges)
           → BOULDSPY (25 neighbors, 25 edges)
           → Keylogging (25 neighbors, 25 edges)
           → KGH_SPY (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 8/8: บันทึกข้อมูลการกดแป้นพิมพ์ลงไฟล์ข้อความที่ซ่อนไว้ในเครื่อง...
[RETRIEVE] Query: บันทึกข้อมูลการกดแป้นพิมพ์ลงไฟล์ข้อความที่ซ่อนไว้ในเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MacMa (0.369), TYPEFRAME (0.002), Prevent Command History Logging (0.001), Shell History (0.001), Hidden Window (0.000), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → MacMa (28 neighbors, 28 edges)
           → Keylogging (160 neighbors, 160 edges)
           → Prevent Command History Logging (15 neighbors, 15 edges)
           → Shell History (5 neighbors, 5 edges)
           → TYPEFRAME (16 neighbors, 16 edges)
           → Fileless Storage (34 neighbors, 34 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [5/100] retrieved=778 relevant=3 latency=15772ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 24 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่า...
[RETRIEVE] Query: เมื่อวันที่ 24 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dok (0.008), AutoIt backdoor (0.002), PipeMon (0.001), System Script Proxy Execution (0.000), PipeMon (0.000), Adversary-in-the-Middle (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), ARP Cache Poisoning (0.000), Evil Twin (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Dok (11 neighbors, 11 edges)
           → AutoIt backdoor (6 neighbors, 6 edges)
           → PipeMon (24 neighbors, 24 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → System Script Proxy Execution (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 2/7: ติดตั้งไฟล์ backdoor เขียนด้วยภาษา Python ลงในเครื่องคอมพิวเตอร์...
[RETRIEVE] Query: ติดตั้งไฟล์ backdoor เขียนด้วยภาษา Python ลงในเครื่องคอมพิวเตอร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VIRTUALPIE (0.787), DropBook (0.748), DropBook (0.577), Operation Wocao (0.243), UPSTYLE (0.216), Small Sieve (0.214), Machete (0.148), THINCRUST (0.104), BPFDoor (0.002), MiniDuke (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → VIRTUALPIE (7 neighbors, 7 edges)
           → DropBook (10 neighbors, 10 edges)
           → Python (66 neighbors, 66 edges)
           → Operation Wocao (79 neighbors, 79 edges)
           → UPSTYLE (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 3/7: เพิ่มรายการเรียกใช้งานไฟล์ backdoor ในทะเบียนระบบ (Registry Run Key Persistence)...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานไฟล์ backdoor ในทะเบียนระบบ (Registry Run Key Persistence)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ke3chang (0.666), Registry Run Keys / Startup Folder (0.349), Leviathan (0.116), Active Setup (0.036), Modify Registry (0.011), RC Scripts (0.009), Spark (0.000), Samurai (0.000), Mori (0.000), Heyoka Backdoor (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Ke3chang (58 neighbors, 58 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → Leviathan (68 neighbors, 68 edges)
           → Active Setup (6 neighbors, 6 edges)
           → Modify Registry (177 neighbors, 177 edges)
[RETRIEVE-QUOTA] Query 4/7: ตั้งชื่อไฟล์ backdoor คล้ายคลึงกับชื่อผู้ผลิตซอฟต์แวร์และโปรแกรมอีเมลเพื่อหลอกผู...
[RETRIEVE] Query: ตั้งชื่อไฟล์ backdoor คล้ายคลึงกับชื่อผู้ผลิตซอฟต์แวร์และโปรแกรมอีเมลเพื่อหลอกผู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Empire (0.031), AutoIt backdoor (0.025), BackConfig (0.011), CLAIMLOADER (0.006), Spica (0.004), Dok (0.003), Helminth (0.003), Spark (0.003), Heyoka Backdoor (0.002), APT32 (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Empire (91 neighbors, 91 edges)
           → Shortcut Modification (37 neighbors, 37 edges)
           → AutoIt backdoor (6 neighbors, 6 edges)
           → BackConfig (17 neighbors, 17 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
[RETRIEVE-QUOTA] Query 5/7: โปรแกรม backdoor ติดต่อกลับไปยังคนร้าย (Command and Control)...
[RETRIEVE] Query: โปรแกรม backdoor ติดต่อกลับไปยังคนร้าย (Command and Control)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MuddyViper (0.329), BRICKSTORM (0.288), BISCUIT (0.135), Triada (0.103), Command and Control (0.090), BACKSPACE (0.021), BPFDoor (0.021), DarkComet (0.012), Comnie (0.008), AutoIt backdoor (0.005)
[RETRIEVE] Graph expansion: 6 subgraphs
           → MuddyViper (19 neighbors, 19 edges)
           → BRICKSTORM (25 neighbors, 25 edges)
           → BISCUIT (11 neighbors, 11 edges)
           → Fallback Channels (58 neighbors, 58 edges)
           → Triada (8 neighbors, 8 edges)
           → Download New Code at Runtime (42 neighbors, 42 edges)
[RETRIEVE-QUOTA] Query 6/7: รับคำสั่งผ่านแอปพลิเคชันสนทนายอดนิยมโดยใช้โพรโทคอลเว็บที่เข้ารหัสลับ...
[RETRIEVE] Query: รับคำสั่งผ่านแอปพลิเคชันสนทนายอดนิยมโดยใช้โพรโทคอลเว็บที่เข้ารหัสลับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BBSRAT (0.017), One-Way Communication (0.013), SpeakUp (0.011), Web Protocols (0.008), Bidirectional Communication (0.006), Exfiltration Over Alternative Protocol (0.006), PoshC2 (0.005), Application Layer Protocol (0.003), Cobalt Strike (0.002), Credential API Hooking (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BBSRAT (14 neighbors, 14 edges)
           → Web Protocols (424 neighbors, 424 edges)
           → One-Way Communication (14 neighbors, 14 edges)
           → SpeakUp (15 neighbors, 15 edges)
           → Bidirectional Communication (61 neighbors, 61 edges)
[RETRIEVE-QUOTA] Query 7/7: เข้ารหัสข้อมูลที่รับส่งด้วยการสลับตำแหน่งไบต์และการเข้ารหัสข้อความเพิ่มเติม (Obf...
[RETRIEVE] Query: เข้ารหัสข้อมูลที่รับส่งด้วยการสลับตำแหน่งไบต์และการเข้ารหัสข้อความเพิ่มเติม (Obf...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Encrypted/Encoded File (0.299), FRAMESTING (0.232), Command Obfuscation (0.191), PHPsert (0.178), Data Obfuscation (0.088), Obfuscated Files or Information (0.085), QUADAGENT (0.056), Empire (0.025), Deobfuscate/Decode Files or Information (0.019), Polymorphic Code (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → FRAMESTING (8 neighbors, 8 edges)
           → Data Obfuscation (21 neighbors, 21 edges)
           → Command Obfuscation (74 neighbors, 74 edges)
           → PHPsert (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [6/100] retrieved=344 relevant=4 latency=13683ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 7 มีนาคม 2567 บริษัทโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งว่าเค...
[RETRIEVE] Query: เมื่อวันที่ 7 มีนาคม 2567 บริษัทโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งว่าเค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Comnie (0.009), Proxysvc (0.001), Lokibot (0.000), FIN8 (0.000), Hijack Execution Flow (0.000), Reg (0.000), CrossRAT (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Comnie (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Proxysvc (16 neighbors, 16 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/5: Persistence mechanism using Registry Run key modification to execute malicious p...
[RETRIEVE] Query: Persistence mechanism using Registry Run key modification to execute malicious p...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Octopus (0.844), CozyCar (0.820), Registry Run Keys / Startup Folder (0.767), Boot or Logon Autostart Execution (0.735), Active Setup (0.641), LookBack (0.640), Cardinal RAT (0.484), Unix Shell Configuration Modification (0.220), Modify Registry (0.179), Login Hook (0.104)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → Boot or Logon Autostart Execution (24 neighbors, 24 edges)
           → Octopus (20 neighbors, 20 edges)
           → CozyCar (15 neighbors, 15 edges)
           → Active Setup (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 3/5: System reconnaissance collecting OS version, computer name, and hardware details...
[RETRIEVE] Query: System reconnaissance collecting OS version, computer name, and hardware details...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Epic (0.972), DarkWatchman (0.923), Octopus (0.909), Remsec (0.894), System Information Discovery (0.199), Systeminfo (0.091), Hardware (0.063), OSInfo (0.036), Response Metadata (0.028), DNS (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Epic (23 neighbors, 23 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → DarkWatchman (34 neighbors, 34 edges)
           → Octopus (20 neighbors, 20 edges)
           → Remsec (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 4/5: Process enumeration discovering all running programs on the compromised machine...
[RETRIEVE] Query: Process enumeration discovering all running programs on the compromised machine...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SDBbot (0.991), DarkTortilla (0.976), Remcos (0.964), Rising Sun (0.954), Instance Enumeration (0.109), Process Discovery (0.067), Virtual Machine Discovery (0.055), Software Discovery (0.006), Internet Connection Discovery (0.003), Privileged Process Integrity (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SDBbot (25 neighbors, 25 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → DarkTortilla (28 neighbors, 28 edges)
           → Remcos (43 neighbors, 43 edges)
           → Rising Sun (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 5/5: Unauthorized outbound network connection from accounting department computer...
[RETRIEVE] Query: Unauthorized outbound network connection from accounting department computer...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Filter Network Traffic (0.169), Filter Network Traffic (0.006), APT29 (0.004), Ping (0.004), Exfiltration Over Other Network Medium (0.004), Network Boundary Bridging (0.001), NotCompatible (0.001), Threat Group-1314 (0.001), FoggyWeb (0.001), Transfer Data to Cloud Account (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Filter Network Traffic (49 neighbors, 49 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
           → APT29 (117 neighbors, 117 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [7/100] retrieved=636 relevant=3 latency=9480ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 15 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความว่ามีการเข้าถึงข้...
[RETRIEVE] Query: เมื่อวันที่ 15 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความว่ามีการเข้าถึงข้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OS Credential Dumping (0.475), Windows Credential Editor (0.439), Axiom (0.409), Credential Access (0.354), Mustang Panda (0.346), HOMEFRY (0.284), Suckfly (0.171), Credential Access Protection (0.029), Credential Stuffing (0.011), Credentials In Files (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Axiom (24 neighbors, 24 edges)
           → Credential Access (67 neighbors, 67 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
           → Mustang Panda (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] Query 2/6: Credential Dumping โดยแทรกตัวในหน่วยความจำของกระบวนการยืนยันตัวตนระบบปฏิบัติการ...
[RETRIEVE] Query: Credential Dumping โดยแทรกตัวในหน่วยความจำของกระบวนการยืนยันตัวตนระบบปฏิบัติการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OS Credential Dumping (0.616), Mustang Panda (0.293), Credential Stuffing (0.200), Axiom (0.180), Sowbug (0.103), Credential Access (0.078), Windows Credential Editor (0.051), Credentials In Files (0.051), pwdump (0.048), Credential Access Protection (0.036)
[RETRIEVE] Graph expansion: 5 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Mustang Panda (109 neighbors, 109 edges)
           → Credential Stuffing (10 neighbors, 10 edges)
           → Axiom (24 neighbors, 24 edges)
           → Sowbug (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 3/6: ดึงค่าแฮชรหัสผ่านของบัญชีผู้ใช้จากหน่วยความจำ...
[RETRIEVE] Query: ดึงค่าแฮชรหัสผ่านของบัญชีผู้ใช้จากหน่วยความจำ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cachedump (0.667), Cachedump (0.396), Lslsass (0.245), CrackMapExec (0.161), Security Account Manager (0.030), Password Managers (0.004), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Cachedump (2 neighbors, 2 edges)
           → Cached Domain Credentials (16 neighbors, 16 edges)
           → Lslsass (2 neighbors, 2 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Security Account Manager (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 4/6: แก้ไขไฟล์ทางลัดบนเดสก์ท็อปให้ชี้ไปยังโปรแกรมที่วางไว้แทนโปรแกรมเดิม...
[RETRIEVE] Query: แก้ไขไฟล์ทางลัดบนเดสก์ท็อปให้ชี้ไปยังโปรแกรมที่วางไว้แทนโปรแกรมเดิม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kazuar (0.023), IMAPLoader (0.004), Overwrite Process Arguments (0.003), Change Default File Association (0.002), KernelCallbackTable (0.001), Visual Basic (0.001), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Kazuar (32 neighbors, 32 edges)
           → Shortcut Modification (37 neighbors, 37 edges)
           → IMAPLoader (10 neighbors, 10 edges)
           → Create or Modify System Process (25 neighbors, 25 edges)
           → Overwrite Process Arguments (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] Query 5/6: รันสคริปต์ขโมยสิทธิ์ประจำตัวจากกระบวนการของผู้ใช้รายอื่น...
[RETRIEVE] Query: รันสคริปต์ขโมยสิทธิ์ประจำตัวจากกระบวนการของผู้ใช้รายอื่น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.375), Create Process with Token (0.084), ROKRAT (0.068), RDP Hijacking (0.013), RDFSNIFFER (0.003), Visual Basic (0.001), Cobian RAT (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Create Process with Token (19 neighbors, 19 edges)
           → ROKRAT (31 neighbors, 31 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 6/6: สวมสิทธิ์ของผู้ใช้อื่นเพื่อสั่งงานในนามของผู้ใช้นั้น...
[RETRIEVE] Query: สวมสิทธิ์ของผู้ใช้อื่นเพื่อสั่งงานในนามของผู้ใช้นั้น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Token Impersonation/Theft (0.356), Make and Impersonate Token (0.173), Bankshot (0.156), GUI Input Capture (0.047), Temporary Elevated Cloud Access (0.029), APT28 (0.009), Visual Basic (0.001), CrossRAT (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Token Impersonation/Theft (26 neighbors, 26 edges)
           → Make and Impersonate Token (11 neighbors, 11 edges)
           → Bankshot (26 neighbors, 26 edges)
           → Create Process with Token (19 neighbors, 19 edges)
           → GUI Input Capture (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [8/100] retrieved=171 relevant=3 latency=11879ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 11 เมษายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความว่ามีการเข้าถึงเครื่องแ...
[RETRIEVE] Query: เมื่อวันที่ 11 เมษายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความว่ามีการเข้าถึงเครื่องแ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Credential Editor (0.258), Axiom (0.249), Suckfly (0.139), OS Credential Dumping (0.138), Ember Bear (0.116), Mimikatz (0.028), Credential Access Protection (0.027), Credential Access (0.024), Credentials In Files (0.003), Credential Stuffing (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
           → Suckfly (6 neighbors, 6 edges)
           → Ember Bear (58 neighbors, 58 edges)
[RETRIEVE-QUOTA] Query 2/6: อัปโหลดสคริปต์ข้ามการขออนุญาตยกระดับสิทธิ์ (privilege escalation exploit)...
[RETRIEVE] Query: อัปโหลดสคริปต์ข้ามการขออนุญาตยกระดับสิทธิ์ (privilege escalation exploit)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploitation for Privilege Escalation (0.811), Wingbird (0.763), APT28 (0.513), ZIRCONIUM (0.447), Privilege Escalation (0.242), Downdelph (0.170), Elevated Execution with Prompt (0.154), Exploitation for Credential Access (0.052), Exploits (0.008), Exploits (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → Wingbird (10 neighbors, 10 edges)
           → APT28 (124 neighbors, 124 edges)
           → ZIRCONIUM (29 neighbors, 29 edges)
           → Privilege Escalation (96 neighbors, 96 edges)
[RETRIEVE-QUOTA] Query 3/6: Credential Dumping ด้วยเครื่องมือที่ดัดแปลงแล้วเพื่อขโมยรหัสผ่านผู้ดูแลระบบ...
[RETRIEVE] Query: Credential Dumping ด้วยเครื่องมือที่ดัดแปลงแล้วเพื่อขโมยรหัสผ่านผู้ดูแลระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: menuPass (0.708), Credential Access (0.610), Suckfly (0.469), OS Credential Dumping (0.454), Windows Credential Editor (0.453), pwdump (0.253), Poseidon Group (0.199), Axiom (0.158), Credential Access Protection (0.130), Credentials In Files (0.034)
[RETRIEVE] Graph expansion: 5 subgraphs
           → menuPass (71 neighbors, 71 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → Credential Access (67 neighbors, 67 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Suckfly (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 4/6: นำเข้าเครื่องมือชุดใหม่จากเครื่องภายนอกเข้ามาในเครื่องที่ยึดครองได้...
[RETRIEVE] Query: นำเข้าเครื่องมือชุดใหม่จากเครื่องภายนอกเข้ามาในเครื่องที่ยึดครองได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ingress Tool Transfer (0.067), Hardware Additions (0.039), Kazuar (0.021), Cobalt Strike (0.018), Cobian RAT (0.003), Compromise Hardware Supply Chain (0.002), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Hardware Additions (5 neighbors, 5 edges)
           → Kazuar (32 neighbors, 32 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
           → Compromise Hardware Supply Chain (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 5/6: คัดลอกเครื่องมือจากเครื่องที่ยึดครองไปยังเครื่องแม่ข่ายเก็บเอกสารอื่นผ่านเครือข่...
[RETRIEVE] Query: คัดลอกเครื่องมือจากเครื่องที่ยึดครองไปยังเครื่องแม่ข่ายเก็บเอกสารอื่นผ่านเครือข่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lateral Tool Transfer (0.825), cmd (0.543), Lateral Movement (0.139), Expand (0.121), Communication Through Removable Media (0.111), Exploitation of Remote Services (0.100), Net (0.056), Network Share Discovery (0.039), SILENTTRINITY (0.017), Reaver (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → cmd (13 neighbors, 13 edges)
           → Lateral Movement (23 neighbors, 23 edges)
           → Communication Through Removable Media (7 neighbors, 7 edges)
           → Expand (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] Query 6/6: เชื่อมต่อ SSH ไปยังเครื่องแม่ข่ายเก็บเอกสารโดยใช้รหัสผ่านผู้ดูแลระบบที่ขโมยได้...
[RETRIEVE] Query: เชื่อมต่อ SSH ไปยังเครื่องแม่ข่ายเก็บเอกสารโดยใช้รหัสผ่านผู้ดูแลระบบที่ขโมยได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH Hijacking (0.128), Kobalos (0.010), Kobalos (0.009), SSH Authorized Keys (0.009), Chaos (0.005), SSH (0.004), Kessel (0.003), Cobalt Strike (0.002), Leviathan (0.001), Password Managers (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SSH Hijacking (8 neighbors, 8 edges)
           → SSH Authorized Keys (15 neighbors, 15 edges)
           → Kobalos (15 neighbors, 15 edges)
           → Data Staged (13 neighbors, 13 edges)
           → Input Capture (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [9/100] retrieved=233 relevant=4 latency=12188ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 20 ตุลาคม 2563 หน่วยงานปกครองส่วนท้องถิ่นหลายแห่งแจ้งความว่าระบบสารส...
[RETRIEVE] Query: เมื่อวันที่ 20 ตุลาคม 2563 หน่วยงานปกครองส่วนท้องถิ่นหลายแห่งแจ้งความว่าระบบสารส...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.220), FIN13 (0.203), UNC3886 (0.090), SoreFang (0.051), External Remote Services (0.048), SharePoint ToolShell Exploitation (0.004), Brute Force (0.002), Valid Accounts (0.002), Web Portal Capture (0.001), Internal Spearphishing (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → FIN13 (57 neighbors, 57 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → UNC3886 (58 neighbors, 58 edges)
           → SoreFang (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 2/8: Exploit Public-Facing Application ช่องโหว่ของเว็บแม่ข่ายหน่วยงาน...
[RETRIEVE] Query: Exploit Public-Facing Application ช่องโหว่ของเว็บแม่ข่ายหน่วยงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VOID MANTICORE (0.670), Exploit Public-Facing Application (0.559), Moses Staff (0.480), Network Segmentation (0.392), Leviathan (0.308), Exploitation for Stealth (0.002), Exploitation for Defense Impairment (0.001), Exploit Protection (0.001), Exploits (0.000), Exploitation for Client Execution (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Moses Staff (16 neighbors, 16 edges)
           → Network Segmentation (37 neighbors, 37 edges)
           → Leviathan (68 neighbors, 68 edges)
[RETRIEVE-QUOTA] Query 3/8: Drive-by Download จากหน้าเว็บที่ถูกดัดแปลง...
[RETRIEVE] Query: Drive-by Download จากหน้าเว็บที่ถูกดัดแปลง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.708), Mustard Tempest (0.189), Drive-by Compromise (0.149), Machete (0.072), APT32 (0.045), Drive-by Target (0.005), Domains (0.000), RIFLESPINE (0.000), CSPY Downloader (0.000), Drive Creation (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Drive-by Target (12 neighbors, 12 edges)
           → Mustard Tempest (14 neighbors, 14 edges)
           → Drive-by Compromise (51 neighbors, 51 edges)
           → Machete (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 4/8: External Remote Services SSL VPN เข้าถึงเครือข่ายภายในจากระยะไกล...
[RETRIEVE] Query: External Remote Services SSL VPN เข้าถึงเครือข่ายภายในจากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Remote Services (0.922), Limit Access to Resource Over Network (0.496), C0032 (0.280), Operation Wocao (0.251), Volt Typhoon (0.099), Web Portal Capture (0.068), Remote Services (0.012), Exfiltration Over Web Service (0.011), Limit Access to Resource Over Network (0.001), Search Open Technical Databases (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → External Remote Services (52 neighbors, 52 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → C0032 (19 neighbors, 19 edges)
           → Operation Wocao (79 neighbors, 79 edges)
           → Volt Typhoon (100 neighbors, 100 edges)
[RETRIEVE-QUOTA] Query 5/8: Valid Accounts ใช้บัญชีผู้ใช้ที่ถูกต้องเข้าสู่เครื่องแม่ข่ายควบคุมบัญชี...
[RETRIEVE] Query: Valid Accounts ใช้บัญชีผู้ใช้ที่ถูกต้องเข้าสู่เครื่องแม่ข่ายควบคุมบัญชี...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: User Account Management (0.084), Valid Accounts (0.072), Account Discovery (0.032), Cloud Accounts (0.020), User Account Control (0.013), User Account Management (0.010), Application Developer Guidance (0.010), Account Use Policies (0.001), User Account Modification (0.001), Establish Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Valid Accounts (82 neighbors, 82 edges)
           → User Account Management (119 neighbors, 119 edges)
           → Account Discovery (18 neighbors, 18 edges)
           → Cloud Accounts (33 neighbors, 33 edges)
           → User Account Control (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 6/8: Valid Accounts ใช้บัญชีผู้ใช้เข้าสู่ระบบจดหมายอิเล็กทรอนิกส์แบบคลาวด์...
[RETRIEVE] Query: Valid Accounts ใช้บัญชีผู้ใช้เข้าสู่ระบบจดหมายอิเล็กทรอนิกส์แบบคลาวด์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cloud Accounts (0.563), Cloud Services (0.423), Valid Accounts (0.056), Application Developer Guidance (0.048), Cloud Account (0.016), Cloud Accounts (0.008), User Account Management (0.005), AADInternals (0.000), User Account Modification (0.000), Establish Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Cloud Accounts (33 neighbors, 33 edges)
           → Cloud Services (9 neighbors, 9 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Application Developer Guidance (24 neighbors, 24 edges)
           → Cloud Account (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 7/8: Brute Force เดารหัสผ่านซ้ำ ๆ...
[RETRIEVE] Query: Brute Force เดารหัสผ่านซ้ำ ๆ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Brute Force (0.887), Password Guessing (0.493), APT28 (0.241), APT38 (0.057), User Account Management (0.034), Password Policy Discovery (0.011), CrackMapExec (0.007), Wordlist Scanning (0.005), Forced Authentication (0.001), Brute Ratel C4 (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Brute Force (34 neighbors, 34 edges)
           → Password Guessing (19 neighbors, 19 edges)
           → APT28 (124 neighbors, 124 edges)
           → APT38 (62 neighbors, 62 edges)
           → User Account Management (119 neighbors, 119 edges)
[RETRIEVE-QUOTA] Query 8/8: SQL Injection ส่งคำสั่งฐานข้อมูลแทรกเข้าไปทางหน้าเว็บ...
[RETRIEVE] Query: SQL Injection ส่งคำสั่งฐานข้อมูลแทรกเข้าไปทางหน้าเว็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Havij (0.044), Havij (0.022), Content Injection (0.008), SQLRat (0.005), Thread Local Storage (0.004), Process Injection (0.003), SQL Stored Procedures (0.003), Dynamic-link Library Injection (0.002), HTRAN (0.002), Cardinal RAT (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Havij (2 neighbors, 2 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Content Injection (8 neighbors, 8 edges)
           → SQLRat (9 neighbors, 9 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [10/100] retrieved=238 relevant=5 latency=14783ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 5 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งในจังหวัดชลบุรีแจ้งความว่าข้อ...
[RETRIEVE] Query: เมื่อวันที่ 5 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งในจังหวัดชลบุรีแจ้งความว่าข้อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.026), SDBbot (0.021), PUNCHTRACK (0.009), ShimRat (0.008), FrameworkPOS (0.004), Pillowmint (0.002), Pillowmint (0.001), Pillowmint (0.000), RawPOS (0.000), Application Shimming (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → SDBbot (25 neighbors, 25 edges)
           → PUNCHTRACK (4 neighbors, 4 edges)
           → ShimRat (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 2/8: รันคำสั่งบรรทัดเดียวผ่านหน้าต่างคำสั่งของระบบเพื่อติดตั้ง Application Shimming...
[RETRIEVE] Query: รันคำสั่งบรรทัดเดียวผ่านหน้าต่างคำสั่งของระบบเพื่อติดตั้ง Application Shimming...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pillowmint (0.104), SDBbot (0.048), Application Shimming (0.036), ShimRat (0.011), FIN7 (0.007), FRAMESTING (0.001), Application Isolation and Sandboxing (0.001), Skidmap (0.000), ListPlanting (0.000), MimiPenguin (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pillowmint (16 neighbors, 16 edges)
           → PowerShell (241 neighbors, 241 edges)
           → SDBbot (25 neighbors, 25 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → ShimRat (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 3/8: ติดตั้ง Application Shimming เพื่อให้โปรแกรมของคนร้ายทำงานซ้ำหลังจากรีสตาร์ต...
[RETRIEVE] Query: ติดตั้ง Application Shimming เพื่อให้โปรแกรมของคนร้ายทำงานซ้ำหลังจากรีสตาร์ต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SDBbot (0.400), Pillowmint (0.278), ShimRat (0.226), Application Shimming (0.225), FIN7 (0.152), Re-opened Applications (0.007), Create or Modify System Process (0.007), Launch Agent (0.005), AppInit DLLs (0.001), SYNful Knock (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SDBbot (25 neighbors, 25 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → Pillowmint (16 neighbors, 16 edges)
           → ShimRat (22 neighbors, 22 edges)
           → FIN7 (86 neighbors, 86 edges)
[RETRIEVE-QUOTA] Query 4/8: อัปโหลดโปรแกรมปลอมแปลงเป็นเครื่องมือตรวจสอบข้อผิดพลาดของระบบ...
[RETRIEVE] Query: อัปโหลดโปรแกรมปลอมแปลงเป็นเครื่องมือตรวจสอบข้อผิดพลาดของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FakeSpy (0.108), Starloader (0.035), GUI Input Capture (0.002), UACMe (0.001), CrossRAT (0.000), pwdump (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FakeSpy (15 neighbors, 15 edges)
           → System Checks (18 neighbors, 18 edges)
           → Starloader (3 neighbors, 3 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
           → GUI Input Capture (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 5/8: ไล่ตรวจสอบรายการโปรแกรมที่กำลังทำงาน (Process Discovery)...
[RETRIEVE] Query: ไล่ตรวจสอบรายการโปรแกรมที่กำลังทำงาน (Process Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.394), Process Discovery (0.364), SodaMaster (0.261), KillDisk (0.121), Taidoor (0.121), Tasklist (0.076), Software Discovery (0.029), System Owner/User Discovery (0.003), System Network Connections Discovery (0.001), Discovery (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Process Discovery (320 neighbors, 320 edges)
           → Tasklist (19 neighbors, 19 edges)
           → SodaMaster (12 neighbors, 12 edges)
           → KillDisk (18 neighbors, 18 edges)
           → Taidoor (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 6/8: ดึงข้อมูลบัตรเครดิตจากหน่วยความจำ (Credential Access)...
[RETRIEVE] Query: ดึงข้อมูลบัตรเครดิตจากหน่วยความจำ (Credential Access)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FrameworkPOS (0.162), Security Account Manager (0.105), RawPOS (0.105), Credential Access Protection (0.075), Credential Access (0.057), Exploitation for Credential Access (0.006), Credential Access Protection (0.006), Forge Web Credentials (0.001), Windows Credential Manager (0.000), Limit Access to Resource Over Network (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FrameworkPOS (6 neighbors, 6 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → RawPOS (6 neighbors, 6 edges)
           → Credential Access Protection (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 7/8: บีบอัดข้อมูลบัตรเครดิตเป็นไฟล์เดียว...
[RETRIEVE] Query: บีบอัดข้อมูลบัตรเครดิตเป็นไฟล์เดียว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Compression (0.009), Expand (0.005), BitPaymer (0.002), COATHANGER (0.001), Invoke-PSImage (0.000), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Compression (38 neighbors, 38 edges)
           → Expand (3 neighbors, 3 edges)
           → BitPaymer (19 neighbors, 19 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → COATHANGER (18 neighbors, 18 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] Query 8/8: นำข้อมูลบัตรเครดิตออกจากเครื่อง (Exfiltration)...
[RETRIEVE] Query: นำข้อมูลบัตรเครดิตออกจากเครื่อง (Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration (0.126), FIN6 (0.114), FrameworkPOS (0.095), Exfiltration Over Physical Medium (0.053), Exfiltration over USB (0.045), Automated Exfiltration (0.016), Exfiltration Over Alternative Protocol (0.010), Empire (0.004), Exbyte (0.003), Exbyte (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration (19 neighbors, 19 edges)
           → FIN6 (52 neighbors, 52 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → FrameworkPOS (6 neighbors, 6 edges)
           → Archive via Custom Method (42 neighbors, 42 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [11/100] retrieved=350 relevant=4 latency=15237ms
[RETRIEVE-QUOTA] Query 1/4: เมื่อวันที่ 28 สิงหาคม 2566 บริษัทที่ปรึกษาด้านวิศวกรรมแห่งหนึ่งแจ้งความว่าเอกสา...
[RETRIEVE] Query: เมื่อวันที่ 28 สิงหาคม 2566 บริษัทที่ปรึกษาด้านวิศวกรรมแห่งหนึ่งแจ้งความว่าเอกสา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: schtasks (0.005), Ursnif (0.002), APT-C-36 (0.001), Operation Honeybee (0.001), Koadic (0.001), Scheduled Task/Job (0.001), System Script Proxy Execution (0.000), APT-C-36 (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → schtasks (4 neighbors, 4 edges)
           → Ursnif (36 neighbors, 36 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Operation Honeybee (33 neighbors, 33 edges)
           → Windows Service (150 neighbors, 150 edges)
[RETRIEVE-QUOTA] Query 2/4: Windows Remote Management (WinRM) ใช้สั่งให้สคริปต์ทำงานบนเครื่องปลายทาง...
[RETRIEVE] Query: Windows Remote Management (WinRM) ใช้สั่งให้สคริปต์ทำงานบนเครื่องปลายทาง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SolarWinds Compromise (0.603), Cobalt Strike (0.490), Windows Remote Management (0.466), Network Segmentation (0.050), Windows Management Instrumentation (0.011), Windows Command Shell (0.006), RemoteCMD (0.005), Remote Desktop Software (0.001), Remote Data Storage (0.000), Customer Relationship Management Software (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SolarWinds Compromise (83 neighbors, 83 edges)
           → Windows Remote Management (16 neighbors, 16 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
           → Network Segmentation (37 neighbors, 37 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
[RETRIEVE-QUOTA] Query 3/4: Scheduled Task ตั้งงานเพื่อให้โปรแกรมทำงานซ้ำตามช่วงเวลาที่กำหนด...
[RETRIEVE] Query: Scheduled Task ตั้งงานเพื่อให้โปรแกรมทำงานซ้ำตามช่วงเวลาที่กำหนด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Scheduled Task/Job (0.875), schtasks (0.644), TrickBot (0.498), Scheduled Task (0.476), schtasks (0.402), at (0.350), Confucius (0.263), Scheduled Job Modification (0.008), Scheduled Job Metadata (0.002), Masquerade Task or Service (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Scheduled Task/Job (18 neighbors, 18 edges)
           → schtasks (4 neighbors, 4 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → TrickBot (57 neighbors, 57 edges)
           → at (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 4/4: อัปโหลดไฟล์เอกสารโครงการลูกค้าไปยังบัญชีบริการรับฝากข้อมูลออนไลน์ที่ไม่ใช่ของบริ...
[RETRIEVE] Query: อัปโหลดไฟล์เอกสารโครงการลูกค้าไปยังบัญชีบริการรับฝากข้อมูลออนไลน์ที่ไม่ใช่ของบริ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OilCheck (0.307), SampleCheck5000 (0.037), Transfer Data to Cloud Account (0.019), Exfiltration to Cloud Storage (0.014), Exfiltration Over Alternative Protocol (0.007), Exfiltration Over Other Network Medium (0.004), Exfiltration to Code Repository (0.004), APT28 Nearest Neighbor Campaign (0.003), Exfiltration (0.003), Empire (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → OilCheck (4 neighbors, 4 edges)
           → Exfiltration Over Web Service (23 neighbors, 23 edges)
           → SampleCheck5000 (12 neighbors, 12 edges)
           → Transfer Data to Cloud Account (9 neighbors, 9 edges)
           → Exfiltration to Cloud Storage (48 neighbors, 48 edges)
[RETRIEVE-QUOTA] 12 vectors (quota 3/query), 8 subgraphs from 4 queries
  [12/100] retrieved=290 relevant=3 latency=8614ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 14 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Query: เมื่อวันที่ 14 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ursnif (0.035), LockBit 2.0 (0.016), APT29 (0.010), PsExec (0.006), REvil (0.001), Reg (0.000), Registry Run Keys / Startup Folder (0.000), Active Setup (0.000), Windows Registry Key Modification (0.000), Windows Registry Key Access (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Ursnif (36 neighbors, 36 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
           → APT29 (117 neighbors, 117 edges)
           → RC Scripts (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 2/6: ใช้บัญชีผู้ใช้ที่ได้มาก่อนหน้าเข้าถึงเครื่องคอมพิวเตอร์ในห้องควบคุม...
[RETRIEVE] Query: ใช้บัญชีผู้ใช้ที่ได้มาก่อนหน้าเข้าถึงเครื่องคอมพิวเตอร์ในห้องควบคุม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VOID MANTICORE (0.066), Valid Accounts (0.031), Qilin (0.020), QuasarRAT (0.019), RCSession (0.010), Windows Remote Management (0.006), Bypass User Account Control (0.005), User Account Control (0.002), Access Token Manipulation (0.001), Additional Local or Domain Groups (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Domain Accounts (47 neighbors, 47 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Qilin (54 neighbors, 54 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
[RETRIEVE-QUOTA] Query 3/6: ผลักไฟล์โปรแกรมเข้าไปยังเครื่องปลายทางผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบบ...
[RETRIEVE] Query: ผลักไฟล์โปรแกรมเข้าไปยังเครื่องปลายทางผ่านช่องแบ่งปันไฟล์สำหรับผู้ดูแลระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT3 (0.040), PsExec (0.018), Taint Shared Content (0.006), ftp (0.004), cmd (0.003), Lateral Tool Transfer (0.003), Shared Modules (0.003), cmd (0.003), PsExec (0.002), Expand (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT3 (50 neighbors, 50 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → PsExec (49 neighbors, 49 edges)
           → Taint Shared Content (18 neighbors, 18 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 4/6: สร้างบริการของระบบขึ้นใหม่เพื่อเรียกใช้โปรแกรมที่ผลักเข้ามาด้วยสิทธิ์ระดับระบบ...
[RETRIEVE] Query: สร้างบริการของระบบขึ้นใหม่เพื่อเรียกใช้โปรแกรมที่ผลักเข้ามาด้วยสิทธิ์ระดับระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Azorult (0.176), Create or Modify System Process (0.105), PsExec (0.070), Bypass User Account Control (0.025), Systemd Service (0.025), Create Process with Token (0.010), ZxShell (0.008), gh0st RAT (0.007), Elevated Execution with Prompt (0.007), Parent PID Spoofing (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Azorult (17 neighbors, 17 edges)
           → Create Process with Token (19 neighbors, 19 edges)
           → Create or Modify System Process (25 neighbors, 25 edges)
           → PsExec (49 neighbors, 49 edges)
           → Windows Service (150 neighbors, 150 edges)
[RETRIEVE-QUOTA] Query 5/6: เพิ่มรายการเรียกใช้งานโปรแกรมไว้ใน Registry Run Key เพื่อคงการทำงานอัตโนมัติ...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานโปรแกรมไว้ใน Registry Run Key เพื่อคงการทำงานอัตโนมัติ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.477), RunningRAT (0.475), Ursnif (0.393), Ixeshe (0.346), LockBit 2.0 (0.285), Boot or Logon Autostart Execution (0.031), Active Setup (0.026), Windows Registry Key Access (0.002), Windows Registry Key Modification (0.002), Modify Registry (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → RunningRAT (10 neighbors, 10 edges)
           → Ursnif (36 neighbors, 36 edges)
           → Ixeshe (16 neighbors, 16 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 6/6: เข้าใช้งานเครื่องผ่านช่องทางเดสก์ท็อประยะไกล (RDP) เพื่อกระตุ้นให้โปรแกรมทำงาน...
[RETRIEVE] Query: เข้าใช้งานเครื่องผ่านช่องทางเดสก์ท็อประยะไกล (RDP) เพื่อกระตุ้นให้โปรแกรมทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Desktop Protocol (0.352), RDP Hijacking (0.335), Operating System Configuration (0.112), Terminal Services DLL (0.069), Carbanak (0.054), SILENTTRINITY (0.016), Remote Access Tools (0.010), PingPull (0.003), FRP (0.000), DUSTTRAP (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → Accessibility Features (15 neighbors, 15 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [13/100] retrieved=489 relevant=3 latency=11132ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 8 กันยายน 2565 โรงเรียนมัธยมแห่งหนึ่งในจังหวัดสงขลาแจ้งความว่าระบบทะ...
[RETRIEVE] Query: เมื่อวันที่ 8 กันยายน 2565 โรงเรียนมัธยมแห่งหนึ่งในจังหวัดสงขลาแจ้งความว่าระบบทะ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Medusa Group (0.157), APT29 (0.142), Koadic (0.013), Windows Management Instrumentation (0.007), Windows Management Instrumentation Event Subscription (0.000), Unsecured Credentials (0.000), Query Registry (0.000), Windows Remote Management (0.000), Security Account Manager (0.000), Password Managers (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Medusa Group (62 neighbors, 62 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → APT29 (117 neighbors, 117 edges)
           → Koadic (31 neighbors, 31 edges)
           → Windows Management Instrumentation Event Subscription (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 2/6: ใช้ชื่อผู้ใช้และรหัสผ่านของเจ้าหน้าที่ที่หลุดออกไปเข้าสู่ระบบผ่านแอปพลิเคชันของโ...
[RETRIEVE] Query: ใช้ชื่อผู้ใช้และรหัสผ่านของเจ้าหน้าที่ที่หลุดออกไปเข้าสู่ระบบผ่านแอปพลิเคชันของโ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ROKRAT (0.002), Unsecured Credentials (0.001), H1N1 (0.001), Astaroth (0.000), Astaroth (0.000), Valid Accounts (0.000), Web Credential Usage (0.000), OS Credential Dumping (0.000), Windows Credential Manager (0.000), Cloud Services (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → ROKRAT (31 neighbors, 31 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → Unsecured Credentials (27 neighbors, 27 edges)
           → H1N1 (13 neighbors, 13 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] Query 3/6: เรียกใช้ Windows Management Instrumentation เพื่อดำเนินการบนระบบ...
[RETRIEVE] Query: เรียกใช้ Windows Management Instrumentation เพื่อดำเนินการบนระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: EKANS (0.963), Windows Management Instrumentation (0.907), CrackMapExec (0.718), Koadic (0.709), PoshC2 (0.689), Windows Management Instrumentation Event Subscription (0.529), MMC (0.033), Windows Remote Management (0.016), Scheduled Task (0.001), Distributed Component Object Model (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → EKANS (9 neighbors, 9 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Koadic (31 neighbors, 31 edges)
           → PoshC2 (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 4/6: แทรกไฟล์อันตรายลงในโฟลเดอร์ที่ใช้แบ่งปันร่วมกันภายในองค์กร...
[RETRIEVE] Query: แทรกไฟล์อันตรายลงในโฟลเดอร์ที่ใช้แบ่งปันร่วมกันภายในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Taint Shared Content (0.365), Gamaredon Group (0.056), Gamaredon Group (0.047), Restrict File and Directory Permissions (0.004), Lateral Tool Transfer (0.004), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Taint Shared Content (18 neighbors, 18 edges)
           → Gamaredon Group (76 neighbors, 76 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Component Object Model (27 neighbors, 27 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 5/6: โจมตีช่องโหว่ของบริการจัดการเครื่องพิมพ์บนเครื่องแม่ข่ายเพื่อยกระดับสิทธิ์เป็นผู...
[RETRIEVE] Query: โจมตีช่องโหว่ของบริการจัดการเครื่องพิมพ์บนเครื่องแม่ข่ายเพื่อยกระดับสิทธิ์เป็นผู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Empire (0.159), Exploitation for Privilege Escalation (0.103), Gelsemium (0.038), Exploitation for Credential Access (0.005), Service Execution (0.002), Cobian RAT (0.002), CrossRAT (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Empire (91 neighbors, 91 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → Gelsemium (33 neighbors, 33 edges)
           → Exploitation for Credential Access (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 6/6: เข้ารหัสลับระบบทะเบียนนักเรียน...
[RETRIEVE] Query: เข้ารหัสลับระบบทะเบียนนักเรียน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.001), Credentials in Registry (0.001), OwaAuth (0.000), InnaputRAT (0.000), Security Account Manager (0.000), OwaAuth (0.000), DRYHOOK (0.000), Reversible Encryption (0.000), Windows Credential Manager (0.000), Invisible Unicode (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
           → OwaAuth (8 neighbors, 8 edges)
           → Archive via Custom Method (42 neighbors, 42 edges)
           → InnaputRAT (11 neighbors, 11 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [14/100] retrieved=404 relevant=4 latency=11784ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 3 ธันวาคม 2566 สำนักงานกฎหมายแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่ามีผู...
[RETRIEVE] Query: เมื่อวันที่ 3 ธันวาคม 2566 สำนักงานกฎหมายแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่ามีผู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.114), SSH Hijacking (0.015), Cobalt Strike (0.015), LP-Notes (0.008), Kessel (0.004), Ramsay (0.004), File Deletion (0.002), DarkWatchman (0.002), SSH (0.001), GlassWorm (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → SSH (33 neighbors, 33 edges)
           → SSH Hijacking (8 neighbors, 8 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
           → LP-Notes (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 2/7: โปรแกรมฝังตัวบนเครื่องคอมพิวเตอร์ทนายความรับคำสั่งจากภายนอก...
[RETRIEVE] Query: โปรแกรมฝังตัวบนเครื่องคอมพิวเตอร์ทนายความรับคำสั่งจากภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Attor (0.009), CrossRAT (0.006), Cobian RAT (0.006), PsExec (0.005), BRICKSTORM (0.005), Havoc (0.005), Cardinal RAT (0.002), Extra Window Memory Injection (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Attor (35 neighbors, 35 edges)
           → CrossRAT (6 neighbors, 6 edges)
           → Cobian RAT (8 neighbors, 8 edges)
           → BRICKSTORM (25 neighbors, 25 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 3/7: ลบไฟล์โปรแกรมดักบันทึกแป้นพิมพ์และบันทึกผลเพื่อลบร่องรอย...
[RETRIEVE] Query: ลบไฟล์โปรแกรมดักบันทึกแป้นพิมพ์และบันทึกผลเพื่อลบร่องรอย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LockBit 2.0 (0.009), Uroburos (0.006), DUSTTRAP (0.005), File Deletion (0.003), gh0st RAT (0.003), Lslsass (0.001), PUNCHTRACK (0.001), Indicator Removal from Tools (0.000), Clear Windows Event Logs (0.000), Windows Registry Key Deletion (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → LockBit 2.0 (26 neighbors, 26 edges)
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Uroburos (37 neighbors, 37 edges)
           → File Deletion (310 neighbors, 310 edges)
           → DUSTTRAP (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 4/7: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่จากเครื่องสั่งการภายนอก...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่จากเครื่องสั่งการภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.100), Zen (0.059), xCmd (0.006), PsExec (0.006), RemoteCMD (0.004), dsquery (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Zen (8 neighbors, 8 edges)
           → Download New Code at Runtime (42 neighbors, 42 edges)
           → xCmd (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 5/7: ตั้งชื่อไฟล์โปรแกรมให้ดูเหมือนไฟล์ชั่วคราวของระบบ...
[RETRIEVE] Query: ตั้งชื่อไฟล์โปรแกรมให้ดูเหมือนไฟล์ชั่วคราวของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Space after Filename (0.033), Overwrite Process Arguments (0.010), admin@338 (0.009), ccf32 (0.004), Change Default File Association (0.002), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Space after Filename (4 neighbors, 4 edges)
           → Overwrite Process Arguments (3 neighbors, 3 edges)
           → admin@338 (19 neighbors, 19 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
           → ccf32 (13 neighbors, 13 edges)
           → Local Data Staging (138 neighbors, 138 edges)
[RETRIEVE-QUOTA] Query 6/7: คัดลอกไฟล์โปรแกรมไปยังเครื่องแม่ข่ายเว็บของสำนักงาน...
[RETRIEVE] Query: คัดลอกไฟล์โปรแกรมไปยังเครื่องแม่ข่ายเว็บของสำนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.045), esentutl (0.010), PsExec (0.008), spwebmember (0.002), CrossRAT (0.000), Visual Basic (0.000), Impacket (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → esentutl (9 neighbors, 9 edges)
           → PsExec (49 neighbors, 49 edges)
           → spwebmember (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 7/7: เชื่อมต่อ SSH ด้วยรหัสผ่านของผู้ใช้รายที่สาม...
[RETRIEVE] Query: เชื่อมต่อ SSH ด้วยรหัสผ่านของผู้ใช้รายที่สาม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH Hijacking (0.127), Bundlore (0.041), SSH Authorized Keys (0.038), SSH (0.021), XCSSET (0.013), Cobalt Strike (0.001), Kessel (0.001), Leviathan (0.000), Forced Authentication (0.000), Password Guessing (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SSH Hijacking (8 neighbors, 8 edges)
           → SSH Authorized Keys (15 neighbors, 15 edges)
           → Bundlore (23 neighbors, 23 edges)
           → SSH (33 neighbors, 33 edges)
           → XCSSET (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [15/100] retrieved=184 relevant=3 latency=14574ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 19 พฤษภาคม 2567 บริษัทหลักทรัพย์แห่งหนึ่งแจ้งความว่าหน้าจอการทำงานขอ...
[RETRIEVE] Query: เมื่อวันที่ 19 พฤษภาคม 2567 บริษัทหลักทรัพย์แห่งหนึ่งแจ้งความว่าหน้าจอการทำงานขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VERMIN (0.018), RogueRobin (0.003), Screen Capture (0.000), Exfiltration Over C2 Channel (0.000), FIN8 (0.000), Video Capture (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), CrossRAT (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → VERMIN (17 neighbors, 17 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → RogueRobin (19 neighbors, 19 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/8: ดาวน์โหลดสคริปต์ถ่ายภาพหน้าจอเข้ามาบนเครื่องเป้าหมาย...
[RETRIEVE] Query: ดาวน์โหลดสคริปต์ถ่ายภาพหน้าจอเข้ามาบนเครื่องเป้าหมาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AsyncRAT (0.053), Ginp (0.035), Screen Capture (0.031), Video Capture (0.003), Visual Basic (0.001), Cobian RAT (0.000), 4H RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AsyncRAT (23 neighbors, 23 edges)
           → Video Capture (37 neighbors, 37 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → Ginp (12 neighbors, 12 edges)
           → Screen Capture (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 3/8: สั่งให้สคริปต์ถ่ายภาพหน้าจอทำงาน...
[RETRIEVE] Query: สั่งให้สคริปต์ถ่ายภาพหน้าจอทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BISCUIT (0.252), Screen Capture (0.035), AhRat (0.010), S.O.V.A. (0.004), AsyncRAT (0.004), Video Capture (0.002), AppleScript (0.002), Invoke-PSImage (0.001), Trap (0.001), Image File Execution Options Injection (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → BISCUIT (11 neighbors, 11 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → AhRat (15 neighbors, 15 edges)
           → Screen Capture (31 neighbors, 31 edges)
           → S.O.V.A. (19 neighbors, 19 edges)
           → Input Injection (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 4/8: ส่งภาพหน้าจอออกไปภายนอก (exfiltration)...
[RETRIEVE] Query: ส่งภาพหน้าจอออกไปภายนอก (exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Physical Medium (0.133), eSurv (0.058), Exfiltration over USB (0.057), Exfiltration Over Other Network Medium (0.044), Exfiltration (0.021), Exfiltration Over Alternative Protocol (0.021), Exfiltration Over C2 Channel (0.007), Exbyte (0.006), APT28 Nearest Neighbor Campaign (0.006), Salesforce Data Exfiltration (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration Over Physical Medium (6 neighbors, 6 edges)
           → Exfiltration over USB (13 neighbors, 13 edges)
           → eSurv (10 neighbors, 10 edges)
           → Data from Local System (56 neighbors, 56 edges)
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 5/8: เขียนชุดข้อมูลโปรแกรมควบคุมระยะไกลลงในทะเบียนระบบเพื่อหลีกเลี่ยงการตรวจจับ...
[RETRIEVE] Query: เขียนชุดข้อมูลโปรแกรมควบคุมระยะไกลลงในทะเบียนระบบเพื่อหลีกเลี่ยงการตรวจจับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Modify Registry (0.012), Mori (0.009), Regsvr32 (0.006), Execution Prevention (0.002), Regsvcs/Regasm (0.002), NOOPLDR (0.001), Execution Prevention (0.001), Remote Data Storage (0.001), Rogue Domain Controller (0.000), Ptrace System Calls (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Modify Registry (177 neighbors, 177 edges)
           → Mori (10 neighbors, 10 edges)
           → Regsvr32 (39 neighbors, 39 edges)
           → Regsvcs/Regasm (5 neighbors, 5 edges)
           → Execution Prevention (79 neighbors, 79 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 6/8: อ่านชุดข้อมูลที่ซ่อนไว้ในทะเบียนระบบกลับออกมา...
[RETRIEVE] Query: อ่านชุดข้อมูลที่ซ่อนไว้ในทะเบียนระบบกลับออกมา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Query Registry (0.047), Cachedump (0.043), njRAT (0.020), Credentials in Registry (0.013), LSA Secrets (0.006), InvisiMole (0.004), Security Account Manager (0.003), HiddenFace (0.002), Dtrack (0.001), Proc Filesystem (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Query Registry (121 neighbors, 121 edges)
           → Cachedump (2 neighbors, 2 edges)
           → njRAT (40 neighbors, 40 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
           → LSA Secrets (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 7/8: แปลงกลับข้อมูลให้อยู่ในรูปที่ประมวลผลได้...
[RETRIEVE] Query: แปลงกลับข้อมูลให้อยู่ในรูปที่ประมวลผลได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sliver (0.012), Invoke-PSImage (0.003), Mythic (0.003), Visual Basic (0.002), Data Encoding (0.001), Standard Encoding (0.001), reGeorg (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Sliver (27 neighbors, 27 edges)
           → Steganography (17 neighbors, 17 edges)
           → Visual Basic (140 neighbors, 140 edges)
           → Mythic (13 neighbors, 13 edges)
           → Data Encoding (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 8/8: สั่งให้โปรแกรมควบคุมระยะไกลขั้นที่สองทำงานในหน่วยความจำ...
[RETRIEVE] Query: สั่งให้โปรแกรมควบคุมระยะไกลขั้นที่สองทำงานในหน่วยความจำ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Proc Memory (0.001), CrackMapExec (0.001), Thread Execution Hijacking (0.001), Bumblebee (0.001), Extra Window Memory Injection (0.000), Process Hollowing (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Proc Memory (7 neighbors, 7 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → At (17 neighbors, 17 edges)
           → Thread Execution Hijacking (9 neighbors, 9 edges)
           → Extra Window Memory Injection (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [16/100] retrieved=421 relevant=3 latency=14969ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 26 ตุลาคม 2565 คลินิกเวชกรรมเครือข่ายแห่งหนึ่งแจ้งความว่าข้อมูลคนไข้...
[RETRIEVE] Query: เมื่อวันที่ 26 ตุลาคม 2565 คลินิกเวชกรรมเครือข่ายแห่งหนึ่งแจ้งความว่าข้อมูลคนไข้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.131), Cobalt Strike (0.006), DCHSpy (0.004), DRYHOOK (0.004), SSH Hijacking (0.000), Remote Service Session Hijacking (0.000), SSH (0.000), Kessel (0.000), Valid Accounts (0.000), POSHSPY (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → SSH (33 neighbors, 33 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
           → DCHSpy (13 neighbors, 13 edges)
           → Contact List (61 neighbors, 61 edges)
[RETRIEVE-QUOTA] Query 2/6: ช่องโหว่ที่ยังไม่ได้แก้ไขในอุปกรณ์เชื่อมต่อเครือข่ายส่วนตัวเสมือน (VPN unpatched...
[RETRIEVE] Query: ช่องโหว่ที่ยังไม่ได้แก้ไขในอุปกรณ์เชื่อมต่อเครือข่ายส่วนตัวเสมือน (VPN unpatched...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Application Isolation and Sandboxing (0.171), Vulnerability Scanning (0.028), Exploitation of Remote Services (0.011), FIN13 (0.007), Exploitation for Client Execution (0.006), Exploit Public-Facing Application (0.006), Volt Typhoon (0.005), Exploit Protection (0.004), Valid Accounts (0.001), Web Portal Capture (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Application Isolation and Sandboxing (14 neighbors, 14 edges)
           → Exploitation for Credential Access (9 neighbors, 9 edges)
           → Vulnerability Scanning (5 neighbors, 5 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
           → FIN13 (57 neighbors, 57 edges)
           → External Remote Services (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] Query 3/6: ล็อกอินเข้าอุปกรณ์เชื่อมต่อระยะไกลโดยใช้ชื่อผู้ใช้และรหัสผ่านที่รั่วไหล (credent...
[RETRIEVE] Query: ล็อกอินเข้าอุปกรณ์เชื่อมต่อระยะไกลโดยใช้ชื่อผู้ใช้และรหัสผ่านที่รั่วไหล (credent...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Threat Group-1314 (0.333), Valid Accounts (0.079), LAPSUS$ (0.031), APT18 (0.029), Steal or Forge Authentication Certificates (0.019), Kinsing (0.005), ROKRAT (0.004), Remote Access Hardware (0.003), MechaFlounder (0.002), BRONZE BUTLER (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Threat Group-1314 (6 neighbors, 6 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
           → APT18 (17 neighbors, 17 edges)
           → External Remote Services (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] Query 4/6: เปิดการเชื่อมต่อต่อเนื่องผ่าน SSH ไปยังเครื่องอื่นในวงเครือข่ายภายใน (SSH latera...
[RETRIEVE] Query: เปิดการเชื่อมต่อต่อเนื่องผ่าน SSH ไปยังเครื่องอื่นในวงเครือข่ายภายใน (SSH latera...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH Hijacking (0.749), APT5 (0.306), Exploitation of Remote Services (0.150), Lateral Movement (0.114), Kinsing (0.087), GCMAN (0.072), Indrik Spider (0.059), Lateral Tool Transfer (0.021), SSH (0.016), Filter Network Traffic (0.006)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SSH Hijacking (8 neighbors, 8 edges)
           → APT5 (43 neighbors, 43 edges)
           → SSH (33 neighbors, 33 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
           → Lateral Movement (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 5/6: เชื่อมต่อระยะไกลไปยังเครื่องอื่นผ่านเดสก์ท็อประยะไกล (remote desktop lateral mov...
[RETRIEVE] Query: เชื่อมต่อระยะไกลไปยังเครื่องอื่นผ่านเดสก์ท็อประยะไกล (remote desktop lateral mov...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RDP Hijacking (0.777), Net (0.445), HEXANE (0.429), hcdLoader (0.337), ConnectWise (0.321), Exploitation of Remote Services (0.173), Lateral Movement (0.128), SILENTTRINITY (0.025), Network Share Discovery (0.023), Lateral Tool Transfer (0.018)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → Net (50 neighbors, 50 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → HEXANE (48 neighbors, 48 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
[RETRIEVE-QUOTA] Query 6/6: เข้าถึงข้อมูลคนไข้ในระบบ (patient data access)...
[RETRIEVE] Query: เข้าถึงข้อมูลคนไข้ในระบบ (patient data access)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Active Directory Object Access (0.009), NanoCore (0.002), Network Share Access (0.002), SILENTTRINITY (0.002), Pegasus for iOS (0.001), Remsec (0.001), Cloud Storage Access (0.000), Drive Access (0.000), Gather Victim Identity Information (0.000), Data from Cloud Storage (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Active Directory Object Access (0 neighbors, 0 edges)
           → NanoCore (17 neighbors, 17 edges)
           → Video Capture (37 neighbors, 37 edges)
           → Network Share Access (0 neighbors, 0 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [17/100] retrieved=245 relevant=3 latency=12644ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 2 กันยายน 2567 บริษัทประกันภัยแห่งหนึ่งแจ้งความว่าบัญชีผู้ดูแลระบบขอ...
[RETRIEVE] Query: เมื่อวันที่ 2 กันยายน 2567 บริษัทประกันภัยแห่งหนึ่งแจ้งความว่าบัญชีผู้ดูแลระบบขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN6 (0.003), Security Account Manager (0.000), Unsecured Credentials (0.000), Valid Accounts (0.000), FIN8 (0.000), Daggerfly (0.000), Clear Windows Event Logs (0.000), Exploitation for Credential Access (0.000), Clear Linux or Mac System Logs (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → FIN6 (52 neighbors, 52 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → Unsecured Credentials (27 neighbors, 27 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/6: ใช้เครื่องมือสาธารณะร้องขอตั๋วยืนยันสิทธิ์ของบัญชีบริการจากระบบยืนยันตัวตนขององค...
[RETRIEVE] Query: ใช้เครื่องมือสาธารณะร้องขอตั๋วยืนยันสิทธิ์ของบัญชีบริการจากระบบยืนยันตัวตนขององค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Active Directory Credential Request (0.169), PowerSploit (0.153), Mimikatz (0.027), Rubeus (0.027), Pass the Ticket (0.007), Steal or Forge Kerberos Tickets (0.003), Cloud Account (0.002), Kerberoasting (0.002), ZxShell (0.000), Trust Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Active Directory Credential Request (0 neighbors, 0 edges)
           → PowerSploit (39 neighbors, 39 edges)
           → Kerberoasting (18 neighbors, 18 edges)
           → Mimikatz (77 neighbors, 77 edges)
           → Pass the Ticket (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 3/6: ถอดรหัสตั๋วยืนยันสิทธิ์นอกระบบเพื่อให้ได้รหัสผ่านบัญชีบริการ...
[RETRIEVE] Query: ถอดรหัสตั๋วยืนยันสิทธิ์นอกระบบเพื่อให้ได้รหัสผ่านบัญชีบริการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerSploit (0.161), Pass the Ticket (0.078), AADInternals (0.075), Silver Ticket (0.051), Golden Ticket (0.029), Mimikatz (0.006), Steal or Forge Kerberos Tickets (0.003), Astaroth (0.002), Reversible Encryption (0.001), Security Account Manager (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PowerSploit (39 neighbors, 39 edges)
           → Kerberoasting (18 neighbors, 18 edges)
           → Pass the Ticket (13 neighbors, 13 edges)
           → AADInternals (26 neighbors, 26 edges)
           → Silver Ticket (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 4/6: เปิดการเชื่อมต่อหน้าจอระยะไกล (RDP) เข้ามายังเครื่องเป้าหมายภายในองค์กร...
[RETRIEVE] Query: เปิดการเชื่อมต่อหน้าจอระยะไกล (RDP) เข้ามายังเครื่องเป้าหมายภายในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RDP Hijacking (0.097), Remote Desktop Protocol (0.045), Limit Access to Resource Over Network (0.044), Terminal Services DLL (0.030), Operating System Configuration (0.026), Carbanak (0.018), SILENTTRINITY (0.014), Remote Access Tools (0.002), FRP (0.000), DUSTTRAP (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Accessibility Features (15 neighbors, 15 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 5/6: ส่งไฟล์สคริปต์และไฟล์โปรแกรมเรียกค่าไถ่ผ่านการแบ่งปันไดรฟ์ระยะไกล...
[RETRIEVE] Query: ส่งไฟล์สคริปต์และไฟล์โปรแกรมเรียกค่าไถ่ผ่านการแบ่งปันไดรฟ์ระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Taint Shared Content (0.586), CHOPSTICK (0.057), Network Share Discovery (0.028), SEASHARPEE (0.027), RIFLESPINE (0.013), cmd (0.010), Ingress Tool Transfer (0.004), Lateral Tool Transfer (0.003), Shared Modules (0.003), Cobalt Strike (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Taint Shared Content (18 neighbors, 18 edges)
           → CHOPSTICK (20 neighbors, 20 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
           → SEASHARPEE (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 6/6: ติดตั้งโปรแกรมเรียกค่าไถ่บนเครื่องของผู้เสียหาย...
[RETRIEVE] Query: ติดตั้งโปรแกรมเรียกค่าไถ่บนเครื่องของผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kerrdown (0.035), CLAIMLOADER (0.017), Black Basta (0.014), CallMe (0.014), Shamoon (0.008), OopsIE (0.002), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Kerrdown (12 neighbors, 12 edges)
           → Black Basta (27 neighbors, 27 edges)
           → Internal Defacement (18 neighbors, 18 edges)
           → CLAIMLOADER (12 neighbors, 12 edges)
           → CallMe (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [18/100] retrieved=241 relevant=3 latency=11957ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 14 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Query: เมื่อวันที่ 14 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.003), DRYHOOK (0.001), Threat Group-3390 (0.000), Magic Hound (0.000), Unsecured Credentials (0.000), Internal Spearphishing (0.000), Clear Windows Event Logs (0.000), Wevtutil (0.000), Password Managers (0.000), Clear Linux or Mac System Logs (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Keylogging (160 neighbors, 160 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Threat Group-3390 (81 neighbors, 81 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
[RETRIEVE-QUOTA] Query 2/9: Phishing หรือ Exploitation ของช่องโหว่ Remote Code Execution บนเว็บเซิร์ฟเวอร์...
[RETRIEVE] Query: Phishing หรือ Exploitation ของช่องโหว่ Remote Code Execution บนเว็บเซิร์ฟเวอร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploitation for Client Execution (0.837), Conficker (0.770), Exploitation of Remote Services (0.731), Phishing for Information (0.129), P.A.S. Webshell (0.096), Phishing (0.044), User Execution (0.024), VOID MANTICORE (0.013), Kimsuky (0.007), Spearphishing Link (0.003)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Exploitation for Client Execution (65 neighbors, 65 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
           → Conficker (13 neighbors, 13 edges)
           → Phishing for Information (12 neighbors, 12 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Web Shell (71 neighbors, 71 edges)
[RETRIEVE-QUOTA] Query 3/9: อัปโหลดไฟล์โปรแกรมและสคริปต์เว็บเพื่อสั่งการจากระยะไกล (Web Shell)...
[RETRIEVE] Query: อัปโหลดไฟล์โปรแกรมและสคริปต์เว็บเพื่อสั่งการจากระยะไกล (Web Shell)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: P.A.S. Webshell (0.679), P.A.S. Webshell (0.488), Web Shell (0.455), ZxShell (0.258), BUSHWALK (0.177), China Chopper (0.120), StreamEx (0.068), Windows Command Shell (0.029), SSH Hijacking (0.015), LunarWeb (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Web Shell (71 neighbors, 71 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → ZxShell (37 neighbors, 37 edges)
           → BUSHWALK (7 neighbors, 7 edges)
           → China Chopper (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 4/9: แก้ไขไฟล์บันทึกเหตุการณ์ของระบบเพื่อลบหลักฐานการบุกรุก...
[RETRIEVE] Query: แก้ไขไฟล์บันทึกเหตุการณ์ของระบบเพื่อลบหลักฐานการบุกรุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File Deletion (0.132), Clear Persistence (0.122), Clear Windows Event Logs (0.069), Indicator Removal (0.057), Disable or Modify Windows Event Log (0.005), BACKSPACE (0.003), FIN5 (0.002), gh0st RAT (0.002), VIRTUALPITA (0.001), Prevent Command History Logging (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → Clear Persistence (19 neighbors, 19 edges)
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Indicator Removal (45 neighbors, 45 edges)
           → Disable or Modify Windows Event Log (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 5/9: ลบไฟล์ที่สร้างขึ้นเพื่อกลบร่องรอยการเข้าถึง...
[RETRIEVE] Query: ลบไฟล์ที่สร้างขึ้นเพื่อกลบร่องรอยการเข้าถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File Deletion (0.239), MacSpy (0.024), Clear Persistence (0.016), Dtrack (0.005), Disable or Remove Feature or Program (0.001), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → MacSpy (9 neighbors, 9 edges)
           → Clear Persistence (19 neighbors, 19 edges)
           → Dtrack (24 neighbors, 24 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
[RETRIEVE-QUOTA] Query 6/9: รวบรวมรายชื่อผู้ใช้และรหัสผ่านจากระบบ...
[RETRIEVE] Query: รวบรวมรายชื่อผู้ใช้และรหัสผ่านจากระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SILENTTRINITY (0.510), HOPLIGHT (0.404), Lslsass (0.057), gsecdump (0.054), Mimikatz (0.054), Visual Basic (0.001), Cobian RAT (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SILENTTRINITY (53 neighbors, 53 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → HOPLIGHT (23 neighbors, 23 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → Lslsass (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 7/9: รวบรวมกุญแจหลัก (Private Keys) ของระบบ...
[RETRIEVE] Query: รวบรวมกุญแจหลัก (Private Keys) ของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AADInternals (0.472), Keychain (0.217), Private Keys (0.168), Empire (0.037), Peirates (0.011), Cachedump (0.006), APT3 (0.002), Prikormka (0.001), Skeleton Key (0.000), Environmental Keying (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AADInternals (26 neighbors, 26 edges)
           → Private Keys (26 neighbors, 26 edges)
           → Keychain (16 neighbors, 16 edges)
           → Empire (91 neighbors, 91 edges)
           → Peirates (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 8/9: รวบรวมกฎของไฟร์วอลล์...
[RETRIEVE] Query: รวบรวมกฎของไฟร์วอลล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Firewall Enumeration (0.905), Firewall Metadata (0.480), Firewall Rule Modification (0.465), Cloud Firewall (0.203), Firewall Disable (0.013), OilRig (0.000), FIN7 (0.000), admin@338 (0.000), POWERTON (0.000), Local Storage Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Firewall Enumeration (0 neighbors, 0 edges)
           → Firewall Metadata (0 neighbors, 0 edges)
           → Firewall Rule Modification (0 neighbors, 0 edges)
           → Cloud Firewall (5 neighbors, 5 edges)
           → Firewall Disable (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 9/9: บีบอัดไฟล์ที่รวบรวมไว้เพื่อเตรียมการส่งออก...
[RETRIEVE] Query: บีบอัดไฟล์ที่รวบรวมไว้เพื่อเตรียมการส่งออก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lurid (0.266), TajMahal (0.097), Compression (0.073), Archive Collected Data (0.023), Archive via Utility (0.017), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), The White Company (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Lurid (3 neighbors, 3 edges)
           → Archive Collected Data (62 neighbors, 62 edges)
           → TajMahal (24 neighbors, 24 edges)
           → Automated Collection (77 neighbors, 77 edges)
           → Compression (38 neighbors, 38 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [19/100] retrieved=531 relevant=3 latency=17134ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 21 ตุลาคม 2567 บริษัทผู้ผลิตชิ้นส่วนยานยนต์แห่งหนึ่งในจังหวัดปทุมธาน...
[RETRIEVE] Query: เมื่อวันที่ 21 ตุลาคม 2567 บริษัทผู้ผลิตชิ้นส่วนยานยนต์แห่งหนึ่งในจังหวัดปทุมธาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FlawedAmmyy (0.009), LookBack (0.003), Stuxnet (0.003), FIN8 (0.000), Software (0.000), CrossRAT (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Visual Basic (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FlawedAmmyy (24 neighbors, 24 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → LookBack (16 neighbors, 16 edges)
           → System Service Discovery (71 neighbors, 71 edges)
           → Stuxnet (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 2/5: โปรแกรมไม่พึงประสงค์เรียกดูรายการการเชื่อมต่อเครือข่ายที่เปิดค้างอยู่ (netstat e...
[RETRIEVE] Query: โปรแกรมไม่พึงประสงค์เรียกดูรายการการเชื่อมต่อเครือข่ายที่เปิดค้างอยู่ (netstat e...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QakBot (0.673), Ramsay (0.537), netstat (0.520), PoshC2 (0.290), netstat (0.212), nbtstat (0.010), System Network Connections Discovery (0.003), Nltest (0.002), spwebmember (0.001), Instance Enumeration (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → QakBot (74 neighbors, 74 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → Ramsay (39 neighbors, 39 edges)
           → netstat (16 neighbors, 16 edges)
           → PoshC2 (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 3/5: โปรแกรมเก็บรวบรวมข้อมูลประจำเครื่อง ชื่อเครื่อง รุ่นระบบปฏิบัติการ และการตั้งค่า...
[RETRIEVE] Query: โปรแกรมเก็บรวบรวมข้อมูลประจำเครื่อง ชื่อเครื่อง รุ่นระบบปฏิบัติการ และการตั้งค่า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BUBBLEWRAP (0.666), ViperRAT (0.365), ifconfig (0.156), nbtstat (0.046), ipconfig (0.031), Cobian RAT (0.004), CrossRAT (0.004), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BUBBLEWRAP (4 neighbors, 4 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → ViperRAT (13 neighbors, 13 edges)
           → System Network Configuration Discovery (52 neighbors, 52 edges)
           → ifconfig (1 neighbors, 1 edges)
[RETRIEVE-QUOTA] Query 4/5: โปรแกรมสอบถามความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนองค์กรกับโดเมนอื่น (domain t...
[RETRIEVE] Query: โปรแกรมสอบถามความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนองค์กรกับโดเมนอื่น (domain t...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BADHATCH (0.959), QakBot (0.893), Domain Trust Discovery (0.736), Brute Ratel C4 (0.671), Nltest (0.259), Network Trust Dependencies (0.034), Subvert Trust Controls (0.002), OSInfo (0.001), Search Open Technical Databases (0.000), Network Service Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BADHATCH (36 neighbors, 36 edges)
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → QakBot (74 neighbors, 74 edges)
           → Brute Ratel C4 (33 neighbors, 33 edges)
           → Nltest (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 5/5: โปรแกรมตรวจสอบสมาชิกของกลุ่มสิทธิ์ที่บัญชีผู้ใช้เป็นสมาชิก (group membership enu...
[RETRIEVE] Query: โปรแกรมตรวจสอบสมาชิกของกลุ่มสิทธิ์ที่บัญชีผู้ใช้เป็นสมาชิก (group membership enu...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT3 (0.308), StealBit (0.281), APT41 (0.248), IcedID (0.189), Nltest (0.054), spwebmember (0.043), Local Account (0.009), Group Modification (0.008), Domain Account (0.005), Instance Enumeration (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT3 (50 neighbors, 50 edges)
           → Permission Groups Discovery (18 neighbors, 18 edges)
           → StealBit (15 neighbors, 15 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → APT41 (116 neighbors, 116 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [20/100] retrieved=578 relevant=4 latency=9958ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 17 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งซึ่งประกอบธุรกิจซื้อขายสินทรัพย...
[RETRIEVE] Query: เมื่อวันที่ 17 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งซึ่งประกอบธุรกิจซื้อขายสินทรัพย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Fakecalls (0.176), MacMa (0.131), APT39 (0.065), CURIUM (0.061), Exfiltration Over C2 Channel (0.045), Automated Exfiltration (0.014), Scheduled Transfer (0.012), Exfiltration Over Alternative Protocol (0.001), Exfiltration Over Unencrypted Non-C2 Protocol (0.000), Installer Packages (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Fakecalls (11 neighbors, 11 edges)
           → Exfiltration Over C2 Channel (31 neighbors, 31 edges)
           → MacMa (28 neighbors, 28 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → APT39 (64 neighbors, 64 edges)
[RETRIEVE-QUOTA] Query 2/7: หลอกให้ติดตั้งโปรแกรมซื้อขายปลอมบนเครื่องแมค...
[RETRIEVE] Query: หลอกให้ติดตั้งโปรแกรมซื้อขายปลอมบนเครื่องแมค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CoinTicker (0.072), MacSpy (0.055), XCSSET (0.037), Agent Smith (0.026), iKitten (0.015), CrossRAT (0.001), Cobian RAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → CoinTicker (9 neighbors, 9 edges)
           → MacSpy (9 neighbors, 9 edges)
           → XCSSET (33 neighbors, 33 edges)
           → Masquerading (81 neighbors, 81 edges)
           → Agent Smith (9 neighbors, 9 edges)
           → Compromise Application Executable (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 3/7: ชุดคำสั่งในตัวติดตั้งทำงานอัตโนมัติหลังการติดตั้งเสร็จสิ้น...
[RETRIEVE] Query: ชุดคำสั่งในตัวติดตั้งทำงานอัตโนมัติหลังการติดตั้งเสร็จสิ้น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: njRAT (0.289), Installer Packages (0.165), LightSpy (0.010), EventBot (0.006), Boot or Logon Autostart Execution (0.003), InstallUtil (0.001), Active Setup (0.001), XDG Autostart Entries (0.001), Authentication Package (0.001), Re-opened Applications (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → njRAT (40 neighbors, 40 edges)
           → Compile After Delivery (12 neighbors, 12 edges)
           → Installer Packages (8 neighbors, 8 edges)
           → LightSpy (52 neighbors, 52 edges)
           → Boot or Logon Initialization Scripts (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 4/7: ย้ายไฟล์ตั้งค่าไปวางในโฟลเดอร์ Scheduled Task/Job: Launchd เพื่อให้โปรแกรมทำงานเ...
[RETRIEVE] Query: ย้ายไฟล์ตั้งค่าไปวางในโฟลเดอร์ Scheduled Task/Job: Launchd เพื่อให้โปรแกรมทำงานเ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operating System Configuration (0.078), Launch Daemon (0.049), Scheduled Task/Job (0.035), Operating System Configuration (0.024), Re-opened Applications (0.007), User Account Management (0.006), At (0.005), Registry Run Keys / Startup Folder (0.004), Scheduled Task (0.004), Systemd Service (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Operating System Configuration (39 neighbors, 39 edges)
           → Scheduled Task/Job (18 neighbors, 18 edges)
           → Launch Daemon (18 neighbors, 18 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Re-opened Applications (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/7: เก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่กำลังใช้งาน (System Owner/User Dis...
[RETRIEVE] Query: เก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้ที่กำลังใช้งาน (System Owner/User Dis...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Owner/User Discovery (0.964), Epic (0.911), Micropsia (0.909), T9000 (0.890), Kimsuky (0.856), System Service Discovery (0.085), System Information Discovery (0.080), System Location Discovery (0.055), System Network Connections Discovery (0.036), Device Driver Discovery (0.005)
[RETRIEVE] Graph expansion: 5 subgraphs
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Epic (23 neighbors, 23 edges)
           → Micropsia (17 neighbors, 17 edges)
           → T9000 (13 neighbors, 13 edges)
           → Kimsuky (150 neighbors, 150 edges)
[RETRIEVE-QUOTA] Query 6/7: เข้ารหัสข้อมูลที่รวบรวมด้วยกุญแจที่ฝังไว้ในตัวโปรแกรม...
[RETRIEVE] Query: เข้ารหัสข้อมูลที่รวบรวมด้วยกุญแจที่ฝังไว้ในตัวโปรแกรม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Fooder (0.124), RegDuke (0.021), DUSTPAN (0.013), Credential API Hooking (0.012), DRYHOOK (0.011), Cachedump (0.010), gsecdump (0.004), Encrypted/Encoded File (0.002), Software Packing (0.002), Password Managers (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Fooder (8 neighbors, 8 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → RegDuke (11 neighbors, 11 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → Credential API Hooking (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งข้อมูลออกไปยังเว็บไซต์สั่งการของคนร้ายผ่าน C2 Channel (Exfiltration Over C2 C...
[RETRIEVE] Query: ส่งข้อมูลออกไปยังเว็บไซต์สั่งการของคนร้ายผ่าน C2 Channel (Exfiltration Over C2 C...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over C2 Channel (0.968), Kevin (0.950), Okrum (0.909), APT39 (0.875), Automated Exfiltration (0.855), OopsIE (0.820), Exfiltration to Text Storage Sites (0.812), Scheduled Transfer (0.793), Exfiltration Over Unencrypted Non-C2 Protocol (0.460), Data Staged (0.008)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Automated Exfiltration (33 neighbors, 33 edges)
           → Exfiltration to Text Storage Sites (4 neighbors, 4 edges)
           → Scheduled Transfer (21 neighbors, 21 edges)
           → Kevin (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [21/100] retrieved=329 relevant=4 latency=13769ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 6 พฤศจิกายน 2566 สถานเอกอัครราชทูตแห่งหนึ่งแจ้งว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Query: เมื่อวันที่ 6 พฤศจิกายน 2566 สถานเอกอัครราชทูตแห่งหนึ่งแจ้งว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackdoorDiplomacy (0.044), BackdoorDiplomacy (0.009), File Deletion (0.003), APT-C-36 (0.002), Ursnif (0.001), APT-C-36 (0.000), Internal Spearphishing (0.000), Password Managers (0.000), Data Encrypted for Impact (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → BackdoorDiplomacy (20 neighbors, 20 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Peripheral Device Discovery (60 neighbors, 60 edges)
           → File Deletion (310 neighbors, 310 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/9: ลบไฟล์เครื่องมือสั่งงานเครื่องระยะไกล (remote command execution tools) ออกจากเคร...
[RETRIEVE] Query: ลบไฟล์เครื่องมือสั่งงานเครื่องระยะไกล (remote command execution tools) ออกจากเคร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ODAgent (0.386), RemoteCMD (0.035), Disable or Remove Feature or Program (0.026), RemoteUtilities (0.009), ESXi Administration Command (0.008), Execution Prevention (0.006), Hypervisor CLI (0.004), Remote Access Tools (0.004), Unix Shell (0.001), Tonto Team (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → ODAgent (10 neighbors, 10 edges)
           → File Deletion (310 neighbors, 310 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 3/9: ลบไฟล์ตัวติดตั้งโปรแกรมฝังตัว (implant installer) ออกจากเครื่องแม่ข่ายเก็บไฟล์...
[RETRIEVE] Query: ลบไฟล์ตัวติดตั้งโปรแกรมฝังตัว (implant installer) ออกจากเครื่องแม่ข่ายเก็บไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TriangleDB (0.378), SUNSPOT (0.044), CreepyDrive (0.005), InstallUtil (0.003), Executable Installer File Permissions Weakness (0.001), SDBbot (0.001), PipeMon (0.000), Installer Packages (0.000), ISMInjector (0.000), Triton Safety Instrumented System Attack (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → TriangleDB (13 neighbors, 13 edges)
           → File Deletion (23 neighbors, 23 edges)
           → SUNSPOT (14 neighbors, 14 edges)
           → File Deletion (310 neighbors, 310 edges)
           → CreepyDrive (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 4/9: ลบไฟล์เครื่องมือดึงรหัสผ่าน (credential extraction tools) ออกจากเครื่องแม่ข่ายเก...
[RETRIEVE] Query: ลบไฟล์เครื่องมือดึงรหัสผ่าน (credential extraction tools) ออกจากเครื่องแม่ข่ายเก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Daggerfly (0.019), Security Account Manager (0.015), pwdump (0.012), Windows Credential Editor (0.010), OS Credential Dumping (0.004), menuPass (0.003), APT33 (0.002), Tonto Team (0.002), Impacket (0.001), Group Policy Preferences (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Daggerfly (23 neighbors, 23 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → pwdump (7 neighbors, 7 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 5/9: โปรแกรมฝังตัวไล่แจกแจงรายการโปรแกรมที่กำลังทำงาน (process enumeration)...
[RETRIEVE] Query: โปรแกรมฝังตัวไล่แจกแจงรายการโปรแกรมที่กำลังทำงาน (process enumeration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MacMa (0.286), POORAIM (0.195), SombRAT (0.130), Tasklist (0.090), Proc Memory (0.020), Instance Enumeration (0.016), Pod Enumeration (0.014), spwebmember (0.006), Process Discovery (0.004), Process Injection (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → MacMa (28 neighbors, 28 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → POORAIM (7 neighbors, 7 edges)
           → SombRAT (25 neighbors, 25 edges)
           → Tasklist (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 6/9: ค้นหากระบวนการที่ทำงานภายใต้สิทธิ์ผู้ดูแลโดเมน (domain admin process discovery)...
[RETRIEVE] Query: ค้นหากระบวนการที่ทำงานภายใต้สิทธิ์ผู้ดูแลโดเมน (domain admin process discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain Trust Discovery (0.343), Process Discovery (0.205), Latrodectus (0.077), Domain Groups (0.059), BADHATCH (0.050), TAINTEDSCRIBE (0.020), Ke3chang (0.011), System Owner/User Discovery (0.009), OSInfo (0.001), File and Directory Discovery (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Latrodectus (45 neighbors, 45 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Domain Groups (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] Query 7/9: สร้างบัญชีผู้ใช้ใหม่ในโดเมนขององค์กร (domain user account creation)...
[RETRIEVE] Query: สร้างบัญชีผู้ใช้ใหม่ในโดเมนขององค์กร (domain user account creation)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Active Directory Object Creation (0.784), Net (0.710), Domain Account (0.658), Empire (0.608), User Account Creation (0.191), Local Account (0.031), User Account Management (0.028), Domain Account (0.023), Turla (0.016), SoreFang (0.014)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Domain Account (18 neighbors, 18 edges)
           → Active Directory Object Creation (0 neighbors, 0 edges)
           → Net (50 neighbors, 50 edges)
           → Empire (91 neighbors, 91 edges)
           → User Account Creation (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 8/9: กำหนดสิทธิ์ระดับผู้ดูแลให้กับบัญชีผู้ใช้ใหม่ (domain admin privilege assignment)...
[RETRIEVE] Query: กำหนดสิทธิ์ระดับผู้ดูแลให้กับบัญชีผู้ใช้ใหม่ (domain admin privilege assignment)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Privileged Account Management (0.090), Domain Account (0.042), Domain Accounts (0.033), Empire (0.016), Additional Local or Domain Groups (0.002), Additional Cloud Roles (0.002), LitePower (0.001), Network Logon Script (0.000), Parent PID Spoofing (0.000), Disable or Modify Linux Audit System Log (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Privileged Account Management (112 neighbors, 112 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Domain Account (18 neighbors, 18 edges)
           → Domain Accounts (47 neighbors, 47 edges)
           → Empire (91 neighbors, 91 edges)
[RETRIEVE-QUOTA] Query 9/9: ใช้บัญชีผู้ดูแลใหม่เป็นช่องทางกลับเข้าเครื่องแม่ข่ายเก็บไฟล์ (persistence via ad...
[RETRIEVE] Query: ใช้บัญชีผู้ดูแลใหม่เป็นช่องทางกลับเข้าเครื่องแม่ข่ายเก็บไฟล์ (persistence via ad...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LAPSUS$ (0.069), POWERSOURCE (0.051), Additional Cloud Roles (0.006), Cloud Accounts (0.002), Valak (0.001), Local Account (0.000), Compromise Accounts (0.000), Ember Bear (0.000), User Account Management (0.000), Password Managers (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → LAPSUS$ (45 neighbors, 45 edges)
           → Cloud Account (9 neighbors, 9 edges)
           → POWERSOURCE (7 neighbors, 7 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → Additional Cloud Roles (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [22/100] retrieved=726 relevant=3 latency=18159ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 30 มิถุนายน 2565 บริษัทขนส่งแห่งหนึ่งในจังหวัดพระนครศรีอยุธยาแจ้งควา...
[RETRIEVE] Query: เมื่อวันที่ 30 มิถุนายน 2565 บริษัทขนส่งแห่งหนึ่งในจังหวัดพระนครศรีอยุธยาแจ้งควา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.005), Data Encrypted for Impact (0.003), BlackByte (0.001), Deobfuscate/Decode Files or Information (0.001), Adversary-in-the-Middle (0.000), Evil Twin (0.000), Magic Hound (0.000), ARP Cache Poisoning (0.000), Threat Group-3390 (0.000), Anthropic AI-orchestrated Campaign (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → BlackByte (56 neighbors, 56 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
[RETRIEVE-QUOTA] Query 2/8: เรียกใช้โหมดปลอดภัย (Safe Mode) เพื่อหลีกเลี่ยงโปรแกรมด้านความปลอดภัย...
[RETRIEVE] Query: เรียกใช้โหมดปลอดภัย (Safe Mode) เพื่อหลีกเลี่ยงโปรแกรมด้านความปลอดภัย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Qilin (0.679), Safe Mode Boot (0.639), RansomHub (0.077), Disable or Remove Feature or Program (0.001), Execution Prevention (0.001), Restrict Library Loading (0.001), Restrict Library Loading (0.001), Gold Dragon (0.000), Bankshot (0.000), StrifeWater (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Safe Mode Boot (10 neighbors, 10 edges)
           → Qilin (54 neighbors, 54 edges)
           → RansomHub (21 neighbors, 21 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → Execution Prevention (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] Query 3/8: เข้ารหัสลับไฟล์งานในเครื่องแม่ข่ายและเครื่องลูกข่ายด้วยอัลกอริทึมสมมาตร 256-bit...
[RETRIEVE] Query: เข้ารหัสลับไฟล์งานในเครื่องแม่ข่ายและเครื่องลูกข่ายด้วยอัลกอริทึมสมมาตร 256-bit...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: StarProxy (0.723), ComRAT (0.549), BOOSTWRITE (0.302), TONESHELL (0.074), Encrypted/Encoded File (0.030), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.024), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.018), LockBit 2.0 (0.004), StealBit (0.002), UPPERCUT (0.002)
[RETRIEVE] Graph expansion: 6 subgraphs
           → StarProxy (10 neighbors, 10 edges)
           → Symmetric Cryptography (188 neighbors, 188 edges)
           → ComRAT (23 neighbors, 23 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → BOOSTWRITE (6 neighbors, 6 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
[RETRIEVE-QUOTA] Query 4/8: เข้ารหัสซ้ำกุญแจด้วยกุญแจสาธารณะ 2048-bit...
[RETRIEVE] Query: เข้ารหัสซ้ำกุญแจด้วยกุญแจสาธารณะ 2048-bit...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HELLOKITTY (0.230), NotPetya (0.017), Kapeka (0.003), BlackByte (0.002), LockBit 2.0 (0.001), BlackByte Ransomware (0.001), UPPERCUT (0.001), Pikabot (0.000), StealBit (0.000), Pikabot Distribution February 2024 (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → HELLOKITTY (6 neighbors, 6 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → NotPetya (15 neighbors, 15 edges)
           → Kapeka (15 neighbors, 15 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
[RETRIEVE-QUOTA] Query 5/8: ลบข้อมูลสำรองในเครื่อง...
[RETRIEVE] Query: ลบข้อมูลสำรองในเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SDelete (0.188), Inhibit System Recovery (0.064), Volume Deletion (0.021), MegaCortex (0.017), DEADWOOD (0.005), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SDelete (7 neighbors, 7 edges)
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → Volume Deletion (0 neighbors, 0 edges)
           → MegaCortex (16 neighbors, 16 edges)
           → Disk Content Wipe (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 6/8: ปิดตัวเลือกการกู้คืนระบบ (System Recovery)...
[RETRIEVE] Query: ปิดตัวเลือกการกู้คืนระบบ (System Recovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Inhibit System Recovery (0.827), ROADSWEEP (0.392), Operating System Configuration (0.111), EKANS (0.109), System Shutdown/Reboot (0.011), TURNEDUP (0.001), SDelete (0.001), SystemBC (0.000), Systeminfo (0.000), DnsSystem (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → ROADSWEEP (16 neighbors, 16 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → EKANS (9 neighbors, 9 edges)
           → System Shutdown/Reboot (32 neighbors, 32 edges)
[RETRIEVE-QUOTA] Query 7/8: ลบสำเนาเงาของไฟล์ (Volume Shadow Copies)...
[RETRIEVE] Query: ลบสำเนาเงาของไฟล์ (Volume Shadow Copies)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Conti (0.957), ROADSWEEP (0.652), Inhibit System Recovery (0.239), Snapshot Deletion (0.029), Volume Deletion (0.010), /etc/passwd and /etc/shadow (0.005), Direct Volume Access (0.002), Image Deletion (0.002), ShadowPad (0.001), ShadowRay (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Conti (18 neighbors, 18 edges)
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → ROADSWEEP (16 neighbors, 16 edges)
           → Snapshot Deletion (0 neighbors, 0 edges)
           → Volume Deletion (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 8/8: แสดงข้อความเรียกค่าไถ่ (Ransom Note)...
[RETRIEVE] Query: แสดงข้อความเรียกค่าไถ่ (Ransom Note)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RansomHub (0.222), Moneybird (0.025), INC Ransom (0.004), Embargo (0.002), Black Basta (0.002), Avaddon (0.001), RansomHub (0.001), Akira (0.001), JCry (0.001), RansomHub (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RansomHub (21 neighbors, 21 edges)
           → Internal Defacement (18 neighbors, 18 edges)
           → Moneybird (3 neighbors, 3 edges)
           → INC Ransom (33 neighbors, 33 edges)
           → Embargo (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [23/100] retrieved=587 relevant=2 latency=15897ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 25 มกราคม 2567 โรงแรมแห่งหนึ่งในจังหวัดภูเก็ตแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Query: เมื่อวันที่ 25 มกราคม 2567 โรงแรมแห่งหนึ่งในจังหวัดภูเก็ตแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Denis (0.001), Darkhotel (0.001), RDP Hijacking (0.000), FIN8 (0.000), Reg (0.000), Scheduled Task/Job (0.000), Windows Remote Management (0.000), Right-to-Left Override (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Denis (21 neighbors, 21 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Darkhotel (24 neighbors, 24 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 2/5: ควบคุมเครื่องคอมพิวเตอร์จากระยะไกล (Remote Access)...
[RETRIEVE] Query: ควบคุมเครื่องคอมพิวเตอร์จากระยะไกล (Remote Access)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Access Tools (0.455), Execution Prevention (0.421), RemoteCMD (0.316), RemoteUtilities (0.262), Execution Prevention (0.249), Remote Desktop Software (0.106), RemoteCMD (0.102), RemoteCMD (0.085), Windows Remote Management (0.064), Drive Access (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Remote Access Tools (31 neighbors, 31 edges)
           → Execution Prevention (79 neighbors, 79 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → Remote Desktop Software (21 neighbors, 21 edges)
           → RemoteUtilities (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 3/5: โปรแกรมแปลกปลอมบันทึกภาพจอของพนักงาน (Screen Capture)...
[RETRIEVE] Query: โปรแกรมแปลกปลอมบันทึกภาพจอของพนักงาน (Screen Capture)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: POORAIM (0.485), PowerSploit (0.273), AsyncRAT (0.087), Screen Capture (0.056), GUI Input Capture (0.016), Keydnap (0.014), Video Capture (0.009), HenBox (0.008), Input Capture (0.005), Audio Capture (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → POORAIM (7 neighbors, 7 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → PowerSploit (39 neighbors, 39 edges)
           → AsyncRAT (23 neighbors, 23 edges)
           → Video Capture (37 neighbors, 37 edges)
[RETRIEVE-QUOTA] Query 4/5: เรียกใช้ไฟล์โปรแกรมผ่านหน้าต่างพิมพ์คำสั่งระบบปฏิบัติการวินโดวส์...
[RETRIEVE] Query: เรียกใช้ไฟล์โปรแกรมผ่านหน้าต่างพิมพ์คำสั่งระบบปฏิบัติการวินโดวส์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Forfiles (0.210), cmd (0.045), cmd (0.034), Kasidet (0.022), Indirect Command Execution (0.015), NETWIRE (0.012), Windows Command Shell (0.011), PsExec (0.006), Tasklist (0.005), Nebulae (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Forfiles (4 neighbors, 4 edges)
           → cmd (13 neighbors, 13 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Kasidet (10 neighbors, 10 edges)
           → Indirect Command Execution (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 5/5: ไล่ตรวจสอบรายการกระบวนการที่กำลังทำงานบนเครื่อง (Process Discovery)...
[RETRIEVE] Query: ไล่ตรวจสอบรายการกระบวนการที่กำลังทำงานบนเครื่อง (Process Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.678), APT3 (0.498), Process Discovery (0.365), KillDisk (0.171), Taidoor (0.160), Tasklist (0.069), System Information Discovery (0.010), System Owner/User Discovery (0.008), System Network Connections Discovery (0.003), Discovery (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → APT3 (50 neighbors, 50 edges)
           → KillDisk (18 neighbors, 18 edges)
           → Taidoor (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [24/100] retrieved=630 relevant=3 latency=10216ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 12 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งว่าเครื่องคอมพิวเต...
[RETRIEVE] Query: เมื่อวันที่ 12 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งว่าเครื่องคอมพิวเต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.048), APT29 (0.040), Password Spraying (0.025), CrackMapExec (0.003), Password Cracking (0.001), Password Guessing (0.000), Password Managers (0.000), Active Setup (0.000), Subvert Trust Controls (0.000), Password Policies (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Password Spraying (23 neighbors, 23 edges)
           → APT29 (117 neighbors, 117 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Password Cracking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมควบคุมระยะไกล (Remote Access Trojan) ฝังตัวในเครื่องคอมพิวเตอร์เจ้าหน้าที...
[RETRIEVE] Query: โปรแกรมควบคุมระยะไกล (Remote Access Trojan) ฝังตัวในเครื่องคอมพิวเตอร์เจ้าหน้าที...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BLINDINGCAN (0.247), FIN7 (0.118), JSS Loader (0.111), BBSRAT (0.084), HiddenWasp (0.065), Night Dragon (0.056), RemoteUtilities (0.039), Cannon (0.003), NGLite (0.002), NGLite (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BLINDINGCAN (23 neighbors, 23 edges)
           → FIN7 (86 neighbors, 86 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
           → JSS Loader (8 neighbors, 8 edges)
           → BBSRAT (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 3/8: โปรแกรมฝังตัวเรียกตัวติดตั้งรุ่นถัดไปขึ้นมาทำงานด้วยสิทธิ์ระดับระบบ...
[RETRIEVE] Query: โปรแกรมฝังตัวเรียกตัวติดตั้งรุ่นถัดไปขึ้นมาทำงานด้วยสิทธิ์ระดับระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Installer Packages (0.037), NOKKI (0.004), OldBoot (0.002), Active Setup (0.001), CrossRAT (0.001), Cobian RAT (0.001), Ptrace System Calls (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Installer Packages (8 neighbors, 8 edges)
           → NOKKI (17 neighbors, 17 edges)
           → Credential API Hooking (17 neighbors, 17 edges)
           → Active Setup (6 neighbors, 6 edges)
           → OldBoot (1 neighbors, 1 edges)
           → Boot or Logon Initialization Scripts (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 4/8: แก้ไขค่าในทะเบียนระบบ (Registry Modification) เพื่อวางการตั้งค่าของตนเอง...
[RETRIEVE] Query: แก้ไขค่าในทะเบียนระบบ (Registry Modification) เพื่อวางการตั้งค่าของตนเอง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Registry Key Modification (0.299), Modify Registry (0.047), RCSession (0.026), Reg (0.024), User Account Modification (0.002), Instance Modification (0.002), Drive Modification (0.001), Restrict Registry Permissions (0.001), AADInternals (0.000), Execution Prevention (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Windows Registry Key Modification (0 neighbors, 0 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → RCSession (24 neighbors, 24 edges)
           → Reg (12 neighbors, 12 edges)
           → User Account Modification (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 5/8: ตรวจสอบชื่อบัญชีผู้ใช้ที่กำลังทำงานอยู่ในปัจจุบัน (Account Discovery)...
[RETRIEVE] Query: ตรวจสอบชื่อบัญชีผู้ใช้ที่กำลังทำงานอยู่ในปัจจุบัน (Account Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Owner/User Discovery (0.673), Remsec (0.299), Account Discovery (0.210), HAPPYWORK (0.020), Wi-Fi Discovery (0.007), TAINTEDSCRIBE (0.001), OSInfo (0.001), System Network Connections Discovery (0.001), Process Discovery (0.001), Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Remsec (31 neighbors, 31 edges)
           → Account Discovery (18 neighbors, 18 edges)
           → HAPPYWORK (4 neighbors, 4 edges)
           → Wi-Fi Discovery (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 6/8: ดาวน์โหลดสคริปต์เข้ามาในเครื่อง...
[RETRIEVE] Query: ดาวน์โหลดสคริปต์เข้ามาในเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dvmap (0.032), PsExec (0.013), OilBooster (0.011), Get2 (0.008), BISCUIT (0.008), Visual Basic (0.002), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Dvmap (7 neighbors, 7 edges)
           → Download New Code at Runtime (42 neighbors, 42 edges)
           → PsExec (49 neighbors, 49 edges)
           → OilBooster (16 neighbors, 16 edges)
           → BISCUIT (11 neighbors, 11 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 7/8: Password Spraying ลองรหัสผ่านที่คาดเดาง่ายกับบัญชีผู้ดูแลโดเมนหลายบัญชี...
[RETRIEVE] Query: Password Spraying ลองรหัสผ่านที่คาดเดาง่ายกับบัญชีผู้ดูแลโดเมนหลายบัญชี...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Password Spraying (0.930), Multi-factor Authentication (0.049), Password Guessing (0.048), Password Policies (0.038), CrackMapExec (0.011), Domain Accounts (0.004), Password Policies (0.004), Password Policy Discovery (0.001), Password Cracking (0.001), Password Policies (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Password Spraying (23 neighbors, 23 edges)
           → Password Guessing (19 neighbors, 19 edges)
           → Multi-factor Authentication (48 neighbors, 48 edges)
           → Password Policies (47 neighbors, 47 edges)
           → Domain Accounts (47 neighbors, 47 edges)
[RETRIEVE-QUOTA] Query 8/8: พยายามเชื่อมต่อไดรฟ์ของเครื่องแม่ข่ายควบคุมโดเมน (Domain Controller)...
[RETRIEVE] Query: พยายามเชื่อมต่อไดรฟ์ของเครื่องแม่ข่ายควบคุมโดเมน (Domain Controller)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DCSync (0.024), Chimera (0.015), APT32 (0.012), Volt Typhoon (0.010), Domain Controller Authentication (0.008), Rogue Domain Controller (0.007), Command and Control (0.002), DNS (0.001), Bypass User Account Control (0.000), User Account Control (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DCSync (14 neighbors, 14 edges)
           → Chimera (65 neighbors, 65 edges)
           → Domain Controller Authentication (12 neighbors, 12 edges)
           → APT32 (93 neighbors, 93 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [25/100] retrieved=235 relevant=3 latency=15185ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 21 กุมภาพันธ์ 2565 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าตรวจพบโปรแกรมไม...
[RETRIEVE] Query: เมื่อวันที่ 21 กุมภาพันธ์ 2565 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าตรวจพบโปรแกรมไม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CLAIMLOADER (0.252), DLL (0.172), PowGoop (0.112), POWERSOURCE (0.052), POWERSOURCE (0.011), Netwalker (0.006), StrelaStealer (0.005), PowerShell (0.001), PowerShell Profile (0.000), Rundll32 (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DLL (123 neighbors, 123 edges)
           → CLAIMLOADER (12 neighbors, 12 edges)
           → PowGoop (9 neighbors, 9 edges)
           → POWERSOURCE (7 neighbors, 7 edges)
           → NTFS File Attributes (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 2/6: ไฟล์สคริปต์ PowerShell ที่ถูกอำพรางด้วยนามสกุลไฟล์ข้อมูลธรรมดา...
[RETRIEVE] Query: ไฟล์สคริปต์ PowerShell ที่ถูกอำพรางด้วยนามสกุลไฟล์ข้อมูลธรรมดา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowGoop (0.982), FIN7 (0.670), POWERSOURCE (0.398), POWERSTATS (0.030), Masquerade File Type (0.021), XSL Script Processing (0.017), PowerShell Profile (0.015), PowerShell (0.012), POWERSTATS (0.002), Disable or Remove Feature or Program (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PowGoop (9 neighbors, 9 edges)
           → Masquerading (81 neighbors, 81 edges)
           → FIN7 (86 neighbors, 86 edges)
           → Hidden Window (65 neighbors, 65 edges)
           → POWERSOURCE (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 3/6: สคริปต์ PowerShell ถอดรหัสและเรียกสคริปต์ PowerShell ชั้นที่สองขึ้นมาทำงาน...
[RETRIEVE] Query: สคริปต์ PowerShell ถอดรหัสและเรียกสคริปต์ PowerShell ชั้นที่สองขึ้นมาทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Snip3 (0.571), PowerShower (0.064), POWRUNER (0.057), PowerShell (0.045), WellMess (0.039), PowerSploit (0.016), PowerShell Profile (0.011), POWERSTATS (0.002), POWERSTATS (0.002), Disable or Remove Feature or Program (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Snip3 (21 neighbors, 21 edges)
           → PowerShell (241 neighbors, 241 edges)
           → PowerShower (15 neighbors, 15 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → WellMess (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/6: DLL Side-Loading หลอกโปรแกรมที่ถูกต้องตามลิขสิทธิ์เรียกไฟล์ของคนร้าย...
[RETRIEVE] Query: DLL Side-Loading หลอกโปรแกรมที่ถูกต้องตามลิขสิทธิ์เรียกไฟล์ของคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sidewinder (0.932), CLAIMLOADER (0.857), Javali (0.789), PAKLOG (0.540), DLL (0.459), SideCopy (0.299), BOOSTWRITE (0.094), AppCert DLLs (0.028), Print Processors (0.015), Dynamic-link Library Injection (0.004)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Sidewinder (31 neighbors, 31 edges)
           → DLL (123 neighbors, 123 edges)
           → Javali (12 neighbors, 12 edges)
           → CLAIMLOADER (12 neighbors, 12 edges)
           → PAKLOG (11 neighbors, 11 edges)
           → Code Signing (90 neighbors, 90 edges)
[RETRIEVE-QUOTA] Query 5/6: อำพรางเนื้อหาสคริปต์ PowerShell เพื่อซ่อนคำสั่งติดต่อเครื่องสั่งการ...
[RETRIEVE] Query: อำพรางเนื้อหาสคริปต์ PowerShell เพื่อซ่อนคำสั่งติดต่อเครื่องสั่งการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Empire (0.934), Command Obfuscation (0.871), Sardonic (0.858), POWERSOURCE (0.244), POWERSTATS (0.040), PowerShell (0.016), POWRUNER (0.012), PowerShell Profile (0.009), Disable or Remove Feature or Program (0.003), POWERSTATS (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Command Obfuscation (74 neighbors, 74 edges)
           → Empire (91 neighbors, 91 edges)
           → Sardonic (26 neighbors, 26 edges)
           → POWERSOURCE (7 neighbors, 7 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → PowerShell (241 neighbors, 241 edges)
[RETRIEVE-QUOTA] Query 6/6: เปลี่ยนชื่อไฟล์ DLL ให้ตรงกับชื่อไฟล์โปรแกรมที่ถูกต้อง...
[RETRIEVE] Query: เปลี่ยนชื่อไฟล์ DLL ให้ตรงกับชื่อไฟล์โปรแกรมที่ถูกต้อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sibot (0.029), Space after Filename (0.026), AppInit DLLs (0.004), Change Default File Association (0.003), DLL (0.002), AppCert DLLs (0.002), Dynamic-link Library Injection (0.001), Audit (0.001), Terminal Services DLL (0.000), Authentication Package (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Space after Filename (4 neighbors, 4 edges)
           → Sibot (20 neighbors, 20 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
           → AppInit DLLs (11 neighbors, 11 edges)
           → Change Default File Association (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [26/100] retrieved=314 relevant=3 latency=12135ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 27 ตุลาคม 2563 หน่วยงานวิจัยแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Query: เมื่อวันที่ 27 ตุลาคม 2563 หน่วยงานวิจัยแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NanHaiShu (0.073), APT32 (0.032), FIN7 (0.027), Mshta (0.001), SideCopy (0.001), Maze (0.000), Ingress Tool Transfer (0.000), Winexe (0.000), Msiexec (0.000), cmd (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → NanHaiShu (13 neighbors, 13 edges)
           → Mshta (34 neighbors, 34 edges)
           → APT32 (93 neighbors, 93 edges)
           → FIN7 (86 neighbors, 86 edges)
           → SideCopy (18 neighbors, 18 edges)
           → Visual Basic (140 neighbors, 140 edges)
[RETRIEVE-QUOTA] Query 2/7: อีเมล Phishing แนบไฟล์เอกสารอันตรายหลอกนักวิจัยเปิดไฟล์...
[RETRIEVE] Query: อีเมล Phishing แนบไฟล์เอกสารอันตรายหลอกนักวิจัยเปิดไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chaes (0.703), Molerats (0.677), Spearphishing Attachment (0.248), Spearphishing Link (0.140), Spearphishing Attachment (0.123), Phishing (0.074), VOID MANTICORE (0.013), Phishing for Information (0.007), Spearphishing Link (0.005), Kimsuky (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Chaes (28 neighbors, 28 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Molerats (22 neighbors, 22 edges)
           → Spearphishing Link (93 neighbors, 93 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/7: อีเมลปลอมแจ้งเตือนความปลอดภัยบัญชีพร้อมแนบลิงก์ร้าย...
[RETRIEVE] Query: อีเมลปลอมแจ้งเตือนความปลอดภัยบัญชีพร้อมแนบลิงก์ร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.701), Evilnum (0.099), Email Accounts (0.003), TA578 (0.003), CALENDAR (0.001), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Malicious Link (93 neighbors, 93 edges)
           → Evilnum (14 neighbors, 14 edges)
           → Email Accounts (19 neighbors, 19 edges)
           → TA578 (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 4/7: ดัดแปลงเว็บไซต์เป้าหมายให้ติดตั้งโปรแกรมลงเครื่องผู้เข้าชม...
[RETRIEVE] Query: ดัดแปลงเว็บไซต์เป้าหมายให้ติดตั้งโปรแกรมลงเครื่องผู้เข้าชม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Drive-by Target (0.010), ClickOnce (0.001), Browser Extensions (0.001), Kasidet (0.000), HTTPBrowser (0.000), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Drive-by Target (12 neighbors, 12 edges)
           → ClickOnce (7 neighbors, 7 edges)
           → Browser Extensions (15 neighbors, 15 edges)
           → Kasidet (10 neighbors, 10 edges)
           → Disable or Modify System Firewall (38 neighbors, 38 edges)
[RETRIEVE-QUOTA] Query 5/7: แจกจ่ายโปรแกรมอันตรายผ่านเว็บแบ่งปันไฟล์...
[RETRIEVE] Query: แจกจ่ายโปรแกรมอันตรายผ่านเว็บแบ่งปันไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AshTag (0.922), Taint Shared Content (0.791), Chameleon (0.584), StreamEx (0.107), EvilGrab (0.039), CrossRAT (0.002), Cobian RAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Taint Shared Content (18 neighbors, 18 edges)
           → AshTag (20 neighbors, 20 edges)
           → Web Service (56 neighbors, 56 edges)
           → Chameleon (26 neighbors, 26 edges)
           → Phishing (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 6/7: หลอกติดตั้งส่วนขยายโปรแกรมท่องเว็บที่คนร้ายสร้างขึ้น...
[RETRIEVE] Query: หลอกติดตั้งส่วนขยายโปรแกรมท่องเว็บที่คนร้ายสร้างขึ้น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bundlore (0.230), TRANSLATEXT (0.059), Browser Extensions (0.039), SimBad (0.020), Dok (0.019), httpclient (0.004), CrossRAT (0.001), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bundlore (23 neighbors, 23 edges)
           → Browser Extensions (15 neighbors, 15 edges)
           → TRANSLATEXT (16 neighbors, 16 edges)
           → SimBad (4 neighbors, 4 edges)
           → Generate Traffic from Victim (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 7/7: mshta.exe ดาวน์โหลดและรันไฟล์แอปพลิเคชันเอชทีเอ็มแอลจากเครื่องปลายทางภายนอก...
[RETRIEVE] Query: mshta.exe ดาวน์โหลดและรันไฟล์แอปพลิเคชันเอชทีเอ็มแอลจากเครื่องปลายทางภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BabyShark (0.962), Pteranodon (0.858), Mshta (0.415), APT32 (0.121), NanHaiShu (0.117), Mavinject (0.005), Msiexec (0.002), CMSTP (0.002), xCmd (0.001), Winexe (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BabyShark (17 neighbors, 17 edges)
           → Mshta (34 neighbors, 34 edges)
           → Pteranodon (18 neighbors, 18 edges)
           → APT32 (93 neighbors, 93 edges)
           → NanHaiShu (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [27/100] retrieved=355 relevant=4 latency=12750ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 12 กรกฎาคม 2565 บริษัทรับจ้างผลิตแห่งหนึ่งในจังหวัดสมุทรสาครแจ้งความ...
[RETRIEVE] Query: เมื่อวันที่ 12 กรกฎาคม 2565 บริษัทรับจ้างผลิตแห่งหนึ่งในจังหวัดสมุทรสาครแจ้งความ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Daggerfly (0.084), C0021 (0.067), Netwalker (0.067), POWERSTATS (0.032), POWERSTATS (0.010), POWERSOURCE (0.009), PowerShell Profile (0.000), PowerShell (0.000), ServHelper (0.000), Disable or Remove Feature or Program (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Daggerfly (23 neighbors, 23 edges)
           → PowerShell (241 neighbors, 241 edges)
           → C0021 (16 neighbors, 16 edges)
           → Netwalker (18 neighbors, 18 edges)
           → POWERSTATS (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 2/7: เข้าถึงเครื่องแม่ข่ายผ่านบริการ Remote Desktop Protocol ที่ตั้งค่าไม่รัดกุมและเป...
[RETRIEVE] Query: เข้าถึงเครื่องแม่ข่ายผ่านบริการ Remote Desktop Protocol ที่ตั้งค่าไม่รัดกุมและเป...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Limit Access to Resource Over Network (0.140), RDP Hijacking (0.104), Remote Desktop Protocol (0.079), Koadic (0.063), Terminal Services DLL (0.034), Axiom (0.026), Remote Access Tools (0.025), Limit Access to Resource Over Network (0.005), Remote Access Hardware (0.005), Remote Services (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Koadic (31 neighbors, 31 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 3/7: ใช้รหัสผ่านที่คาดเดาได้เพื่อเข้าสู่ระบบ Remote Desktop...
[RETRIEVE] Query: ใช้รหัสผ่านที่คาดเดาได้เพื่อเข้าสู่ระบบ Remote Desktop...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Threat Group-1314 (0.118), Password Guessing (0.105), RDP Hijacking (0.056), Remote Desktop Protocol (0.033), Aquatic Panda (0.014), Koadic (0.002), Remote Services (0.002), Blue Mockingbird (0.001), Terminal Services DLL (0.001), Remote Access Tools (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Password Guessing (19 neighbors, 19 edges)
           → Threat Group-1314 (6 neighbors, 6 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Aquatic Panda (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] Query 4/7: ส่งอีเมลหลอกลวงและอีเมลขยะพร้อมไฟล์แนบโปรแกรมเรียกค่าไถ่ให้พนักงาน...
[RETRIEVE] Query: ส่งอีเมลหลอกลวงและอีเมลขยะพร้อมไฟล์แนบโปรแกรมเรียกค่าไถ่ให้พนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: menuPass (0.516), FIN7 (0.378), Lumma Stealer (0.229), Spearphishing Attachment (0.128), Squirrelwaffle (0.125), Squirrelwaffle (0.019), Email Accounts (0.003), Financial Theft (0.003), EvilGrab (0.003), Email Bombing (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → menuPass (71 neighbors, 71 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → FIN7 (86 neighbors, 86 edges)
           → Lumma Stealer (35 neighbors, 35 edges)
           → Squirrelwaffle (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 5/7: ใช้ไฟล์แบตช์เรียกสคริปต์ PowerShell ขึ้นมาทำงาน...
[RETRIEVE] Query: ใช้ไฟล์แบตช์เรียกสคริปต์ PowerShell ขึ้นมาทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Invoke-PSImage (0.032), PowerShell (0.019), PowerPunch (0.009), PowerShell Profile (0.007), POWRUNER (0.004), PowerShower (0.001), BONDUPDATER (0.001), POWERSTATS (0.001), POWERSTATS (0.000), Disable or Remove Feature or Program (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Invoke-PSImage (3 neighbors, 3 edges)
           → PowerShell (241 neighbors, 241 edges)
           → PowerPunch (5 neighbors, 5 edges)
           → PowerShell Profile (9 neighbors, 9 edges)
           → POWRUNER (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 6/7: โหลดโปรแกรมเรียกค่าไถ่เข้าไปทำงานในหน่วยความจำของเครื่องโดยไม่เขียนไฟล์ลงดิสก์...
[RETRIEVE] Query: โหลดโปรแกรมเรียกค่าไถ่เข้าไปทำงานในหน่วยความจำของเครื่องโดยไม่เขียนไฟล์ลงดิสก์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Deep Panda (0.842), Netwalker (0.815), ThiefQuest (0.484), Portable Executable Injection (0.051), Proc Memory (0.050), Extra Window Memory Injection (0.003), CrossRAT (0.002), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Deep Panda (17 neighbors, 17 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Netwalker (18 neighbors, 18 edges)
           → ThiefQuest (18 neighbors, 18 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 7/7: เข้ารหัสลับไฟล์งานในเครื่องแม่ข่ายและแสดงข้อความเรียกค่าไถ่...
[RETRIEVE] Query: เข้ารหัสลับไฟล์งานในเครื่องแม่ข่ายและแสดงข้อความเรียกค่าไถ่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: REvil (0.219), ShrinkLocker (0.190), Maze (0.155), Black Basta (0.069), Encrypted/Encoded File (0.051), Medusa Ransomware (0.019), Deobfuscate/Decode Files or Information (0.014), ThiefQuest (0.005), POWERSOURCE (0.003), FIN6 (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → REvil (37 neighbors, 37 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → ShrinkLocker (21 neighbors, 21 edges)
           → Maze (25 neighbors, 25 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [28/100] retrieved=344 relevant=3 latency=13630ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 13 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบยูนิกซ์...
[RETRIEVE] Query: เมื่อวันที่ 13 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบยูนิกซ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Indrik Spider (0.016), PlugX (0.013), Unsecured Credentials (0.002), Ingress Tool Transfer (0.001), OS Credential Dumping (0.000), Valid Accounts (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), Clear Linux or Mac System Logs (0.000), Clear Windows Event Logs (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Indrik Spider (41 neighbors, 41 edges)
           → Credentials In Files (44 neighbors, 44 edges)
           → PlugX (65 neighbors, 65 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Unsecured Credentials (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] Query 2/8: Remote Code Execution บนเครื่องแม่ข่ายระบบยูนิกซ์ผ่านคำสั่งระบบจำนวนมาก...
[RETRIEVE] Query: Remote Code Execution บนเครื่องแม่ข่ายระบบยูนิกซ์ผ่านคำสั่งระบบจำนวนมาก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.235), Execution (0.102), RemoteCMD (0.081), RemoteCMD (0.054), Ke3chang (0.051), Exploitation of Remote Services (0.026), APT28 (0.026), Command and Scripting Interpreter (0.013), Dynamic-link Library Injection (0.001), Code Signing (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Execution (64 neighbors, 64 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Ke3chang (58 neighbors, 58 edges)
[RETRIEVE-QUOTA] Query 3/8: การอ่านไฟล์รายชื่อบัญชีผู้ใช้ (passwd file) บนระบบยูนิกซ์...
[RETRIEVE] Query: การอ่านไฟล์รายชื่อบัญชีผู้ใช้ (passwd file) บนระบบยูนิกซ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: /etc/passwd and /etc/shadow (0.569), P.A.S. Webshell (0.132), LaZagne (0.010), Empire (0.009), Password Policies (0.006), Unsecured Credentials (0.005), Password Policy Discovery (0.001), Group Policy Preferences (0.000), Mark-of-the-Web Bypass (0.000), Compiled HTML File (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → /etc/passwd and /etc/shadow (7 neighbors, 7 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Local Account (69 neighbors, 69 edges)
           → LaZagne (22 neighbors, 22 edges)
           → Empire (91 neighbors, 91 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 4/8: การอ่านไฟล์รหัสผ่านของระบบ (shadow file) บนระบบยูนิกซ์...
[RETRIEVE] Query: การอ่านไฟล์รหัสผ่านของระบบ (shadow file) บนระบบยูนิกซ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: /etc/passwd and /etc/shadow (0.834), LaZagne (0.157), cd00r (0.006), Obfuscated Files or Information (0.005), Hidden File System (0.003), Execution Prevention (0.001), Login Hook (0.001), Group Policy Preferences (0.000), Nightdoor (0.000), Rogue Domain Controller (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → /etc/passwd and /etc/shadow (7 neighbors, 7 edges)
           → LaZagne (22 neighbors, 22 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → cd00r (4 neighbors, 4 edges)
           → Hidden File System (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 5/8: การเปลี่ยนสิทธิ์การเข้าถึงไฟล์ในโฟลเดอร์ไฟล์ชั่วคราว (/tmp)...
[RETRIEVE] Query: การเปลี่ยนสิทธิ์การเข้าถึงไฟล์ในโฟลเดอร์ไฟล์ชั่วคราว (/tmp)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File and Directory Permissions Modification (0.025), Timestomp (0.021), Restrict File and Directory Permissions (0.004), Empire (0.001), Terminal Services DLL (0.001), Cobalt Strike (0.000), cmd (0.000), pwdump (0.000), cmd (0.000), Cachedump (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → File and Directory Permissions Modification (6 neighbors, 6 edges)
           → Timestomp (60 neighbors, 60 edges)
           → Restrict File and Directory Permissions (60 neighbors, 60 edges)
           → Empire (91 neighbors, 91 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 6/8: การเข้ารหัสคำสั่งและผลลัพธ์ด้วยกุญแจลับเพื่อหลีกเลี่ยงการตรวจจับ...
[RETRIEVE] Query: การเข้ารหัสคำสั่งและผลลัพธ์ด้วยกุญแจลับเพื่อหลีกเลี่ยงการตรวจจับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Encrypted Channel (0.382), Data Obfuscation (0.209), Obfuscated Files or Information (0.148), Encrypt Sensitive Information (0.135), Data Encoding (0.049), Encrypt Sensitive Information (0.036), Encrypted/Encoded File (0.022), InvisiMole (0.010), Archive Collected Data (0.006), Forfiles (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Encrypted Channel (23 neighbors, 23 edges)
           → Data Obfuscation (21 neighbors, 21 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Encrypt Sensitive Information (33 neighbors, 33 edges)
           → Indicator Removal (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] Query 7/8: ดาวน์โหลดและติดตั้งโปรแกรม reverse shell เพื่อคงการเข้าถึงเครื่อง...
[RETRIEVE] Query: ดาวน์โหลดและติดตั้งโปรแกรม reverse shell เพื่อคงการเข้าถึงเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: KOMPROGO (0.061), PHOREAL (0.060), SUGARUSH (0.054), Chaos (0.048), Kessel (0.035), TDTESS (0.026), SnappyTCP (0.014), REPTILE (0.010), ZxShell (0.003), RAPIDPULSE (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → KOMPROGO (4 neighbors, 4 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → PHOREAL (4 neighbors, 4 edges)
           → SUGARUSH (7 neighbors, 7 edges)
           → Chaos (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 8/8: การสร้างช่องทางส่งต่อการเชื่อมต่อแบบย้อนกลับเข้าถึงเครือข่ายภายในจากภายนอก...
[RETRIEVE] Query: การสร้างช่องทางส่งต่อการเชื่อมต่อแบบย้อนกลับเข้าถึงเครือข่ายภายในจากภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Network Segmentation (0.029), Sandworm Team (0.012), Bidirectional Communication (0.009), Internal Proxy (0.007), Cobian RAT (0.001), CrossRAT (0.000), Visual Basic (0.000), 4H RAT (0.000), The White Company (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Network Segmentation (37 neighbors, 37 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → Sandworm Team (113 neighbors, 113 edges)
           → Proxy (84 neighbors, 84 edges)
           → Bidirectional Communication (61 neighbors, 61 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [29/100] retrieved=668 relevant=5 latency=15129ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 4 สิงหาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความว่าฐานข้อมูลสำรองของระบ...
[RETRIEVE] Query: เมื่อวันที่ 4 สิงหาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความว่าฐานข้อมูลสำรองของระบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.003), File Deletion (0.002), FIN8 (0.000), RAPIDPULSE (0.000), POWERSOURCE (0.000), 4H RAT (0.000), KernelCallbackTable (0.000), Network Boundary Bridging (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Local Email Collection (25 neighbors, 25 edges)
           → File Deletion (310 neighbors, 310 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/7: รันคำสั่ง dir/ls ไล่สำรวจรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่าย...
[RETRIEVE] Query: รันคำสั่ง dir/ls ไล่สำรวจรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Rclone (0.069), File and Directory Discovery (0.028), Forfiles (0.024), Fysbis (0.011), Denis (0.009), dsquery (0.007), Network Share Discovery (0.002), Cutting Edge (0.001), SSL/TLS Inspection (0.000), Hidden Files and Directories (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Rclone (16 neighbors, 16 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → Forfiles (4 neighbors, 4 edges)
           → Fysbis (13 neighbors, 13 edges)
           → System Information Discovery (426 neighbors, 426 edges)
[RETRIEVE-QUOTA] Query 3/7: สร้างโฟลเดอร์ใหม่สำหรับพักข้อมูลที่รวบรวมได้...
[RETRIEVE] Query: สร้างโฟลเดอร์ใหม่สำหรับพักข้อมูลที่รวบรวมได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Carbon (0.079), Local Data Staging (0.011), Cloud Storage Creation (0.010), Data Staged (0.008), Container Creation (0.006), SombRAT (0.006), Remote Data Staging (0.002), InvisiMole (0.001), Archive via Library (0.001), Forfiles (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Carbon (19 neighbors, 19 edges)
           → Local Data Staging (138 neighbors, 138 edges)
           → Cloud Storage Creation (0 neighbors, 0 edges)
           → Data Staged (13 neighbors, 13 edges)
           → Container Creation (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 4/7: อ่านไฟล์ฐานข้อมูลสำรองออกเป็นชิ้นเล็ก ๆ...
[RETRIEVE] Query: อ่านไฟล์ฐานข้อมูลสำรองออกเป็นชิ้นเล็ก ๆ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Security Account Manager (0.001), SNMP (MIB Dump) (0.001), Credentials In Files (0.001), Pod Enumeration (0.000), SLIGHTPULSE (0.000), LoFiSe (0.000), PAKLOG (0.000), TAINTEDSCRIBE (0.000), Cachedump (0.000), Local Email Collection (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Security Account Manager (43 neighbors, 43 edges)
           → SNMP (MIB Dump) (9 neighbors, 9 edges)
           → Credentials In Files (44 neighbors, 44 edges)
           → Pod Enumeration (0 neighbors, 0 edges)
           → SLIGHTPULSE (10 neighbors, 10 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 5/7: ส่งข้อมูลฐานข้อมูลสำรองออกไปยังบัญชีจดหมายอิเล็กทรอนิกส์ของคนร้ายผ่านบริการอีเมล...
[RETRIEVE] Query: ส่งข้อมูลฐานข้อมูลสำรองออกไปยังบัญชีจดหมายอิเล็กทรอนิกส์ของคนร้ายผ่านบริการอีเมล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Email Addresses (0.005), Email Accounts (0.003), Email Collection (0.002), VOID MANTICORE (0.002), VOID MANTICORE (0.002), Email Accounts (0.002), Clear Mailbox Data (0.001), Indrik Spider (0.001), Storm-1811 (0.001), Email Bombing (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Email Addresses (20 neighbors, 20 edges)
           → Email Accounts (30 neighbors, 30 edges)
           → Email Collection (15 neighbors, 15 edges)
           → Email Accounts (19 neighbors, 19 edges)
           → Clear Mailbox Data (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 6/7: ลบไฟล์เครื่องมือที่นำเข้ามาออกจากเครื่อง...
[RETRIEVE] Query: ลบไฟล์เครื่องมือที่นำเข้ามาออกจากเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File Deletion (0.272), Cuba (0.065), Ixeshe (0.056), Indicator Removal from Tools (0.027), SDelete (0.015), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → Cuba (23 neighbors, 23 edges)
           → Ixeshe (16 neighbors, 16 edges)
           → Indicator Removal from Tools (20 neighbors, 20 edges)
           → SDelete (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 7/7: ลบตัวโปรแกรมฝังตัวของคนร้ายทิ้ง...
[RETRIEVE] Query: ลบตัวโปรแกรมฝังตัวของคนร้ายทิ้ง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Disable or Remove Feature or Program (0.009), FunnyDream (0.004), DarkWatchman (0.003), Inhibit System Recovery (0.001), Netwalker (0.001), pngdowner (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → FunnyDream (38 neighbors, 38 edges)
           → Indicator Removal (45 neighbors, 45 edges)
           → DarkWatchman (34 neighbors, 34 edges)
           → Inhibit System Recovery (62 neighbors, 62 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [30/100] retrieved=618 relevant=3 latency=13680ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 16 กันยายน 2567 บริษัทนำเข้าส่งออกแห่งหนึ่งแจ้งความว่าบัญชีผู้ใช้งาน...
[RETRIEVE] Query: เมื่อวันที่ 16 กันยายน 2567 บริษัทนำเข้าส่งออกแห่งหนึ่งแจ้งความว่าบัญชีผู้ใช้งาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.010), POWRUNER (0.003), Password Managers (0.001), FIN8 (0.001), Unsecured Credentials (0.000), Reversible Encryption (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Credentials in Registry (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Keylogging (160 neighbors, 160 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Password Managers (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 2/8: การสวมรอยบัญชีผู้ใช้งานระบบภายในบริษัท...
[RETRIEVE] Query: การสวมรอยบัญชีผู้ใช้งานระบบภายในบริษัท...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Internal Spearphishing (0.767), Dragonfly (0.040), Credential Stuffing (0.007), Masquerade Account Name (0.004), Hybrid Identity (0.002), Compromise Accounts (0.002), SystemBC (0.002), Bankshot (0.001), DUSTTRAP (0.000), Employee Names (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Internal Spearphishing (10 neighbors, 10 edges)
           → Dragonfly (66 neighbors, 66 edges)
           → Masquerade Account Name (11 neighbors, 11 edges)
           → Credential Stuffing (10 neighbors, 10 edges)
           → Hybrid Identity (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 3/8: โปรแกรมอ่านคลังเก็บรหัสผ่านของระบบปฏิบัติการวินโดวส์...
[RETRIEVE] Query: โปรแกรมอ่านคลังเก็บรหัสผ่านของระบบปฏิบัติการวินโดวส์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: gsecdump (0.811), Mimikatz (0.707), LaZagne (0.551), Windows Credential Manager (0.084), PoshC2 (0.060), Cobian RAT (0.013), CrossRAT (0.010), Cardinal RAT (0.006), Visual Basic (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → gsecdump (8 neighbors, 8 edges)
           → Mimikatz (77 neighbors, 77 edges)
           → LaZagne (22 neighbors, 22 edges)
           → Windows Credential Manager (18 neighbors, 18 edges)
           → PoshC2 (35 neighbors, 35 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 4/8: ขโมยชื่อผู้ใช้และรหัสผ่านจากโปรแกรมท่องเว็บ...
[RETRIEVE] Query: ขโมยชื่อผู้ใช้และรหัสผ่านจากโปรแกรมท่องเว็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Unknown Logger (0.846), MgBot (0.715), APT37 (0.488), Net Crawler (0.413), njRAT (0.388), WARPWIRE (0.242), OwaAuth (0.213), DRYHOOK (0.081), Mimikatz (0.021), gsecdump (0.016)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Unknown Logger (9 neighbors, 9 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → MgBot (18 neighbors, 18 edges)
           → APT37 (42 neighbors, 42 edges)
           → njRAT (40 neighbors, 40 edges)
[RETRIEVE-QUOTA] Query 5/8: เขียนข้อมูลรหัสผ่านลงเป็นไฟล์ฐานข้อมูลบนเครื่อง...
[RETRIEVE] Query: เขียนข้อมูลรหัสผ่านลงเป็นไฟล์ฐานข้อมูลบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OwaAuth (0.046), Security Account Manager (0.039), Password Managers (0.029), Credentials In Files (0.025), TYPEFRAME (0.004), Credentials from Password Stores (0.001), Visual Basic (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Security Account Manager (43 neighbors, 43 edges)
           → OwaAuth (8 neighbors, 8 edges)
           → Keylogging (160 neighbors, 160 edges)
           → Password Managers (20 neighbors, 20 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 6/8: ส่งไฟล์ฐานข้อมูลรหัสผ่านออกไปยังเครื่องสั่งการภายนอก...
[RETRIEVE] Query: ส่งไฟล์ฐานข้อมูลรหัสผ่านออกไปยังเครื่องสั่งการภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.033), Exfiltration Over Alternative Protocol (0.013), cmd (0.011), XCSSET (0.007), RemoteCMD (0.005), SSH (0.004), Password Managers (0.004), Private Keys (0.002), Out1 (0.001), Mafalda (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → XCSSET (33 neighbors, 33 edges)
           → SSH Authorized Keys (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 7/8: โปรแกรมฝังตัวติดต่อรับคำสั่งจากเครื่องสั่งการภายนอก...
[RETRIEVE] Query: โปรแกรมฝังตัวติดต่อรับคำสั่งจากเครื่องสั่งการภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cobian RAT (0.026), Bumblebee (0.012), CrossRAT (0.007), Woody RAT (0.003), Credential API Hooking (0.002), Portable Executable Injection (0.001), Ptrace System Calls (0.001), Visual Basic (0.001), Proc Memory (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Cobian RAT (8 neighbors, 8 edges)
           → Bumblebee (41 neighbors, 41 edges)
           → Asynchronous Procedure Call (18 neighbors, 18 edges)
           → CrossRAT (6 neighbors, 6 edges)
           → Woody RAT (30 neighbors, 30 edges)
           → Process Injection (104 neighbors, 104 edges)
[RETRIEVE-QUOTA] Query 8/8: ดาวน์โหลดไฟล์ชุดคำสั่งเพิ่มเติมจากเครื่องภายนอก...
[RETRIEVE] Query: ดาวน์โหลดไฟล์ชุดคำสั่งเพิ่มเติมจากเครื่องภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Seasalt (0.184), cmd (0.111), xCmd (0.012), Pupy (0.011), RemoteCMD (0.011), Exfiltration Over Alternative Protocol (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Seasalt (11 neighbors, 11 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → cmd (13 neighbors, 13 edges)
           → xCmd (2 neighbors, 2 edges)
           → Pupy (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [31/100] retrieved=432 relevant=3 latency=16075ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 14 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ได้รับอีเมลต้...
[RETRIEVE] Query: เมื่อวันที่ 14 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ได้รับอีเมลต้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Frankenstein (0.210), BlackTech (0.051), Covenant (0.010), Windows Command Shell (0.007), EvilGrab (0.005), cmd (0.005), XLoader (0.003), Masquerade File Type (0.002), Chaos (0.001), Command and Scripting Interpreter (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Frankenstein (28 neighbors, 28 edges)
           → Malicious File (202 neighbors, 202 edges)
           → BlackTech (20 neighbors, 20 edges)
           → Covenant (11 neighbors, 11 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 2/7: อีเมล Phishing พร้อมไฟล์แนบเอกสารเวิร์ดที่มีมาโครอันตรายหลอกลวงพนักงาน...
[RETRIEVE] Query: อีเมล Phishing พร้อมไฟล์แนบเอกสารเวิร์ดที่มีมาโครอันตรายหลอกลวงพนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Molerats (0.872), BLINDINGCAN (0.825), Spearphishing Attachment (0.462), Spearphishing Link (0.215), Phishing (0.160), Spearphishing Attachment (0.052), VOID MANTICORE (0.007), Phishing for Information (0.004), Spearphishing Link (0.003), Kimsuky (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Molerats (22 neighbors, 22 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → BLINDINGCAN (23 neighbors, 23 edges)
           → Spearphishing Link (93 neighbors, 93 edges)
           → Phishing (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 3/7: มาโครอันตรายเปลี่ยนสีตัวอักษรในเอกสารเพื่อหลอกให้ผู้ใช้อนุญาตให้เนื้อหาทำงาน...
[RETRIEVE] Query: มาโครอันตรายเปลี่ยนสีตัวอักษรในเอกสารเพื่อหลอกให้ผู้ใช้อนุญาตให้เนื้อหาทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operation Honeybee (0.214), C0015 (0.158), Hancitor (0.124), Dark Caracal (0.025), Masquerading (0.018), Template Injection (0.016), Malicious File (0.008), Masquerade File Type (0.007), Malicious Copy and Paste (0.002), Modify or Spoof Tool UI (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Operation Honeybee (33 neighbors, 33 edges)
           → Malicious File (202 neighbors, 202 edges)
           → C0015 (39 neighbors, 39 edges)
           → Hancitor (14 neighbors, 14 edges)
           → Dark Caracal (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 4/7: ตรวจสอบสถาปัตยกรรมระบบปฏิบัติการ (32-bit หรือ 64-bit)...
[RETRIEVE] Query: ตรวจสอบสถาปัตยกรรมระบบปฏิบัติการ (32-bit หรือ 64-bit)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gelsemium (0.980), Kerrdown (0.974), FinFisher (0.955), RotaJakiro (0.081), TDTESS (0.017), Koadic (0.015), Screensaver (0.001), APT32 (0.001), ccf32 (0.001), APT32 (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Gelsemium (33 neighbors, 33 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Kerrdown (12 neighbors, 12 edges)
           → FinFisher (28 neighbors, 28 edges)
           → RotaJakiro (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 5/7: ประกอบบรรทัดคำสั่งและสั่งงานผ่าน Windows Command Shell...
[RETRIEVE] Query: ประกอบบรรทัดคำสั่งและสั่งงานผ่าน Windows Command Shell...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Covenant (0.584), cmd (0.328), Windows Command Shell (0.276), KEYMARBLE (0.087), cmd (0.031), PowerShell (0.031), Indirect Command Execution (0.014), Command and Scripting Interpreter (0.013), Unix Shell (0.004), Shell History (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Covenant (11 neighbors, 11 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → cmd (13 neighbors, 13 edges)
           → KEYMARBLE (12 neighbors, 12 edges)
           → PowerShell (241 neighbors, 241 edges)
[RETRIEVE-QUOTA] Query 6/7: ดาวน์โหลดไฟล์เพิ่มเติมเข้ามาในเครื่องผ่าน Command Shell...
[RETRIEVE] Query: ดาวน์โหลดไฟล์เพิ่มเติมเข้ามาในเครื่องผ่าน Command Shell...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lucifer (0.558), Seasalt (0.304), Windows Command Shell (0.016), cmd (0.014), cmd (0.014), Command and Scripting Interpreter (0.004), SUGARUSH (0.001), Shell History (0.001), dsquery (0.001), Container Administration Command (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Lucifer (24 neighbors, 24 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Seasalt (11 neighbors, 11 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งข้อมูลที่รวบรวมออกไปทางโพรโทคอลรับส่งไฟล์ธรรมดาที่ไม่เข้ารหัสลับ (exfiltratio...
[RETRIEVE] Query: ส่งข้อมูลที่รวบรวมออกไปทางโพรโทคอลรับส่งไฟล์ธรรมดาที่ไม่เข้ารหัสลับ (exfiltratio...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ftp (0.839), Exfiltration Over Unencrypted Non-C2 Protocol (0.806), Dok (0.695), Exfiltration Over Alternative Protocol (0.593), Exfiltration Over C2 Channel (0.219), Exfiltration (0.170), Exfiltration Over Other Network Medium (0.039), Exfiltration Over Physical Medium (0.030), Empire (0.015), APT28 Nearest Neighbor Campaign (0.009)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
           → ftp (10 neighbors, 10 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → Dok (11 neighbors, 11 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [32/100] retrieved=556 relevant=3 latency=14212ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 30 พฤศจิกายน 2566 บริษัทผู้ให้บริการด้านเทคโนโลยีสารสนเทศแห่งหนึ่งแจ...
[RETRIEVE] Query: เมื่อวันที่ 30 พฤศจิกายน 2566 บริษัทผู้ให้บริการด้านเทคโนโลยีสารสนเทศแห่งหนึ่งแจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.436), pwdump (0.279), OS Credential Dumping (0.259), Windows Credential Editor (0.210), BlackByte (0.189), Sowbug (0.175), Suckfly (0.157), Credentials In Files (0.002), Credential Access (0.002), Credential Access Protection (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → pwdump (7 neighbors, 7 edges)
           → BlackByte (56 neighbors, 56 edges)
           → Sowbug (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 2/7: Credential Dumping ดึงรหัสผ่านจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่องปลาย...
[RETRIEVE] Query: Credential Dumping ดึงรหัสผ่านจากหน่วยความจำของกระบวนการยืนยันตัวตนบนเครื่องปลาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MgBot (0.830), OS Credential Dumping (0.640), gsecdump (0.359), pwdump (0.320), Credentials In Files (0.233), pwdump (0.178), Credential Access (0.129), Windows Credential Editor (0.103), Axiom (0.092), Credential Access Protection (0.062)
[RETRIEVE] Graph expansion: 5 subgraphs
           → MgBot (18 neighbors, 18 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → pwdump (7 neighbors, 7 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → gsecdump (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/7: Credential Dumping จากระยะไกลดึงข้อมูลการยืนยันตัวตนจากเครื่องอื่นในเครือข่าย...
[RETRIEVE] Query: Credential Dumping จากระยะไกลดึงข้อมูลการยืนยันตัวตนจากเครื่องอื่นในเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HOMEFRY (0.455), OS Credential Dumping (0.328), Poseidon Group (0.285), Axiom (0.227), Credential Stuffing (0.135), Credential Access (0.121), Credentials In Files (0.091), Credential Access Protection (0.084), Windows Credential Editor (0.069), IceApple (0.029)
[RETRIEVE] Graph expansion: 5 subgraphs
           → HOMEFRY (4 neighbors, 4 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Poseidon Group (8 neighbors, 8 edges)
           → Axiom (24 neighbors, 24 edges)
           → Credential Stuffing (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 4/7: สร้างบริการของระบบบนเครื่องปลายทางเพื่อสั่งรันคำสั่งจากระยะไกล...
[RETRIEVE] Query: สร้างบริการของระบบบนเครื่องปลายทางเพื่อสั่งรันคำสั่งจากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.812), RemoteCMD (0.236), RemoteCMD (0.123), CrackMapExec (0.087), Emissary (0.056), Terminal Services DLL (0.041), xCmd (0.027), Container Administration Command (0.016), Create or Modify System Process (0.008), Service Execution (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → At (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 5/7: รวบรวมไฟล์ข้อมูลลูกค้าและบีบอัดเป็นไฟล์เดียว...
[RETRIEVE] Query: รวบรวมไฟล์ข้อมูลลูกค้าและบีบอัดเป็นไฟล์เดียว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Staged (0.064), PUNCHTRACK (0.011), Remote Data Staging (0.008), spwebmember (0.005), SampleCheck5000 (0.003), Customer Relationship Management Software (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Data Staged (13 neighbors, 13 edges)
           → PUNCHTRACK (4 neighbors, 4 edges)
           → Local Data Staging (138 neighbors, 138 edges)
           → Remote Data Staging (17 neighbors, 17 edges)
           → spwebmember (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 6/7: ซ่อนไฟล์ข้อมูลที่บีบอัดแล้วในถังขยะของเครื่องเพื่อหลีกเลี่ยงการตรวจสอบ...
[RETRIEVE] Query: ซ่อนไฟล์ข้อมูลที่บีบอัดแล้วในถังขยะของเครื่องเพื่อหลีกเลี่ยงการตรวจสอบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Obfuscated Files or Information (0.057), Encrypt Sensitive Information (0.004), COATHANGER (0.003), Embedded Payloads (0.003), Compression (0.002), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Encrypt Sensitive Information (33 neighbors, 33 edges)
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Embedded Payloads (27 neighbors, 27 edges)
           → Compression (38 neighbors, 38 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งไฟล์ข้อมูลลูกค้าออกไปภายนอก...
[RETRIEVE] Query: ส่งไฟล์ข้อมูลลูกค้าออกไปภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Transfer Data to Cloud Account (0.167), ftp (0.029), cmd (0.015), PUBLOAD (0.013), Exfiltration Over Alternative Protocol (0.009), SpyDealer (0.008), BusyGasper (0.006), Email Forwarding Rule (0.003), Customer Relationship Management Software (0.002), Clear Mailbox Data (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Transfer Data to Cloud Account (9 neighbors, 9 edges)
           → ftp (10 neighbors, 10 edges)
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → PUBLOAD (36 neighbors, 36 edges)
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [33/100] retrieved=163 relevant=4 latency=15148ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 8 ธันวาคม 2566 บริษัทที่ปรึกษาแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใ...
[RETRIEVE] Query: เมื่อวันที่ 8 ธันวาคม 2566 บริษัทที่ปรึกษาแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ShadowPad (0.006), APT-C-36 (0.002), POWRUNER (0.001), APT-C-36 (0.000), Account Discovery (0.000), Domains (0.000), Ursnif (0.000), System Network Connections Discovery (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → ShadowPad (31 neighbors, 31 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Groups (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] Query 2/8: ผลักไฟล์เครื่องมือของคนร้ายเข้าไปเก็บไว้บนเครื่องที่ยึดครองได้...
[RETRIEVE] Query: ผลักไฟล์เครื่องมือของคนร้ายเข้าไปเก็บไว้บนเครื่องที่ยึดครองได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lateral Tool Transfer (0.138), Ingress Tool Transfer (0.105), TrickBot (0.084), QuasarRAT (0.024), TONESHELL (0.015), Replication Through Removable Media (0.007), Data from Removable Media (0.007), File Deletion (0.005), Input Injection (0.004), Communication Through Removable Media (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → TrickBot (57 neighbors, 57 edges)
           → QuasarRAT (32 neighbors, 32 edges)
           → TONESHELL (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 3/8: สั่งแสดงรายการโฟลเดอร์ที่เปิดแบ่งปันไว้บนเครือข่ายภายใน...
[RETRIEVE] Query: สั่งแสดงรายการโฟลเดอร์ที่เปิดแบ่งปันไว้บนเครือข่ายภายใน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.281), Net (0.114), Pupy (0.061), Diavol (0.059), Network Share Discovery (0.014), Network Share Access (0.010), SMB/Windows Admin Shares (0.002), Shared Modules (0.001), Change Default File Association (0.000), Distributed Component Object Model (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
           → Net (50 neighbors, 50 edges)
           → Pupy (43 neighbors, 43 edges)
           → Diavol (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 4/8: ไล่ค้นหารายชื่อเครื่องอื่น ๆ ที่อยู่ในวงเครือข่ายเดียวกัน...
[RETRIEVE] Query: ไล่ค้นหารายชื่อเครื่องอื่น ๆ ที่อยู่ในวงเครือข่ายเดียวกัน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote System Discovery (0.131), System Network Connections Discovery (0.028), CrossRAT (0.011), Deep Panda (0.010), APT3 (0.009), Cobian RAT (0.006), Network Share Discovery (0.006), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Remote System Discovery (104 neighbors, 104 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → Deep Panda (17 neighbors, 17 edges)
           → APT3 (50 neighbors, 50 edges)
           → CrossRAT (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 5/8: ใช้คำสั่งพื้นฐานของระบบและสคริปต์เพื่อสำรวจเครือข่าย...
[RETRIEVE] Query: ใช้คำสั่งพื้นฐานของระบบและสคริปต์เพื่อสำรวจเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Net (0.696), Scattered Spider (0.507), Epic (0.494), Net (0.059), Net (0.038), System Network Connections Discovery (0.023), CrackMapExec (0.017), Process Discovery (0.015), Ping (0.011), File and Directory Discovery (0.007)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Net (50 neighbors, 50 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → Scattered Spider (76 neighbors, 76 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → Epic (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 6/8: ตรวจสอบพอร์ตบริการที่เปิดไว้บนเครื่องปลายทางแต่ละเครื่อง...
[RETRIEVE] Query: ตรวจสอบพอร์ตบริการที่เปิดไว้บนเครื่องปลายทางแต่ละเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BADHATCH (0.417), Koadic (0.366), Response Metadata (0.067), netstat (0.046), Port Monitors (0.003), Port Knocking (0.002), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BADHATCH (36 neighbors, 36 edges)
           → Network Service Discovery (78 neighbors, 78 edges)
           → Koadic (31 neighbors, 31 edges)
           → Response Metadata (0 neighbors, 0 edges)
           → netstat (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 7/8: สอบถามรายการเครื่องแม่ข่ายที่ทำหน้าที่แปลงชื่อโดเมน (DNS enumeration)...
[RETRIEVE] Query: สอบถามรายการเครื่องแม่ข่ายที่ทำหน้าที่แปลงชื่อโดเมน (DNS enumeration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Active DNS (0.024), DEADEYE (0.023), Nltest (0.005), DNS (0.005), Software Configuration (0.004), Instance Enumeration (0.002), TAINTEDSCRIBE (0.002), Samurai (0.001), Name Resolution Poisoning and SMB Relay (0.001), spwebmember (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Active DNS (0 neighbors, 0 edges)
           → DEADEYE (13 neighbors, 13 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → DNS (60 neighbors, 60 edges)
           → Software Configuration (36 neighbors, 36 edges)
           → DNS (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] Query 8/8: ไล่แจกแจงการเชื่อมต่อที่ค้างอยู่ระหว่างเครื่องในเครือข่าย...
[RETRIEVE] Query: ไล่แจกแจงการเชื่อมต่อที่ค้างอยู่ระหว่างเครื่องในเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ping (0.083), HTRAN (0.041), PlugX (0.014), System Network Connections Discovery (0.014), netstat (0.013), Kwampirs (0.011), APT3 (0.009), Internet Connection Discovery (0.006), Port Knocking (0.003), Machete (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Ping (20 neighbors, 20 edges)
           → HTRAN (5 neighbors, 5 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → PlugX (65 neighbors, 65 edges)
           → Kwampirs (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [34/100] retrieved=725 relevant=5 latency=15505ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 19 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Query: เมื่อวันที่ 19 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.008), Clambling (0.002), APT-C-36 (0.001), Ursnif (0.000), Conficker (0.000), File Deletion (0.000), Hidden File System (0.000), Pre-OS Boot (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Clambling (35 neighbors, 35 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → AsyncRAT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 2/7: โปรแกรมฝังตัวเดิมดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดใหม่...
[RETRIEVE] Query: โปรแกรมฝังตัวเดิมดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดใหม่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bundlore (0.122), down_new (0.008), Backdoor.Oldrea (0.007), OLDBAIT (0.005), Downgrade System Image (0.003), PipeMon (0.003), SDBbot (0.002), PolyglotDuke (0.001), ISMInjector (0.001), OLDBAIT (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Bundlore (23 neighbors, 23 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Backdoor.Oldrea (17 neighbors, 17 edges)
           → down_new (11 neighbors, 11 edges)
           → OLDBAIT (7 neighbors, 7 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
[RETRIEVE-QUOTA] Query 3/7: รันตัวติดตั้งโปรแกรมฝังตัวพร้อมตัวเลือกยกระดับสิทธิ์...
[RETRIEVE] Query: รันตัวติดตั้งโปรแกรมฝังตัวพร้อมตัวเลือกยกระดับสิทธิ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Elevated Execution with Prompt (0.469), Installer Packages (0.304), User Account Control (0.075), User Account Control (0.027), AppInit DLLs (0.014), Registry Run Keys / Startup Folder (0.001), CrossRAT (0.001), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Elevated Execution with Prompt (5 neighbors, 5 edges)
           → Installer Packages (8 neighbors, 8 edges)
           → User Account Control (7 neighbors, 7 edges)
           → Executable Installer File Permissions Weakness (8 neighbors, 8 edges)
           → Services File Permissions Weakness (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/7: โปรแกรมฝังตัวซ่อนตัวเองจากรายการไฟล์และรายการกระบวนการ...
[RETRIEVE] Query: โปรแกรมฝังตัวซ่อนตัวเองจากรายการไฟล์และรายการกระบวนการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Monokle (0.553), Ixeshe (0.148), Rootkit (0.071), Hidden Files and Directories (0.013), Cobian RAT (0.005), Hidden Window (0.002), CrossRAT (0.002), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Monokle (24 neighbors, 24 edges)
           → Hooking (6 neighbors, 6 edges)
           → Ixeshe (16 neighbors, 16 edges)
           → Hidden Files and Directories (60 neighbors, 60 edges)
           → Rootkit (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 5/7: ไล่แจกแจงรายการกระบวนการที่ทำงานอยู่บนเครื่อง...
[RETRIEVE] Query: ไล่แจกแจงรายการกระบวนการที่ทำงานอยู่บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.154), Tasklist (0.100), PLAINTEE (0.019), Process Discovery (0.009), ListPlanting (0.002), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → PLAINTEE (10 neighbors, 10 edges)
           → ListPlanting (6 neighbors, 6 edges)
           → Visual Basic (140 neighbors, 140 edges)
[RETRIEVE-QUOTA] Query 6/7: ตรวจสอบสมาชิกกลุ่มผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์ในโดเมน...
[RETRIEVE] Query: ตรวจสอบสมาชิกกลุ่มผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์ในโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain Groups (0.260), BADHATCH (0.212), OSInfo (0.170), Nltest (0.047), Domain Account (0.011), Local Groups (0.005), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Domain Groups (41 neighbors, 41 edges)
           → BADHATCH (36 neighbors, 36 edges)
           → OSInfo (11 neighbors, 11 edges)
           → Nltest (11 neighbors, 11 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 7/7: แจกแจงรายการเชื่อมต่อเครือข่ายไปยังไดรฟ์ที่เชื่อมกับเครื่องแม่ข่ายเก็บไฟล์...
[RETRIEVE] Query: แจกแจงรายการเชื่อมต่อเครือข่ายไปยังไดรฟ์ที่เชื่อมกับเครื่องแม่ข่ายเก็บไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Drive Access (0.017), ShimRat (0.015), Network Share Discovery (0.003), Data from Network Shared Drive (0.003), Industroyer (0.001), CrackMapExec (0.001), netstat (0.000), System Network Connections Discovery (0.000), Network Share Access (0.000), ipconfig (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Drive Access (0 neighbors, 0 edges)
           → ShimRat (22 neighbors, 22 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
           → Data from Network Shared Drive (15 neighbors, 15 edges)
           → Industroyer (21 neighbors, 21 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [35/100] retrieved=674 relevant=5 latency=14915ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 22 กุมภาพันธ์ 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ถูกหลอกให้...
[RETRIEVE] Query: เมื่อวันที่ 22 กุมภาพันธ์ 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ถูกหลอกให้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Frankenstein (0.651), Malicious File (0.435), Rancor (0.176), Deobfuscate/Decode Files or Information (0.006), Adversary-in-the-Middle (0.001), Evil Twin (0.001), Outlook Forms (0.001), Magic Hound (0.000), Threat Group-3390 (0.000), ARP Cache Poisoning (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Frankenstein (28 neighbors, 28 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Rancor (13 neighbors, 13 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → Adversary-in-the-Middle (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 2/6: จดหมายอิเล็กทรอนิกส์ Phishing แนบไฟล์เอกสารเจาะจงเป้าหมายเจ้าหน้าที่...
[RETRIEVE] Query: จดหมายอิเล็กทรอนิกส์ Phishing แนบไฟล์เอกสารเจาะจงเป้าหมายเจ้าหน้าที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.290), Chaes (0.237), Spearphishing Attachment (0.141), Phishing (0.121), Spearphishing Attachment (0.095), Phishing for Information (0.042), Written Content (0.012), Spearphishing Link (0.006), VOID MANTICORE (0.004), Kimsuky (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Chaes (28 neighbors, 28 edges)
           → Phishing (23 neighbors, 23 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/6: เปิดไฟล์ตารางคำนวณที่มีมาโครอันตราย...
[RETRIEVE] Query: เปิดไฟล์ตารางคำนวณที่มีมาโครอันตราย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Rancor (0.688), Flagpro (0.432), TA2541 (0.184), C0015 (0.113), SQLRat (0.005), CALENDAR (0.003), XLoader (0.002), EvilGrab (0.002), AuditCred (0.001), TAMECAT (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Rancor (13 neighbors, 13 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Flagpro (25 neighbors, 25 edges)
           → Visual Basic (140 neighbors, 140 edges)
           → TA2541 (37 neighbors, 37 edges)
[RETRIEVE-QUOTA] Query 4/6: ชุดคำสั่งมาโครทำงานบนเครื่องหลังจากผู้ใช้อนุญาต...
[RETRIEVE] Query: ชุดคำสั่งมาโครทำงานบนเครื่องหลังจากผู้ใช้อนุญาต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Megazord (0.003), Installer Packages (0.002), Dok (0.002), MacMa (0.002), Launch Daemon (0.002), Sudo and Sudo Caching (0.001), MMC (0.000), BackConfig (0.000), At (0.000), Kernel Modules and Extensions (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Megazord (7 neighbors, 7 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Installer Packages (8 neighbors, 8 edges)
           → Dok (11 neighbors, 11 edges)
           → Linux and Mac Permissions (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 5/6: ไฟล์สคริปต์ติดตั้งในโฟลเดอร์เริ่มต้นระบบ (Startup folder persistence)...
[RETRIEVE] Query: ไฟล์สคริปต์ติดตั้งในโฟลเดอร์เริ่มต้นระบบ (Startup folder persistence)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RC Scripts (0.876), Startup Items (0.859), Registry Run Keys / Startup Folder (0.684), STARWHALE (0.626), Helminth (0.547), MuddyViper (0.356), Python Startup Hooks (0.159), Persistence (0.099), Login Hook (0.019), Active Setup (0.006)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RC Scripts (13 neighbors, 13 edges)
           → Startup Items (7 neighbors, 7 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → STARWHALE (15 neighbors, 15 edges)
           → Helminth (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 6/6: สคริปต์ทำงานซ้ำทุกครั้งที่ผู้ใช้ล็อกอินเข้าเครื่อง...
[RETRIEVE] Query: สคริปต์ทำงานซ้ำทุกครั้งที่ผู้ใช้ล็อกอินเข้าเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RogueRobin (0.912), Logon Script (Windows) (0.893), Zebrocy (0.635), Login Hook (0.582), xCaon (0.425), Boot or Logon Initialization Scripts (0.389), APT28 (0.262), Network Logon Script (0.259), Re-opened Applications (0.062), Active Setup (0.021)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Logon Script (Windows) (12 neighbors, 12 edges)
           → RogueRobin (19 neighbors, 19 edges)
           → Shortcut Modification (37 neighbors, 37 edges)
           → Login Hook (6 neighbors, 6 edges)
           → Zebrocy (32 neighbors, 32 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [36/100] retrieved=574 relevant=3 latency=11962ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 27 มิถุนายน 2567 บริษัทโลจิสติกส์ข้ามชาติสาขาประเทศไทยแจ้งความว่าเคร...
[RETRIEVE] Query: เมื่อวันที่ 27 มิถุนายน 2567 บริษัทโลจิสติกส์ข้ามชาติสาขาประเทศไทยแจ้งความว่าเคร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: admin@338 (0.001), admin@338 (0.001), Ingress Tool Transfer (0.000), FIN8 (0.000), Exploitation of Remote Services (0.000), Data Encrypted for Impact (0.000), Pikabot (0.000), Exfiltration to Text Storage Sites (0.000), Setuid and Setgid (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → admin@338 (19 neighbors, 19 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
[RETRIEVE-QUOTA] Query 2/9: เปิดการเชื่อมต่อ Remote Desktop Protocol (RDP) จากเครื่องภายนอกเข้าสู่เครื่องแม่...
[RETRIEVE] Query: เปิดการเชื่อมต่อ Remote Desktop Protocol (RDP) จากเครื่องภายนอกเข้าสู่เครื่องแม่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RDP Hijacking (0.055), SILENTTRINITY (0.046), Remote Desktop Protocol (0.040), Carbanak (0.039), Terminal Services DLL (0.023), Network Segmentation (0.011), Remote Desktop Software (0.005), Remote Access Tools (0.002), Remote Services (0.002), Windows Remote Management (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → Carbanak (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 3/9: ดาวน์โหลดไฟล์โปรแกรมมัลแวร์ลงบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมมัลแวร์ลงบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: GuLoader (0.058), Drovorub (0.014), admin@338 (0.010), OopsIE (0.007), Ingress Tool Transfer (0.003), Cobian RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → GuLoader (12 neighbors, 12 edges)
           → Drovorub (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → admin@338 (19 neighbors, 19 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] Query 4/9: สั่งให้รันมัลแวร์ผ่านการเชื่อมต่อ RDP...
[RETRIEVE] Query: สั่งให้รันมัลแวร์ผ่านการเชื่อมต่อ RDP...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Medusa Group (0.295), WarzoneRAT (0.036), Terminal Services DLL (0.033), RDP Hijacking (0.029), Remote Service Session Hijacking (0.023), Remote Desktop Protocol (0.018), Chimera (0.018), Axiom (0.007), BPFDoor (0.001), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Medusa Group (62 neighbors, 62 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
           → WarzoneRAT (33 neighbors, 33 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 5/9: สร้างงานตั้งเวลา (Scheduled Task) สำหรับรีสตาร์ตเครื่องคอมพิวเตอร์...
[RETRIEVE] Query: สร้างงานตั้งเวลา (Scheduled Task) สำหรับรีสตาร์ตเครื่องคอมพิวเตอร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SVCReady (0.705), Kimsuky (0.275), schtasks (0.122), At (0.116), at (0.100), Scheduled Task/Job (0.062), PowerSploit (0.059), schtasks (0.031), Scheduled Task (0.019), Tasklist (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SVCReady (24 neighbors, 24 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Kimsuky (150 neighbors, 150 edges)
           → At (17 neighbors, 17 edges)
           → schtasks (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/9: เข้ารหัสลับไฟล์ทั้งหมดในโฟลเดอร์ผู้ใช้ (Ransomware encryption)...
[RETRIEVE] Query: เข้ารหัสลับไฟล์ทั้งหมดในโฟลเดอร์ผู้ใช้ (Ransomware encryption)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ShrinkLocker (0.137), BlackByte (0.132), cipher.exe (0.085), INC Ransomware (0.065), Data Encrypted for Impact (0.049), Playcrypt (0.042), INC Ransom (0.027), Cheerscrypt (0.024), Akira (0.014), BlackByte Ransomware (0.008)
[RETRIEVE] Graph expansion: 6 subgraphs
           → BlackByte (56 neighbors, 56 edges)
           → Internal Defacement (18 neighbors, 18 edges)
           → ShrinkLocker (21 neighbors, 21 edges)
           → cipher.exe (3 neighbors, 3 edges)
           → INC Ransomware (16 neighbors, 16 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] Query 7/9: วางไฟล์ข้อความเรียกค่าไถ่บนไดรฟ์หลัก...
[RETRIEVE] Query: วางไฟล์ข้อความเรียกค่าไถ่บนไดรฟ์หลัก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CHIMNEYSWEEP (0.007), KernelCallbackTable (0.001), Pisloader (0.001), Overwrite Process Arguments (0.000), Visual Basic (0.000), Dynamic-link Library Injection (0.000), Terminal Services DLL (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CHIMNEYSWEEP (32 neighbors, 32 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → KernelCallbackTable (7 neighbors, 7 edges)
           → Pisloader (10 neighbors, 10 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 8/9: คัดลอกมัลแวร์ไปทำงานต่อบนเครื่องอื่นในเครือข่าย (Lateral Movement)...
[RETRIEVE] Query: คัดลอกมัลแวร์ไปทำงานต่อบนเครื่องอื่นในเครือข่าย (Lateral Movement)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Replication Through Removable Media (0.945), Lateral Tool Transfer (0.518), Lateral Movement (0.417), Expand (0.123), esentutl (0.090), Network Share Discovery (0.067), APT18 (0.015), OS Credential Dumping (0.012), LSASS Memory (0.012), Pcexter (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Replication Through Removable Media (35 neighbors, 35 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Lateral Movement (23 neighbors, 23 edges)
           → Expand (3 neighbors, 3 edges)
           → esentutl (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 9/9: ปิดการเชื่อมต่อ RDP กับเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: ปิดการเชื่อมต่อ RDP กับเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Disable or Remove Feature or Program (0.238), Network Segmentation (0.073), Chimera (0.003), RDP Hijacking (0.003), Limit Access to Resource Over Network (0.002), Terminal Services DLL (0.002), Remote Desktop Protocol (0.001), Axiom (0.001), Disable or Modify System Firewall (0.000), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Network Segmentation (37 neighbors, 37 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Chimera (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [37/100] retrieved=723 relevant=3 latency=17598ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 18 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ระ...
[RETRIEVE] Query: เมื่อวันที่ 18 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ระ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Create or Modify System Process (0.644), APT3 (0.458), Pallas (0.433), PUNCHTRACK (0.219), Deobfuscate/Decode Files or Information (0.147), VERMIN (0.099), Hide Artifacts (0.041), Obfuscated Files or Information (0.021), Encrypted/Encoded File (0.018), Hidden Files and Directories (0.011)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → APT3 (50 neighbors, 50 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Pallas (15 neighbors, 15 edges)
           → Obfuscated Files or Information (51 neighbors, 51 edges)
[RETRIEVE-QUOTA] Query 2/7: ดาวน์โหลดแอปพลิเคชันซื้อขายที่ดาวน์โหลดมาจากเว็บไซต์ปลอม...
[RETRIEVE] Query: ดาวน์โหลดแอปพลิเคชันซื้อขายที่ดาวน์โหลดมาจากเว็บไซต์ปลอม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RatMilad (0.169), CSPY Downloader (0.014), CoinTicker (0.011), GuLoader (0.001), 4H RAT (0.000), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RatMilad (18 neighbors, 18 edges)
           → Download New Code at Runtime (42 neighbors, 42 edges)
           → CSPY Downloader (13 neighbors, 13 edges)
           → Masquerade Task or Service (94 neighbors, 94 edges)
           → CoinTicker (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 3/7: Create or Modify System Process: Launch Daemon เพื่อเรียกโปรแกรมของคนร้ายทำงานเบ...
[RETRIEVE] Query: Create or Modify System Process: Launch Daemon เพื่อเรียกโปรแกรมของคนร้ายทำงานเบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Create or Modify System Process (0.843), Launch Daemon (0.793), LITTLELAMB.WOOLTEA (0.779), Launch Agent (0.323), System Services (0.243), IMAPLoader (0.172), REPTILE (0.102), Process Modification (0.017), Audit (0.015), Service Creation (0.009)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → Launch Daemon (18 neighbors, 18 edges)
           → LITTLELAMB.WOOLTEA (8 neighbors, 8 edges)
           → Launch Agent (28 neighbors, 28 edges)
           → System Services (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 4/7: Hide Artifacts: Hidden Files and Directories ตั้งชื่อไฟล์ขึ้นต้นด้วยจุด...
[RETRIEVE] Query: Hide Artifacts: Hidden Files and Directories ตั้งชื่อไฟล์ขึ้นต้นด้วยจุด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Hide Artifacts (0.452), Antivirus/Antimalware (0.289), Remcos (0.080), Tarrask (0.042), Hidden Files and Directories (0.031), Space after Filename (0.028), File/Path Exclusions (0.027), Encrypted/Encoded File (0.007), Hide Infrastructure (0.005), Restrict File and Directory Permissions (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Hide Artifacts (26 neighbors, 26 edges)
           → Antivirus/Antimalware (23 neighbors, 23 edges)
           → Remcos (43 neighbors, 43 edges)
           → Tarrask (8 neighbors, 8 edges)
           → Hidden Files and Directories (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] Query 5/7: Obfuscated Files or Information เข้ารหัสลับและอำพรางโปรแกรม...
[RETRIEVE] Query: Obfuscated Files or Information เข้ารหัสลับและอำพรางโปรแกรม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Obfuscated Files or Information (0.938), OBAD (0.937), WolfRAT (0.901), PUBLOAD (0.896), APT3 (0.884), Deobfuscate/Decode Files or Information (0.763), Encrypted/Encoded File (0.561), Compression (0.145), Malicious File (0.024), Polymorphic Code (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → OBAD (2 neighbors, 2 edges)
           → Obfuscated Files or Information (51 neighbors, 51 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → WolfRAT (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 6/7: ติดตั้งโปรแกรมควบคุมระยะไกล (Remote Access Trojan) ลงบนเครื่อง...
[RETRIEVE] Query: ติดตั้งโปรแกรมควบคุมระยะไกล (Remote Access Trojan) ลงบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MarkiRAT (0.401), JSS Loader (0.257), SLOTHFULMEDIA (0.117), Execution Prevention (0.059), FIN7 (0.043), OopsIE (0.018), Cannon (0.002), NGLite (0.002), NGLite (0.001), NGLite (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → MarkiRAT (23 neighbors, 23 edges)
           → JSS Loader (8 neighbors, 8 edges)
           → SLOTHFULMEDIA (24 neighbors, 24 edges)
           → Execution Prevention (79 neighbors, 79 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 7/7: ติดตั้งโปรแกรมควบคุมระยะไกลให้ทำงานเป็นบริการของระบบ...
[RETRIEVE] Query: ติดตั้งโปรแกรมควบคุมระยะไกลให้ทำงานเป็นบริการของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteUtilities (0.595), RemoteCMD (0.171), RemoteCMD (0.056), xCmd (0.027), Execution Prevention (0.023), Windows Remote Management (0.018), RemoteUtilities (0.010), Remote Access Tools (0.005), Service Execution (0.002), Tasklist (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → RemoteUtilities (5 neighbors, 5 edges)
           → Msiexec (35 neighbors, 35 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Execution Prevention (79 neighbors, 79 edges)
           → Remote Desktop Software (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [38/100] retrieved=332 relevant=3 latency=13416ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 21 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Query: เมื่อวันที่ 21 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Credential Editor (0.276), Axiom (0.202), HOMEFRY (0.154), OS Credential Dumping (0.116), Suckfly (0.055), gsecdump (0.020), Password Cracking (0.007), Credential Access (0.006), Credential Access Protection (0.001), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Windows Credential Editor (8 neighbors, 8 edges)
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → HOMEFRY (4 neighbors, 4 edges)
           → Suckfly (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมฝังตัวบนเครื่องแม่ข่ายควบคุมโดเมนได้รับคำสั่งดาวน์โหลดเครื่องมือ Credenti...
[RETRIEVE] Query: โปรแกรมฝังตัวบนเครื่องแม่ข่ายควบคุมโดเมนได้รับคำสั่งดาวน์โหลดเครื่องมือ Credenti...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HOMEFRY (0.555), MgBot (0.295), Suckfly (0.289), pwdump (0.249), Windows Credential Editor (0.232), MimiPenguin (0.212), Axiom (0.212), OS Credential Dumping (0.093), Credentials In Files (0.012), Credential Access Protection (0.007)
[RETRIEVE] Graph expansion: 5 subgraphs
           → HOMEFRY (4 neighbors, 4 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → MgBot (18 neighbors, 18 edges)
           → Suckfly (6 neighbors, 6 edges)
           → Axiom (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 3/8: ดึงค่าความลับของบัญชีผู้ใช้จากฐานข้อมูลความปลอดภัยของระบบ...
[RETRIEVE] Query: ดึงค่าความลับของบัญชีผู้ใช้จากฐานข้อมูลความปลอดภัยของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Security Account Manager (0.428), APT41 (0.326), LSA Secrets (0.045), HOPLIGHT (0.042), Reversible Encryption (0.003), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Security Account Manager (43 neighbors, 43 edges)
           → APT41 (116 neighbors, 116 edges)
           → LSA Secrets (25 neighbors, 25 edges)
           → HOPLIGHT (23 neighbors, 23 edges)
           → Reversible Encryption (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/8: ดาวน์โหลดเครื่องมือสั่งงานเครื่องระยะไกล...
[RETRIEVE] Query: ดาวน์โหลดเครื่องมือสั่งงานเครื่องระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ZxShell (0.706), RemoteCMD (0.673), RTM (0.450), MCMD (0.398), xCmd (0.390), Quick Assist (0.232), FunnyDream (0.131), gh0st RAT (0.064), RemoteUtilities (0.033), dsquery (0.026)
[RETRIEVE] Graph expansion: 5 subgraphs
           → ZxShell (37 neighbors, 37 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → RTM (39 neighbors, 39 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
           → MCMD (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 5/8: ดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวสำเนาที่สามเก็บไว้บนเครื่องแม่ข่าย...
[RETRIEVE] Query: ดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวสำเนาที่สามเก็บไว้บนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kerrdown (0.004), PUNCHBUGGY (0.002), APT3 (0.001), PlugX (0.001), LockBit 3.0 (0.001), APT3 (0.001), BUBBLEWRAP (0.001), 3PARA RAT (0.000), gsecdump (0.000), Fgdump (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Kerrdown (12 neighbors, 12 edges)
           → PUNCHBUGGY (18 neighbors, 18 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → APT3 (50 neighbors, 50 edges)
           → LockBit 3.0 (34 neighbors, 34 edges)
           → Windows Service (150 neighbors, 150 edges)
[RETRIEVE-QUOTA] Query 6/8: ใช้ค่าแฮชรหัสผ่านเพื่อยืนยันตัวตนกับเครื่องปลายทาง (Pass-the-Hash)...
[RETRIEVE] Query: ใช้ค่าแฮชรหัสผ่านเพื่อยืนยันตัวตนกับเครื่องปลายทาง (Pass-the-Hash)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pass the Hash (0.813), Kimsuky (0.512), Pass-The-Hash Toolkit (0.464), Pass-The-Hash Toolkit (0.246), APT1 (0.083), Password Cracking (0.018), Modify Authentication Process (0.001), netsh (0.000), menuPass (0.000), PUBLOAD (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pass the Hash (29 neighbors, 29 edges)
           → Kimsuky (150 neighbors, 150 edges)
           → Pass-The-Hash Toolkit (2 neighbors, 2 edges)
           → APT1 (40 neighbors, 40 edges)
           → Password Cracking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 7/8: คัดลอกตัวติดตั้งโปรแกรมฝังตัวไปยังเครื่องคอมพิวเตอร์ของพนักงาน...
[RETRIEVE] Query: คัดลอกตัวติดตั้งโปรแกรมฝังตัวไปยังเครื่องคอมพิวเตอร์ของพนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: USBferry (0.016), PsExec (0.002), cmd (0.001), PoshC2 (0.001), Psylo (0.000), gsecdump (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → USBferry (12 neighbors, 12 edges)
           → Replication Through Removable Media (35 neighbors, 35 edges)
           → PsExec (49 neighbors, 49 edges)
           → cmd (13 neighbors, 13 edges)
           → PoshC2 (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 8/8: เรียกใช้โปรแกรมฝังตัวบนเครื่องพนักงานผ่านเครื่องมือสั่งงานระยะไกล...
[RETRIEVE] Query: เรียกใช้โปรแกรมฝังตัวบนเครื่องพนักงานผ่านเครื่องมือสั่งงานระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.044), xCmd (0.014), HermeticWizard (0.010), RemoteCMD (0.007), Windows Remote Management (0.001), CrossRAT (0.000), Ptrace System Calls (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → xCmd (2 neighbors, 2 edges)
           → HermeticWizard (16 neighbors, 16 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Scheduled Task (201 neighbors, 201 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [39/100] retrieved=192 relevant=3 latency=14726ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 19 กุมภาพันธ์ 2564 ผู้เสียหายอีกรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Query: เมื่อวันที่ 19 กุมภาพันธ์ 2564 ผู้เสียหายอีกรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: JHUHUGIT (0.828), ccf32 (0.641), Solar (0.407), CURIUM (0.300), Exfiltration Over C2 Channel (0.085), Scheduled Transfer (0.079), Automated Exfiltration (0.047), Scheduled Task/Job (0.026), Scheduled Task (0.005), Exfiltration Over Unencrypted Non-C2 Protocol (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → JHUHUGIT (21 neighbors, 21 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → ccf32 (13 neighbors, 13 edges)
           → Solar (10 neighbors, 10 edges)
           → CURIUM (20 neighbors, 20 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
[RETRIEVE-QUOTA] Query 2/6: ติดตั้ง Scheduled Task ที่ทำงานด้วยสิทธิ์ระบบเมื่อผู้ใช้ล็อกอิน...
[RETRIEVE] Query: ติดตั้ง Scheduled Task ที่ทำงานด้วยสิทธิ์ระบบเมื่อผู้ใช้ล็อกอิน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operating System Configuration (0.846), Operating System Configuration (0.836), Scheduled Task/Job (0.072), schtasks (0.034), Scheduled Task (0.016), At (0.015), at (0.009), schtasks (0.007), Confucius (0.004), Masquerade Task or Service (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Operating System Configuration (39 neighbors, 39 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Scheduled Task/Job (18 neighbors, 18 edges)
           → schtasks (4 neighbors, 4 edges)
           → At (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 3/6: System Owner/User Discovery เก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้...
[RETRIEVE] Query: System Owner/User Discovery เก็บรวบรวมข้อมูลเจ้าของเครื่องและชื่อผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DarkComet (0.921), Micropsia (0.914), Epic (0.912), System Owner/User Discovery (0.890), XLoader (0.817), System Network Configuration Discovery (0.062), Systeminfo (0.049), System Network Connections Discovery (0.037), System Information Discovery (0.034), Device Driver Discovery (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → DarkComet (21 neighbors, 21 edges)
           → Micropsia (17 neighbors, 17 edges)
           → Epic (23 neighbors, 23 edges)
           → XLoader (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] Query 4/6: เข้ารหัสข้อมูลด้วยกุญแจที่ฝังในโปรแกรมแล้วส่งออก...
[RETRIEVE] Query: เข้ารหัสข้อมูลด้วยกุญแจที่ฝังในโปรแกรมแล้วส่งออก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Fooder (0.041), DRYHOOK (0.012), BitPaymer (0.009), Credential API Hooking (0.007), KEYPLUG (0.006), cipher.exe (0.003), Cachedump (0.003), Process Injection (0.002), Ryuk (0.002), Software Packing (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Fooder (8 neighbors, 8 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → DRYHOOK (11 neighbors, 11 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → BitPaymer (19 neighbors, 19 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] Query 5/6: Exfiltration Over C2 Channel ส่งข้อมูลไปยังเว็บไซต์สั่งการ...
[RETRIEVE] Query: Exfiltration Over C2 Channel ส่งข้อมูลไปยังเว็บไซต์สั่งการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration to Text Storage Sites (0.910), Exfiltration Over C2 Channel (0.903), BLINDINGCAN (0.859), ShimRatReporter (0.738), Exfiltration Over Unencrypted Non-C2 Protocol (0.707), MacMa (0.556), Scheduled Transfer (0.455), Automated Exfiltration (0.350), APT39 (0.269), Data Staged (0.021)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration to Text Storage Sites (4 neighbors, 4 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → BLINDINGCAN (23 neighbors, 23 edges)
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
           → ShimRatReporter (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 6/6: รวบรวมข้อมูลประจำเครื่องของผู้เสียหายและส่งออกไปยังเว็บไซต์สั่งการ...
[RETRIEVE] Query: รวบรวมข้อมูลประจำเครื่องของผู้เสียหายและส่งออกไปยังเว็บไซต์สั่งการ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gather Victim Host Information (0.155), NOKKI (0.080), Gather Victim Network Information (0.028), CORESHELL (0.026), Gather Victim Identity Information (0.016), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Gather Victim Host Information (7 neighbors, 7 edges)
           → NOKKI (17 neighbors, 17 edges)
           → Local Data Staging (138 neighbors, 138 edges)
           → Gather Victim Network Information (11 neighbors, 11 edges)
           → CORESHELL (12 neighbors, 12 edges)
           → Local Storage Discovery (103 neighbors, 103 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [40/100] retrieved=423 relevant=3 latency=11298ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 11 ตุลาคม 2567 บริษัทวิศวกรรมแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใน...
[RETRIEVE] Query: เมื่อวันที่ 11 ตุลาคม 2567 บริษัทวิศวกรรมแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lucifer (0.031), Operation Honeybee (0.005), FIN8 (0.001), File Deletion (0.000), Deobfuscate/Decode Files or Information (0.000), Windows Management Instrumentation (0.000), Browser Extensions (0.000), Video Capture (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Lucifer (24 neighbors, 24 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Operation Honeybee (33 neighbors, 33 edges)
           → File Deletion (310 neighbors, 310 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/6: เครื่องแม่ข่ายภายในถูกใช้เป็นทางผ่านเชื่อมต่อจากภายนอก...
[RETRIEVE] Query: เครื่องแม่ข่ายภายในถูกใช้เป็นทางผ่านเชื่อมต่อจากภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Strider (0.140), StarProxy (0.067), Internal Proxy (0.055), Network Segmentation (0.019), External Proxy (0.011), Network Boundary Bridging (0.006), Exfiltration over USB (0.002), Exfiltration Over Bluetooth (0.001), Exfiltration Over Physical Medium (0.001), Exfiltration Over Other Network Medium (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Strider (4 neighbors, 4 edges)
           → Internal Proxy (39 neighbors, 39 edges)
           → StarProxy (10 neighbors, 10 edges)
           → Network Segmentation (37 neighbors, 37 edges)
           → External Remote Services (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] Query 3/6: ลบไฟล์โปรแกรมและไฟล์ผลลัพธ์เพื่อเก็บกวาดร่องรอย...
[RETRIEVE] Query: ลบไฟล์โปรแกรมและไฟล์ผลลัพธ์เพื่อเก็บกวาดร่องรอย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File Deletion (0.049), Disable or Remove Feature or Program (0.013), Uroburos (0.004), Milan (0.003), Visual Basic (0.000), 4H RAT (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → Uroburos (37 neighbors, 37 edges)
           → Milan (21 neighbors, 21 edges)
           → Visual Basic (140 neighbors, 140 edges)
[RETRIEVE-QUOTA] Query 4/6: ดาวน์โหลดโปรแกรมเชื่อมต่อระยะไกลขนาดเล็กเก็บไว้บนเครื่อง...
[RETRIEVE] Query: ดาวน์โหลดโปรแกรมเชื่อมต่อระยะไกลขนาดเล็กเก็บไว้บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NavRAT (0.035), xCmd (0.016), Cobian RAT (0.014), Small Sieve (0.012), cmd (0.008), HTRAN (0.005), CrossRAT (0.004), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → NavRAT (10 neighbors, 10 edges)
           → xCmd (2 neighbors, 2 edges)
           → Small Sieve (14 neighbors, 14 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Cobian RAT (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 5/6: สั่งโปรแกรมเชื่อมต่อระยะไกลทำงานเพื่อห่อหุ้มการเชื่อมต่อหน้าจอระยะไกล...
[RETRIEVE] Query: สั่งโปรแกรมเชื่อมต่อระยะไกลทำงานเพื่อห่อหุ้มการเชื่อมต่อหน้าจอระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Desktop Software (0.044), RemoteCMD (0.036), Koadic (0.006), RemoteCMD (0.003), Terminal Services DLL (0.002), CrackMapExec (0.002), Application Layer Protocol (0.002), HTRAN (0.001), Windows Remote Management (0.001), Regsvr32 (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Remote Desktop Software (21 neighbors, 21 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → Koadic (31 neighbors, 31 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Scheduled Task (201 neighbors, 201 edges)
[RETRIEVE-QUOTA] Query 6/6: ซ่อนการเชื่อมต่อระยะไกลภายในช่องทางเชื่อมต่ออีกชั้นหนึ่งเพื่อหลีกเลี่ยงการตรวจจั...
[RETRIEVE] Query: ซ่อนการเชื่อมต่อระยะไกลภายในช่องทางเชื่อมต่ออีกชั้นหนึ่งเพื่อหลีกเลี่ยงการตรวจจั...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Protocol Tunneling (0.431), Network Segmentation (0.020), DNS (0.019), Hide Infrastructure (0.012), Network Segmentation (0.009), Cobian RAT (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Protocol Tunneling (46 neighbors, 46 edges)
           → DNS (60 neighbors, 60 edges)
           → Network Segmentation (37 neighbors, 37 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → Hide Infrastructure (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [41/100] retrieved=595 relevant=3 latency=12217ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 29 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Query: เมื่อวันที่ 29 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dragonfly (0.021), APT-C-36 (0.011), APT-C-36 (0.005), BADHATCH (0.001), Domain Accounts (0.000), Ursnif (0.000), Domains (0.000), Internal Spearphishing (0.000), Domain Account (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Dragonfly (66 neighbors, 66 edges)
           → Domain Account (65 neighbors, 65 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → AsyncRAT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 2/7: รหัสผ่านผู้ดูแลโดเมนถูกใช้เข้าถึงเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล...
[RETRIEVE] Query: รหัสผ่านผู้ดูแลโดเมนถูกใช้เข้าถึงเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VOID MANTICORE (0.208), Volt Typhoon (0.052), Domain Controller Authentication (0.021), Domain Accounts (0.019), Domain Account (0.002), MCMD (0.001), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Domain Accounts (47 neighbors, 47 edges)
           → Volt Typhoon (100 neighbors, 100 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Domain Controller Authentication (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/7: แก้ไขงานตั้งเวลาที่มีอยู่เดิมบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: แก้ไขงานตั้งเวลาที่มีอยู่เดิมบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operating System Configuration (0.155), Scheduled Job Modification (0.051), Operating System Configuration (0.050), Service Modification (0.007), Domain or Tenant Policy Modification (0.003), System Time Discovery (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Operating System Configuration (39 neighbors, 39 edges)
           → Scheduled Task/Job (18 neighbors, 18 edges)
           → Scheduled Job Modification (0 neighbors, 0 edges)
           → At (17 neighbors, 17 edges)
           → Service Modification (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 4/7: สั่งให้งานตั้งเวลาที่แก้ไขแล้วเริ่มทำงานทันที...
[RETRIEVE] Query: สั่งให้งานตั้งเวลาที่แก้ไขแล้วเริ่มทำงานทันที...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: schtasks (0.004), yty (0.004), at (0.003), at (0.003), Visual Basic (0.000), 4H RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Cobian RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → yty (15 neighbors, 15 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → schtasks (4 neighbors, 4 edges)
           → at (5 neighbors, 5 edges)
           → At (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 5/7: ติดตั้งโปรแกรมฝังตัวใหม่บนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: ติดตั้งโปรแกรมฝังตัวใหม่บนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RegDuke (0.050), Mimikatz (0.006), Regsvr32 (0.004), PipeMon (0.004), AppDomainManager (0.003), Pandora (0.003), Domain Controller Authentication (0.003), Rogue Domain Controller (0.002), TYPEFRAME (0.001), Additional Local or Domain Groups (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RegDuke (11 neighbors, 11 edges)
           → Mimikatz (77 neighbors, 77 edges)
           → Rogue Domain Controller (2 neighbors, 2 edges)
           → Regsvr32 (39 neighbors, 39 edges)
           → AppDomainManager (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 6/7: แจกแจงรายชื่อสมาชิกของกลุ่มสิทธิ์ในโดเมนเพื่อค้นหาบัญชีผู้มีสิทธิ์สูง...
[RETRIEVE] Query: แจกแจงรายชื่อสมาชิกของกลุ่มสิทธิ์ในโดเมนเพื่อค้นหาบัญชีผู้มีสิทธิ์สูง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain Groups (0.549), Domain Account (0.186), Sykipot (0.185), CrackMapExec (0.096), Cobalt Strike (0.040), BADHATCH (0.020), Cloud Account (0.004), Additional Local or Domain Groups (0.004), Cloud Groups (0.003), Domain Trust Discovery (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Domain Groups (41 neighbors, 41 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Sykipot (11 neighbors, 11 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] Query 7/7: ไล่แจกแจงรายชื่อเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนในระบบทะเบียนโดเมน...
[RETRIEVE] Query: ไล่แจกแจงรายชื่อเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนในระบบทะเบียนโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain Account (0.016), Nltest (0.015), CrackMapExec (0.015), DUSTTRAP (0.004), Domain Registration (0.001), Active DNS (0.001), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Domain Account (65 neighbors, 65 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Nltest (11 neighbors, 11 edges)
           → DUSTTRAP (31 neighbors, 31 edges)
           → Domain Registration (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [42/100] retrieved=265 relevant=3 latency=13807ms
[RETRIEVE-QUOTA] Query 1/10: เมื่อวันที่ 15 พฤศจิกายน 2566 มหาวิทยาลัยแห่งหนึ่งแจ้งความว่าระบบสารสนเทศของมหาว...
[RETRIEVE] Query: เมื่อวันที่ 15 พฤศจิกายน 2566 มหาวิทยาลัยแห่งหนึ่งแจ้งความว่าระบบสารสนเทศของมหาว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ZxShell (0.006), zwShell (0.001), LAPSUS$ (0.000), RDP Hijacking (0.000), POWERSOURCE (0.000), Remote Desktop Protocol (0.000), Duqu (0.000), Valid Accounts (0.000), PowerShell (0.000), Modify Authentication Process (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → ZxShell (37 neighbors, 37 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → zwShell (12 neighbors, 12 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
           → Password Managers (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 2/10: Phishing email ส่งให้บุคลากรมหาวิทยาลัยเพื่อหลอกลวง...
[RETRIEVE] Query: Phishing email ส่งให้บุคลากรมหาวิทยาลัยเพื่อหลอกลวง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT41 (0.025), Phishing for Information (0.017), AppleJeus (0.015), Phishing (0.015), Spearphishing Attachment (0.014), Spearphishing Attachment (0.013), Spearphishing Link (0.012), Spearphishing Link (0.008), VOID MANTICORE (0.004), Email Accounts (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT41 (116 neighbors, 116 edges)
           → Impersonation (24 neighbors, 24 edges)
           → Phishing for Information (12 neighbors, 12 edges)
           → Phishing (23 neighbors, 23 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
[RETRIEVE-QUOTA] Query 3/10: ช่องโหว่ร้ายแรงของโพรโทคอลยืนยันตัวตนระหว่างเครื่องลูกข่ายกับเครื่องแม่ข่ายควบคุ...
[RETRIEVE] Query: ช่องโหว่ร้ายแรงของโพรโทคอลยืนยันตัวตนระหว่างเครื่องลูกข่ายกับเครื่องแม่ข่ายควบคุ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Heyoka Backdoor (0.173), Domain Controller Authentication (0.070), DNS (0.006), DRYHOOK (0.003), POWERSOURCE (0.003), DCSync (0.001), BADCALL (0.001), Domains (0.001), BackConfig (0.000), Break Process Trees (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Heyoka Backdoor (16 neighbors, 16 edges)
           → Protocol Tunneling (46 neighbors, 46 edges)
           → Domain Controller Authentication (12 neighbors, 12 edges)
           → DNS (60 neighbors, 60 edges)
           → DRYHOOK (11 neighbors, 11 edges)
           → Modify Authentication Process (29 neighbors, 29 edges)
[RETRIEVE-QUOTA] Query 4/10: ยกระดับสิทธิ์เป็นผู้ดูแลระบบผ่านช่องโหว่โพรโทคอลยืนยันตัวตน...
[RETRIEVE] Query: ยกระดับสิทธิ์เป็นผู้ดูแลระบบผ่านช่องโหว่โพรโทคอลยืนยันตัวตน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bypass User Account Control (0.034), Threat Group-3390 (0.010), PowerShell Profile (0.001), Parent PID Spoofing (0.001), Modify Authentication Process (0.000), Update Software (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bypass User Account Control (70 neighbors, 70 edges)
           → Threat Group-3390 (81 neighbors, 81 edges)
           → PowerShell Profile (9 neighbors, 9 edges)
           → Parent PID Spoofing (8 neighbors, 8 edges)
           → Modify Authentication Process (29 neighbors, 29 edges)
[RETRIEVE-QUOTA] Query 5/10: ขโมยชื่อผู้ใช้และรหัสผ่านที่ยังใช้งานได้...
[RETRIEVE] Query: ขโมยชื่อผู้ใช้และรหัสผ่านที่ยังใช้งานได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credential Access (0.549), APT37 (0.341), Lokibot (0.229), FIN6 (0.217), MirrorStealer (0.199), Keydnap (0.187), LP-Notes (0.164), Mimikatz (0.090), Valid Accounts (0.024), LAPSUS$ (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Credential Access (67 neighbors, 67 edges)
           → APT37 (42 neighbors, 42 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → FIN6 (52 neighbors, 52 edges)
           → Valid Accounts (82 neighbors, 82 edges)
[RETRIEVE-QUOTA] Query 6/10: ยืนยันตัวตนเข้าสู่จุดเชื่อมต่อเครือข่ายส่วนตัวเสมือนโดยใช้ข้อมูลประจำตัวที่ขโมยม...
[RETRIEVE] Query: ยืนยันตัวตนเข้าสู่จุดเชื่อมต่อเครือข่ายส่วนตัวเสมือนโดยใช้ข้อมูลประจำตัวที่ขโมยม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN10 (0.030), Suckfly (0.005), Steal or Forge Authentication Certificates (0.004), Valid Accounts (0.001), Web Portal Capture (0.000), Modify Authentication Process (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN10 (12 neighbors, 12 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Suckfly (6 neighbors, 6 edges)
           → Steal or Forge Authentication Certificates (9 neighbors, 9 edges)
           → Web Portal Capture (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 7/10: เปิดการเชื่อมต่อ Remote Desktop Protocol ไปยังเครื่องอื่นเพื่อขยายการเข้าถึง...
[RETRIEVE] Query: เปิดการเชื่อมต่อ Remote Desktop Protocol ไปยังเครื่องอื่นเพื่อขยายการเข้าถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Koadic (0.075), Limit Access to Resource Over Network (0.060), Terminal Services DLL (0.042), VNC (0.041), Remote Desktop Protocol (0.039), RDP Hijacking (0.030), Remote Access Tools (0.009), Remote Desktop Software (0.009), Axiom (0.002), Remote Services (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Koadic (31 neighbors, 31 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
           → VNC (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 8/10: เปิดช่องทางเครือข่ายส่วนตัวเสมือนไว้เพื่อคงการเข้าถึงต่อเนื่อง...
[RETRIEVE] Query: เปิดช่องทางเครือข่ายส่วนตัวเสมือนไว้เพื่อคงการเข้าถึงต่อเนื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: GALLIUM (0.011), Leviathan (0.007), Valid Accounts (0.004), Create Account (0.002), C0032 (0.002), Remote Service Session Hijacking (0.002), SILENTTRINITY (0.001), External Remote Services (0.001), Network Logon Script (0.000), HTRAN (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → GALLIUM (47 neighbors, 47 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → Leviathan (68 neighbors, 68 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Create Account (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 9/10: สั่งงานผ่าน PowerShell เพื่อดำเนินการต่างๆ ในระบบ...
[RETRIEVE] Query: สั่งงานผ่าน PowerShell เพื่อดำเนินการต่างๆ ในระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerShell (0.670), PowerExchange (0.191), POWERSTATS (0.153), Disable or Remove Feature or Program (0.132), POWRUNER (0.131), AADInternals (0.085), PowerSploit (0.042), PowerShell Profile (0.017), POWERSTATS (0.007), Invoke-PSImage (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PowerShell (241 neighbors, 241 edges)
           → PowerExchange (6 neighbors, 6 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → POWRUNER (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 10/10: เข้ารหัสลับข้อมูลนักศึกษาของมหาวิทยาลัย...
[RETRIEVE] Query: เข้ารหัสลับข้อมูลนักศึกษาของมหาวิทยาลัย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TianySpy (0.003), PolyglotDuke (0.001), UNC3886 (0.001), Deobfuscate/Decode Files or Information (0.001), gsecdump (0.001), Encrypted/Encoded File (0.001), Obfuscated Files or Information (0.001), PolyglotDuke (0.000), ShrinkLocker (0.000), Archive via Utility (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → TianySpy (9 neighbors, 9 edges)
           → Obfuscated Files or Information (51 neighbors, 51 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → PolyglotDuke (12 neighbors, 12 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 10 queries
  [43/100] retrieved=245 relevant=5 latency=19236ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความว่าข้อมูลลูกค้าถูกนำออ...
[RETRIEVE] Query: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความว่าข้อมูลลูกค้าถูกนำออ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.204), INC Ransom (0.127), Pay2Key (0.014), Data Encrypted for Impact (0.013), Ursnif (0.004), Exfiltration (0.003), APT-C-36 (0.000), Internal Spearphishing (0.000), Social Engineering (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → INC Ransom (33 neighbors, 33 edges)
           → Financial Theft (27 neighbors, 27 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] Query 2/5: ใช้โปรแกรมรับส่งไฟล์ลำเลียงข้อมูลลูกค้าออกจากเครือข่ายไปยังบัญชีปลายทางของคนร้าย...
[RETRIEVE] Query: ใช้โปรแกรมรับส่งไฟล์ลำเลียงข้อมูลลูกค้าออกจากเครือข่ายไปยังบัญชีปลายทางของคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Koadic (0.089), Drovorub (0.072), WellMess (0.061), Ingress Tool Transfer (0.043), Briba (0.033), Net Crawler (0.009), Exploitation for Client Execution (0.004), PUNCHTRACK (0.003), FrameworkPOS (0.003), Financial Theft (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Koadic (31 neighbors, 31 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Drovorub (13 neighbors, 13 edges)
           → WellMess (16 neighbors, 16 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 3/5: เข้ารหัสลับไฟล์ระบบงานด้วยวิธีผสมระหว่างการเข้ารหัสแบบสมมาตรและแบบกุญแจสาธารณะ...
[RETRIEVE] Query: เข้ารหัสลับไฟล์ระบบงานด้วยวิธีผสมระหว่างการเข้ารหัสแบบสมมาตรและแบบกุญแจสาธารณะ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Asymmetric Cryptography (0.347), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.153), Symmetric Cryptography (0.149), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.102), BitPaymer (0.051), Encrypted/Encoded File (0.043), ComRAT (0.016), PHPsert (0.008), TrickMo (0.005), Standard Encoding (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Asymmetric Cryptography (100 neighbors, 100 edges)
           → Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (15 neighbors, 15 edges)
           → Symmetric Cryptography (188 neighbors, 188 edges)
           → Exfiltration Over Symmetric Encrypted Non-C2 Protocol (6 neighbors, 6 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
[RETRIEVE-QUOTA] Query 4/5: เข้ารหัสเพียงบางช่วงของไฟล์สลับกันเพื่อหลีกเลี่ยงการตรวจจับ...
[RETRIEVE] Query: เข้ารหัสเพียงบางช่วงของไฟล์สลับกันเพื่อหลีกเลี่ยงการตรวจจับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Encrypted/Encoded File (0.099), Obfuscated Files or Information (0.086), Selective Exclusion (0.059), APT41 (0.023), QakBot (0.019), PlugX (0.015), Data Transfer Size Limits (0.014), InvisiMole (0.008), Masquerade File Type (0.001), Compression (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Selective Exclusion (8 neighbors, 8 edges)
           → APT41 (116 neighbors, 116 edges)
           → Data Transfer Size Limits (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 5/5: ข่มขู่เปิดเผยข้อมูลลูกค้าต่อสาธารณะเพื่อบังคับให้จ่ายเงิน (Double Extortion Rans...
[RETRIEVE] Query: ข่มขู่เปิดเผยข้อมูลลูกค้าต่อสาธารณะเพื่อบังคับให้จ่ายเงิน (Double Extortion Rans...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Embargo (0.802), Storm-0501 (0.614), Akira (0.535), Medusa Ransomware (0.492), Black Basta (0.430), Embargo (0.414), Play (0.356), INC Ransom (0.206), INC Ransom (0.043), Financial Theft (0.013)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Embargo (23 neighbors, 23 edges)
           → Storm-0501 (50 neighbors, 50 edges)
           → Financial Theft (27 neighbors, 27 edges)
           → Akira (25 neighbors, 25 edges)
           → Medusa Ransomware (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [44/100] retrieved=420 relevant=3 latency=10545ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 1 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าแม้จะล้างเครื่องและติดตั้...
[RETRIEVE] Query: เมื่อวันที่ 1 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าแม้จะล้างเครื่องและติดตั้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Create or Modify System Process (0.011), MoonWind (0.005), BackConfig (0.002), Active Setup (0.001), ZxShell (0.000), APT28 (0.000), Event Triggered Execution (0.000), Network Denial of Service (0.000), Lazarus Group (0.000), Password Policies (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → MoonWind (15 neighbors, 15 edges)
           → Windows Service (150 neighbors, 150 edges)
           → BackConfig (17 neighbors, 17 edges)
           → Scheduled Task (201 neighbors, 201 edges)
[RETRIEVE-QUOTA] Query 2/6: สคริปต์ทำงานอัตโนมัติเมื่อผู้ใช้ล็อกอินเข้าระบบ (Logon Script Persistence)...
[RETRIEVE] Query: สคริปต์ทำงานอัตโนมัติเมื่อผู้ใช้ล็อกอินเข้าระบบ (Logon Script Persistence)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Logon Script (Windows) (0.991), Network Logon Script (0.947), Boot or Logon Initialization Scripts (0.935), Zebrocy (0.899), Login Hook (0.887), Attor (0.788), Cobalt Group (0.753), APT28 (0.669), RC Scripts (0.042), Persistence (0.041)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Logon Script (Windows) (12 neighbors, 12 edges)
           → Network Logon Script (6 neighbors, 6 edges)
           → Boot or Logon Initialization Scripts (19 neighbors, 19 edges)
           → Login Hook (6 neighbors, 6 edges)
           → Zebrocy (32 neighbors, 32 edges)
[RETRIEVE-QUOTA] Query 3/6: ลงทะเบียนการสมัครรับเหตุการณ์ Windows Management Instrumentation (WMI Event Subs...
[RETRIEVE] Query: ลงทะเบียนการสมัครรับเหตุการณ์ Windows Management Instrumentation (WMI Event Subs...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Management Instrumentation Event Subscription (0.862), HOPLIGHT (0.134), User Account Management (0.069), Leviathan (0.059), Windows Management Instrumentation (0.036), WMI Creation (0.030), Time Providers (0.001), Disable or Modify Windows Event Log (0.000), Windows Remote Management (0.000), Scheduled Task (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Windows Management Instrumentation Event Subscription (33 neighbors, 33 edges)
           → HOPLIGHT (23 neighbors, 23 edges)
           → User Account Management (119 neighbors, 119 edges)
           → Leviathan (68 neighbors, 68 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
[RETRIEVE-QUOTA] Query 4/6: การเรียกคำสั่งในหน่วยความจำโดยไม่มีไฟล์บนดิสก์ (Fileless Execution)...
[RETRIEVE] Query: การเรียกคำสั่งในหน่วยความจำโดยไม่มีไฟล์บนดิสก์ (Fileless Execution)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Deep Panda (0.797), Netwalker (0.360), Portable Executable Injection (0.191), Process Hollowing (0.066), Fileless Storage (0.064), PowerLess (0.043), Serverless Execution (0.041), Script Execution (0.020), User Account Management (0.009), Account Use Policies (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Deep Panda (17 neighbors, 17 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Netwalker (18 neighbors, 18 edges)
           → Portable Executable Injection (20 neighbors, 20 edges)
           → Process Hollowing (48 neighbors, 48 edges)
[RETRIEVE-QUOTA] Query 5/6: เพิ่มรายการในทะเบียนระบบ (Registry Run Key) เพื่อให้โปรแกรมทำงานเมื่อเปิดเครื่อง...
[RETRIEVE] Query: เพิ่มรายการในทะเบียนระบบ (Registry Run Key) เพื่อให้โปรแกรมทำงานเมื่อเปิดเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.899), Ursnif (0.646), RunningRAT (0.463), Lucifer (0.182), Active Setup (0.135), Boot or Logon Autostart Execution (0.111), Reg (0.007), Windows Registry Key Access (0.007), Services Registry Permissions Weakness (0.004), Keychain (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → Ursnif (36 neighbors, 36 edges)
           → RunningRAT (10 neighbors, 10 edges)
           → Lucifer (24 neighbors, 24 edges)
           → Active Setup (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 6/6: เพิ่มไฟล์ในโฟลเดอร์เริ่มต้นระบบ (Startup Folder Persistence) เพื่อให้โปรแกรมทำงา...
[RETRIEVE] Query: เพิ่มไฟล์ในโฟลเดอร์เริ่มต้นระบบ (Startup Folder Persistence) เพื่อให้โปรแกรมทำงา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.900), PLAINTEE (0.610), Pupy (0.591), Cardinal RAT (0.483), Startup Items (0.471), PowerSploit (0.240), Persistence (0.035), Launch Daemon (0.015), Re-opened Applications (0.008), Clear Persistence (0.005)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → PLAINTEE (10 neighbors, 10 edges)
           → Pupy (43 neighbors, 43 edges)
           → Startup Items (7 neighbors, 7 edges)
           → Cardinal RAT (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [45/100] retrieved=359 relevant=3 latency=13724ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 23 มิถุนายน 2565 บริษัทเทคโนโลยีแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายขอ...
[RETRIEVE] Query: เมื่อวันที่ 23 มิถุนายน 2565 บริษัทเทคโนโลยีแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QUADAGENT (0.135), Confucius (0.108), BackConfig (0.010), Scheduled Task/Job (0.006), schtasks (0.004), Seth-Locker (0.003), schtasks (0.002), Scheduled Task (0.002), Scheduled Transfer (0.000), Masquerade Task or Service (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → QUADAGENT (18 neighbors, 18 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Confucius (22 neighbors, 22 edges)
           → BackConfig (17 neighbors, 17 edges)
           → Scheduled Task/Job (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 2/6: โปรแกรมควบคุมระยะไกล (Remote Access Trojan) ฝังในเครื่องแม่ข่าย...
[RETRIEVE] Query: โปรแกรมควบคุมระยะไกล (Remote Access Trojan) ฝังในเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MarkiRAT (0.730), JSS Loader (0.397), BBSRAT (0.343), SLOTHFULMEDIA (0.293), HiddenWasp (0.239), FIN7 (0.069), Cannon (0.008), NGLite (0.003), RDFSNIFFER (0.001), Zeroaccess (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → MarkiRAT (23 neighbors, 23 edges)
           → JSS Loader (8 neighbors, 8 edges)
           → BBSRAT (14 neighbors, 14 edges)
           → SLOTHFULMEDIA (24 neighbors, 24 edges)
           → HiddenWasp (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 3/6: สร้าง Scheduled Task ปลอมชื่องานปรับปรุงเซสชันวินโดวส์เพื่อคงการทำงานซ้ำทุกชั่วโ...
[RETRIEVE] Query: สร้าง Scheduled Task ปลอมชื่องานปรับปรุงเซสชันวินโดวส์เพื่อคงการทำงานซ้ำทุกชั่วโ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Disco (0.540), SVCReady (0.376), Masquerade Task or Service (0.261), Confucius (0.091), Scheduled Task/Job (0.063), schtasks (0.043), Scheduled Task (0.037), schtasks (0.023), Scheduled Job Modification (0.003), Scheduled Job Metadata (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Disco (6 neighbors, 6 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → SVCReady (24 neighbors, 24 edges)
           → Masquerade Task or Service (94 neighbors, 94 edges)
           → Confucius (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 4/6: ใช้เครื่องแม่ข่ายเป็นจุดพักส่งต่อ (pivot point) เข้าถึงเครื่องอื่นในเครือข่าย...
[RETRIEVE] Query: ใช้เครื่องแม่ข่ายเป็นจุดพักส่งต่อ (pivot point) เข้าถึงเครื่องอื่นในเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Wi-Fi Networks (0.016), SDBbot (0.006), Network Boundary Bridging (0.002), Filter Network Traffic (0.002), Ping (0.001), Cardinal RAT (0.001), Cardinal RAT (0.001), Business Relationships (0.000), Identify Roles (0.000), Gather Victim Org Information (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Wi-Fi Networks (7 neighbors, 7 edges)
           → SDBbot (25 neighbors, 25 edges)
           → Proxy (84 neighbors, 84 edges)
           → Network Boundary Bridging (9 neighbors, 9 edges)
           → Filter Network Traffic (49 neighbors, 49 edges)
[RETRIEVE-QUOTA] Query 5/6: กระโดดข้ามเครื่องเพื่อเจาะลึกเข้าไปในเครือข่ายภายใน (lateral movement)...
[RETRIEVE] Query: กระโดดข้ามเครื่องเพื่อเจาะลึกเข้าไปในเครือข่ายภายใน (lateral movement)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lateral Movement (0.216), Exploitation of Remote Services (0.149), Net (0.037), Lateral Tool Transfer (0.025), APT28 (0.012), SILENTTRINITY (0.010), Network Address Translation Traversal (0.009), Network Share Discovery (0.008), Network Device Authentication (0.000), Reaver (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Lateral Movement (23 neighbors, 23 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
           → Net (50 neighbors, 50 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 6/6: เข้ารหัสการติดต่อขาเข้าและขาออกด้วยกุญแจลับ 128 บิต (encryption)...
[RETRIEVE] Query: เข้ารหัสการติดต่อขาเข้าและขาออกด้วยกุญแจลับ 128 บิต (encryption)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Uroburos (0.477), BitPaymer (0.057), Encrypt Sensitive Information (0.029), Weaken Encryption (0.006), Data Encoding (0.003), Archive Collected Data (0.003), Standard Encoding (0.003), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.002), cipher.exe (0.002), Desert Scorpion (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Uroburos (37 neighbors, 37 edges)
           → Symmetric Cryptography (188 neighbors, 188 edges)
           → BitPaymer (19 neighbors, 19 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → Encrypt Sensitive Information (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [46/100] retrieved=268 relevant=3 latency=12506ms
[RETRIEVE-QUOTA] Query 1/11: เมื่อวันที่ 9 กรกฎาคม 2567 บริษัทปิโตรเคมีแห่งหนึ่งในจังหวัดระยองแจ้งความว่าเครื...
[RETRIEVE] Query: เมื่อวันที่ 9 กรกฎาคม 2567 บริษัทปิโตรเคมีแห่งหนึ่งในจังหวัดระยองแจ้งความว่าเครื...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Carbon (0.001), POWRUNER (0.000), FIN8 (0.000), Password Policy Discovery (0.000), Account Discovery (0.000), Exfiltration to Text Storage Sites (0.000), CrossRAT (0.000), Pikabot (0.000), Query Registry (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Carbon (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Account (65 neighbors, 65 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/11: โปรแกรมสำรวจข้อมูลฝังในเครื่องคอมพิวเตอร์สำนักงาน...
[RETRIEVE] Query: โปรแกรมสำรวจข้อมูลฝังในเครื่องคอมพิวเตอร์สำนักงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Babuk (0.005), sqlmap (0.003), CrackMapExec (0.003), AADInternals (0.001), Cobian RAT (0.001), Deep Panda (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Babuk (14 neighbors, 14 edges)
           → Local Storage Discovery (103 neighbors, 103 edges)
           → sqlmap (4 neighbors, 4 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → AADInternals (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 3/11: เรียกดูชื่อเครื่องของเป้าหมาย (System Information Discovery)...
[RETRIEVE] Query: เรียกดูชื่อเครื่องของเป้าหมาย (System Information Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SideTwist (0.922), Milan (0.796), System Information Discovery (0.108), SYSCON (0.046), Systeminfo (0.035), System Location Discovery (0.015), System Network Configuration Discovery (0.008), Device Driver Discovery (0.008), System Owner/User Discovery (0.006), Process Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SideTwist (16 neighbors, 16 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Milan (21 neighbors, 21 edges)
           → SYSCON (6 neighbors, 6 edges)
           → Systeminfo (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 4/11: เรียกดูชื่อบัญชีผู้ใช้ที่กำลังใช้งาน (Account Discovery)...
[RETRIEVE] Query: เรียกดูชื่อบัญชีผู้ใช้ที่กำลังใช้งาน (Account Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Owner/User Discovery (0.693), UPPERCUT (0.484), Account Discovery (0.264), HAPPYWORK (0.197), Wi-Fi Discovery (0.044), Cloud Account (0.024), OSInfo (0.002), TAINTEDSCRIBE (0.002), System Network Connections Discovery (0.001), Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → UPPERCUT (18 neighbors, 18 edges)
           → Account Discovery (18 neighbors, 18 edges)
           → HAPPYWORK (4 neighbors, 4 edges)
           → Wi-Fi Discovery (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 5/11: เรียกดูชื่อเครื่องเป้าหมายอีกเครื่องเพื่อยืนยันตำแหน่ง (System Information Disco...
[RETRIEVE] Query: เรียกดูชื่อเครื่องเป้าหมายอีกเครื่องเพื่อยืนยันตำแหน่ง (System Information Disco...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SodaMaster (0.428), System Location Discovery (0.154), WellMess (0.133), FunnyDream (0.106), STARWHALE (0.085), System Information Discovery (0.081), Remote System Discovery (0.064), System Owner/User Discovery (0.007), Device Driver Discovery (0.005), Virtual Machine Discovery (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SodaMaster (12 neighbors, 12 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → System Location Discovery (29 neighbors, 29 edges)
           → WellMess (16 neighbors, 16 edges)
           → FunnyDream (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 6/11: เรียกดูรายละเอียดการตั้งค่าเครือข่าย ไอพี เกตเวย์ และเซิร์ฟเวอร์ DNS (Network Co...
[RETRIEVE] Query: เรียกดูรายละเอียดการตั้งค่าเครือข่าย ไอพี เกตเวย์ และเซิร์ฟเวอร์ DNS (Network Co...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ipconfig (0.729), ifconfig (0.724), System Network Configuration Discovery (0.526), ipconfig (0.368), DEADEYE (0.315), CrackMapExec (0.308), Network Service Discovery (0.013), System Network Connections Discovery (0.008), Operating System Configuration (0.002), Data from Configuration Repository (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → ipconfig (16 neighbors, 16 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → ifconfig (1 neighbors, 1 edges)
           → DEADEYE (13 neighbors, 13 edges)
           → CrackMapExec (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 7/11: ใช้คำสั่งระบบแจกแจงรายชื่อบัญชีผู้ใช้ทั้งหมดในโดเมน (Domain Account Enumeration)...
[RETRIEVE] Query: ใช้คำสั่งระบบแจกแจงรายชื่อบัญชีผู้ใช้ทั้งหมดในโดเมน (Domain Account Enumeration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.776), Domain Account (0.527), DUSTTRAP (0.386), Domain Account (0.057), Security Account Manager (0.052), User Account Management (0.020), Operating System Configuration (0.009), Firewall Enumeration (0.002), Instance Enumeration (0.002), Cloud Storage Enumeration (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → DUSTTRAP (31 neighbors, 31 edges)
           → Domain Account (18 neighbors, 18 edges)
           → Security Account Manager (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 8/11: แจกแจงรายชื่อกลุ่มสิทธิ์ในโดเมน (Domain Group Enumeration)...
[RETRIEVE] Query: แจกแจงรายชื่อกลุ่มสิทธิ์ในโดเมน (Domain Group Enumeration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.700), Domain Groups (0.272), Group Enumeration (0.140), Latrodectus (0.137), Domain Account (0.136), Volume Enumeration (0.008), Instance Enumeration (0.008), Operating System Configuration (0.007), Cloud Storage Enumeration (0.004), Firewall Enumeration (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Group Enumeration (0 neighbors, 0 edges)
           → Latrodectus (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] Query 9/11: เจาะจงดูสมาชิกของกลุ่มผู้ดูแลโดเมน (Domain Admin Group Membership Discovery)...
[RETRIEVE] Query: เจาะจงดูสมาชิกของกลุ่มผู้ดูแลโดเมน (Domain Admin Group Membership Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain Groups (0.689), BADHATCH (0.488), Turla (0.308), Group Metadata (0.146), Group Policy Discovery (0.119), Domain Account (0.077), System Owner/User Discovery (0.043), Scattered Spider (0.032), Group Enumeration (0.021), Group Modification (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Domain Groups (41 neighbors, 41 edges)
           → BADHATCH (36 neighbors, 36 edges)
           → Turla (98 neighbors, 98 edges)
           → Group Metadata (0 neighbors, 0 edges)
           → Group Policy Discovery (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 10/11: เจาะจงดูสมาชิกของกลุ่มที่ดูแลระบบจดหมายอิเล็กทรอนิกส์ (Email Admin Group Members...
[RETRIEVE] Query: เจาะจงดูสมาชิกของกลุ่มที่ดูแลระบบจดหมายอิเล็กทรอนิกส์ (Email Admin Group Members...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Permission Groups Discovery (0.049), System Owner/User Discovery (0.026), Scattered Spider (0.016), Domain Groups (0.007), Group Policy Discovery (0.004), Group Metadata (0.002), OSInfo (0.002), BADHATCH (0.001), Group Modification (0.001), Domain Account (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Permission Groups Discovery (18 neighbors, 18 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Scattered Spider (76 neighbors, 76 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → Group Policy Discovery (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 11/11: เรียกดูนโยบายการตั้งรหัสผ่านของโดเมน (Domain Password Policy Discovery)...
[RETRIEVE] Query: เรียกดูนโยบายการตั้งรหัสผ่านของโดเมน (Domain Password Policy Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PoshC2 (0.910), Net (0.877), Password Policies (0.861), Group Policy Preferences (0.392), Password Policy Discovery (0.360), CrackMapExec (0.293), Group Policy Discovery (0.047), Domain Trust Discovery (0.046), System Owner/User Discovery (0.001), Wi-Fi Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PoshC2 (35 neighbors, 35 edges)
           → Password Policy Discovery (11 neighbors, 11 edges)
           → Net (50 neighbors, 50 edges)
           → Password Policies (47 neighbors, 47 edges)
           → Group Policy Preferences (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 11 queries
  [47/100] retrieved=481 relevant=6 latency=21101ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 20 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความว่าเจ้า...
[RETRIEVE] Query: เมื่อวันที่ 20 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความว่าเจ้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA2541 (0.017), POWERSTATS (0.014), POWERSOURCE (0.007), POWERSTATS (0.007), POWRUNER (0.003), POWERSOURCE (0.002), PowerShell (0.001), PowerShell Profile (0.000), Disable or Remove Feature or Program (0.000), ZxShell (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → TA2541 (37 neighbors, 37 edges)
           → PowerShell (241 neighbors, 241 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → POWERSOURCE (7 neighbors, 7 edges)
           → NTFS File Attributes (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 2/7: ไฟล์แนบที่ใช้อักขระพิเศษ Right-to-Left Override (RLO) เพื่อปลอมแปลงนามสกุลไฟล์...
[RETRIEVE] Query: ไฟล์แนบที่ใช้อักขระพิเศษ Right-to-Left Override (RLO) เพื่อปลอมแปลงนามสกุลไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BlackTech (0.931), Ke3chang (0.928), Scarlet Mimic (0.903), Right-to-Left Override (0.808), BRONZE BUTLER (0.161), Masquerade File Type (0.035), Space after Filename (0.006), CLAIMLOADER (0.002), ftp (0.001), Dridex (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Right-to-Left Override (7 neighbors, 7 edges)
           → BlackTech (20 neighbors, 20 edges)
           → Ke3chang (58 neighbors, 58 edges)
           → Scarlet Mimic (5 neighbors, 5 edges)
           → BRONZE BUTLER (54 neighbors, 54 edges)
[RETRIEVE-QUOTA] Query 3/7: เปิดไฟล์ที่ปลอมแปลงนามสกุลเพื่อให้ PowerShell ทำงาน...
[RETRIEVE] Query: เปิดไฟล์ที่ปลอมแปลงนามสกุลเพื่อให้ PowerShell ทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gorgon Group (0.628), POWERSOURCE (0.085), POWERSOURCE (0.016), Invoke-PSImage (0.004), PowerSploit (0.002), PowerShell (0.001), PowerShell Profile (0.001), POWERSTATS (0.001), POWERSTATS (0.000), Disable or Remove Feature or Program (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Gorgon Group (20 neighbors, 20 edges)
           → PowerShell (241 neighbors, 241 edges)
           → POWERSOURCE (7 neighbors, 7 edges)
           → NTFS File Attributes (19 neighbors, 19 edges)
           → Invoke-PSImage (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] Query 4/7: เรียกใช้ PowerShell จากหน้าต่างคำสั่งของระบบ...
[RETRIEVE] Query: เรียกใช้ PowerShell จากหน้าต่างคำสั่งของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerShell (0.353), PowerExchange (0.197), Disable or Remove Feature or Program (0.171), POWRUNER (0.070), CreepySnail (0.035), POWERSTATS (0.014), PowerShell Profile (0.010), POWERSOURCE (0.006), Invoke-PSImage (0.004), POWERSTATS (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PowerShell (241 neighbors, 241 edges)
           → PowerExchange (6 neighbors, 6 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → CreepySnail (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 5/7: สคริปต์ไล่เก็บรวบรวมไฟล์ตามนามสกุลที่กำหนด...
[RETRIEVE] Query: สคริปต์ไล่เก็บรวบรวมไฟล์ตามนามสกุลที่กำหนด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: StrongPity (0.081), T9000 (0.037), Automated Collection (0.035), WindTail (0.025), Forfiles (0.011), Pupy (0.003), ListPlanting (0.001), Path Interception by Search Order Hijacking (0.001), Dylib Hijacking (0.001), Change Default File Association (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → StrongPity (28 neighbors, 28 edges)
           → Automated Collection (77 neighbors, 77 edges)
           → T9000 (13 neighbors, 13 edges)
           → WindTail (16 neighbors, 16 edges)
           → Forfiles (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/7: บีบอัดไฟล์ที่รวบรวมไว้เป็นไฟล์เดียว...
[RETRIEVE] Query: บีบอัดไฟล์ที่รวบรวมไว้เป็นไฟล์เดียว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Compression (0.234), Ramsay (0.155), Archive via Library (0.037), SampleCheck5000 (0.021), Remote Data Staging (0.018), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Compression (38 neighbors, 38 edges)
           → Ramsay (39 neighbors, 39 edges)
           → Archive via Utility (88 neighbors, 88 edges)
           → Archive via Library (18 neighbors, 18 edges)
           → Remote Data Staging (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 7/7: เตรียมส่งออกไฟล์บีบอัดที่มีข้อมูลที่ถูกเก็บรวบรวม...
[RETRIEVE] Query: เตรียมส่งออกไฟล์บีบอัดที่มีข้อมูลที่ถูกเก็บรวบรวม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Staged (0.024), Spica (0.016), BBSRAT (0.014), Archive Collected Data (0.011), Remote Data Staging (0.005), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), The White Company (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Data Staged (13 neighbors, 13 edges)
           → Spica (10 neighbors, 10 edges)
           → Archive Collected Data (62 neighbors, 62 edges)
           → BBSRAT (14 neighbors, 14 edges)
           → Archive via Library (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [48/100] retrieved=351 relevant=3 latency=13072ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 6 มิถุนายน 2567 บริษัทมหาชนแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของ...
[RETRIEVE] Query: เมื่อวันที่ 6 มิถุนายน 2567 บริษัทมหาชนแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Net Crawler (0.000), WannaCry (0.000), FIN8 (0.000), Darkhotel (0.000), EvilGrab (0.000), Lokibot (0.000), Password Policy Discovery (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → WannaCry (17 neighbors, 17 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Net Crawler (5 neighbors, 5 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/7: Phishing หรือ Initial Access ที่ทำให้ได้สิทธิ์เข้าถึงเครื่องคอมพิวเตอร์ผู้บริหาร...
[RETRIEVE] Query: Phishing หรือ Initial Access ที่ทำให้ได้สิทธิ์เข้าถึงเครื่องคอมพิวเตอร์ผู้บริหาร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Initial Access (0.089), DocSwap (0.081), Kimsuky (0.070), Phishing (0.022), Phishing for Information (0.004), Audit (0.003), Spearphishing Attachment (0.001), Spearphishing Link (0.001), BITTER (0.001), Written Content (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Initial Access (22 neighbors, 22 edges)
           → DocSwap (27 neighbors, 27 edges)
           → Phishing (20 neighbors, 20 edges)
           → Kimsuky (150 neighbors, 150 edges)
           → Phishing (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 3/7: เพิ่มสคริปต์ลงในทะเบียนระบบ (Registry) เพื่อให้ทำงานอัตโนมัติเมื่อล็อกอิน (Logon...
[RETRIEVE] Query: เพิ่มสคริปต์ลงในทะเบียนระบบ (Registry) เพื่อให้ทำงานอัตโนมัติเมื่อล็อกอิน (Logon...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Logon Script (Windows) (0.968), Zebrocy (0.922), Attor (0.900), JHUHUGIT (0.757), Network Logon Script (0.480), Cobalt Group (0.460), Boot or Logon Initialization Scripts (0.325), Login Hook (0.232), RC Scripts (0.020), Persistence (0.011)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Logon Script (Windows) (12 neighbors, 12 edges)
           → Zebrocy (32 neighbors, 32 edges)
           → Attor (35 neighbors, 35 edges)
           → JHUHUGIT (21 neighbors, 21 edges)
           → Network Logon Script (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 4/7: อัปโหลดและรันโปรแกรมดักบันทึกแป้นพิมพ์ (Keylogger) ภายใต้สิทธิ์ผู้บริหาร...
[RETRIEVE] Query: อัปโหลดและรันโปรแกรมดักบันทึกแป้นพิมพ์ (Keylogger) ภายใต้สิทธิ์ผู้บริหาร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PAKLOG (0.093), CorKLOG (0.049), KeyBoy (0.039), WarzoneRAT (0.013), PAKLOG (0.011), Wevtutil (0.007), Keylogging (0.003), Winlogon Helper DLL (0.001), Limit Software Installation (0.001), Multi-Factor Authentication Interception (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PAKLOG (11 neighbors, 11 edges)
           → CorKLOG (9 neighbors, 9 edges)
           → KeyBoy (19 neighbors, 19 edges)
           → Keylogging (160 neighbors, 160 edges)
           → WarzoneRAT (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 5/7: อ่านไฟล์ผลลัพธ์จากโปรแกรมดักบันทึกแป้นพิมพ์...
[RETRIEVE] Query: อ่านไฟล์ผลลัพธ์จากโปรแกรมดักบันทึกแป้นพิมพ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MacMa (0.019), PACEMAKER (0.002), gsecdump (0.002), Fgdump (0.001), Cachedump (0.001), Hornbill (0.001), Clipboard Data (0.001), Wevtutil (0.001), POWRUNER (0.000), Process Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → MacMa (28 neighbors, 28 edges)
           → Keylogging (160 neighbors, 160 edges)
           → PACEMAKER (7 neighbors, 7 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → gsecdump (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 6/7: อัปโหลดและรันโปรแกรมดึงข้อมูลรหัสผ่านจากเบราว์เซอร์ (Credential Dumping from Bro...
[RETRIEVE] Query: อัปโหลดและรันโปรแกรมดึงข้อมูลรหัสผ่านจากเบราว์เซอร์ (Credential Dumping from Bro...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Zebrocy (0.970), gsecdump (0.716), Mimikatz (0.679), Windows Credential Editor (0.676), pwdump (0.557), OilRig (0.354), OS Credential Dumping (0.231), Credentials from Web Browsers (0.128), Credential Access Protection (0.038), Windows Credential Manager (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Zebrocy (32 neighbors, 32 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → Mimikatz (77 neighbors, 77 edges)
           → gsecdump (8 neighbors, 8 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 7/7: ลบไฟล์ที่เกี่ยวข้องในโฟลเดอร์ไฟล์ชั่วคราว (Temporary Files Deletion)...
[RETRIEVE] Query: ลบไฟล์ที่เกี่ยวข้องในโฟลเดอร์ไฟล์ชั่วคราว (Temporary Files Deletion)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VBShower (0.562), Sakula (0.554), File Deletion (0.034), Hi-Zor (0.016), Forfiles (0.011), Restrict File and Directory Permissions (0.004), Malicious File (0.004), Hidden File System (0.003), Disable or Remove Feature or Program (0.003), Encrypted/Encoded File (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → VBShower (6 neighbors, 6 edges)
           → File Deletion (310 neighbors, 310 edges)
           → Sakula (12 neighbors, 12 edges)
           → Hi-Zor (9 neighbors, 9 edges)
           → Forfiles (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [49/100] retrieved=183 relevant=4 latency=14593ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 2 มิถุนายน 2566 บริษัทแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Query: เมื่อวันที่ 2 มิถุนายน 2566 บริษัทแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Duqu (0.040), APT-C-36 (0.038), Pasam (0.025), Ursnif (0.021), APT-C-36 (0.007), Internal Spearphishing (0.000), Lateral Tool Transfer (0.000), System Script Proxy Execution (0.000), Social Engineering (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Duqu (21 neighbors, 21 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Pasam (9 neighbors, 9 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมไม่พึงประสงค์ติดตั้งบนเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Query: โปรแกรมไม่พึงประสงค์ติดตั้งบนเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: EvilGrab (0.150), Limit Software Installation (0.141), Escobar (0.024), Ke3chang (0.017), Disable or Remove Feature or Program (0.006), Cobian RAT (0.005), Cardinal RAT (0.001), CrossRAT (0.001), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Limit Software Installation (17 neighbors, 17 edges)
           → EvilGrab (6 neighbors, 6 edges)
           → Escobar (16 neighbors, 16 edges)
           → Uninstall Malicious Application (12 neighbors, 12 edges)
           → Ke3chang (58 neighbors, 58 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
[RETRIEVE-QUOTA] Query 3/8: Backdoor ฝังตัวในโปรแกรมเพื่อรับคำสั่งจากคนร้าย...
[RETRIEVE] Query: Backdoor ฝังตัวในโปรแกรมเพื่อรับคำสั่งจากคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AutoIt backdoor (0.038), ServHelper (0.025), Heyoka Backdoor (0.017), BPFDoor (0.013), RARSTONE (0.011), Heyoka Backdoor (0.010), Heyoka Backdoor (0.009), Backdoor.Oldrea (0.007), BackdoorDiplomacy (0.001), Nightdoor (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → AutoIt backdoor (6 neighbors, 6 edges)
           → ServHelper (16 neighbors, 16 edges)
           → Heyoka Backdoor (16 neighbors, 16 edges)
           → Malicious File (202 neighbors, 202 edges)
           → RARSTONE (5 neighbors, 5 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 4/8: Remote Access Trojan เก็บรวบรวมข้อมูลเครื่องและติดต่อกลับเซิร์ฟเวอร์คนร้าย...
[RETRIEVE] Query: Remote Access Trojan เก็บรวบรวมข้อมูลเครื่องและติดต่อกลับเซิร์ฟเวอร์คนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: JSS Loader (0.150), SLOTHFULMEDIA (0.145), OopsIE (0.026), HiddenWasp (0.010), RogueRobin (0.009), Catchamas (0.008), APT38 (0.005), Zeroaccess (0.005), RCSession (0.003), Cannon (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → JSS Loader (8 neighbors, 8 edges)
           → SLOTHFULMEDIA (24 neighbors, 24 edges)
           → OopsIE (20 neighbors, 20 edges)
           → RogueRobin (19 neighbors, 19 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] Query 5/8: ดาวน์โหลดและติดตั้งส่วนประกอบเพิ่มเติมของโปรแกรมอันตราย...
[RETRIEVE] Query: ดาวน์โหลดและติดตั้งส่วนประกอบเพิ่มเติมของโปรแกรมอันตราย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AbstractEmu (0.741), Software Extensions (0.160), BadPatch (0.151), SoreFang (0.027), Malicious Library (0.021), Browser Extensions (0.013), Visual Basic (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AbstractEmu (23 neighbors, 23 edges)
           → Download New Code at Runtime (42 neighbors, 42 edges)
           → Software Extensions (9 neighbors, 9 edges)
           → BadPatch (12 neighbors, 12 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 6/8: แพร่กระจายโปรแกรมไปยังเครื่องอื่นโดยใช้ช่องโหว่...
[RETRIEVE] Query: แพร่กระจายโปรแกรมไปยังเครื่องอื่นโดยใช้ช่องโหว่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NotPetya (0.025), Ingress Tool Transfer (0.025), PsExec (0.022), BlackByte Ransomware (0.022), Taint Shared Content (0.015), Lateral Tool Transfer (0.010), CrossRAT (0.005), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → NotPetya (15 neighbors, 15 edges)
           → Service Execution (78 neighbors, 78 edges)
           → BlackByte Ransomware (22 neighbors, 22 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 7/8: คัดลอกสำเนาโปรแกรมไปยังสื่อบันทึกแบบถอดได้...
[RETRIEVE] Query: คัดลอกสำเนาโปรแกรมไปยังสื่อบันทึกแบบถอดได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: USBferry (0.442), Rover (0.168), Clipboard Data (0.008), PsExec (0.003), Cherry Picker (0.002), xCmd (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → USBferry (12 neighbors, 12 edges)
           → Replication Through Removable Media (35 neighbors, 35 edges)
           → Rover (10 neighbors, 10 edges)
           → Local Data Staging (138 neighbors, 138 edges)
           → Clipboard Data (48 neighbors, 48 edges)
[RETRIEVE-QUOTA] Query 8/8: คัดลอกสำเนาโปรแกรมไปยังโฟลเดอร์ที่เปิดแบ่งปันบนเครือข่าย...
[RETRIEVE] Query: คัดลอกสำเนาโปรแกรมไปยังโฟลเดอร์ที่เปิดแบ่งปันบนเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.082), Taint Shared Content (0.049), APT32 (0.020), Network Share Discovery (0.019), Lateral Tool Transfer (0.012), SMB/Windows Admin Shares (0.003), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Taint Shared Content (18 neighbors, 18 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
           → APT32 (93 neighbors, 93 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [50/100] retrieved=448 relevant=3 latency=14738ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 12 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าจดหมายอิเล็กทรอนิก...
[RETRIEVE] Query: เมื่อวันที่ 12 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าจดหมายอิเล็กทรอนิก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackdoorDiplomacy (0.008), APT-C-36 (0.004), Ursnif (0.001), XLoader (0.001), APT-C-36 (0.001), AADInternals (0.000), System Script Proxy Execution (0.000), File Deletion (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BackdoorDiplomacy (20 neighbors, 20 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Ursnif (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 2/5: โปรแกรมฝังตัวบนเครื่องที่ยึดครองดาวน์โหลดไฟล์โปรแกรมหลัก ไฟล์ประกอบ สคริปต์ติดตั...
[RETRIEVE] Query: โปรแกรมฝังตัวบนเครื่องที่ยึดครองดาวน์โหลดไฟล์โปรแกรมหลัก ไฟล์ประกอบ สคริปต์ติดตั...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Embedded Payloads (0.027), Installer Packages (0.004), System Script Proxy Execution (0.002), cmd (0.002), Local Email Collection (0.001), Cerberus (0.001), TYPEFRAME (0.001), TYPEFRAME (0.001), Change Default File Association (0.000), File Deletion (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Embedded Payloads (27 neighbors, 27 edges)
           → Installer Packages (8 neighbors, 8 edges)
           → System Script Proxy Execution (4 neighbors, 4 edges)
           → Local Email Collection (25 neighbors, 25 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 3/5: คนร้ายสวมสิทธิ์ประจำตัวของผู้ดูแลโดเมนเพื่อคัดลอกไฟล์จากเครื่องที่ยึดครองไปยังเค...
[RETRIEVE] Query: คนร้ายสวมสิทธิ์ประจำตัวของผู้ดูแลโดเมนเพื่อคัดลอกไฟล์จากเครื่องที่ยึดครองไปยังเค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cinnamon Tempest (0.067), Domains (0.038), Domain Accounts (0.012), POWRUNER (0.003), Domains (0.002), Domain Controller Authentication (0.002), CreepySnail (0.002), Email Accounts (0.001), APT29 (0.001), Net Crawler (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Cinnamon Tempest (27 neighbors, 27 edges)
           → Domain Accounts (47 neighbors, 47 edges)
           → Domains (15 neighbors, 15 edges)
           → Domains (65 neighbors, 65 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 4/5: ติดตั้งโปรแกรมบนเครื่องแม่ข่ายจดหมายจากระยะไกลเพื่อแทรกอยู่ในขั้นตอนรับส่งจดหมาย...
[RETRIEVE] Query: ติดตั้งโปรแกรมบนเครื่องแม่ข่ายจดหมายจากระยะไกลเพื่อแทรกอยู่ในขั้นตอนรับส่งจดหมาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CARROTBALL (0.048), RemoteUtilities (0.008), Mail Protocols (0.007), IPsec Helper (0.004), RemoteCMD (0.003), Impacket (0.003), cmd (0.001), Portable Executable Injection (0.001), cmd (0.001), Asynchronous Procedure Call (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CARROTBALL (4 neighbors, 4 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Mail Protocols (31 neighbors, 31 edges)
           → RemoteUtilities (5 neighbors, 5 edges)
           → Msiexec (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 5/5: ลักลอบอ่านและส่งต่อจดหมายอิเล็กทรอนิกส์ของผู้บริหารออกไปภายนอก...
[RETRIEVE] Query: ลักลอบอ่านและส่งต่อจดหมายอิเล็กทรอนิกส์ของผู้บริหารออกไปภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA505 (0.014), Email Forwarding Rule (0.010), XLoader (0.008), APT1 (0.006), Rover (0.003), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → TA505 (50 neighbors, 50 edges)
           → Email Account (17 neighbors, 17 edges)
           → Email Forwarding Rule (12 neighbors, 12 edges)
           → XLoader (28 neighbors, 28 edges)
           → APT1 (40 neighbors, 40 edges)
           → Remote Email Collection (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [51/100] retrieved=621 relevant=3 latency=10364ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 8 พฤษภาคม 2567 ผู้ให้บริการโครงข่ายแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่า...
[RETRIEVE] Query: เมื่อวันที่ 8 พฤษภาคม 2567 ผู้ให้บริการโครงข่ายแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dragonfly (0.001), LAPSUS$ (0.001), System Time Discovery (0.000), FIN8 (0.000), AppInit DLLs (0.000), Lokibot (0.000), Scheduled Task/Job (0.000), Password Policy Discovery (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Dragonfly (66 neighbors, 66 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
           → Password Managers (20 neighbors, 20 edges)
           → System Time Discovery (100 neighbors, 100 edges)
[RETRIEVE-QUOTA] Query 2/6: เพิ่มรายการงานตั้งเวลา (Cron Job) ในตารางเวลาของเครื่องแม่ข่ายลินุกซ์เพื่อให้โปร...
[RETRIEVE] Query: เพิ่มรายการงานตั้งเวลา (Cron Job) ในตารางเวลาของเครื่องแม่ข่ายลินุกซ์เพื่อให้โปร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT38 (0.732), Cron (0.418), Systemd Timers (0.296), Penquin (0.190), Container Orchestration Job (0.081), Scheduled Job Modification (0.001), Operation Dream Job (0.000), Operation Dream Job (0.000), Electron Applications (0.000), Operation Dream Job (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT38 (62 neighbors, 62 edges)
           → Cron (25 neighbors, 25 edges)
           → Systemd Timers (10 neighbors, 10 edges)
           → Penquin (19 neighbors, 19 edges)
           → Container Orchestration Job (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 3/6: สร้างหน่วยบริการเบื้องหลัง (Systemd Service) เพื่อให้โปรแกรมทำงานเองทุกครั้งที่เ...
[RETRIEVE] Query: สร้างหน่วยบริการเบื้องหลัง (Systemd Service) เพื่อให้โปรแกรมทำงานเองทุกครั้งที่เ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Systemd Service (0.345), Create or Modify System Process (0.126), Windows Service (0.115), Ursnif (0.113), Boot or Logon Autostart Execution (0.072), Systemctl (0.035), Fysbis (0.011), Systemd Timers (0.004), System Service Discovery (0.002), Service Creation (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Systemd Service (22 neighbors, 22 edges)
           → Create or Modify System Process (25 neighbors, 25 edges)
           → Windows Service (150 neighbors, 150 edges)
           → Ursnif (36 neighbors, 36 edges)
           → Boot or Logon Autostart Execution (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 4/6: เปิดอ่านไฟล์รหัสผ่านของบัญชีผู้ใช้ (Shadow File / /etc/shadow)...
[RETRIEVE] Query: เปิดอ่านไฟล์รหัสผ่านของบัญชีผู้ใช้ (Shadow File / /etc/shadow)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: /etc/passwd and /etc/shadow (0.879), LaZagne (0.685), ShadowRay (0.353), Password Policies (0.225), Empire (0.022), ShadowPad (0.002), SSH (0.001), cipher.exe (0.001), WINDSHIELD (0.000), Rogue Domain Controller (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → /etc/passwd and /etc/shadow (7 neighbors, 7 edges)
           → LaZagne (22 neighbors, 22 edges)
           → ShadowRay (10 neighbors, 10 edges)
           → Password Policies (47 neighbors, 47 edges)
           → Empire (91 neighbors, 91 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 5/6: เปิดอ่านไฟล์ประวัติคำสั่ง (Bash History / Command History)...
[RETRIEVE] Query: เปิดอ่านไฟล์ประวัติคำสั่ง (Bash History / Command History)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Shell History (0.827), Prevent Command History Logging (0.665), Operating System Configuration (0.606), Clear Command History (0.397), Operating System Configuration (0.150), Aquatic Panda (0.009), VIRTUALPITA (0.009), Command and Scripting Interpreter (0.001), Command Obfuscation (0.001), Cloud Service Dashboard (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Shell History (5 neighbors, 5 edges)
           → Prevent Command History Logging (15 neighbors, 15 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → Unsecured Credentials (27 neighbors, 27 edges)
           → Clear Command History (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 6/6: เปิดอ่านไฟล์กุญแจสำหรับเชื่อมต่อระยะไกล (SSH Private Keys)...
[RETRIEVE] Query: เปิดอ่านไฟล์กุญแจสำหรับเชื่อมต่อระยะไกล (SSH Private Keys)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Private Keys (0.504), XCSSET (0.444), Operation Digital Eye (0.431), SSH Authorized Keys (0.282), Restrict File and Directory Permissions (0.074), Rocke (0.031), SSH (0.020), SSH Hijacking (0.014), TruffleHog (0.002), Kessel (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Private Keys (26 neighbors, 26 edges)
           → XCSSET (33 neighbors, 33 edges)
           → SSH Authorized Keys (15 neighbors, 15 edges)
           → Operation Digital Eye (26 neighbors, 26 edges)
           → Restrict File and Directory Permissions (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [52/100] retrieved=399 relevant=4 latency=12491ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 12 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Query: เมื่อวันที่ 12 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DCHSpy (0.001), Exploit Public-Facing Application (0.001), Cardinal RAT (0.000), Ingress Tool Transfer (0.000), Exploitation for Client Execution (0.000), ThiefQuest (0.000), OwaAuth (0.000), Wevtutil (0.000), Clear Linux or Mac System Logs (0.000), Clear Windows Event Logs (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DCHSpy (13 neighbors, 13 edges)
           → Call Log (44 neighbors, 44 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Cardinal RAT (22 neighbors, 22 edges)
           → Keylogging (160 neighbors, 160 edges)
[RETRIEVE-QUOTA] Query 2/6: Exploit ช่องโหว่ซอฟต์แวร์บนเครื่องแม่ข่ายบริหารจัดการอุปกรณ์ปลายทาง...
[RETRIEVE] Query: Exploit ช่องโหว่ซอฟต์แวร์บนเครื่องแม่ข่ายบริหารจัดการอุปกรณ์ปลายทาง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.112), Exploitation for Client Execution (0.040), Exploit Protection (0.035), Exploit Protection (0.022), SpeakUp (0.015), Exploit Protection (0.015), Exploit Protection (0.013), Exploits (0.007), Explosive (0.007), Exploits (0.006)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Exploitation for Client Execution (65 neighbors, 65 edges)
           → Exploit Protection (12 neighbors, 12 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
           → SpeakUp (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 3/6: ดาวน์โหลดไฟล์สคริปต์อันตรายจากเว็บไซต์ภายนอก...
[RETRIEVE] Query: ดาวน์โหลดไฟล์สคริปต์อันตรายจากเว็บไซต์ภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TRANSLATEXT (0.039), OopsIE (0.032), NICECURL (0.021), LNK Icon Smuggling (0.020), Sliver (0.018), ccf32 (0.006), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → TRANSLATEXT (16 neighbors, 16 edges)
           → OopsIE (20 neighbors, 20 edges)
           → LNK Icon Smuggling (8 neighbors, 8 edges)
           → Sliver (27 neighbors, 27 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
[RETRIEVE-QUOTA] Query 4/6: สั่งให้สคริปต์อันตรายทำงานบนเครื่องแม่ข่าย...
[RETRIEVE] Query: สั่งให้สคริปต์อันตรายทำงานบนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Poisoned Pipeline Execution (0.057), Asynchronous Procedure Call (0.012), NETEAGLE (0.009), Indirect Command Execution (0.003), BlackCat (0.002), Cardinal RAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Poisoned Pipeline Execution (5 neighbors, 5 edges)
           → Asynchronous Procedure Call (18 neighbors, 18 edges)
           → NETEAGLE (12 neighbors, 12 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Indirect Command Execution (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 5/6: Exploit ช่องโหว่เพิ่มเติมเพื่อยกระดับสิทธิ์เป็นสิทธิ์สูงสุดของระบบ...
[RETRIEVE] Query: Exploit ช่องโหว่เพิ่มเติมเพื่อยกระดับสิทธิ์เป็นสิทธิ์สูงสุดของระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: JHUHUGIT (0.798), Volt Typhoon (0.623), Exploitation for Privilege Escalation (0.545), Privilege Escalation (0.333), Exploit Protection (0.077), Exploit Public-Facing Application (0.021), Exploit Protection (0.016), Exploits (0.003), Exploit Protection (0.003), Exploits (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → JHUHUGIT (21 neighbors, 21 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → Volt Typhoon (100 neighbors, 100 edges)
           → Privilege Escalation (96 neighbors, 96 edges)
           → Exploit Protection (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 6/6: ใช้ส่วนประกอบการแจ้งเตือนของซอฟต์แวร์เป็นช่องทางสั่งงานเครื่องผ่านโพรโทคอลเว็บ...
[RETRIEVE] Query: ใช้ส่วนประกอบการแจ้งเตือนของซอฟต์แวร์เป็นช่องทางสั่งงานเครื่องผ่านโพรโทคอลเว็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: P.A.S. Webshell (0.028), IPsec Helper (0.016), Component Object Model (0.006), BlackMould (0.005), One-Way Communication (0.003), Port Knocking (0.003), POWRUNER (0.001), Credential API Hooking (0.000), Inter-Process Communication (0.000), Asynchronous Procedure Call (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Web Protocols (424 neighbors, 424 edges)
           → IPsec Helper (16 neighbors, 16 edges)
           → Component Object Model (27 neighbors, 27 edges)
           → BlackMould (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [53/100] retrieved=372 relevant=5 latency=12355ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 14 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Query: เมื่อวันที่ 14 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.006), Bankshot (0.002), Pikabot (0.000), FIN8 (0.000), Domains (0.000), Domain Account (0.000), Domain Accounts (0.000), Windows Registry Key Modification (0.000), Access Token Manipulation (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Local Account (69 neighbors, 69 edges)
           → Pikabot (24 neighbors, 24 edges)
           → Non-Standard Port (70 neighbors, 70 edges)
[RETRIEVE-QUOTA] Query 2/7: ค้นหาหมายเลขไอพีของเครื่องแม่ข่ายควบคุมโดเมนผ่านคำสั่งสอบถามชื่อโดเมน (DNS Enume...
[RETRIEVE] Query: ค้นหาหมายเลขไอพีของเครื่องแม่ข่ายควบคุมโดเมนผ่านคำสั่งสอบถามชื่อโดเมน (DNS Enume...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LazyWiper (0.208), Active DNS (0.111), DNS Calculation (0.038), DEADEYE (0.036), Instance Enumeration (0.008), Firewall Enumeration (0.004), Container Enumeration (0.001), Cloud Storage Enumeration (0.001), Ember Bear (0.000), Pacu (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → LazyWiper (9 neighbors, 9 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Active DNS (0 neighbors, 0 edges)
           → DNS Calculation (4 neighbors, 4 edges)
           → DEADEYE (13 neighbors, 13 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] Query 3/7: สร้างบริการของระบบบนเครื่องแม่ข่ายควบคุมโดเมนเพื่อสั่งรันคำสั่งจากระยะไกล...
[RETRIEVE] Query: สร้างบริการของระบบบนเครื่องแม่ข่ายควบคุมโดเมนเพื่อสั่งรันคำสั่งจากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.775), Cloud Administration Command (0.195), RemoteCMD (0.115), RemoteCMD (0.114), CrackMapExec (0.088), Container Administration Command (0.023), PsExec (0.017), Remote Services (0.007), Domain Account (0.003), Service Execution (0.002)
[RETRIEVE] Graph expansion: 6 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Cloud Administration Command (7 neighbors, 7 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → At (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 4/7: ส่งคำสั่งข้ามจากเครื่องแม่ข่ายเก็บเอกสารไปยังเครื่องแม่ข่ายควบคุมโดเมน (Lateral ...
[RETRIEVE] Query: ส่งคำสั่งข้ามจากเครื่องแม่ข่ายเก็บเอกสารไปยังเครื่องแม่ข่ายควบคุมโดเมน (Lateral ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Net (0.256), Lateral Movement (0.174), hcdLoader (0.098), APT18 (0.081), Network Share Discovery (0.022), LSASS Memory (0.021), Remote System Discovery (0.019), OS Credential Dumping (0.010), Expand (0.005), Pcexter (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Net (50 neighbors, 50 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → Lateral Movement (23 neighbors, 23 edges)
           → APT18 (17 neighbors, 17 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 5/7: อัปโหลดไฟล์โปรแกรมขนาดเล็กบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: อัปโหลดไฟล์โปรแกรมขนาดเล็กบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Small Sieve (0.022), LitePower (0.021), AppDomainManager (0.020), Winexe (0.006), ClickOnce (0.001), Visual Basic (0.000), LNK Icon Smuggling (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AppDomainManager (6 neighbors, 6 edges)
           → Small Sieve (14 neighbors, 14 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → LitePower (13 neighbors, 13 edges)
           → Winexe (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/7: ติดต่อกลับออกไปยังเครื่องสั่งการภายนอกผ่านพอร์ตที่ไม่ใช่มาตรฐาน (Command and Con...
[RETRIEVE] Query: ติดต่อกลับออกไปยังเครื่องสั่งการภายนอกผ่านพอร์ตที่ไม่ใช่มาตรฐาน (Command and Con...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exodus (0.644), External Proxy (0.300), Exfiltration Over Alternative Protocol (0.181), Non-Standard Port (0.139), Covenant (0.106), Command and Control (0.034), Bypass User Account Control (0.000), User Account Control (0.000), Anubis (0.000), WolfRAT (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exodus (19 neighbors, 19 edges)
           → Non-Standard Port (9 neighbors, 9 edges)
           → External Proxy (27 neighbors, 27 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → Non-Standard Port (70 neighbors, 70 edges)
[RETRIEVE-QUOTA] Query 7/7: เรียกดูรายละเอียดเครื่องคอมพิวเตอร์ของผู้บริหารฝ่ายการเงินจากระบบทะเบียนโดเมน (D...
[RETRIEVE] Query: เรียกดูรายละเอียดเครื่องคอมพิวเตอร์ของผู้บริหารฝ่ายการเงินจากระบบทะเบียนโดเมน (D...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: dsquery (0.001), System Owner/User Discovery (0.000), Gold Dragon (0.000), Local Storage Discovery (0.000), Device Driver Discovery (0.000), TruffleHog (0.000), Diskpart (0.000), SVCReady (0.000), HAMMERTOSS (0.000), Goopy (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → dsquery (9 neighbors, 9 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Gold Dragon (15 neighbors, 15 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [54/100] retrieved=543 relevant=3 latency=15449ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 27 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความว่าอุปกรณ์เ...
[RETRIEVE] Query: เมื่อวันที่ 27 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความว่าอุปกรณ์เ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.002), BlackByte (0.001), APT-C-36 (0.001), Component Firmware (0.000), DRYHOOK (0.000), Ursnif (0.000), Internal Spearphishing (0.000), Compromise Host Software Binary (0.000), Shortcut Modification (0.000), Social Engineering (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → BlackByte (56 neighbors, 56 edges)
           → Disable or Modify System Firewall (38 neighbors, 38 edges)
           → AsyncRAT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 2/6: เข้าถึงและแก้ไขเฟิร์มแวร์ของอุปกรณ์เราเตอร์...
[RETRIEVE] Query: เข้าถึงและแก้ไขเฟิร์มแวร์ของอุปกรณ์เราเตอร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Firmware Corruption (0.029), Update Software (0.007), BONDUPDATER (0.004), Cobian RAT (0.001), Visual Basic (0.001), RDFSNIFFER (0.000), CrossRAT (0.000), route (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Firmware Corruption (8 neighbors, 8 edges)
           → Update Software (42 neighbors, 42 edges)
           → BONDUPDATER (8 neighbors, 8 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Cobian RAT (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/6: ฝังชุดคำสั่งลับในเฟิร์มแวร์เพื่อคงการเข้าถึงแม้หลังรีสตาร์ต...
[RETRIEVE] Query: ฝังชุดคำสั่งลับในเฟิร์มแวร์เพื่อคงการเข้าถึงแม้หลังรีสตาร์ต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HiddenWasp (0.168), RC Scripts (0.058), UNC3886 (0.020), Active Setup (0.006), Cobian RAT (0.001), Thread Local Storage (0.001), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → HiddenWasp (10 neighbors, 10 edges)
           → RC Scripts (13 neighbors, 13 edges)
           → UNC3886 (58 neighbors, 58 edges)
           → Active Setup (6 neighbors, 6 edges)
           → Thread Local Storage (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 4/6: สร้างช่องทางเชื่อมต่อระยะไกลลับในเฟิร์มแวร์เราเตอร์...
[RETRIEVE] Query: สร้างช่องทางเชื่อมต่อระยะไกลลับในเฟิร์มแวร์เราเตอร์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HTRAN (0.011), RansomHub (0.005), FRP (0.003), FIN5 (0.002), FoggyWeb (0.002), SSH Hijacking (0.002), SSH (0.001), External Remote Services (0.001), FatDuke (0.001), Exfiltration Over Alternative Protocol (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → HTRAN (5 neighbors, 5 edges)
           → RansomHub (21 neighbors, 21 edges)
           → Proxy (84 neighbors, 84 edges)
           → FRP (16 neighbors, 16 edges)
           → Protocol Tunneling (46 neighbors, 46 edges)
[RETRIEVE-QUOTA] Query 5/6: ปิดการบันทึกเหตุการณ์เพื่อซ่อนการเชื่อมต่อระยะไกล...
[RETRIEVE] Query: ปิดการบันทึกเหตุการณ์เพื่อซ่อนการเชื่อมต่อระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Data Storage (0.075), Encrypt Sensitive Information (0.033), Clear Network Connection History and Configurations (0.017), Remote Data Storage (0.002), Encrypt Sensitive Information (0.000), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), The White Company (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Remote Data Storage (11 neighbors, 11 edges)
           → Clear Network Connection History and Configurations (8 neighbors, 8 edges)
           → Encrypt Sensitive Information (33 neighbors, 33 edges)
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Cobian RAT (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 6/6: ควบคุมช่องทางลับด้วยแพ็กเก็ตที่ประกอบขึ้นเป็นพิเศษ...
[RETRIEVE] Query: ควบคุมช่องทางลับด้วยแพ็กเก็ตที่ประกอบขึ้นเป็นพิเศษ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Impacket (0.002), CHIMNEYSWEEP (0.001), Privileged Account Management (0.000), Cobian RAT (0.000), Privileged Process Integrity (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), Ptrace System Calls (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Impacket (35 neighbors, 35 edges)
           → CHIMNEYSWEEP (32 neighbors, 32 edges)
           → Embedded Payloads (27 neighbors, 27 edges)
           → Privileged Account Management (112 neighbors, 112 edges)
           → Ptrace System Calls (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [55/100] retrieved=180 relevant=3 latency=12369ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 28 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความว่าเครือข่ายของสำนักง...
[RETRIEVE] Query: เมื่อวันที่ 28 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความว่าเครือข่ายของสำนักง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.025), ServHelper (0.016), HomeLand Justice (0.000), RDP Hijacking (0.000), Network Intrusion Prevention (0.000), File Deletion (0.000), Remote Services (0.000), Remote Desktop Protocol (0.000), Terminal Services DLL (0.000), Data Encrypted for Impact (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → ServHelper (16 neighbors, 16 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → HomeLand Justice (33 neighbors, 33 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] Query 2/8: ปิดการบันทึกเหตุการณ์ของระบบ (Event Log Clearing) เพื่อลบหลักฐาน...
[RETRIEVE] Query: ปิดการบันทึกเหตุการณ์ของระบบ (Event Log Clearing) เพื่อลบหลักฐาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Clear Windows Event Logs (0.651), ZxShell (0.481), FinFisher (0.356), Mafalda (0.230), Disable or Modify Windows Event Log (0.153), Clear Linux or Mac System Logs (0.101), Clear Command History (0.028), Windows Registry Key Deletion (0.026), Disable or Modify Linux Audit System Log (0.014), Volume Deletion (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → ZxShell (37 neighbors, 37 edges)
           → FinFisher (28 neighbors, 28 edges)
           → Mafalda (37 neighbors, 37 edges)
           → Disable or Modify Windows Event Log (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/8: ใช้ความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนสำหรับ Lateral Movement จากบริษัทลูกเข...
[RETRIEVE] Query: ใช้ความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนสำหรับ Lateral Movement จากบริษัทลูกเข...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain Trust Discovery (0.579), Lateral Movement (0.035), Net (0.007), Replication Through Removable Media (0.003), APT18 (0.002), Remote System Discovery (0.002), Lateral Tool Transfer (0.001), APT18 (0.001), hcdLoader (0.001), Network Share Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → Lateral Movement (23 neighbors, 23 edges)
           → Net (50 neighbors, 50 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → Replication Through Removable Media (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 4/8: ขโมยใบรับรองสำหรับลงลายมือชื่อโปรแกรม (Code Signing Certificate Theft)...
[RETRIEVE] Query: ขโมยใบรับรองสำหรับลงลายมือชื่อโปรแกรม (Code Signing Certificate Theft)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PipeMon (0.937), Code Signing Certificates (0.869), Suckfly (0.846), Code Signing (0.829), Code Signing Certificates (0.558), STATICPLUGIN (0.397), Operation Dream Job (0.392), Code Signing (0.260), Invalid Code Signature (0.225), Steal or Forge Authentication Certificates (0.098)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Code Signing Certificates (14 neighbors, 14 edges)
           → Code Signing (90 neighbors, 90 edges)
           → PipeMon (24 neighbors, 24 edges)
           → Suckfly (6 neighbors, 6 edges)
           → Code Signing Certificates (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/8: เซ็นกำกับไฟล์โปรแกรมอันตรายด้วยใบรับรองที่ขโมยมา (Code Signing)...
[RETRIEVE] Query: เซ็นกำกับไฟล์โปรแกรมอันตรายด้วยใบรับรองที่ขโมยมา (Code Signing)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Suckfly (0.950), PipeMon (0.887), Code Signing (0.881), Code Signing Certificates (0.763), Code Signing (0.603), Code Signing Certificates (0.530), Invalid Code Signature (0.232), Operation Dream Job (0.049), SIP and Trust Provider Hijacking (0.012), Mustang Panda (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Code Signing (90 neighbors, 90 edges)
           → Suckfly (6 neighbors, 6 edges)
           → Code Signing Certificates (14 neighbors, 14 edges)
           → PipeMon (24 neighbors, 24 edges)
           → Code Signing Certificates (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 6/8: เปิดเชลล์รับการเชื่อมต่อค้างไว้เพื่อคงการเข้าถึง (Reverse Shell / Persistence)...
[RETRIEVE] Query: เปิดเชลล์รับการเชื่อมต่อค้างไว้เพื่อคงการเข้าถึง (Reverse Shell / Persistence)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SnappyTCP (0.334), Persistence (0.086), Web Shell (0.024), REPTILE (0.021), Terminal Services DLL (0.018), SSH Hijacking (0.009), Netsh Helper DLL (0.006), PowerSploit (0.004), Clear Persistence (0.004), PowerSploit (0.003)
[RETRIEVE] Graph expansion: 6 subgraphs
           → SnappyTCP (6 neighbors, 6 edges)
           → Web Shell (71 neighbors, 71 edges)
           → Persistence (113 neighbors, 113 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
           → REPTILE (13 neighbors, 13 edges)
           → Traffic Signaling (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 7/8: แก้ไขทะเบียนระบบเพื่อเปิดใช้งาน Remote Desktop Protocol (RDP Persistence)...
[RETRIEVE] Query: แก้ไขทะเบียนระบบเพื่อเปิดใช้งาน Remote Desktop Protocol (RDP Persistence)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SILENTTRINITY (0.880), Modify Registry (0.554), Operating System Configuration (0.079), RDP Hijacking (0.016), Remote Desktop Protocol (0.016), Terminal Services DLL (0.009), Carbanak (0.007), VNC (0.001), Remote Access Tools (0.000), Remote Services (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 8/8: เข้าใช้งานผ่าน SSH เพื่อคงการเข้าถึง (SSH Persistence)...
[RETRIEVE] Query: เข้าใช้งานผ่าน SSH เพื่อคงการเข้าถึง (SSH Persistence)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Persistence (0.807), SSH Hijacking (0.148), PowerSploit (0.080), SSH (0.066), PowerSploit (0.050), Cloud Application Integration (0.046), Clear Persistence (0.043), Helminth (0.026), PowerSploit (0.023), Netsh Helper DLL (0.020)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Persistence (113 neighbors, 113 edges)
           → SSH Hijacking (8 neighbors, 8 edges)
           → PowerSploit (39 neighbors, 39 edges)
           → Security Support Provider (9 neighbors, 9 edges)
           → SSH (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [56/100] retrieved=248 relevant=4 latency=15965ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 16 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความว่าระบบงานทั้งหมดถูกเข้า...
[RETRIEVE] Query: เมื่อวันที่ 16 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความว่าระบบงานทั้งหมดถูกเข้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: REvil (0.005), POWERSTATS (0.004), Pay2Key (0.001), BitPaymer (0.001), Data Encrypted for Impact (0.000), POWERSOURCE (0.000), Disable or Remove Feature or Program (0.000), PowerSploit (0.000), PowerShell (0.000), PowerShell Profile (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → REvil (37 neighbors, 37 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Pay2Key (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 2/8: Malware injection ลงในหน่วยความจำของกระบวนการที่ทำงาน (Process Injection)...
[RETRIEVE] Query: Malware injection ลงในหน่วยความจำของกระบวนการที่ทำงาน (Process Injection)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Proc Memory (0.993), Process Injection (0.954), Extra Window Memory Injection (0.894), REvil (0.791), Process Hollowing (0.728), SLOTHFULMEDIA (0.613), Mavinject (0.311), Portable Executable Injection (0.077), Dynamic-link Library Injection (0.037), Uroburos (0.016)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Proc Memory (7 neighbors, 7 edges)
           → Process Injection (104 neighbors, 104 edges)
           → Extra Window Memory Injection (7 neighbors, 7 edges)
           → Process Hollowing (48 neighbors, 48 edges)
           → REvil (37 neighbors, 37 edges)
[RETRIEVE-QUOTA] Query 3/8: รันคำสั่งแก้ไขทะเบียนระบบ Windows Registry ผ่าน Command Prompt...
[RETRIEVE] Query: รันคำสั่งแก้ไขทะเบียนระบบ Windows Registry ผ่าน Command Prompt...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Reg (0.743), HeartCrypt (0.472), Modify Registry (0.365), Reg (0.206), Windows Registry Key Modification (0.038), Registry Run Keys / Startup Folder (0.027), Credentials in Registry (0.012), Query Registry (0.010), Windows Command Shell (0.005), RedCurl (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Reg (12 neighbors, 12 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → HeartCrypt (12 neighbors, 12 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Windows Registry Key Modification (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 4/8: เปลี่ยนนามสกุลไฟล์ทั้งหมดเป็นนามสกุลเฉพาะของโปรแกรมเรียกค่าไถ่...
[RETRIEVE] Query: เปลี่ยนนามสกุลไฟล์ทั้งหมดเป็นนามสกุลเฉพาะของโปรแกรมเรียกค่าไถ่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Change Default File Association (0.006), Space after Filename (0.005), CHIMNEYSWEEP (0.004), BADCALL (0.001), KernelCallbackTable (0.001), Path Interception by PATH Environment Variable (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Change Default File Association (7 neighbors, 7 edges)
           → Space after Filename (4 neighbors, 4 edges)
           → CHIMNEYSWEEP (32 neighbors, 32 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → BADCALL (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 5/8: รันคำสั่ง PowerShell ลบไฟล์โปรแกรมเรียกค่าไถ่ผ่านหน้าต่างคำสั่งที่ซ่อนไว้...
[RETRIEVE] Query: รันคำสั่ง PowerShell ลบไฟล์โปรแกรมเรียกค่าไถ่ผ่านหน้าต่างคำสั่งที่ซ่อนไว้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.374), Netwalker (0.024), POWERSOURCE (0.021), RansomHub (0.019), PowerShell (0.015), Disable or Remove Feature or Program (0.007), PowerShell Profile (0.006), POWERSTATS (0.004), PowerSploit (0.004), Invoke-PSImage (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Hidden Window (65 neighbors, 65 edges)
           → RansomHub (21 neighbors, 21 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Netwalker (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 6/8: เข้ารหัสข้อมูลโรงพยาบาลด้วยกุญแจสาธารณะ 4096 บิตและอัลกอริทึมเข้ารหัสแบบสตรีม...
[RETRIEVE] Query: เข้ารหัสข้อมูลโรงพยาบาลด้วยกุญแจสาธารณะ 4096 บิตและอัลกอริทึมเข้ารหัสแบบสตรีม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LunarWeb (0.014), Asymmetric Cryptography (0.011), Carbanak (0.010), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.002), BitPaymer (0.002), Helminth (0.001), DNS (0.000), Compute Hijacking (0.000), Dridex (0.000), Domain Properties (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → LunarWeb (31 neighbors, 31 edges)
           → Asymmetric Cryptography (100 neighbors, 100 edges)
           → Carbanak (20 neighbors, 20 edges)
           → Data Transfer Size Limits (24 neighbors, 24 edges)
           → Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 7/8: ดึงข้อมูลอ่อนไหวของโรงพยาบาลออกจากเครือข่าย (Data Exfiltration)...
[RETRIEVE] Query: ดึงข้อมูลอ่อนไหวของโรงพยาบาลออกจากเครือข่าย (Data Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration (0.188), Exfiltration Over Other Network Medium (0.028), Archive Collected Data (0.024), Exfiltration Over Physical Medium (0.018), Remsec (0.016), Data from Network Shared Drive (0.013), Data Loss Prevention (0.009), Empire (0.003), Exbyte (0.002), Exbyte (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Exfiltration (19 neighbors, 19 edges)
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
           → Archive Collected Data (62 neighbors, 62 edges)
           → Exfiltration Over Physical Medium (6 neighbors, 6 edges)
           → Remsec (31 neighbors, 31 edges)
           → Exfiltration over USB (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 8/8: ข่มขู่สองชั้นเรียกค่าไถ่พร้อมขู่เผยแพร่ข้อมูลอ่อนไหว...
[RETRIEVE] Query: ข่มขู่สองชั้นเรียกค่าไถ่พร้อมขู่เผยแพร่ข้อมูลอ่อนไหว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Black Basta (0.116), Akira (0.108), Spearphishing Attachment (0.042), Play (0.035), Spearphishing Link (0.026), Spearphishing Service (0.023), Spearphishing Voice (0.021), Scattered Spider (0.010), DoubleAgent (0.001), SMS Pumping (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Akira (25 neighbors, 25 edges)
           → Financial Theft (27 neighbors, 27 edges)
           → Black Basta (27 neighbors, 27 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
           → Play (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [57/100] retrieved=408 relevant=6 latency=18030ms
[RETRIEVE-QUOTA] Query 1/11: เมื่อวันที่ 17 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความว่าลูกค้าหลายรายถูกโอนเงินออกจ...
[RETRIEVE] Query: เมื่อวันที่ 17 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความว่าลูกค้าหลายรายถูกโอนเงินออกจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.282), Frankenstein (0.252), Exfiltration Over C2 Channel (0.150), Octopus (0.147), AuTo Stealer (0.143), Resource Hijacking (0.140), Automated Exfiltration (0.040), Scheduled Transfer (0.008), Exfiltration Over Unencrypted Non-C2 Protocol (0.001), Financial Theft (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Frankenstein (28 neighbors, 28 edges)
           → Resource Hijacking (6 neighbors, 6 edges)
           → Octopus (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 2/11: Phishing หรือ Social Engineering เพื่อให้ผู้ใช้ติดตั้งโปรแกรมไม่พึงประสงค์...
[RETRIEVE] Query: Phishing หรือ Social Engineering เพื่อให้ผู้ใช้ติดตั้งโปรแกรมไม่พึงประสงค์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Social Engineering (0.689), Phishing (0.550), User Training (0.544), User Training (0.512), User Training (0.476), Spearphishing Link (0.130), Spearphishing Attachment (0.130), Spearphishing Service (0.076), Phishing for Information (0.008), Kimsuky (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Social Engineering (6 neighbors, 6 edges)
           → Phishing (23 neighbors, 23 edges)
           → User Training (60 neighbors, 60 edges)
           → Phishing for Information (12 neighbors, 12 edges)
           → Spearphishing Link (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 3/11: โปรแกรมไม่พึงประสงค์แทรกตัวในเบราว์เซอร์ (Browser Injection)...
[RETRIEVE] Query: โปรแกรมไม่พึงประสงค์แทรกตัวในเบราว์เซอร์ (Browser Injection)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Browser Session Hijacking (0.875), TSCookie (0.859), Smoke Loader (0.691), ISMInjector (0.183), Browser Extensions (0.065), Cardinal RAT (0.065), Content Injection (0.051), HTRAN (0.043), Input Injection (0.022), Process Injection (0.007)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Browser Session Hijacking (19 neighbors, 19 edges)
           → TSCookie (14 neighbors, 14 edges)
           → Process Injection (104 neighbors, 104 edges)
           → Smoke Loader (14 neighbors, 14 edges)
           → ISMInjector (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 4/11: ดักจับและแก้ไขข้อมูลที่ผู้ใช้กรอกบนหน้าเว็บธนาคาร (Credential Interception)...
[RETRIEVE] Query: ดักจับและแก้ไขข้อมูลที่ผู้ใช้กรอกบนหน้าเว็บธนาคาร (Credential Interception)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Input Capture (0.338), SharkBot (0.119), Mispadu (0.025), Multi-Factor Authentication Interception (0.008), SLOWPULSE (0.004), Multi-factor Authentication (0.003), Inception (0.002), Windows Credential Manager (0.001), Social Media (0.000), Input Injection (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Input Capture (20 neighbors, 20 edges)
           → SharkBot (18 neighbors, 18 edges)
           → GUI Input Capture (34 neighbors, 34 edges)
           → Mispadu (27 neighbors, 27 edges)
           → Browser Information Discovery (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 5/11: ขโมยชื่อผู้ใช้และรหัสผ่านจากการกรอกข้อมูลบนเว็บธนาคาร...
[RETRIEVE] Query: ขโมยชื่อผู้ใช้และรหัสผ่านจากการกรอกข้อมูลบนเว็บธนาคาร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ursnif (0.774), QakBot (0.571), Chaes (0.121), Lokibot (0.076), QakBot (0.054), IcedID (0.032), Bankshot (0.010), Financial Theft (0.010), Mimikatz (0.005), Bankshot (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Ursnif (36 neighbors, 36 edges)
           → Browser Session Hijacking (19 neighbors, 19 edges)
           → QakBot (74 neighbors, 74 edges)
           → Chaes (28 neighbors, 28 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
[RETRIEVE-QUOTA] Query 6/11: โปรแกรมทำหน้าที่เป็นตัวดาวน์โหลด (Downloader) ดึงไฟล์อันตรายจากเครื่องภายนอก...
[RETRIEVE] Query: โปรแกรมทำหน้าที่เป็นตัวดาวน์โหลด (Downloader) ดึงไฟล์อันตรายจากเครื่องภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Caminho (0.306), Power Loader (0.209), build_downer (0.198), Hancitor (0.189), Gazer (0.081), pngdowner (0.015), Silence (0.007), Gazer (0.006), Responder (0.004), LP-Notes (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Caminho (7 neighbors, 7 edges)
           → build_downer (9 neighbors, 9 edges)
           → Steganography (32 neighbors, 32 edges)
           → Power Loader (1 neighbors, 1 edges)
           → Hancitor (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 7/11: ติดตั้งโปรแกรมอันตรายเพิ่มเติมบนเครื่องผู้เสียหาย (Secondary Payload Installatio...
[RETRIEVE] Query: ติดตั้งโปรแกรมอันตรายเพิ่มเติมบนเครื่องผู้เสียหาย (Secondary Payload Installatio...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Zebrocy (0.660), Upload Malware (0.134), Embedded Payloads (0.057), SodaMaster (0.038), P8RAT (0.033), Relocate Malware (0.017), Compile After Delivery (0.011), CLAIMLOADER (0.005), Obfuscated Files or Information (0.002), Cuckoo Stealer (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Zebrocy (32 neighbors, 32 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Upload Malware (39 neighbors, 39 edges)
           → Embedded Payloads (27 neighbors, 27 edges)
           → SodaMaster (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 8/11: ส่งข้อมูลที่รวบรวมออกไปยังเครื่องสั่งการ (Exfiltration Over C2 Channel)...
[RETRIEVE] Query: ส่งข้อมูลที่รวบรวมออกไปยังเครื่องสั่งการ (Exfiltration Over C2 Channel)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SVCReady (0.935), Industroyer (0.900), Exfiltration Over C2 Channel (0.882), Automated Exfiltration (0.728), Okrum (0.607), APT39 (0.587), Scheduled Transfer (0.466), Exfiltration Over Unencrypted Non-C2 Protocol (0.423), Data Staged (0.025), Remote Data Staging (0.010)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → SVCReady (24 neighbors, 24 edges)
           → Industroyer (21 neighbors, 21 edges)
           → Automated Exfiltration (33 neighbors, 33 edges)
           → Okrum (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 9/11: ใช้ทรัพยากรของเครื่องผู้เสียหายขุดเหรียญสกุลเงินดิจิทัล (Resource Hijacking)...
[RETRIEVE] Query: ใช้ทรัพยากรของเครื่องผู้เสียหายขุดเหรียญสกุลเงินดิจิทัล (Resource Hijacking)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Resource Hijacking (0.903), Compute Hijacking (0.673), LoudMiner (0.649), DarkGate (0.438), BBSRAT (0.025), VDSO Hijacking (0.007), Use Recent OS Version (0.006), Bandwidth Hijacking (0.006), Thread Execution Hijacking (0.005), Remote Service Session Hijacking (0.004)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Resource Hijacking (6 neighbors, 6 edges)
           → Compute Hijacking (17 neighbors, 17 edges)
           → LoudMiner (18 neighbors, 18 edges)
           → DarkGate (59 neighbors, 59 edges)
           → BBSRAT (14 neighbors, 14 edges)
           → Component Object Model Hijacking (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 10/11: เรียกดูข้อมูลของเครื่องและข้อมูลเฟิร์มแวร์ระดับล่าง (System Information Discover...
[RETRIEVE] Query: เรียกดูข้อมูลของเครื่องและข้อมูลเฟิร์มแวร์ระดับล่าง (System Information Discover...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HALFBAKED (0.690), System Information Discovery (0.634), Systeminfo (0.582), SYSCON (0.492), cmd (0.294), Systeminfo (0.197), Backup Software Discovery (0.047), System Owner/User Discovery (0.033), Device Driver Discovery (0.017), Process Discovery (0.017)
[RETRIEVE] Graph expansion: 5 subgraphs
           → System Information Discovery (426 neighbors, 426 edges)
           → HALFBAKED (7 neighbors, 7 edges)
           → Systeminfo (14 neighbors, 14 edges)
           → SYSCON (6 neighbors, 6 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 11/11: โอนเงินออกจากบัญชีธนาคารของผู้เสียหาย (Unauthorized Fund Transfer)...
[RETRIEVE] Query: โอนเงินออกจากบัญชีธนาคารของผู้เสียหาย (Unauthorized Fund Transfer)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.004), Transfer Data to Cloud Account (0.002), GCMAN (0.001), SSH Authorized Keys (0.001), User Account Management (0.001), Lateral Tool Transfer (0.000), Ingress Tool Transfer (0.000), TFTP Boot (0.000), Expand (0.000), cmd (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Transfer Data to Cloud Account (9 neighbors, 9 edges)
           → SSH Authorized Keys (15 neighbors, 15 edges)
           → GCMAN (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 11 queries
  [58/100] retrieved=296 relevant=4 latency=19895ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 1 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครือข่ายภายในถูกบุกรุกผ...
[RETRIEVE] Query: เมื่อวันที่ 1 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครือข่ายภายในถูกบุกรุกผ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NETWIRE (0.007), Network Device Firewall (0.006), SharePoint ToolShell Exploitation (0.002), Internal Spearphishing (0.001), Magic Hound (0.001), Threat Group-3390 (0.000), Valid Accounts (0.000), Trusted Relationship (0.000), Clear Windows Event Logs (0.000), Clear Linux or Mac System Logs (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Network Device Firewall (9 neighbors, 9 edges)
           → NETWIRE (49 neighbors, 49 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → SharePoint ToolShell Exploitation (39 neighbors, 39 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 2/5: ช่องโหว่ในอุปกรณ์ VPN SSL ที่ไม่ได้ปรับปรุงซอฟต์แวร์ถูกใช้เพื่อบุกรุกเครือข่าย...
[RETRIEVE] Query: ช่องโหว่ในอุปกรณ์ VPN SSL ที่ไม่ได้ปรับปรุงซอฟต์แวร์ถูกใช้เพื่อบุกรุกเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SoreFang (0.469), WARPWIRE (0.268), PITSTOP (0.245), UNC3886 (0.224), XTunnel (0.082), STEADYPULSE (0.070), Cutting Edge (0.039), Cutting Edge (0.016), VPNFilter (0.013), APT5 (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SoreFang (15 neighbors, 15 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → UNC3886 (58 neighbors, 58 edges)
           → WARPWIRE (6 neighbors, 6 edges)
           → PITSTOP (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 3/5: ช่องโหว่ในอุปกรณ์ไฟร์วอลล์และอุปกรณ์เชื่อมต่อระยะไกลที่ไม่ได้ปรับปรุงถูกเข้าถึงจ...
[RETRIEVE] Query: ช่องโหว่ในอุปกรณ์ไฟร์วอลล์และอุปกรณ์เชื่อมต่อระยะไกลที่ไม่ได้ปรับปรุงถูกเข้าถึงจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FLASHFLOOD (0.003), WIREFIRE (0.001), BUSHWALK (0.001), Threat Group-1314 (0.001), Quad7 Activity (0.001), POORAIM (0.001), FoggyWeb (0.000), FlawedAmmyy (0.000), Volt Typhoon (0.000), Daggerfly (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FLASHFLOOD (7 neighbors, 7 edges)
           → Quad7 Activity (16 neighbors, 16 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → WIREFIRE (8 neighbors, 8 edges)
           → BUSHWALK (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 4/5: ใช้ชื่อผู้ใช้และรหัสผ่าน VPN ที่ขโมยมาเพื่อเข้าสู่ระบบ...
[RETRIEVE] Query: ใช้ชื่อผู้ใช้และรหัสผ่าน VPN ที่ขโมยมาเพื่อเข้าสู่ระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN10 (0.746), Operation Wocao (0.686), WARPWIRE (0.245), LAPSUS$ (0.215), Valid Accounts (0.052), Web Portal Capture (0.016), VPNFilter (0.008), C0032 (0.002), Cutting Edge (0.001), XTunnel (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN10 (12 neighbors, 12 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Operation Wocao (79 neighbors, 79 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] Query 5/5: ใช้ชื่อผู้ใช้และรหัสผ่านหน้าจอระยะไกลที่ขโมยมาเพื่อเข้าสู่ระบบ...
[RETRIEVE] Query: ใช้ชื่อผู้ใช้และรหัสผ่านหน้าจอระยะไกลที่ขโมยมาเพื่อเข้าสู่ระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RDP Hijacking (0.299), FIN10 (0.259), LP-Notes (0.156), Remote Service Session Hijacking (0.094), Threat Group-1314 (0.088), APT18 (0.005), Remote Services (0.004), APT18 (0.004), Windows Remote Management (0.004), SSH (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → FIN10 (12 neighbors, 12 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → LP-Notes (12 neighbors, 12 edges)
           → Remote Service Session Hijacking (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] 14 vectors (quota 3/query), 8 subgraphs from 5 queries
  [59/100] retrieved=451 relevant=3 latency=10261ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 3 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์หลาย...
[RETRIEVE] Query: เมื่อวันที่ 3 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์หลาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WINDSHIELD (0.009), njRAT (0.003), 3CX Supply Chain Attack (0.000), FIN8 (0.000), Software Discovery (0.000), 3PARA RAT (0.000), Software (0.000), Process Discovery (0.000), Pikabot (0.000), APT1 (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → WINDSHIELD (6 neighbors, 6 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → njRAT (40 neighbors, 40 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/9: Remote Desktop Protocol (RDP) ที่เปิดค้างไว้ถูกใช้เข้าถึงเครื่องเป้าหมายแรก...
[RETRIEVE] Query: Remote Desktop Protocol (RDP) ที่เปิดค้างไว้ถูกใช้เข้าถึงเครื่องเป้าหมายแรก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.631), C0015 (0.249), Remote Desktop Protocol (0.129), RDP Hijacking (0.072), Carbanak (0.015), SILENTTRINITY (0.013), Terminal Services DLL (0.013), Remote Access Tools (0.002), Remote Services (0.000), ARP Cache Poisoning (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → C0015 (39 neighbors, 39 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 3/9: ขโมยชื่อผู้ใช้และรหัสผ่านจากเครื่องแรกเพื่อเข้าถึงเครื่องเป้าหมายถัดไป...
[RETRIEVE] Query: ขโมยชื่อผู้ใช้และรหัสผ่านจากเครื่องแรกเพื่อเข้าถึงเครื่องเป้าหมายถัดไป...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credential Access (0.167), USBStealer (0.131), USBStealer (0.059), LAPSUS$ (0.020), Exploitation for Credential Access (0.019), Token Impersonation/Theft (0.015), Valid Accounts (0.014), Acquire Access (0.013), Gamaredon Group (0.009), Access Token Manipulation (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Credential Access (67 neighbors, 67 edges)
           → USBStealer (15 neighbors, 15 edges)
           → Data from Removable Media (27 neighbors, 27 edges)
           → Communication Through Removable Media (7 neighbors, 7 edges)
           → Exploitation for Credential Access (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 4/9: ดาวน์โหลดและสั่งให้โปรแกรมทำงานผ่าน RDP connection...
[RETRIEVE] Query: ดาวน์โหลดและสั่งให้โปรแกรมทำงานผ่าน RDP connection...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pupy (0.321), ServHelper (0.120), NETEAGLE (0.114), Terminal Services DLL (0.052), INC Ransom (0.020), RDP Hijacking (0.014), Remote Service Session Hijacking (0.012), Remote Desktop Protocol (0.012), Application Layer Protocol (0.002), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pupy (43 neighbors, 43 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → ServHelper (16 neighbors, 16 edges)
           → NETEAGLE (12 neighbors, 12 edges)
           → Application Layer Protocol (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 5/9: เก็บรวบรวมข้อมูลระบบปฏิบัติการ ชื่อเครื่อง ประเภท CPU และหน่วยความจำ...
[RETRIEVE] Query: เก็บรวบรวมข้อมูลระบบปฏิบัติการ ชื่อเครื่อง ประเภท CPU และหน่วยความจำ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Azorult (0.795), RedLeaves (0.746), Systeminfo (0.343), LoudMiner (0.029), Instance Creation (0.011), Instance Deletion (0.010), Instance Enumeration (0.008), MegaCortex (0.008), Instance Stop (0.004), Pod Enumeration (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Azorult (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → RedLeaves (18 neighbors, 18 edges)
           → Systeminfo (14 neighbors, 14 edges)
           → LoudMiner (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 6/9: เก็บรวบรวมข้อมูลเฟิร์มแวร์ระดับล่างของเครื่อง...
[RETRIEVE] Query: เก็บรวบรวมข้อมูลเฟิร์มแวร์ระดับล่างของเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Firmware (0.693), Systeminfo (0.071), down_new (0.034), SLOWDRIFT (0.006), Firmware Modification (0.005), Visual Basic (0.001), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Firmware (3 neighbors, 3 edges)
           → Systeminfo (14 neighbors, 14 edges)
           → down_new (11 neighbors, 11 edges)
           → Software Discovery (56 neighbors, 56 edges)
           → SLOWDRIFT (4 neighbors, 4 edges)
           → System Information Discovery (426 neighbors, 426 edges)
[RETRIEVE-QUOTA] Query 7/9: เรียกดูรายการโปรแกรมและบริการที่ติดตั้งบนเครื่อง...
[RETRIEVE] Query: เรียกดูรายการโปรแกรมและบริการที่ติดตั้งบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.650), BOULDSPY (0.331), GPlayed (0.253), ipconfig (0.006), netstat (0.005), Cobian RAT (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → BOULDSPY (25 neighbors, 25 edges)
           → Software Discovery (56 neighbors, 56 edges)
           → GPlayed (18 neighbors, 18 edges)
           → ipconfig (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 8/9: รวบรวมรายชื่อบัญชีผู้ใช้ในเครื่องและโดเมนขององค์กร...
[RETRIEVE] Query: รวบรวมรายชื่อบัญชีผู้ใช้ในเครื่องและโดเมนขององค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.362), PoshC2 (0.313), Cloud Account (0.046), Nltest (0.013), Account Discovery (0.012), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → PoshC2 (35 neighbors, 35 edges)
           → Cloud Account (11 neighbors, 11 edges)
           → Account Discovery (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 9/9: เรียกดูหมายเลข IP ตำแหน่งที่ตั้ง และการตั้งค่าเครือข่ายของเครื่องผู้เสียหาย...
[RETRIEVE] Query: เรียกดูหมายเลข IP ตำแหน่งที่ตั้ง และการตั้งค่าเครือข่ายของเครื่องผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ixeshe (0.763), Carbon (0.641), cd00r (0.602), Grandoreiro (0.539), System Network Configuration Discovery (0.407), ipconfig (0.299), Gather Victim Network Information (0.101), Scanning IP Blocks (0.063), IP Addresses (0.062), route (0.010)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Ixeshe (16 neighbors, 16 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → Carbon (19 neighbors, 19 edges)
           → cd00r (4 neighbors, 4 edges)
           → Grandoreiro (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [60/100] retrieved=610 relevant=6 latency=17970ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 20 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบเดสก์...
[RETRIEVE] Query: เมื่อวันที่ 20 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบเดสก์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OSInfo (0.001), VOID MANTICORE (0.001), Wiarp (0.001), Adversary-in-the-Middle (0.000), Evil Twin (0.000), Ingress Tool Transfer (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), Input Injection (0.000), ARP Cache Poisoning (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → OSInfo (11 neighbors, 11 edges)
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Wiarp (5 neighbors, 5 edges)
           → Process Injection (104 neighbors, 104 edges)
[RETRIEVE-QUOTA] Query 2/7: ช่องโหว่ไลบรารีบันทึกเหตุการณ์ที่ไม่ได้แก้ไขบนเซิร์ฟเวอร์เดสก์ท็อปเสมือนเปิดให้เ...
[RETRIEVE] Query: ช่องโหว่ไลบรารีบันทึกเหตุการณ์ที่ไม่ได้แก้ไขบนเซิร์ฟเวอร์เดสก์ท็อปเสมือนเปิดให้เ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.001), FoggyWeb (0.000), Fileless Storage (0.000), BlackTech (0.000), Operation MidnightEclipse (0.000), Quad7 Activity (0.000), Unsecured Credentials (0.000), DRYHOOK (0.000), Component Object Model Hijacking (0.000), Process Hollowing (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Fileless Storage (34 neighbors, 34 edges)
           → FoggyWeb (22 neighbors, 22 edges)
           → BlackTech (20 neighbors, 20 edges)
           → Unsecured Credentials (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] Query 3/7: วางไฟล์โปรแกรมปลอมแปลงเป็นบริการระบบปฏิบัติการวินโดวส์ที่ดัดแปลงจากเครื่องมือตรว...
[RETRIEVE] Query: วางไฟล์โปรแกรมปลอมแปลงเป็นบริการระบบปฏิบัติการวินโดวส์ที่ดัดแปลงจากเครื่องมือตรว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exaramel for Windows (0.095), RawPOS (0.079), Dok (0.029), LP-Notes (0.025), GUI Input Capture (0.006), Mimikatz (0.006), UACMe (0.001), MimiPenguin (0.001), gsecdump (0.001), pwdump (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exaramel for Windows (9 neighbors, 9 edges)
           → Masquerade Task or Service (94 neighbors, 94 edges)
           → RawPOS (6 neighbors, 6 edges)
           → LP-Notes (12 neighbors, 12 edges)
           → Token Impersonation/Theft (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 4/7: ฝังชุดคำสั่งอันตรายบีบอัดภายในไฟล์โปรแกรมปลอม...
[RETRIEVE] Query: ฝังชุดคำสั่งอันตรายบีบอัดภายในไฟล์โปรแกรมปลอม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: IcedID (0.642), Embedded Payloads (0.540), PROMETHIUM (0.058), Masquerade File Type (0.011), Mavinject (0.005), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Embedded Payloads (27 neighbors, 27 edges)
           → IcedID (34 neighbors, 34 edges)
           → PROMETHIUM (14 neighbors, 14 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
           → Masquerade File Type (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 5/7: ติดตั้งเครื่องมือควบคุมเครื่องระยะไกลที่ดักบันทึกการกดแป้นพิมพ์ (keylogging)...
[RETRIEVE] Query: ติดตั้งเครื่องมือควบคุมเครื่องระยะไกลที่ดักบันทึกการกดแป้นพิมพ์ (keylogging)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ZxShell (0.887), Duqu (0.476), DUSTTRAP (0.473), Fysbis (0.397), CorKLOG (0.190), Keylogging (0.113), PAKLOG (0.105), Input Injection (0.009), Psylo (0.001), Private Keys (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → ZxShell (37 neighbors, 37 edges)
           → Keylogging (160 neighbors, 160 edges)
           → Duqu (21 neighbors, 21 edges)
           → DUSTTRAP (31 neighbors, 31 edges)
           → Fysbis (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 6/7: อัปโหลดและสั่งรันไฟล์เพิ่มเติมเข้ามาบนเครื่องเป้าหมายผ่านเครื่องมือควบคุมระยะไกล...
[RETRIEVE] Query: อัปโหลดและสั่งรันไฟล์เพิ่มเติมเข้ามาบนเครื่องเป้าหมายผ่านเครื่องมือควบคุมระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteUtilities (0.884), NavRAT (0.845), P8RAT (0.572), RemoteCMD (0.220), Cobian RAT (0.035), Remote Access Tools (0.030), CrossRAT (0.001), Visual Basic (0.001), Cardinal RAT (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RemoteUtilities (5 neighbors, 5 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → NavRAT (10 neighbors, 10 edges)
           → P8RAT (6 neighbors, 6 edges)
           → RemoteCMD (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 7/7: ดูและควบคุมหน้าจอของเครื่องเป้าหมายโดยตรงผ่านเครื่องมือควบคุมระยะไกล...
[RETRIEVE] Query: ดูและควบคุมหน้าจอของเครื่องเป้าหมายโดยตรงผ่านเครื่องมือควบคุมระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Quick Assist (0.492), Remote Desktop Software (0.406), Quick Assist (0.131), RemoteCMD (0.063), BRATA (0.056), Remote Access Tools (0.044), QakBot (0.036), AsyncRAT (0.018), Windows Remote Management (0.006), Direct Volume Access (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Remote Desktop Software (21 neighbors, 21 edges)
           → Quick Assist (4 neighbors, 4 edges)
           → Video Capture (37 neighbors, 37 edges)
           → BRATA (27 neighbors, 27 edges)
           → Remote Access Software (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [61/100] retrieved=371 relevant=4 latency=14761ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 5 เมษายน 2567 บริษัทผู้ให้บริการระบบสารสนเทศแห่งหนึ่งแจ้งความว่าเครื...
[RETRIEVE] Query: เมื่อวันที่ 5 เมษายน 2567 บริษัทผู้ให้บริการระบบสารสนเทศแห่งหนึ่งแจ้งความว่าเครื...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.045), Cobalt Strike (0.003), ServHelper (0.001), SSH Hijacking (0.000), SSH Authorized Keys (0.000), DCHSpy (0.000), SSH (0.000), P.A.S. Webshell (0.000), Forced Authentication (0.000), Internal Spearphishing (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → SSH (33 neighbors, 33 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
           → ServHelper (16 neighbors, 16 edges)
           → PowerShell (241 neighbors, 241 edges)
[RETRIEVE-QUOTA] Query 2/7: SSH login ด้วยบัญชีที่ถูกต้องเข้าเครื่องแม่ข่ายเว็บ...
[RETRIEVE] Query: SSH login ด้วยบัญชีที่ถูกต้องเข้าเครื่องแม่ข่ายเว็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SSH (0.270), UNC3886 (0.091), Kinsing (0.057), SSH Authorized Keys (0.041), SSH Hijacking (0.018), Bundlore (0.016), User Account Management (0.016), Remote Services (0.008), Password Guessing (0.001), Domain Controller Authentication (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SSH (33 neighbors, 33 edges)
           → UNC3886 (58 neighbors, 58 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Kinsing (17 neighbors, 17 edges)
           → SSH Authorized Keys (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 3/7: ส่งไฟล์สคริปต์ PHP จากเครื่องภายนอกเข้าวางบนเครื่องแม่ข่าย...
[RETRIEVE] Query: ส่งไฟล์สคริปต์ PHP จากเครื่องภายนอกเข้าวางบนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PHPsert (0.030), P.A.S. Webshell (0.030), PHPsert (0.012), PHPsert (0.012), netsh (0.005), SSH (0.001), Exfiltration Over Alternative Protocol (0.001), P.A.S. Webshell (0.001), Operation Digital Eye (0.000), Masquerade File Type (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PHPsert (7 neighbors, 7 edges)
           → Web Protocols (424 neighbors, 424 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → netsh (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 4/7: ติดตั้งสคริปต์ PHP เป็นหน้าเว็บสำหรับรับคำสั่ง (web shell)...
[RETRIEVE] Query: ติดตั้งสคริปต์ PHP เป็นหน้าเว็บสำหรับรับคำสั่ง (web shell)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Web Shell (0.390), PHPsert (0.312), P.A.S. Webshell (0.157), PHPsert (0.109), Operation Digital Eye (0.037), P.A.S. Webshell (0.028), P.A.S. Webshell (0.011), Command and Scripting Interpreter (0.003), Netsh Helper DLL (0.002), Windows Command Shell (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Web Shell (71 neighbors, 71 edges)
           → PHPsert (7 neighbors, 7 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Operation Digital Eye (26 neighbors, 26 edges)
           → Web Protocols (424 neighbors, 424 edges)
[RETRIEVE-QUOTA] Query 5/7: เรียกดูชื่อบัญชีผู้ใช้ที่สคริปต์กำลังทำงานอยู่...
[RETRIEVE] Query: เรียกดูชื่อบัญชีผู้ใช้ที่สคริปต์กำลังทำงานอยู่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN13 (0.108), System Owner/User Discovery (0.006), Local Account (0.003), BISCUIT (0.002), Cloud Account (0.001), Visual Basic (0.000), Cardinal RAT (0.000), CrossRAT (0.000), Cobian RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN13 (57 neighbors, 57 edges)
           → Domain Account (65 neighbors, 65 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Local Account (69 neighbors, 69 edges)
           → BISCUIT (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 6/7: เรียกดูรายละเอียดระบบปฏิบัติการที่ติดตั้งบนเครื่อง...
[RETRIEVE] Query: เรียกดูรายละเอียดระบบปฏิบัติการที่ติดตั้งบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.161), Systeminfo (0.072), BOULDSPY (0.068), Tasklist (0.046), netstat (0.008), Cobian RAT (0.003), Visual Basic (0.002), CrossRAT (0.001), Cardinal RAT (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → cmd (13 neighbors, 13 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → BOULDSPY (25 neighbors, 25 edges)
           → Software Discovery (56 neighbors, 56 edges)
           → Systeminfo (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 7/7: แจกแจงรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่าย...
[RETRIEVE] Query: แจกแจงรายชื่อไฟล์และโฟลเดอร์บนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BBSRAT (0.188), CrackMapExec (0.154), Nebulae (0.145), Proxysvc (0.129), ROADTools (0.105), Forfiles (0.032), File and Directory Discovery (0.023), Tasklist (0.004), Firewall Enumeration (0.002), ipconfig (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BBSRAT (14 neighbors, 14 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
           → Nebulae (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [62/100] retrieved=431 relevant=5 latency=13226ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 30 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเอกสารราชการในเครื่องคอมพ...
[RETRIEVE] Query: เมื่อวันที่ 30 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเอกสารราชการในเครื่องคอมพ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.112), Koadic (0.036), P.A.S. Webshell (0.002), RDP Hijacking (0.002), Remote Desktop Protocol (0.001), ZxShell (0.001), File Deletion (0.000), Ingress Tool Transfer (0.000), System Script Proxy Execution (0.000), Remote Services (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Koadic (31 neighbors, 31 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมขโมยเอกสารแก้ไขทะเบียนระบบเปลี่ยนโปรแกรมเริ่มต้นเมื่อเปิดไฟล์เอกสาร...
[RETRIEVE] Query: โปรแกรมขโมยเอกสารแก้ไขทะเบียนระบบเปลี่ยนโปรแกรมเริ่มต้นเมื่อเปิดไฟล์เอกสาร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kimsuky (0.785), Change Default File Association (0.068), Bankshot (0.009), Modify Registry (0.007), FELIXROOT (0.006), LP-Notes (0.006), Reg (0.003), Windows Registry Key Modification (0.002), Overwrite Process Arguments (0.000), Office Template Macros (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Kimsuky (150 neighbors, 150 edges)
           → Change Default File Association (7 neighbors, 7 edges)
           → Bankshot (26 neighbors, 26 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → FELIXROOT (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 3/8: โปรแกรมของคนร้ายถูกเรียกทำงานอัตโนมัติทุกครั้งที่เปิดเอกสารชนิดนั้น...
[RETRIEVE] Query: โปรแกรมของคนร้ายถูกเรียกทำงานอัตโนมัติทุกครั้งที่เปิดเอกสารชนิดนั้น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Change Default File Association (0.179), Re-opened Applications (0.164), AutoIt backdoor (0.046), xCaon (0.030), ccf32 (0.003), Visual Basic (0.001), Cardinal RAT (0.001), Cobian RAT (0.000), CrossRAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Change Default File Association (7 neighbors, 7 edges)
           → Re-opened Applications (7 neighbors, 7 edges)
           → AutoIt backdoor (6 neighbors, 6 edges)
           → xCaon (12 neighbors, 12 edges)
           → Boot or Logon Autostart Execution (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 4/8: คัดลอกเอกสารราชการออกจากเครื่องคอมพิวเตอร์เจ้าหน้าที่...
[RETRIEVE] Query: คัดลอกเอกสารราชการออกจากเครื่องคอมพิวเตอร์เจ้าหน้าที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AuTo Stealer (0.001), Octopus (0.001), cmd (0.001), Clipboard Data (0.000), File Deletion (0.000), Office Template Macros (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AuTo Stealer (11 neighbors, 11 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Octopus (20 neighbors, 20 edges)
           → Clipboard Data (48 neighbors, 48 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 5/8: Web Shell ดัดแปลงจากโครงการโอเพนซอร์ซอัปโหลดบนเครื่องแม่ข่าย...
[RETRIEVE] Query: Web Shell ดัดแปลงจากโครงการโอเพนซอร์ซอัปโหลดบนเครื่องแม่ข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Web Shell (0.085), Caterpillar WebShell (0.009), P.A.S. Webshell (0.008), P.A.S. Webshell (0.008), China Chopper (0.006), Netsh Helper DLL (0.005), SEASHARPEE (0.003), SUPERNOVA (0.003), SSH Hijacking (0.001), netsh (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Web Shell (71 neighbors, 71 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Caterpillar WebShell (16 neighbors, 16 edges)
           → Netsh Helper DLL (6 neighbors, 6 edges)
           → China Chopper (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 6/8: Web Shell ใช้อัปโหลด ดาวน์โหลด และลบไฟล์กับโฟลเดอร์บนเว็บไซต์...
[RETRIEVE] Query: Web Shell ใช้อัปโหลด ดาวน์โหลด และลบไฟล์กับโฟลเดอร์บนเว็บไซต์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Web Shell (0.469), RAPIDPULSE (0.314), BUSHWALK (0.195), P.A.S. Webshell (0.177), Caterpillar WebShell (0.083), China Chopper (0.066), Netsh Helper DLL (0.050), SUPERNOVA (0.042), SSH Hijacking (0.003), Unix Shell (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Web Shell (71 neighbors, 71 edges)
           → RAPIDPULSE (5 neighbors, 5 edges)
           → BUSHWALK (7 neighbors, 7 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Caterpillar WebShell (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 7/8: เพิ่มบัญชีผู้ดูแลระบบวินโดวส์ขึ้นใหม่...
[RETRIEVE] Query: เพิ่มบัญชีผู้ดูแลระบบวินโดวส์ขึ้นใหม่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kimsuky (0.441), Operating System Configuration (0.044), User Account Control (0.016), Indrik Spider (0.014), Local Account (0.011), Additional Local or Domain Groups (0.005), Additional Cloud Roles (0.004), Kimsuky (0.003), Windows Credential Manager (0.000), Parent PID Spoofing (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Kimsuky (150 neighbors, 150 edges)
           → Local Accounts (33 neighbors, 33 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
           → Domain Account (65 neighbors, 65 edges)
           → User Account Control (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 8/8: เปิดใช้งาน Remote Desktop Protocol หลบเลี่ยงกฎไฟร์วอลล์...
[RETRIEVE] Query: เปิดใช้งาน Remote Desktop Protocol หลบเลี่ยงกฎไฟร์วอลล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Network Segmentation (0.715), Koadic (0.036), RDP Hijacking (0.032), Remote Desktop Protocol (0.019), Pupy (0.015), VNC (0.012), Axiom (0.006), Terminal Services DLL (0.003), Non-Standard Port (0.000), Remote Services (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Network Segmentation (37 neighbors, 37 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Koadic (31 neighbors, 31 edges)
           → Pupy (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [63/100] retrieved=411 relevant=3 latency=15479ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 18 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกลุก...
[RETRIEVE] Query: เมื่อวันที่ 18 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกลุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN8 (0.002), POWRUNER (0.001), POWRUNER (0.000), Ingress Tool Transfer (0.000), Gamaredon Group (0.000), Winlogon Helper DLL (0.000), Named Pipe Metadata (0.000), Exploitation for Privilege Escalation (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 2/5: ใช้ชื่อผู้ใช้และรหัสผ่านที่ค้นพบเพื่อเปิดการเชื่อมต่อ RDP ไปยังเครื่องแม่ข่ายควบ...
[RETRIEVE] Query: ใช้ชื่อผู้ใช้และรหัสผ่านที่ค้นพบเพื่อเปิดการเชื่อมต่อ RDP ไปยังเครื่องแม่ข่ายควบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Volt Typhoon (0.065), Remote Service Session Hijacking (0.017), Remote Desktop Protocol (0.005), RDP Hijacking (0.004), Remote Services (0.003), Chimera (0.002), Terminal Services DLL (0.001), Limit Access to Resource Over Network (0.001), Axiom (0.001), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Volt Typhoon (100 neighbors, 100 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Remote Service Session Hijacking (9 neighbors, 9 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Remote Services (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 3/5: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่ไปยังเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: ดาวน์โหลดไฟล์โปรแกรมชุดใหม่ไปยังเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AppDomainManager (0.015), Mongall (0.006), BONDUPDATER (0.004), BoomBox (0.002), dsquery (0.001), Impacket (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AppDomainManager (6 neighbors, 6 edges)
           → Mongall (16 neighbors, 16 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → BONDUPDATER (8 neighbors, 8 edges)
           → BoomBox (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 4/5: สั่งให้โปรแกรมทำงานผ่านการเชื่อมต่อ RDP...
[RETRIEVE] Query: สั่งให้โปรแกรมทำงานผ่านการเชื่อมต่อ RDP...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pupy (0.331), ServHelper (0.239), Terminal Services DLL (0.095), Remote Service Session Hijacking (0.059), Chimera (0.057), Axiom (0.045), RDP Hijacking (0.026), Remote Desktop Protocol (0.022), Application Layer Protocol (0.004), Clear Network Connection History and Configurations (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pupy (43 neighbors, 43 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → ServHelper (16 neighbors, 16 edges)
           → Terminal Services DLL (5 neighbors, 5 edges)
           → Remote Service Session Hijacking (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 5/5: แก้ไขทะเบียนระบบ Windows Logon Process เพื่อเพิ่มไฟล์โปรแกรมของคนร้ายให้ทำงานระห...
[RETRIEVE] Query: แก้ไขทะเบียนระบบ Windows Logon Process เพื่อเพิ่มไฟล์โปรแกรมของคนร้ายให้ทำงานระห...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NPPSPY (0.572), Winlogon Helper DLL (0.099), Network Provider DLL (0.080), Logon Script (Windows) (0.035), DarkComet (0.014), Modify Registry (0.013), Logon Session Creation (0.000), Cardinal RAT (0.000), WinMM (0.000), Process Argument Spoofing (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → NPPSPY (7 neighbors, 7 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → Winlogon Helper DLL (20 neighbors, 20 edges)
           → Network Provider DLL (9 neighbors, 9 edges)
           → Logon Script (Windows) (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [64/100] retrieved=687 relevant=3 latency=11159ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 24 กรกฎาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการสำรวจ...
[RETRIEVE] Query: เมื่อวันที่ 24 กรกฎาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการสำรวจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Net (0.018), menuPass (0.007), Remote System Discovery (0.004), System Network Connections Discovery (0.002), Process Discovery (0.000), FIN8 (0.000), Cloud Accounts (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Password Policies (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Net (50 neighbors, 50 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → menuPass (71 neighbors, 71 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
           → Process Discovery (320 neighbors, 320 edges)
[RETRIEVE-QUOTA] Query 2/5: การอ่านค่าในทะเบียนระบบ RDP เพื่อค้นหาประวัติเครื่องปลายทางที่เชื่อมต่อ...
[RETRIEVE] Query: การอ่านค่าในทะเบียนระบบ RDP เพื่อค้นหาประวัติเครื่องปลายทางที่เชื่อมต่อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Earth Lusca (0.232), APT41 (0.107), Clear Network Connection History and Configurations (0.004), Remote System Discovery (0.002), netstat (0.001), RDP Hijacking (0.001), Chimera (0.001), Remote Desktop Protocol (0.001), Terminal Services DLL (0.001), Axiom (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Earth Lusca (53 neighbors, 53 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → APT41 (116 neighbors, 116 edges)
           → Query Registry (121 neighbors, 121 edges)
           → Clear Network Connection History and Configurations (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/5: การใช้คำสั่งระบบผ่านหน้าต่างคำสั่งเพื่อสอบถามรายละเอียดบัญชีผู้ใช้ในโดเมน...
[RETRIEVE] Query: การใช้คำสั่งระบบผ่านหน้าต่างคำสั่งเพื่อสอบถามรายละเอียดบัญชีผู้ใช้ในโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Net (0.752), FIN13 (0.579), Domain Account (0.455), SILENTTRINITY (0.358), Domain Account (0.096), Local Account (0.028), BISCUIT (0.009), Additional Local or Domain Groups (0.008), Domain Accounts (0.003), Active Directory Credential Request (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Net (50 neighbors, 50 edges)
           → Domain Account (65 neighbors, 65 edges)
           → FIN13 (57 neighbors, 57 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Domain Account (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 4/5: การสอบถามสมาชิกของกลุ่มสิทธิ์ที่ดูแลระบบฐานข้อมูล...
[RETRIEVE] Query: การสอบถามสมาชิกของกลุ่มสิทธิ์ที่ดูแลระบบฐานข้อมูล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Local Groups (0.007), Group Metadata (0.003), APT3 (0.001), Cloud Groups (0.001), Active Directory Credential Request (0.001), Domain Groups (0.001), OSInfo (0.000), Poseidon Group (0.000), Poseidon Group (0.000), Domain Account (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Local Groups (35 neighbors, 35 edges)
           → Group Metadata (0 neighbors, 0 edges)
           → Cloud Groups (7 neighbors, 7 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → APT3 (50 neighbors, 50 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] Query 5/5: การใช้คำสั่งสอบถามชื่อโดเมน (DNS query) เพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายเป...
[RETRIEVE] Query: การใช้คำสั่งสอบถามชื่อโดเมน (DNS query) เพื่อค้นหาหมายเลขไอพีของเครื่องแม่ข่ายเป...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Active DNS (0.454), DNS/Passive DNS (0.430), DEADEYE (0.325), DNS (0.104), LazyWiper (0.041), DNS Calculation (0.028), dsquery (0.015), Samurai (0.001), Name Resolution Poisoning and SMB Relay (0.001), Bazar (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DNS/Passive DNS (3 neighbors, 3 edges)
           → Active DNS (0 neighbors, 0 edges)
           → DEADEYE (13 neighbors, 13 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → DNS (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [65/100] retrieved=552 relevant=4 latency=11263ms
[RETRIEVE-QUOTA] Query 1/11: เมื่อวันที่ 21 พฤศจิกายน 2565 บริษัทแห่งหนึ่งแจ้งความว่าข้อมูลในระบบถูกเข้ารหัสล...
[RETRIEVE] Query: เมื่อวันที่ 21 พฤศจิกายน 2565 บริษัทแห่งหนึ่งแจ้งความว่าข้อมูลในระบบถูกเข้ารหัสล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: INC Ransomware (0.034), ThiefQuest (0.018), Data Encrypted for Impact (0.003), Inhibit System Recovery (0.002), Evil Twin (0.000), ARP Cache Poisoning (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), Adversary-in-the-Middle (0.000), Clear Windows Event Logs (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → INC Ransomware (16 neighbors, 16 edges)
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → ThiefQuest (18 neighbors, 18 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → Evil Twin (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 2/11: ปิดการทำงานของบริการ Volume Shadow Copy เพื่อลบสำเนาเงา...
[RETRIEVE] Query: ปิดการทำงานของบริการ Volume Shadow Copy เพื่อลบสำเนาเงา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HermeticWiper (0.921), Conti (0.520), Inhibit System Recovery (0.274), Snapshot Deletion (0.001), Volume Deletion (0.001), Direct Volume Access (0.000), /etc/passwd and /etc/shadow (0.000), NTDS (0.000), Volume Modification (0.000), Volume Creation (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → HermeticWiper (26 neighbors, 26 edges)
           → Service Stop (61 neighbors, 61 edges)
           → Conti (18 neighbors, 18 edges)
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → Snapshot Deletion (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 3/11: ลบสำเนาเงาของไฟล์ผ่านหน้าต่างคำสั่ง (Command Line)...
[RETRIEVE] Query: ลบสำเนาเงาของไฟล์ผ่านหน้าต่างคำสั่ง (Command Line)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Black Basta (0.887), REvil (0.862), Command Obfuscation (0.075), Overwrite Process Arguments (0.003), Prevent Command History Logging (0.001), Line Dancer (0.000), Line Runner (0.000), Cloud Administration Command (0.000), Line Runner (0.000), Line Runner (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Black Basta (27 neighbors, 27 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → REvil (37 neighbors, 37 edges)
           → Command Obfuscation (74 neighbors, 74 edges)
           → Overwrite Process Arguments (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] Query 4/11: ลบสำเนาเงาของไฟล์ผ่านสคริปต์...
[RETRIEVE] Query: ลบสำเนาเงาของไฟล์ผ่านสคริปต์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RansomHub (0.532), Black Basta (0.394), Inhibit System Recovery (0.002), Invoke-PSImage (0.002), Overwrite Process Arguments (0.001), CrossRAT (0.000), Visual Basic (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RansomHub (21 neighbors, 21 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Black Basta (27 neighbors, 27 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Inhibit System Recovery (62 neighbors, 62 edges)
[RETRIEVE-QUOTA] Query 5/11: ลบไฟล์บันทึกเหตุการณ์ของวินโดวส์ (Windows Event Log deletion)...
[RETRIEVE] Query: ลบไฟล์บันทึกเหตุการณ์ของวินโดวส์ (Windows Event Log deletion)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mafalda (0.949), BlackCat (0.856), Clear Windows Event Logs (0.828), Restrict File and Directory Permissions (0.651), Windows Registry Key Deletion (0.562), Disable or Modify Windows Event Log (0.489), Volume Deletion (0.020), Windows Registry Key Modification (0.018), Active Directory Object Deletion (0.003), Image Deletion (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Mafalda (37 neighbors, 37 edges)
           → BlackCat (22 neighbors, 22 edges)
           → Restrict File and Directory Permissions (60 neighbors, 60 edges)
           → Disable or Modify Windows Event Log (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 6/11: ลบบันทึกเหตุการณ์ระบบ เหตุการณ์ด้านความปลอดภัย และเหตุการณ์แอปพลิเคชัน...
[RETRIEVE] Query: ลบบันทึกเหตุการณ์ระบบ เหตุการณ์ด้านความปลอดภัย และเหตุการณ์แอปพลิเคชัน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Meteor (0.968), RansomHub (0.958), Clear Windows Event Logs (0.887), Disable or Modify Windows Event Log (0.247), Active Directory Object Deletion (0.002), Snapshot Deletion (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Meteor (20 neighbors, 20 edges)
           → RansomHub (21 neighbors, 21 edges)
           → Disable or Modify Windows Event Log (12 neighbors, 12 edges)
           → Active Directory Object Deletion (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 7/11: แก้ไขทะเบียนระบบเพื่อลบฐานข้อมูลลายเซ็นไวรัส...
[RETRIEVE] Query: แก้ไขทะเบียนระบบเพื่อลบฐานข้อมูลลายเซ็นไวรัส...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BACKSPACE (0.058), Mori (0.057), ADVSTORESHELL (0.033), Clambling (0.013), Modify Registry (0.004), Windows Registry Key Modification (0.001), Windows Registry Key Deletion (0.000), Restrict Registry Permissions (0.000), Modify Authentication Process (0.000), Lslsass (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BACKSPACE (15 neighbors, 15 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → Mori (10 neighbors, 10 edges)
           → ADVSTORESHELL (24 neighbors, 24 edges)
           → Clambling (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 8/11: ปิดการทำงานของโปรแกรมป้องกันไวรัส (Antivirus Disabling)...
[RETRIEVE] Query: ปิดการทำงานของโปรแกรมป้องกันไวรัส (Antivirus Disabling)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pysa (0.300), TinyZBot (0.121), Disable or Remove Feature or Program (0.023), Antivirus/Antimalware (0.022), Firewall Disable (0.009), Cloud Service Disable (0.002), Execution Prevention (0.002), Clambling (0.001), Clambling (0.000), Clambling (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pysa (16 neighbors, 16 edges)
           → Disable or Modify Tools (142 neighbors, 142 edges)
           → TinyZBot (9 neighbors, 9 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → Antivirus/Antimalware (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 9/11: ส่งข้อมูลบริษัทไปยังบริการรับฝากข้อมูลออนไลน์ (Cloud Storage Exfiltration)...
[RETRIEVE] Query: ส่งข้อมูลบริษัทไปยังบริการรับฝากข้อมูลออนไลน์ (Cloud Storage Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration to Cloud Storage (0.626), ROKRAT (0.445), HAMMERTOSS (0.357), Rclone (0.340), Transfer Data to Cloud Account (0.310), Empire (0.097), Exfiltration Over Web Service (0.019), Exfiltration Over Alternative Protocol (0.017), Exfiltration to Text Storage Sites (0.010), Exfiltration (0.007)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration to Cloud Storage (48 neighbors, 48 edges)
           → ROKRAT (31 neighbors, 31 edges)
           → Transfer Data to Cloud Account (9 neighbors, 9 edges)
           → HAMMERTOSS (8 neighbors, 8 edges)
           → Rclone (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 10/11: เข้ารหัสข้อมูลทั้งหมดในระบบ (Ransomware Encryption)...
[RETRIEVE] Query: เข้ารหัสข้อมูลทั้งหมดในระบบ (Ransomware Encryption)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Data Encrypted for Impact (0.594), INC Ransomware (0.565), BlackByte Ransomware (0.292), ShrinkLocker (0.144), INC Ransom (0.079), BlackByte (0.057), Playcrypt (0.032), Cheerscrypt (0.017), BlackByte Ransomware (0.015), Akira (0.015)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → INC Ransomware (16 neighbors, 16 edges)
           → BlackByte Ransomware (22 neighbors, 22 edges)
           → ShrinkLocker (21 neighbors, 21 edges)
           → INC Ransom (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 11/11: วางไฟล์ข้อความเรียกค่าไถ่ในโฟลเดอร์ที่ได้รับผลกระทบ...
[RETRIEVE] Query: วางไฟล์ข้อความเรียกค่าไถ่ในโฟลเดอร์ที่ได้รับผลกระทบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.006), Pisloader (0.002), Path Interception by PATH Environment Variable (0.002), Template Injection (0.001), FIN7 (0.000), KernelCallbackTable (0.000), CallMe (0.000), Asynchronous Procedure Call (0.000), ListPlanting (0.000), Additional Email Delegate Permissions (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Path Interception by PATH Environment Variable (11 neighbors, 11 edges)
           → Pisloader (10 neighbors, 10 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 11 queries
  [66/100] retrieved=187 relevant=6 latency=22611ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 21 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้...
[RETRIEVE] Query: เมื่อวันที่ 21 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Crimson (0.344), KeyBoy (0.155), PowerSploit (0.038), LaZagne (0.023), Unsecured Credentials (0.018), Password Managers (0.006), Registry Run Keys / Startup Folder (0.004), Credentials from Web Browsers (0.003), Credentials in Registry (0.002), Windows Credential Manager (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Crimson (32 neighbors, 32 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → KeyBoy (19 neighbors, 19 edges)
           → PowerSploit (39 neighbors, 39 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 2/7: โปรแกรมขโมยรหัสผ่าน (Stealer) ฝังในเครื่องคอมพิวเตอร์เจ้าหน้าที่...
[RETRIEVE] Query: โปรแกรมขโมยรหัสผ่าน (Stealer) ฝังในเครื่องคอมพิวเตอร์เจ้าหน้าที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AuTo Stealer (0.647), MirrorStealer (0.243), Troll Stealer (0.056), StrelaStealer (0.027), AuTo Stealer (0.023), Net Crawler (0.022), USBStealer (0.017), Troll Stealer (0.017), USBStealer (0.006), USBStealer (0.006)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AuTo Stealer (11 neighbors, 11 edges)
           → MirrorStealer (5 neighbors, 5 edges)
           → Troll Stealer (23 neighbors, 23 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → StrelaStealer (34 neighbors, 34 edges)
[RETRIEVE-QUOTA] Query 3/7: เพิ่มรายการเรียกใช้งานโปรแกรมในRegistry Run Key เพื่อ Persistence...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานโปรแกรมในRegistry Run Key เพื่อ Persistence...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.931), PLAINTEE (0.839), RCSession (0.668), Cardinal RAT (0.662), PowerSploit (0.605), Active Setup (0.435), Boot or Logon Autostart Execution (0.046), RC Scripts (0.017), Persistence (0.002), Login Hook (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → PLAINTEE (10 neighbors, 10 edges)
           → RCSession (24 neighbors, 24 edges)
           → Cardinal RAT (22 neighbors, 22 edges)
           → PowerSploit (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 4/7: เพิ่มโปรแกรมในโฟลเดอร์เริ่มต้นระบบ (Startup Folder) เพื่อ Persistence...
[RETRIEVE] Query: เพิ่มโปรแกรมในโฟลเดอร์เริ่มต้นระบบ (Startup Folder) เพื่อ Persistence...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.971), PLAINTEE (0.933), Helminth (0.917), Cardinal RAT (0.843), PowerSploit (0.687), Startup Items (0.479), RC Scripts (0.175), Persistence (0.133), Create or Modify System Process (0.010), Clear Persistence (0.005)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → PLAINTEE (10 neighbors, 10 edges)
           → Helminth (22 neighbors, 22 edges)
           → Cardinal RAT (22 neighbors, 22 edges)
           → PowerSploit (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 5/7: หลบเลี่ยงกลไก UAC (User Account Control) เพื่อยกระดับสิทธิ์เป็น Administrator...
[RETRIEVE] Query: หลบเลี่ยงกลไก UAC (User Account Control) เพื่อยกระดับสิทธิ์เป็น Administrator...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bypass User Account Control (0.988), RCSession (0.956), User Account Control (0.952), Koadic (0.854), User Account Control (0.832), User Account Control (0.820), Abuse Elevation Control Mechanism (0.728), UACMe (0.480), Privileged Account Management (0.016), Additional Container Cluster Roles (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bypass User Account Control (70 neighbors, 70 edges)
           → RCSession (24 neighbors, 24 edges)
           → User Account Control (7 neighbors, 7 edges)
           → Abuse Elevation Control Mechanism (18 neighbors, 18 edges)
           → Koadic (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 6/7: อ่าน Credentials from Web Browsers ที่บันทึกในเครื่อง...
[RETRIEVE] Query: อ่าน Credentials from Web Browsers ที่บันทึกในเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.959), PLEAD (0.743), LaZagne (0.497), SUGARDUMP (0.423), Windows Credential Manager (0.040), Forge Web Credentials (0.013), Credentials in Registry (0.008), Web Credential Usage (0.006), Browser Information Discovery (0.005), Credentials (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → PLEAD (16 neighbors, 16 edges)
           → LaZagne (22 neighbors, 22 edges)
           → SUGARDUMP (14 neighbors, 14 edges)
           → Windows Credential Manager (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งรหัสผ่านและชื่อผู้ใช้ออกไปยังคนร้าย (Exfiltration)...
[RETRIEVE] Query: ส่งรหัสผ่านและชื่อผู้ใช้ออกไปยังคนร้าย (Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration (0.137), Exfiltration Over Physical Medium (0.098), Exfiltration Over Alternative Protocol (0.093), InnaputRAT (0.047), HAMMERTOSS (0.044), Exbyte (0.022), Exbyte (0.021), Exploitation for Credential Access (0.013), Empire (0.012), Exodus (0.006)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration (19 neighbors, 19 edges)
           → Exfiltration Over Physical Medium (6 neighbors, 6 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → HAMMERTOSS (8 neighbors, 8 edges)
           → Exfiltration to Cloud Storage (48 neighbors, 48 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [67/100] retrieved=185 relevant=3 latency=12646ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 11 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าข้อมูลที่รวบ...
[RETRIEVE] Query: เมื่อวันที่ 11 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าข้อมูลที่รวบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MobileOrder (0.002), WellMail (0.002), Ingress Tool Transfer (0.001), Data from Local System (0.000), Windows Management Instrumentation (0.000), FIN8 (0.000), Exploitation of Remote Services (0.000), Pikabot (0.000), Cloud Accounts (0.000), Browser Extensions (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → MobileOrder (8 neighbors, 8 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → WellMail (10 neighbors, 10 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
[RETRIEVE-QUOTA] Query 2/7: เปิดการเชื่อมต่อแบบโต้ตอบไปยังเครื่องแม่ข่ายภายนอกองค์กร...
[RETRIEVE] Query: เปิดการเชื่อมต่อแบบโต้ตอบไปยังเครื่องแม่ข่ายภายนอกองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Proxy (0.001), SSH (0.001), metaMain (0.001), Hikit (0.001), Responder (0.001), Non-Application Layer Protocol (0.000), Out-of-Band Communications Channel (0.000), Cobalt Strike (0.000), Cobalt Strike (0.000), Out1 (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → External Proxy (27 neighbors, 27 edges)
           → SSH (33 neighbors, 33 edges)
           → metaMain (29 neighbors, 29 edges)
           → Non-Application Layer Protocol (114 neighbors, 114 edges)
           → Hikit (12 neighbors, 12 edges)
           → Internal Proxy (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 3/7: ใช้โปรแกรมคัดลอกไฟล์ผ่านช่องทางเข้ารหัสลำเลียงข้อมูลออกไปเก็บบนเครื่องปลายทาง...
[RETRIEVE] Query: ใช้โปรแกรมคัดลอกไฟล์ผ่านช่องทางเข้ารหัสลำเลียงข้อมูลออกไปเก็บบนเครื่องปลายทาง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sliver (0.220), cmd (0.113), ftp (0.058), Rover (0.024), IMAPLoader (0.007), Exfiltration Over C2 Channel (0.005), Exfiltration Over Alternative Protocol (0.004), Archive via Utility (0.004), Deobfuscate/Decode Files or Information (0.001), Software Packing (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Sliver (27 neighbors, 27 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → cmd (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → ftp (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 4/7: ส่งข้อมูลที่รวบรวมไว้ออกนอกองค์กร (exfiltration)...
[RETRIEVE] Query: ส่งข้อมูลที่รวบรวมไว้ออกนอกองค์กร (exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Automated Exfiltration (0.670), Exfiltration (0.400), Machete (0.210), Archive Collected Data (0.146), Exfiltration Over Alternative Protocol (0.084), Salesforce Data Exfiltration (0.084), Exfiltration Over Other Network Medium (0.072), APT28 Nearest Neighbor Campaign (0.034), Empire (0.019), Exodus (0.012)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Automated Exfiltration (33 neighbors, 33 edges)
           → Exfiltration (19 neighbors, 19 edges)
           → Machete (42 neighbors, 42 edges)
           → Archive Collected Data (62 neighbors, 62 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 5/7: ใช้เครื่องมือสั่งงานระยะไกลสร้างบริการของระบบบนเครื่องปลายทาง...
[RETRIEVE] Query: ใช้เครื่องมือสั่งงานระยะไกลสร้างบริการของระบบบนเครื่องปลายทาง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.618), RemoteCMD (0.388), Remote Access Hardware (0.267), QakBot (0.206), xCmd (0.139), Remote Access Tools (0.045), xCmd (0.022), Emissary (0.021), Terminal Services DLL (0.015), Software Deployment Tools (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Remote Access Hardware (4 neighbors, 4 edges)
           → QakBot (74 neighbors, 74 edges)
           → Windows Service (150 neighbors, 150 edges)
[RETRIEVE-QUOTA] Query 6/7: สั่งรันคำสั่งบนเครื่องปลายทางจากระยะไกล...
[RETRIEVE] Query: สั่งรันคำสั่งบนเครื่องปลายทางจากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.768), RemoteCMD (0.580), RemoteCMD (0.364), xCmd (0.130), Windows Command Shell (0.067), Cobian RAT (0.007), CrossRAT (0.002), Visual Basic (0.001), Cardinal RAT (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → xCmd (2 neighbors, 2 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 7/7: ใช้กลไกบริหารจัดการเครื่องของวินโดวส์สั่งให้กระบวนการทำงานบนเครื่องปลายทางอื่น...
[RETRIEVE] Query: ใช้กลไกบริหารจัดการเครื่องของวินโดวส์สั่งให้กระบวนการทำงานบนเครื่องปลายทางอื่น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: HermeticWizard (0.812), PsExec (0.042), Winexe (0.042), Koadic (0.029), Windows Remote Management (0.028), Windows Command Shell (0.025), Koadic (0.022), ECCENTRICBANDWAGON (0.017), Service Execution (0.008), KernelCallbackTable (0.006)
[RETRIEVE] Graph expansion: 5 subgraphs
           → HermeticWizard (16 neighbors, 16 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Windows Remote Management (16 neighbors, 16 edges)
           → PsExec (49 neighbors, 49 edges)
           → Winexe (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [68/100] retrieved=686 relevant=3 latency=13196ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 17 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดเค...
[RETRIEVE] Query: เมื่อวันที่ 17 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดเค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.054), Bankshot (0.049), APT-C-36 (0.030), Data Encrypted for Impact (0.014), APT-C-36 (0.011), Ursnif (0.008), Ingress Tool Transfer (0.000), Input Injection (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/6: ไฟล์แบตช์นำไฟล์สคริปต์ไปวางบนเครื่องผู้เสียหายหลายเครื่อง...
[RETRIEVE] Query: ไฟล์แบตช์นำไฟล์สคริปต์ไปวางบนเครื่องผู้เสียหายหลายเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Taint Shared Content (0.013), Lateral Tool Transfer (0.008), Bankshot (0.006), TrickBot (0.005), SLOTHFULMEDIA (0.005), Ingress Tool Transfer (0.005), Data Encrypted for Impact (0.002), Input Injection (0.001), FIN7 (0.001), Internal Spearphishing (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Taint Shared Content (18 neighbors, 18 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → TrickBot (57 neighbors, 57 edges)
[RETRIEVE-QUOTA] Query 3/6: ลบไฟล์บันทึกเหตุการณ์ Windows Event Log เป็นจำนวนมาก...
[RETRIEVE] Query: ลบไฟล์บันทึกเหตุการณ์ Windows Event Log เป็นจำนวนมาก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mafalda (0.400), Clear Windows Event Logs (0.345), BlackCat (0.252), Qilin (0.114), Disable or Modify Windows Event Log (0.095), Windows Registry Key Deletion (0.018), Volume Deletion (0.007), Service Creation (0.001), Windows Registry Key Modification (0.001), Active Directory Object Deletion (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Mafalda (37 neighbors, 37 edges)
           → BlackCat (22 neighbors, 22 edges)
           → Disable or Modify Windows Event Log (12 neighbors, 12 edges)
           → Qilin (54 neighbors, 54 edges)
[RETRIEVE-QUOTA] Query 4/6: ลบบันทึกเหตุการณ์ระบบ แอปพลิเคชัน และความปลอดภัย...
[RETRIEVE] Query: ลบบันทึกเหตุการณ์ระบบ แอปพลิเคชัน และความปลอดภัย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Meteor (0.964), RansomHub (0.954), Clear Windows Event Logs (0.927), Disable or Modify Windows Event Log (0.393), Active Directory Object Deletion (0.002), Snapshot Deletion (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Meteor (20 neighbors, 20 edges)
           → RansomHub (21 neighbors, 21 edges)
           → Disable or Modify Windows Event Log (12 neighbors, 12 edges)
           → Active Directory Object Deletion (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 5/6: ติดตั้งซอฟต์แวร์ควบคุมเครื่องระยะไกล (Remote Access Software) เพื่อคงการเข้าถึง...
[RETRIEVE] Query: ติดตั้งซอฟต์แวร์ควบคุมเครื่องระยะไกล (Remote Access Software) เพื่อคงการเข้าถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Execution Prevention (0.449), Execution Prevention (0.437), Remote Access Tools (0.196), User Guidance (0.117), Remote Access Hardware (0.090), Medusa Group (0.051), RemoteCMD (0.033), RemoteUtilities (0.032), Remote Desktop Software (0.017), Emotet (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Execution Prevention (79 neighbors, 79 edges)
           → Remote Desktop Software (21 neighbors, 21 edges)
           → Remote Access Tools (31 neighbors, 31 edges)
           → User Guidance (49 neighbors, 49 edges)
           → Remote Access Software (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 6/6: ปล่อยโปรแกรมเรียกค่าไถ่ (Ransomware) เข้ารหัสลับข้อมูล...
[RETRIEVE] Query: ปล่อยโปรแกรมเรียกค่าไถ่ (Ransomware) เข้ารหัสลับข้อมูล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA505 (0.733), INC Ransomware (0.675), INC Ransom (0.445), ShrinkLocker (0.419), AvosLocker (0.063), INC Ransom (0.034), Avaddon (0.025), RansomHub (0.007), Akira (0.005), IcedID (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → TA505 (50 neighbors, 50 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → INC Ransomware (16 neighbors, 16 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → INC Ransom (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [69/100] retrieved=786 relevant=3 latency=12364ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 20 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการเชื่...
[RETRIEVE] Query: เมื่อวันที่ 20 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการเชื่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.007), Bankshot (0.003), FIN8 (0.001), Salesforce Data Exfiltration (0.000), DNS (0.000), FrostyGoop Incident (0.000), Valid Accounts (0.000), Domain Accounts (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Local Account (69 neighbors, 69 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/5: DNS tunneling เพื่อห่อหุ้มการติดต่อสั่งการและส่งข้อมูลออกไปภายนอก...
[RETRIEVE] Query: DNS tunneling เพื่อห่อหุ้มการติดต่อสั่งการและส่งข้อมูลออกไปภายนอก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Protocol Tunneling (0.186), Mori (0.067), WellMess (0.062), Heyoka Backdoor (0.044), DNS (0.040), Domain Fronting (0.025), FRP (0.015), DNS Server (0.008), IDE Tunneling (0.005), DNS (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Protocol Tunneling (46 neighbors, 46 edges)
           → Mori (10 neighbors, 10 edges)
           → DNS (60 neighbors, 60 edges)
           → WellMess (16 neighbors, 16 edges)
           → Heyoka Backdoor (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 3/5: การรันคำสั่งตรวจสอบสถานะเซสชันเพื่อค้นหาผู้บริหารฝ่ายการเงินที่ล็อกอินอยู่...
[RETRIEVE] Query: การรันคำสั่งตรวจสอบสถานะเซสชันเพื่อค้นหาผู้บริหารฝ่ายการเงินที่ล็อกอินอยู่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: StrongPity (0.022), FIN8 (0.011), RCSession (0.002), AsyncRAT (0.002), System Owner/User Discovery (0.001), BISCUIT (0.000), RDP Hijacking (0.000), Process Discovery (0.000), Account Discovery (0.000), Account Use Policies (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → StrongPity (28 neighbors, 28 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → FIN8 (47 neighbors, 47 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → AsyncRAT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 4/5: อัปโหลดไฟล์โปรแกรมและสคริปต์ลงบนเครื่องผู้บริหาร...
[RETRIEVE] Query: อัปโหลดไฟล์โปรแกรมและสคริปต์ลงบนเครื่องผู้บริหาร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PsExec (0.027), BITSAdmin (0.023), Okrum (0.009), cmd (0.003), Wevtutil (0.003), Installer Packages (0.002), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BITSAdmin (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → PsExec (49 neighbors, 49 edges)
           → Okrum (35 neighbors, 35 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 5/5: ปลอมแปลงชื่อไฟล์เป็นตัวปรับปรุงซอฟต์แวร์เพื่อหลีกเลี่ยงการลบอัตโนมัติ...
[RETRIEVE] Query: ปลอมแปลงชื่อไฟล์เป็นตัวปรับปรุงซอฟต์แวร์เพื่อหลีกเลี่ยงการลบอัตโนมัติ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PlugX (0.025), Polymorphic Code (0.016), Update Software (0.011), Timestomp (0.005), Rename Legitimate Utilities (0.002), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PlugX (65 neighbors, 65 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Polymorphic Code (5 neighbors, 5 edges)
           → Update Software (42 neighbors, 42 edges)
           → Hijack Execution Flow (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [70/100] retrieved=276 relevant=3 latency=10862ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 19 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Query: เมื่อวันที่ 19 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PUNCHTRACK (0.035), RawPOS (0.001), Exfiltration to Text Storage Sites (0.000), FIN8 (0.000), Hijack Execution Flow (0.000), Event Triggered Execution (0.000), Password Managers (0.000), Pikabot (0.000), Process Injection (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → PUNCHTRACK (4 neighbors, 4 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → RawPOS (6 neighbors, 6 edges)
           → Exfiltration to Text Storage Sites (4 neighbors, 4 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/6: เพิ่มรายการเรียกใช้งานโปรแกรมในทะเบียนระบบ (Registry Run Key Persistence)...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานโปรแกรมในทะเบียนระบบ (Registry Run Key Persistence)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Registry Run Keys / Startup Folder (0.828), PLAINTEE (0.733), Cardinal RAT (0.428), PowerSploit (0.377), RCSession (0.356), Active Setup (0.348), Reg (0.046), Boot or Logon Autostart Execution (0.025), Persistence (0.006), Windows Registry Key Modification (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → PLAINTEE (10 neighbors, 10 edges)
           → Cardinal RAT (22 neighbors, 22 edges)
           → Active Setup (6 neighbors, 6 edges)
           → PowerSploit (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 3/6: สร้างงานตั้งเวลาในระบบเป็นกลไกสำรองสำหรับการทำงานอัตโนมัติ (Scheduled Task Persi...
[RETRIEVE] Query: สร้างงานตั้งเวลาในระบบเป็นกลไกสำรองสำหรับการทำงานอัตโนมัติ (Scheduled Task Persi...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AsyncRAT (0.794), Kimsuky (0.421), SVCReady (0.366), PowerSploit (0.312), At (0.035), at (0.030), Scheduled Task/Job (0.028), schtasks (0.017), Persistence (0.007), Scheduled Task (0.007)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AsyncRAT (23 neighbors, 23 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Kimsuky (150 neighbors, 150 edges)
           → SVCReady (24 neighbors, 24 edges)
           → PowerSploit (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 4/6: สกัดข้อมูลบัตรจากเครื่องรับชำระเงิน (POS Data Exfiltration)...
[RETRIEVE] Query: สกัดข้อมูลบัตรจากเครื่องรับชำระเงิน (POS Data Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PUNCHTRACK (0.680), FrameworkPOS (0.600), FrameworkPOS (0.429), RawPOS (0.155), Salesforce Data Exfiltration (0.023), Salesforce Data Exfiltration (0.019), Exfiltration (0.011), Data from Removable Media (0.007), Data from Local System (0.005), Data from Network Shared Drive (0.004)
[RETRIEVE] Graph expansion: 6 subgraphs
           → FrameworkPOS (6 neighbors, 6 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → PUNCHTRACK (4 neighbors, 4 edges)
           → RawPOS (6 neighbors, 6 edges)
           → Salesforce Data Exfiltration (19 neighbors, 19 edges)
           → Automated Exfiltration (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 5/6: ซุกข้อมูลบัตรในคำขอสอบถามชื่อโดเมน (DNS Tunneling for Data Exfiltration)...
[RETRIEVE] Query: ซุกข้อมูลบัตรในคำขอสอบถามชื่อโดเมน (DNS Tunneling for Data Exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FrameworkPOS (0.388), NightClub (0.227), Exfiltration Over Alternative Protocol (0.009), Salesforce Data Exfiltration (0.006), Domain Fronting (0.003), DNS (0.002), BRICKSTORM (0.002), Salesforce Data Exfiltration (0.002), Protocol Tunneling (0.002), Data from Local System (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FrameworkPOS (6 neighbors, 6 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → NightClub (22 neighbors, 22 edges)
           → DNS (60 neighbors, 60 edges)
           → Salesforce Data Exfiltration (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 6/6: ส่งข้อมูลบัตรออกไปภายนอกทีละน้อย (Slow Exfiltration via DNS Queries)...
[RETRIEVE] Query: ส่งข้อมูลบัตรออกไปภายนอกทีละน้อย (Slow Exfiltration via DNS Queries)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FrameworkPOS (0.064), Exfiltration Over Alternative Protocol (0.043), C0017 (0.030), Exfiltration Over Unencrypted Non-C2 Protocol (0.023), Exfiltration Over Physical Medium (0.018), OilRig (0.013), Filter Network Traffic (0.012), Exfiltration (0.008), DNS (0.001), Fast Flux DNS (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FrameworkPOS (6 neighbors, 6 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → C0017 (36 neighbors, 36 edges)
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
           → Exfiltration Over Physical Medium (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [71/100] retrieved=505 relevant=3 latency=12419ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 4 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Query: เมื่อวันที่ 4 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.272), Suckfly (0.088), pwdump (0.087), Windows Credential Editor (0.069), OS Credential Dumping (0.053), BlackByte (0.036), Credential Access Protection (0.012), Credential Access Protection (0.004), Credentials In Files (0.001), Credential Access (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Suckfly (6 neighbors, 6 edges)
           → pwdump (7 neighbors, 7 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 2/5: ลบไฟล์อย่างถาวรโดยเขียนทับเนื้อที่บนดิสก์เพื่อป้องกันการกู้คืน...
[RETRIEVE] Query: ลบไฟล์อย่างถาวรโดยเขียนทับเนื้อที่บนดิสก์เพื่อป้องกันการกู้คืน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SDelete (0.143), KillDisk (0.053), LiteDuke (0.013), Disk Wipe (0.013), MegaCortex (0.008), Visual Basic (0.000), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SDelete (7 neighbors, 7 edges)
           → KillDisk (18 neighbors, 18 edges)
           → Disk Wipe (5 neighbors, 5 edges)
           → LiteDuke (14 neighbors, 14 edges)
           → File Deletion (310 neighbors, 310 edges)
[RETRIEVE-QUOTA] Query 3/5: Credential Dumping เก็บรวบรวมรหัสผ่านบัญชีผู้ใช้บนเครื่อง...
[RETRIEVE] Query: Credential Dumping เก็บรวบรวมรหัสผ่านบัญชีผู้ใช้บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OS Credential Dumping (0.715), MgBot (0.601), APT32 (0.438), Credential Access (0.437), Poseidon Group (0.424), Windows Credential Editor (0.409), Axiom (0.403), Credentials In Files (0.395), pwdump (0.197), Credential Access Protection (0.118)
[RETRIEVE] Graph expansion: 6 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → MgBot (18 neighbors, 18 edges)
           → Credential Access (67 neighbors, 67 edges)
           → Credentials In Files (44 neighbors, 44 edges)
           → APT32 (93 neighbors, 93 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/5: DLL Hijacking ใช้โปรแกรมช่วยเรียกไลบรารีระบบวินโดวส์เพื่อเรียกไฟล์ของคนร้าย...
[RETRIEVE] Query: DLL Hijacking ใช้โปรแกรมช่วยเรียกไลบรารีระบบวินโดวส์เพื่อเรียกไฟล์ของคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: InvisiMole (0.702), DLL (0.525), Dynamic Linker Hijacking (0.272), FinFisher (0.251), Astaroth (0.189), Path Interception by Search Order Hijacking (0.114), Restrict File and Directory Permissions (0.078), VDSO Hijacking (0.060), Thread Execution Hijacking (0.050), Dylib Hijacking (0.030)
[RETRIEVE] Graph expansion: 5 subgraphs
           → InvisiMole (73 neighbors, 73 edges)
           → DLL (123 neighbors, 123 edges)
           → Dynamic Linker Hijacking (16 neighbors, 16 edges)
           → FinFisher (28 neighbors, 28 edges)
           → Astaroth (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 5/5: ฝังรายการในทะเบียนระบบเพื่อเรียกไฟล์ผ่าน DLL ที่มีลายเซ็นถูกต้อง...
[RETRIEVE] Query: ฝังรายการในทะเบียนระบบเพื่อเรียกไฟล์ผ่าน DLL ที่มีลายเซ็นถูกต้อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Regsvr32 (0.014), PUNCHBUGGY (0.005), AppCert DLLs (0.004), Mori (0.003), AppInit DLLs (0.002), Ramsay (0.002), Authentication Package (0.002), DLL (0.001), Dynamic-link Library Injection (0.000), Audit (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Regsvr32 (39 neighbors, 39 edges)
           → AppCert DLLs (7 neighbors, 7 edges)
           → PUNCHBUGGY (18 neighbors, 18 edges)
           → AppInit DLLs (11 neighbors, 11 edges)
           → Mori (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [72/100] retrieved=100 relevant=3 latency=10649ms
[RETRIEVE-QUOTA] Query 1/11: เมื่อวันที่ 26 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเต...
[RETRIEVE] Query: เมื่อวันที่ 26 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WINDSHIELD (0.012), BackConfig (0.001), Query Registry (0.001), FIN8 (0.000), Process Discovery (0.000), Password Guessing (0.000), System Language Discovery (0.000), Security Software Discovery (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → WINDSHIELD (6 neighbors, 6 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → BackConfig (17 neighbors, 17 edges)
           → Query Registry (121 neighbors, 121 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/11: เรียกดูรายการโปรแกรมที่กำลังทำงานอยู่บนเครื่องผ่านฟังก์ชันระบบ...
[RETRIEVE] Query: เรียกดูรายการโปรแกรมที่กำลังทำงานอยู่บนเครื่องผ่านฟังก์ชันระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.306), Tasklist (0.112), VERMIN (0.056), cmd (0.011), Forfiles (0.001), Visual Basic (0.001), CrossRAT (0.001), Cardinal RAT (0.000), Cobian RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → VERMIN (17 neighbors, 17 edges)
           → cmd (13 neighbors, 13 edges)
           → Forfiles (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 3/11: รันคำสั่งเพื่อแจกแจงรายการโปรแกรมที่ทำงานอยู่ผ่านหน้าต่างคำสั่ง...
[RETRIEVE] Query: รันคำสั่งเพื่อแจกแจงรายการโปรแกรมที่ทำงานอยู่ผ่านหน้าต่างคำสั่ง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.034), PLAINTEE (0.030), MoonWind (0.022), Forfiles (0.010), cmd (0.006), Cardinal RAT (0.004), Visual Basic (0.001), CrossRAT (0.000), Cobian RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PLAINTEE (10 neighbors, 10 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Tasklist (19 neighbors, 19 edges)
           → MoonWind (15 neighbors, 15 edges)
           → Forfiles (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 4/11: เรียกดูรายการบริการเบื้องหลังที่กำลังทำงานบนเครื่อง...
[RETRIEVE] Query: เรียกดูรายการบริการเบื้องหลังที่กำลังทำงานบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.077), Tasklist (0.043), BACKSPACE (0.034), VERMIN (0.013), LookBack (0.009), Wevtutil (0.003), BUBBLEWRAP (0.002), KernelCallbackTable (0.001), netstat (0.001), Process Discovery (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → System Service Discovery (71 neighbors, 71 edges)
           → BACKSPACE (15 neighbors, 15 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → VERMIN (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 5/11: เรียกดูการตั้งค่าของระบบปฏิบัติการที่ติดตั้งอยู่...
[RETRIEVE] Query: เรียกดูการตั้งค่าของระบบปฏิบัติการที่ติดตั้งอยู่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ifconfig (0.157), ipconfig (0.147), Milan (0.111), Operating System Configuration (0.095), ifconfig (0.091), Cobian RAT (0.001), Visual Basic (0.001), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → ifconfig (1 neighbors, 1 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → ipconfig (16 neighbors, 16 edges)
           → Milan (21 neighbors, 21 edges)
           → Operating System Configuration (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] Query 6/11: แจกแจงรายชื่อสมาชิกของกลุ่มผู้ดูแลระบบบนเครื่องท้องถิ่น...
[RETRIEVE] Query: แจกแจงรายชื่อสมาชิกของกลุ่มผู้ดูแลระบบบนเครื่องท้องถิ่น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sykipot (0.380), OSInfo (0.269), Tonto Team (0.208), Local Groups (0.109), Local Account (0.099), APT41 (0.021), Additional Local or Domain Groups (0.010), Nltest (0.009), Group Modification (0.002), Domain Account (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Sykipot (11 neighbors, 11 edges)
           → Domain Account (65 neighbors, 65 edges)
           → OSInfo (11 neighbors, 11 edges)
           → Local Groups (35 neighbors, 35 edges)
           → Tonto Team (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 7/11: แจกแจงรายชื่อสมาชิกของกลุ่มผู้ดูแลระบบบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: แจกแจงรายชื่อสมาชิกของกลุ่มผู้ดูแลระบบบนเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sykipot (0.537), Dragonfly (0.169), Nltest (0.164), Domain Groups (0.128), BADHATCH (0.116), APT41 (0.093), Group Metadata (0.093), Domain Account (0.022), Group Enumeration (0.013), Additional Local or Domain Groups (0.009)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Sykipot (11 neighbors, 11 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Dragonfly (66 neighbors, 66 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → Nltest (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 8/11: แจกแจงรายชื่อสมาชิกของกลุ่มผู้ดูแลระบบในระดับโดเมนขององค์กร...
[RETRIEVE] Query: แจกแจงรายชื่อสมาชิกของกลุ่มผู้ดูแลระบบในระดับโดเมนขององค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Domain Groups (0.107), OSInfo (0.067), Nltest (0.051), BADHATCH (0.021), Group Enumeration (0.008), Domain Account (0.005), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Domain Groups (41 neighbors, 41 edges)
           → OSInfo (11 neighbors, 11 edges)
           → Nltest (11 neighbors, 11 edges)
           → BADHATCH (36 neighbors, 36 edges)
           → Group Enumeration (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 9/11: แจกแจงรายชื่อบัญชีผู้ใช้ในโดเมน...
[RETRIEVE] Query: แจกแจงรายชื่อบัญชีผู้ใช้ในโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.687), PoshC2 (0.650), SoreFang (0.609), Domain Account (0.318), DUSTTRAP (0.279), Domain Account (0.050), Domain Accounts (0.036), Account Discovery (0.006), Cloud Account (0.004), Domain Registration (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → PoshC2 (35 neighbors, 35 edges)
           → SoreFang (15 neighbors, 15 edges)
           → DUSTTRAP (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 10/11: เรียกดูรายละเอียดของบัญชีผู้ใช้ในโดเมนเป็นรายบัญชี...
[RETRIEVE] Query: เรียกดูรายละเอียดของบัญชีผู้ใช้ในโดเมนเป็นรายบัญชี...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.461), PoshC2 (0.352), Domain Account (0.220), Domain Account (0.043), Account Discovery (0.001), Cloud Account (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → PoshC2 (35 neighbors, 35 edges)
           → Domain Account (18 neighbors, 18 edges)
           → Account Discovery (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 11/11: อ่านค่าในทะเบียนระบบส่วนนโยบายความปลอดภัยของเครื่อง...
[RETRIEVE] Query: อ่านค่าในทะเบียนระบบส่วนนโยบายความปลอดภัยของเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Registry Key Access (0.158), Qilin (0.031), Credentials in Registry (0.028), njRAT (0.007), SILENTTRINITY (0.005), Operating System Configuration (0.003), Windows Registry Key Modification (0.003), Modify Registry (0.002), Active Directory Object Access (0.000), Windows Credential Manager (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Windows Registry Key Access (0 neighbors, 0 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
           → Qilin (54 neighbors, 54 edges)
           → Query Registry (121 neighbors, 121 edges)
           → njRAT (40 neighbors, 40 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 11 queries
  [73/100] retrieved=644 relevant=6 latency=19965ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 4 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ข...
[RETRIEVE] Query: เมื่อวันที่ 4 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ข...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ursnif (0.038), NetTraveler (0.014), TrickBot (0.012), APT-C-36 (0.006), Malicious File (0.005), APT-C-36 (0.004), BADNEWS (0.002), External Defacement (0.001), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Ursnif (36 neighbors, 36 edges)
           → TrickBot (57 neighbors, 57 edges)
           → Malicious File (202 neighbors, 202 edges)
           → NetTraveler (3 neighbors, 3 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/9: Drive-by download ผ่านเว็บไซต์ปลอมที่มีชื่อคล้ายกับเว็บไซต์ข่าวต่างประเทศ...
[RETRIEVE] Query: Drive-by download ผ่านเว็บไซต์ปลอมที่มีชื่อคล้ายกับเว็บไซต์ข่าวต่างประเทศ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mustard Tempest (0.097), APT32 (0.060), SocGholish (0.053), Drive-by Compromise (0.025), FIN7 (0.021), Drive-by Target (0.005), BBK (0.001), ABK (0.000), Dok (0.000), RIFLESPINE (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Mustard Tempest (14 neighbors, 14 edges)
           → Drive-by Compromise (51 neighbors, 51 edges)
           → APT32 (93 neighbors, 93 edges)
           → Drive-by Target (12 neighbors, 12 edges)
           → SocGholish (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 3/9: DNS hijacking หรือ HTTP redirect ไปยังเว็บไซต์อันตรายของคนร้าย...
[RETRIEVE] Query: DNS hijacking หรือ HTTP redirect ไปยังเว็บไซต์อันตรายของคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Browser Session Hijacking (0.101), Domains (0.088), VDSO Hijacking (0.027), HTTPBrowser (0.019), DHCP Spoofing (0.018), Execution Prevention (0.017), Thread Execution Hijacking (0.012), Bandwidth Hijacking (0.010), DarkGate (0.007), Prikormka (0.006)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Browser Session Hijacking (19 neighbors, 19 edges)
           → Domains (15 neighbors, 15 edges)
           → VDSO Hijacking (5 neighbors, 5 edges)
           → DHCP Spoofing (7 neighbors, 7 edges)
           → HTTPBrowser (13 neighbors, 13 edges)
           → DNS (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] Query 4/9: ดาวน์โหลดไฟล์ปรับปรุงโปรแกรมปลอมที่มีมัลแวร์แนบมา...
[RETRIEVE] Query: ดาวน์โหลดไฟล์ปรับปรุงโปรแกรมปลอมที่มีมัลแวร์แนบมา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BadPatch (0.168), Starloader (0.080), CLAIMLOADER (0.042), TRANSLATEXT (0.012), Software Extensions (0.002), Cobian RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BadPatch (12 neighbors, 12 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Starloader (3 neighbors, 3 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
           → CLAIMLOADER (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 5/9: การเปิดไฟล์มัลแวร์ผ่านช่องสั่งเรียกโปรแกรมของระบบ (command line execution)...
[RETRIEVE] Query: การเปิดไฟล์มัลแวร์ผ่านช่องสั่งเรียกโปรแกรมของระบบ (command line execution)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ROADSWEEP (0.170), Seth-Locker (0.144), Indirect Command Execution (0.050), Forfiles (0.045), Systemctl (0.020), Windows Command Shell (0.018), Akira (0.018), Launchctl (0.006), HARDRAIN (0.004), Execution (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → ROADSWEEP (16 neighbors, 16 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Seth-Locker (3 neighbors, 3 edges)
           → Indirect Command Execution (5 neighbors, 5 edges)
           → Forfiles (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 6/9: มัลแวร์ติดต่อกลับไปยังเครื่องสั่งการของคนร้ายผ่านเครื่องพักสัญญาณ (C2 communicat...
[RETRIEVE] Query: มัลแวร์ติดต่อกลับไปยังเครื่องสั่งการของคนร้ายผ่านเครื่องพักสัญญาณ (C2 communicat...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: One-Way Communication (0.273), Anchor (0.163), Exfiltration Over C2 Channel (0.154), MuddyViper (0.146), TrickBot (0.126), Bidirectional Communication (0.123), Non-Application Layer Protocol (0.059), UPPERCUT (0.045), RedCurl (0.034), Inter-Process Communication (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → One-Way Communication (14 neighbors, 14 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Anchor (21 neighbors, 21 edges)
           → Fallback Channels (58 neighbors, 58 edges)
           → Bidirectional Communication (61 neighbors, 61 edges)
[RETRIEVE-QUOTA] Query 7/9: เก็บรวบรวมข้อมูลรายละเอียดของเครื่องเป้าหมาย (system information discovery)...
[RETRIEVE] Query: เก็บรวบรวมข้อมูลรายละเอียดของเครื่องเป้าหมาย (system information discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Information Discovery (0.547), SVCReady (0.495), Systeminfo (0.420), SHUTTERSPEED (0.251), System Owner/User Discovery (0.165), System Service Discovery (0.100), Ke3chang (0.092), System Time Discovery (0.046), File and Directory Discovery (0.003), Backup Software Discovery (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → System Information Discovery (426 neighbors, 426 edges)
           → SVCReady (24 neighbors, 24 edges)
           → Systeminfo (14 neighbors, 14 edges)
           → SHUTTERSPEED (4 neighbors, 4 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
[RETRIEVE-QUOTA] Query 8/9: ค้นหารายชื่อเครื่องคอมพิวเตอร์อื่นในโดเมนขององค์กร (network enumeration)...
[RETRIEVE] Query: ค้นหารายชื่อเครื่องคอมพิวเตอร์อื่นในโดเมนขององค์กร (network enumeration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: dsquery (0.088), Industroyer (0.020), Nltest (0.019), Instance Enumeration (0.015), BRONZE BUTLER (0.003), spwebmember (0.002), Volt Typhoon (0.002), ROADTools (0.001), Pod Enumeration (0.001), Snapshot Enumeration (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → dsquery (9 neighbors, 9 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Industroyer (21 neighbors, 21 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
           → Instance Enumeration (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 9/9: ส่งข้อมูลรายละเอียดเครื่องและรายชื่อเครื่องคอมพิวเตอร์ออกไปยังคนร้าย (exfiltrati...
[RETRIEVE] Query: ส่งข้อมูลรายละเอียดเครื่องและรายชื่อเครื่องคอมพิวเตอร์ออกไปยังคนร้าย (exfiltrati...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration (0.250), Exfiltration Over Other Network Medium (0.162), Exfiltration over USB (0.103), Exfiltration Over Physical Medium (0.077), Data from Network Shared Drive (0.052), HAMMERTOSS (0.049), Salesforce Data Exfiltration (0.019), ThiefQuest (0.016), APT28 Nearest Neighbor Campaign (0.015), Empire (0.011)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration (19 neighbors, 19 edges)
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
           → Exfiltration over USB (13 neighbors, 13 edges)
           → Exfiltration Over Physical Medium (6 neighbors, 6 edges)
           → Data from Network Shared Drive (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [74/100] retrieved=318 relevant=3 latency=18247ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 1 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Query: เมื่อวันที่ 1 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploitation for Privilege Escalation (0.039), Modify Registry (0.005), UPPERCUT (0.004), FIN8 (0.003), BackConfig (0.001), Valid Accounts (0.000), Exfiltration to Text Storage Sites (0.000), Lazarus Group (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → UPPERCUT (18 neighbors, 18 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → FIN8 (47 neighbors, 47 edges)
[RETRIEVE-QUOTA] Query 2/5: ไฟล์ที่ปลอมแปลงชื่อและตำแหน่งให้เหมือนไฟล์ระบบที่ถูกต้อง (DLL Hijacking / DLL Si...
[RETRIEVE] Query: ไฟล์ที่ปลอมแปลงชื่อและตำแหน่งให้เหมือนไฟล์ระบบที่ถูกต้อง (DLL Hijacking / DLL Si...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DLL (0.668), Sidewinder (0.638), FoggyWeb (0.356), Restrict File and Directory Permissions (0.126), Dylib Hijacking (0.092), Thread Execution Hijacking (0.069), Dynamic Linker Hijacking (0.053), Path Interception by Search Order Hijacking (0.028), Component Object Model Hijacking (0.017), VDSO Hijacking (0.016)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DLL (123 neighbors, 123 edges)
           → Sidewinder (31 neighbors, 31 edges)
           → FoggyWeb (22 neighbors, 22 edges)
           → Restrict File and Directory Permissions (60 neighbors, 60 edges)
           → SIP and Trust Provider Hijacking (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 3/5: ขโมยสิทธิ์ประจำตัวจากกระบวนการที่ทำงานด้วยสิทธิ์สูง (Token Impersonation)...
[RETRIEVE] Query: ขโมยสิทธิ์ประจำตัวจากกระบวนการที่ทำงานด้วยสิทธิ์สูง (Token Impersonation)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SILENTTRINITY (0.684), Token Impersonation/Theft (0.622), Havoc (0.376), KONNI (0.370), HomeLand Justice (0.243), Create Process with Token (0.161), Make and Impersonate Token (0.041), Access Token Manipulation (0.035), Temporary Elevated Cloud Access (0.007), Protocol or Service Impersonation (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Token Impersonation/Theft (26 neighbors, 26 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Havoc (30 neighbors, 30 edges)
           → KONNI (40 neighbors, 40 edges)
           → Create Process with Token (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 4/5: รันโปรแกรมควบคุมระยะไกลด้วยสิทธิ์ที่ขโมยมา (Remote Access Tool execution with el...
[RETRIEVE] Query: รันโปรแกรมควบคุมระยะไกลด้วยสิทธิ์ที่ขโมยมา (Remote Access Tool execution with el...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Elevated Execution with Prompt (0.577), LockBit 3.0 (0.497), Exploitation for Privilege Escalation (0.219), RemoteCMD (0.197), Bypass User Account Control (0.111), RemoteCMD (0.098), Privilege Escalation (0.067), QuasarRAT (0.028), Portable Executable Injection (0.013), Dynamic-link Library Injection (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Elevated Execution with Prompt (5 neighbors, 5 edges)
           → LockBit 3.0 (34 neighbors, 34 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → RemoteCMD (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 5/5: แก้ไขทะเบียนระบบเพื่อปิดการใช้งาน User Account Control (UAC Bypass via Registry ...
[RETRIEVE] Query: แก้ไขทะเบียนระบบเพื่อปิดการใช้งาน User Account Control (UAC Bypass via Registry ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Shamoon (0.894), LockBit 2.0 (0.722), Bypass User Account Control (0.292), Patchwork (0.210), User Account Control (0.170), UACMe (0.108), Modify Registry (0.057), Windows Registry Key Modification (0.021), Restrict Registry Permissions (0.006), User Account Management (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Shamoon (24 neighbors, 24 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
           → Patchwork (50 neighbors, 50 edges)
           → User Account Control (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] 14 vectors (quota 3/query), 8 subgraphs from 5 queries
  [75/100] retrieved=564 relevant=3 latency=13528ms
[RETRIEVE-QUOTA] Query 1/11: เมื่อวันที่ 19 กรกฎาคม 2564 หน่วยงานแห่งหนึ่งแจ้งความว่าถูกลักลอบเข้าถึงข้อมูลภา...
[RETRIEVE] Query: เมื่อวันที่ 19 กรกฎาคม 2564 หน่วยงานแห่งหนึ่งแจ้งความว่าถูกลักลอบเข้าถึงข้อมูลภา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN13 (0.309), External Remote Services (0.063), Duqu (0.011), FLIPSIDE (0.008), FakeSpy (0.001), Protocol or Service Impersonation (0.001), RDP Hijacking (0.001), Exfiltration Over Alternative Protocol (0.000), Protocol Tunneling (0.000), Remote Desktop Protocol (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN13 (57 neighbors, 57 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → Duqu (21 neighbors, 21 edges)
           → Protocol Tunneling (46 neighbors, 46 edges)
           → FLIPSIDE (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 2/11: External Remote Services เช่น VPN ใช้เข้าถึงเครือข่ายองค์กร...
[RETRIEVE] Query: External Remote Services เช่น VPN ใช้เข้าถึงเครือข่ายองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Remote Services (0.988), Limit Access to Resource Over Network (0.773), Operation Wocao (0.615), C0032 (0.528), Volt Typhoon (0.500), Web Portal Capture (0.158), Trusted Relationship (0.030), Remote Services (0.025), Limit Access to Resource Over Network (0.005), Terminal Services DLL (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → External Remote Services (52 neighbors, 52 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Operation Wocao (79 neighbors, 79 edges)
           → C0032 (19 neighbors, 19 edges)
           → Volt Typhoon (100 neighbors, 100 edges)
[RETRIEVE-QUOTA] Query 3/11: เอกสารล่อลวง (Phishing) ที่ใช้ช่องโหว่โปรแกรมอ่านเอกสาร...
[RETRIEVE] Query: เอกสารล่อลวง (Phishing) ที่ใช้ช่องโหว่โปรแกรมอ่านเอกสาร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DocSwap (0.540), BLINDINGCAN (0.446), Dridex (0.221), VOID MANTICORE (0.024), Written Content (0.022), Phishing (0.022), Phishing for Information (0.013), User Execution (0.010), Gather Victim Identity Information (0.002), Domains (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → DocSwap (27 neighbors, 27 edges)
           → Phishing (20 neighbors, 20 edges)
           → BLINDINGCAN (23 neighbors, 23 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Dridex (17 neighbors, 17 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] Query 4/11: การสั่งรันชุดคำสั่งผ่านช่องโหว่โปรแกรมอ่านเอกสาน (Exploit)...
[RETRIEVE] Query: การสั่งรันชุดคำสั่งผ่านช่องโหว่โปรแกรมอ่านเอกสาน (Exploit)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Indirect Command Execution (0.010), PowerSploit (0.009), PowerSploit (0.008), PowerSploit (0.005), PowerSploit (0.003), PowerSploit (0.003), Exploit Protection (0.001), Proc Memory (0.001), XSL Script Processing (0.000), Explosive (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Indirect Command Execution (5 neighbors, 5 edges)
           → PowerSploit (39 neighbors, 39 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 5/11: วางโปรแกรมอันตรายลงบนเครื่องผู้ใช้...
[RETRIEVE] Query: วางโปรแกรมอันตรายลงบนเครื่องผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Limit Software Installation (0.326), PROMETHIUM (0.263), BOULDSPY (0.213), BBSRAT (0.018), 4H RAT (0.016), Cobian RAT (0.005), CrossRAT (0.002), Visual Basic (0.001), Cardinal RAT (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Limit Software Installation (17 neighbors, 17 edges)
           → PROMETHIUM (14 neighbors, 14 edges)
           → Malicious File (202 neighbors, 202 edges)
           → BOULDSPY (25 neighbors, 25 edges)
           → Compromise Application Executable (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 6/11: ซ่อนข้อมูลที่ขโมยได้ในไฟล์อื่นที่ดูเหมือนปกติ (Steganography)...
[RETRIEVE] Query: ซ่อนข้อมูลที่ขโมยได้ในไฟล์อื่นที่ดูเหมือนปกติ (Steganography)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.960), Steganography (0.860), Steganography (0.626), Embedded Payloads (0.487), Daserf (0.303), Operation Ghost (0.267), HTML Smuggling (0.093), Data Obfuscation (0.039), LunarWeb (0.009), LunarMail (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Steganography (32 neighbors, 32 edges)
           → Leviathan (68 neighbors, 68 edges)
           → Steganography (17 neighbors, 17 edges)
           → Embedded Payloads (27 neighbors, 27 edges)
           → Daserf (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] Query 7/11: อัปโหลดข้อมูลไปยังบริการเก็บซอร์สโค้ดสาธารณะ...
[RETRIEVE] Query: อัปโหลดข้อมูลไปยังบริการเก็บซอร์สโค้ดสาธารณะ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SombRAT (0.073), Code Repositories (0.064), Code Repositories (0.029), BONDUPDATER (0.003), Cloud Storage Access (0.000), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Code Repositories (14 neighbors, 14 edges)
           → SombRAT (25 neighbors, 25 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → Code Repositories (8 neighbors, 8 edges)
           → BONDUPDATER (8 neighbors, 8 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 8/11: ปลอมรูปแบบการติดต่อให้เหมือนการใช้งานปกติ (Protocol Impersonation)...
[RETRIEVE] Query: ปลอมรูปแบบการติดต่อให้เหมือนการใช้งานปกติ (Protocol Impersonation)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Protocol or Service Impersonation (0.884), FakeM (0.826), InvisiMole (0.700), C0027 (0.032), GUI Input Capture (0.032), Impersonation (0.019), Token Impersonation/Theft (0.017), Operation Dream Job (0.005), Access Token Manipulation (0.003), Temporary Elevated Cloud Access (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Protocol or Service Impersonation (26 neighbors, 26 edges)
           → FakeM (5 neighbors, 5 edges)
           → InvisiMole (73 neighbors, 73 edges)
           → GUI Input Capture (21 neighbors, 21 edges)
           → C0027 (30 neighbors, 30 edges)
           → Impersonation (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 9/11: ใช้กุญแจเรียกใช้บริการผู้ให้บริการรับฝากไฟล์ในการอัปโหลด...
[RETRIEVE] Query: ใช้กุญแจเรียกใช้บริการผู้ให้บริการรับฝากไฟล์ในการอัปโหลด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: KEYMARBLE (0.148), Pisloader (0.003), HOPLIGHT (0.003), Spica (0.002), Private Keys (0.001), Credential API Hooking (0.001), Upload Tool (0.000), Forced Authentication (0.000), Password Managers (0.000), Archive via Utility (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → KEYMARBLE (12 neighbors, 12 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Pisloader (10 neighbors, 10 edges)
           → HOPLIGHT (23 neighbors, 23 edges)
           → Spica (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 10/11: Protocol Tunneling ห่อหุ้มการติดต่อไว้ภายในโพรโทคอลอื่น...
[RETRIEVE] Query: Protocol Tunneling ห่อหุ้มการติดต่อไว้ภายในโพรโทคอลอื่น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Protocol Tunneling (0.996), Duqu (0.880), Mythic (0.746), FRP (0.548), FLIPSIDE (0.184), DNS (0.020), IDE Tunneling (0.015), Web Protocols (0.011), Mail Protocols (0.009), ARP Cache Poisoning (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Protocol Tunneling (46 neighbors, 46 edges)
           → Duqu (21 neighbors, 21 edges)
           → Mythic (13 neighbors, 13 edges)
           → FRP (16 neighbors, 16 edges)
           → FLIPSIDE (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 11/11: ส่งต่อการเชื่อมต่อผ่านเครื่องพักสัญญาณหลายทอด (Proxy)...
[RETRIEVE] Query: ส่งต่อการเชื่อมต่อผ่านเครื่องพักสัญญาณหลายทอด (Proxy)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SPACEHOP Activity (0.094), Multi-hop Proxy (0.089), Kobalos (0.061), Proxy (0.040), External Proxy (0.015), Internal Proxy (0.010), StarProxy (0.005), StarProxy (0.004), Proxysvc (0.001), StarProxy (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Multi-hop Proxy (45 neighbors, 45 edges)
           → SPACEHOP Activity (6 neighbors, 6 edges)
           → Kobalos (15 neighbors, 15 edges)
           → Proxy (84 neighbors, 84 edges)
           → External Proxy (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 11 queries
  [76/100] retrieved=194 relevant=6 latency=21566ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 25 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Query: เมื่อวันที่ 25 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.047), File Deletion (0.041), Bankshot (0.019), APT-C-36 (0.002), Ingress Tool Transfer (0.002), Ursnif (0.001), USBStealer (0.001), Internal Spearphishing (0.000), Right-to-Left Override (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมฝังตัวบนเครื่องแรกรับคำสั่งดาวน์โหลดเครื่องมือสั่งงานเครื่องระยะไกล...
[RETRIEVE] Query: โปรแกรมฝังตัวบนเครื่องแรกรับคำสั่งดาวน์โหลดเครื่องมือสั่งงานเครื่องระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SEASHARPEE (0.161), Volgmer (0.121), RemoteCMD (0.082), RemoteCMD (0.056), xCmd (0.034), CrackMapExec (0.011), Remote Access Tools (0.004), Command and Scripting Interpreter (0.000), Launch Daemon (0.000), Ptrace System Calls (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SEASHARPEE (5 neighbors, 5 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Volgmer (20 neighbors, 20 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → xCmd (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 3/8: ดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดที่สองเข้ามาเก็บไว้บนเครื่องแรก...
[RETRIEVE] Query: ดาวน์โหลดตัวติดตั้งโปรแกรมฝังตัวชุดที่สองเข้ามาเก็บไว้บนเครื่องแรก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Grandoreiro (0.015), DownPaper (0.002), PipeMon (0.001), BUBBLEWRAP (0.001), SoreFang (0.000), CrossRAT (0.000), Visual Basic (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Grandoreiro (43 neighbors, 43 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → PipeMon (24 neighbors, 24 edges)
           → DownPaper (8 neighbors, 8 edges)
           → BUBBLEWRAP (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 4/8: การลุกลามจากเครื่องแรกไปยังเครื่องแม่ข่ายเก็บไฟล์ผ่านเครื่องมือสั่งงานระยะไกล...
[RETRIEVE] Query: การลุกลามจากเครื่องแรกไปยังเครื่องแม่ข่ายเก็บไฟล์ผ่านเครื่องมือสั่งงานระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CHOPSTICK (0.022), Volgmer (0.020), RemoteUtilities (0.018), Multi-Stage Channels (0.012), cmd (0.011), Communication Through Removable Media (0.010), Ingress Tool Transfer (0.009), File Transfer Protocols (0.007), Lateral Tool Transfer (0.005), Replication Through Removable Media (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CHOPSTICK (20 neighbors, 20 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Volgmer (20 neighbors, 20 edges)
           → RemoteUtilities (5 neighbors, 5 edges)
           → Multi-Stage Channels (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 5/8: รันเครื่องมือสั่งงานระยะไกลในนามของบัญชีผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์...
[RETRIEVE] Query: รันเครื่องมือสั่งงานระยะไกลในนามของบัญชีผู้ดูแลเครื่องแม่ข่ายเก็บไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cloud Administration Command (0.024), RemoteCMD (0.023), ESXi Administration Command (0.019), HyperStack (0.008), Windows Remote Management (0.007), MCMD (0.007), Leafminer (0.004), PsExec (0.003), RemoteCMD (0.003), Remote Services (0.002)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Cloud Administration Command (7 neighbors, 7 edges)
           → ESXi Administration Command (5 neighbors, 5 edges)
           → RemoteCMD (4 neighbors, 4 edges)
           → Windows Remote Management (16 neighbors, 16 edges)
           → HyperStack (7 neighbors, 7 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] Query 6/8: สร้างบริการของระบบบนเครื่องแม่ข่ายเก็บไฟล์เพื่อเรียกทำงานตัวติดตั้งโปรแกรมฝังตัว...
[RETRIEVE] Query: สร้างบริการของระบบบนเครื่องแม่ข่ายเก็บไฟล์เพื่อเรียกทำงานตัวติดตั้งโปรแกรมฝังตัว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Systemd Service (0.012), Windows Service (0.008), Create or Modify System Process (0.007), Native API (0.003), STARWHALE (0.002), Conficker (0.002), HermeticWiper (0.001), Industroyer (0.001), Thread Local Storage (0.000), Portable Executable Injection (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Systemd Service (22 neighbors, 22 edges)
           → Windows Service (150 neighbors, 150 edges)
           → Create or Modify System Process (25 neighbors, 25 edges)
           → Native API (232 neighbors, 232 edges)
           → STARWHALE (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 7/8: โปรแกรมฝังตัวบนเครื่องใหม่ติดต่อกลับมาเพื่อรับคำสั่งจากคนร้าย...
[RETRIEVE] Query: โปรแกรมฝังตัวบนเครื่องใหม่ติดต่อกลับมาเพื่อรับคำสั่งจากคนร้าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: USBStealer (0.021), Cobian RAT (0.003), Credential API Hooking (0.002), KernelCallbackTable (0.002), CrossRAT (0.001), 4H RAT (0.001), Nightdoor (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → USBStealer (15 neighbors, 15 edges)
           → Communication Through Removable Media (7 neighbors, 7 edges)
           → Credential API Hooking (17 neighbors, 17 edges)
           → Cobian RAT (8 neighbors, 8 edges)
           → KernelCallbackTable (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 8/8: ลบไฟล์ที่นำเข้าไปวางไว้บนเครื่องแรกเพื่อเก็บกวาดร่องรอย...
[RETRIEVE] Query: ลบไฟล์ที่นำเข้าไปวางไว้บนเครื่องแรกเพื่อเก็บกวาดร่องรอย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: File Deletion (0.010), Donut (0.007), Clear Persistence (0.003), Bankshot (0.003), BackConfig (0.001), Clear Linux or Mac System Logs (0.001), SUNSPOT (0.001), Image Deletion (0.000), Clear Network Connection History and Configurations (0.000), Overwrite Process Arguments (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → Donut (17 neighbors, 17 edges)
           → Indicator Removal (45 neighbors, 45 edges)
           → Clear Persistence (19 neighbors, 19 edges)
           → Bankshot (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [77/100] retrieved=707 relevant=3 latency=16314ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 29 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความเพิ่มเติมถึงเส้นทางที...
[RETRIEVE] Query: เมื่อวันที่ 29 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความเพิ่มเติมถึงเส้นทางที...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sandworm Team (0.831), Sea Turtle (0.700), Trusted Relationship (0.229), TeamTNT (0.004), Business Relationships (0.001), Ingress Tool Transfer (0.001), Network Trust Dependencies (0.000), Network Security Appliances (0.000), Domain Trust Discovery (0.000), Customer Relationship Management Software (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Sandworm Team (113 neighbors, 113 edges)
           → Trusted Relationship (18 neighbors, 18 edges)
           → Sea Turtle (28 neighbors, 28 edges)
           → TeamTNT (60 neighbors, 60 edges)
           → SSH (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 2/6: ประยุกต์ใช้ Trusted Relationship ผ่านอุปกรณ์เราเตอร์สาขาเพื่อเข้าถึงเครือข่ายองค...
[RETRIEVE] Query: ประยุกต์ใช้ Trusted Relationship ผ่านอุปกรณ์เราเตอร์สาขาเพื่อเข้าถึงเครือข่ายองค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sandworm Team (0.530), Trusted Relationship (0.477), Sea Turtle (0.139), APT29 (0.048), Trust Modification (0.017), Network Trust Dependencies (0.012), Business Relationships (0.010), Domain Trust Discovery (0.006), Acquire Access (0.000), Trusted Developer Utilities Proxy Execution (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Trusted Relationship (18 neighbors, 18 edges)
           → Sandworm Team (113 neighbors, 113 edges)
           → Sea Turtle (28 neighbors, 28 edges)
           → APT29 (117 neighbors, 117 edges)
           → Trust Modification (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 3/6: สแกนสำรวจเครือข่ายภายในองค์กรด้วยเครื่องมือสแกน...
[RETRIEVE] Query: สแกนสำรวจเครือข่ายภายในองค์กรด้วยเครื่องมือสแกน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NBTscan (0.763), Vulnerability Scanning (0.490), Ke3chang (0.062), Active Scanning (0.030), Scan Databases (0.004), CrossRAT (0.001), Cobian RAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → NBTscan (15 neighbors, 15 edges)
           → Vulnerability Scanning (5 neighbors, 5 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
           → Ke3chang (58 neighbors, 58 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
[RETRIEVE-QUOTA] Query 4/6: ติดตั้งเซิร์ฟเวอร์ไฟล์ภายในเครือข่ายเพื่อลำเลียงข้อมูลระหว่างเครื่องต่าง ๆ...
[RETRIEVE] Query: ติดตั้งเซิร์ฟเวอร์ไฟล์ภายในเครือข่ายเพื่อลำเลียงข้อมูลระหว่างเครื่องต่าง ๆ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ftp (0.006), Internal Proxy (0.006), File Transfer Protocols (0.005), Expand (0.005), PsExec (0.005), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Internal Proxy (39 neighbors, 39 edges)
           → File Transfer Protocols (32 neighbors, 32 edges)
           → ftp (10 neighbors, 10 edges)
           → Expand (3 neighbors, 3 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 5/6: ยึดครองอุปกรณ์เราเตอร์สาขาและเปิดสู่อินเทอร์เน็ตเป็นส่วนของโครงสร้างพื้นฐานของผู...
[RETRIEVE] Query: ยึดครองอุปกรณ์เราเตอร์สาขาและเปิดสู่อินเทอร์เน็ตเป็นส่วนของโครงสร้างพื้นฐานของผู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Network Devices (0.027), APT28 (0.011), Wi-Fi Networks (0.003), Quad7 Activity (0.003), Communication Through Removable Media (0.002), Initial Access (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Network Devices (13 neighbors, 13 edges)
           → APT28 (124 neighbors, 124 edges)
           → Wi-Fi Networks (7 neighbors, 7 edges)
           → Quad7 Activity (16 neighbors, 16 edges)
           → Communication Through Removable Media (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 6/6: ใช้เราเตอร์สาขาที่ยึดครองเป็นทางผ่านไปยังผู้เสียหายรายอื่นในเครือข่ายเดียวกัน...
[RETRIEVE] Query: ใช้เราเตอร์สาขาที่ยึดครองเป็นทางผ่านไปยังผู้เสียหายรายอื่นในเครือข่ายเดียวกัน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kwampirs (0.004), Communication Through Removable Media (0.003), Adversary-in-the-Middle (0.002), Acquire Access (0.001), Lucifer (0.001), Lateral Tool Transfer (0.001), Transfer Data to Cloud Account (0.000), APT41 (0.000), WastedLocker (0.000), Token Impersonation/Theft (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Kwampirs (23 neighbors, 23 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → Communication Through Removable Media (7 neighbors, 7 edges)
           → Adversary-in-the-Middle (23 neighbors, 23 edges)
           → Acquire Access (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [78/100] retrieved=259 relevant=3 latency=12328ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 30 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความเพิ่มเติมถึ...
[RETRIEVE] Query: เมื่อวันที่ 30 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความเพิ่มเติมถึ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.006), APT-C-36 (0.001), Attestation (0.000), Network Intrusion Prevention (0.000), Ursnif (0.000), Compromise Host Software Binary (0.000), Internal Spearphishing (0.000), Subvert Trust Controls (0.000), Social Engineering (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → AsyncRAT (23 neighbors, 23 edges)
           → Attestation (13 neighbors, 13 edges)
           → Indicator Removal on Host (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 2/7: ติดตั้งซอฟต์แวร์รุ่นเก่าที่มีลายเซ็นถูกต้องเพื่อหลบเลี่ยงการตรวจสอบความถูกต้อง...
[RETRIEVE] Query: ติดตั้งซอฟต์แวร์รุ่นเก่าที่มีลายเซ็นถูกต้องเพื่อหลบเลี่ยงการตรวจสอบความถูกต้อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QakBot (0.026), Code Signing (0.012), Invalid Code Signature (0.010), Code Signing Policy Modification (0.004), Code Signing (0.002), Disable or Remove Feature or Program (0.001), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → QakBot (74 neighbors, 74 edges)
           → Code Signing (90 neighbors, 90 edges)
           → Code Signing (22 neighbors, 22 edges)
           → Invalid Code Signature (12 neighbors, 12 edges)
           → Code Signing Policy Modification (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 3/7: แก้ไขซอฟต์แวร์ในหน่วยความจำเพื่อเปิดทางติดตั้งซอฟต์แวร์ที่ไม่มีลายเซ็น...
[RETRIEVE] Query: แก้ไขซอฟต์แวร์ในหน่วยความจำเพื่อเปิดทางติดตั้งซอฟต์แวร์ที่ไม่มีลายเซ็น...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operating System Configuration (0.018), Code Signing Policy Modification (0.014), TYPEFRAME (0.003), Modify Authentication Process (0.001), Cobian RAT (0.000), Visual Basic (0.000), 4H RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Operating System Configuration (39 neighbors, 39 edges)
           → Create or Modify System Process (25 neighbors, 25 edges)
           → Code Signing Policy Modification (10 neighbors, 10 edges)
           → TYPEFRAME (16 neighbors, 16 edges)
           → Modify Registry (177 neighbors, 177 edges)
[RETRIEVE-QUOTA] Query 4/7: ติดตั้งตัวโหลดระบบที่ดัดแปลงเพื่อให้ซอฟต์แวร์ดัดแปลงผ่านการตรวจสอบ...
[RETRIEVE] Query: ติดตั้งตัวโหลดระบบที่ดัดแปลงเพื่อให้ซอฟต์แวร์ดัดแปลงผ่านการตรวจสอบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Execution Prevention (0.010), TRANSLATEXT (0.001), Installer Packages (0.001), Restrict Library Loading (0.000), CrossRAT (0.000), UACMe (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Execution Prevention (79 neighbors, 79 edges)
           → Modify or Spoof Tool UI (4 neighbors, 4 edges)
           → Installer Packages (8 neighbors, 8 edges)
           → TRANSLATEXT (16 neighbors, 16 edges)
           → Modify Registry (177 neighbors, 177 edges)
[RETRIEVE-QUOTA] Query 5/7: ติดตั้งซอฟต์แวร์ที่ดัดแปลงเองลงในอุปกรณ์เครือข่าย...
[RETRIEVE] Query: ติดตั้งซอฟต์แวร์ที่ดัดแปลงเองลงในอุปกรณ์เครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kerrdown (0.324), Network Device Authentication (0.038), PHASEJAM (0.031), Impacket (0.020), Kazuar (0.002), Cobian RAT (0.001), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Kerrdown (12 neighbors, 12 edges)
           → Network Device Authentication (11 neighbors, 11 edges)
           → PHASEJAM (15 neighbors, 15 edges)
           → Network Device CLI (11 neighbors, 11 edges)
           → Impacket (35 neighbors, 35 edges)
[RETRIEVE-QUOTA] Query 6/7: ตั้งกฎอัตโนมัติตัดบรรทัดข้อความออกจากผลลัพธ์คำสั่งตรวจสอบของผู้ดูแลระบบ...
[RETRIEVE] Query: ตั้งกฎอัตโนมัติตัดบรรทัดข้อความออกจากผลลัพธ์คำสั่งตรวจสอบของผู้ดูแลระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Audit (0.007), Ruler (0.002), Audit (0.001), Disable or Modify Linux Audit System Log (0.001), Scattered Spider (0.001), User Account Control (0.000), Execution Prevention (0.000), Firewall Rule Modification (0.000), Clear Mailbox Data (0.000), Firewall Disable (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Audit (110 neighbors, 110 edges)
           → Email Forwarding Rule (12 neighbors, 12 edges)
           → Ruler (5 neighbors, 5 edges)
           → Outlook Rules (6 neighbors, 6 edges)
           → Disable or Modify Linux Audit System Log (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 7/7: ตั้งกฎอัตโนมัติขัดขวางคำสั่งคัดลอก เปลี่ยนชื่อ และย้ายไฟล์ทำงาน...
[RETRIEVE] Query: ตั้งกฎอัตโนมัติขัดขวางคำสั่งคัดลอก เปลี่ยนชื่อ และย้ายไฟล์ทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Restrict File and Directory Permissions (0.130), Restrict Web-Based Content (0.073), Environment Variable Permissions (0.011), File and Directory Permissions Modification (0.005), Group Policy Modification (0.001), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Restrict File and Directory Permissions (60 neighbors, 60 edges)
           → Runtime Data Manipulation (6 neighbors, 6 edges)
           → Restrict Web-Based Content (31 neighbors, 31 edges)
           → Malicious Copy and Paste (10 neighbors, 10 edges)
           → Environment Variable Permissions (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [79/100] retrieved=219 relevant=2 latency=14167ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 6 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Query: เมื่อวันที่ 6 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA505 (0.023), KeyBoy (0.016), NotPetya (0.015), LaZagne (0.004), Credentials from Web Browsers (0.004), Unsecured Credentials (0.001), Web Credential Usage (0.000), Credentials in Registry (0.000), Query Registry (0.000), Windows Credential Manager (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → TA505 (50 neighbors, 50 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → KeyBoy (19 neighbors, 19 edges)
           → NotPetya (15 neighbors, 15 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมไม่พึงประสงค์ติดตั้งและแพร่กระจายไปยังเครื่องอื่นในเครือข่าย...
[RETRIEVE] Query: โปรแกรมไม่พึงประสงค์ติดตั้งและแพร่กระจายไปยังเครื่องอื่นในเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NotPetya (0.581), Ramsay (0.502), Duqu (0.260), HALFBAKED (0.236), Taint Shared Content (0.206), NKAbuse (0.113), CrossRAT (0.004), Cardinal RAT (0.001), Visual Basic (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → NotPetya (15 neighbors, 15 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Ramsay (39 neighbors, 39 edges)
           → Taint Shared Content (18 neighbors, 18 edges)
           → Duqu (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 3/8: เพิ่มรายการเรียกใช้งานโปรแกรมในRegistry Run Key เพื่อให้ทำงานอัตโนมัติ...
[RETRIEVE] Query: เพิ่มรายการเรียกใช้งานโปรแกรมในRegistry Run Key เพื่อให้ทำงานอัตโนมัติ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ursnif (0.537), KOCTOPUS (0.476), Registry Run Keys / Startup Folder (0.322), LockBit 2.0 (0.051), Lucifer (0.036), Boot or Logon Autostart Execution (0.021), Active Setup (0.016), Services Registry Permissions Weakness (0.002), Modify Registry (0.002), Skeleton Key (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Ursnif (36 neighbors, 36 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → KOCTOPUS (21 neighbors, 21 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
           → Lucifer (24 neighbors, 24 edges)
[RETRIEVE-QUOTA] Query 4/8: เพิ่มโปรแกรมในโฟลเดอร์เริ่มต้นระบบเพื่อให้ทำงานทุกครั้งเปิดเครื่อง...
[RETRIEVE] Query: เพิ่มโปรแกรมในโฟลเดอร์เริ่มต้นระบบเพื่อให้ทำงานทุกครั้งเปิดเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DarkComet (0.884), Registry Run Keys / Startup Folder (0.738), CozyCar (0.643), RogueRobin (0.391), XDG Autostart Entries (0.049), Boot or Logon Autostart Execution (0.040), Startup Items (0.017), Create or Modify System Process (0.017), Re-opened Applications (0.016), Launch Daemon (0.010)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → DarkComet (21 neighbors, 21 edges)
           → CozyCar (15 neighbors, 15 edges)
           → RogueRobin (19 neighbors, 19 edges)
           → XDG Autostart Entries (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 5/8: อ่าน Credentials from Web Browsers ชื่อผู้ใช้และรหัสผ่านที่บันทึกไว้...
[RETRIEVE] Query: อ่าน Credentials from Web Browsers ชื่อผู้ใช้และรหัสผ่านที่บันทึกไว้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.976), Lizar (0.782), PLEAD (0.514), LaZagne (0.202), SUGARDUMP (0.146), Credentials from Password Stores (0.021), Browser Information Discovery (0.012), Forge Web Credentials (0.011), Windows Credential Manager (0.010), Web Credential Usage (0.006)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → Lizar (29 neighbors, 29 edges)
           → PLEAD (16 neighbors, 16 edges)
           → LaZagne (22 neighbors, 22 edges)
           → SUGARDUMP (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 6/8: ใช้ชุดเครื่องมือโจมตีช่องโหว่บริการแบ่งปันไฟล์ Windows เพื่อขยายการเข้าถึง...
[RETRIEVE] Query: ใช้ชุดเครื่องมือโจมตีช่องโหว่บริการแบ่งปันไฟล์ Windows เพื่อขยายการเข้าถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Neoichor (0.049), MCMD (0.040), Lateral Tool Transfer (0.018), Ingress Tool Transfer (0.006), Samurai (0.003), Taint Shared Content (0.002), cmd (0.002), Windows Command Shell (0.002), Cobalt Group (0.001), Scheduled Task (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Neoichor (12 neighbors, 12 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → MCMD (11 neighbors, 11 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Samurai (20 neighbors, 20 edges)
           → Native API (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 7/8: เชื่อมต่อไปยังเครื่องต้องสงสัยผ่านพอร์ตแบ่งปันไฟล์ Windows...
[RETRIEVE] Query: เชื่อมต่อไปยังเครื่องต้องสงสัยผ่านพอร์ตแบ่งปันไฟล์ Windows...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SMB/Windows Admin Shares (0.028), Network Share Discovery (0.026), CreepyDrive (0.008), PcShare (0.002), Taint Shared Content (0.001), Windows Command Shell (0.000), cmd (0.000), Visual Basic (0.000), Samurai (0.000), Cobalt Group (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
           → CreepyDrive (9 neighbors, 9 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → PcShare (23 neighbors, 23 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
[RETRIEVE-QUOTA] Query 8/8: ติดต่อกลับไปยังเครื่องสั่งการผ่านโพรโทคอล HTTP/HTTPS ด้วยเส้นทางโฟลเดอร์สุ่ม...
[RETRIEVE] Query: ติดต่อกลับไปยังเครื่องสั่งการผ่านโพรโทคอล HTTP/HTTPS ด้วยเส้นทางโฟลเดอร์สุ่ม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Alternative Protocol (0.016), RATANKBA (0.007), PoshC2 (0.007), ELMER (0.004), Web Protocols (0.002), HTTPTroy (0.002), HTTPTroy (0.002), ELMER (0.001), Thread Local Storage (0.000), HTTPBrowser (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → RATANKBA (16 neighbors, 16 edges)
           → Web Protocols (424 neighbors, 424 edges)
           → PoshC2 (35 neighbors, 35 edges)
           → ELMER (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [80/100] retrieved=332 relevant=4 latency=16895ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 2 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายหลบ...
[RETRIEVE] Query: เมื่อวันที่ 2 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายหลบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operation Wocao (0.476), APT3 (0.285), Indicator Removal (0.021), Indicator Removal from Tools (0.020), Bypass User Account Control (0.001), Disable or Modify Tools (0.000), User Account Control (0.000), Clear Windows Event Logs (0.000), User Account Control (0.000), Multi-factor Authentication (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Operation Wocao (79 neighbors, 79 edges)
           → Indicator Removal from Tools (20 neighbors, 20 edges)
           → APT3 (50 neighbors, 50 edges)
           → Indicator Removal (45 neighbors, 45 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
[RETRIEVE-QUOTA] Query 2/5: หลบเลี่ยงกลไกการยืนยันก่อนยกระดับสิทธิ์ (UAC bypass)...
[RETRIEVE] Query: หลบเลี่ยงกลไกการยืนยันก่อนยกระดับสิทธิ์ (UAC bypass)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bypass User Account Control (0.921), User Account Control (0.719), User Account Control (0.606), Abuse Elevation Control Mechanism (0.451), UPPERCUT (0.311), Sliver (0.267), Patchwork (0.092), UACMe (0.059), Pass the Hash (0.031), Multi-Factor Authentication (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bypass User Account Control (70 neighbors, 70 edges)
           → User Account Control (7 neighbors, 7 edges)
           → Abuse Elevation Control Mechanism (18 neighbors, 18 edges)
           → UPPERCUT (18 neighbors, 18 edges)
           → Sliver (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] Query 3/5: ยกระดับสิทธิ์เป็นผู้ดูแลระบบโดยไม่มีหน้าต่างขออนุญาต...
[RETRIEVE] Query: ยกระดับสิทธิ์เป็นผู้ดูแลระบบโดยไม่มีหน้าต่างขออนุญาต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Raspberry Robin (0.264), Elevated Execution with Prompt (0.164), Privilege Escalation (0.137), Bypass User Account Control (0.059), User Account Control (0.022), InvisiMole (0.015), Cardinal RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Raspberry Robin (41 neighbors, 41 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
           → Elevated Execution with Prompt (5 neighbors, 5 edges)
           → Privilege Escalation (96 neighbors, 96 edges)
           → User Account Control (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 4/5: ปรับแต่งเครื่องมือโดยตัดข้อความและค่าเฉพาะที่ใช้ตรวจจับ (Indicator Removal from ...
[RETRIEVE] Query: ปรับแต่งเครื่องมือโดยตัดข้อความและค่าเฉพาะที่ใช้ตรวจจับ (Indicator Removal from ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Indicator Removal from Tools (0.723), QakBot (0.677), Operation Wocao (0.509), Penquin (0.436), Indicator Removal (0.409), APT3 (0.403), Disable or Modify Tools (0.016), Tool (0.001), Multi-factor Authentication (0.000), Ccache Files (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Indicator Removal from Tools (20 neighbors, 20 edges)
           → QakBot (74 neighbors, 74 edges)
           → Operation Wocao (79 neighbors, 79 edges)
           → Indicator Removal (45 neighbors, 45 edges)
           → Penquin (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 5/5: ล้างไฟล์บันทึกเหตุการณ์ Windows (Indicator Removal on Host)...
[RETRIEVE] Query: ล้างไฟล์บันทึกเหตุการณ์ Windows (Indicator Removal on Host)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Attestation (0.251), Chameleon (0.241), Neoichor (0.191), Clear Windows Event Logs (0.177), Indicator Removal (0.133), Windows Registry Key Deletion (0.008), Inhibit System Recovery (0.001), Koadic (0.001), Attor (0.000), Account Access Removal (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Attestation (13 neighbors, 13 edges)
           → Indicator Removal on Host (10 neighbors, 10 edges)
           → Chameleon (26 neighbors, 26 edges)
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Neoichor (12 neighbors, 12 edges)
           → Indicator Removal (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] 14 vectors (quota 3/query), 8 subgraphs from 5 queries
  [81/100] retrieved=220 relevant=3 latency=10642ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 19 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร...
[RETRIEVE] Query: เมื่อวันที่ 19 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gamaredon Group (0.064), POWRUNER (0.062), APT-C-36 (0.016), Ursnif (0.002), APT-C-36 (0.002), Ingress Tool Transfer (0.001), Exfiltration (0.000), Internal Spearphishing (0.000), Archive via Utility (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Gamaredon Group (76 neighbors, 76 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] Query 2/5: Group Policy Object (GPO) ใช้ส่งโปรแกรมมัลแวร์ไปติดตั้งบนเครื่องลูกข่ายทั้งองค์ก...
[RETRIEVE] Query: Group Policy Object (GPO) ใช้ส่งโปรแกรมมัลแวร์ไปติดตั้งบนเครื่องลูกข่ายทั้งองค์ก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT41 (0.537), 2022 Ukraine Electric Power Attack (0.151), Group Policy Discovery (0.061), Empire (0.054), Group Policy Modification (0.046), 2022 Ukraine Electric Power Attack (0.026), Group Policy Preferences (0.002), Active Directory Object Access (0.000), Impacket (0.000), Domain or Tenant Policy Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT41 (116 neighbors, 116 edges)
           → Group Policy Modification (22 neighbors, 22 edges)
           → 2022 Ukraine Electric Power Attack (12 neighbors, 12 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Group Policy Discovery (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 3/5: แบ่งข้อมูลที่รวบรวมได้ออกเป็นส่วนย่อยหลายส่วนเพื่อเตรียมการส่งออก...
[RETRIEVE] Query: แบ่งข้อมูลที่รวบรวมได้ออกเป็นส่วนย่อยหลายส่วนเพื่อเตรียมการส่งออก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cobalt Strike (0.070), Data Staged (0.026), Kessel (0.017), Network Segmentation (0.008), Remote Data Staging (0.003), Visual Basic (0.000), CrossRAT (0.000), Cobian RAT (0.000), The White Company (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Cobalt Strike (109 neighbors, 109 edges)
           → Data Transfer Size Limits (24 neighbors, 24 edges)
           → Data Staged (13 neighbors, 13 edges)
           → Kessel (14 neighbors, 14 edges)
           → Network Segmentation (37 neighbors, 37 edges)
[RETRIEVE-QUOTA] Query 4/5: บีบอัดข้อมูลแต่ละส่วนด้วยโปรแกรมบีบอัดไฟล์เพื่อเตรียมนำออก...
[RETRIEVE] Query: บีบอัดข้อมูลแต่ละส่วนด้วยโปรแกรมบีบอัดไฟล์เพื่อเตรียมนำออก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Compression (0.034), Software Packing (0.011), FRAMESTING (0.009), Archive via Utility (0.007), COATHANGER (0.003), Expand (0.003), Archive via Library (0.003), Expand (0.003), Forfiles (0.003), Catchamas (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Compression (38 neighbors, 38 edges)
           → Software Packing (106 neighbors, 106 edges)
           → FRAMESTING (8 neighbors, 8 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
           → Archive via Utility (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] Query 5/5: ส่งข้อมูลที่บีบอัดแล้วออกจากเครือข่ายไปยังบัญชีปลายทางที่คนร้ายควบคุม...
[RETRIEVE] Query: ส่งข้อมูลที่บีบอัดแล้วออกจากเครือข่ายไปยังบัญชีปลายทางที่คนร้ายควบคุม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration (0.216), Taint Shared Content (0.083), BlackByte (0.017), Communication Through Removable Media (0.013), Content Injection (0.012), Spearphishing via Service (0.009), Exfiltration Over C2 Channel (0.007), CASTLETAP (0.001), RAPIDPULSE (0.001), Input Injection (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration (19 neighbors, 19 edges)
           → Taint Shared Content (18 neighbors, 18 edges)
           → BlackByte (56 neighbors, 56 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Communication Through Removable Media (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [82/100] retrieved=605 relevant=4 latency=10681ms
[RETRIEVE-QUOTA] Query 1/10: เมื่อวันที่ 24 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนที่คนร...
[RETRIEVE] Query: เมื่อวันที่ 24 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนที่คนร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.044), VERMIN (0.027), VERMIN (0.011), APT-C-36 (0.005), Ursnif (0.001), File Deletion (0.000), Internal Spearphishing (0.000), Password Managers (0.000), Credentials In Files (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → VERMIN (17 neighbors, 17 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
[RETRIEVE-QUOTA] Query 2/10: Phishing email ที่มีไฟล์แนบมัลแวร์หลอกพนักงานเปิดไฟล์...
[RETRIEVE] Query: Phishing email ที่มีไฟล์แนบมัลแวร์หลอกพนักงานเปิดไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BLINDINGCAN (0.811), Molerats (0.556), Spearphishing Attachment (0.487), Spearphishing Link (0.355), Phishing (0.270), Spearphishing Attachment (0.141), AppleJeus (0.081), Spearphishing Link (0.009), Phishing for Information (0.008), VOID MANTICORE (0.005)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BLINDINGCAN (23 neighbors, 23 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Molerats (22 neighbors, 22 edges)
           → Spearphishing Link (93 neighbors, 93 edges)
           → Phishing (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 3/10: มัลแวร์ติดตั้ง backdoor เพื่อคงการเข้าถึงเครื่อง...
[RETRIEVE] Query: มัลแวร์ติดตั้ง backdoor เพื่อคงการเข้าถึงเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: metaMain (0.404), Upload Malware (0.137), Spark (0.008), APT32 (0.005), Spica (0.005), Empire (0.005), Nightdoor (0.005), Mongall (0.004), Heyoka Backdoor (0.003), APT32 (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → metaMain (29 neighbors, 29 edges)
           → Upload Malware (39 neighbors, 39 edges)
           → Spark (11 neighbors, 11 edges)
           → APT32 (93 neighbors, 93 edges)
           → Service Execution (78 neighbors, 78 edges)
[RETRIEVE-QUOTA] Query 4/10: ขโมยรหัสผ่านผู้ดูแลโดเมนจากเครื่องที่ติดเชื้อ...
[RETRIEVE] Query: ขโมยรหัสผ่านผู้ดูแลโดเมนจากเครื่องที่ติดเชื้อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AuTo Stealer (0.192), TONESHELL (0.078), ZxxZ (0.022), Diavol (0.017), Domain Accounts (0.010), DCSync (0.005), Net Crawler (0.004), DRYHOOK (0.002), OwaAuth (0.002), Threat Group-1314 (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AuTo Stealer (11 neighbors, 11 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → TONESHELL (44 neighbors, 44 edges)
           → ZxxZ (15 neighbors, 15 edges)
           → Diavol (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] Query 5/10: ลบไฟล์สคริปต์ลองรหัสผ่านเพื่อลบหลักฐาน...
[RETRIEVE] Query: ลบไฟล์สคริปต์ลองรหัสผ่านเพื่อลบหลักฐาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Audit (0.002), LaZagne (0.002), LockBit 2.0 (0.002), Clear Mailbox Data (0.002), Lslsass (0.001), OS Credential Dumping (0.001), Pay2Key (0.001), Deobfuscate/Decode Files or Information (0.001), Windows Credential Editor (0.000), Windows Registry Key Deletion (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Clear Mailbox Data (10 neighbors, 10 edges)
           → Audit (110 neighbors, 110 edges)
           → Credentials In Files (44 neighbors, 44 edges)
           → LaZagne (22 neighbors, 22 edges)
           → Proc Filesystem (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 6/10: ดาวน์โหลดสำเนาที่สองของโปรแกรมฝังตัวเข้ามาในระบบ...
[RETRIEVE] Query: ดาวน์โหลดสำเนาที่สองของโปรแกรมฝังตัวเข้ามาในระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Grandoreiro (0.051), DownPaper (0.034), Get2 (0.019), Chrommme (0.003), PsExec (0.000), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Grandoreiro (43 neighbors, 43 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → DownPaper (8 neighbors, 8 edges)
           → Get2 (7 neighbors, 7 edges)
           → Chrommme (14 neighbors, 14 edges)
[RETRIEVE-QUOTA] Query 7/10: คัดลอกไฟล์ติดตั้งไปวางในโฟลเดอร์ระบบของเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: คัดลอกไฟล์ติดตั้งไปวางในโฟลเดอร์ระบบของเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Taidoor (0.022), Conficker (0.011), SysUpdate (0.010), Local Data Staging (0.003), AppDomainManager (0.003), InstallUtil (0.001), Shared Modules (0.000), BackConfig (0.000), Regsvr32 (0.000), Installer Packages (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Taidoor (20 neighbors, 20 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Conficker (13 neighbors, 13 edges)
           → Windows Service (150 neighbors, 150 edges)
           → SysUpdate (32 neighbors, 32 edges)
           → Systemd Service (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] Query 8/10: ขยายการเข้าถึงไปยังเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Query: ขยายการเข้าถึงไปยังเครื่องแม่ข่ายควบคุมโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Network Segmentation (0.033), Network Segmentation (0.019), Additional Local or Domain Groups (0.018), Cobian RAT (0.004), Domain Account (0.004), Rogue Domain Controller (0.003), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Network Segmentation (37 neighbors, 37 edges)
           → Domain Account (18 neighbors, 18 edges)
           → Additional Local or Domain Groups (16 neighbors, 16 edges)
           → Create Account (14 neighbors, 14 edges)
           → Rogue Domain Controller (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 9/10: ไล่แจกแจงรายการงานตั้งเวลาบนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล...
[RETRIEVE] Query: ไล่แจกแจงรายการงานตั้งเวลาบนเครื่องแม่ข่ายควบคุมโดเมนจากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.038), Scheduled Task/Job (0.017), APT32 (0.006), SHOTPUT (0.006), DCSync (0.002), C0015 (0.002), System Time Discovery (0.002), Time Providers (0.001), Scheduled Task (0.001), Systemd Timers (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → At (17 neighbors, 17 edges)
           → Scheduled Task/Job (18 neighbors, 18 edges)
           → APT32 (93 neighbors, 93 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
[RETRIEVE-QUOTA] Query 10/10: ใช้รหัสผ่านผู้ดูแลโดเมนเพื่อเรียกไฟล์ที่วางไว้ให้ทำงาน...
[RETRIEVE] Query: ใช้รหัสผ่านผู้ดูแลโดเมนเพื่อเรียกไฟล์ที่วางไว้ให้ทำงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cached Domain Credentials (0.003), Group Policy Preferences (0.002), NTDS (0.002), Net (0.001), Pisloader (0.001), Reversible Encryption (0.000), Pisloader (0.000), Domain Account (0.000), Change Default File Association (0.000), Pisloader (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Cached Domain Credentials (16 neighbors, 16 edges)
           → Group Policy Preferences (11 neighbors, 11 edges)
           → NTDS (33 neighbors, 33 edges)
           → Net (50 neighbors, 50 edges)
           → Domain Account (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 10 queries
  [83/100] retrieved=625 relevant=3 latency=18440ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 15 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุ...
[RETRIEVE] Query: เมื่อวันที่ 15 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.045), Bankshot (0.017), Data from Local System (0.009), FIN8 (0.001), Password Managers (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Software Discovery (0.000), Account Use Policies (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/7: การบุกรุกจากเครื่องรับชำระเงินไปยังเครื่องของฝ่ายเทคโนโลยีสารสนเทศ (lateral move...
[RETRIEVE] Query: การบุกรุกจากเครื่องรับชำระเงินไปยังเครื่องของฝ่ายเทคโนโลยีสารสนเทศ (lateral move...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lateral Movement (0.135), Waterbear (0.062), Exploitation of Remote Services (0.045), Net (0.038), Lateral Tool Transfer (0.034), ConnectWise (0.007), SILENTTRINITY (0.006), GALLIUM (0.006), Reaver (0.000), Acquire Access (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Lateral Movement (23 neighbors, 23 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
           → Waterbear (15 neighbors, 15 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
           → Net (50 neighbors, 50 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
[RETRIEVE-QUOTA] Query 3/7: ดึงค่ารหัสผ่านออกจากฐานข้อมูลบัญชีผู้ใช้ที่เก็บในเครื่อง (credential dumping)...
[RETRIEVE] Query: ดึงค่ารหัสผ่านออกจากฐานข้อมูลบัญชีผู้ใช้ที่เก็บในเครื่อง (credential dumping)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: IceApple (0.337), Credentials In Files (0.315), OS Credential Dumping (0.313), pwdump (0.309), HOMEFRY (0.184), Windows Credential Editor (0.141), Credential Access (0.119), pwdump (0.078), Axiom (0.069), Credential Access Protection (0.039)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Credentials In Files (44 neighbors, 44 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → IceApple (19 neighbors, 19 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → pwdump (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 4/7: ใช้เครื่องมือสั่งงานเครื่องระยะไกลคัดลอกไฟล์โปรแกรมข้ามไปยังเครื่องอื่น (remote ...
[RETRIEVE] Query: ใช้เครื่องมือสั่งงานเครื่องระยะไกลคัดลอกไฟล์โปรแกรมข้ามไปยังเครื่องอื่น (remote ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.965), cmd (0.929), RemoteCMD (0.868), RemoteCMD (0.692), xCmd (0.429), RemoteCMD (0.353), cmd (0.098), Remote Access Tools (0.058), Indirect Command Execution (0.042), Command and Scripting Interpreter (0.009)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → cmd (13 neighbors, 13 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Scheduled Task (201 neighbors, 201 edges)
[RETRIEVE-QUOTA] Query 5/7: สั่งให้ทำงานไฟล์โปรแกรมบนเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ (execution)...
[RETRIEVE] Query: สั่งให้ทำงานไฟล์โปรแกรมบนเครื่องคอมพิวเตอร์ของเจ้าหน้าที่ (execution)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PsExec (0.052), Winexe (0.010), PsExec (0.010), cmd (0.007), CALENDAR (0.005), User Execution (0.002), cipher.exe (0.001), Pacu (0.000), Pacu (0.000), Pacu (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → PsExec (49 neighbors, 49 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Winexe (4 neighbors, 4 edges)
           → cmd (13 neighbors, 13 edges)
           → CALENDAR (3 neighbors, 3 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 6/7: วางไฟล์ไลบรารีในตำแหน่งที่ระบบค้นหาก่อนตำแหน่งจริง (DLL Hijacking / DLL Search O...
[RETRIEVE] Query: วางไฟล์ไลบรารีในตำแหน่งที่ระบบค้นหาก่อนตำแหน่งจริง (DLL Hijacking / DLL Search O...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: InvisiMole (0.940), DLL (0.727), Dylib Hijacking (0.615), Restrict Library Loading (0.573), Path Interception by Search Order Hijacking (0.481), Dynamic Linker Hijacking (0.230), FoggyWeb (0.171), Astaroth (0.118), Thread Execution Hijacking (0.052), VDSO Hijacking (0.049)
[RETRIEVE] Graph expansion: 5 subgraphs
           → InvisiMole (73 neighbors, 73 edges)
           → DLL (123 neighbors, 123 edges)
           → Dylib Hijacking (6 neighbors, 6 edges)
           → Path Interception by Search Order Hijacking (9 neighbors, 9 edges)
           → Restrict Library Loading (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] Query 7/7: โหลดไฟล์ของคนร้ายแทนไฟล์ที่ถูกต้องเพื่อยกระดับสิทธิ์ (privilege escalation via D...
[RETRIEVE] Query: โหลดไฟล์ของคนร้ายแทนไฟล์ที่ถูกต้องเพื่อยกระดับสิทธิ์ (privilege escalation via D...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DLL (0.773), Downdelph (0.548), Thread Execution Hijacking (0.213), Dynamic Linker Hijacking (0.074), Execution Prevention (0.067), Privilege Escalation (0.058), VDSO Hijacking (0.054), Executable Installer File Permissions Weakness (0.035), Path Interception by Search Order Hijacking (0.035), PowerSploit (0.031)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DLL (123 neighbors, 123 edges)
           → Downdelph (6 neighbors, 6 edges)
           → Thread Execution Hijacking (9 neighbors, 9 edges)
           → Dynamic Linker Hijacking (16 neighbors, 16 edges)
           → Execution Prevention (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [84/100] retrieved=793 relevant=3 latency=15115ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 19 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งความเพิ่มเติมว่าพบกา...
[RETRIEVE] Query: เมื่อวันที่ 19 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งความเพิ่มเติมว่าพบกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackConfig (0.013), APT37 (0.010), Remote System Discovery (0.003), Data from Network Shared Drive (0.002), FIN8 (0.000), System Network Connections Discovery (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Pikabot (0.000), CrossRAT (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BackConfig (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → APT37 (42 neighbors, 42 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
[RETRIEVE-QUOTA] Query 2/6: เรียกดูชื่อบัญชีผู้ใช้ที่กำลังทำงานอยู่บนเครื่องที่ยึดครอง (Account Discovery)...
[RETRIEVE] Query: เรียกดูชื่อบัญชีผู้ใช้ที่กำลังทำงานอยู่บนเครื่องที่ยึดครอง (Account Discovery)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: UPPERCUT (0.278), System Owner/User Discovery (0.216), Account Discovery (0.188), HAPPYWORK (0.037), Wi-Fi Discovery (0.022), OSInfo (0.006), Process Discovery (0.001), TAINTEDSCRIBE (0.001), System Network Connections Discovery (0.001), Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → UPPERCUT (18 neighbors, 18 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
           → Account Discovery (18 neighbors, 18 edges)
           → HAPPYWORK (4 neighbors, 4 edges)
           → Wi-Fi Discovery (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] Query 3/6: เรียกดูรายละเอียดระบบปฏิบัติการที่ติดตั้งบนเครื่อง (System Information Discovery...
[RETRIEVE] Query: เรียกดูรายละเอียดระบบปฏิบัติการที่ติดตั้งบนเครื่อง (System Information Discovery...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Systeminfo (0.710), cmd (0.605), SYSCON (0.391), System Information Discovery (0.281), Systeminfo (0.108), System Network Configuration Discovery (0.049), System Time Discovery (0.015), System Owner/User Discovery (0.011), Device Driver Discovery (0.003), Process Discovery (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Systeminfo (14 neighbors, 14 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → cmd (13 neighbors, 13 edges)
           → SYSCON (6 neighbors, 6 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] Query 4/6: ไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์บนเครื่องเพื่อค้นหาข้อมูล (File and Directory Dis...
[RETRIEVE] Query: ไล่แจกแจงรายชื่อไฟล์และโฟลเดอร์บนเครื่องเพื่อค้นหาข้อมูล (File and Directory Dis...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DynoWiper (0.906), File and Directory Discovery (0.673), SILENTTRINITY (0.493), BoomBox (0.408), Forfiles (0.319), Network Share Discovery (0.077), Cloud Storage Object Discovery (0.055), Forfiles (0.037), System Information Discovery (0.014), System Owner/User Discovery (0.008)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DynoWiper (10 neighbors, 10 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
           → BoomBox (17 neighbors, 17 edges)
           → Forfiles (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 5/6: เก็บรวบรวมข้อมูลเซสชัน Remote Desktop Connection ที่ค้างอยู่บนเครื่อง...
[RETRIEVE] Query: เก็บรวบรวมข้อมูลเซสชัน Remote Desktop Connection ที่ค้างอยู่บนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RedLeaves (0.173), RDP Hijacking (0.040), RCSession (0.040), Remote Desktop Protocol (0.009), Terminal Services DLL (0.004), Clear Network Connection History and Configurations (0.003), Execution Prevention (0.001), Remote Desktop Software (0.001), Remote Access Tools (0.001), Remote Services (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RedLeaves (18 neighbors, 18 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → RCSession (24 neighbors, 24 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 6/6: ดึงชื่อผู้ใช้ หมายเลขไอพี และชื่อเครื่องแม่ข่ายจากข้อมูลการเชื่อมต่อระยะไกล (Cre...
[RETRIEVE] Query: ดึงชื่อผู้ใช้ หมายเลขไอพี และชื่อเครื่องแม่ข่ายจากข้อมูลการเชื่อมต่อระยะไกล (Cre...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Service Session Hijacking (0.148), Logon Session Creation (0.025), Remote Services (0.017), IceApple (0.016), Forge Web Credentials (0.008), RCSession (0.008), APT28 (0.004), Remote Desktop Protocol (0.003), User Account Management (0.002), Active Directory Credential Request (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Remote Service Session Hijacking (9 neighbors, 9 edges)
           → Logon Session Creation (0 neighbors, 0 edges)
           → Remote Services (23 neighbors, 23 edges)
           → IceApple (19 neighbors, 19 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [85/100] retrieved=632 relevant=4 latency=13362ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 20 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าถูกหลอกให้ติดตั้งโปร...
[RETRIEVE] Query: เมื่อวันที่ 20 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าถูกหลอกให้ติดตั้งโปร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pikabot (0.021), Clambling (0.018), CoinTicker (0.015), EventBot (0.008), Encrypted/Encoded File (0.004), Symmetric Cryptography (0.003), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.003), Lucifer (0.002), Deobfuscate/Decode Files or Information (0.002), Subvert Trust Controls (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pikabot (24 neighbors, 24 edges)
           → Symmetric Cryptography (188 neighbors, 188 edges)
           → Clambling (35 neighbors, 35 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → CoinTicker (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 2/5: หลอกให้ผู้เสียหายติดตั้งโปรแกรมซื้อขายสินทรัพย์ดิจิทัลปลอมบนวินโดวส์...
[RETRIEVE] Query: หลอกให้ผู้เสียหายติดตั้งโปรแกรมซื้อขายสินทรัพย์ดิจิทัลปลอมบนวินโดวส์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CoinTicker (0.124), Lucifer (0.009), APT41 DUST (0.006), Saint Bot (0.002), Cardinal RAT (0.001), CrossRAT (0.001), Cobian RAT (0.000), Visual Basic (0.000), 4H RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → CoinTicker (9 neighbors, 9 edges)
           → Lucifer (24 neighbors, 24 edges)
           → APT41 DUST (28 neighbors, 28 edges)
           → Masquerade Task or Service (94 neighbors, 94 edges)
           → Saint Bot (39 neighbors, 39 edges)
           → Match Legitimate Resource Name or Location (221 neighbors, 221 edges)
[RETRIEVE-QUOTA] Query 3/5: User Execution: Malicious File โปรแกรมปลอมขอสิทธิ์ผู้ดูแลระบบ...
[RETRIEVE] Query: User Execution: Malicious File โปรแกรมปลอมขอสิทธิ์ผู้ดูแลระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Malicious File (0.394), Execution Prevention (0.269), User Execution (0.242), FIN6 (0.175), TYPEFRAME (0.128), System Script Proxy Execution (0.058), User Training (0.046), GUI Input Capture (0.030), Malicious Link (0.024), Execution (0.019)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Malicious File (202 neighbors, 202 edges)
           → User Execution (18 neighbors, 18 edges)
           → Execution Prevention (79 neighbors, 79 edges)
           → FIN6 (52 neighbors, 52 edges)
           → TYPEFRAME (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 4/5: Obfuscated Files or Information ใช้ไลบรารีบิดเบือนโครงสร้างโปรแกรมป้องกันการถอดร...
[RETRIEVE] Query: Obfuscated Files or Information ใช้ไลบรารีบิดเบือนโครงสร้างโปรแกรมป้องกันการถอดร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SynAck (0.888), WireLurker (0.807), PUBLOAD (0.605), ISMInjector (0.503), Deobfuscate/Decode Files or Information (0.423), Obfuscated Files or Information (0.392), Encrypted/Encoded File (0.030), Compression (0.008), Malicious File (0.002), Polymorphic Code (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SynAck (14 neighbors, 14 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → WireLurker (2 neighbors, 2 edges)
           → Obfuscated Files or Information (51 neighbors, 51 edges)
           → PUBLOAD (36 neighbors, 36 edges)
[RETRIEVE-QUOTA] Query 5/5: Encrypted Channel: Symmetric Cryptography ใช้อัลกอริทึมเข้ารหัสแบบสตรีมกับเครื่อ...
[RETRIEVE] Query: Encrypted Channel: Symmetric Cryptography ใช้อัลกอริทึมเข้ารหัสแบบสตรีมกับเครื่อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Duqu (0.809), Symmetric Cryptography (0.735), Encrypted Channel (0.575), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.235), ZIPLINE (0.149), Epic (0.127), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.068), Asymmetric Cryptography (0.039), Archive Collected Data (0.001), Playcrypt (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Symmetric Cryptography (188 neighbors, 188 edges)
           → Duqu (21 neighbors, 21 edges)
           → Encrypted Channel (23 neighbors, 23 edges)
           → Exfiltration Over Symmetric Encrypted Non-C2 Protocol (6 neighbors, 6 edges)
           → ZIPLINE (10 neighbors, 10 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [86/100] retrieved=452 relevant=3 latency=10043ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 17 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงช่องทางที่...
[RETRIEVE] Query: เมื่อวันที่ 17 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงช่องทางที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan Australian Intrusions (0.311), Threat Group-3390 (0.111), External Remote Services (0.052), Valid Accounts (0.031), Remote Services (0.017), Remote Desktop Protocol (0.005), User Account Management (0.000), Exploitation of Remote Services (0.000), Remote Service Session Hijacking (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Leviathan Australian Intrusions (27 neighbors, 27 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Threat Group-3390 (81 neighbors, 81 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → Remote Services (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 2/9: External Remote Services ผ่านบริการเชื่อมต่อหน้าจอระยะไกลและ VPN ที่เปิดให้เข้าถ...
[RETRIEVE] Query: External Remote Services ผ่านบริการเชื่อมต่อหน้าจอระยะไกลและ VPN ที่เปิดให้เข้าถ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Remote Services (0.944), LAPSUS$ (0.784), Limit Access to Resource Over Network (0.748), Operation Wocao (0.394), Web Portal Capture (0.126), RDP Hijacking (0.009), Terminal Services DLL (0.008), Remote Access Tools (0.003), Remote Desktop Protocol (0.001), Limit Access to Resource Over Network (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → External Remote Services (52 neighbors, 52 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Operation Wocao (79 neighbors, 79 edges)
           → Web Portal Capture (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 3/9: Valid Accounts บัญชีผู้ใช้ที่ยังใช้งานได้เพื่อเข้าถึงเครือข่าย...
[RETRIEVE] Query: Valid Accounts บัญชีผู้ใช้ที่ยังใช้งานได้เพื่อเข้าถึงเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: GALLIUM (0.926), Valid Accounts (0.466), Cloud Accounts (0.152), APT18 (0.109), User Account Management (0.044), Domain Account (0.005), Create Account (0.004), User Account Management (0.001), User Account Modification (0.000), Establish Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → GALLIUM (47 neighbors, 47 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Cloud Accounts (33 neighbors, 33 edges)
           → APT18 (17 neighbors, 17 edges)
           → User Account Management (119 neighbors, 119 edges)
[RETRIEVE-QUOTA] Query 4/9: Exploit Public-Facing Application ช่องโหว่ของแอปพลิเคชันที่เปิดให้บริการต่อสาธาร...
[RETRIEVE] Query: Exploit Public-Facing Application ช่องโหว่ของแอปพลิเคชันที่เปิดให้บริการต่อสาธาร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.693), Leviathan (0.361), Update Software (0.242), Network Segmentation (0.214), Limit Access to Resource Over Network (0.205), Exploitation for Client Execution (0.009), Application or System Exploitation (0.007), Exploit Protection (0.001), Exploits (0.001), Exploits (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Leviathan (68 neighbors, 68 edges)
           → Update Software (42 neighbors, 42 edges)
           → Network Segmentation (37 neighbors, 37 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] Query 5/9: Exploit ช่องโหว่ของอุปกรณ์ไฟร์วอลล์ที่ยังไม่ได้ปรับปรุง...
[RETRIEVE] Query: Exploit ช่องโหว่ของอุปกรณ์ไฟร์วอลล์ที่ยังไม่ได้ปรับปรุง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN6 (0.006), Exploits (0.004), Exploits (0.002), Phenakite (0.002), Exploit Protection (0.002), Exploit Public-Facing Application (0.001), Exploit Protection (0.001), Exploit Protection (0.001), Exploitation for Privilege Escalation (0.001), Exploitation for Credential Access (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → FIN6 (52 neighbors, 52 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → Exploits (7 neighbors, 7 edges)
           → Exploits (5 neighbors, 5 edges)
           → Phenakite (11 neighbors, 11 edges)
           → Exploitation for Privilege Escalation (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 6/9: Exploit ช่องโหว่ของเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ที่ยังไม่ได้ปรับปรุง...
[RETRIEVE] Query: Exploit ช่องโหว่ของเครื่องแม่ข่ายจดหมายอิเล็กทรอนิกส์ที่ยังไม่ได้ปรับปรุง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT1 (0.007), Sandworm Team (0.007), Exploits (0.001), Exploits (0.001), Exploit Public-Facing Application (0.001), Exploit Protection (0.001), Exploit Protection (0.001), Exploitation for Credential Access (0.000), Exploit Protection (0.000), Email Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT1 (40 neighbors, 40 edges)
           → Remote Email Collection (26 neighbors, 26 edges)
           → Sandworm Team (113 neighbors, 113 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Exploits (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] Query 7/9: Domain Name System (DNS) query เพื่อไล่เก็บรายละเอียดของเครือข่าย...
[RETRIEVE] Query: Domain Name System (DNS) query เพื่อไล่เก็บรายละเอียดของเครือข่าย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DNS/Passive DNS (0.468), DnsSystem (0.122), DNS (0.090), DNS (0.036), DNS Server (0.021), dsquery (0.019), dsquery (0.013), OilRig (0.004), Doki (0.001), Name Resolution Poisoning and SMB Relay (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DNS/Passive DNS (3 neighbors, 3 edges)
           → DnsSystem (10 neighbors, 10 edges)
           → DNS (60 neighbors, 60 edges)
           → DNS (3 neighbors, 3 edges)
           → DNS Server (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 8/9: Network Service Scanning เครื่องมือสอบถามข้อมูลจากระบบทะเบียนโดเมน...
[RETRIEVE] Query: Network Service Scanning เครื่องมือสอบถามข้อมูลจากระบบทะเบียนโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cobalt Group (0.139), OilRig (0.133), dsquery (0.091), dsquery (0.019), dsquery (0.008), Nltest (0.006), Scan Databases (0.006), Scanning IP Blocks (0.002), Active Scanning (0.002), Vulnerability Scanning (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Cobalt Group (40 neighbors, 40 edges)
           → Network Service Discovery (78 neighbors, 78 edges)
           → OilRig (108 neighbors, 108 edges)
           → dsquery (9 neighbors, 9 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 9/9: System Information Discovery โปรแกรมขโมยข้อมูลตรวจสอบโปรแกรมป้องกันไวรัสที่ติดตั...
[RETRIEVE] Query: System Information Discovery โปรแกรมขโมยข้อมูลตรวจสอบโปรแกรมป้องกันไวรัสที่ติดตั...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OSInfo (0.550), yty (0.352), System Information Discovery (0.141), Systeminfo (0.119), Software Discovery (0.044), DEFENSOR ID (0.024), Backup Software Discovery (0.008), System Owner/User Discovery (0.008), System Time Discovery (0.002), Process Discovery (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → OSInfo (11 neighbors, 11 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → yty (15 neighbors, 15 edges)
           → Systeminfo (14 neighbors, 14 edges)
           → Software Discovery (56 neighbors, 56 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [87/100] retrieved=253 relevant=5 latency=17105ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 16 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความเพิ่มเติมถึงจุดเริ่มต้นที่ลูกค...
[RETRIEVE] Query: เมื่อวันที่ 16 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความเพิ่มเติมถึงจุดเริ่มต้นที่ลูกค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pony (0.403), SYSCON (0.110), User Training (0.073), User Execution (0.049), Malicious File (0.046), User Training (0.033), Malicious Link (0.013), Spearphishing Link (0.008), Maze (0.007), Exploitation for Client Execution (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pony (16 neighbors, 16 edges)
           → Malicious Link (93 neighbors, 93 edges)
           → SYSCON (6 neighbors, 6 edges)
           → Malicious File (202 neighbors, 202 edges)
           → User Training (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] Query 2/9: อีเมลหลอกลวง Phishing ที่ปรับเนื้อความให้ตรงกับผู้รับแต่ละราย...
[RETRIEVE] Query: อีเมลหลอกลวง Phishing ที่ปรับเนื้อความให้ตรงกับผู้รับแต่ละราย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kimsuky (0.121), Phishing (0.055), Written Content (0.028), Spearphishing Attachment (0.013), APT42 (0.012), Phishing for Information (0.011), Spearphishing Link (0.010), Spearphishing Service (0.010), VOID MANTICORE (0.006), Kimsuky (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Kimsuky (150 neighbors, 150 edges)
           → Phishing for Information (12 neighbors, 12 edges)
           → Phishing (23 neighbors, 23 edges)
           → Written Content (5 neighbors, 5 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 3/9: ไฟล์แนบอันตรายในอีเมล Phishing...
[RETRIEVE] Query: ไฟล์แนบอันตรายในอีเมล Phishing...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Saint Bear (0.919), FIN4 (0.908), Spearphishing Attachment (0.837), Spearphishing Link (0.805), Spearphishing Attachment (0.690), Phishing (0.359), Spearphishing Link (0.010), VOID MANTICORE (0.004), Phishing for Information (0.004), Kimsuky (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Spearphishing Link (93 neighbors, 93 edges)
           → Saint Bear (20 neighbors, 20 edges)
           → FIN4 (12 neighbors, 12 edges)
           → Spearphishing Attachment (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 4/9: ลิงก์อันตรายในอีเมล Phishing...
[RETRIEVE] Query: ลิงก์อันตรายในอีเมล Phishing...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Spearphishing Link (0.960), Hancitor (0.949), FIN4 (0.934), Link Target (0.785), Spearphishing Link (0.607), Phishing (0.420), Spearphishing Attachment (0.012), VOID MANTICORE (0.009), Phishing for Information (0.005), Kimsuky (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Spearphishing Link (93 neighbors, 93 edges)
           → Hancitor (14 neighbors, 14 edges)
           → Link Target (8 neighbors, 8 edges)
           → FIN4 (12 neighbors, 12 edges)
           → Malicious Link (93 neighbors, 93 edges)
[RETRIEVE-QUOTA] Query 5/9: User Execution: Malicious Link เมื่อผู้รับกดลิงก์...
[RETRIEVE] Query: User Execution: Malicious Link เมื่อผู้รับกดลิงก์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Malicious Link (0.939), Kerrdown (0.805), TA577 (0.757), User Execution (0.585), Link Target (0.436), User Training (0.260), Spearphishing Link (0.125), Malicious File (0.024), Malicious Copy and Paste (0.014), Execution (0.012)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Malicious Link (93 neighbors, 93 edges)
           → Kerrdown (12 neighbors, 12 edges)
           → TA577 (9 neighbors, 9 edges)
           → User Execution (18 neighbors, 18 edges)
           → Link Target (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] Query 6/9: User Execution: Malicious File เมื่อผู้รับเปิดไฟล์แนบ...
[RETRIEVE] Query: User Execution: Malicious File เมื่อผู้รับเปิดไฟล์แนบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mofang (0.904), Malicious File (0.860), User Execution (0.671), TYPEFRAME (0.519), Execution Prevention (0.152), User Training (0.090), Executable Installer File Permissions Weakness (0.046), Malicious Link (0.045), Execution (0.023), Double File Extension (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Malicious File (202 neighbors, 202 edges)
           → Mofang (8 neighbors, 8 edges)
           → User Execution (18 neighbors, 18 edges)
           → TYPEFRAME (16 neighbors, 16 edges)
           → Execution Prevention (79 neighbors, 79 edges)
[RETRIEVE-QUOTA] Query 7/9: ดาวน์โหลดไฟล์สคริปต์จาวาสคริปต์โดยผู้ใช้ไม่ทราบ...
[RETRIEVE] Query: ดาวน์โหลดไฟล์สคริปต์จาวาสคริปต์โดยผู้ใช้ไม่ทราบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Javali (0.088), YiSpecter (0.003), XLoader (0.002), JavaScript (0.001), Mark-of-the-Web Bypass (0.001), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Javali (12 neighbors, 12 edges)
           → Visual Basic (140 neighbors, 140 edges)
           → YiSpecter (12 neighbors, 12 edges)
           → Download New Code at Runtime (42 neighbors, 42 edges)
           → JavaScript (76 neighbors, 76 edges)
[RETRIEVE-QUOTA] Query 8/9: สคริปต์ติดต่อเครื่องสั่งการของคนร้าย (Command and Control)...
[RETRIEVE] Query: สคริปต์ติดต่อเครื่องสั่งการของคนร้าย (Command and Control)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Command and Control (0.157), Trap (0.017), Command and Scripting Interpreter (0.013), ECCENTRICBANDWAGON (0.005), Anubis (0.002), Chameleon (0.002), WolfRAT (0.001), Bypass User Account Control (0.000), User Account Control (0.000), Windows Permissions (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Command and Control (45 neighbors, 45 edges)
           → Trap (5 neighbors, 5 edges)
           → Command and Scripting Interpreter (68 neighbors, 68 edges)
           → ECCENTRICBANDWAGON (8 neighbors, 8 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 9/9: ดาวน์โหลดและติดตั้งโปรแกรมม้าโทรจัน (Trojan Installation)...
[RETRIEVE] Query: ดาวน์โหลดและติดตั้งโปรแกรมม้าโทรจัน (Trojan Installation)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pony (0.133), ISMInjector (0.020), Trojan.Karagany (0.016), OopsIE (0.009), Trojan.Karagany (0.008), YAHOYAH (0.008), Catchamas (0.006), Trojan.Mebromi (0.003), Trojan.Karagany (0.001), Trojan.Karagany (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pony (16 neighbors, 16 edges)
           → ISMInjector (5 neighbors, 5 edges)
           → Trojan.Karagany (23 neighbors, 23 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → OopsIE (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [88/100] retrieved=361 relevant=3 latency=16735ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 13 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Query: เมื่อวันที่ 13 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Storm-1811 (0.045), POWERSTATS (0.033), POWERSTATS (0.030), FIN7 (0.007), PowerShell Profile (0.006), POWERSOURCE (0.003), Forced Authentication (0.000), PowerShell (0.000), Disable or Remove Feature or Program (0.000), Input Injection (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Storm-1811 (38 neighbors, 38 edges)
           → Input Capture (20 neighbors, 20 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → PowerShell (241 neighbors, 241 edges)
           → PowerShell Profile (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 2/7: รันสคริปต์สร้างช่องทางสื่อสารระหว่างกระบวนการ (Named Pipe) เพื่อหลอกบริการระบบเช...
[RETRIEVE] Query: รันสคริปต์สร้างช่องทางสื่อสารระหว่างกระบวนการ (Named Pipe) เพื่อหลอกบริการระบบเช...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Medusa Ransomware (0.554), ROADSWEEP (0.300), Process Injection (0.027), Named Pipe Metadata (0.027), Poisoned Pipeline Execution (0.015), Native API (0.001), Rocke (0.000), PipeMon (0.000), PipeMon (0.000), PipeMon (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Medusa Ransomware (23 neighbors, 23 edges)
           → Inter-Process Communication (28 neighbors, 28 edges)
           → ROADSWEEP (16 neighbors, 16 edges)
           → Process Injection (104 neighbors, 104 edges)
           → Named Pipe Metadata (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 3/7: สวมสิทธิ์ประจำตัวของบริการระบบเพื่อยกระดับเป็นสิทธิ์ระดับระบบ...
[RETRIEVE] Query: สวมสิทธิ์ประจำตัวของบริการระบบเพื่อยกระดับเป็นสิทธิ์ระดับระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PsExec (0.275), Privilege Escalation (0.189), AppleSeed (0.093), Temporary Elevated Cloud Access (0.004), Parent PID Spoofing (0.004), Trust Modification (0.003), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PsExec (49 neighbors, 49 edges)
           → Windows Service (150 neighbors, 150 edges)
           → Privilege Escalation (96 neighbors, 96 edges)
           → AppleSeed (33 neighbors, 33 edges)
           → Access Token Manipulation (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 4/7: เรียกสคริปต์จากเครื่องภายนอกผ่าน PowerShell...
[RETRIEVE] Query: เรียกสคริปต์จากเครื่องภายนอกผ่าน PowerShell...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: POWRUNER (0.253), PowerShell (0.094), AADInternals (0.020), POWERSOURCE (0.018), PowerShell Profile (0.012), PowerExchange (0.009), Invoke-PSImage (0.007), POWERSTATS (0.003), Disable or Remove Feature or Program (0.002), POWERSTATS (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → POWRUNER (21 neighbors, 21 edges)
           → PowerShell (241 neighbors, 241 edges)
           → AADInternals (26 neighbors, 26 edges)
           → PowerShell Profile (9 neighbors, 9 edges)
           → POWERSOURCE (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] Query 5/7: ดึงรหัสผ่านจากหน่วยความจำของกระบวนการยืนยันตัวตน...
[RETRIEVE] Query: ดึงรหัสผ่านจากหน่วยความจำของกระบวนการยืนยันตัวตน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PACEMAKER (0.206), Lslsass (0.130), pwdump (0.128), OS Credential Dumping (0.034), Security Account Manager (0.015), Credential Access Protection (0.002), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PACEMAKER (7 neighbors, 7 edges)
           → Proc Filesystem (8 neighbors, 8 edges)
           → pwdump (7 neighbors, 7 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → Lslsass (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 6/7: บีบอัดไฟล์ข้อความที่รวบรวมไว้และเปลี่ยนชื่อไฟล์ให้ดูไม่ผิดสังเกต...
[RETRIEVE] Query: บีบอัดไฟล์ข้อความที่รวบรวมไว้และเปลี่ยนชื่อไฟล์ให้ดูไม่ผิดสังเกต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OopsIE (0.032), Compression (0.018), Archive via Library (0.005), Masquerade File Type (0.002), TAINTEDSCRIBE (0.002), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → OopsIE (20 neighbors, 20 edges)
           → Archive via Custom Method (42 neighbors, 42 edges)
           → Compression (38 neighbors, 38 edges)
           → Archive via Library (18 neighbors, 18 edges)
           → Masquerade File Type (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 7/7: เตรียมไฟล์บีบอัดเพื่อนำออกจากองค์กร...
[RETRIEVE] Query: เตรียมไฟล์บีบอัดเพื่อนำออกจากองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Archive via Utility (0.001), Archive via Library (0.001), BBSRAT (0.000), Remote Data Storage (0.000), Remote Data Staging (0.000), BITSAdmin (0.000), Visual Basic (0.000), The White Company (0.000), CrossRAT (0.000), Cardinal RAT (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Archive via Utility (88 neighbors, 88 edges)
           → Archive via Library (18 neighbors, 18 edges)
           → BBSRAT (14 neighbors, 14 edges)
           → Remote Data Storage (11 neighbors, 11 edges)
           → Remote Data Staging (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [89/100] retrieved=344 relevant=3 latency=13797ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงเครื่องมือ...
[RETRIEVE] Query: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงเครื่องมือ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.461), HOMEFRY (0.405), Suckfly (0.318), OS Credential Dumping (0.221), BlackByte (0.218), Windows Credential Editor (0.205), Credential Access (0.014), Credential Access Protection (0.004), Credential Stuffing (0.001), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → HOMEFRY (4 neighbors, 4 edges)
           → Suckfly (6 neighbors, 6 edges)
           → BlackByte (56 neighbors, 56 edges)
[RETRIEVE-QUOTA] Query 2/7: รันชุดสคริปต์สำเร็จรูปเพื่อไล่ตรวจสอบช่องทางยกระดับสิทธิ์...
[RETRIEVE] Query: รันชุดสคริปต์สำเร็จรูปเพื่อไล่ตรวจสอบช่องทางยกระดับสิทธิ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Elevated Execution with Prompt (0.021), AppCert DLLs (0.007), OSX/Shlayer (0.006), Ptrace System Calls (0.005), Koadic (0.004), Bypass User Account Control (0.002), Privilege Escalation (0.002), PHASEJAM (0.002), SILENTTRINITY (0.001), Exploitation for Credential Access (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Elevated Execution with Prompt (5 neighbors, 5 edges)
           → AppCert DLLs (7 neighbors, 7 edges)
           → Ptrace System Calls (7 neighbors, 7 edges)
           → OSX/Shlayer (15 neighbors, 15 edges)
           → Koadic (31 neighbors, 31 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
[RETRIEVE-QUOTA] Query 3/7: ปิดการทำงานของโปรแกรมป้องกันไวรัส (Antivirus Disabling)...
[RETRIEVE] Query: ปิดการทำงานของโปรแกรมป้องกันไวรัส (Antivirus Disabling)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pysa (0.300), TinyZBot (0.121), Disable or Remove Feature or Program (0.023), Antivirus/Antimalware (0.022), Firewall Disable (0.009), Cloud Service Disable (0.002), Execution Prevention (0.002), Clambling (0.001), Clambling (0.000), Clambling (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Pysa (16 neighbors, 16 edges)
           → Disable or Modify Tools (142 neighbors, 142 edges)
           → TinyZBot (9 neighbors, 9 edges)
           → Disable or Remove Feature or Program (71 neighbors, 71 edges)
           → Antivirus/Antimalware (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 4/7: ลบไฟล์บันทึกเหตุการณ์ของระบบ (Log Deletion)...
[RETRIEVE] Query: ลบไฟล์บันทึกเหตุการณ์ของระบบ (Log Deletion)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LockBit 2.0 (0.576), Clear Windows Event Logs (0.290), Windows Registry Key Deletion (0.164), Binary Validator (0.144), FinFisher (0.138), Snapshot Deletion (0.022), Instance Deletion (0.016), User Account Deletion (0.009), Volume Deletion (0.008), Mustang Panda (0.007)
[RETRIEVE] Graph expansion: 5 subgraphs
           → LockBit 2.0 (26 neighbors, 26 edges)
           → Clear Windows Event Logs (47 neighbors, 47 edges)
           → Windows Registry Key Deletion (0 neighbors, 0 edges)
           → Binary Validator (8 neighbors, 8 edges)
           → File Deletion (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 5/7: ค้นหาข้อมูลรับรองตัวตนที่เก็บไว้ในระบบ...
[RETRIEVE] Query: ค้นหาข้อมูลรับรองตัวตนที่เก็บไว้ในระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Unsecured Credentials (0.670), Credentials in Registry (0.663), PowerSploit (0.417), Security Account Manager (0.255), Reg (0.197), Kimsuky (0.128), gsecdump (0.103), Windows Credential Manager (0.060), pwdump (0.023), POWERSTATS (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Unsecured Credentials (27 neighbors, 27 edges)
           → Credentials in Registry (16 neighbors, 16 edges)
           → PowerSploit (39 neighbors, 39 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → Reg (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 6/7: Credential Dumping ดึงรหัสผ่านจากหน่วยความจำ...
[RETRIEVE] Query: Credential Dumping ดึงรหัสผ่านจากหน่วยความจำ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LaZagne (0.955), MgBot (0.910), OS Credential Dumping (0.853), Credentials In Files (0.737), Credential Access (0.423), pwdump (0.355), Axiom (0.319), Windows Credential Editor (0.293), Credential Access Protection (0.242), Password Cracking (0.095)
[RETRIEVE] Graph expansion: 5 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → LaZagne (22 neighbors, 22 edges)
           → LSASS Memory (89 neighbors, 89 edges)
           → MgBot (18 neighbors, 18 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 7/7: ได้สิทธิ์ระดับผู้ดูแลโดเมน (Domain Administrator Privilege Escalation)...
[RETRIEVE] Query: ได้สิทธิ์ระดับผู้ดูแลโดเมน (Domain Administrator Privilege Escalation)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Privilege Escalation (0.629), Domain Accounts (0.457), Exploitation for Privilege Escalation (0.210), CosmicDuke (0.161), BITTER (0.149), Abuse Elevation Control Mechanism (0.034), OSX/Shlayer (0.026), AppleSeed (0.021), Local Accounts (0.009), Software Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Privilege Escalation (96 neighbors, 96 edges)
           → Domain Accounts (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → CosmicDuke (20 neighbors, 20 edges)
           → BITTER (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [90/100] retrieved=120 relevant=4 latency=12343ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 6 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Query: เมื่อวันที่ 6 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.014), Seth-Locker (0.013), Clambling (0.012), Clambling (0.009), Ursnif (0.005), APT-C-36 (0.002), Subvert Trust Controls (0.000), Internal Spearphishing (0.000), Data Encrypted for Impact (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Clambling (35 neighbors, 35 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Seth-Locker (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] Query 2/6: อีเมล Phishing ที่เขียนถึงเจ้าหน้าที่โดยเฉพาะพร้อมลิงก์ดาวน์โหลดไฟล์ตัวปล่อยโปรแ...
[RETRIEVE] Query: อีเมล Phishing ที่เขียนถึงเจ้าหน้าที่โดยเฉพาะพร้อมลิงก์ดาวน์โหลดไฟล์ตัวปล่อยโปรแ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Spearphishing Link (0.777), Chaes (0.235), Molerats (0.147), Phishing (0.085), Spearphishing Attachment (0.069), Spearphishing Link (0.021), VOID MANTICORE (0.016), Spearphishing Attachment (0.012), Phishing for Information (0.004), Kimsuky (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Spearphishing Link (93 neighbors, 93 edges)
           → Chaes (28 neighbors, 28 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Molerats (22 neighbors, 22 edges)
           → Phishing (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 3/6: ดาวน์โหลดไฟล์ตัวปล่อยโปรแกรมอันตรายผ่านลิงก์ในอีเมล...
[RETRIEVE] Query: ดาวน์โหลดไฟล์ตัวปล่อยโปรแกรมอันตรายผ่านลิงก์ในอีเมล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Spearphishing Link (0.849), Evilnum (0.463), JSS Loader (0.165), GuLoader (0.036), IMAPLoader (0.017), Cobian RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Spearphishing Link (93 neighbors, 93 edges)
           → Evilnum (14 neighbors, 14 edges)
           → Malicious Link (93 neighbors, 93 edges)
           → JSS Loader (8 neighbors, 8 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] Query 4/6: เปิดไฟล์ตัวปล่อยโปรแกรมทำให้มัลแวร์ทำงานและติดตั้งโปรแกรมฝังตัวบนเครื่อง...
[RETRIEVE] Query: เปิดไฟล์ตัวปล่อยโปรแกรมทำให้มัลแวร์ทำงานและติดตั้งโปรแกรมฝังตัวบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DEADEYE (0.060), Dok (0.054), Bumblebee (0.044), BadPatch (0.016), EvilGrab (0.007), Pasam (0.005), P8RAT (0.005), Mavinject (0.004), FLASHFLOOD (0.004), Netwalker (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → DEADEYE (13 neighbors, 13 edges)
           → Bumblebee (41 neighbors, 41 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Dok (11 neighbors, 11 edges)
           → BadPatch (12 neighbors, 12 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 5/6: รันคำสั่งแจกแจงรายชื่อกลุ่มสิทธิ์ในโดเมนขององค์กร...
[RETRIEVE] Query: รันคำสั่งแจกแจงรายชื่อกลุ่มสิทธิ์ในโดเมนขององค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SoreFang (0.338), FIN7 (0.270), C0015 (0.254), Nltest (0.158), Domain Groups (0.122), Dragonfly (0.107), Domain Account (0.030), Group Metadata (0.015), Cloud Groups (0.004), Additional Local or Domain Groups (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → SoreFang (15 neighbors, 15 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → FIN7 (86 neighbors, 86 edges)
           → C0015 (39 neighbors, 39 edges)
           → Nltest (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 6/6: ค้นหารายการบริการที่กำลังทำงานบนเครื่องเพื่อการสำรวจระบบ...
[RETRIEVE] Query: ค้นหารายการบริการที่กำลังทำงานบนเครื่องเพื่อการสำรวจระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Tasklist (0.523), Turla (0.448), Tasklist (0.255), System Service Discovery (0.187), Tasklist (0.084), VERMIN (0.055), Process Discovery (0.023), dsquery (0.010), Ping (0.002), netstat (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Tasklist (19 neighbors, 19 edges)
           → System Service Discovery (71 neighbors, 71 edges)
           → Turla (98 neighbors, 98 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → VERMIN (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [91/100] retrieved=320 relevant=3 latency=11489ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 3 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายได้...
[RETRIEVE] Query: เมื่อวันที่ 3 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT38 (0.513), APT28 (0.454), Password Spraying (0.288), CrackMapExec (0.233), APT3 (0.222), Brute Force (0.095), Password Cracking (0.042), Password Managers (0.003), Credentials from Web Browsers (0.002), Password Policy Discovery (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT38 (62 neighbors, 62 edges)
           → Brute Force (34 neighbors, 34 edges)
           → APT28 (124 neighbors, 124 edges)
           → Password Spraying (23 neighbors, 23 edges)
           → CrackMapExec (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] Query 2/7: Brute Force: Password Cracking ถอดรหัสแฮชรหัสผ่านนอกระบบ...
[RETRIEVE] Query: Brute Force: Password Cracking ถอดรหัสแฮชรหัสผ่านนอกระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT3 (0.538), APT38 (0.329), Brute Force (0.258), Password Cracking (0.158), Pass-The-Hash Toolkit (0.050), Password Policy Discovery (0.042), Password Guessing (0.030), Password Policies (0.029), Compute Hijacking (0.004), Password Managers (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT3 (50 neighbors, 50 edges)
           → Password Cracking (12 neighbors, 12 edges)
           → APT38 (62 neighbors, 62 edges)
           → Brute Force (34 neighbors, 34 edges)
           → Password Policy Discovery (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 3/7: Brute Force: Password Spraying ลองรหัสผ่านง่ายกับบัญชีจำนวนมาก...
[RETRIEVE] Query: Brute Force: Password Spraying ลองรหัสผ่านง่ายกับบัญชีจำนวนมาก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Password Spraying (0.973), APT28 (0.548), Account Use Policies (0.156), Brute Force (0.132), Multi-factor Authentication (0.064), CrackMapExec (0.061), Password Guessing (0.010), Password Policy Discovery (0.009), Password Cracking (0.002), Password Policies (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Password Spraying (23 neighbors, 23 edges)
           → APT28 (124 neighbors, 124 edges)
           → Brute Force (34 neighbors, 34 edges)
           → Account Use Policies (11 neighbors, 11 edges)
           → Multi-factor Authentication (48 neighbors, 48 edges)
[RETRIEVE-QUOTA] Query 4/7: Credentials from Web Browsers อ่านชื่อผู้ใช้และรหัสผ่านจากโปรแกรมท่องเว็บ...
[RETRIEVE] Query: Credentials from Web Browsers อ่านชื่อผู้ใช้และรหัสผ่านจากโปรแกรมท่องเว็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.972), TrickBot (0.808), LaZagne (0.658), XLoader (0.551), Web Credential Usage (0.033), Windows Credential Manager (0.022), Forge Web Credentials (0.020), Credentials from Password Stores (0.017), Browser Information Discovery (0.009), Browser Fingerprint (0.005)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → TrickBot (57 neighbors, 57 edges)
           → LaZagne (22 neighbors, 22 edges)
           → XLoader (28 neighbors, 28 edges)
           → Web Credential Usage (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 5/7: Bypass User Account Control หลบเลี่ยงกลไกยืนยันก่อนยกระดับสิทธิ์...
[RETRIEVE] Query: Bypass User Account Control หลบเลี่ยงกลไกยืนยันก่อนยกระดับสิทธิ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bypass User Account Control (0.959), RCSession (0.852), User Account Control (0.797), BlackCat (0.778), User Account Control (0.591), Abuse Elevation Control Mechanism (0.510), LockBit 2.0 (0.466), UACMe (0.248), GUI Input Capture (0.067), User Account Management (0.020)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Bypass User Account Control (70 neighbors, 70 edges)
           → RCSession (24 neighbors, 24 edges)
           → User Account Control (7 neighbors, 7 edges)
           → BlackCat (22 neighbors, 22 edges)
           → Abuse Elevation Control Mechanism (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 6/7: ยกระดับสิทธิ์เป็นผู้ดูแลระบบโดยไม่มีหน้าต่างขออนุญาต...
[RETRIEVE] Query: ยกระดับสิทธิ์เป็นผู้ดูแลระบบโดยไม่มีหน้าต่างขออนุญาต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Raspberry Robin (0.264), Elevated Execution with Prompt (0.164), Bypass User Account Control (0.059), User Account Control (0.022), InvisiMole (0.015), Cardinal RAT (0.000), Cobian RAT (0.000), CrossRAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Raspberry Robin (41 neighbors, 41 edges)
           → Bypass User Account Control (70 neighbors, 70 edges)
           → Elevated Execution with Prompt (5 neighbors, 5 edges)
           → User Account Control (7 neighbors, 7 edges)
           → InvisiMole (73 neighbors, 73 edges)
[RETRIEVE-QUOTA] Query 7/7: ส่งข้อมูลออกไปทางโพรโทคอลรับส่งไฟล์ที่ไม่เข้ารหัสลับ...
[RETRIEVE] Query: ส่งข้อมูลออกไปทางโพรโทคอลรับส่งไฟล์ที่ไม่เข้ารหัสลับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CharmPower (0.894), BusyGasper (0.854), Exfiltration Over Unencrypted Non-C2 Protocol (0.820), FIN6 (0.688), WARPWIRE (0.680), Exfiltration Over Alternative Protocol (0.403), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.388), File Transfer Protocols (0.055), Non-Application Layer Protocol (0.006), Non-Standard Port (0.005)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
           → CharmPower (25 neighbors, 25 edges)
           → BusyGasper (18 neighbors, 18 edges)
           → Exfiltration Over Unencrypted Non-C2 Protocol (5 neighbors, 5 edges)
           → FIN6 (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [92/100] retrieved=215 relevant=4 latency=12906ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 18 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความเพิ่มเติมถึงข้อมู...
[RETRIEVE] Query: เมื่อวันที่ 18 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความเพิ่มเติมถึงข้อมู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.144), MuddyWater (0.115), njRAT (0.080), Lokibot (0.004), Unsecured Credentials (0.003), FIN8 (0.000), Gamaredon Group (0.000), Named Pipe Metadata (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → MuddyWater (89 neighbors, 89 edges)
           → Credentials In Files (44 neighbors, 44 edges)
           → njRAT (40 neighbors, 40 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
[RETRIEVE-QUOTA] Query 2/6: โปรแกรมดึงชื่อผู้ใช้และรหัสผ่านจากเบราว์เซอร์ที่บันทึกไว้ในเครื่อง...
[RETRIEVE] Query: โปรแกรมดึงชื่อผู้ใช้และรหัสผ่านจากเบราว์เซอร์ที่บันทึกไว้ในเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TrickBot (0.733), Backdoor.Oldrea (0.481), Credentials from Web Browsers (0.342), LaZagne (0.208), Cachedump (0.144), gsecdump (0.121), CrossRAT (0.008), Cardinal RAT (0.004), Visual Basic (0.003), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → TrickBot (57 neighbors, 57 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → Backdoor.Oldrea (17 neighbors, 17 edges)
           → LaZagne (22 neighbors, 22 edges)
           → Cachedump (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] Query 3/6: สคริปต์ขโมยสิทธิ์ประจำตัวจากกระบวนการผู้ใช้อื่นที่เปิดค้างอยู่...
[RETRIEVE] Query: สคริปต์ขโมยสิทธิ์ประจำตัวจากกระบวนการผู้ใช้อื่นที่เปิดค้างอยู่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.557), SILENTTRINITY (0.238), Token Impersonation/Theft (0.041), ROKRAT (0.037), Access Token Manipulation (0.025), Create Process with Token (0.018), Exploitation for Credential Access (0.007), APT37 (0.004), RDFSNIFFER (0.003), GUI Input Capture (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Token Impersonation/Theft (26 neighbors, 26 edges)
           → ROKRAT (31 neighbors, 31 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
[RETRIEVE-QUOTA] Query 4/6: สวมสิทธิ์ของผู้ใช้อื่นเพื่อสั่งงาน (Token Impersonation)...
[RETRIEVE] Query: สวมสิทธิ์ของผู้ใช้อื่นเพื่อสั่งงาน (Token Impersonation)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Token Impersonation/Theft (0.913), BitPaymer (0.714), SILENTTRINITY (0.667), Shamoon (0.630), Make and Impersonate Token (0.501), Create Process with Token (0.488), Access Token Manipulation (0.487), Havoc (0.326), Protocol or Service Impersonation (0.037), Impersonation (0.034)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Token Impersonation/Theft (26 neighbors, 26 edges)
           → BitPaymer (19 neighbors, 19 edges)
           → SILENTTRINITY (53 neighbors, 53 edges)
           → Shamoon (24 neighbors, 24 edges)
           → Make and Impersonate Token (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 5/6: สคริปต์ค้นหาไฟล์กุญแจส่วนตัวที่ไม่มีรหัสผ่านป้องกัน...
[RETRIEVE] Query: สคริปต์ค้นหาไฟล์กุญแจส่วนตัวที่ไม่มีรหัสผ่านป้องกัน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: InvisibleFerret (0.277), Private Keys (0.157), Unsecured Credentials (0.098), PoshC2 (0.085), Empire (0.062), Credentials In Files (0.050), TruffleHog (0.027), Pacu (0.018), Group Policy Preferences (0.006), Credentials in Registry (0.002)
[RETRIEVE] Graph expansion: 6 subgraphs
           → InvisibleFerret (36 neighbors, 36 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Private Keys (26 neighbors, 26 edges)
           → Unsecured Credentials (27 neighbors, 27 edges)
           → PoshC2 (35 neighbors, 35 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] Query 6/6: คัดลอกไฟล์กุญแจส่วนตัวออกจากเครื่อง...
[RETRIEVE] Query: คัดลอกไฟล์กุญแจส่วนตัวออกจากเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mimikatz (0.053), PACEMAKER (0.049), Cachedump (0.035), Private Keys (0.004), Security Account Manager (0.004), CrossRAT (0.001), Windows Registry Key Deletion (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Mimikatz (77 neighbors, 77 edges)
           → Private Keys (26 neighbors, 26 edges)
           → PACEMAKER (7 neighbors, 7 edges)
           → Proc Filesystem (8 neighbors, 8 edges)
           → Cachedump (2 neighbors, 2 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [93/100] retrieved=240 relevant=3 latency=11865ms
[RETRIEVE-QUOTA] Query 1/9: เมื่อวันที่ 14 ตุลาคม 2564 การประปาส่วนภูมิภาคสาขาหนึ่งแจ้งความว่าระบบควบคุมการผ...
[RETRIEVE] Query: เมื่อวันที่ 14 ตุลาคม 2564 การประปาส่วนภูมิภาคสาขาหนึ่งแจ้งความว่าระบบควบคุมการผ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MuddyWater (0.002), SMS Pumping (0.000), CharmPower (0.000), ccf32 (0.000), BendyBear (0.000), Fysbis (0.000), Samurai (0.000), Supply Chain Compromise (0.000), Data Encoding (0.000), Standard Encoding (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → MuddyWater (89 neighbors, 89 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → SMS Pumping (4 neighbors, 4 edges)
           → CharmPower (25 neighbors, 25 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] Query 2/9: จดหมายอิเล็กทรอนิกส์หลอกลวงพร้อมไฟล์แนบมัลแวร์ส่งถึงเจ้าหน้าที่...
[RETRIEVE] Query: จดหมายอิเล็กทรอนิกส์หลอกลวงพร้อมไฟล์แนบมัลแวร์ส่งถึงเจ้าหน้าที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BLINDINGCAN (0.879), Molerats (0.609), Spearphishing Attachment (0.546), Rover (0.048), CALENDAR (0.001), Cobian RAT (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BLINDINGCAN (23 neighbors, 23 edges)
           → Spearphishing Attachment (158 neighbors, 158 edges)
           → Molerats (22 neighbors, 22 edges)
           → Rover (10 neighbors, 10 edges)
           → CALENDAR (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] Query 3/9: ติดตั้งโปรแกรมอันตรายและโปรแกรมเรียกค่าไถ่จากไฟล์แนบ...
[RETRIEVE] Query: ติดตั้งโปรแกรมอันตรายและโปรแกรมเรียกค่าไถ่จากไฟล์แนบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pony (0.348), CLAIMLOADER (0.063), EvilGrab (0.034), BadPatch (0.010), Hancitor (0.006), Cobian RAT (0.000), Visual Basic (0.000), CrossRAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Pony (16 neighbors, 16 edges)
           → Malicious File (202 neighbors, 202 edges)
           → CLAIMLOADER (12 neighbors, 12 edges)
           → EvilGrab (6 neighbors, 6 edges)
           → BadPatch (12 neighbors, 12 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] Query 4/9: ใช้ประโยชน์จากช่องโหว่ของบริการและแอปพลิเคชันที่เปิดให้เข้าถึงจากอินเทอร์เน็ต...
[RETRIEVE] Query: ใช้ประโยชน์จากช่องโหว่ของบริการและแอปพลิเคชันที่เปิดให้เข้าถึงจากอินเทอร์เน็ต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.308), Exploitation of Remote Services (0.023), Exploitation for Client Execution (0.008), Web Services (0.004), XTunnel (0.003), Web Service (0.002), P.A.S. Webshell (0.000), Vulnerability Scanning (0.000), Search Open Technical Databases (0.000), Query Public AI Services (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → Exploitation of Remote Services (34 neighbors, 34 edges)
           → Exploitation for Client Execution (65 neighbors, 65 edges)
           → Web Services (9 neighbors, 9 edges)
           → XTunnel (9 neighbors, 9 edges)
           → Network Service Discovery (78 neighbors, 78 edges)
[RETRIEVE-QUOTA] Query 5/9: เข้าถึงเครือข่ายของหน่วยงานจากระยะไกล...
[RETRIEVE] Query: เข้าถึงเครือข่ายของหน่วยงานจากระยะไกล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: External Remote Services (0.590), Limit Access to Resource Over Network (0.065), Cobian RAT (0.038), Net (0.012), Net (0.009), Windows Remote Management (0.004), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → External Remote Services (52 neighbors, 52 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Cobian RAT (8 neighbors, 8 edges)
           → Net (50 neighbors, 50 edges)
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
[RETRIEVE-QUOTA] Query 6/9: ขยายการเข้าถึงไปยังเครื่องอื่นในเครือข่ายควบคุม...
[RETRIEVE] Query: ขยายการเข้าถึงไปยังเครื่องอื่นในเครือข่ายควบคุม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Other Network Medium (0.093), Limit Access to Resource Over Network (0.033), Network Device CLI (0.018), Limit Access to Resource Over Network (0.015), Additional Local or Domain Groups (0.008), IPsec Helper (0.002), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Hardware Additions (5 neighbors, 5 edges)
           → Network Device CLI (11 neighbors, 11 edges)
           → Additional Local or Domain Groups (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] Query 7/9: เข้าถึงอุปกรณ์ควบคุมการผลิตน้ำประปา...
[RETRIEVE] Query: เข้าถึงอุปกรณ์ควบคุมการผลิตน้ำประปา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Cobian RAT (0.001), Out1 (0.001), UBoatRAT (0.001), CrossRAT (0.000), HyperStack (0.000), CharmPower (0.000), Socket Filters (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Cobian RAT (8 neighbors, 8 edges)
           → Out1 (6 neighbors, 6 edges)
           → UBoatRAT (8 neighbors, 8 edges)
           → CrossRAT (6 neighbors, 6 edges)
           → HyperStack (7 neighbors, 7 edges)
           → Modify Registry (177 neighbors, 177 edges)
[RETRIEVE-QUOTA] Query 8/9: หยุดให้บริการระบบควบคุมการผลิต...
[RETRIEVE] Query: หยุดให้บริการระบบควบคุมการผลิต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BRICKSTORM (0.060), MegaCortex (0.005), Industroyer2 (0.000), PITSTOP (0.000), Limit Hardware Installation (0.000), CrossRAT (0.000), Visual Basic (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BRICKSTORM (25 neighbors, 25 edges)
           → Service Stop (61 neighbors, 61 edges)
           → MegaCortex (16 neighbors, 16 edges)
           → Industroyer2 (2 neighbors, 2 edges)
           → PITSTOP (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] Query 9/9: รั่วไหลข้อมูลอ่อนไหวของหน่วยงาน...
[RETRIEVE] Query: รั่วไหลข้อมูลอ่อนไหวของหน่วยงาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Clambling (0.012), FLASHFLOOD (0.007), FoggyWeb (0.004), LAPSUS$ (0.004), Volt Typhoon (0.003), Ramsay (0.002), POWERSOURCE (0.001), FoggyWeb (0.001), Lokibot (0.000), Business Relationships (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Clambling (35 neighbors, 35 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → FLASHFLOOD (7 neighbors, 7 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
           → FoggyWeb (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 9 queries
  [94/100] retrieved=707 relevant=2 latency=15766ms
[RETRIEVE-QUOTA] Query 1/5: เมื่อวันที่ 20 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนสุ...
[RETRIEVE] Query: เมื่อวันที่ 20 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนสุ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.070), admin@338 (0.008), APT-C-36 (0.007), File Deletion (0.004), Wingbird (0.004), Ursnif (0.002), Ingress Tool Transfer (0.001), System Script Proxy Execution (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → admin@338 (19 neighbors, 19 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → AsyncRAT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] Query 2/5: โปรแกรมฝังตัวเปิดอ่านไฟล์บันทึกผลการติดตั้งผ่านหน้าต่างคำสั่งวินโดวส์...
[RETRIEVE] Query: โปรแกรมฝังตัวเปิดอ่านไฟล์บันทึกผลการติดตั้งผ่านหน้าต่างคำสั่งวินโดวส์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Nightdoor (0.110), OilBooster (0.108), Forfiles (0.055), Koadic (0.043), cmd (0.014), Cardinal RAT (0.012), CrossRAT (0.009), Visual Basic (0.002), Change Default File Association (0.001), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Nightdoor (15 neighbors, 15 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → OilBooster (16 neighbors, 16 edges)
           → Inter-Process Communication (28 neighbors, 28 edges)
           → Forfiles (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] Query 3/5: ลบไฟล์และร่องรอยที่ทิ้งไว้บนเครื่องเป้าหมาย (artifact removal)...
[RETRIEVE] Query: ลบไฟล์และร่องรอยที่ทิ้งไว้บนเครื่องเป้าหมาย (artifact removal)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FALLCHILL (0.481), Cuba (0.425), NICECURL (0.374), Indicator Removal (0.311), Clear Persistence (0.165), File Deletion (0.102), Delete Cloud Instance (0.045), UNC3886 (0.028), Clear Network Connection History and Configurations (0.024), Hide Artifacts (0.013)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FALLCHILL (10 neighbors, 10 edges)
           → File Deletion (310 neighbors, 310 edges)
           → Cuba (23 neighbors, 23 edges)
           → NICECURL (6 neighbors, 6 edges)
           → Indicator Removal (45 neighbors, 45 edges)
[RETRIEVE-QUOTA] Query 4/5: เรียกดูรายละเอียดการตั้งค่าเครือข่ายของเครื่องแม่ข่าย (network configuration dis...
[RETRIEVE] Query: เรียกดูรายละเอียดการตั้งค่าเครือข่ายของเครื่องแม่ข่าย (network configuration dis...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: System Network Configuration Discovery (0.728), ifconfig (0.667), route (0.631), Turla (0.540), Ke3chang (0.457), Network Device Configuration Dump (0.223), ipconfig (0.043), System Network Connections Discovery (0.017), Backup Software Discovery (0.002), System Time Discovery (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → ifconfig (1 neighbors, 1 edges)
           → route (3 neighbors, 3 edges)
           → Turla (98 neighbors, 98 edges)
           → Ke3chang (58 neighbors, 58 edges)
[RETRIEVE-QUOTA] Query 5/5: ส่งไฟล์บันทึกจดหมายอิเล็กทรอนิกส์ออกไปยังคนร้าย (email exfiltration)...
[RETRIEVE] Query: ส่งไฟล์บันทึกจดหมายอิเล็กทรอนิกส์ออกไปยังคนร้าย (email exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exfiltration Over Alternative Protocol (0.035), OilCheck (0.035), TianySpy (0.024), Exfiltration Over Other Network Medium (0.020), Exfiltration (0.014), Exfiltration Over Physical Medium (0.010), Exbyte (0.004), Email Bombing (0.003), Manjusaka (0.002), Empire (0.001)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → OilCheck (4 neighbors, 4 edges)
           → Exfiltration Over Web Service (23 neighbors, 23 edges)
           → Exfiltration Over Other Network Medium (5 neighbors, 5 edges)
           → TianySpy (9 neighbors, 9 edges)
           → Exfiltration Over Alternative Protocol (3 neighbors, 3 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 5 queries
  [95/100] retrieved=628 relevant=4 latency=10470ms
[RETRIEVE-QUOTA] Query 1/6: เมื่อวันที่ 25 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งแจ้งความเพิ่มเติมถึงพฤติกร...
[RETRIEVE] Query: เมื่อวันที่ 25 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งแจ้งความเพิ่มเติมถึงพฤติกร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT18 (0.135), Obfuscated Files or Information (0.009), Adversary-in-the-Middle (0.004), Masquerade File Type (0.003), ARP Cache Poisoning (0.002), Evil Twin (0.001), Magic Hound (0.001), Threat Group-3390 (0.000), Right-to-Left Override (0.000), BackConfig (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT18 (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Adversary-in-the-Middle (23 neighbors, 23 edges)
           → Masquerade File Type (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 2/6: ไฟล์อันตรายที่มีข้อความเข้ารหัสฐานสิบหกและสลับตำแหน่ง (obfuscation)...
[RETRIEVE] Query: ไฟล์อันตรายที่มีข้อความเข้ารหัสฐานสิบหกและสลับตำแหน่ง (obfuscation)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Final1stspy (0.514), Encrypted/Encoded File (0.113), Obfuscated Files or Information (0.073), Machete (0.053), Clambling (0.048), Deobfuscate/Decode Files or Information (0.024), Command Obfuscation (0.012), Masquerade File Type (0.006), NOKKI (0.004), Polymorphic Code (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Final1stspy (7 neighbors, 7 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Machete (42 neighbors, 42 edges)
           → Command Obfuscation (74 neighbors, 74 edges)
[RETRIEVE-QUOTA] Query 3/6: เก็บรวบรวมข้อมูลเครื่องรวมถึงหมายเลขไอพี ชื่อเครื่อง และชื่อบัญชีผู้ใช้...
[RETRIEVE] Query: เก็บรวบรวมข้อมูลเครื่องรวมถึงหมายเลขไอพี ชื่อเครื่อง และชื่อบัญชีผู้ใช้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LightSpy (0.633), DCHSpy (0.289), ifconfig (0.264), User Account Metadata (0.100), ipconfig (0.041), spwebmember (0.012), CrossRAT (0.001), Visual Basic (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → LightSpy (52 neighbors, 52 edges)
           → System Network Configuration Discovery (52 neighbors, 52 edges)
           → DCHSpy (13 neighbors, 13 edges)
           → Accounts (8 neighbors, 8 edges)
           → ifconfig (1 neighbors, 1 edges)
[RETRIEVE-QUOTA] Query 4/6: แปลงข้อมูลที่เก็บรวบรวมเป็นค่าฐานสิบหก...
[RETRIEVE] Query: แปลงข้อมูลที่เก็บรวบรวมเป็นค่าฐานสิบหก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN6 (0.076), Local Data Staging (0.002), Data Staged (0.002), BusyGasper (0.001), Visual Basic (0.000), SHARPSTATS (0.000), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → FIN6 (52 neighbors, 52 edges)
           → Archive via Custom Method (42 neighbors, 42 edges)
           → Local Data Staging (138 neighbors, 138 edges)
           → Data Staged (13 neighbors, 13 edges)
           → BusyGasper (18 neighbors, 18 edges)
           → Keylogging (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 5/6: ส่งข้อมูลออกไปยังหมายเลขไอพีของคนร้ายผ่านโพรโทคอลเว็บ (HTTP POST exfiltration)...
[RETRIEVE] Query: ส่งข้อมูลออกไปยังหมายเลขไอพีของคนร้ายผ่านโพรโทคอลเว็บ (HTTP POST exfiltration)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BlackByte (0.369), Exfiltration Over Alternative Protocol (0.236), CharmPower (0.183), Shai-Hulud (0.073), Exfiltration to Code Repository (0.024), Exfiltration Over Other Network Medium (0.019), Exfiltration (0.019), Exfiltration Over Web Service (0.019), Exfiltration Over Physical Medium (0.007), Salesforce Data Exfiltration (0.003)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BlackByte (56 neighbors, 56 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Exfiltration Over Alternative Protocol (20 neighbors, 20 edges)
           → CharmPower (25 neighbors, 25 edges)
           → Shai-Hulud (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 6/6: ติดต่อรับคำสั่งจากเซิร์ฟเวอร์ควบคุมผ่านโพรโทคอลเว็บ (Command and Control)...
[RETRIEVE] Query: ติดต่อรับคำสั่งจากเซิร์ฟเวอร์ควบคุมผ่านโพรโทคอลเว็บ (Command and Control)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gustuff (0.748), Exodus (0.494), Command and Control (0.085), POWRUNER (0.038), Web Protocols (0.037), Service Execution (0.001), Bypass User Account Control (0.000), Anubis (0.000), User Account Control (0.000), WolfRAT (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Gustuff (15 neighbors, 15 edges)
           → Web Protocols (52 neighbors, 52 edges)
           → Exodus (19 neighbors, 19 edges)
           → Command and Control (45 neighbors, 45 edges)
           → Web Protocols (424 neighbors, 424 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 6 queries
  [96/100] retrieved=678 relevant=3 latency=12791ms
[RETRIEVE-QUOTA] Query 1/11: เมื่อวันที่ 25 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดการเ...
[RETRIEVE] Query: เมื่อวันที่ 25 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดการเ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA505 (0.040), Daggerfly (0.018), zwShell (0.011), ZxShell (0.011), Netwalker (0.002), RDP Hijacking (0.001), Remote Desktop Protocol (0.001), POWERSOURCE (0.000), Forced Authentication (0.000), PowerShell (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → TA505 (50 neighbors, 50 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Daggerfly (23 neighbors, 23 edges)
           → zwShell (12 neighbors, 12 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
[RETRIEVE-QUOTA] Query 2/11: PowerShell สคริปต์ติดต่อออกไปยังหมายเลขไอพีภายนอกผ่านโพรโทคอลเว็บ...
[RETRIEVE] Query: PowerShell สคริปต์ติดต่อออกไปยังหมายเลขไอพีภายนอกผ่านโพรโทคอลเว็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: POWRUNER (0.107), P.A.S. Webshell (0.082), POWERSOURCE (0.025), PowerShell Profile (0.008), P.A.S. Webshell (0.006), PowerShell (0.006), IPsec Helper (0.005), POWERSTATS (0.001), POWERSTATS (0.001), Disable or Remove Feature or Program (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → POWRUNER (21 neighbors, 21 edges)
           → P.A.S. Webshell (17 neighbors, 17 edges)
           → Web Protocols (424 neighbors, 424 edges)
           → POWERSOURCE (7 neighbors, 7 edges)
           → PowerShell Profile (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 3/11: ดึงสคริปต์ชุดถัดไปเข้ามาทำงานบนเครื่องผ่าน PowerShell...
[RETRIEVE] Query: ดึงสคริปต์ชุดถัดไปเข้ามาทำงานบนเครื่องผ่าน PowerShell...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PowerShell (0.060), CHIMNEYSWEEP (0.026), POWRUNER (0.020), AADInternals (0.008), PowerShower (0.008), Invoke-PSImage (0.008), PowerShell Profile (0.005), POWERSTATS (0.002), POWERSTATS (0.001), Disable or Remove Feature or Program (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PowerShell (241 neighbors, 241 edges)
           → CHIMNEYSWEEP (32 neighbors, 32 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → AADInternals (26 neighbors, 26 edges)
           → PowerShower (15 neighbors, 15 edges)
[RETRIEVE-QUOTA] Query 4/11: Remote Desktop Protocol เคลื่อนย้ายไปยังเครื่องแม่ข่ายเดสก์ท็อปเสมือน...
[RETRIEVE] Query: Remote Desktop Protocol เคลื่อนย้ายไปยังเครื่องแม่ข่ายเดสก์ท็อปเสมือน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VOID MANTICORE (0.230), RDP Hijacking (0.196), VNC (0.121), Koadic (0.089), Remote Desktop Protocol (0.053), Limit Access to Resource Over Network (0.042), Axiom (0.017), Remote Desktop Software (0.006), Terminal Services DLL (0.003), Remote Access Tools (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → VNC (18 neighbors, 18 edges)
           → Koadic (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 5/11: Remote Desktop Protocol เคลื่อนย้ายไปยังเครื่องแม่ข่ายบริหารจัดการความปลอดภัย...
[RETRIEVE] Query: Remote Desktop Protocol เคลื่อนย้ายไปยังเครื่องแม่ข่ายบริหารจัดการความปลอดภัย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT5 (0.449), RDP Hijacking (0.042), Limit Access to Resource Over Network (0.018), Koadic (0.015), Remote Desktop Protocol (0.010), VNC (0.009), Axiom (0.007), Terminal Services DLL (0.003), Remote Access Tools (0.002), Remote Services (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → APT5 (43 neighbors, 43 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Limit Access to Resource Over Network (19 neighbors, 19 edges)
           → Koadic (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] Query 6/11: Remote Desktop Protocol เคลื่อนย้ายไปยังเครื่องออกใบรับรอง...
[RETRIEVE] Query: Remote Desktop Protocol เคลื่อนย้ายไปยังเครื่องออกใบรับรอง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RDP Hijacking (0.092), Remote Desktop Protocol (0.048), Koadic (0.033), VNC (0.022), Limit Access to Resource Over Network (0.003), Axiom (0.003), Remote Desktop Software (0.003), Terminal Services DLL (0.002), Remote Access Tools (0.000), Remote Services (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RDP Hijacking (12 neighbors, 12 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Koadic (31 neighbors, 31 edges)
           → VNC (18 neighbors, 18 edges)
           → Remote Desktop Software (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 7/11: Remote Desktop Protocol เคลื่อนย้ายไปยังฐานข้อมูลที่เก็บข้อมูลการสืบสวนคดี...
[RETRIEVE] Query: Remote Desktop Protocol เคลื่อนย้ายไปยังฐานข้อมูลที่เก็บข้อมูลการสืบสวนคดี...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Remote Data Storage (0.168), FIN7 (0.079), menuPass (0.065), RDP Hijacking (0.014), Axiom (0.005), Remote Desktop Protocol (0.003), Koadic (0.002), VNC (0.001), Terminal Services DLL (0.000), File Transfer Protocols (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Remote Data Storage (11 neighbors, 11 edges)
           → FIN7 (86 neighbors, 86 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → menuPass (71 neighbors, 71 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 8/11: Remote Desktop Protocol เคลื่อนย้ายไปยังเครื่องส่งต่อจดหมายอิเล็กทรอนิกส์...
[RETRIEVE] Query: Remote Desktop Protocol เคลื่อนย้ายไปยังเครื่องส่งต่อจดหมายอิเล็กทรอนิกส์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dragonfly (0.091), Mail Protocols (0.038), Koadic (0.032), RDP Hijacking (0.022), Remote Desktop Protocol (0.007), Axiom (0.007), APT28 Nearest Neighbor Campaign (0.004), Terminal Services DLL (0.002), VNC (0.002), Remote Access Tools (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Dragonfly (66 neighbors, 66 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Mail Protocols (31 neighbors, 31 edges)
           → Koadic (31 neighbors, 31 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 9/11: สร้างไฟล์บีตอัดข้อมูลการสืบสวนคดีอ่อนไหวภายใต้บัญชีผู้ดูแลระบบ...
[RETRIEVE] Query: สร้างไฟล์บีตอัดข้อมูลการสืบสวนคดีอ่อนไหวภายใต้บัญชีผู้ดูแลระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BITSAdmin (0.002), BITSAdmin (0.001), Security Account Manager (0.000), BBSRAT (0.000), Expand (0.000), Expand (0.000), BackConfig (0.000), Wordlist Scanning (0.000), AADInternals (0.000), Process Argument Spoofing (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → BITSAdmin (13 neighbors, 13 edges)
           → Exfiltration Over Unencrypted Non-C2 Protocol (42 neighbors, 42 edges)
           → Security Account Manager (43 neighbors, 43 edges)
           → BBSRAT (14 neighbors, 14 edges)
           → Deobfuscate/Decode Files or Information (351 neighbors, 351 edges)
[RETRIEVE-QUOTA] Query 10/11: ดาวน์โหลดไฟล์อันตรายจากหมายเลขไอพีภายนอกเข้ามาสั่งให้ทำงานบนเครื่อง...
[RETRIEVE] Query: ดาวน์โหลดไฟล์อันตรายจากหมายเลขไอพีภายนอกเข้ามาสั่งให้ทำงานบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OopsIE (0.028), LNK Icon Smuggling (0.015), Conficker (0.009), Kerrdown (0.009), IMAPLoader (0.007), ccf32 (0.001), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → OopsIE (20 neighbors, 20 edges)
           → LNK Icon Smuggling (8 neighbors, 8 edges)
           → Conficker (13 neighbors, 13 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Kerrdown (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] Query 11/11: การติดต่อขาเข้าและขาออกของไฟล์ถูกแปลงด้วยกุญแจลับ (encryption)...
[RETRIEVE] Query: การติดต่อขาเข้าและขาออกของไฟล์ถูกแปลงด้วยกุญแจลับ (encryption)...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Private Keys (0.057), Encrypted/Encoded File (0.056), Weaken Encryption (0.044), Encrypt Sensitive Information (0.044), HenBox (0.035), Encrypt Sensitive Information (0.029), HeartCrypt (0.027), cipher.exe (0.013), Exfiltration Over Asymmetric Encrypted Non-C2 Protocol (0.005), Desert Scorpion (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Private Keys (26 neighbors, 26 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Weaken Encryption (3 neighbors, 3 edges)
           → Encrypt Sensitive Information (33 neighbors, 33 edges)
           → HenBox (17 neighbors, 17 edges)
           → Obfuscated Files or Information (51 neighbors, 51 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 11 queries
  [97/100] retrieved=642 relevant=6 latency=19793ms
[RETRIEVE-QUOTA] Query 1/7: เมื่อวันที่ 22 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าโปรแกรมเรียก...
[RETRIEVE] Query: เมื่อวันที่ 22 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าโปรแกรมเรียก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NotPetya (0.008), Wizard Spider (0.000), FIN8 (0.000), Exploitation of Remote Services (0.000), Pikabot (0.000), Hijack Execution Flow (0.000), Exfiltration to Text Storage Sites (0.000), Filter Network Traffic (0.000), Process Discovery (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → NotPetya (15 neighbors, 15 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Wizard Spider (86 neighbors, 86 edges)
           → Windows Remote Management (16 neighbors, 16 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/7: Windows Management Instrumentation (WMI) ใช้กระจายโปรแกรมเรียกค่าไถ่ไปยังเครื่อง...
[RETRIEVE] Query: Windows Management Instrumentation (WMI) ใช้กระจายโปรแกรมเรียกค่าไถ่ไปยังเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.784), Windows Management Instrumentation (0.323), POWRUNER (0.214), EKANS (0.180), Windows Management Instrumentation Event Subscription (0.175), Koadic (0.134), WMI Creation (0.003), Windows Remote Management (0.001), Extra Window Memory Injection (0.001), Scheduled Task (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Windows Management Instrumentation Event Subscription (33 neighbors, 33 edges)
           → EKANS (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 3/7: Command line execution สั่งคำสั่งคัดลอกไฟล์โปรแกรมเรียกค่าไถ่และสคริปต์...
[RETRIEVE] Query: Command line execution สั่งคำสั่งคัดลอกไฟล์โปรแกรมเรียกค่าไถ่และสคริปต์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: cmd (0.108), Command Obfuscation (0.091), Command and Scripting Interpreter (0.050), Indirect Command Execution (0.045), LookBack (0.015), Felismus (0.010), Akira (0.008), Windows Command Shell (0.007), Execution (0.002), BackConfig (0.002)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Command Obfuscation (74 neighbors, 74 edges)
           → cmd (13 neighbors, 13 edges)
           → Command and Scripting Interpreter (68 neighbors, 68 edges)
           → Indirect Command Execution (5 neighbors, 5 edges)
           → LookBack (16 neighbors, 16 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
[RETRIEVE-QUOTA] Query 4/7: ใช้ช่องแบ่งปันไฟล์ (file share) สำหรับผู้ดูแลระบบเก็บไฟล์โปรแกรมเรียกค่าไถ่บนเคร...
[RETRIEVE] Query: ใช้ช่องแบ่งปันไฟล์ (file share) สำหรับผู้ดูแลระบบเก็บไฟล์โปรแกรมเรียกค่าไถ่บนเคร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: SMB/Windows Admin Shares (0.009), Shared Modules (0.007), Network Share Discovery (0.003), PsExec (0.003), Taint Shared Content (0.003), Net (0.001), Forfiles (0.001), Network Share Access (0.000), Network Share Connection Removal (0.000), Forfiles (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → SMB/Windows Admin Shares (72 neighbors, 72 edges)
           → Shared Modules (25 neighbors, 25 edges)
           → Network Share Discovery (80 neighbors, 80 edges)
           → Taint Shared Content (18 neighbors, 18 edges)
           → PsExec (49 neighbors, 49 edges)
           → Lateral Tool Transfer (59 neighbors, 59 edges)
[RETRIEVE-QUOTA] Query 5/7: Windows Management Instrumentation (WMI) สั่งให้สคริปต์หยุดการทำงานของโปรแกรมอื่...
[RETRIEVE] Query: Windows Management Instrumentation (WMI) สั่งให้สคริปต์หยุดการทำงานของโปรแกรมอื่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Behavior Prevention on Endpoint (0.258), Windows Management Instrumentation (0.249), Windows Management Instrumentation Event Subscription (0.172), Koadic (0.169), EKANS (0.125), schtasks (0.012), WMI Creation (0.003), System Shutdown/Reboot (0.001), Scheduled Task (0.001), Windows Remote Management (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Behavior Prevention on Endpoint (51 neighbors, 51 edges)
           → Windows Management Instrumentation Event Subscription (33 neighbors, 33 edges)
           → Koadic (31 neighbors, 31 edges)
           → EKANS (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] Query 6/7: Windows Management Instrumentation (WMI) สั่งให้โปรแกรมเรียกค่าไถ่ทำงานบนเครื่อง...
[RETRIEVE] Query: Windows Management Instrumentation (WMI) สั่งให้โปรแกรมเรียกค่าไถ่ทำงานบนเครื่อง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Management Instrumentation (0.225), MoleNet (0.098), EKANS (0.096), Koadic (0.048), Windows Management Instrumentation Event Subscription (0.031), WMI Creation (0.001), At (0.001), Scheduled Task (0.001), Windows Remote Management (0.001), Extra Window Memory Injection (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → MoleNet (8 neighbors, 8 edges)
           → EKANS (9 neighbors, 9 edges)
           → Koadic (31 neighbors, 31 edges)
           → Windows Management Instrumentation Event Subscription (33 neighbors, 33 edges)
[RETRIEVE-QUOTA] Query 7/7: เครื่องมือสั่งงานเครื่องระยะไกล (remote command execution tool) สร้างบริการของระ...
[RETRIEVE] Query: เครื่องมือสั่งงานเครื่องระยะไกล (remote command execution tool) สร้างบริการของระ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: RemoteCMD (0.833), RemoteCMD (0.687), Winexe (0.294), RemoteCMD (0.187), Execution (0.167), RemoteUtilities (0.099), PsExec (0.093), Remote Access Tools (0.035), WhisperGate (0.006), Brute Ratel C4 (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → RemoteCMD (4 neighbors, 4 edges)
           → Service Execution (78 neighbors, 78 edges)
           → Winexe (4 neighbors, 4 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Execution (64 neighbors, 64 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 7 queries
  [98/100] retrieved=322 relevant=3 latency=15115ms
[RETRIEVE-QUOTA] Query 1/8: เมื่อวันที่ 22 กันยายน 2563 ผู้เสียหายหลายรายแจ้งความว่าบัญชีผู้ใช้งานออนไลน์ของ...
[RETRIEVE] Query: เมื่อวันที่ 22 กันยายน 2563 ผู้เสียหายหลายรายแจ้งความว่าบัญชีผู้ใช้งานออนไลน์ของ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Crimson (0.259), njRAT (0.200), LAPSUS$ (0.072), Malicious File (0.069), User Execution (0.046), Execution Prevention (0.013), Lokibot (0.009), Malicious Link (0.003), Exploitation for Client Execution (0.000), Compromise Accounts (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Crimson (32 neighbors, 32 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → njRAT (40 neighbors, 40 edges)
           → Malicious File (202 neighbors, 202 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
           → User Execution (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 2/8: โปรแกรมขโมยรหัสผ่านกระจายผ่านอีเมล เว็บไซต์อันตราย ข้อความสั้น และข้อความส่วนตัว...
[RETRIEVE] Query: โปรแกรมขโมยรหัสผ่านกระจายผ่านอีเมล เว็บไซต์อันตราย ข้อความสั้น และข้อความส่วนตัว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QakBot (0.192), Lokibot (0.116), AADInternals (0.090), XLoader (0.070), 4H RAT (0.004), Cobian RAT (0.003), CrossRAT (0.001), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → QakBot (74 neighbors, 74 edges)
           → Spearphishing Link (93 neighbors, 93 edges)
           → Lokibot (29 neighbors, 29 edges)
           → AADInternals (26 neighbors, 26 edges)
           → Steal Application Access Token (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 3/8: User Execution: Malicious File เมื่อผู้เสียหายเปิดไฟล์ที่ได้รับ...
[RETRIEVE] Query: User Execution: Malicious File เมื่อผู้เสียหายเปิดไฟล์ที่ได้รับ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Kerrdown (0.938), Malicious File (0.930), User Execution (0.821), Execution Prevention (0.129), Malicious Link (0.064), Executable Installer File Permissions Weakness (0.055), Execution (0.047), Malicious Library (0.016), Exploitation for Client Execution (0.005), Double File Extension (0.002)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Malicious File (202 neighbors, 202 edges)
           → User Execution (18 neighbors, 18 edges)
           → Kerrdown (12 neighbors, 12 edges)
           → Execution Prevention (79 neighbors, 79 edges)
           → Malicious Link (93 neighbors, 93 edges)
[RETRIEVE-QUOTA] Query 4/8: Event Triggered Execution: Accessibility Features สร้างช่องทางลับในเครื่องที่ติด...
[RETRIEVE] Query: Event Triggered Execution: Accessibility Features สร้างช่องทางลับในเครื่องที่ติด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Event Triggered Execution (0.310), Accessibility Features (0.287), Execution Prevention (0.112), Privileged Account Management (0.062), Chameleon (0.010), Update Software (0.005), User Execution (0.003), Process Injection (0.002), Privilege Escalation (0.001), Path Interception by Unquoted Path (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Event Triggered Execution (28 neighbors, 28 edges)
           → Accessibility Features (15 neighbors, 15 edges)
           → Execution Prevention (79 neighbors, 79 edges)
           → Privileged Account Management (112 neighbors, 112 edges)
           → Chameleon (26 neighbors, 26 edges)
           → Abuse Accessibility Features (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 5/8: ดักบันทึกแป้นพิมพ์เพื่อขโมยข้อมูลรับรองตัวตน...
[RETRIEVE] Query: ดักบันทึกแป้นพิมพ์เพื่อขโมยข้อมูลรับรองตัวตน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.099), LP-Notes (0.054), Steal or Forge Authentication Certificates (0.036), gsecdump (0.033), Mimikatz (0.029), S.O.V.A. (0.018), Suckfly (0.006), Dtrack (0.005), DCSync (0.001), LP-Notes (0.001)
[RETRIEVE] Graph expansion: 5 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Steal or Forge Authentication Certificates (9 neighbors, 9 edges)
           → LP-Notes (12 neighbors, 12 edges)
           → gsecdump (8 neighbors, 8 edges)
           → Mimikatz (77 neighbors, 77 edges)
[RETRIEVE-QUOTA] Query 6/8: เฝ้าดูการใช้งานโปรแกรมท่องเว็บและหน้าจอเพื่อขโมยข้อมูลรับรองตัวตน...
[RETRIEVE] Query: เฝ้าดูการใช้งานโปรแกรมท่องเว็บและหน้าจอเพื่อขโมยข้อมูลรับรองตัวตน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chaes (0.151), NetTraveler (0.102), DRYHOOK (0.065), Mispadu (0.018), Cobian RAT (0.006), Browser Fingerprint (0.004), CrossRAT (0.001), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Chaes (28 neighbors, 28 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → NetTraveler (3 neighbors, 3 edges)
           → DRYHOOK (11 neighbors, 11 edges)
           → Mispadu (27 neighbors, 27 edges)
           → GUI Input Capture (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 7/8: Credentials from Password Stores อ่านชื่อผู้ใช้และรหัสผ่านจากโปรแกรมท่องเว็บ...
[RETRIEVE] Query: Credentials from Password Stores อ่านชื่อผู้ใช้และรหัสผ่านจากโปรแกรมท่องเว็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Credentials from Web Browsers (0.776), TrickBot (0.270), XLoader (0.248), KGH_SPY (0.177), Credentials from Password Stores (0.171), Credentials in Registry (0.071), Windows Credential Manager (0.043), Password Managers (0.040), Credentials In Files (0.019), Web Credential Usage (0.004)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → TrickBot (57 neighbors, 57 edges)
           → XLoader (28 neighbors, 28 edges)
           → Credentials from Password Stores (50 neighbors, 50 edges)
           → KGH_SPY (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] Query 8/8: สวมรอยบัญชีผู้ใช้งานออนไลน์ของผู้เสียหาย...
[RETRIEVE] Query: สวมรอยบัญชีผู้ใช้งานออนไลน์ของผู้เสียหาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: LAPSUS$ (0.509), Compromise Accounts (0.054), Social Media Accounts (0.027), APT37 (0.001), Establish Accounts (0.000), CrossRAT (0.000), Cobian RAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → LAPSUS$ (45 neighbors, 45 edges)
           → Impersonation (24 neighbors, 24 edges)
           → Compromise Accounts (5 neighbors, 5 edges)
           → Social Media Accounts (5 neighbors, 5 edges)
           → APT37 (42 neighbors, 42 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 8 queries
  [99/100] retrieved=383 relevant=3 latency=15445ms
[RETRIEVE-QUOTA] Query 1/11: เมื่อวันที่ 7 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าก่อนเกิดเหตุม...
[RETRIEVE] Query: เมื่อวันที่ 7 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าก่อนเกิดเหตุม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.014), POWRUNER (0.001), Domain Properties (0.000), FIN8 (0.000), Search Victim-Owned Websites (0.000), Domain Registration (0.000), Exfiltration to Text Storage Sites (0.000), Scan Databases (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Properties (5 neighbors, 5 edges)
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] Query 2/11: สำรวจข้อมูลทะเบียนโดเมนขององค์กรอย่างเป็นระบบ...
[RETRIEVE] Query: สำรวจข้อมูลทะเบียนโดเมนขององค์กรอย่างเป็นระบบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: AdFind (0.143), Domain Registration (0.066), Active DNS (0.052), Certificate Registration (0.018), Passive DNS (0.009), Empire (0.002), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → AdFind (19 neighbors, 19 edges)
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → Domain Registration (0 neighbors, 0 edges)
           → Active DNS (0 neighbors, 0 edges)
           → Certificate Registration (0 neighbors, 0 edges)
[RETRIEVE-QUOTA] Query 3/11: ใช้เครื่องมือสอบถามข้อมูลจากระบบทะเบียนโดเมนเพื่อไล่ค้นหารายการบัญชีบุคคลทั้งหมด...
[RETRIEVE] Query: ใช้เครื่องมือสอบถามข้อมูลจากระบบทะเบียนโดเมนเพื่อไล่ค้นหารายการบัญชีบุคคลทั้งหมด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.043), BoomBox (0.031), Domain Account (0.029), SoreFang (0.020), DUSTTRAP (0.012), Account Discovery (0.011), Domain Registration (0.008), Nltest (0.003), Active DNS (0.001), Domain Trust Discovery (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → CrackMapExec (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → BoomBox (17 neighbors, 17 edges)
           → SoreFang (15 neighbors, 15 edges)
           → Account Discovery (18 neighbors, 18 edges)
[RETRIEVE-QUOTA] Query 4/11: บันทึกรายการบัญชีผู้ใช้ลงเป็นไฟล์ข้อความ...
[RETRIEVE] Query: บันทึกรายการบัญชีผู้ใช้ลงเป็นไฟล์ข้อความ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PAKLOG (0.091), DocSwap (0.004), spwebmember (0.001), Local Email Collection (0.001), Visual Basic (0.001), User Account Metadata (0.001), CrossRAT (0.000), Cobian RAT (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → PAKLOG (11 neighbors, 11 edges)
           → Local Data Staging (138 neighbors, 138 edges)
           → DocSwap (27 neighbors, 27 edges)
           → Accounts (8 neighbors, 8 edges)
           → Local Email Collection (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] Query 5/11: ไล่ค้นหารายการเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนในโดเมน...
[RETRIEVE] Query: ไล่ค้นหารายการเครื่องคอมพิวเตอร์ทั้งหมดที่ลงทะเบียนในโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CrackMapExec (0.099), Domain Account (0.098), Nltest (0.094), SHOTPUT (0.090), Domain Registration (0.009), Active DNS (0.004), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Domain Account (65 neighbors, 65 edges)
           → CrackMapExec (26 neighbors, 26 edges)
           → SHOTPUT (7 neighbors, 7 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
           → Nltest (11 neighbors, 11 edges)
[RETRIEVE-QUOTA] Query 6/11: บันทึกรายการเครื่องคอมพิวเตอร์ลงไฟล์...
[RETRIEVE] Query: บันทึกรายการเครื่องคอมพิวเตอร์ลงไฟล์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Mafalda (0.117), AsyncRAT (0.034), cmd (0.008), Forfiles (0.005), spwebmember (0.004), Visual Basic (0.003), Cobian RAT (0.001), CrossRAT (0.001), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Mafalda (37 neighbors, 37 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → AsyncRAT (23 neighbors, 23 edges)
           → Video Capture (37 neighbors, 37 edges)
           → cmd (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] Query 7/11: แจกแจงรายการหน่วยจัดการภายในโดเมน...
[RETRIEVE] Query: แจกแจงรายการหน่วยจัดการภายในโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.059), Nltest (0.033), Sykipot (0.008), C0015 (0.004), BADHATCH (0.004), Group Metadata (0.003), Pod Enumeration (0.001), Domain Groups (0.001), Domain Account (0.001), Local Account (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Nltest (11 neighbors, 11 edges)
           → Sykipot (11 neighbors, 11 edges)
           → C0015 (39 neighbors, 39 edges)
           → Domain Groups (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] Query 8/11: ค้นหาความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนในโครงสร้างองค์กร...
[RETRIEVE] Query: ค้นหาความสัมพันธ์ความน่าเชื่อถือระหว่างโดเมนในโครงสร้างองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Magic Hound (0.498), BADHATCH (0.486), Chimera (0.399), MirrorFace (0.349), Domain Trust Discovery (0.135), Active DNS (0.007), Trusted Relationship (0.003), Domain Properties (0.001), Domain Registration (0.000), Search Open Technical Databases (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Magic Hound (91 neighbors, 91 edges)
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → BADHATCH (36 neighbors, 36 edges)
           → Chimera (65 neighbors, 65 edges)
           → MirrorFace (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] Query 9/11: บันทึกข้อมูลความสัมพันธ์โดเมนไว้...
[RETRIEVE] Query: บันทึกข้อมูลความสัมพันธ์โดเมนไว้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Passive DNS (0.141), Domain Registration (0.112), Domain Trust Discovery (0.072), Active DNS (0.020), PoshC2 (0.003), SILENTTRINITY (0.001), CrossRAT (0.000), Visual Basic (0.000), Cardinal RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 6 subgraphs
           → Passive DNS (0 neighbors, 0 edges)
           → Domain Registration (0 neighbors, 0 edges)
           → Domain Trust Discovery (37 neighbors, 37 edges)
           → Active DNS (0 neighbors, 0 edges)
           → PoshC2 (35 neighbors, 35 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] Query 10/11: เรียกดูรายการช่วงหมายเลขเครือข่ายย่อยที่องค์กรใช้งาน...
[RETRIEVE] Query: เรียกดูรายการช่วงหมายเลขเครือข่ายย่อยที่องค์กรใช้งาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Scanning IP Blocks (0.019), Ramsay (0.004), netstat (0.003), netstat (0.002), Local Account (0.000), CrossRAT (0.000), Cardinal RAT (0.000), Visual Basic (0.000), Cobian RAT (0.000), The White Company (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Scanning IP Blocks (6 neighbors, 6 edges)
           → Ramsay (39 neighbors, 39 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → netstat (16 neighbors, 16 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] Query 11/11: แจกแจงรายชื่อกลุ่มสิทธิ์ทั้งหมดในโดเมน...
[RETRIEVE] Query: แจกแจงรายชื่อกลุ่มสิทธิ์ทั้งหมดในโดเมน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Nltest (0.387), Domain Groups (0.157), Sykipot (0.154), C0015 (0.117), Domain Account (0.064), Group Metadata (0.047), CrossRAT (0.000), The White Company (0.000), Cardinal RAT (0.000), Visual Basic (0.000)
[RETRIEVE] Graph expansion: 5 subgraphs
           → Nltest (11 neighbors, 11 edges)
           → Domain Groups (41 neighbors, 41 edges)
           → Sykipot (11 neighbors, 11 edges)
           → Domain Account (65 neighbors, 65 edges)
           → C0015 (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] 15 vectors (quota 3/query), 8 subgraphs from 11 queries
  [100/100] retrieved=192 relevant=5 latency=20439ms

============================================================
  Retriever: Hybrid+Quota (decompose)  (100 samples)
============================================================
  Metric                    @1      @3      @5     @10     @15     @20     @50
  ────────────────────────────────────────────────────────────────────────────
  Hit                    0.460   0.600   0.640   0.810   0.870   0.900   0.940
  Recall (capped)        0.460   0.302   0.316   0.423   0.516   0.541   0.658
  Precision              0.460   0.300   0.220   0.147   0.119   0.093   0.046
  NDCG                   0.460   0.335   0.338   0.387   0.423   0.432   0.467

  Attack-chain samples: 100 (343 scoreable steps, 4 unscoreable)
  StepCoverage           0.143   0.268   0.320   0.434   0.528   0.551   0.661
  StepCoverage strict    0.108   0.236   0.290   0.401   0.502   0.528   0.642
    by cue: described    0.119   0.215   0.267   0.382   0.467   0.477   0.594
    by cue: named        0.323   0.581   0.645   0.709   0.872   0.949   0.987

  MRR                    0.554
  MAP                    0.313
  Avg Latency (ms)     14199.2


════════════════════════════════════════════════════════════
  EVALUATION COMPLETE
════════════════════════════════════════════════════════════
