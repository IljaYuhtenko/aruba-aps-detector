import csv
import yaml
import getpass
from netmiko import ConnectHandler
import re
import os.path


def parse_line(line):
    """
    This function is needed to parse one-liner from the controller and extract the information we need

    :param line: a one line of output from "show ap database long" command
    :return: object, representing AP and it's key values, like MAC-address or given name
    """
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
    """
    This function is needed to go all over the list of APs comparing their serial numbers to make a match

    :param aps: a list of objects, that represent the APs that we are looking for
    :param ap: an object, representing one of the APs found on the controller
    :return: an index of ap in aps if there is any
    """
    for i, v in enumerate(aps):
        if v["serNum"] == ap["serNum"]:
            return i
    return -1


# First, we need to read the list of APs that we are looking for
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

# Second, we need to read task parameters
# That is, controller address and APs group
with open("params.yml") as f:
    params = yaml.safe_load(f)

# Third, we ask for auth parameters for the given controller
user = input(f"User for {params['controller']}: ")
passwd = getpass.getpass(f"Password for {params['controller']}: ")
controller = {
    "device_type": "aruba_os",
    "host": params["controller"],
    "username": user,
    "password": passwd,
    "secret": passwd
}

# Fourth, we log in and query the controller
# We are looking for every AP in the given group
with ConnectHandler(**controller) as ssh:
    ssh.enable()
    ssh.send_command("no paging")
    target_aps = ssh.send_command(f"show ap database long group {params['group']}")

# Then, we go line after line, not taking into account any garbage lines
i = 0
lines = target_aps.split("\n")
while i < len(lines):
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
    found = find_aruba(aps, ap)
    if found != -1:
        print(f"Found AP num. {found + 1}")
        aps[found]["mac"] = ap["mac"]
        aps[found]["name"] = ap["name"]
    i += 1

# Last one, we print our results to file
if os.path.exists("found.txt"):
    mode = 'w'
else:
    mode = 'x'
with open("found.txt", mode) as f:
    writer = csv.DictWriter(f, fieldnames=list(aps[0].keys()), quoting=csv.QUOTE_MINIMAL, delimiter=";")
    for ap in aps:
        writer.writerow(ap)
