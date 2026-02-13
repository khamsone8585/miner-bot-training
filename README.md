# 🏭 Factory SD-WAN & Miner Monitor Bot

โปรเจกต์นี้ผมทำขึ้นมาเพื่อ Monitor สถานะ Internet (SD-WAN) ของโรงงานครับ เอาไว้เช็คว่าเน็ตเส้น Main หรือ Backup หลุดหรือเปล่า แบบ Real-time ครับ

### 🚀 สิ่งที่ระบบทำได้
* **Check 4 Links:** ตรวจสอบเน็ตทั้ง 4 เส้น (LTC Main/Backup, ETL Main/Backup) ตลอด 24 ชม.
* **Smart Alert:** แจ้งเตือนผ่าน **Telegram** ทันทีถ้ามีเส้นไหนดับ (มีระบบกรอง Error ไม่แจ้งเตือนพร่ำเพรื่อถ้าแค่กระตุกนิดหน่อย)
* **Dashboard:** ส่งค่าไปโชว์บน **Uptime Kuma** ดูเป็นกราฟสวยๆ ได้เลย
* **Auto Restart:** รันบน **Docker** ถ้าเครื่องรีสตาร์ท บอทกลับมาทำงานเองอัตโนมัติ

### 🛠️ Tech Stack
* Python (Logic การเช็ค Ping)
* Docker & Docker Compose (Container)
* Uptime Kuma (Dashboard)

---

### ⚙️ วิธีติดตั้ง (Installation)

1. **Clone Project**
   ```bash
   git clone <your-repo-url>
   cd <folder-name>
