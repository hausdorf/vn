# Copyright 2011
# Human Language Technology Center of Excellence
# Johns Hopkins University
# Author: Glen A. Coppersmith [coppersmith@jhu.edu]
# Author: James Dennis [jdennis@gmail.com]


from __future__ import division

from arbreapp.hltlib.constants import *
from arbreapp.hltlib.divergences import *
from arbreapp.hltlib.wch import *

from arbreapp.mailman.queries import find_emails, find_communications


def add_communication_to_edgelist(edgelist, communication,
                                  induced_subgraph=None,
                                  disallow_self_loops=True):
    """Process the single communication (output from Mongo), and add it to the
    aggregating edgelist appropriately.

    If induced_subgraph is specified, only do so for the vertices listed in
    induced subgraph.

    NB: This alone is an inefficient approach for small subgraphs, for better
    performance, be certain to use 'find_communications_by_subgraph' instead of
    a generic find_communications query.

    By default we disallow self loops to be created. Turn on at your own risk of
    headache.

    Return types are not currently used, but indicate whether or not the edge
    was added to the edgelist.
    """

    # Filter out messages not in the specified induced subgraph
    if not induced_subgraph == None:
        if not communication['to'] in induced_subgraph or \
           not communication['ffrom'] in induced_subgraph:
            return False

    # Filter out messages that would induce self-loops
    if disallow_self_loops and communication['to'] == communication['ffrom']:
        return False
        
    vertices = ao(communication['to'], communication['ffrom'])

    if vertices in edgelist:
        edgelist[vertices]['weight'] += 1
        edgelist[vertices]['message_ids'].append( communication['message_id'])
    else:
        edgelist[vertices] = {}
        edgelist[vertices]['weight'] = 1
        edgelist[vertices]['message_ids'] = [ communication['message_id'] ]
    return True


def add_attributes_to_edgelist(db, edgelist, edge_key, message_id,
                               edge_attribute_names, source='maildir'):
    """Given an existing edgelist, a message to pull attributes from, the names
    in the database of the attributes to be pulled, and the source of the
    emails, query the db and add the requested attributes to the edgelist.
    """
    cursor = find_emails(db, source=source, message_id=message_id)

    email = cursor.next() # Only get one email -- others should be dups
    for edge_attribute_name in edge_attribute_names:
        this_attribute = email[edge_attribute_name]
        #print edge_attribute_name, this_attribute
        if edge_attribute_name in edgelist[edge_key]:
            edgelist[edge_key][edge_attribute_name].append(this_attribute)
        else:
            edgelist[edge_key][edge_attribute_name] = [this_attribute]
        

def edgelist_from_communications_by_subgraph(db, vertices, source='maildir',
                                             edge_attributes=[], count=50,
                                             for_networkx=True,
                                             start_date="9/24/2001",
                                             end_date="2/4/2002"):
    """Queries the db for the edges (and associated attributes) for the subgraph
    induced by vertices.

    To accomplish this, query for all messages where 'ffrom' is one of the
    vertices, then filter out the messages where none of the vertices in 'to'
    are also in the vertices list.

    edge_attributes net you additional information added to the edgelist.
    
    NB: this is off the communications collection so many email-specific things
    are missing (e.g. 'body' or 'ldc_knn_topic'). To get this additional
    information, use add_attributes_to_edgelist

    TODO: make this transparent to the API user, so we check to see which
    attributes are not available with the current return and query for the rest.
    --GAC
    
    [JD - is there a smarter way to do this with a single query instead of one
    to db.communications and then one to db.email?]
    
    We return a weighted, attributed edgelist, ostensibly for ingestion into
    NetworkX.
    """

    edgelist = {}
    
    for vertex in vertices:
        cursor = find_communications(db, source=source, ffrom=vertex, count=count,
                                     start_date=start_date, end_date=end_date)
        
        # Sets up the edges only, attributes added in the next step
        [add_communication_to_edgelist(edgelist, com)
         for com in cursor if com['to'] in vertices]

    # Otherwise skip time consuming lookups        
    if len(edge_attributes) > 0:
        # loop over edges present in the subgraph
        for edge_key in edgelist.keys(): 
            for message_id in edgelist[edge_key]['message_ids']:
                add_attributes_to_edgelist(db, edgelist, edge_key, message_id,
                                           edge_attributes, source=source)
        
    if for_networkx:
        # Run the prep command here to be able to feed directly --GAC
        return prepare_edgelist_for_nx(edgelist)
    else:
        return edgelist
