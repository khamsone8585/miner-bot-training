import os
import datetime

target_ips = ["8.8.8.8","1.1.1.1","192.168.0.0"]

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"------- Start Checking at {now} -----")

for ip in target_ips:
	response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")

	if response == 0:
		print(f"[{ip}] :  is ONLINE !!!")
	else:
		print(f"[{ip}] : is DEAD (check Now!)")

print("-------------------------------------------")

