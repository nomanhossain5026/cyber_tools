import socket
import subprocess
import platform
import re
import ipaddress
from concurrent.futures import ThreadPoolExecutor

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()

def ping_once(ip):
    system = platform.system()
    if system == "Windows":
        cmd = ["ping", "-n", "1", "-w", "500", ip]
    elif system == "Darwin":  # Mac
        cmd = ["ping", "-c", "1", "-W", "500", ip]
    else:  # Linux
        cmd = ["ping", "-c", "1", "-W", "1", ip]
    try:
        subprocess.run(cmd, capture_output=True, timeout=3)
    except subprocess.TimeoutExpired:
        pass

def read_arp_table():
    output = subprocess.run(["arp", "-a"], capture_output=True, text=True).stdout
    devices = {}
    for line in output.splitlines():
        ip_match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", line)
        mac_match = re.search(r"((?:[0-9a-fA-F]{1,2}[:-]){5}[0-9a-fA-F]{1,2})", line)
        if ip_match and mac_match:
            ip = ip_match.group(1)
            # MAC ke ekta format e anà (aa:bb:cc:dd:ee:ff)
            parts = re.split(r"[:-]", mac_match.group(1))
            mac = ":".join(p.zfill(2) for p in parts).lower()
            # broadcast ar multicast bad dao
            if mac == "ff:ff:ff:ff:ff:ff" or mac.startswith("01:00:5e"):
                continue
            devices[ip] = mac
    return devices

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except OSError:
        return "Unknown"

def scan_network():
    local_ip = get_local_ip()
    if not local_ip:
        print("Network e connected nao, Wi-Fi check koro.")
        return {}

    # Dhore nichhi /24 network (192.168.0.0/24 type)
    network = ipaddress.ip_network(local_ip + "/24", strict=False)
    print(f"Tomar IP      : {local_ip}")
    print(f"Scan korchi   : {network}  (ektu somoy lagbe...)\n")

    ips = [str(ip) for ip in network.hosts()]

    # 1) shobaike ping kore ARP table bhore nao
    with ThreadPoolExecutor(max_workers=60) as pool:
        list(pool.map(ping_once, ips))

    # 2) ARP table pore, shudhu amader network er IP rakho
    arp = read_arp_table()
    found = {ip: mac for ip, mac in arp.items() if ip in ips}

    # 3) hostname ber koro
    with ThreadPoolExecutor(max_workers=30) as pool:
        names = dict(zip(found.keys(), pool.map(get_hostname, found.keys())))

    result = {}
    for ip, mac in found.items():
        result[mac] = {"ip": ip, "hostname": names[ip]}
    return result

if __name__ == "__main__":
    devices = scan_network()

    print(f"{'IP':<16}{'MAC Address':<20}Hostname")
    print("-" * 60)
    for mac, info in sorted(devices.items(), key=lambda x: tuple(map(int, x[1]["ip"].split(".")))):
        print(f"{info['ip']:<16}{mac:<20}{info['hostname']}")

    print(f"\nMot {len(devices)} ta device pawa gelo.")
    