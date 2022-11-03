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

for address in listdir(traces_folder):
    all_time = listdir(join(traces_folder, address))
    graph = Graph()
    for time_stamp in all_time:
        file = join(traces_folder, address, time_stamp)
        with open(file) as f:
            graph.from_json(load(f))
    max_tsp = max(map(lambda x: int(splitext(x)[0]), all_time))
    image_file = join(images_folder, "{}_{}.png".format(address, max_tsp))
    graph.draw(image_file)


