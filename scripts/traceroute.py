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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse trace route json')
    parser.add_argument('address', help="the address to trace", default="", nargs='?')

    args = parser.parse_args()
    if args.address:
        run_one(args.address)
    else:
        with open(list_ip_folder) as f:
            list_address = load(f)
        
        run_address(list_address)