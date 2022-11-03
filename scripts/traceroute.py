from os.path import join, exists
from os import makedirs
import datetime
from json import load, dump

from dublintraceroute import DublinTraceroute

traces_folder = join("..", "traces")

list_ip_folder = join("ip.json")

# date_time = datetime.datetime.fromtimestamp(time_stamp)

def check_folder(foldername):
    if not exists(foldername):
        makedirs(foldername)

def run_address(list_address):
    for address in list_address:
        run_one(address)

def run_one(address):
    time_stamp = int(datetime.datetime.now().timestamp())
    if not address:
        return

    address_folder = join(traces_folder, address)
    check_folder(address_folder)

    current_file = join(address_folder, str(time_stamp) + ".json")

    print("Traceroute to", address)
    try:
        DublinTraceroute(address).traceroute().save(current_file)
    except:
        print("OH NO")

def get_ips(filename):
    with open(filename) as f:
        return load(f)

def save_ips(data, filename):
    with open(filename) as f:
        dump(data, f)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse trace route json')
    parser.add_argument('address', help="the address to trace", default="", nargs='?')

    args = parser.parse_args()
    if args.address:
        run_one(args.address)
    else:
        data = get_ips(list_ip_folder)
        while data["index"] < len(data["ip"]):
            run_one(data["ip"][data["index"]])
            data["index"] += 1
            data["currently_running"] = True
            data["last_try"] = int(datetime.datetime.now().timestamp())
            save_ips(data, list_ip_folder)

        data["index"] = 0
        data["currently_running"] = False
        data["last_finish"] = int(datetime.datetime.now().timestamp())
        save_ips(data, list_ip_folder)
        
        