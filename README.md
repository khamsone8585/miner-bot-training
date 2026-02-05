# 🤖 Miner Monitor Bot (V.1.5)
**ระบบเฝ้าระวังเหมืองขุด Crypto และตรวจสอบสถานะ Network ภายในโรงงานแบบอัตโนมัติ**

พัฒนาโดย: **Khamsone**
Tech Stack: **Python 3, Linux Cronjob, Shell Script, Git**

---

## 🚀 ฟีเจอร์หลัก (Key Features)

* **Multi-Target Monitoring:** รองรับการเช็ค IP Address จำนวนมากพร้อมกัน (Mining Rigs, Firewall, Switches)
* **Real-time Telegram Alert:** แจ้งเตือนเข้ามือถือทันทีเมื่ออุปกรณ์มีปัญหา (Offline) หรือกลับมาทำงานปกติ (Recovered)
* **🧠 Smart State Monitoring (V1.5):** มีระบบจำสถานะก่อนหน้า (State Persistence) เพื่อ **ลดการแจ้งเตือนขยะ (Spam Alert)**
    * แจ้งเตือนเมื่อสถานะ *เปลี่ยน* เท่านั้น (เช่น จาก Online -> Offline)
    * หากดับต่อเนื่อง จะไม่แจ้งเตือนซ้ำให้รำคาญ
* **24/7 Automation:** ทำงานอัตโนมัติทุกๆ 5 นาทีผ่านระบบ Cronjob
* **Logging System:** บันทึกประวัติการทำงานลงไฟล์ Log เพื่อตรวจสอบย้อนหลัง

---

## 🛠️ วิธีการติดตั้ง (Installation)

1. **Clone โปรเจกต์ลงเครื่อง Server**
   ```bash
   git clone [https://github.com/khamsone8585/miner-bot-training.git](https://github.com/khamsone8585/miner-bot-training.git)
   cd miner-bot-training
2. Install Library 
   apt install python3-requests
3. ตั้งค่า Config แก้ไขไฟล์ miner_bot.py เพื่อใส่ Token และ IP ที่ต้องการเช็ค
   # ตั้งค่า Telegram Bot
TELEGRAM_TOKEN = "ใส่_Token_ของคุณ"
CHAT_ID = "ใส่_Chat_ID_ของคุณ"

# รายชื่อ IP ที่ต้องการตรวจสอบ
target_ips = ["192.168.1.10", "192.168.1.20", "8.8.8.8"]	
------------------------------------------------------------
📅 Update Log
Day 1: เริ่มต้นโปรเจกต์ (Basic Ping Script)

Day 2: เชื่อมต่อระบบ Version Control (Git & GitHub)

Day 3: พัฒนาระบบ Loop และ Function เพื่อรองรับหลาย IP

Day 4: เชื่อมต่อ API แจ้งเตือนผ่าน Telegram Bot

Day 5 (Latest): อัปเกรด Logic เป็น V1.5 (Smart State Monitoring) และตั้งค่า Cronjob

