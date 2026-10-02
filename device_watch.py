import json
import os
from device_scan import scan_network

KNOWN_FILE = "known_devices.json"

def load_known():
    if os.path.exists(KNOWN_FILE):
        with open(KNOWN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_known(known):
    with open(KNOWN_FILE, "w") as f:
        json.dump(known, f, indent=2)

known = load_known()
current = scan_network()

# Prothombar chalale
if not known:
    print("Prothombar chalachho. Ekhon jara connected tader 'chena' dhora hocche.")
    print("Dhore nao eder shobai tomar ba tomar poribarer device.\n")
    for mac, info in current.items():
        print(f"  {info['ip']:<16}{mac}  {info['hostname']}")
    save_known(current)
    print(f"\n{len(current)} ta device save hoyeche ({KNOWN_FILE})")
else:
    new_devices = {m: i for m, i in current.items() if m not in known}
    missing = {m: i for m, i in known.items() if m not in current}

    if new_devices:
        print("!!! NOTUN DEVICE PAWA GELO !!!")
        for mac, info in new_devices.items():
            print(f"  IP: {info['ip']}  MAC: {mac}  Name: {info['hostname']}")
        answer = input("\nEta ki tomar chena device? Save korbo? (y/n): ")
        if answer.lower() == "y":
            known.update(new_devices)
            save_known(known)
            print("Save hoyeche.")
        else:
            print("Shotorko thako! Router password bodlano bhalo.")
    else:
        print("Shob thik ache, kono notun device nai.")

    if missing:
        print(f"\n(Ekhon offline: {len(missing)} ta chena device)")