# 🤖 Miner Monitor Bot (Docker + SD-WAN Edition) - V1.9
**ระบบเฝ้าระวังเหมืองขุด Crypto และตรวจสอบสถานะ Network (SD-WAN) ภายในโรงงานแบบอัตโนมัติ**

พัฒนาโดย: **Khamsone**  
Tech Stack: **Python 3, Docker, Shell Script, Git**

---

## 🚀 ฟีเจอร์หลัก (Key Features)

* **🔧 Modular Architecture (V1.9):** โครงสร้างโค้ดแบบโมดูลาร์ที่สะอาดและเป็นมืออาชีพ
* **🛡️ SD-WAN Monitoring:** ตรวจสอบเส้นทางอินเทอร์เน็ต 4 เส้นแบบละเอียด (Main vs Backup)
  * แยกแยะสถานะ **Normal**, **Failover** (วิ่งเส้นสำรอง), และ **Critical** (ดับสนิท)
* **📱 Real-time Alert:** แจ้งเตือนผ่าน Telegram ทันทีเมื่อสถานะมีการเปลี่ยนแปลง
* **🧠 Smart State Persistence:** มีระบบจำสถานะลดการแจ้งเตือนซ้ำ (No Spam)
* **🔒 Secure Configuration:** ใช้ไฟล์ `.env` เก็บข้อมูลสำคัญอย่างปลอดภัย
* **🐳 Dockerized:** รันบน Docker Container 100% ทำงานแยกอิสระ ปลอดภัย และย้ายเครื่องง่าย
* **⚡ Enhanced Error Handling:** ระบบจัดการข้อผิดพลาดที่แข็งแกร่งและฟื้นตัวอัตโนมัติ

---

## 🐳 คู่มือการติดตั้งด้วย Docker (แนะนำ)

### Step 1: Clone Repository
```bash
git clone https://github.com/khamsone8585/miner-bot-training.git
cd miner-bot-training
```

### Step 2: ตั้งค่าไฟล์ Environment Variables
```bash
# คัดลอกไฟล์ตัวอย่าง
cp .env.example .env

# แก้ไขไฟล์ .env ด้วย text editor
nano .env
```

**ตัวแปรที่ต้องแก้ไข:**
- `TELEGRAM_TOKEN`: Token ของ Telegram Bot (ได้จาก @BotFather)
- `CHAT_ID`: ID ของแชทที่จะรับการแจ้งเตือน
- `LTC_H3_IP`, `LTC_H4_IP`: IP Address ของเส้น Main
- `ETL_H3_IP`, `ETL_H4_IP`: IP Address ของเส้น Backup
- `CHECK_INTERVAL`: ช่วงเวลาการตรวจสอบ (วินาที, ค่าเริ่มต้น 300 = 5 นาที)

### Step 3: Build Docker Image
```bash
docker build -t miner-bot:v1.9 .
```

### Step 4: Run Container
```bash
# รันแบบ Background (แนะนำ)
docker run -d --name miner-monitor \
  --env-file .env \
  --restart unless-stopped \
  miner-bot:v1.9

# รันแบบ Interactive (สำหรับทดสอบ)
docker run -it --env-file .env miner-bot:v1.9
```

### การจัดการ Container
```bash
# ดูสถานะ Container
docker ps

# ดู Log
docker logs miner-monitor

# หยุด Container
docker stop miner-monitor

# เริ่ม Container ใหม่
docker start miner-monitor

# ลบ Container
docker rm miner-monitor
```

---

## 📁 โครงสร้างไฟล์ (File Structure)

```
miner-bot-training/
├── miner_bot.py          # โค้ดหลักแบบโมดูลาร์ (V1.9)
├── Dockerfile            # การตั้งค่า Docker Container
├── .env.example          # ตัวอย่างไฟล์ Environment Variables
├── .env                  # ไฟล์ตั้งค่าจริง (ไม่อัปโหลด Git)
├── .gitignore           # ไฟล์ที่ไม่ต้องการใน Git
├── README.md            # คู่มือนี้
└── logs/                # โฟลเดอร์เก็บ Log (ถ้ามี)
```

### คำอธิบายไฟล์สำคัญ:

**`.env`** - ไฟล์เก็บการตั้งค่าที่สำคัญและเป็นความลับ
- เก็บ Telegram Token, Chat ID, และ IP Address ต่างๆ
- ไม่ถูกอัปโหลดไปยัง Git เพื่อความปลอดภัย
- ต้องสร้างจาก `.env.example` และแก้ไขค่าให้ถูกต้อง

