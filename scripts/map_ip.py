import plotly.graph_objects as go
from os.path import join, exists, splitext
from os import makedirs, listdir
from json import load
from graph_info import Graph
import ipinfo

traces_folder = join("..", "traces")

images_folder = join("..", "images")

def check_folder(foldername):
    if not exists(foldername):
        makedirs(foldername)

check_folder(images_folder)

def mapsInit(fig):

    fig.update_layout(
    margin ={'l':50,'t':50,'b':50,'r':50},
    mapbox = {
        'center': {'lon': 0, 'lat': 0},
        'style': "stamen-terrain",
        'center': {'lon': 0, 'lat': 0},
        'zoom': 1})

def addRoute(fig, name, localite, city):
    '''
    name --> (str) name of the line
    position --> (tuple) ((lon1,lon2), (lat1,lat2))
    '''
    lonPath = localite[0]
    latPath = localite[1]

    fig.add_trace(go.Scattermapbox(
        name = name,
        text = city,
        mode = "markers+lines",
        lon = lonPath,
        lat = latPath,
        marker = {'size':10}))

def mark(fig ,markName, position,name='My IP'):
    '''
    position --> (tuple) (lon,lat)
    '''
    lonPath = position[0]
    latPath = position[1]
    fig.add_trace(go.Scattermapbox(
        name = name,
        text = markName,    
        mode = "markers+text",
        lon = (lonPath,),
        lat = (latPath,),
        marker = {'size': 15}
        ))

if __name__ == "__main__":
    fig = go.Figure()
    mapsInit(fig)

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

    for node in graph.nodes:
        hostname = graph.names.get(node, '')
        if not hostname:
            hostname = ipinfo.get_hostname(node)
        if hostname:
            mark(fig, ipinfo.get_org(node), ipinfo.get_loc(node), node)
    
    # for (n1, n2), value in graph.edges.items():
    #     n1_loc = ipinfo.get_loc(n1)
    #     n2_loc = ipinfo.get_loc(n2)
    #     addRoute(fig, n1, tuple(zip(n1_loc,n2_loc)), ipinfo.get_city(n1))


    fig.write_image(join(images_folder,"map.png"))