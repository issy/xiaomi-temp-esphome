#!/usr/bin/python3
import re
import os.path
from os import path

try:
    import yaml
except ModuleNotFoundError:
    print("Please install pyyaml using pip")
    print("Exiting...")
    exit()

for f in ['devices.txt','pairings.txt']:
    if path.exists(f) == False:
        print(f"Can't find {f}! Make sure it is in this directory")
        print("Exiting...")
        exit()
    else:
        continue

count = 0
devices = []

# define regexes
reg = re.compile("(.*):.\t(.*)")
first = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} - device list dump:")
mac = re.compile("Mac:\t.(.*)")

for line in open("devices.txt", "r"):
    line = line.strip()
    matches = reg.match(line)
    if line == '': # blank line
        continue
    if first.match(line): # first line of file
        continue
    if (count == 0) and (matches.group(1) == 'Did'): # first line of new entry
        count = 1
        sensor = {}
    if (count == 0) and (matches.group(1) != 'Did'): # not a temp sensor
        sensor = {}
        continue
    if (matches.group(1) == 'Model') and (matches.group(2) != 'miaomiaoce.sensor_ht.t2'): # if object is not temp sensor
        count = 0
        sensor = {}
        continue
    if (count == 1) and (reg.match(line)): # if object is a temp sensor
        if mac.match(line): # mac address
            sensor['Mac'] = mac.match(line).group(1)
            continue
        sensor[matches.group(1)] = matches.group(2)
        if matches.group(1) == 'FW': # end of temp sensor
            devices.append(sensor)
            count = 0
            continue

#print(devices)
print(f'gathered data for {len(devices)} devices')

masterReg = re.compile("Did:.\t(.*)\nToken:.\t(.*)\nBindkey:.\t(.*)\nMac:.\t(.*)")
pairings = []
f = open("pairings.txt", "r").read().split('\n\n\n')
for item in f:
    if item == '':
        continue
    count = 0
    data = {1:"Did",2:"Token",3:"Bindkey",4:"Mac"}
    if not masterReg.match(item):
        continue
    matches = masterReg.match(item)
    for x in devices: # make sure this is a valid temp sensor that matches up with our devices list
        if x['Did'] != matches.group(1):
            continue
        else:
            count = 1
            break
    if count != 1:
        continue

    sensor = {}
    for i in range(1,4):
        sensor[data[i]] = matches.group(i)
    pairings.append(sensor)

#print(pairings)
print(f"gathered data for {len(pairings)} pairings")

final = []
for device in devices:
    for pairing in pairings:
        if device['Did'] == pairing['Did']:
            sensor = {}
            sensor['name'] = device['Name']
            sensor['mac_address'] = device['Mac']
            sensor['bindkey'] = pairing['Bindkey']
            final.append(sensor)
            break
        else:
            continue
    continue

def gen_yaml(sensors):
    myYaml = {'sensor':[]}
    for sensor in sensors:
        data = {}
        data['platform'] = 'xiaomi_lywsd03mmc'
        data['mac_address'] = sensor['mac_address']
        data['bindkey'] = sensor['bindkey']
        data['temperature']['name'] = f"{sensor['name']} Temperature"
        data['humidity']['name'] = f"{sensor['name']} Humidity"
        data['battery_level']['name'] = f"{sensor['name']} Battery Level"
        myYaml['sensors'].append(data)
    return yaml.dump(myYaml)

for sensor in final:
    print(f"Found sensor with name \"{sensor['name']}\"")
    a = input("Do you want to change this name? [y/N]\n")
    if a.lower().strip() == 'y': # if change name
        while True:
            name = input("What do you want to call this sensor?\n")
            sure = input(f"Are you sure you want to rename {sensor['name']} to {name}? [Y/n]\n")
            if sure.lower().strip() in ['','y']: # rename and end loop
                name = name.capitalize() # assert capitalisation
                print(f"Renamed {sensor['name']} to {name}")
                sensor['name'] = name
                break

gen_yaml(final)