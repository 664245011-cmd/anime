หน้ารวมงาน https://main011-flzqrvdvjwvmjykj78txqk.streamlit.app/?fbclid=IwY2xjawUseAVleHRuA2FlbQIxMABwZG9mBWJyaWQRMUk2QXlsdUNRb2hsOE9pV2JzcnRjBmFwcF9pZBAyMjIwMzkxNzg4MjAwODkyAAEejVQucUikJpAJtHOvDv4agRU-wVOrDE2D-HDm_BUKR5PYqrehlk_BRyV8I2I_aem_m-v9C1fpFrP_f2ZcE_DHHw
Anime Recommendation System

โปรเจ็กต์ตัวอย่างสำหรับรายวิชา Graph Database / Advanced Database พัฒนาด้วย Streamlit + Neo4j Aura + Cypher โดยปรับข้อมูลจากระบบต้นแบบให้เป็นระบบแนะนำอนิเมะของโปรเจ็กต์นี้

1. แนวคิดของระบบ

ระบบใช้ Property Graph โดยมี Node เพียง 2 ประเภท คือ User และ Anime

(User)-[:FRIEND_OF]-(User)
(User)-[:WATCHED {watch_date}]->(Anime)

จุดเด่นของระบบคือการแนะนำอนิเมะจากเครือข่ายเพื่อน โดยดูว่าเพื่อนของผู้ใช้เคยดูอนิเมะเรื่องใด และผู้ใช้ยังไม่เคยดูเรื่องนั้น

ตัวอย่างแนวคิดคะแนน:

score = จำนวนเพื่อนที่เคยดูอนิเมะเรื่องนั้น

สูตรนี้เป็น heuristic เพื่อการเรียนการสอน ไม่ใช่โมเดล ML ที่ผ่านการ optimize

2. โครงสร้างไฟล์

anime_graph_recommender/
├── app.py
├── neo4j_service.py
├── requirements.txt
├── README.md
└── 664245011_Anime_User.ipynb

3. โครงสร้างข้อมูล

User

มีตัวอย่าง User 10 คน ได้แก่ Mint, Non, Fah, Ton, Bank, Aom, Beam, Nene, Game และ Palm

Anime

มีตัวอย่าง Anime 10 เรื่อง ได้แก่ One Piece, Naruto, Demon Slayer, Attack on Titan, Jujutsu Kaisen, My Hero Academia, Haikyuu!!, Spy x Family, Death Note และ Dragon Ball

Relationship

FRIEND_OF — ความสัมพันธ์ระหว่าง User กับ User

WATCHED — User เคยดู Anime และเก็บ watch_date

ระบบตั้ง Unique Constraint สำหรับ User.user_id และ Anime.anime_id

4. รันในเครื่อง

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py

5. ครั้งแรกที่เปิดระบบ

ตั้งค่า Neo4j Aura ใน Streamlit Secrets

เปิดระบบผ่าน streamlit run app.py

หากฐานข้อมูลยังไม่มีข้อมูล ให้กด โหลดข้อมูลตัวอย่าง (10 User / 10 Anime)

ทดลองหน้า Anime ที่แนะนำ, โปรไฟล์, ค้นหา Anime, จัดการข้อมูล และกราฟเครือข่าย

ตัวอย่าง Secrets:

[neo4j]
uri = "neo4j+s://YOUR_INSTANCE.databases.neo4j.io"
username = "neo4j"
password = "YOUR_PASSWORD"
database = "neo4j"

อย่านำ password ไปใส่ในไฟล์ที่ commit ขึ้น GitHub

6. การทำงานของระบบแนะนำ

ระบบจะเลือก Anime ที่ User ยังไม่เคยดู แล้วตรวจสอบเพื่อนของ User ว่าเคยดู Anime เรื่องนั้นหรือไม่ หากมีเพื่อนหลายคนเคยดู จะได้คะแนนสูงขึ้น และแสดงรายชื่อเพื่อนที่เกี่ยวข้องเพื่อช่วยอธิบายคำแนะนำ

7. ประเด็น Graph Database ที่ได้ฝึก

Node, Label, Property

Relationship และ Direction

Constraint และ Unique Key

MATCH, MERGE, OPTIONAL MATCH, WITH, UNWIND

Graph traversal ผ่านเพื่อน → Anime

Aggregation เช่น count และ collect

Recommendation จาก topology ของกราฟ

Parameterized Cypher

Python Driver และ connection pooling

Streamlit UI

Secrets และ cloud deployment

8. สิ่งที่ปรับจากระบบต้นแบบ

เปลี่ยนจาก Student / Book เป็น User / Anime

ตัด Author และ Category ออก

ใช้เฉพาะ Node User และ Anime

เปลี่ยน BORROWED เป็น WATCHED

คง FRIEND_OF สำหรับการแนะนำจากเครือข่ายเพื่อน

ใช้ MERGE เพื่อรองรับการรันข้อมูลตัวอย่างซ้ำ

ใช้ Unique Constraints สำหรับ User และ Anime

ใช้ parameterized Cypher

แยก database layer (neo4j_service.py) ออกจาก UI (app.py)

9. Notebook

ไฟล์ 664245011_Anime_User.ipynb ใช้สำหรับสร้างและตรวจสอบ Graph ใน Neo4j โดยเน้นให้เหลือเฉพาะ User และ Anime พร้อมความสัมพันธ์ FRIEND_OF และ WATCHED และมีฟังก์ชันแนะนำ Anime จาก Anime ที่เพื่อนเคยดู
