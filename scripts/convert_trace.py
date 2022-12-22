from os.path import join, exists, splitext
from os import makedirs, listdir
from json import load, dump
import ipinfo
from graph_info import Graph

traces_folder = join("..", "traces")

images_folder = join("..", "images")

exclusif = ["5.135.137.253",
        "51.79.140.1",
        "141.94.18.1",
        "135.148.101.1",
        "51.210.158.1",
        "135.125.244.1",
        "145.239.28.1",
        "139.99.216.1",
        "51.79.100.1",
        "51.81.200.1",
        "51.89.228.1"]

def check_folder(foldername):
    if not exists(foldername):
        makedirs(foldername)

check_folder(images_folder)

def graph_apa(asn, file_image, coloring, only):
    for address in listdir(traces_folder):
        all_time = listdir(join(traces_folder, address))
        graph = Graph()
        for time_stamp in all_time:
            file = join(traces_folder, address, time_stamp)
            with open(file) as f:
                graph.from_json(load(f), only)
        max_tsp = max(map(lambda x: int(splitext(x)[0]), all_time))
        _image_folder = join(images_folder, "by_dest")
        check_folder(_image_folder)
        if not file_image:
            image_file = join(_image_folder, "{}_{}.png".format(address, max_tsp))
        else:
            image_file = join(_image_folder, file_image)
        if asn:
            graph.as_to_graphviz().draw(image_file)
        else:
            if coloring:
                graph.to_graphviz_color().draw(image_file)
            else:
                graph.draw(image_file)


def graph_aio(asn, file_image, coloring, filter):
    graph = Graph()
    for address in listdir(traces_folder):
        all_time = listdir(join(traces_folder, address))
        for time_stamp in all_time:
            file = join(traces_folder, address, time_stamp)
            with open(file) as f:
                try:
                    graph.from_json(load(f))
                except:
                    print(file)

    if not file_image:
        file_image = "ALL_IN_ONE.png"
    image_file = join(images_folder, file_image)
    if asn:
        graph.as_to_graphviz().draw(image_file)
    else:
        if filter:
            graph.to_graphviz_filtered().draw(image_file)
        elif coloring:
            graph.to_graphviz_color().draw(image_file)
        else:
            graph.draw(image_file)

def graph_exclu(file_image, coloring, filter, only):
    graph = Graph()
    for address in exclusif:
        all_time = listdir(join(traces_folder, address))
        for time_stamp in all_time:
            file = join(traces_folder, address, time_stamp)
            with open(file) as f:
                try:
                    graph.from_json(load(f), only) 
                except:
                    print(file)

    if not file_image:
        file_image = "ALL_IN_ONE.png"
    image_file = join(images_folder, file_image)

    if filter:
        graph.to_graphviz_filtered().draw(image_file)
    elif coloring:
        graph.to_graphviz_color().draw(image_file)
    else:
        graph.draw(image_file)
    with open("ip_failed.json","w") as f:
        try:
            dump(ipinfo.IP_FAILED, f)
        except:
            pass

def graph_to_dest(address, file_image, coloring, only):
    all_time = listdir(join(traces_folder, address))
    graph = Graph()
    for time_stamp in all_time:
        file = join(traces_folder, address, time_stamp)
        with open(file) as f:
            graph.from_json(load(f), only)
    max_tsp = max(map(lambda x: int(splitext(x)[0]), all_time))
    _image_folder = join(images_folder, "by_dest")
    check_folder(_image_folder)
    if not file_image:
        if not only:
            image_file = join(_image_folder, "{}_{}.png".format(address, max_tsp))
        else:
            image_file = join(_image_folder, "{}_{}_{}.png".format(address, only, max_tsp))
    else:
        image_file = join(_image_folder, file_image)
  
    if coloring:
        graph.to_graphviz_color().draw(image_file)
    else:
        graph.draw(image_file)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse trace route json')
    parser.add_argument("-a", "--aio", action="store_true", help="ALL IN ONE")
    parser.add_argument("--local", action="store_true", help="use local file")
    parser.add_argument("-s", "--asn", action="store_true", help="graph the AS")
    parser.add_argument("-f", default=None, help="Name of the output file")
    parser.add_argument("-r", default=None, help="Select the source")
    parser.add_argument("-d", default=None, help="Select the destination")
    parser.add_argument("-c", action="store_true", help="Color")
    parser.add_argument("-p", action="store_true", help="A restricted set of IP")
    parser.add_argument("-o", action="store_true", help="Keep Only OVH, NULL and bogon")

    args = parser.parse_args()
    if args.local:
        images_folder += "_local"
        traces_folder += "_local"
    check_folder(images_folder)
    if args.d:
        graph_to_dest(args.d, args.f, args.c, args.r)
    elif args.p:
        graph_exclu(args.f, args.c, args.o, args.r)
    elif args.aio:
        graph_aio(args.asn, args.f, args.c, args.o)
    else:
        graph_apa(args.asn, args.f, args.c, args.r)