from os.path import join, exists, splitext
from os import makedirs, listdir
from json import load
from graph_info import Graph

traces_folder = join("..", "traces")

images_folder = join("..", "images")

def check_folder(foldername):
    if not exists(foldername):
        makedirs(foldername)

check_folder(images_folder)

def graph_apa(asn, file_image):
    for address in listdir(traces_folder):
        all_time = listdir(join(traces_folder, address))
        graph = Graph()
        for time_stamp in all_time:
            file = join(traces_folder, address, time_stamp)
            with open(file) as f:
                graph.from_json(load(f))
        max_tsp = max(map(lambda x: int(splitext(x)[0]), all_time))
        if not file_image:
            image_file = join(images_folder, "{}_{}.png".format(address, max_tsp))
        else:
            image_file = join(images_folder, file_image)
        if asn:
            graph.as_to_graphviz().draw(image_file)
        else:
            graph.draw(image_file)


def graph_aio(asn, file_image):
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
        graph.draw(image_file)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse trace route json')
    parser.add_argument("-a", "--aio", action="store_true")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("-s", "--asn", action="store_true")
    parser.add_argument("-f", default=None)

    args = parser.parse_args()
    if args.local:
        images_folder += "_local"
        traces_folder += "_local"
    check_folder(images_folder)
    if args.aio:
        graph_aio(args.asn, args.f)
    else:
        graph_apa(args.asn, args.f)