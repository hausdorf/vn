import networkx as nx
import cPickle as pickle


###
### Graph Management
###

def new_graph(edgelist):
    """Takes an iterable `edgelist` and creates a new networkx graph mapping
    each edge in the list to an nx node.
    """
    g = nx.Graph()
    # g.add_edges_from(edgelist)
    for edge in edgelist:
        g.add_edge(edge)
    return g

def save_graph(filename, g):
    """Saves a networkx graph to the filesystem by pickling it.
    """
    f = open(filename, 'w')
    pickled_g = pickle.dumps(g)
    f.write(pickled_g)
    f.close()
    return True

def load_graph(filename):
    """Loads a pickled networkx graph from the filesystem and returns it
    """
    f = open(filename, 'r')
    pickled_g = f.read()
    f.close()
    g = pickle.loads(pickled_g)
    return g
    
def prepare_edgelist_for_nx(edgelist):
    """Simply takes the edgelist dictionary where keys are vertex pairs
    and returns a generator of the format NetworkX handles to create
    an attributed, weighted graph.
    """
    return ((key[0],key[1],edgelist[key]) for key in edgelist.keys())
