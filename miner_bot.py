import os
import datetime
import requests
import json
import time

def load_config():
    """
    โหลดการตั้งค่าต่างๆ จากตัวแปรสภาพแวดล้อม
    ฟังก์ชันนี้จะคืนค่าการตั้งค่าทั้งหมดที่จำเป็นสำหรับการทำงานของบอท
    """
    config = {
        "TELEGRAM_TOKEN": "8216223522:AAEvbQ_TU0I_iAIchfIQljGdK_K8FyNFezg",
        "CHAT_ID": "6417593756",
        "STATE_FILE": "/app/monitor_state.json",
        "WAN_LINKS": {
            "LTC_H3 (Main)": "202.137.147.163",
            "LTC_H4 (Main)": "202.137.147.164",
            "ETL_H3 (Backup)": "114.129.29.226",
            "ETL_H4 (Backup)": "114.129.29.227"
        },
        "CHECK_INTERVAL": 300  # 5 นาที
    }
    return config

def check_ping(ip):
    """
    ตรวจสอบการเชื่อมต่อไปยัง IP address ด้วยคำสั่ง ping
    Args:
        ip (str): IP address ที่ต้องการตรวจสอบ
    Returns:
        bool: True หากสามารถ ping ได้, False หากไม่สามารถ ping ได้
    """
    try:
        # Ping 1 ครั้ง รอ 1 วินาที
        response = os.system(f"ping -c 1 -W 1 {ip} > /dev/null 2>&1")
        return response == 0
    except Exception as e:
        print(f"Ping Error for {ip}: {e}")
        return False

def analyze_network(results):
    """
    วิเคราะห์สถานะของเครือข่ายจากผลการตรวจสอบ
    Args:
        results (dict): ผลการตรวจสอบแต่ละ link
    Returns:
        str: สถานะของเครือข่าย (NORMAL, FAILOVER, CRITICAL)
    """
    # ตรวจสอบว่าเส้น Main (LTC) มีชีวิตอยู่หรือไม่
    ltc_alive = results.get("LTC_H3 (Main)", False) or results.get("LTC_H4 (Main)", False)
    
    # ตรวจสอบว่าเส้น Backup (ETL) มีชีวิตอยู่หรือไม่
    etl_alive = results.get("ETL_H3 (Backup)", False) or results.get("ETL_H4 (Backup)", False)
    
    # วิเคราะห์สถานะ
    if not ltc_alive and not etl_alive:
        return "CRITICAL"  # ทั้งหมดล่ม
    elif not ltc_alive and etl_alive:
        return "FAILOVER"  # Main ล่ม แต่ Backup ยังทำงาน
    else:
        return "NORMAL"    # Main ทำงานปกติ

def send_telegram(message, config):
    """
    ส่งข้อความแจ้งเตือนไปยัง Telegram
    Args:
        message (str): ข้อความที่ต้องการส่ง
        config (dict): การตั้งค่าที่มี TELEGRAM_TOKEN และ CHAT_ID
    """
    try:
        url = f"https://api.telegram.org/bot{config['TELEGRAM_TOKEN']}/sendMessage"
        data = {
            "chat_id": config["CHAT_ID"], 
            "text": message
        }
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Telegram message sent successfully")
        else:
            print(f"⚠️ Telegram API returned status code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Telegram send timeout")
    except requests.exceptions.ConnectionError:
        print("❌ Telegram connection error")
    except Exception as e:
        print(f"❌ Telegram send error: {e}")

def load_state(state_file):
    """
    โหลดสถานะเดิมจากไฟล์
    Args:
        state_file (str): path ของไฟล์ที่เก็บสถานะ
    Returns:
        dict: สถานะที่โหลดมา หรือ dict ว่างหากไม่มีไฟล์
    """
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading state: {e}")
    return {}

def save_state(state, state_file):
    """
    บันทึกสถานะปัจจุบันลงไฟล์
    Args:
        state (dict): สถานะที่ต้องการบันทึก
        state_file (str): path ของไฟล์ที่จะบันทึก
    """
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

def run_monitoring_cycle(config):
    """
    รันการตรวจสอบหนึ่งรอบ
    Args:
        config (dict): การตั้งค่าทั้งหมด
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"--- SD-WAN Check: {now} ---")

    # 1. เช็คสถานะทุกเส้น
    link_results = {}
    for name, ip in config["WAN_LINKS"].items():
        is_up = check_ping(ip)
        link_results[name] = is_up
        print(f"[{'✅' if is_up else '❌'}] {name} ({ip})")

    # 2. วิเคราะห์ภาพรวม
    current_summary = analyze_network(link_results)
    print(f"📊 Network Status: {current_summary}")

    # 3. โหลดความจำเดิมมาเทียบ
    last_state = load_state(config["STATE_FILE"])
    last_summary = last_state.get("SUMMARY", "NORMAL")

    # 4. ตัดสินใจแจ้งเตือน
    alert_message = ""
    if current_summary == "CRITICAL" and last_summary != "CRITICAL":
        alert_message = f"🚨 **วิกฤต! โรงงานดับสนิท** 🚨\nเวลา: {now}\nตรวจสอบด่วน!"
    elif current_summary == "FAILOVER" and last_summary == "NORMAL":
        alert_message = f"⚠️ **แจ้งเตือน: Main ล่ม!**\nวิ่งเส้นสำรอง ETL 🔄\nเวลา: {now}"
    elif current_summary == "NORMAL" and last_summary != "NORMAL":
        alert_message = f"✅ **ระบบกลับมาปกติแล้ว**\nLTC Online 🚀\nเวลา: {now}"

    # 5. ส่งแจ้งเตือนหากมีการเปลี่ยนแปลงสถานะ
    if alert_message:
        print(f"📤 Sending Alert: {current_summary}")
        send_telegram(alert_message, config)
    else:
        print("🔕 No status change, no alert sent")
    
    # 6. บันทึกสถานะปัจจุบัน
    new_state = {
        "SUMMARY": current_summary, 
        "LINKS": link_results,
        "LAST_CHECK": now
    }
    save_state(new_state, config["STATE_FILE"])
    print("-" * 50)

def main():
    """
    ฟังก์ชันหลักที่รันการตรวจสอบแบบ loop ตลอดกาล
    """
    print("🤖 Miner Bot Started...")
    print("📡 Monitoring SD-WAN Links...")
    
    # โหลดการตั้งค่า
    config = load_config()
    print(f"⏰ Check interval: {config['CHECK_INTERVAL']} seconds")
    print(f"📁 State file: {config['STATE_FILE']}")
    print(f"🔗 Monitoring {len(config['WAN_LINKS'])} links")
    print("=" * 50)
    
    # Loop ตลอดกาล
    while True:
        try:
            run_monitoring_cycle(config)
            time.sleep(config["CHECK_INTERVAL"])
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error in main loop: {e}")
            print("⏳ Waiting 60 seconds before retry...")
            time.sleep(60)

# --- 🚀 เริ่มต้นการทำงาน ---
if __name__ == "__main__":
    main()