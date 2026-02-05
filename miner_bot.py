import os
import datetime
import requests
import json

# --- ⚙️ ตั้งค่า (CONFIG) ---
TELEGRAM_TOKEN = "8216223522:AAEvbQ_TU0I_iAIchfIQljGdK_K8FyNFezg"
CHAT_ID = "6417593756"
STATE_FILE = "/root/dev_train/monitor_state.json"

# 🎯 เป้าหมายหลัก (พระเอกของเรา)
# ใส่ Public IP ของโรงงาน (ที่ได้จาก whatismyip.com)
WAN_LINKS = {
	"LTC_H3 (Main)":"202.137.147.163",
	"LTC_H4 (Main)":"202.137.147.164",
	"ETL_H3 (Backup)":"114.129.29.226",
	"ETL_H4 (Backup)":"114.129.29.227"
}
# 🏥 เป้าหมายวินิจฉัย (ตัวประกอบที่ใช้เช็คอาการ)
# --- 🛠️ โซนฟังก์ชัน ---
def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Send Error: {e}")

def check_ip_status(ip_address):
    # ปรับ Ping ให้ไวขึ้น (รอแค่ 1 วิ)
    response = os.system(f"ping -c 1 -W 1 {ip_address} > /dev/null 2>&1")
    return response == 0

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

# --- 🚀 เริ่มทำงาน ---
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"--- Check Round: {now} ---")

#1. เช็คสถานะทุกเสั้น
link_results = {}
for name, ip in WAN_LINKS.items():
	is_up = check_ip_status(ip)
	link_results[name] = is_up
	status_icon = "✅" if is_up else "❌"
    	print(f"[{status_icon}] {name}: {ip}")

# 2. วิเคราะห์ภาพรวม (Aggregation Logic)
# LTC ถือว่า UP ถ้า H3 หรือ H4 ตัวใดตัวหนึ่งติด
ltc_alive = link_results["LTC_H3 (Main)"] or link_results["LTC_H4 (Main)"]
# ETL ถือว่า UP ถ้า H3 หรือ H4 ตัวใดตัวหนึ่งติด
etl_alive = link_results["ETL_H3 (Backup)"] or link_results["ETL_H4 (Backup)"]

# สรุปสถานะปัจจุบัน
current_summary = "NORMAL"
if not ltc_alive and not etl_alive:
    current_summary = "CRITICAL" # ดับหมด
elif not ltc_alive and etl_alive:
    current_summary = "FAILOVER" # Main ดับ ใช้ Backup แทน

# 3. โหลดความจำเดิมมาเทียบ
last_state = load_state()
last_summary = last_state.get("SUMMARY", "NORMAL")

# 4. ตัดสินใจแจ้งเตือน (Decision Engine)
alert_message = ""

if current_summary == "CRITICAL" and last_summary != "CRITICAL":
    # 🔴 เรื่องใหญ่: โรงงานดับสนิท
    alert_message = f"🚨 **วิกฤต! โรงงานดับสนิท (All Links Down)** 🚨\nเวลา: {now}\n\nสถานะรายเส้น:\n"
    for name, is_up in link_results.items():
        alert_message += f"{'✅' if is_up else '❌'} {name}\n"
    alert_message += "\n⚠️ ตรวจสอบด่วน ไฟดับหรือเปล่า?"

elif current_summary == "FAILOVER" and last_summary == "NORMAL":
    # 🟡 เรื่องรอง: Main ดับ สลับไปใช้ Backup
    alert_message = f"⚠️ **แจ้งเตือน: LTC (Main) ล่ม!**\nเวลา: {now}\nกำลังวิ่งบนเส้นสำรอง ETL (Backup) 🔄\n\nสถานะ:\n❌ LTC H3 & H4: Down\n✅ ETL: Active"

elif current_summary == "NORMAL" and last_summary != "NORMAL":
    # 🟢 ข่าวดี: กลับมาปกติ
    alert_message = f"✅ **ระบบกลับมาปกติแล้ว (Main Online)**\nเวลา: {now}\nLTC กลับมาทำงานแล้ว 🚀"

# ส่งแจ้งเตือน (ถ้ามีเรื่องต้องแจ้ง)
if alert_message:
    print(f"Sending Alert: {current_summary}")
    send_telegram_msg(alert_message)
else:
    print(f"Status: {current_summary} (No Change)")

# บันทึกสถานะล่าสุด
save_data = {"SUMMARY": current_summary, "LINKS": link_results}
save_state(save_data)
print("---------------------------------")
