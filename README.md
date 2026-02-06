# 🤖 Miner Monitor Bot (V.1.7) - Docker Edition
**ระบบเฝ้าระวังเหมืองขุด Crypto และตรวจสอบสถานะ Network (SD-WAN) ภายในโรงงานแบบอัตโนมัติ**

พัฒนาโดย: **Khamsone**
Tech Stack: **Python 3, Docker, Shell Script, Git**

---

## 🚀 ฟีเจอร์หลัก (Key Features)

* **Multi-Target Monitoring:** รองรับการเช็ค IP Address จำนวนมากพร้อมกัน
* **🛡️ SD-WAN Monitoring (V1.7):** ตรวจสอบเส้นทางอินเทอร์เน็ตแบบละเอียด (Main vs Backup)
    * แยกแยะสถานะ **Normal**, **Failover** (วิ่งเส้นสำรอง), และ **Critical** (ดับสนิท)
* **Real-time Alert:** แจ้งเตือนผ่าน Telegram ทันทีเมื่อสถานะมีการเปลี่ยนแปลง
* **🧠 Smart State:** มีระบบจำสถานะ (State Persistence) ลดการแจ้งเตือนซ้ำ (No Spam)
* **🐳 Dockerized:** รันบน Docker Container 100% ทำงานแยกอิสระ ปลอดภัย และย้ายเครื่องง่าย

---

## 🐳 วิธีการติดตั้งด้วย Docker (แนะนำ)

วิธีนี้ง่ายและเสถียรที่สุด ไม่ต้องตั้งค่า Cronjob เอง

1. **Clone โปรเจกต์**
   ```bash
   git clone [https://github.com/khamsone8585/miner-bot-training.git](https://github.com/khamsone8585/miner-bot-training.git)
   cd miner-bot-training
------------------------------------------------------------
📅 Update Log
Day 1: เริ่มต้นโปรเจกต์ (Basic Ping Script)

Day 2: เชื่อมต่อระบบ Version Control (Git & GitHub)

Day 3: พัฒนาระบบ Loop และ Function เพื่อรองรับหลาย IP

Day 4: เชื่อมต่อ API แจ้งเตือนผ่าน Telegram Bot

Day 5 (Latest): อัปเกรด Logic เป็น V1.5 (Smart State Monitoring) และตั้งค่า Cronjob

Day 6 (Latest):

🐳 Docker Containerization: เปลี่ยนระบบรันเป็น Service บน Docker

🛡️ SD-WAN Logic (V1.7): เพิ่มการตรวจสอบ Network แบบ 4 เส้นทาง (LTC/ETL) แยก Main/Backup
