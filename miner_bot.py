import os
import datetime
import requests
import json
import time  # <--- เพิ่มตัวจับเวลา

# --- ⚙️ ตั้งค่า (CONFIG) ---
TELEGRAM_TOKEN = "8216223522:AAEvbQ_TU0I_iAIchfIQljGdK_K8FyNFezg"
CHAT_ID = "6417593756"
STATE_FILE = "/app/monitor_state.json"  # <--- แก้ Path ให้เป็นใน Docker (/app)

# 🌐 รายชื่อท่อ WAN (SD-WAN)
WAN_LINKS = {
    "LTC_H3 (Main)": "202.137.147.163",
    "LTC_H4 (Main)": "202.137.147.164",
    "ETL_H3 (Backup)": "114.129.29.226",
    "ETL_H4 (Backup)": "114.129.29.227"
}

# --- 🛠️ โซนฟังก์ชัน ---
def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"Send Error: {e}")

def check_ip_status(ip_address):
    # Ping 1 ครั้ง รอ 1 วินาที
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

def run_check_cycle():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"--- SD-WAN Check: {now} ---")

    # 1. เช็คสถานะทุกเส้น
    link_results = {}
    for name, ip in WAN_LINKS.items():
        is_up = check_ip_status(ip)
        link_results[name] = is_up
        print(f"[{'✅' if is_up else '❌'}] {name}")

    # 2. วิเคราะห์ภาพรวม
    ltc_alive = link_results["LTC_H3 (Main)"] or link_results["LTC_H4 (Main)"]
    etl_alive = link_results["ETL_H3 (Backup)"] or link_results["ETL_H4 (Backup)"]

    current_summary = "NORMAL"
    if not ltc_alive and not etl_alive:
        current_summary = "CRITICAL"
    elif not ltc_alive and etl_alive:
        current_summary = "FAILOVER"

    # 3. โหลดความจำเดิมมาเทียบ
    last_state = load_state()
    last_summary = last_state.get("SUMMARY", "NORMAL")

    # 4. ตัดสินใจแจ้งเตือน
    alert_message = ""
    if current_summary == "CRITICAL" and last_summary != "CRITICAL":
        alert_message = f"🚨 **วิกฤต! โรงงานดับสนิท** 🚨\nเวลา: {now}\nตรวจสอบด่วน!"
    elif current_summary == "FAILOVER" and last_summary == "NORMAL":
        alert_message = f"⚠️ **แจ้งเตือน: Main ล่ม!**\nวิ่งเส้นสำรอง ETL 🔄\nเวลา: {now}"
    elif current_summary == "NORMAL" and last_summary != "NORMAL":
        alert_message = f"✅ **ระบบกลับมาปกติแล้ว**\nLTC Online 🚀\nเวลา: {now}"

    if alert_message:
        print(f"Sending Alert: {current_summary}")
        send_telegram_msg(alert_message)
    
    save_state({"SUMMARY": current_summary, "LINKS": link_results})
    print("---------------------------------")

# --- 🚀 Loop ตลอดกาล (Service Mode) ---
print("🤖 Bot Started... Loop every 300 seconds")
while True:
    run_check_cycle()
    time.sleep(300) # หลับ 300 วินาที (5 นาที)
