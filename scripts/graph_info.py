import json
import random
try:
    import scripts.ipinfo as ipinfo
except ModuleNotFoundError:
    import ipinfo

@ipinfo.cache
def info_to_graphviz(traceroute, no_rtt=False):
    '''
    Convert a traceroute to a graphviz object.

    This method creates a GraphViz object from the output of
    DublinTraceroute.traceroute(), suitable for plotting.

    Example:
    >>> dub = DublinTraceroute(12345, 33434, "8.8.8.8")
    >>> results = dub.traceroute()
    >>> graph = to_graphviz(results)
    >>> graph.draw('traceroute.png')
    >>> graph.write('traceroute.dot')
    '''
    # importing here, so if pygraphviz is not installed it will not fail at
    # import time
    import pygraphviz
    
    graph = pygraphviz.AGraph(strict=False, directed=True)
    graph.node_attr['shape'] = 'ellipse'
    graph.graph_attr['rankdir'] = 'BT'

    # create a dummy first node to add the source host to the graph
    # FIXME this approach sucks
    for flow, hops in traceroute['flows'].items():
        src_ip = hops[0]['sent']['ip']['src']
        firsthop = {}
        hops = [firsthop] + hops
        color = random.randrange(0, 0xffffff)

        previous_nat_id = 0
        for index, hop in enumerate(hops):

            # add node
            if index == 0:
                # first hop, the source host
                nodename = src_ip
                org = ipinfo.get_org(nodename)
                nodeattrs = {"shape":'rectangle',
                            "label":"{ip}\n{org}".format(ip=nodename, org=org)}

                graph.add_node(nodename)
                graph.get_node(nodename).attr.update(nodeattrs)
            else:
                # all the other hops
                received = hop.get('received', None)
                nodeattrs = {}
                if received is None:
                    nodename = 'NULL{idx}'.format(idx=index)
                    nodeattrs['label'] = '*'
                else:
                    nodename = received['ip']['src']
                    if hop['name'] != nodename:
                        hostname = '\n{h}'.format(h=hop['name'])
                    else:
                        hostname = ''

    
                    org = ipinfo.get_org_org_bogon(ipinfo.ipInfo(nodename))
                    nodeattrs['label'] = '{ip}{name}\n{icmp}\n{org}'.format(
                        ip=nodename,
                        name=hostname,
                        icmp=received['icmp']['description'],
                        org=org,
                    )
                if index == 0 or hop['is_last']:
                    nodeattrs['shape'] = 'rectangle'
                graph.add_node(nodename)
                graph.get_node(nodename).attr.update(nodeattrs)

            # add edge
            try:
                nexthop = hops[index + 1]
            except IndexError:
                # This means that we are at the last hop, no further edge
                continue

            next_received = nexthop.get('received', None)
            edgeattrs = {'color': '#{c:x}'.format(c=color), 'label': ''}
            if next_received is None:
                next_nodename = 'NULL{idx}'.format(idx=index + 1)
            else:
                next_nodename = next_received['ip']['src']
            if index == 0:
                u = nexthop['sent']['udp']
                edgeattrs['label'] = 'srcport {sp}\ndstport {dp}'.format(sp=u['sport'], dp=u['dport'])
            rtt = nexthop['rtt_usec']
            try:
                if previous_nat_id != nexthop['nat_id']:
                    edgeattrs['label'] += '\nNAT detected'
                previous_nat_id = hop['nat_id']
            except KeyError:
                pass
            if not no_rtt:
                if rtt is not None:
                    edgeattrs['label'] += '\n{sec}.{usec} ms'.format(
                        sec=rtt // 1000, usec=rtt % 1000)
            graph.add_edge(nodename, next_nodename)
            graph.get_edge(nodename, next_nodename).attr.update(edgeattrs)

    graph.layout()
    graph.layout('dot')
    return graph


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.names = {}
    
    def add_node(self, nodename):
        self.nodes[nodename] = self.nodes.get(nodename, 0) + 1
    
    def add_edge(self, nodename, next_node):
        self.edges[(nodename, next_node)] = self.edges.get((nodename, next_node), 0) + 1
    
    def add_hostname(self, nodename, hostname):
        if nodename in self.names and self.names[nodename]:
            return
        self.names[nodename] = hostname
    
    def save(self, filename):
        data = {"nodes":self.nodes, "edges":self.edges, "names":self.names}
        with open(filename, "w") as f:
            json.dump(data, f)

    def load(self, filename):
        with open(filename) as f:
            data = json.load(f)
            self.nodes = data["nodes"]
            self.edges = data["edges"]
            self.names = data["names"]


    def from_json(self, traceroute):
        for _, hops in traceroute['flows'].items():
            
            src = hops[0]['sent']['ip']['src']
            self.add_node(src)

            for index, hop in enumerate(hops):
                def get_name(i, h):
                    received = h.get('received', None)
                    if received is None:
                        return f'NULL{i}', ''
                    name = received['ip']['src']
                    host = ""
                    if h['name'] != name:
                        host = h["name"]
                    return name, host

                nodename, hostname = get_name(index, hop)
                self.add_node(nodename)
                self.add_hostname(nodename, hostname)

                if index == 0:
                    self.add_edge(src, nodename)

                if hop.get("is_last", False):
                    continue

                nexthop = hops[index + 1]
                next_nodename, hostname = get_name(index + 1, nexthop)
                self.add_hostname(next_nodename, hostname)

                self.add_edge(nodename, next_nodename)

    @ipinfo.cache
    def to_graphviz(self):
        import pygraphviz
        graph = pygraphviz.AGraph(strict=False, directed=True)
        graph.node_attr['shape'] = 'ellipse'
        graph.graph_attr['rankdir'] = 'BT'
        for node in self.nodes:
            hostname = self.names.get(node, '')
            if not hostname:
                hostname = ipinfo.get_hostname(node)
            graph.add_node(node, label=f"{node}\n{ipinfo.get_org(node)}\n{hostname}")
        
        for (n1, n2), value in self.edges.items():
            graph.add_edge(n1, n2, label=str(value))

        graph.layout('dot')
        return graph
    
    @ipinfo.cache
    def to_graphviz_color(self):
        import pygraphviz
        graph = pygraphviz.AGraph(strict=False, directed=True)
        graph.node_attr['shape'] = 'ellipse'
        graph.graph_attr['rankdir'] = 'BT'
        for node in self.nodes:
            hostname = self.names.get(node, '')
            if not hostname:
                hostname = ipinfo.get_hostname(node)
            org = ipinfo.get_org(node)
            color = "#FFFFFF"
            colorScheme = {
                "ovh":"#25FF25",
                "google":"#AAAAAA",
                "no info":"#FFDDDD",
                "bogon":"#BBCCFF",
                "globalcom":"#2BD1F2"
            }
            for orgName, colorCode in colorScheme.items():
                if orgName.lower() in org.lower():
                    color = colorCode
                    break
            graph.add_node(node, label=f"{node}\n{org}\n{hostname}", fillcolor=color, style="filled", color="#000000")
        
        for (n1, n2), value in self.edges.items():
            graph.add_edge(n1, n2, label=str(value))

        graph.layout('dot')
        return graph


    @ipinfo.cache
    def as_to_graphviz(self):
        import pygraphviz
        graph = pygraphviz.AGraph(strict=False, directed=True)
        graph.node_attr['shape'] = 'ellipse'
        graph.graph_attr['rankdir'] = 'BT'

        edges = self.as_graph()

        nodes = set()

        for n1, n2 in edges:
            nodes.add(n1)
            nodes.add(n2)
            graph.add_edge(n1,n2)
        
        for node in nodes:
            # graph.add_node(node)
            graph.add_node(node, label=ipinfo.get_org(node))
      

        graph.layout('dot')
        return graph

    def as_graph(self):
        edges_to = {}
        for (n1, n2), value in self.edges.items():
            l = edges_to.get(n1, list())
            l.append(n2)
            edges_to[n1] = l
      
        # Filter child
        keys = list(edges_to.keys())
        i = 0

        while i < len(keys):
            n1 = keys[i]
            from_n1 = edges_to[n1]
            n1_info = ipinfo.get_org(n1)
            change = False
            for n2 in from_n1:
                n2_info = ipinfo.get_org(n2)
                if n1_info == n2_info:
                    change = True
                    if n2 in keys:
                        keys.remove(n2)
                    if n2 in edges_to:
                        from_n1.remove(n2)
                        for tps_n1, tps_l in edges_to.items():
                            if tps_n1 == n1 or tps_n1 == n2:
                                continue
                            if n2 in tps_l :
                                tps_l.remove(n2)
                                tps_l.append(n1)
                        for nt in edges_to[n2]:
                            if nt != n1 and nt != n2 and nt not in from_n1:
                                from_n1.append(nt)
                    else:
                        i += 1

            if change == False:
                i += 1


        # Filter neighboor
        keys = list(edges_to.keys())
        i = 0

        while i < len(keys):
            n1 = keys[i]
            from_n1 = edges_to[n1]
            change = False
            for n2 in from_n1:
                n2_info = ipinfo.get_org(n2)
                for n3 in from_n1:
                    if n2 == n3:
                        continue
                    n3_info = ipinfo.get_org(n3)
                    if n2_info == n3_info:
                        if n3 in keys:
                            keys.remove(n3)
                        if n3 in edges_to:
                            from_n1.remove(n3)
                            for tps_n1, tps_l in edges_to.items():
                                if tps_n1 == n2 or tps_n1 == n3:
                                    continue
                                if n3 in tps_l :
                                    tps_l.remove(n3)
                                    tps_l.append(n2)
                            for nt in edges_to[n3]:
                                if nt != n2 and nt != n3 and nt not in from_n1:
                                    from_n1.append(nt)
                    
            if change == False:
                i += 1



        # Reverse the tree
        # and filter the normal tree
        edges_to_reverse = {}
        edges_to_filtered = {}
        for n1, l in edges_to.items():
            n1_info = ipinfo.get_org(n1)
            edges_to_filtered[n1] = []
            for n2 in l:
                n2_info = ipinfo.get_org(n2)
                if n1_info != n2_info:
                    list_n2 = edges_to_reverse.get(n2, list())
                    list_n2.append(n1)
                    edges_to_reverse[n2] = list_n2
                    edges_to_filtered[n1].append(n2)
        

        # Filter reverse way
        def get_end_leaf(node):
            l = edges_to_filtered.get(node, [])
            visited = {node}
            while len(l) > 0:
                node = None
                for j in l:
                    if j not in visited:
                        node = j
                        visited.add(j)
                        break
                l = edges_to_filtered.get(node, [])
            return node
        root = get_end_leaf(list(edges_to_filtered.keys())[0])
        translate = {n:n for n in edges_to_reverse.keys()}
        heap = [root]
        while len(heap) > 0:
            element = heap.pop(0)
            list_next_nodes = edges_to_reverse.get(element, [])
            already_seen = {}
            for next_node in list_next_nodes:
                node_info = ipinfo.get_org(next_node)
                if node_info not in already_seen:
                    already_seen[node_info] = next_node
                else:
                    translate[next_node] = already_seen[node_info]
                heap.append(next_node)
        
        new_edge_to = {}
        for n1, li in edges_to_reverse.items():
            next_li = new_edge_to.get(translate[n1], [])
            for n2 in li:
                next_li.append(translate.get(n2, n2))
            new_edge_to[translate[n1]] = next_li



        edges = {}
        for n1, l in new_edge_to.items():
            for n2 in l:
                # edges[(n1,n2)] = 0
                edges[(n2,n1)] = 0
        
        return edges
        
    def draw(self, filename):
        self.to_graphviz().draw(filename)





if __name__ == "__main__":
    # from dublintraceroute import DublinTraceroute, to_graphviz
    # dub = DublinTraceroute("142.250.204.4")
    # results = dub.traceroute()
    # graph = to_graphviz(results)
    # graph.draw('traceroute.png')
    
    with open("../test/test_json_parse.json") as f:
        data = json.load(f)
        my_graph = Graph()
        my_graph.from_json(data)

        # my_graph.draw("test_5.png")
        # my_graph.as_to_graphviz().draw("test_9b.png")
        my_graph.draw("../test/test_1.png")
        # try:
        # except Exception as e:
        #     print(e)

        # graph = info_to_graphviz(data)
        # graph.draw("test_2.png")
