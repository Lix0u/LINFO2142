from urllib.request import urlopen
from json import load, dump

IP_INFO = {}

def cache(func):
    def wrapper(*args, **kwargs):
        cache_load()
        r = func(*args, **kwargs)
        cache_save()
        return r
    return wrapper

def cacheIpInfo(func):
    global IP_INFO
    def wrapper(addr=""):
        if addr in IP_INFO:
            return IP_INFO[addr]
        info = func(addr)
        IP_INFO[addr] = info
        return info
    return wrapper

def cache_load(filename="ipinfo.json"):
    global IP_INFO
    try:
        if len(IP_INFO) == 0:
            with open(filename) as f:
                IP_INFO = load(f)
    except:
        pass

def cache_save(filename="ipinfo.json"):
    global IP_INFO
    with open(filename, "w") as f:
        dump(IP_INFO, f)

def checkIPv4(addr):
    try:
        for i in addr.split("."):
            int(i)
    except:
        return False
    return True

def get_org(addr):
    return get_org_bogon(ipInfo(addr))

def get_hostname(addr):
    return ipInfo(addr).get("hostname", "")

@cacheIpInfo
def ipInfo(addr=''):
    if not checkIPv4(addr):
        return {}
    if addr == '':
        url = 'https://ipinfo.io/json'
    else:
        url = 'https://ipinfo.io/' + addr + '/json'
    res = urlopen(url)
    if res == None:
        return {}
    data = load(res)
    if data == None:
        return {}
    return data


def get_all_ip(from_file, to_file, a=False):
    maxi_dict = {}
    if a:
        with open(to_file) as f:
            maxi_dict = load(f)

    def recur(d):
        if isinstance(d, dict):
            for k,v in d.items():
                if k == "name" or k == "src" or k == "dst":
                    if v in maxi_dict:
                        pass
                        # print(v, "in double")
                    else:
                        maxi_dict[v] = ipInfo(v)
                recur(v)
        elif isinstance(d, (list, tuple)):
            for v in d:
                recur(v)

    with open(from_file) as f:
        data = load(f)
        recur(data)
    
    with open(to_file, "w") as f:
        dump(maxi_dict, f)


def get_org_bogon(info):
    if info is None:
        return "No info"
    if "bogon" in info and info["bogon"]:
        return "bogon"
    if "org" in info:
        return info["org"]
    return "No info"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse trace route json and get info on all IP address')
    parser.add_argument('trace_filename', help="the output file from dublin traceroute")
    parser.add_argument('output_filename')
    parser.add_argument('-a',
                        action='store_true',
                        help="append the current output file")

    args = parser.parse_args()
    get_all_ip(args.trace_filename, args.output_filename, args.a)

