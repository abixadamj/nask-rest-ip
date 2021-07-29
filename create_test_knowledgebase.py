import os
import json
import ipaddress
import psutil
from datetime import datetime
from random import randint, seed

seed(3333)
pid = os.getpid()
start = datetime.now()
step_time = datetime.now()
print(f"Starting at: {start}")
print(f"Memory consumed at start: {psutil.Process(pid).memory_info()[0] / 1000000}")
with open("test_knowledgebase.json", mode="a") as json_file:
    json_file.write("[\n")
    for main in range(100):
        print(f"Writing 1000: {main} / time elapsed: {datetime.now() - step_time}")
        for bucket in range(100):
            ipv4 = '.'.join(str(randint(0,255)) for _ in range(2)) + '.0.0/16'
            tag = chr(randint(65,100)) * randint(3,20)
            dict_ip = {"tag": tag, "ip_network": ipv4}
            json_file.write(f"  {json.dumps(dict_ip)},\n")
        step_time = datetime.now()
    else:
        json_file.write(f"  {json.dumps(dict_ip)}\n]")
        print(f"Memory consumed after loop: {psutil.Process(pid).memory_info()[0] / 1000000}")
print(f"total time : {datetime.now() - start}")
print(f"Memory consumed total: {psutil.Process(pid).memory_info()[0] / 1000000}")