**`.gitignore`** - ไฟล์ควบคุมการอัปโหลด Git
- ป้องกันไฟล์ `.env` และไฟล์สำคัญอื่นๆ ไม่ให้อัปโหลดไปยัง GitHub
- รักษาความปลอดภัยของข้อมูลสำคัญ

**`monitor_state.json`** - ไฟล์เก็บสถานะการทำงาน
- เก็บสถานะล่าสุดของแต่ละ Link (NORMAL/FAILOVER/CRITICAL)
- ใช้เปรียบเทียบเพื่อตัดสินใจส่งการแจ้งเตือน
- สร้างอัตโนมัติเมื่อรันครั้งแรก

---

## 🔧 ฟีเจอร์ใหม่ใน V1.9 (Modular Architecture)

### โครงสร้างฟังก์ชันใหม่:
- **`load_config()`** - โหลดการตั้งค่าทั้งหมด
- **`check_ping(ip)`** - ตรวจสอบการเชื่อมต่อ IP เดียว
- **`analyze_network(results)`** - วิเคราะห์สถานะเครือข่าย (Normal/Failover/Critical)
- **`send_telegram(message, config)`** - ส่งการแจ้งเตือนพร้อม Error Handling
- **`main()`** - ฟังก์ชันหลักที่ควบคุมการทำงานทั้งหมด

### การปรับปรุง:
- ✅ โค้ดสะอาดและเป็นระเบียบมากขึ้น
- ✅ เพิ่มคอมเมนต์ภาษาไทยอธิบายแต่ละฟังก์ชัน
- ✅ ระบบจัดการข้อผิดพลาดที่แข็งแกร่ง
- ✅ การแสดงผลที่ชัดเจนด้วย Emoji และสถานะ
- ✅ ฟื้นตัวอัตโนมัติเมื่อเกิดข้อผิดพลาด

---

## 📊 การทำงานของระบบ

1. **ตรวจสอบ 4 เส้นทาง:** LTC_H3, LTC_H4 (Main) และ ETL_H3, ETL_H4 (Backup)
2. **วิเคราะห์สถานะ:**
   - **NORMAL:** เส้น Main ทำงานปกติ
   - **FAILOVER:** เส้น Main ล่ม แต่ Backup ยังทำงาน
   - **CRITICAL:** ทั้ง Main และ Backup ล่มหมด
3. **แจ้งเตือนอัจฉริยะ:** ส่งการแจ้งเตือนเฉพาะเมื่อสถานะเปลี่ยนแปลง
4. **บันทึกสถานะ:** เก็บสถานะล่าสุดไว้เปรียบเทียบรอบถัดไป

---

## 🛠️ การแก้ไขปัญหา (Troubleshooting)

### ปัญหาที่พบบ่อย:

**1. Container หยุดทำงาน**
```bash
# ตรวจสอบ Log
docker logs miner-monitor

# เริ่มใหม่
docker restart miner-monitor
```

**2. ไม่ได้รับการแจ้งเตือน Telegram**
- ตรวจสอบ `TELEGRAM_TOKEN` และ `CHAT_ID` ในไฟล์ `.env`
- ทดสอบส่งข้อความผ่าน Bot ก่อน

**3. ไฟล์ State ไม่สามารถบันทึกได้**
- ตรวจสอบสิทธิ์การเขียนไฟล์ใน Container
- ตรวจสอบ Path ในตัวแปร `STATE_FILE`

---

## 📅 Update Log

- **Day 1:** เริ่มต้นโปรเจกต์ (Basic Ping Script)
- **Day 2:** เชื่อมต่อระบบ Version Control (Git & GitHub)
- **Day 3:** พัฒนาระบบ Loop และ Function เพื่อรองรับหลาย IP
- **Day 4:** เชื่อมต่อ API แจ้งเตือนผ่าน Telegram Bot
- **Day 5:** อัปเกรด Logic เป็น V1.5 (Smart State Monitoring) และตั้งค่า Cronjob
- **Day 6:** 🐳 Docker Containerization และ SD-WAN Logic (V1.7)
- **Day 7:** 🔧 **Modular Architecture Refactoring (V1.9)** - โครงสร้างโค้ดแบบมืออาชีพ

---

**🎯 เป้าหมาย:** สร้างระบบเฝ้าระวังที่เสถียร แม่นยำ และใช้งานง่าย เพื่อรักษาความต่อเนื่องของการทำงานในโรงงาน