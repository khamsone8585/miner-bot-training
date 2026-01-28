import os
import datetime

target_ip = "1.1.1.1"

response = os.system(f"ping -c 1 {target_ip} > /dev/null 2<&1")

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if response == 0:
	print(f"[{now}] IP: {target_ip} is ONLINE !!!")
else:
	print(f"[{now}] IP: {target_ip} is DEAD (check Now!)")
