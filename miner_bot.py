import os
import sys
import datetime
import requests
import json
import time

def load_config():
    """
    โหลดการตั้งค่าต่างๆ จากตัวแปรสภาพแวดล้อม
    ฟังก์ชันนี้จะคืนค่าการตั้งค่าทั้งหมดที่จำเป็นสำหรับการทำงานของบอท
    ไม่มีค่า fallback สำหรับ credentials — ต้องตั้งค่าใน .env เท่านั้น
    """
    config = {
        "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),   # Required — no fallback
        "CHAT_ID": os.getenv("CHAT_ID"),                  # Required — no fallback
        "STATE_FILE": "/app/monitor_state.json",
        "KUMA_PUSH_URL": os.getenv("KUMA_PUSH_URL"),      # Optional — Uptime Kuma Push URL
        "WAN_LINKS": {
            "LTC_H3 (Main)": "202.137.147.163",
            "LTC_H4 (Main)": "202.137.147.164",
            "ETL_H3 (Backup)": "114.129.29.226",
            "ETL_H4 (Backup)": "114.129.29.227"
        },
        "CHECK_INTERVAL": 300  # 5 นาที
    }
    return config


def validate_config(config):
    """
    ตรวจสอบว่าค่าตั้งค่าที่จำเป็นทั้งหมดมีอยู่ก่อนที่บอทจะเริ่มทำงาน
    หากขาดค่าใดๆ จะพิมพ์ข้อผิดพลาดชัดเจนและออกจากโปรแกรมทันที
    """
    REQUIRED = ["TELEGRAM_TOKEN", "CHAT_ID"]
    missing = [key for key in REQUIRED if not config.get(key)]

    if missing:
        print("❌ STARTUP ERROR: Missing required environment variables:")
        for key in missing:
            print(f"   - {key} (must be set in .env)")
        print("💡 Copy .env.example to .env and fill in the values, then restart via Docker Compose.")
        sys.exit(1)

    print("✅ Config validated — all required environment variables are present.")

def check_ping(ip):
    """
    ตรวจสอบการเชื่อมต่อไปยัง IP address ด้วยคำสั่ง ping
    Args:
        ip (str): IP address ที่ต้องการตรวจสอบ
    Returns:
        bool: True หากสามารถ ping ได้, False หากไม่สามารถ ping ได้
    """
    import subprocess
    import re
    
    try:
        # Ping 4 ครั้ง รอ 1 วินาทีต่อครั้ง
        result = subprocess.run(
            ["ping", "-c", "4", "-W", "1", ip],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse packet loss from ping output
        packet_loss = 100  # Default to 100% loss if parsing fails
        if result.stdout:
            # Look for packet loss percentage in ping output
            loss_match = re.search(r'(\d+)% packet loss', result.stdout)
            if loss_match:
                packet_loss = int(loss_match.group(1))
        
        # Log ping results for debugging
        if packet_loss > 0:
            print(f"Ping to {ip} failed (Packet Loss: {packet_loss}%)")
        
        # Only consider link DOWN if packet loss is 100% (all 4 pings fail)
        return packet_loss < 100
        
    except subprocess.TimeoutExpired:
        print(f"Ping to {ip} failed (Packet Loss: 100%) - Timeout")
        return False
    except Exception as e:
        print(f"Ping to {ip} failed (Packet Loss: 100%) - Error: {e}")
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

def send_kuma_heartbeat(kuma_url):
    """
    ส่ง heartbeat ไปยัง Uptime Kuma Push Monitor เพื่อแจ้งว่าบอทยังทำงานอยู่
    Args:
        kuma_url (str): URL ของ Kuma Push Monitor
    """
    if not kuma_url:
        return  # ถ้าไม่มี URL ให้ข้าม
    
    try:
        response = requests.get(kuma_url, timeout=10)
        if response.status_code == 200:
            print("❤️ Sent Heartbeat to Kuma")
        else:
            print(f"⚠️ Kuma returned status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print("❌ Kuma heartbeat timeout")
    except requests.exceptions.ConnectionError:
        print("❌ Kuma connection error")
    except Exception as e:
        print(f"❌ Kuma heartbeat error: {e}")

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
    
    # โหลดและตรวจสอบการตั้งค่า — จะออกทันทีหาก .env ไม่ครบ
    config = load_config()
    validate_config(config)
    print(f"⏰ Check interval: {config['CHECK_INTERVAL']} seconds")
    print(f"📁 State file: {config['STATE_FILE']}")
    print(f"🔗 Monitoring {len(config['WAN_LINKS'])} links")
    print("=" * 50)
    
    # Loop ตลอดกาล
    while True:
        try:
            run_monitoring_cycle(config)
            
            # ส่ง heartbeat ไปยัง Uptime Kuma หลังจากการตรวจสอบเสร็จสิ้น
            if config["KUMA_PUSH_URL"]:
                try:
                    response = requests.get(config["KUMA_PUSH_URL"], timeout=10)
                    if response.status_code == 200:
                        print("❤️ Sent Heartbeat to Kuma")
                    else:
                        print(f"⚠️ Kuma returned status code: {response.status_code}")
                except Exception as e:
                    print(f"❌ Kuma heartbeat failed: {e}")
            
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