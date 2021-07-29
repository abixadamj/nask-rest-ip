import requests
import timeit

ip_list = [f"192.{a}.{b}.{c}" for a in range(100) for b in range(100) for c in range(100)]

def speed(lista: list):
    for ip in lista:
        response = requests.get(f"http://localhost:8000/ip-tags/{ip}")

start = 0
stop = 0

for _50 in range(0,999950, 50):
    start = _50
    stop = _50 + 50
    elapsed = timeit.Timer(lambda: speed(ip_list[start:stop]))
    print(f"Time for access 50 ip's: {elapsed.timeit(1)} seconds.")
