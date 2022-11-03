from os.path import join, exists
from os import makedirs
import datetime
from json import load

from dublintraceroute import DublinTraceroute

traces_folder = join("..", "traces")

list_ip_folder = join("ip.json")

# date_time = datetime.datetime.fromtimestamp(time_stamp)

def check_folder(foldername):
    if not exists(foldername):
        makedirs(foldername)

with open(list_ip_folder) as f:
    list_address = load(f)

for address in list_address:
    if not address:
        continue
    address_folder = join(traces_folder, address)
    check_folder(address_folder)
    time_stamp = int(datetime.datetime.now().timestamp())
    current_file = join(address_folder, str(time_stamp) + ".json")

    print("Traceroute to", address)
    try:
        DublinTraceroute(address).traceroute().save(current_file)
    except:
        print("OH NO")