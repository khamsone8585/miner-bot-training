import os
import datetime
import requests 

TELEGRAM_TOKEN = "8216223522:AAEvbQ_TU0I_iAIchfIQljGdK_K8FyNFezg"
CHAT_ID = "6417593756"

target_ips = ["8.8.8.8","1.1.1.1","192.168.99.99"]

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


now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"------- Start Checking at {now} -----")

for ip in target_ips:
	is_online = check_ip_status(ip)

	if is_online:
		print(f"[{ip}] :  is ONLINE !!!")
	else:
		print(f"[{ip}] : is DEAD (check Now!.....)")
		
		alert_msg = f" Warining \n Time: {now}\nIP: {ip} Disconnent !!!!"
		send_telegram_msg(alert_msg)
print("-------------------------------------------")

