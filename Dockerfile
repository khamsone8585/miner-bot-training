# 1. ใช้ Python เวอร์ชั่นเล็กจิ๋ว (Slim) เพื่อประหยัดพื้นที่
FROM python:3.9-slim

# 2. ติดตั้ง Ping (เพราะ Docker ตัวโล่งๆ จะไม่มีคำสั่ง Ping)
RUN apt-get update && apt-get install -y iputils-ping

# 3. ตั้งโฟลเดอร์ทำงานข้างในกล่อง
WORKDIR /app

# 4. ก๊อปปี้ไฟล์จากเครื่องเรา เข้าไปในกล่อง
COPY miner_bot.py .

# 5. ลง Library ที่ต้องใช้
RUN pip install requests

# 6. คำสั่งรันเมื่อเปิดกล่อง
CMD ["python","-u", "miner_bot.py"]
