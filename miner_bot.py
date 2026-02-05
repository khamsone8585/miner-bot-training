import os
import datetime
import requests 
import json 


TELEGRAM_TOKEN = "8216223522:AAEvbQ_TU0I_iAIchfIQljGdK_K8FyNFezg"
CHAT_ID = "6417593756"

STATE_FILE = "/root/dev_train/monitor_state.json"

target_ips = ["8.8.8.8","1.1.1.1","8.8.4.4"]

def send_telegram_msg(message):
	url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
	data = {"chat_id": CHAT_ID, "text": message}

	try:
		requests.post(url, data=data)
	except Exception as e:
		print(f"Send Error: {e}")


def check_ip_status(ip_address):
	response = os.system(f"ping -c 1 -W 2  {ip_address} > //dev/null 2>&1")
	return response == 0

def load_state():
	if os.path.exists(STATE_FILE):
		with open(STATE_FILE, 'r') as f:
			return json.load(f)
	return {}

def save_state(state):
	with open(STATE_FILE, 'w') as f:
		json.dump(state, f)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"------- Start Checking at {now} -----")

last_status = load_state()
current_status = {}

for ip in target_ips:
	is_online = check_ip_status(ip)
	current_status[ip] = is_online
	
	was_online = last_status.get(ip, True)	

	if is_online and not was_online:
		print(f"[{ip}] :  is ✅ ກັບມາໃຊ້ງານແລ້ວ !!!")
		send_telegram_msg(f"✅ ສັນຍານກັບມາແລ້ວ!\nIP: {ip}\nເວລາ: {now}")
	elif not is_online and was_online:
		print(f"[{ip}] : is ຫາກະລົ້ມ !!!(ແຈ້ງເຕືອນ)")
		send_telegram_msg(f" ແຈ້ງເຕືອນດ່ວນ!\nIP: {ip} ຂາດການເຊື່ອມຕໍ່ !\nເວລາ: {now}")
	elif not is_online and not was_online:
		print(f"[{ip}] : ຍັງຄົງລົ້ມຢູ່ ")
	else:
		print(f"[{ip}] : ໃຊ້ງານປົກກະຕິ ກຳລັງທຳງານ")

save_state(current_status)
print("-------------------------------------------")

