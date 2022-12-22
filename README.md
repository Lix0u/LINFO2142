# Equal-cost multi-path using Dublin traceroute

A graph with every hops found can be found [there](/images/every_hops.png)

For a graph with only the inside node of OVH can be found [there](/images/OVH_two_sources.png)

## Utilisation

You need to install the requirements that are in *scripts/requirement.txt*

To trace all ip launch the `trace.sh` script.

> Need to be run with **sudo** to work

It will restart where it stop in case of a error.

### Trace

`trace.sh` will run *traceroute.py* with the default argument. *traceroute.py* can be found in the *scripts* folder.

*traceroute.py* will save the traces in the *traces* folders, but it can have two arguments.

``python3 traceroute.py [address] [--local]``

> Also need to berun with **sudo**

If no address if given it will trace all the ip in the *ip.json* file.
If the local flag is put the trace will be save in a folder named *traces_local* in other case all the trace will be saved in a *traces* folder.

Inside the *traces* folders there are saved in a directory named after there ip, them in a json file, named with the timestamp from when there were traced.

### Graph

To make sens of the traces, there is *convert_trace.py* in the *scripts* folder

It will read the traces from the *traces* folder and write the images inside the *images* folder.

``python3 convert_trace.py [-a|--aio] [--local] [-f filename] [-r address_source] [-d address_destination] [-c] [-o]``

Without any argument, convert_trace will take every destination separetly and save each image in *images/by_dest* with the name *(dest)_(most_recent_timestamp).png*.

The -a | --aio is all in one, wich mean all destination in one graph. If -f not defined the images will be named *ALL_IN_ONE.png" and save in *images*

The --local will take the trace from *traces_local* instead of *traces* and save the images in *images_local* instead of *images*

The -f filename will overwrite the name of the image.

The -r is use to select only one source instead of the two by default. Can't be used with -a

The -d make an image of only one destination

The -c will put color one the graph. Really usefull (Recommended)

The -o (only work with -a) output only the hops from OVH.

Other parameter can be ignored.

## Description of the files

Inside the folder *scripts*:

