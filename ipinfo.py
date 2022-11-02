from urllib.request import urlopen
from json import load, dump

def checkIPv4(addr):
    try:
        for i in addr.split("."):
            int(i)
    except:
        return False
    return True

def ipInfo(addr=''):
    if not checkIPv4(addr):
        return
    if addr == '':
        url = 'https://ipinfo.io/json'
    else:
        url = 'https://ipinfo.io/' + addr + '/json'
    res = urlopen(url)
    if res == None:
        return
    data = load(res)
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

