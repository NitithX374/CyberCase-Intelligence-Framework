# Value check: every flagged claim on the three stored reading sets (2026-10-05)

Local file, not committed: for the owner's check sheet. The texts are public news.

Produced by `backend/app/trace/value_check.py` (branch `feat/value-check`, stacked on #66) re-binding the three stored
reading sets with the production binder, the real checkpoint in float32, the narrowed minus rule, and no time limit.
A flag is a review suggestion from a rule and an NLI model, not a finding. Rate of flags is not precision.

## English confirmation

Cases 100; numeric claims with a located quote 457; V0 394, V1 23, V2 35, V3 5; checked 60; possible_conflict 0; support_uncertain 31; skipped too_long 3.

### English confirmation 1: case 10032 A-07 (V2, neutral -> support_uncertain)

- Claim: A hacker group known as the Shadow Brokers released a set of exploits on April 14.
- Missing numbers: 14
- Quote text: when a hacker group known as the Shadow Brokers released a set of exploits
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 2: case 10052 A-02 (V2, neutral -> support_uncertain)

- Claim: APT10 attacks companies by targeting their suppliers.
- Missing numbers: 10
- Quote text: Advanced Persistent Threat group linked to China said to be attacking companies by targeting their suppliers
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 3: case 10052 A-03 (V2, neutral -> support_uncertain)

- Claim: APT10 is thought to target managed service providers to access client companies and facilitate intellectual property theft.
- Missing numbers: 10
- Quote text: A Chinese hacking group is thought to be behind attacks on managed service providers as a way into their client companies, to facilitate the theft of intellectual property.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 4: case 10052 A-05 (V2, neutral -> support_uncertain)

- Claim: Once access is gained, APT10 uses the company's credentials to attack client companies.
- Missing numbers: 10
- Quote text: Once inside, they used the company's credentials to attack their client companies.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 5: case 10052 A-11 (V2, neutral -> support_uncertain)

- Claim: The APT10 campaign is thought to have launched in 2014.
- Missing numbers: 10
- Quote text: It is thought the group launched the campaign in 2014
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 6: case 10052 A-12 (V2, neutral -> support_uncertain)

- Claim: APT10 significantly ramped up its campaign in early 2016.
- Missing numbers: 10
- Quote text: and then significantly ramped it up in early 2016
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 7: case 10052 A-14 (V2, neutral -> support_uncertain)

- Claim: APT10 has exfiltrated a high volume of data from multiple victims.
- Missing numbers: 10
- Quote text: The group is known to have exfiltrated a high volume of data from multiple victims
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 8: case 10052 A-16 (V2, neutral -> support_uncertain)

- Claim: Japanese organisations were targeted in a separate, simultaneous campaign by APT10.
- Missing numbers: 10
- Quote text: A number of Japanese organisations have also been targeted directly in a separate, simultaneous campaign by the same group
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 9: case 10239 A-07 (V3, neutral -> support_uncertain)

- Claim: $22,000 was transferred on August 17.
- Missing numbers: 17
- Quote text: Another $22,000 were transferred seven days later.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 10: case 10380 A-04 (V1, neutral -> support_uncertain)

- Claim: The 2015 breach resulted in a "tremendous loss of consumer trust" and violated the discretion users relied on.
- Missing numbers: 2015
- Quote text: Even Maglieri says the company suffered a “tremendous loss of consumer trust,” and “users relied on discretion using the service, and that discretion was violated.”
- Added sentence: Matthew Maglieri faced more than a challenge when he agreed to become the chief information security officer for Ruby Life Inc., parent of the Toronto-based Ashley Madison and other dating sites which in 2015 saw hackers release records of some 36 million members, plus application code and corporate email.
- Problem? (yes / no): 

### English confirmation 11: case 119 A-01 (V2, neutral -> support_uncertain)

- Claim: In 2016, hackers stole millions of username and password combinations from various online services.
- Missing numbers: 2016
- Quote text: They stole millions of username and password combinations from online services of all shapes and sizes.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 12: case 119 A-02 (V2, neutral -> support_uncertain)

- Claim: In 2016, blogs and discussion forums were particularly hard hit by credential theft.
- Missing numbers: 2016
- Quote text: Blogs and discussion forums were hit particularly hard.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 13: case 1879 A-16 (V2, neutral -> support_uncertain)

- Claim: The Fancy Bear phishing scheme sidesteps 2-step verification by tricking users into granting access through a fake Google security app.
- Missing numbers: 2
- Quote text: However, the phishing scheme from Fancy Bear manages to sidestep this security measure, by tricking users into granting access through the fake Google security app.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 14: case 2104 A-06 (V2, neutral -> support_uncertain)

- Claim: SS7 is a protocol that specifies how public switched telephone networks (PSTN) exchange data over digital signaling networks.
- Missing numbers: 7
- Quote text: It’s a protocol that specifies how public switched telephone networks (PSTN) exchange data over digital signaling network.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 15: case 2104 A-07 (V2, neutral -> support_uncertain)

- Claim: Researchers Tobias Engel and Karsten Nohl discovered flaws in the SS7 protocol in 2014.
- Missing numbers: 7
- Quote text: That’s what researchers Tobias Engel and Karsten Nohl found back in 2014.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 16: case 22 A-07 (V2, neutral -> support_uncertain)

- Claim: For the January 2016 Indian bank and pharmaceutical company infections, the attacker asked for 1 bitcoin (approximately $905) per infected computer.
- Missing numbers: 2016
- Quote text: The attacker asked for 1 bitcoin (about $905) for each infected computer, and then used unprotected desktop interface to infect other connected computers from remote.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 17: case 22 A-08 (V2, neutral -> support_uncertain)

- Claim: In the January 2016 Indian infections, the attacker used an unprotected desktop interface to infect other connected computers remotely.
- Missing numbers: 2016
- Quote text: The attacker asked for 1 bitcoin (about $905) for each infected computer, and then used unprotected desktop interface to infect other connected computers from remote.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 18: case 22 A-17 (V2, neutral -> support_uncertain)

- Claim: Locky ransomware began spreading via email in mid-February 2016.
- Missing numbers: 2016
- Quote text: In the mid-February, a new ransomware “Locky” started to spread out via email.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 19: case 22 A-24 (V2, neutral -> support_uncertain)

- Claim: Most malware in the October 2016 Hong Kong attacks was hidden in email attachments disguised as bills or receipts to trick users into clicking.
- Missing numbers: 2016
- Quote text: Most of the malware were hidden in email attachments and disguised as bills or receipts to trick users to click.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 20: case 2602 A-24 (V2, neutral -> support_uncertain)

- Claim: The attackers may have used the name "Tsar Team" to add weight to their demands because the target is unusual for APT28.
- Missing numbers: 28
- Quote text: it’s possible that these attackers have simply used the name to add weight to their demands.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 21: case 2625 A-10 (V1, neutral -> support_uncertain)

- Claim: OneLogin staff was alerted of unusual database activity around 9 am PST on May 31, 2017.
- Missing numbers: 31, 2017
- Quote text: OneLogin staff was alerted of unusual database activity around 9 am PST
- Added sentence: Evidence shows the attack started on May 31, 2017 around 2 am PST.
- Problem? (yes / no): 

### English confirmation 22: case 326 A-10 (V2, neutral -> support_uncertain)

- Claim: Hacker #2 reached out via Twitter a few hours after Hacker #1.
- Missing numbers: 2, 1
- Quote text: A second hacker reached out via Twitter a few hours later
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 23: case 326 A-11 (V2, neutral -> support_uncertain)

- Claim: Hacker #2's contact confirmed that he and Hacker #1 knew each other.
- Missing numbers: 2, 1
- Quote text: was surprised to find out that his colleague already shared the PasteBin link, confirming they knew each other.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 24: case 326 A-13 (V2, neutral -> support_uncertain)

- Claim: The demo provided by Hacker #2 used methods specific to how hackers demonstrate responsibility for DDoS attacks.
- Missing numbers: 2
- Quote text: The demo was specific with how hackers demonstrate they are behind DDoS attacks.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 25: case 83 A-02 (V2, neutral -> support_uncertain)

- Claim: Harak1r1's method involved exporting database content and replacing all tables with a single table named WARNING containing a ransom note.
- Missing numbers: 1, 1
- Quote text: The group was exporting the database's content and replacing all tables with one named WARNING, that contained a ransom note
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 26: case 83 A-05 (V2, neutral -> support_uncertain)

- Claim: 11 victims paid the ransom to Harak1r1 to recover their files.
- Missing numbers: 1, 1
- Quote text: 11 victims have paid the ransom in order to recover their files.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 27: case 83 A-08 (V2, neutral -> support_uncertain)

- Claim: Two copycat groups appeared after Harak1r1's attacks: 0wn3d and 0704341626asdf.
- Missing numbers: 1, 1
- Quote text: two copycats appeared and started doing the same. The second group goes by the name of 0wn3d A day later, the same Gevers came across a third actor, using the name 0704341626asdf
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 28: case 83 A-10 (V2, neutral -> support_uncertain)

- Claim: The group 0wn3d has hijacked just over 930 databases.
- Missing numbers: 0, 3
- Quote text: this second group has hijacked just over 930 databases.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 29: case 83 A-11 (V2, neutral -> support_uncertain)

- Claim: 0wn3d's ransom demand is 0.5 Bitcoin, which is approximately $500.
- Missing numbers: 0, 3
- Quote text: Unlike Harak1r1, this second group is a little bit more greedy and asks for 0.5 Bitcoin, which is around $500
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 30: case 863 A-06 (V2, neutral -> support_uncertain)

- Claim: The forged cookies used in 2015 and 2016 were connected to the same nation-sponsored attackers who compromised Yahoo in 2014.
- Missing numbers: 2015, 2016
- Quote text: The investigators said some of the forgeries were connected to the same nation-sponsored attackers who compromised Yahoo in 2014.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation 31: case 863 A-11 (V2, neutral -> support_uncertain)

- Claim: Following the 2014 incidents, the company notified 26 specific users and consulted with law enforcement.
- Missing numbers: 2014
- Quote text: The Company took certain remedial actions, notifying 26 specifically targeted users and consulting with law enforcement.
- Added sentence: -
- Problem? (yes / no): 

### English confirmation: not checked, pair over 512 tokens

- case 10053 A-15 (V1, skipped too_long): APT10's work demonstrates a pattern in line with China Standard Time (UTC+8).
- case 10053 A-16 (V1, skipped too_long): APT10 targets specific commercial enterprises "closely aligned with strategic Chinese interests".
- case 2224 A-08 (V1, skipped too_long): SLocker accounted for 22 per cent of Android malware threats in the UK during the second half of 2015.

## English development

Cases 99; numeric claims with a located quote 399; V0 347, V1 19, V2 31, V3 2; checked 51; possible_conflict 0; support_uncertain 23; skipped too_long 1.

### English development 1: case 10035 A-22 (V2, neutral -> support_uncertain)

- Claim: The 2014 breach compromised 500 million accounts.
- Missing numbers: 2014
- Quote text: which compromised 500 million accounts.
- Added sentence: -
- Problem? (yes / no): 

### English development 2: case 10051 A-02 (V2, neutral -> support_uncertain)

- Claim: APT10 is a Chinese hacking group with advanced cyber-espionage capabilities.
- Missing numbers: 10
- Quote text: A Chinese hacking group with advanced cyber-espionage capabilities has been targeting managed IT services providers across the globe in a campaign to steal sensitive data.
- Added sentence: -
- Problem? (yes / no): 

### English development 3: case 10051 A-03 (V2, neutral -> support_uncertain)

- Claim: APT10 targets managed IT services providers (MSPs) globally to steal sensitive data.
- Missing numbers: 10
- Quote text: A Chinese hacking group with advanced cyber-espionage capabilities has been targeting managed IT services providers across the globe in a campaign to steal sensitive data.
- Added sentence: -
- Problem? (yes / no): 

### English development 4: case 10051 A-04 (V2, neutral -> support_uncertain)

- Claim: APT10 uses phishing and customized malware to infect machines and gain access to IT providers and customer networks.
- Missing numbers: 10
- Quote text: The cybercriminal gang is using sophisticated phishing attacks and customised malware in order to infect victims' machines and then gain access to IT providers and their customer networks.
- Added sentence: -
- Problem? (yes / no): 

### English development 5: case 10051 A-09 (V2, neutral -> support_uncertain)

- Claim: APT10 was behind the Poison Ivy malware family.
- Missing numbers: 10
- Quote text: The group was behind the Poison Ivy malware family and has evolved its operations to include using custom tools capable of compromising high volumes of data from organisations and their customers, and stealthily moving it around the world.
- Added sentence: -
- Problem? (yes / no): 

### English development 6: case 10051 A-19 (V2, neutral -> support_uncertain)

- Claim: APT10 has targeted organizations in the US, Canada, the UK, France, Switzerland, Scandinavia, South Africa, India, and Australia.
- Missing numbers: 10
- Quote text: Using this approach, the group has been able to target organisations in the US, Canada, the UK, France, Switzerland, Scandinavia, South Africa, India, and Australia.
- Added sentence: -
- Problem? (yes / no): 

### English development 7: case 10314 A-17 (V2, neutral -> support_uncertain)

- Claim: Ralph Echemendia believes the April 19 payment was linked to the Atlanta attack as a way for federal agents to connect the breach to the defendants.
- Missing numbers: 19
- Quote text: Ralph Echemendia thinks the payment was associated with the Atlanta attack because it would be one way that federal agents connected the breach to Savanda and Mansouri.
- Added sentence: -
- Problem? (yes / no): 

### English development 8: case 1071 A-10 (V2, neutral -> support_uncertain)

- Claim: The drive included completed national security clearance applications (SF86) for two US four-star generals.
- Missing numbers: 86
- Quote text: Among the most damaging documents on the drive included the completed applications for renewed national security clearances for two US four-star generals
- Added sentence: -
- Problem? (yes / no): 

### English development 9: case 1093 A-02 (V2, neutral -> support_uncertain)

- Claim: The 13 applications targeted Instagram users looking to manage or boost their follower counts.
- Missing numbers: 13
- Quote text: These apps, as stated by ESET, target Instagram users who are wanting to either manage or boost the number of followers.
- Added sentence: -
- Problem? (yes / no): 

### English development 10: case 1734 A-03 (V2, neutral -> support_uncertain)

- Claim: The breach occurred between September 29 and December 29, 2016.
- Missing numbers: 2016
- Quote text: were affected between September 29 and December 29 last year.
- Added sentence: -
- Problem? (yes / no): 

### English development 11: case 1913 A-23 (V2, neutral -> support_uncertain)

- Claim: DD4BC and Armada Collective targeted companies worldwide in the summer and autumn of 2015.
- Missing numbers: 4
- Quote text: These two groups appeared in the summer and autumn of 2015 and targeted companies worldwide.
- Added sentence: -
- Problem? (yes / no): 

### English development 12: case 1913 A-25 (V1, neutral -> support_uncertain)

- Claim: Both DD4BC and Armada Collective became inactive following the arrests in January 2016.
- Missing numbers: 4, 2016
- Quote text: Following the arrests, both groups became inactive.
- Added sentence: In January 2016, Europol arrested suspects believed to be DD4BC members in Bosnia and Herzegovina.
- Problem? (yes / no): 

### English development 13: case 1913 A-26 (V2, neutral -> support_uncertain)

- Claim: A wave of copycat groups followed the demise of DD4BC and Armada Collective.
- Missing numbers: 4
- Quote text: After the demise of these two main groups, there was a wave of copycats
- Added sentence: -
- Problem? (yes / no): 

### English development 14: case 2044 A-10 (V2, neutral -> support_uncertain)

- Claim: The S3 buckets were left online without requiring authentication.
- Missing numbers: 3
- Quote text: They were specifically hunting for buckets that had been left online but required no authentication.
- Added sentence: -
- Problem? (yes / no): 

### English development 15: case 2780 A-12 (V2, neutral -> support_uncertain)

- Claim: Cyberpunk 2077 does not currently have a release date.
- Missing numbers: 2077
- Quote text: but doesn't have a release date at this point.
- Added sentence: -
- Problem? (yes / no): 

### English development 16: case 2901 A-17 (V2, neutral -> support_uncertain)

- Claim: Morphisec researchers believe FIN7 is responsible for attacks on 140+ banks and other businesses earlier this year.
- Missing numbers: 7
- Quote text: Morphisec researchers believe that the series of attacks leveraged against 140+ banks and other businesses earlier this year is also their work.
- Added sentence: -
- Problem? (yes / no): 

### English development 17: case 2901 A-19 (V2, neutral -> support_uncertain)

- Claim: It is unknown whether FIN7 and the Carbanak gang are the same group.
- Missing numbers: 7
- Quote text: but whether they are one and the same it’s still impossible to say for sure.
- Added sentence: -
- Problem? (yes / no): 

### English development 18: case 575 A-02 (V2, neutral -> support_uncertain)

- Claim: Some researchers state that cybercriminals received over $1 billion in ransom payments in 2016.
- Missing numbers: 2016
- Quote text: some researchers state that cybercriminals received over $1 billion in ransom payments last year.
- Added sentence: -
- Problem? (yes / no): 

### English development 19: case 575 A-05 (V2, neutral -> support_uncertain)

- Claim: The highest year-on-year ransomware growth in 2016 was seen in technology (218%), utilities and energy (112%), and banking (93%).
- Missing numbers: 2016
- Quote text: Technology (218%), utilities and energy (112%) and banking (93%) saw the highest year-on-year ransomware growth last year.
- Added sentence: -
- Problem? (yes / no): 

### English development 20: case 581 A-08 (V2, neutral -> support_uncertain)

- Claim: W-2 forms contain personal financial information, including taxpayer ID and annual employee pay.
- Missing numbers: 2
- Quote text: that has a wealth of personal financial information, including taxpayer ID and how much an employee was paid in a year.
- Added sentence: -
- Problem? (yes / no): 

### English development 21: case 67 A-06 (V2, neutral -> support_uncertain)

- Claim: Ransomware was on track to generate nearly $1 billion in payments in 2016.
- Missing numbers: 2016
- Quote text: putting ransomware on track to rake in nearly $1 billion this year.
- Added sentence: -
- Problem? (yes / no): 

### English development 22: case 865 A-19 (V2, neutral -> support_uncertain)

- Claim: The intrusion responsible for the 2013 theft has not been identified.
- Missing numbers: 2013
- Quote text: We have not been able to identify the intrusion associated with this theft
- Added sentence: -
- Problem? (yes / no): 

### English development 23: case 865 A-20 (V2, neutral -> support_uncertain)

- Claim: The 2013 breach is believed to be a distinct incident from the 2014 security incident.
- Missing numbers: 2013
- Quote text: we believe this incident is likely distinct from the 2014 Security Incident
- Added sentence: -
- Problem? (yes / no): 

### English development: not checked, pair over 512 tokens

- case 10130 A-15 (V1, skipped too_long): Unit 42 could not conclude that the MuddyWater group was behind the Saudi attacks described by the NCSC.

## Thai clean

Cases 98; numeric claims with a located quote 756; V0 676, V1 37, V2 27, V3 16; checked 80; possible_conflict 6; support_uncertain 29; skipped too_long 0.

### Thai clean 1: case r121041 A-07 (V2, neutral -> support_uncertain)

- Claim: ในคำพิพากษาฎีกาที่ 16412/2555 จำเลยมีความผิดฐานพยายามฆ่าเนื่องจากละเลยไม่ช่วยเหลือคู่รักที่ประสบอุบัติเหตุซึ่งถือเป็นหน้าที่ที่เกิดจากการกระทำครั้งก่อนของจำเลย
- Missing numbers: 16412, 2555
- Quote text: การกระทำเช่นนี้ถือเป็นหน้าที่อันเกิดจากการกระทำครั้งก่อนของจำเลยเอง ที่พาสาวคนรักมาเที่ยวแล้วเกิดอุบัติเหตุ ถือว่า เกิดหน้าที่ต้องช่วย ต้องดูแลสาวคนรัก ถ้าไม่ช่วยถือเป็นการงดเว้น ซึ่งคดีนี้ศาลเห็นว่าการกระทำดังกล่าวของจำเลยเล็งเห็นผล เพราะการงดเว้นไม่ให้ความช่วยเหลือสาวคนรักอาจทำให้มีอันตรายถึงแก่ความตายได้
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 2: case r121222 A-01 (V2, neutral -> support_uncertain)

- Claim: พบศพ น.ส.ศิริวรรณ หรือวา วงษ์ประเสริฐ อายุ 32 ปี เสียชีวิตภายในห้องพักเลขที่ 179/9 อาคาร 29 แฟลตบ้านเอื้ออาทร ถนนปัญญารามอินทรา กรุงเทพฯ
- Missing numbers: 179, 9, 29
- Quote text: พบศพ น.ส.ศิริวรรณ หรือวา วงษ์ประเสริฐ อายุ 32 ปี ที่อยู่ตามบัตรประชาชนเดียวกับเลขที่ห้องเกิดเหตุ
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 3: case r130890 A-03 (V1, neutral -> support_uncertain)

- Claim: เหตุเกิดเมื่อเวลา 01.20 น. วันที่ 8 พ.ค. 61
- Missing numbers: 61
- Quote text: เมื่อเวลา 01.20 น. วันที่ 8 พ.ค.
- Added sentence: 61 ที่สน.นางเลิ้ง พล.ต.ต.
- Problem? (yes / no): 

### Thai clean 4: case r130890 A-06 (V2, neutral -> support_uncertain)

- Claim: นายธนธรณ์ถูกจับกุมในซอยพิษณุโลก 3 เมื่อวันที่ 17 พ.ค. 61
- Missing numbers: 3, 61
- Quote text: กระทั่งถูกจับกุมในซอยดังกล่าวเมื่อวันที่ 17 พ.ค.ที่ผ่านมา
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 5: case r146696 A-17 (V3, neutral -> support_uncertain)

- Claim: โทษตามมาตรา 15 คือจำคุก 5 ปี และปรับไม่เกิน 50,000 บาท
- Missing numbers: 15, 50,000
- Quote text: มีโทษจำคุก 5 ปี และปรับไม่เกิน 50000 บาท
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 6: case r169149 A-08 (V2, contradiction -> possible_conflict)

- Claim: นายธีรวัฒน์อ้างว่าได้ส่งนายอ่ำกลับประเทศลาวไปตั้งแต่วันที่ 10 มิ.ย. 2563
- Missing numbers: 2563
- Quote text: ส่วนนายอ่ำ ลูกจ้างชาวลาวอีกคนตนได้ส่งกลับบ้านประเทศลาวไปตั้งแต่วันเกิดเหตุเมื่อ 10 มิ.ย.ที่ผ่านมาแล้ว
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 7: case r17505 A-02 (V2, neutral -> support_uncertain)

- Claim: หญิงวัย 18 ปี ลาออกจากการเป็นนักศึกษาชั้นปีที่ 1 ของมหาวิทยาลัยเชียงใหม่
- Missing numbers: 18
- Quote text: ลาออกจากการเป็นนักศึกษาชั้นปี 1 ของมหาวิทยาลัยเชียงใหม่เมื่อวานนี้วันนี้ (9 ส.ค.2561)
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 8: case r17505 A-04 (V2, neutral -> support_uncertain)

- Claim: การชี้แจงดังกล่าวเกิดขึ้นจากการเปิดพรีออร์เดอร์สินค้าเมื่อเดือน พ.ค. 2561
- Missing numbers: 2561
- Quote text: การชี้แจงดังกล่าวเกิดขึ้นจากการเปิดพรีออร์เดอร์สินค้าเมื่อเดือน พ.ค.ที่ผ่านมา
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 9: case r204801 A-16 (V2, neutral -> support_uncertain)

- Claim: จากการตรวจค้นบ้านเลขที่ 128/2 ม.8 ต.สัตหีบ พบกัญชาชนิดอบแห้งจำนวน 10 ห่อ
- Missing numbers: 128, 2, 8
- Quote text: และกัญชาชนิดอบแห้ง จำนวน 10 ห่อ
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 10: case r21039 A-07 (V1, contradiction -> possible_conflict)

- Claim: เวลา 18.33 น. มีรายงานผู้เสียชีวิต 9 คน และบาดเจ็บหลายคน
- Missing numbers: 18.33
- Quote text: ผู้ก่อเหตุคือ จ.ส.อ.จักรพันธ์ ถมมา ใช้อาวุธสงคราม กราดยิงประชาชนเสียชีวิต 9 คน และบาดเจ็บหลายคน
- Added sentence: หลายคนเวลา 16.30 น. ผู้ก่อเหตุหลบหนีเข้าไปในห้างสรรพสินค้าเทอร์มินอล 21 ขณะที่ประชาชนหลายคนทยอยหลบหนีออกจากพื้นที่ แต่ยังมีประชาชนบางส่วนติดอยู่ภายในห้างเวลา 18.33 น.
- Problem? (yes / no): 

### Thai clean 11: case r21039 A-18 (V2, contradiction -> possible_conflict)

- Claim: เวลา 00.00 น. (9 ก.พ.) โรงพยาบาลมหาราชสำรองเลือด 1700 ถุง และเตรียมบุคลากรทางการแพทย์จำนวน 240 คน
- Missing numbers: 00.00, 9
- Quote text: เวลาเดียวกัน ผู้สื่อข่าวรายงานว่า สถานการณ์ภายในโรงพยาบาลมหาราช สำรองเลือดจำนวน 1700 ถุง แพทย์จากโรงพยาบาลต่างๆ 50 คน พยาบาล 80 คน แพทย์-พยาบาล สำรอง 240 คน
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 12: case r221439 A-04 (V1, neutral -> support_uncertain)

- Claim: การตรวจค้นเมื่อวันที่ 20 กันยายน นำไปสู่การขยายผลถึงเครือข่ายค้ายาบ้าของนายภานุวัฒน์ ศิริชัย
- Missing numbers: 20
- Quote text: จนนำมาสู่การขยายผลถึงเครือข่ายค้ายาบ้าของนายภานุวัฒน์ ศิริชัย
- Added sentence: หลังจากเมื่อวันที่ 20 กันยายนปีที่ผ่านมามีการตรวจค้น และพบยาเสพติดและของต้องห้ามจำนวนมาก จนนำมาสู่การขยายผลถึงเครือข่ายค้ายาบ้าของนายภานุวัฒน์ ศิริชัย และพบเจ้าหน้าที่เรือนจำมีส่วนเกี่ยวข้อง รวม 3 คน ซึ่งกรมราชทัณฑ์มีคำสั่งให้เจ้าหน้าที่ทั้ง 3 คน ออกจากราชการเพื่อดำเนินคดีซึ่งทั้ง 3 คน อยู่ระหว่างยื่นหลักทรัพย์เงินสดคนละ 2000000 บาทประกันตัวเพื่อสู้คดี
- Problem? (yes / no): 

### Thai clean 13: case r221439 A-07 (V3, neutral -> support_uncertain)

- Claim: เจ้าหน้าที่ทั้ง 3 คนอยู่ระหว่างการยื่นหลักทรัพย์เงินสดคนละ 2,000,000 บาท เพื่อประกันตัวสู้คดี
- Missing numbers: 2,000,000
- Quote text: ซึ่งทั้ง 3 คน อยู่ระหว่างยื่นหลักทรัพย์เงินสดคนละ 2000000 บาทประกันตัวเพื่อสู้คดี
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 14: case r243285 A-09 (V2, neutral -> support_uncertain)

- Claim: นายชัยวิทย์ได้มีปากเสียงกับผู้เป็นพ่อนิดหน่อยในช่วงเวลาประมาณ 2 วันก่อนเกิดเหตุ
- Missing numbers: 2
- Quote text: จนเกิดมีปากเสียงกับผู้เป็นพ่อนิดหน่อย
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 15: case r252658 A-04 (V2, neutral -> support_uncertain)

- Claim: นายนิพัทธอ้างว่าทรัพย์สินจำนวน 49 ล้านบาท มาจากการจำหน่ายวัตถุมงคลและการขายที่ดินของภริยา
- Missing numbers: 49
- Quote text: อ้างว่ามาจากการจำหน่ายวัตถุมงคล และการขายที่ดินของภริยา
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 16: case r269094 A-16 (V1, neutral -> support_uncertain)

- Claim: เจ้าหน้าที่ตรวจค้นที่บ้านพักของผู้ใหญ่บ้าน (เลขที่ 10 บ้านห้วยทราย หมู่ 16 ต.ป่าอ้อดอนชัย) พบอาวุธปืนยาว .22 มม. ติดกล้อง 2 กระบอก, กระสุน .22 มม. 150 นัด, อาวุธปืนลูกซองยาว 1 กระบอก พร้อมกระสุนเบอร์ 12 จำนวน 15 นัด, อาวุธปืนขนาด 9 มม. 1 กระบอก และอาวุธปืนขนาด .380 1 กระบอก
- Missing numbers: 10, 16
- Quote text: พบตัวนายสิทธิชัย อยู่ที่บ้านหลังดังกล่าว เจ้าหน้าที่ตรวจค้นภายในบ้านและที่รถยนต์พบอาวุธปืนยาวขนาด .22 มม. ติดกล้องจำนวน 2 กระบอก, กระสุน .22 มม. จำนวน 150 นัด, อาวุธปืนลูกซองยาวจำนวน 1 กระบอก พร้อมกระสุนเบอร์ 12 จำนวน 15 นัด, อาวุธปืนขนาด 9 มม. จำนวน 1 กระบอก, อาวุธปืนขนาด .380 จำนวน 1 กระบอก
- Added sentence: ป่าอ้อดอนชัย อ.เมือง จ.เชียงราย ที่ใช้ให้ตนไปรับมาจากบริษัทขนส่งถึง 2 ครั้ง,จากนั้นเจ้าหน้าที่ตำรวจพร้อมเจ้าหน้าที่ทหาร จึงนำกำลังไปตรวจค้นที่ บ้านเลขที่ 10 บ้านห้วยทราย หมู่ 16 ต.
- Problem? (yes / no): 

### Thai clean 17: case r285341 A-10 (V3, neutral -> support_uncertain)

- Claim: นายณรงค์วิทย์ พาคำ ถูกแจ้งข้อหากระทำอนาจารเด็กอายุไม่เกิน 13 ปี ซึ่งมีบทลงโทษจำคุกตั้งแต่ 1 ปี ถึง 10 ปี และปรับตั้งแต่ 10,000 ถึง 200,000 บาท
- Missing numbers: 10,000, 200,000
- Quote text: เจ้าหน้าที่ตำรวจได้แจ้งข้อกล่าวหา กระทำอนาจารเด็กอายุไม่เกิน 13 ปี ซึ่งมีบทลงโทษหนักจำคุกตั้งแต่ 1 ปี ถึง 10 ปี ปรับตั้งแต่ 10000 ถึง 200000 บาท
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 18: case r296894 A-01 (V1, neutral -> support_uncertain)

- Claim: นายสุทัด ทัดจันดา อายุ 49 ปี ชาว สปป.ลาว ถูกฆ่าปาดคอและทิ้งศพลงในหนองน้ำ บริเวณป่าชุมชน ทิศตะวันตกของบ้านขุนด่าน หมู่ 1 ตำบลบ้านดง อำเภออุบลรัตน์ จังหวัดขอนแก่น ซึ่งพบศพเมื่อวันที่ 29 เม.ย. 61
- Missing numbers: 61
- Quote text: ฆ่าปาดคอ นายสุทัด ทัดจันดา อายุ 49 ปี ชาว สปป.ลาว แล้วทิ้งศพลงในหนองน้ำ บริเวณป่าชุมชน ทิศตะวันตกของบ้านขุนด่าน หมู่ 1 ตำบลบ้านดง อำเภออุบลรัตน์ จังหวัดขอนแก่น ซึ่งพบศพเมื่อวันที่ 29 เม.ย.
- Added sentence: 61 ที่สถานีตำรวจภูธรอุบลรัตน์ จังหวัดขอนแก่น พ.ต.อ.
- Problem? (yes / no): 

### Thai clean 19: case r303443 A-01 (V1, neutral -> support_uncertain)

- Claim: นายฉัตรชัย โพธิ์เมือง อายุ 24 ปี นักศึกษาคณะวิศวกรรมศาสตร์ มหาวิทยาลัยเอเชียอาคเนย์ ถูกคนร้ายขี่รถจักรยานยนต์ประกบยิงเสียชีวิตขณะจอดรถจักรยานยนต์ติดไฟแดง บริเวณสี่แยกคลองขวาง เพชรเกษม 102/4 ในช่วงเย็นวันที่ 20 เม.ย. 59
- Missing numbers: 59
- Quote text: เรียกประชุมชุดคลี่คลายคดีคนร้ายประกบยิง นายฉัตรชัย โพธิ์เมือง อายุ 24 ปี นักศึกษาชั้นปีที่ 2 คณะวิศวกรรมศาสตร์ สาขาวิศวกรรมความปลอดภัย มหาวิทยาลัยเอเชียอาคเนย์ เสียชีวิตขณะจอดรถจักรยานยนต์ติดไฟแดง บริเวณสี่แยกคลองขวาง เพชรเกษม 102/4 เหตุเกิดช่วงเย็นวันที่ 20 เม.ย.
- Added sentence: วันที่ 21 เม.ย. 59 ที่ สน.
- Problem? (yes / no): 

### Thai clean 20: case r304573 A-07 (V2, neutral -> support_uncertain)

- Claim: เหตุการณ์เกิดขึ้นในช่วงเช้ามืดของวันที่ 10 มีนาคม 2562
- Missing numbers: 2562
- Quote text: เหตุเกิดเมื่อช่วงเช้ามืดของวันที่ 10 มี.ค.ที่ผ่านมา
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 21: case r306563 A-11 (V2, contradiction -> possible_conflict)

- Claim: นางสายพิณถูกควบคุมตัวไปที่ศาลอาญาคดีทุจริตและประพฤติมิชอบภาค 7 จ.สมุทรสงคราม เพื่อฝากขังเมื่อวันที่ 23 กรกฎาคม 2563
- Missing numbers: 2563
- Quote text: เมื่อวันที่ 23 กรกฎาคม ร.ต.อ.หญิง สุภาภรณ์ ดวงกัลยา ควบคุมตัวนางสายพิณ ดิบดีคุ้ม เดินทางไปขออำนาจศาลอาญาคดีทุจริตและประพฤติมิชอบภาค 7 จ.สมุทรสงคราม เพื่อฝากขัง
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 22: case r316652 A-17 (V2, neutral -> support_uncertain)

- Claim: 3 สาวผู้ต้องหาคดีฆ่าได้หนีจากร้านโอโซนคาราโอเกะ จ.ท่าขี้เหล็ก ไปกบดานในเขตอิทธิพลมูเซอ
- Missing numbers: 3
- Quote text: หนีออกจากร้านโอโซนคาราโอเกะ จ.ท่าขี้เหล็ก ฝั่งเมียนมา ไปกบดานในเขตอิทธิพลมูเซอ
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 23: case r331726 A-08 (V1, contradiction -> possible_conflict)

- Claim: เมื่อวันที่ 29 ม.ค. 2563 เวลา 13.00 น. นายสมพรเดินทางมายัง สภ.บางใหญ่ ด้วยรถยนต์โตโยต้า ฟอร์จูนเนอร์ สีดำ หมายเลขทะเบียน ฆณ 7207 กทม.
- Missing numbers: 29, 2563
- Quote text: วันนี้ เวลา 13.00 น. นายสมพร กือเย็น ได้เดินทางพร้อมด้วยรถยนต์โตโยต้า ฟอร์จูนเนอร์ สีดำ หมายเลขทะเบียน ฆณ 7207 กทม. เดินทางมายังโรงพัก สภ.บางใหญ่
- Added sentence: วันนี้ (29 ม.ค.2563) ผู้สื่อข่าวรายงาน ความคืบหน้าคดีชายสูงวัยที่ไปขอทานบริเวณตลาดใกล้กับวัดดอนสะแก
- Problem? (yes / no): 

### Thai clean 24: case r331726 A-17 (V3, neutral -> support_uncertain)

- Claim: นายสมพรถูกเปรียบเทียบปรับเป็นเงิน 1,000 บาท ตามที่กฎหมายกำหนด
- Missing numbers: 1,000
- Quote text: เปรียบเทียบปรับเป็นเงิน 1000 บาท ตามที่กฏหมายกำหนด
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 25: case r337255 A-07 (V3, contradiction -> possible_conflict)

- Claim: เวลาประมาณ 04:00 น. มีกลุ่มคน 3 คน ประกอบด้วยผู้หญิง 1 คน และผู้ชาย 2 คน มาขอถังขยะจากพนักงานรักษาความปลอดภัยโดยอ้างว่าจะนำไปใส่ขยะ
- Missing numbers: 04:00, 1, 2
- Quote text: ก่อนเกิดเหตุเวลาประมาณ 4.00 น. มีผู้หญิง และผู้ชายรวม 3 คน ได้ลงมาขอถังขยะหน้าอพาร์ทเม้นท์กับพนักงานรักษาความปลอดภัย อ้างว่านำไปใส่ขยะ
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 26: case r337255 A-09 (V3, neutral -> support_uncertain)

- Claim: เวลาประมาณ 08:00 น. ผู้ก่อเหตุกลับมาที่ห้องพัก นำไปสู่การพบถังขยะที่มีขยะปิดทับศพอยู่ในห้องน้ำ
- Missing numbers: 08:00
- Quote text: ในเวลาประมาณ 8.00 น. ผู้ก่อเหตุกลับมาที่ห้องพักอีกครั้งจึงได้ตามขึ้นไป จนพบถังขยะตั้งอยู่ในห้องน้ำ โดยมีขยะปิดศพอยู่ด้านบน
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 27: case r337910 A-11 (V3, neutral -> support_uncertain)

- Claim: บัญชีดังกล่าวมีเงินหมุนเวียนกว่า 3,000 ล้านบาท
- Missing numbers: 3,000
- Quote text: มีเงินหมุนเวียนกว่า 3000 ล้านบาท
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 28: case r343601 A-20 (V2, neutral -> support_uncertain)

- Claim: ตำรวจทั้ง 2 นายถูกสั่งให้ออกจากราชการไว้ก่อน ตามคำสั่งตำรวจภูธรจังหวัดบึงกาฬ ที่ 299/2560 ลงวันที่ 13 มิ.ย.60
- Missing numbers: 2
- Quote text: และให้ออกจากราชการไว้ก่อน ตามคำสั่งตำรวจภูธรจังหวัดบึงกาฬ ที่ 299/2560 ลงวันที่ 13 มิ.ย.60
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 29: case r343601 A-21 (V2, neutral -> support_uncertain)

- Claim: หากผลสอบสวนพบว่ามีความผิดจริง ตำรวจทั้ง 2 นายอาจถูกให้ออกจากราชการได้ทันที
- Missing numbers: 2
- Quote text: หากผลสอบสวนออกมามีความผิดจริง ก็ให้ออกราชการได้เลย
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 30: case r349226 A-15 (V2, neutral -> support_uncertain)

- Claim: นายอาโมรีจะถูกนำตัวไปศาลจังหวัดพิจิตรในบ่ายวันที่ 30 ม.ค. เพื่อขออำนาจฝากขัง
- Missing numbers: 30
- Quote text: ในช่วงบ่ายวันนี้ จะนำตัวนายอาโมรี เดินทางที่ศาลจังหวัดพิจิตรเพื่อขออำนาจฝากขัง
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 31: case r36573 A-11 (V3, neutral -> support_uncertain)

- Claim: นายอภิชัยจ้างให้นายเอ็มลงไปช่วยงมศพในบ่อเพื่อนำไปทิ้งที่อื่นในราคาศพละ 5,000 บาท
- Missing numbers: 5,000
- Quote text: นายอภิชัยเกิดอาการหลอน ก่อนว่าจ้างให้ลงไปช่วยงมศพในบ่อเพื่อเอาไปทิ้งที่อื่น ในราคาศพละ 5000 บาท
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 32: case r45738 A-06 (V2, neutral -> support_uncertain)

- Claim: เมื่อวันที่ 24 ก.พ.62 เวลาประมาณ 21.00 น. นายบรรณ์กรชัยวุฒิ เพชรมงคลสุข ได้ใช้อาวุธปืน M4 จี้ชิงรถยนต์นิสสัน มาร์ช สีดำ ของนายนันทัศน์ บุญมี บนถนนภายในหมู่บ้านทุ่งลูกนก อ.กำแพงแสน จ.นครปฐม
- Missing numbers: 24, 62
- Quote text: ในวันเดียวกัน เวลาประมาณ 21.00 น. ทหารเกณฑ์ที่ก่อเหตุจี้ชิงปืน ทราบชื่อต่อมาคือ นายบรรณ์กรชัยวุฒิ เพชรมงคลสุข ได้ใช้อาวุธปืน M4 จี้รถรถนิสสัน มาร์ช สีดำ ไม่ทราบทะเบียน ขณะที่นายนันทัศน์ บุญมี ผู้เสียหายขับอยู่บนถนนภายในหมู่บ้านทุ่งลูกนก อ.กำแพงแสน จ.นครปฐม
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 33: case r52314 A-01 (V2, neutral -> support_uncertain)

- Claim: เมื่อเวลาประมาณ 15.00 น. วันที่ 12 เม.ย. 2560 มีเหตุการณ์ใช้อาวุธปืนยิงเข้าไปในบ้านเลขที่ 44 หมู่ 9 ท้ายซอยบางปลา 63 ต.บางปลา อ.บางพลี
- Missing numbers: 12, 2560
- Quote text: เมื่อเวลาประมาณ 15.00 น. วันเดียวกัน ร.ต.ท.อำนวจ บัวหอม รอง สวป. รับแจ้งว่า มีคนใช้อาวุธปืนยิงเข้าไปในบ้านเลขที่ 44 หมู่9 ท้ายซอยบางปลา 63 ต.บางปลา อ.บางพลี
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 34: case r5339 A-12 (V2, neutral -> support_uncertain)

- Claim: จุดยืนของสถานีโทรทัศน์ช่อง 3 เพิ่มน้ำหนักให้ความพยายามของกลุ่มคนที่ต้องการกลไกทางกฎหมายในการควบคุมสื่อ
- Missing numbers: 3
- Quote text: และเป็นการเพิ่มน้ำหนักให้กับความพยายามของกลุ่มคนที่ต้องการให้มีกลไกที่มีอำนาจทางกฎหมายในการควบคุมและลงโทษสื่อที่ละเมิดจริยธรรม
- Added sentence: -
- Problem? (yes / no): 

### Thai clean 35: case r82354 A-23 (V2, neutral -> support_uncertain)

- Claim: จำเลยที่ 1, 2 และ 3 ถูกคุมขังอยู่ในทัณฑสถานบำบัดพิเศษกลาง และทัณฑสถานหญิงกลาง
- Missing numbers: 1
- Quote text: เนื่องจาก นายหง เจิ้ง อี้ ชาวไต้หวัน, นายชลวิทย์ หรือไก่ คีตะตระกูล สามีของปุ๊กกี้ ที่ 2, น.ส.ปริศนา หรือปุ๊กกี้ อดีตนักร้องชื่อดังยุค90 ที่ 3 ถูกคุมขังอยู่ในทัณฑสถานบำบัดพิเศษกลาง และทัณฑสถานหญิงกลาง
- Added sentence: -
- Problem? (yes / no): 

