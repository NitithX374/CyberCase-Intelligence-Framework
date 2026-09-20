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
[DECOMPOSE] No cloud LLM configured: CORE_LLM_PROVIDER=openrouter requires OPENROUTER_CYBERCASE; no automatic provider fallback is configured
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่งในจังหวัดนนทบุรีแจ้งความว่าระบบร...
[RETRIEVE] Query: เมื่อวันที่ 12 พฤษภาคม 2566 บริษัทเอกชนแห่งหนึ่งในจังหวัดนนทบุรีแจ้งความว่าระบบร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.097), ShimRat (0.078), Exploit Public-Facing Application (0.007), Application Shimming (0.003), Clambling (0.001), Application Layer Protocol (0.000), Email Forwarding Rule (0.000), Exploitation for Client Execution (0.000), File Transfer Protocols (0.000), Re-opened Applications (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → ShimRat (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [1/100] retrieved=88 relevant=4 latency=7275ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 3 ตุลาคม 2565 โรงพยาบาลเอกชนแห่งหนึ่งในจังหวัดเชียงใหม่แจ้งว่าระบบเว...
[RETRIEVE] Query: เมื่อวันที่ 3 ตุลาคม 2565 โรงพยาบาลเอกชนแห่งหนึ่งในจังหวัดเชียงใหม่แจ้งว่าระบบเว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.126), Windows Credential Editor (0.024), Ember Bear (0.010), Mustang Panda (0.008), OS Credential Dumping (0.007), Password Cracking (0.002), Credential Access Protection (0.001), IceApple (0.000), Credential Stuffing (0.000), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [2/100] retrieved=60 relevant=5 latency=3153ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 18 พฤศจิกายน 2565 สหกรณ์แห่งหนึ่งในจังหวัดขอนแก่นได้รับแจ้งเบาะแสจาก...
[RETRIEVE] Query: เมื่อวันที่ 18 พฤศจิกายน 2565 สหกรณ์แห่งหนึ่งในจังหวัดขอนแก่นได้รับแจ้งเบาะแสจาก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: KGH_SPY (0.037), Maze (0.010), TianySpy (0.008), H1N1 (0.001), Lokibot (0.001), Magic Hound (0.000), Threat Group-3390 (0.000), ShadowPad (0.000), Clear Windows Event Logs (0.000), Clear Linux or Mac System Logs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → KGH_SPY (21 neighbors, 21 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Maze (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [3/100] retrieved=288 relevant=3 latency=2953ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 9 ตุลาคม 2563 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Query: เมื่อวันที่ 9 ตุลาคม 2563 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Storm-1811 (0.033), LockBit 2.0 (0.030), MuddyWater (0.016), Ryuk (0.002), Registry Run Keys / Startup Folder (0.000), Query Registry (0.000), Modify Registry (0.000), Office Test (0.000), Windows Registry Key Modification (0.000), Windows Registry Key Access (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Storm-1811 (38 neighbors, 38 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [4/100] retrieved=314 relevant=3 latency=2872ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 22 กุมภาพันธ์ 2567 บริษัทรับเหมาก่อสร้างแห่งหนึ่งในจังหวัดระยองแจ้งว...
[RETRIEVE] Query: เมื่อวันที่ 22 กุมภาพันธ์ 2567 บริษัทรับเหมาก่อสร้างแห่งหนึ่งในจังหวัดระยองแจ้งว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: menuPass (0.001), XLoader (0.000), Darkhotel (0.000), FIN8 (0.000), System Script Proxy Execution (0.000), Password Managers (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Pikabot (0.000), Filter Network Traffic (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → menuPass (71 neighbors, 71 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Darkhotel (24 neighbors, 24 edges)
           → Process Discovery (320 neighbors, 320 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [5/100] retrieved=506 relevant=3 latency=3165ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 24 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่า...
[RETRIEVE] Query: เมื่อวันที่ 24 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dok (0.008), AutoIt backdoor (0.002), PipeMon (0.001), System Script Proxy Execution (0.000), PipeMon (0.000), Adversary-in-the-Middle (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), ARP Cache Poisoning (0.000), Evil Twin (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Dok (11 neighbors, 11 edges)
           → AutoIt backdoor (6 neighbors, 6 edges)
           → PipeMon (24 neighbors, 24 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [6/100] retrieved=282 relevant=4 latency=3269ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 7 มีนาคม 2567 บริษัทโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งว่าเค...
[RETRIEVE] Query: เมื่อวันที่ 7 มีนาคม 2567 บริษัทโลจิสติกส์แห่งหนึ่งในจังหวัดสมุทรปราการแจ้งว่าเค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Comnie (0.009), Proxysvc (0.001), Lokibot (0.000), FIN8 (0.000), Hijack Execution Flow (0.000), Reg (0.000), CrossRAT (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Comnie (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Proxysvc (16 neighbors, 16 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [7/100] retrieved=468 relevant=3 latency=2525ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 15 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความว่ามีการเข้าถึงข้...
[RETRIEVE] Query: เมื่อวันที่ 15 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความว่ามีการเข้าถึงข้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OS Credential Dumping (0.475), Windows Credential Editor (0.439), Axiom (0.409), Credential Access (0.354), Mustang Panda (0.346), HOMEFRY (0.284), Suckfly (0.171), Credential Access Protection (0.029), Credential Stuffing (0.011), Credentials In Files (0.002)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Axiom (24 neighbors, 24 edges)
           → Credential Access (67 neighbors, 67 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [8/100] retrieved=70 relevant=3 latency=2878ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 11 เมษายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความว่ามีการเข้าถึงเครื่องแ...
[RETRIEVE] Query: เมื่อวันที่ 11 เมษายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความว่ามีการเข้าถึงเครื่องแ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Credential Editor (0.258), Axiom (0.249), Suckfly (0.139), OS Credential Dumping (0.138), Ember Bear (0.116), Mimikatz (0.028), Credential Access Protection (0.027), Credential Access (0.024), Credentials In Files (0.003), Credential Stuffing (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Windows Credential Editor (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [9/100] retrieved=60 relevant=4 latency=2982ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 20 ตุลาคม 2563 หน่วยงานปกครองส่วนท้องถิ่นหลายแห่งแจ้งความว่าระบบสารส...
[RETRIEVE] Query: เมื่อวันที่ 20 ตุลาคม 2563 หน่วยงานปกครองส่วนท้องถิ่นหลายแห่งแจ้งความว่าระบบสารส...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploit Public-Facing Application (0.220), FIN13 (0.203), UNC3886 (0.090), SoreFang (0.051), External Remote Services (0.048), SharePoint ToolShell Exploitation (0.004), Brute Force (0.002), Valid Accounts (0.002), Web Portal Capture (0.001), Internal Spearphishing (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
           → FIN13 (57 neighbors, 57 edges)
           → External Remote Services (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [10/100] retrieved=155 relevant=5 latency=3402ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 5 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งในจังหวัดชลบุรีแจ้งความว่าข้อ...
[RETRIEVE] Query: เมื่อวันที่ 5 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งในจังหวัดชลบุรีแจ้งความว่าข้อ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN7 (0.026), SDBbot (0.021), PUNCHTRACK (0.009), ShimRat (0.008), FrameworkPOS (0.004), Pillowmint (0.002), Pillowmint (0.001), Pillowmint (0.000), RawPOS (0.000), Application Shimming (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → FIN7 (86 neighbors, 86 edges)
           → Application Shimming (11 neighbors, 11 edges)
           → SDBbot (25 neighbors, 25 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [11/100] retrieved=88 relevant=4 latency=2947ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 28 สิงหาคม 2566 บริษัทที่ปรึกษาด้านวิศวกรรมแห่งหนึ่งแจ้งความว่าเอกสา...
[RETRIEVE] Query: เมื่อวันที่ 28 สิงหาคม 2566 บริษัทที่ปรึกษาด้านวิศวกรรมแห่งหนึ่งแจ้งความว่าเอกสา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: schtasks (0.005), Ursnif (0.002), APT-C-36 (0.001), Operation Honeybee (0.001), Koadic (0.001), Scheduled Task/Job (0.001), System Script Proxy Execution (0.000), APT-C-36 (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → schtasks (4 neighbors, 4 edges)
           → Ursnif (36 neighbors, 36 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [12/100] retrieved=81 relevant=3 latency=2921ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 14 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Query: เมื่อวันที่ 14 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ursnif (0.035), LockBit 2.0 (0.016), APT29 (0.010), PsExec (0.006), REvil (0.001), Reg (0.000), Registry Run Keys / Startup Folder (0.000), Active Setup (0.000), Windows Registry Key Modification (0.000), Windows Registry Key Access (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ursnif (36 neighbors, 36 edges)
           → Registry Run Keys / Startup Folder (265 neighbors, 265 edges)
           → LockBit 2.0 (26 neighbors, 26 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [13/100] retrieved=312 relevant=3 latency=2986ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 8 กันยายน 2565 โรงเรียนมัธยมแห่งหนึ่งในจังหวัดสงขลาแจ้งความว่าระบบทะ...
[RETRIEVE] Query: เมื่อวันที่ 8 กันยายน 2565 โรงเรียนมัธยมแห่งหนึ่งในจังหวัดสงขลาแจ้งความว่าระบบทะ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Medusa Group (0.157), APT29 (0.142), Koadic (0.013), Windows Management Instrumentation (0.007), Windows Management Instrumentation Event Subscription (0.000), Unsecured Credentials (0.000), Query Registry (0.000), Windows Remote Management (0.000), Security Account Manager (0.000), Password Managers (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Medusa Group (62 neighbors, 62 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → APT29 (117 neighbors, 117 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [14/100] retrieved=280 relevant=4 latency=2326ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 3 ธันวาคม 2566 สำนักงานกฎหมายแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่ามีผู...
[RETRIEVE] Query: เมื่อวันที่ 3 ธันวาคม 2566 สำนักงานกฎหมายแห่งหนึ่งในกรุงเทพมหานครแจ้งความว่ามีผู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.114), SSH Hijacking (0.015), Cobalt Strike (0.015), LP-Notes (0.008), Kessel (0.004), Ramsay (0.004), File Deletion (0.002), DarkWatchman (0.002), SSH (0.001), GlassWorm (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → SSH (33 neighbors, 33 edges)
           → SSH Hijacking (8 neighbors, 8 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [15/100] retrieved=89 relevant=3 latency=2600ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 19 พฤษภาคม 2567 บริษัทหลักทรัพย์แห่งหนึ่งแจ้งความว่าหน้าจอการทำงานขอ...
[RETRIEVE] Query: เมื่อวันที่ 19 พฤษภาคม 2567 บริษัทหลักทรัพย์แห่งหนึ่งแจ้งความว่าหน้าจอการทำงานขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: VERMIN (0.018), RogueRobin (0.003), Screen Capture (0.000), Exfiltration Over C2 Channel (0.000), FIN8 (0.000), Video Capture (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), CrossRAT (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → VERMIN (17 neighbors, 17 edges)
           → Screen Capture (173 neighbors, 173 edges)
           → RogueRobin (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [16/100] retrieved=197 relevant=3 latency=3005ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 26 ตุลาคม 2565 คลินิกเวชกรรมเครือข่ายแห่งหนึ่งแจ้งความว่าข้อมูลคนไข้...
[RETRIEVE] Query: เมื่อวันที่ 26 ตุลาคม 2565 คลินิกเวชกรรมเครือข่ายแห่งหนึ่งแจ้งความว่าข้อมูลคนไข้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.131), Cobalt Strike (0.006), DCHSpy (0.004), DRYHOOK (0.004), SSH Hijacking (0.000), Remote Service Session Hijacking (0.000), SSH (0.000), Kessel (0.000), Valid Accounts (0.000), POSHSPY (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → SSH (33 neighbors, 33 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [17/100] retrieved=152 relevant=3 latency=2907ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 2 กันยายน 2567 บริษัทประกันภัยแห่งหนึ่งแจ้งความว่าบัญชีผู้ดูแลระบบขอ...
[RETRIEVE] Query: เมื่อวันที่ 2 กันยายน 2567 บริษัทประกันภัยแห่งหนึ่งแจ้งความว่าบัญชีผู้ดูแลระบบขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN6 (0.003), Security Account Manager (0.000), Unsecured Credentials (0.000), Valid Accounts (0.000), FIN8 (0.000), Daggerfly (0.000), Clear Windows Event Logs (0.000), Exploitation for Credential Access (0.000), Clear Linux or Mac System Logs (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → FIN6 (52 neighbors, 52 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Security Account Manager (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [18/100] retrieved=152 relevant=3 latency=2757ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 14 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Query: เมื่อวันที่ 14 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.003), DRYHOOK (0.001), Threat Group-3390 (0.000), Magic Hound (0.000), Unsecured Credentials (0.000), Internal Spearphishing (0.000), Clear Windows Event Logs (0.000), Wevtutil (0.000), Password Managers (0.000), Clear Linux or Mac System Logs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Keylogging (160 neighbors, 160 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [19/100] retrieved=370 relevant=3 latency=3898ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 21 ตุลาคม 2567 บริษัทผู้ผลิตชิ้นส่วนยานยนต์แห่งหนึ่งในจังหวัดปทุมธาน...
[RETRIEVE] Query: เมื่อวันที่ 21 ตุลาคม 2567 บริษัทผู้ผลิตชิ้นส่วนยานยนต์แห่งหนึ่งในจังหวัดปทุมธาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FlawedAmmyy (0.009), LookBack (0.003), Stuxnet (0.003), HALFBAKED (0.003), FIN8 (0.000), Software (0.000), CrossRAT (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → FlawedAmmyy (24 neighbors, 24 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → LookBack (16 neighbors, 16 edges)
           → System Service Discovery (71 neighbors, 71 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [20/100] retrieved=478 relevant=4 latency=2837ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 17 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งซึ่งประกอบธุรกิจซื้อขายสินทรัพย...
[RETRIEVE] Query: เมื่อวันที่ 17 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งซึ่งประกอบธุรกิจซื้อขายสินทรัพย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Fakecalls (0.176), MacMa (0.131), APT39 (0.065), CURIUM (0.061), Exfiltration Over C2 Channel (0.045), Automated Exfiltration (0.014), Scheduled Transfer (0.012), Exfiltration Over Alternative Protocol (0.001), Exfiltration Over Unencrypted Non-C2 Protocol (0.000), Installer Packages (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Fakecalls (11 neighbors, 11 edges)
           → Exfiltration Over C2 Channel (31 neighbors, 31 edges)
           → MacMa (28 neighbors, 28 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [21/100] retrieved=269 relevant=4 latency=3603ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 6 พฤศจิกายน 2566 สถานเอกอัครราชทูตแห่งหนึ่งแจ้งว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Query: เมื่อวันที่ 6 พฤศจิกายน 2566 สถานเอกอัครราชทูตแห่งหนึ่งแจ้งว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackdoorDiplomacy (0.044), BackdoorDiplomacy (0.009), File Deletion (0.003), APT-C-36 (0.002), Ursnif (0.001), APT-C-36 (0.000), Internal Spearphishing (0.000), Password Managers (0.000), Data Encrypted for Impact (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → BackdoorDiplomacy (20 neighbors, 20 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → Peripheral Device Discovery (60 neighbors, 60 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [22/100] retrieved=566 relevant=3 latency=3095ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 30 มิถุนายน 2565 บริษัทขนส่งแห่งหนึ่งในจังหวัดพระนครศรีอยุธยาแจ้งควา...
[RETRIEVE] Query: เมื่อวันที่ 30 มิถุนายน 2565 บริษัทขนส่งแห่งหนึ่งในจังหวัดพระนครศรีอยุธยาแจ้งควา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.005), Data Encrypted for Impact (0.003), BlackByte (0.001), Deobfuscate/Decode Files or Information (0.001), Adversary-in-the-Middle (0.000), Evil Twin (0.000), Magic Hound (0.000), ARP Cache Poisoning (0.000), Threat Group-3390 (0.000), Anthropic AI-orchestrated Campaign (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Encrypted/Encoded File (250 neighbors, 250 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [23/100] retrieved=326 relevant=2 latency=3555ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 25 มกราคม 2567 โรงแรมแห่งหนึ่งในจังหวัดภูเก็ตแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Query: เมื่อวันที่ 25 มกราคม 2567 โรงแรมแห่งหนึ่งในจังหวัดภูเก็ตแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Denis (0.001), Darkhotel (0.001), RDP Hijacking (0.000), FIN8 (0.000), Reg (0.000), Scheduled Task/Job (0.000), Windows Remote Management (0.000), Right-to-Left Override (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Denis (21 neighbors, 21 edges)
           → Windows Command Shell (390 neighbors, 390 edges)
           → Darkhotel (24 neighbors, 24 edges)
           → Process Discovery (320 neighbors, 320 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [24/100] retrieved=576 relevant=3 latency=2595ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 12 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งว่าเครื่องคอมพิวเต...
[RETRIEVE] Query: เมื่อวันที่ 12 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งว่าเครื่องคอมพิวเต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.048), APT29 (0.040), Password Spraying (0.025), CrackMapExec (0.003), Password Cracking (0.001), Password Guessing (0.000), Password Managers (0.000), Active Setup (0.000), Subvert Trust Controls (0.000), Password Policies (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Password Spraying (23 neighbors, 23 edges)
           → APT29 (117 neighbors, 117 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [25/100] retrieved=151 relevant=3 latency=3288ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 21 กุมภาพันธ์ 2565 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าตรวจพบโปรแกรมไม...
[RETRIEVE] Query: เมื่อวันที่ 21 กุมภาพันธ์ 2565 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าตรวจพบโปรแกรมไม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: CLAIMLOADER (0.252), DLL (0.172), PowGoop (0.112), POWERSOURCE (0.052), POWERSOURCE (0.011), Netwalker (0.006), StrelaStealer (0.005), PowerShell (0.001), PowerShell Profile (0.000), Rundll32 (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DLL (123 neighbors, 123 edges)
           → CLAIMLOADER (12 neighbors, 12 edges)
           → PowGoop (9 neighbors, 9 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [26/100] retrieved=137 relevant=3 latency=4003ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 27 ตุลาคม 2563 หน่วยงานวิจัยแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Query: เมื่อวันที่ 27 ตุลาคม 2563 หน่วยงานวิจัยแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NanHaiShu (0.073), APT32 (0.032), FIN7 (0.027), Mshta (0.001), SideCopy (0.001), Maze (0.000), Ingress Tool Transfer (0.000), Winexe (0.000), Msiexec (0.000), cmd (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → NanHaiShu (13 neighbors, 13 edges)
           → Mshta (34 neighbors, 34 edges)
           → APT32 (93 neighbors, 93 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [27/100] retrieved=104 relevant=4 latency=3591ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 12 กรกฎาคม 2565 บริษัทรับจ้างผลิตแห่งหนึ่งในจังหวัดสมุทรสาครแจ้งความ...
[RETRIEVE] Query: เมื่อวันที่ 12 กรกฎาคม 2565 บริษัทรับจ้างผลิตแห่งหนึ่งในจังหวัดสมุทรสาครแจ้งความ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Daggerfly (0.084), C0021 (0.067), Netwalker (0.067), POWERSTATS (0.032), POWERSTATS (0.010), POWERSOURCE (0.009), PowerShell Profile (0.000), PowerShell (0.000), ServHelper (0.000), Disable or Remove Feature or Program (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Daggerfly (23 neighbors, 23 edges)
           → PowerShell (241 neighbors, 241 edges)
           → C0021 (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [28/100] retrieved=271 relevant=3 latency=3018ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 13 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบยูนิกซ์...
[RETRIEVE] Query: เมื่อวันที่ 13 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบยูนิกซ์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Indrik Spider (0.016), PlugX (0.013), Unsecured Credentials (0.002), Ingress Tool Transfer (0.001), OS Credential Dumping (0.000), Valid Accounts (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), Clear Linux or Mac System Logs (0.000), Clear Windows Event Logs (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Indrik Spider (41 neighbors, 41 edges)
           → Credentials In Files (44 neighbors, 44 edges)
           → PlugX (65 neighbors, 65 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [29/100] retrieved=611 relevant=5 latency=8707ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 4 สิงหาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความว่าฐานข้อมูลสำรองของระบ...
[RETRIEVE] Query: เมื่อวันที่ 4 สิงหาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความว่าฐานข้อมูลสำรองของระบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Chimera (0.003), File Deletion (0.002), FIN8 (0.000), RAPIDPULSE (0.000), POWERSOURCE (0.000), 4H RAT (0.000), KernelCallbackTable (0.000), Network Boundary Bridging (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Chimera (65 neighbors, 65 edges)
           → Local Email Collection (25 neighbors, 25 edges)
           → File Deletion (310 neighbors, 310 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [30/100] retrieved=381 relevant=3 latency=4216ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 16 กันยายน 2567 บริษัทนำเข้าส่งออกแห่งหนึ่งแจ้งความว่าบัญชีผู้ใช้งาน...
[RETRIEVE] Query: เมื่อวันที่ 16 กันยายน 2567 บริษัทนำเข้าส่งออกแห่งหนึ่งแจ้งความว่าบัญชีผู้ใช้งาน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.010), POWRUNER (0.003), Password Managers (0.001), FIN8 (0.001), Unsecured Credentials (0.000), Reversible Encryption (0.000), Pikabot (0.000), Credentials in Registry (0.000), Cloud Accounts (0.000), Windows Credential Manager (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → Keylogging (160 neighbors, 160 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [31/100] retrieved=356 relevant=3 latency=2494ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 14 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ได้รับอีเมลต้...
[RETRIEVE] Query: เมื่อวันที่ 14 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ได้รับอีเมลต้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Frankenstein (0.210), BlackTech (0.051), Covenant (0.010), Windows Command Shell (0.007), EvilGrab (0.005), cmd (0.005), XLoader (0.003), Masquerade File Type (0.002), Chaos (0.001), Command and Scripting Interpreter (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Frankenstein (28 neighbors, 28 edges)
           → Malicious File (202 neighbors, 202 edges)
           → BlackTech (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [32/100] retrieved=236 relevant=3 latency=3115ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 30 พฤศจิกายน 2566 บริษัทผู้ให้บริการด้านเทคโนโลยีสารสนเทศแห่งหนึ่งแจ...
[RETRIEVE] Query: เมื่อวันที่ 30 พฤศจิกายน 2566 บริษัทผู้ให้บริการด้านเทคโนโลยีสารสนเทศแห่งหนึ่งแจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.436), pwdump (0.279), OS Credential Dumping (0.259), Windows Credential Editor (0.210), BlackByte (0.189), Sowbug (0.175), Suckfly (0.157), Credentials In Files (0.002), Credential Access (0.002), Credential Access Protection (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → pwdump (7 neighbors, 7 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [33/100] retrieved=60 relevant=4 latency=2744ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 8 ธันวาคม 2566 บริษัทที่ปรึกษาแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใ...
[RETRIEVE] Query: เมื่อวันที่ 8 ธันวาคม 2566 บริษัทที่ปรึกษาแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ShadowPad (0.006), APT-C-36 (0.002), POWRUNER (0.001), APT-C-36 (0.000), Account Discovery (0.000), Domains (0.000), Ursnif (0.000), System Network Connections Discovery (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → ShadowPad (31 neighbors, 31 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [34/100] retrieved=363 relevant=5 latency=8945ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 19 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Query: เมื่อวันที่ 19 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายเก็บ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.008), Clambling (0.002), APT-C-36 (0.001), Ursnif (0.000), Conficker (0.000), File Deletion (0.000), Hidden File System (0.000), Pre-OS Boot (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Clambling (35 neighbors, 35 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [35/100] retrieved=237 relevant=5 latency=5024ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 22 กุมภาพันธ์ 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ถูกหลอกให้...
[RETRIEVE] Query: เมื่อวันที่ 22 กุมภาพันธ์ 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเจ้าหน้าที่ถูกหลอกให้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Frankenstein (0.651), Malicious File (0.435), Rancor (0.176), Deobfuscate/Decode Files or Information (0.006), Adversary-in-the-Middle (0.001), Evil Twin (0.001), Outlook Forms (0.001), Magic Hound (0.000), Threat Group-3390 (0.000), ARP Cache Poisoning (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Frankenstein (28 neighbors, 28 edges)
           → Malicious File (202 neighbors, 202 edges)
           → Rancor (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [36/100] retrieved=233 relevant=3 latency=2593ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 27 มิถุนายน 2567 บริษัทโลจิสติกส์ข้ามชาติสาขาประเทศไทยแจ้งความว่าเคร...
[RETRIEVE] Query: เมื่อวันที่ 27 มิถุนายน 2567 บริษัทโลจิสติกส์ข้ามชาติสาขาประเทศไทยแจ้งความว่าเคร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: admin@338 (0.001), admin@338 (0.001), Ingress Tool Transfer (0.000), FIN8 (0.000), Exploitation of Remote Services (0.000), Data Encrypted for Impact (0.000), Pikabot (0.000), Exfiltration to Text Storage Sites (0.000), Setuid and Setgid (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → admin@338 (19 neighbors, 19 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [37/100] retrieved=326 relevant=3 latency=3716ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 18 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ระ...
[RETRIEVE] Query: เมื่อวันที่ 18 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ระ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Create or Modify System Process (0.644), APT3 (0.458), Pallas (0.433), PUNCHTRACK (0.219), Deobfuscate/Decode Files or Information (0.147), VERMIN (0.099), Hide Artifacts (0.041), Obfuscated Files or Information (0.021), Encrypted/Encoded File (0.018), Hidden Files and Directories (0.011)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → APT3 (50 neighbors, 50 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [38/100] retrieved=227 relevant=3 latency=4514ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 21 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Query: เมื่อวันที่ 21 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Windows Credential Editor (0.276), Axiom (0.202), HOMEFRY (0.154), OS Credential Dumping (0.116), Suckfly (0.055), gsecdump (0.020), Password Cracking (0.007), Credential Access (0.006), Credential Access Protection (0.001), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Windows Credential Editor (8 neighbors, 8 edges)
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [39/100] retrieved=60 relevant=3 latency=3276ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 19 กุมภาพันธ์ 2564 ผู้เสียหายอีกรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Query: เมื่อวันที่ 19 กุมภาพันธ์ 2564 ผู้เสียหายอีกรายหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: JHUHUGIT (0.828), ccf32 (0.641), Solar (0.407), CURIUM (0.300), Exfiltration Over C2 Channel (0.085), Scheduled Transfer (0.079), Automated Exfiltration (0.047), Scheduled Task/Job (0.026), Scheduled Task (0.005), Exfiltration Over Unencrypted Non-C2 Protocol (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → JHUHUGIT (21 neighbors, 21 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → ccf32 (13 neighbors, 13 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [40/100] retrieved=230 relevant=3 latency=8943ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 11 ตุลาคม 2567 บริษัทวิศวกรรมแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใน...
[RETRIEVE] Query: เมื่อวันที่ 11 ตุลาคม 2567 บริษัทวิศวกรรมแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายภายใน...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Lucifer (0.031), Operation Honeybee (0.005), FIN8 (0.001), File Deletion (0.000), Deobfuscate/Decode Files or Information (0.000), Windows Management Instrumentation (0.000), Browser Extensions (0.000), Video Capture (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Lucifer (24 neighbors, 24 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → Operation Honeybee (33 neighbors, 33 edges)
           → File Deletion (310 neighbors, 310 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [41/100] retrieved=524 relevant=3 latency=3301ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 29 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Query: เมื่อวันที่ 29 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายควบคุมโด...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dragonfly (0.021), APT-C-36 (0.011), APT-C-36 (0.005), BADHATCH (0.001), Domain Accounts (0.000), Ursnif (0.000), Domains (0.000), Internal Spearphishing (0.000), Domain Account (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Dragonfly (66 neighbors, 66 edges)
           → Domain Account (65 neighbors, 65 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [42/100] retrieved=165 relevant=3 latency=3298ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 15 พฤศจิกายน 2566 มหาวิทยาลัยแห่งหนึ่งแจ้งความว่าระบบสารสนเทศของมหาว...
[RETRIEVE] Query: เมื่อวันที่ 15 พฤศจิกายน 2566 มหาวิทยาลัยแห่งหนึ่งแจ้งความว่าระบบสารสนเทศของมหาว...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: ZxShell (0.006), zwShell (0.001), LAPSUS$ (0.000), RDP Hijacking (0.000), POWERSOURCE (0.000), Remote Desktop Protocol (0.000), Duqu (0.000), Valid Accounts (0.000), PowerShell (0.000), Modify Authentication Process (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → ZxShell (37 neighbors, 37 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → zwShell (12 neighbors, 12 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [43/100] retrieved=108 relevant=5 latency=3969ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความว่าข้อมูลลูกค้าถูกนำออ...
[RETRIEVE] Query: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความว่าข้อมูลลูกค้าถูกนำออ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.204), INC Ransom (0.127), Pay2Key (0.014), Data Encrypted for Impact (0.013), Ursnif (0.004), Exfiltration (0.003), APT-C-36 (0.000), Internal Spearphishing (0.000), Social Engineering (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → INC Ransom (33 neighbors, 33 edges)
           → Financial Theft (27 neighbors, 27 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [44/100] retrieved=116 relevant=3 latency=8649ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 1 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าแม้จะล้างเครื่องและติดตั้...
[RETRIEVE] Query: เมื่อวันที่ 1 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าแม้จะล้างเครื่องและติดตั้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Create or Modify System Process (0.011), MoonWind (0.005), BackConfig (0.002), Active Setup (0.001), ZxShell (0.000), APT28 (0.000), Event Triggered Execution (0.000), Network Denial of Service (0.000), Lazarus Group (0.000), Password Policies (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Create or Modify System Process (25 neighbors, 25 edges)
           → MoonWind (15 neighbors, 15 edges)
           → Windows Service (150 neighbors, 150 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [45/100] retrieved=176 relevant=3 latency=4826ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 23 มิถุนายน 2565 บริษัทเทคโนโลยีแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายขอ...
[RETRIEVE] Query: เมื่อวันที่ 23 มิถุนายน 2565 บริษัทเทคโนโลยีแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายขอ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: QUADAGENT (0.135), Confucius (0.108), BackConfig (0.010), Scheduled Task/Job (0.006), schtasks (0.004), Seth-Locker (0.003), schtasks (0.002), Scheduled Task (0.002), Scheduled Transfer (0.000), Masquerade Task or Service (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → QUADAGENT (18 neighbors, 18 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → Confucius (22 neighbors, 22 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [46/100] retrieved=229 relevant=3 latency=2809ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 9 กรกฎาคม 2567 บริษัทปิโตรเคมีแห่งหนึ่งในจังหวัดระยองแจ้งความว่าเครื...
[RETRIEVE] Query: เมื่อวันที่ 9 กรกฎาคม 2567 บริษัทปิโตรเคมีแห่งหนึ่งในจังหวัดระยองแจ้งความว่าเครื...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Carbon (0.001), POWRUNER (0.000), FIN8 (0.000), Password Policy Discovery (0.000), Account Discovery (0.000), Exfiltration to Text Storage Sites (0.000), CrossRAT (0.000), Pikabot (0.000), Query Registry (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Carbon (19 neighbors, 19 edges)
           → Process Discovery (320 neighbors, 320 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [47/100] retrieved=381 relevant=6 latency=3916ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 20 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความว่าเจ้า...
[RETRIEVE] Query: เมื่อวันที่ 20 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความว่าเจ้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA2541 (0.017), POWERSTATS (0.014), POWERSOURCE (0.007), POWERSTATS (0.007), POWRUNER (0.003), POWERSOURCE (0.002), PowerShell (0.001), PowerShell Profile (0.000), Disable or Remove Feature or Program (0.000), ZxShell (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → TA2541 (37 neighbors, 37 edges)
           → PowerShell (241 neighbors, 241 edges)
           → POWERSTATS (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [48/100] retrieved=276 relevant=3 latency=2879ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 6 มิถุนายน 2567 บริษัทมหาชนแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของ...
[RETRIEVE] Query: เมื่อวันที่ 6 มิถุนายน 2567 บริษัทมหาชนแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Net Crawler (0.000), WannaCry (0.000), FIN8 (0.000), Darkhotel (0.000), EvilGrab (0.000), Lokibot (0.000), Password Policy Discovery (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → WannaCry (17 neighbors, 17 edges)
           → RDP Hijacking (12 neighbors, 12 edges)
           → Net Crawler (5 neighbors, 5 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [49/100] retrieved=35 relevant=4 latency=3406ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 2 มิถุนายน 2566 บริษัทแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Query: เมื่อวันที่ 2 มิถุนายน 2566 บริษัทแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Duqu (0.040), APT-C-36 (0.038), Pasam (0.025), Ursnif (0.021), APT-C-36 (0.007), Internal Spearphishing (0.000), Lateral Tool Transfer (0.000), System Script Proxy Execution (0.000), Social Engineering (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Duqu (21 neighbors, 21 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [50/100] retrieved=271 relevant=3 latency=3071ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 12 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าจดหมายอิเล็กทรอนิก...
[RETRIEVE] Query: เมื่อวันที่ 12 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าจดหมายอิเล็กทรอนิก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackdoorDiplomacy (0.008), APT-C-36 (0.004), Ursnif (0.001), XLoader (0.001), APT-C-36 (0.001), AADInternals (0.000), System Script Proxy Execution (0.000), File Deletion (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → BackdoorDiplomacy (20 neighbors, 20 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [51/100] retrieved=582 relevant=3 latency=9800ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 8 พฤษภาคม 2567 ผู้ให้บริการโครงข่ายแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่า...
[RETRIEVE] Query: เมื่อวันที่ 8 พฤษภาคม 2567 ผู้ให้บริการโครงข่ายแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Dragonfly (0.001), LAPSUS$ (0.001), System Time Discovery (0.000), FIN8 (0.000), AppInit DLLs (0.000), Lokibot (0.000), Scheduled Task/Job (0.000), Password Policy Discovery (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Dragonfly (66 neighbors, 66 edges)
           → Scheduled Task (201 neighbors, 201 edges)
           → LAPSUS$ (45 neighbors, 45 edges)
           → Password Managers (20 neighbors, 20 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [52/100] retrieved=290 relevant=4 latency=4662ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 12 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Query: เมื่อวันที่ 12 เมษายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายบริหารจัดกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DCHSpy (0.001), Exploit Public-Facing Application (0.001), Cardinal RAT (0.000), Ingress Tool Transfer (0.000), Exploitation for Client Execution (0.000), ThiefQuest (0.000), OwaAuth (0.000), Wevtutil (0.000), Clear Linux or Mac System Logs (0.000), Clear Windows Event Logs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DCHSpy (13 neighbors, 13 edges)
           → Call Log (44 neighbors, 44 edges)
           → Exploit Public-Facing Application (84 neighbors, 84 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [53/100] retrieved=138 relevant=5 latency=3263ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 14 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Query: เมื่อวันที่ 14 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.006), Bankshot (0.002), Pikabot (0.000), FIN8 (0.000), Domains (0.000), Domain Account (0.000), Domain Accounts (0.000), Windows Registry Key Modification (0.000), Access Token Manipulation (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [54/100] retrieved=128 relevant=3 latency=4585ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 27 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความว่าอุปกรณ์เ...
[RETRIEVE] Query: เมื่อวันที่ 27 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความว่าอุปกรณ์เ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.002), BlackByte (0.001), APT-C-36 (0.001), Component Firmware (0.000), DRYHOOK (0.000), Ursnif (0.000), Internal Spearphishing (0.000), Compromise Host Software Binary (0.000), Shortcut Modification (0.000), Social Engineering (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → BlackByte (56 neighbors, 56 edges)
           → Disable or Modify System Firewall (38 neighbors, 38 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [55/100] retrieved=134 relevant=3 latency=3168ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 28 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความว่าเครือข่ายของสำนักง...
[RETRIEVE] Query: เมื่อวันที่ 28 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความว่าเครือข่ายของสำนักง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.025), ServHelper (0.016), HomeLand Justice (0.000), RDP Hijacking (0.000), Network Intrusion Prevention (0.000), File Deletion (0.000), Remote Services (0.000), Remote Desktop Protocol (0.000), Terminal Services DLL (0.000), Data Encrypted for Impact (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → ServHelper (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [56/100] retrieved=109 relevant=4 latency=3067ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 16 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความว่าระบบงานทั้งหมดถูกเข้า...
[RETRIEVE] Query: เมื่อวันที่ 16 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความว่าระบบงานทั้งหมดถูกเข้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: REvil (0.005), POWERSTATS (0.004), Pay2Key (0.001), BitPaymer (0.001), Data Encrypted for Impact (0.000), POWERSOURCE (0.000), Disable or Remove Feature or Program (0.000), PowerSploit (0.000), PowerShell (0.000), PowerShell Profile (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → REvil (37 neighbors, 37 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → PowerShell (241 neighbors, 241 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [57/100] retrieved=337 relevant=6 latency=4744ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 17 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความว่าลูกค้าหลายรายถูกโอนเงินออกจ...
[RETRIEVE] Query: เมื่อวันที่ 17 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความว่าลูกค้าหลายรายถูกโอนเงินออกจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.282), Frankenstein (0.252), Exfiltration Over C2 Channel (0.150), Octopus (0.147), AuTo Stealer (0.143), Resource Hijacking (0.140), Automated Exfiltration (0.040), Scheduled Transfer (0.008), Exfiltration Over Unencrypted Non-C2 Protocol (0.001), Financial Theft (0.001)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Exfiltration Over C2 Channel (205 neighbors, 205 edges)
           → Frankenstein (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [58/100] retrieved=242 relevant=4 latency=2255ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 1 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครือข่ายภายในถูกบุกรุกผ...
[RETRIEVE] Query: เมื่อวันที่ 1 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครือข่ายภายในถูกบุกรุกผ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NETWIRE (0.007), Network Device Firewall (0.006), SharePoint ToolShell Exploitation (0.002), Internal Spearphishing (0.001), Magic Hound (0.001), Threat Group-3390 (0.000), Valid Accounts (0.000), Trusted Relationship (0.000), Clear Windows Event Logs (0.000), Clear Linux or Mac System Logs (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Network Device Firewall (9 neighbors, 9 edges)
           → NETWIRE (49 neighbors, 49 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [59/100] retrieved=141 relevant=3 latency=2964ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 3 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์หลาย...
[RETRIEVE] Query: เมื่อวันที่ 3 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์หลาย...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WINDSHIELD (0.009), njRAT (0.003), 3CX Supply Chain Attack (0.000), FIN8 (0.000), Software Discovery (0.000), 3PARA RAT (0.000), Software (0.000), Process Discovery (0.000), Pikabot (0.000), APT1 (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → WINDSHIELD (6 neighbors, 6 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → njRAT (40 neighbors, 40 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [60/100] retrieved=462 relevant=6 latency=3921ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 20 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบเดสก์...
[RETRIEVE] Query: เมื่อวันที่ 20 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องแม่ข่ายระบบเดสก์...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: OSInfo (0.001), VOID MANTICORE (0.001), Wiarp (0.001), Adversary-in-the-Middle (0.000), Evil Twin (0.000), Ingress Tool Transfer (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), Input Injection (0.000), ARP Cache Poisoning (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → OSInfo (11 neighbors, 11 edges)
           → VOID MANTICORE (64 neighbors, 64 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [61/100] retrieved=213 relevant=4 latency=9366ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 5 เมษายน 2567 บริษัทผู้ให้บริการระบบสารสนเทศแห่งหนึ่งแจ้งความว่าเครื...
[RETRIEVE] Query: เมื่อวันที่ 5 เมษายน 2567 บริษัทผู้ให้บริการระบบสารสนเทศแห่งหนึ่งแจ้งความว่าเครื...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan (0.045), Cobalt Strike (0.003), ServHelper (0.001), SSH Hijacking (0.000), SSH Authorized Keys (0.000), DCHSpy (0.000), SSH (0.000), P.A.S. Webshell (0.000), Forced Authentication (0.000), Internal Spearphishing (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Leviathan (68 neighbors, 68 edges)
           → SSH (33 neighbors, 33 edges)
           → Cobalt Strike (109 neighbors, 109 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [62/100] retrieved=151 relevant=5 latency=3615ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 30 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเอกสารราชการในเครื่องคอมพ...
[RETRIEVE] Query: เมื่อวันที่ 30 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเอกสารราชการในเครื่องคอมพ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.112), Koadic (0.036), P.A.S. Webshell (0.002), RDP Hijacking (0.002), Remote Desktop Protocol (0.001), ZxShell (0.001), File Deletion (0.000), Ingress Tool Transfer (0.000), System Script Proxy Execution (0.000), Remote Services (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → Remote Desktop Protocol (74 neighbors, 74 edges)
           → Koadic (31 neighbors, 31 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [63/100] retrieved=118 relevant=3 latency=2836ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 18 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกลุก...
[RETRIEVE] Query: เมื่อวันที่ 18 ตุลาคม 2567 บริษัทค้าส่งแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุกลุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN8 (0.002), POWRUNER (0.001), POWRUNER (0.000), Ingress Tool Transfer (0.000), Gamaredon Group (0.000), Winlogon Helper DLL (0.000), Named Pipe Metadata (0.000), Exploitation for Privilege Escalation (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → FIN8 (47 neighbors, 47 edges)
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Account (65 neighbors, 65 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [64/100] retrieved=151 relevant=3 latency=3974ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 24 กรกฎาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการสำรวจ...
[RETRIEVE] Query: เมื่อวันที่ 24 กรกฎาคม 2567 บริษัทพลังงานแห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการสำรวจ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Net (0.018), menuPass (0.007), Remote System Discovery (0.004), System Network Connections Discovery (0.002), Process Discovery (0.000), FIN8 (0.000), Cloud Accounts (0.000), Exfiltration to Text Storage Sites (0.000), Pikabot (0.000), Password Policies (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Net (50 neighbors, 50 edges)
           → System Network Connections Discovery (99 neighbors, 99 edges)
           → menuPass (71 neighbors, 71 edges)
           → Remote System Discovery (104 neighbors, 104 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [65/100] retrieved=237 relevant=4 latency=2927ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 21 พฤศจิกายน 2565 บริษัทแห่งหนึ่งแจ้งความว่าข้อมูลในระบบถูกเข้ารหัสล...
[RETRIEVE] Query: เมื่อวันที่ 21 พฤศจิกายน 2565 บริษัทแห่งหนึ่งแจ้งความว่าข้อมูลในระบบถูกเข้ารหัสล...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: INC Ransomware (0.034), ThiefQuest (0.018), Data Encrypted for Impact (0.003), Inhibit System Recovery (0.002), Evil Twin (0.000), ARP Cache Poisoning (0.000), Magic Hound (0.000), Threat Group-3390 (0.000), Adversary-in-the-Middle (0.000), Clear Windows Event Logs (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → INC Ransomware (16 neighbors, 16 edges)
           → Inhibit System Recovery (62 neighbors, 62 edges)
           → ThiefQuest (18 neighbors, 18 edges)
           → Data Encrypted for Impact (88 neighbors, 88 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [66/100] retrieved=131 relevant=6 latency=4340ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 21 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้...
[RETRIEVE] Query: เมื่อวันที่ 21 สิงหาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ของเจ้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Crimson (0.344), KeyBoy (0.155), PowerSploit (0.038), LaZagne (0.023), Unsecured Credentials (0.018), Password Managers (0.006), Registry Run Keys / Startup Folder (0.004), Credentials from Web Browsers (0.003), Credentials in Registry (0.002), Windows Credential Manager (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Crimson (32 neighbors, 32 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → KeyBoy (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [67/100] retrieved=135 relevant=3 latency=3138ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 11 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าข้อมูลที่รวบ...
[RETRIEVE] Query: เมื่อวันที่ 11 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าข้อมูลที่รวบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MobileOrder (0.002), WellMail (0.002), Ingress Tool Transfer (0.001), Data from Local System (0.000), Windows Management Instrumentation (0.000), FIN8 (0.000), Exploitation of Remote Services (0.000), Pikabot (0.000), Cloud Accounts (0.000), Browser Extensions (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → MobileOrder (8 neighbors, 8 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [68/100] retrieved=591 relevant=3 latency=2751ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 17 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดเค...
[RETRIEVE] Query: เมื่อวันที่ 17 พฤศจิกายน 2566 โรงพยาบาลแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดเค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.054), Bankshot (0.049), APT-C-36 (0.030), Data Encrypted for Impact (0.014), APT-C-36 (0.011), Ursnif (0.008), Ingress Tool Transfer (0.000), Input Injection (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [69/100] retrieved=693 relevant=3 latency=3442ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 20 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการเชื่...
[RETRIEVE] Query: เมื่อวันที่ 20 มิถุนายน 2567 ธนาคารพาณิชย์แห่งหนึ่งแจ้งความเพิ่มเติมว่าพบการเชื่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.007), Bankshot (0.003), FIN8 (0.001), Salesforce Data Exfiltration (0.000), DNS (0.000), FrostyGoop Incident (0.000), Valid Accounts (0.000), Domain Accounts (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → Local Account (69 neighbors, 69 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [70/100] retrieved=129 relevant=3 latency=3167ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 19 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Query: เมื่อวันที่ 19 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: PUNCHTRACK (0.035), RawPOS (0.001), Exfiltration to Text Storage Sites (0.000), FIN8 (0.000), Hijack Execution Flow (0.000), Event Triggered Execution (0.000), Password Managers (0.000), Pikabot (0.000), Process Injection (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → PUNCHTRACK (4 neighbors, 4 edges)
           → Data from Local System (232 neighbors, 232 edges)
           → RawPOS (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [71/100] retrieved=241 relevant=3 latency=3194ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 4 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Query: เมื่อวันที่ 4 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.272), Suckfly (0.088), pwdump (0.087), Windows Credential Editor (0.069), OS Credential Dumping (0.053), BlackByte (0.036), Credential Access Protection (0.012), Credential Access Protection (0.004), Credentials In Files (0.001), Credential Access (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → Suckfly (6 neighbors, 6 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [72/100] retrieved=58 relevant=3 latency=2853ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 26 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเต...
[RETRIEVE] Query: เมื่อวันที่ 26 กุมภาพันธ์ 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเต...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: WINDSHIELD (0.012), BackConfig (0.001), Query Registry (0.001), FIN8 (0.000), Process Discovery (0.000), Password Guessing (0.000), System Language Discovery (0.000), Security Software Discovery (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → WINDSHIELD (6 neighbors, 6 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → BackConfig (17 neighbors, 17 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [73/100] retrieved=444 relevant=6 latency=3226ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 4 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ข...
[RETRIEVE] Query: เมื่อวันที่ 4 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ข...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Ursnif (0.038), NetTraveler (0.014), TrickBot (0.012), APT-C-36 (0.006), Malicious File (0.005), APT-C-36 (0.004), BADNEWS (0.002), External Defacement (0.001), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Ursnif (36 neighbors, 36 edges)
           → TrickBot (57 neighbors, 57 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [74/100] retrieved=258 relevant=3 latency=3285ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 1 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Query: เมื่อวันที่ 1 มีนาคม 2567 หน่วยงานด้านการต่างประเทศแห่งหนึ่งแจ้งความเพิ่มเติมถึง...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Exploitation for Privilege Escalation (0.039), Modify Registry (0.005), UPPERCUT (0.004), FIN8 (0.003), BackConfig (0.001), Valid Accounts (0.000), Exfiltration to Text Storage Sites (0.000), Lazarus Group (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Exploitation for Privilege Escalation (50 neighbors, 50 edges)
           → Modify Registry (177 neighbors, 177 edges)
           → UPPERCUT (18 neighbors, 18 edges)
           → System Network Configuration Discovery (289 neighbors, 289 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [75/100] retrieved=443 relevant=3 latency=3597ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 19 กรกฎาคม 2564 หน่วยงานแห่งหนึ่งแจ้งความว่าถูกลักลอบเข้าถึงข้อมูลภา...
[RETRIEVE] Query: เมื่อวันที่ 19 กรกฎาคม 2564 หน่วยงานแห่งหนึ่งแจ้งความว่าถูกลักลอบเข้าถึงข้อมูลภา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: FIN13 (0.309), External Remote Services (0.063), Duqu (0.011), FLIPSIDE (0.008), FakeSpy (0.001), Protocol or Service Impersonation (0.001), RDP Hijacking (0.001), Exfiltration Over Alternative Protocol (0.000), Protocol Tunneling (0.000), Remote Desktop Protocol (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → FIN13 (57 neighbors, 57 edges)
           → External Remote Services (52 neighbors, 52 edges)
           → Duqu (21 neighbors, 21 edges)
           → Protocol Tunneling (46 neighbors, 46 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [76/100] retrieved=141 relevant=6 latency=4294ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 25 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Query: เมื่อวันที่ 25 กันยายน 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.047), File Deletion (0.041), Bankshot (0.019), APT-C-36 (0.002), Ingress Tool Transfer (0.002), Ursnif (0.001), USBStealer (0.001), Internal Spearphishing (0.000), Right-to-Left Override (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → File Deletion (310 neighbors, 310 edges)
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [77/100] retrieved=368 relevant=3 latency=3209ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 29 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความเพิ่มเติมถึงเส้นทางที...
[RETRIEVE] Query: เมื่อวันที่ 29 กันยายน 2566 บริษัทข้ามชาติแห่งหนึ่งแจ้งความเพิ่มเติมถึงเส้นทางที...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Sandworm Team (0.831), Sea Turtle (0.700), Trusted Relationship (0.229), TeamTNT (0.004), Business Relationships (0.001), Ingress Tool Transfer (0.001), Network Trust Dependencies (0.000), Network Security Appliances (0.000), Domain Trust Discovery (0.000), Customer Relationship Management Software (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Sandworm Team (113 neighbors, 113 edges)
           → Trusted Relationship (18 neighbors, 18 edges)
           → Sea Turtle (28 neighbors, 28 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [78/100] retrieved=124 relevant=3 latency=3242ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 30 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความเพิ่มเติมถึ...
[RETRIEVE] Query: เมื่อวันที่ 30 กันยายน 2566 ผู้ให้บริการอินเทอร์เน็ตแห่งหนึ่งแจ้งความเพิ่มเติมถึ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.006), APT-C-36 (0.001), Attestation (0.000), Network Intrusion Prevention (0.000), Ursnif (0.000), Compromise Host Software Binary (0.000), Internal Spearphishing (0.000), Subvert Trust Controls (0.000), Social Engineering (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → AsyncRAT (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [79/100] retrieved=73 relevant=2 latency=9791ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 6 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Query: เมื่อวันที่ 6 ตุลาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความว่าเครื่องคอมพิวเตอร์ในองค์กร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA505 (0.023), KeyBoy (0.016), NotPetya (0.015), LaZagne (0.004), Credentials from Web Browsers (0.004), Unsecured Credentials (0.001), Web Credential Usage (0.000), Credentials in Registry (0.000), Query Registry (0.000), Windows Credential Manager (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → TA505 (50 neighbors, 50 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → KeyBoy (19 neighbors, 19 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [80/100] retrieved=145 relevant=4 latency=6176ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 2 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายหลบ...
[RETRIEVE] Query: เมื่อวันที่ 2 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายหลบ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Operation Wocao (0.476), APT3 (0.285), Indicator Removal (0.021), Indicator Removal from Tools (0.020), Bypass User Account Control (0.001), Disable or Modify Tools (0.000), User Account Control (0.000), Clear Windows Event Logs (0.000), User Account Control (0.000), Multi-factor Authentication (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Operation Wocao (79 neighbors, 79 edges)
           → Indicator Removal from Tools (20 neighbors, 20 edges)
           → APT3 (50 neighbors, 50 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [81/100] retrieved=105 relevant=3 latency=4547ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 19 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร...
[RETRIEVE] Query: เมื่อวันที่ 19 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Gamaredon Group (0.064), POWRUNER (0.062), APT-C-36 (0.016), Ursnif (0.002), APT-C-36 (0.002), Ingress Tool Transfer (0.001), Exfiltration (0.000), Internal Spearphishing (0.000), Archive via Utility (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Gamaredon Group (76 neighbors, 76 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → POWRUNER (21 neighbors, 21 edges)
           → Domain Groups (41 neighbors, 41 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [82/100] retrieved=505 relevant=4 latency=4176ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 24 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนที่คนร...
[RETRIEVE] Query: เมื่อวันที่ 24 พฤศจิกายน 2566 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนที่คนร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.044), VERMIN (0.027), VERMIN (0.011), APT-C-36 (0.005), Ursnif (0.001), File Deletion (0.000), Internal Spearphishing (0.000), Password Managers (0.000), Credentials In Files (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → VERMIN (17 neighbors, 17 edges)
           → System Owner/User Discovery (243 neighbors, 243 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [83/100] retrieved=306 relevant=3 latency=8879ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 15 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุ...
[RETRIEVE] Query: เมื่อวันที่ 15 มิถุนายน 2567 ห้างสรรพสินค้าแห่งหนึ่งแจ้งความเพิ่มเติมว่าการบุกรุ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.045), Bankshot (0.017), FIN8 (0.001), User Account Management (0.000), Password Managers (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Software Discovery (0.000), Account Use Policies (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → File and Directory Discovery (371 neighbors, 371 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [84/100] retrieved=693 relevant=3 latency=3771ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 19 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งความเพิ่มเติมว่าพบกา...
[RETRIEVE] Query: เมื่อวันที่ 19 กรกฎาคม 2567 การไฟฟ้าส่วนภูมิภาคสาขาหนึ่งแจ้งความเพิ่มเติมว่าพบกา...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: BackConfig (0.013), APT37 (0.010), Data from Local System (0.006), Remote System Discovery (0.003), Data from Network Shared Drive (0.002), FIN8 (0.000), System Network Connections Discovery (0.000), Exfiltration to Text Storage Sites (0.000), Cloud Accounts (0.000), Pikabot (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → BackConfig (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → APT37 (42 neighbors, 42 edges)
           → Data from Local System (232 neighbors, 232 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [85/100] retrieved=559 relevant=4 latency=2522ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 20 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าถูกหลอกให้ติดตั้งโปร...
[RETRIEVE] Query: เมื่อวันที่ 20 กุมภาพันธ์ 2564 ผู้เสียหายรายหนึ่งแจ้งความว่าถูกหลอกให้ติดตั้งโปร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pikabot (0.021), Clambling (0.018), CoinTicker (0.015), EventBot (0.008), Encrypted/Encoded File (0.004), Symmetric Cryptography (0.003), Exfiltration Over Symmetric Encrypted Non-C2 Protocol (0.003), Lucifer (0.002), Deobfuscate/Decode Files or Information (0.002), Subvert Trust Controls (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Pikabot (24 neighbors, 24 edges)
           → Symmetric Cryptography (188 neighbors, 188 edges)
           → Clambling (35 neighbors, 35 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [86/100] retrieved=360 relevant=3 latency=8286ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 17 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงช่องทางที่...
[RETRIEVE] Query: เมื่อวันที่ 17 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงช่องทางที่...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Leviathan Australian Intrusions (0.311), Threat Group-3390 (0.111), External Remote Services (0.052), Valid Accounts (0.031), Remote Services (0.017), Remote Desktop Protocol (0.005), User Account Management (0.000), Exploitation of Remote Services (0.000), Remote Service Session Hijacking (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Leviathan Australian Intrusions (27 neighbors, 27 edges)
           → Valid Accounts (82 neighbors, 82 edges)
           → Threat Group-3390 (81 neighbors, 81 edges)
           → External Remote Services (52 neighbors, 52 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [87/100] retrieved=181 relevant=5 latency=3567ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 16 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความเพิ่มเติมถึงจุดเริ่มต้นที่ลูกค...
[RETRIEVE] Query: เมื่อวันที่ 16 มีนาคม 2564 ธนาคารแห่งหนึ่งแจ้งความเพิ่มเติมถึงจุดเริ่มต้นที่ลูกค...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Pony (0.403), SYSCON (0.110), User Training (0.073), User Execution (0.049), Malicious File (0.046), User Training (0.033), Malicious Link (0.013), Spearphishing Link (0.008), Encrypted/Encoded File (0.000), Exploitation for Client Execution (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Pony (16 neighbors, 16 edges)
           → Malicious Link (93 neighbors, 93 edges)
           → SYSCON (6 neighbors, 6 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [88/100] retrieved=238 relevant=3 latency=4189ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 13 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Query: เมื่อวันที่ 13 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้า...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Storm-1811 (0.045), POWERSTATS (0.033), POWERSTATS (0.030), FIN7 (0.007), PowerShell Profile (0.006), POWERSOURCE (0.003), Forced Authentication (0.000), PowerShell (0.000), Disable or Remove Feature or Program (0.000), Input Injection (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → Storm-1811 (38 neighbors, 38 edges)
           → Input Capture (20 neighbors, 20 edges)
           → POWERSTATS (28 neighbors, 28 edges)
           → PowerShell (241 neighbors, 241 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [89/100] retrieved=295 relevant=3 latency=3164ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงเครื่องมือ...
[RETRIEVE] Query: เมื่อวันที่ 18 ธันวาคม 2566 บริษัทค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมถึงเครื่องมือ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Axiom (0.461), HOMEFRY (0.405), Suckfly (0.318), OS Credential Dumping (0.221), BlackByte (0.218), Windows Credential Editor (0.205), Credential Access (0.014), Credential Access Protection (0.004), Credential Stuffing (0.001), Credentials In Files (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Axiom (24 neighbors, 24 edges)
           → OS Credential Dumping (39 neighbors, 39 edges)
           → HOMEFRY (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [90/100] retrieved=56 relevant=4 latency=2395ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 6 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Query: เมื่อวันที่ 6 ตุลาคม 2566 หน่วยงานด้านความมั่นคงแห่งหนึ่งแจ้งความว่าเครื่องคอมพิ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.014), Seth-Locker (0.013), Clambling (0.012), Clambling (0.009), Ursnif (0.005), APT-C-36 (0.002), Subvert Trust Controls (0.000), Internal Spearphishing (0.000), Data Encrypted for Impact (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → Clambling (35 neighbors, 35 edges)
           → Malicious File (202 neighbors, 202 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [91/100] retrieved=269 relevant=3 latency=3184ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 3 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายได้...
[RETRIEVE] Query: เมื่อวันที่ 3 ธันวาคม 2563 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงวิธีที่คนร้ายได้...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT38 (0.513), APT28 (0.454), Password Spraying (0.288), CrackMapExec (0.233), APT3 (0.222), Brute Force (0.095), Password Cracking (0.042), Password Managers (0.003), Credentials from Web Browsers (0.002), Password Policy Discovery (0.001)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT38 (62 neighbors, 62 edges)
           → Brute Force (34 neighbors, 34 edges)
           → APT28 (124 neighbors, 124 edges)
           → Password Spraying (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [92/100] retrieved=172 relevant=4 latency=8350ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 18 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความเพิ่มเติมถึงข้อมู...
[RETRIEVE] Query: เมื่อวันที่ 18 มกราคม 2567 หน่วยงานรัฐวิสาหกิจแห่งหนึ่งแจ้งความเพิ่มเติมถึงข้อมู...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: DRYHOOK (0.144), MuddyWater (0.115), njRAT (0.080), Lokibot (0.004), Unsecured Credentials (0.003), FIN8 (0.000), Gamaredon Group (0.000), Named Pipe Metadata (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → DRYHOOK (11 neighbors, 11 edges)
           → MuddyWater (89 neighbors, 89 edges)
           → Credentials In Files (44 neighbors, 44 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [93/100] retrieved=116 relevant=3 latency=3226ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 14 ตุลาคม 2564 การประปาส่วนภูมิภาคสาขาหนึ่งแจ้งความว่าระบบควบคุมการผ...
[RETRIEVE] Query: เมื่อวันที่ 14 ตุลาคม 2564 การประปาส่วนภูมิภาคสาขาหนึ่งแจ้งความว่าระบบควบคุมการผ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: MuddyWater (0.002), SMS Pumping (0.000), CharmPower (0.000), ccf32 (0.000), BendyBear (0.000), Fysbis (0.000), Samurai (0.000), Supply Chain Compromise (0.000), Data Encoding (0.000), Standard Encoding (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → MuddyWater (89 neighbors, 89 edges)
           → Ingress Tool Transfer (519 neighbors, 519 edges)
           → SMS Pumping (4 neighbors, 4 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [94/100] retrieved=585 relevant=2 latency=2997ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 20 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนสุ...
[RETRIEVE] Query: เมื่อวันที่ 20 ธันวาคม 2566 หน่วยงานราชการแห่งหนึ่งแจ้งความเพิ่มเติมถึงขั้นตอนสุ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT-C-36 (0.070), admin@338 (0.008), APT-C-36 (0.007), File Deletion (0.004), Wingbird (0.004), Ursnif (0.002), Ingress Tool Transfer (0.001), System Script Proxy Execution (0.000), Internal Spearphishing (0.000), Shortcut Modification (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → APT-C-36 (47 neighbors, 47 edges)
           → Remcos (43 neighbors, 43 edges)
           → admin@338 (19 neighbors, 19 edges)
           → System Information Discovery (426 neighbors, 426 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [95/100] retrieved=497 relevant=4 latency=3082ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 25 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งแจ้งความเพิ่มเติมถึงพฤติกร...
[RETRIEVE] Query: เมื่อวันที่ 25 กุมภาพันธ์ 2565 สถาบันการศึกษาแห่งหนึ่งแจ้งความเพิ่มเติมถึงพฤติกร...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: APT18 (0.135), Obfuscated Files or Information (0.009), Adversary-in-the-Middle (0.004), Masquerade File Type (0.003), ARP Cache Poisoning (0.002), Evil Twin (0.001), Magic Hound (0.001), Threat Group-3390 (0.000), Right-to-Left Override (0.000), BackConfig (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → APT18 (17 neighbors, 17 edges)
           → System Information Discovery (426 neighbors, 426 edges)
           → Obfuscated Files or Information (183 neighbors, 183 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [96/100] retrieved=515 relevant=3 latency=3661ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 25 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดการเ...
[RETRIEVE] Query: เมื่อวันที่ 25 มิถุนายน 2565 หน่วยงานแห่งหนึ่งแจ้งความเพิ่มเติมถึงรายละเอียดการเ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: TA505 (0.040), Daggerfly (0.018), zwShell (0.011), ZxShell (0.011), Netwalker (0.002), RDP Hijacking (0.001), Remote Desktop Protocol (0.001), POWERSOURCE (0.000), Forced Authentication (0.000), PowerShell (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → TA505 (50 neighbors, 50 edges)
           → PowerShell (241 neighbors, 241 edges)
           → Daggerfly (23 neighbors, 23 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [97/100] retrieved=292 relevant=6 latency=8871ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 22 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าโปรแกรมเรียก...
[RETRIEVE] Query: เมื่อวันที่ 22 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าโปรแกรมเรียก...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: NotPetya (0.008), Wizard Spider (0.000), FIN8 (0.000), Exploitation of Remote Services (0.000), Pikabot (0.000), Hijack Execution Flow (0.000), Scheduled Task/Job (0.000), Filter Network Traffic (0.000), Process Discovery (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 4 subgraphs
           → NotPetya (15 neighbors, 15 edges)
           → Windows Management Instrumentation (153 neighbors, 153 edges)
           → Wizard Spider (86 neighbors, 86 edges)
           → Windows Remote Management (16 neighbors, 16 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 4 subgraphs from 1 queries
  [98/100] retrieved=230 relevant=3 latency=5309ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 22 กันยายน 2563 ผู้เสียหายหลายรายแจ้งความว่าบัญชีผู้ใช้งานออนไลน์ของ...
[RETRIEVE] Query: เมื่อวันที่ 22 กันยายน 2563 ผู้เสียหายหลายรายแจ้งความว่าบัญชีผู้ใช้งานออนไลน์ของ...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Crimson (0.259), njRAT (0.200), LAPSUS$ (0.072), Malicious File (0.069), User Execution (0.046), Execution Prevention (0.013), Lokibot (0.009), Malicious Link (0.003), Exploitation for Client Execution (0.000), Compromise Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Crimson (32 neighbors, 32 edges)
           → Credentials from Web Browsers (97 neighbors, 97 edges)
           → njRAT (40 neighbors, 40 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [99/100] retrieved=145 relevant=3 latency=8819ms
[RETRIEVE-QUOTA] Query 1/1: เมื่อวันที่ 7 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าก่อนเกิดเหตุม...
[RETRIEVE] Query: เมื่อวันที่ 7 พฤษภาคม 2567 ห้างค้าปลีกแห่งหนึ่งแจ้งความเพิ่มเติมว่าก่อนเกิดเหตุม...
[RETRIEVE] Vector search: 10 results (pre-rerank)
[RERANKER] Top-10 after reranking: Bankshot (0.014), POWRUNER (0.001), Domain Properties (0.000), FIN8 (0.000), Search Victim-Owned Websites (0.000), Domain Registration (0.000), Exfiltration to Text Storage Sites (0.000), Scan Databases (0.000), Pikabot (0.000), Cloud Accounts (0.000)
[RETRIEVE] Graph expansion: 3 subgraphs
           → Bankshot (26 neighbors, 26 edges)
           → Domain Account (65 neighbors, 65 edges)
           → POWRUNER (21 neighbors, 21 edges)
[RETRIEVE-QUOTA] 3 vectors (quota 3/query), 3 subgraphs from 1 queries
  [100/100] retrieved=96 relevant=5 latency=3662ms

============================================================
  Retriever: Hybrid+Quota (decompose)  (100 samples)
============================================================
  Metric                    @1      @3      @5     @10
  ────────────────────────────────────────────────────
  Hit                    0.520   0.710   0.720   0.730
  Recall (capped)        0.520   0.288   0.260   0.288
  Precision              0.520   0.287   0.180   0.100
  NDCG                   0.520   0.341   0.314   0.324

  Attack-chain samples: 100 (343 scoreable steps, 4 unscoreable)
  StepCoverage           0.164   0.262   0.274   0.305
  StepCoverage strict    0.129   0.222   0.233   0.265
    by cue: described    0.059   0.141   0.159   0.186
    by cue: named        0.705   0.831   0.831   0.857

  MRR                    0.617
  MAP                    0.238
  Avg Latency (ms)      4103.2


════════════════════════════════════════════════════════════
  EVALUATION COMPLETE
════════════════════════════════════════════════════════════
