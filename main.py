import csv
import yaml
import getpass
from netmiko import ConnectHandler
import re
import logging


logging.basicConfig(level=logging.INFO)


def parse_line(line):
    name, group, apType, ipAddr, status, flags, switchAddr, \
    standbyAddr, mac, serNum, *other = re.split(r' {2,}', line)
    ap = {
        "invNum": "",
        "serNum": serNum,
        "mac": mac,
        "name": name
    }
    return ap


def find_aruba(aps, ap):
    for i, v in enumerate(aps):
        if v["serNum"] == ap["serNum"]:
            return i
    return -1


aps = []
with open("arubs.csv") as f:
    reader = csv.reader(f, delimiter=";")
    for invNum, serNum in reader:
        ap = {
            "invNum": invNum.strip(),
            "serNum": serNum.strip(),
            "mac": "",
            "name": ""
        }
        aps.append(ap)

params = {}
with open("params.yml") as f:
    params = yaml.safe_load(f)

user = input(f"User for {params['controller']}: ")
passwd = getpass.getpass(f"Password for {params['controller']}: ")
controller = {
    "device_type": "aruba_os",
    "host": params["controller"],
    "username": user,
    "password": passwd,
    "secret": passwd
}

target_aps = ""
with ConnectHandler(**controller) as ssh:
    ssh.enable()
    ssh.send_command("no paging")
    target_aps = ssh.send_command(f"show ap database long group {params['group']}")

i = 0
lines = target_aps.split("\n")
while i < len(lines):
    if i % 10 == 0 and i > 0:
        print(f"Now on line {i}")
    if lines[i].find("AP Database") != -1:
        i += 4
        continue
    if lines[i].find("Flags: ") != -1:
        i += 8
        continue
    if lines[i].strip() == "":
        i += 1
        continue
    if lines[i].find("Port information is available only on 6xx.") != -1:
        i += 1
        continue
    if lines[i].find("Total APs:") != -1:
        i += 1
        continue
    ap = parse_line(lines[i])
    print(f"Processing {ap['name']}")
    found = find_aruba(aps, ap)
    if found != -1:
        aps[found]["mac"] = ap["mac"]
        aps[found]["name"] = ap["name"]
    i += 1

with open("found.txt", 'x') as f:
    writer = csv.DictWriter(f, fieldnames=list(aps[0].keys()), quoting=csv.QUOTE_NONNUMERIC, delimiter=";")
    for ap in aps:
        writer.writerow(ap)