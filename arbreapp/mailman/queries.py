import pymongo

import copy

from arbre.database import init_apply_all_indexes, gen_date_args
from arbre.graphs import prepare_edgelist_for_nx
from arbreapp.hltlib.constants import ao

###
### Collection Config
###

EMAIL_COLL = 'emails'
EDGES_COLL = 'edges'


###
### Index Handling
###

indexes = {
    ## Indexes for the email collection
    EMAIL_COLL: [
        [('source', pymongo.ASCENDING),
         ('message_id', pymongo.ASCENDING)],
        
        [('message_id', pymongo.ASCENDING)],
        
        [('date', pymongo.ASCENDING),
         ('source', pymongo.ASCENDING),
         ('ffrom', pymongo.ASCENDING)],
    ],

    ## Indexes for communications collection
    EDGES_COLL: [
        [('source', pymongo.ASCENDING),
         ('message_id', pymongo.ASCENDING)],
        
        [('message_id', pymongo.ASCENDING)],
        
        [('date', pymongo.ASCENDING),
         ('source', pymongo.ASCENDING),
         ('ffrom', pymongo.ASCENDING)],
    ],
}

apply_all_indexes = init_apply_all_indexes(indexes)


###
### Argument Handling
###

def _find_by_common(collection, fields=None, source=None, message_id=None,
                    start_date=None, end_date=None, ffrom=None, count=50,
                    page=0, **kw):
    """A `find` query handling system for the `email` collection.

    `source` should be either 'lucene' or 'maildir'.

    `message_id` should be a string that looks like this:

        <24283319.1075842034234.JavaMail.evans@thyme>

    `start_date` and `end_date` are milliseconds since January 1, 1970. If a
    string is provided for either, a conversion will take place. It can cover
    just about whatever you throw at it, but read the documentation for
    `gen_date_args` for more detail.

    The `count` flag defaults to 50, but you can set it to 0 to have no limit
    applied.

    Paging starts counting pages at 0.
    """
    query_dict = copy.deepcopy(kw)

    # At least one of these is required.
    if not source and not ffrom and not message_id:
        return None

    # Arrange fields to optimize index usage
    if source:
        query_dict['source'] = source
    if message_id:
        query_dict['message_id'] = message_id

    date_args = gen_date_args(start_date, end_date)
    if len(date_args.keys()) > 0:
        query_dict = {
            'date': date_args,
        }

    # Support less prominent indexes
    if ffrom:
        query_dict['ffrom'] = ffrom

    # run query and apply paging 
    db_cursor = collection.find(query_dict)
    db_cursor.limit(count) # limit(0) = no limit
    db_cursor.skip(page * count)
    
    return db_cursor


###
### Email Queries
###

def find_emails(db, **kwargs):
    """Accepts any keywords that `_find_by_common` accepts and simply calls
    `_find_by_common` with the email collection.
    """
    return _find_by_common(db[EMAIL_COLL], **kwargs)

def insert_email(db, email):
    """Accepts an `Email` instance and inserts the fields into MongoDB. It
    also updates the indexes on `EMAIL_COLL` after the insert.

    In addition to inserting the email, it generates the communication edge
    list and saves them.

    TODO The db save is done in chunks of 200. Investigate alternatives
    """
    email_id = db[EMAIL_COLL].insert(email.to_python())
    email.id = email_id

    edge_list = email.gen_edge_list(mongo_ready=True)
    insert_communication_edges(db, edge_list)

    apply_all_indexes(db, EMAIL_COLL)
    
    return email

def update_ldc_pair(db, msg_id, ldc, ldcknn):
    """Accepts a database connect, message id and two ldc values. It updates
    the matching message by `msg_id` in `db`.
    """
    # Pymongo supports regex queries by using a compiled expression
    #message_id_matcher = re.compile('%s' % msg_id)
    match_dict = {
        #'message_id': message_id_matcher,
        'message_id': '%s' % (msg_id),
    }
    update_dict = {
        '$set': {
            'ldc_topic': int(ldc),
            'ldc_knn_topic': int(ldcknn),
        }
    }
    try:
        print 'MSG ID:', msg_id, ' -- SET DICT:', update_dict
        # more info on update: http://bit.ly/gNXJ4u
        db[EMAIL_COLL].update(match_dict, update_dict, multi=True)
    except Exception,e:
        print e
        raise


###
### Edge Queries
###

def find_edges(db, **kwargs):
    """Accepts any keywords that `_find_by_common` accepts and simply calls
    `_find_by_common` with the communications collection.
    """
    return _find_by_common(db[EDGES_COLL], **kwargs)


def find_communications(db, **kwargs):
    """Accepts any keywords that `_find_by_common` accepts and simply calls
    `find_edges` and thus `_find_by_common` with the communications collection.
    """
    return find_edges(db, _cls='Email.MaildirEmail', **kwargs)
    

def insert_communication_edges(db, edge_list):
    """Takes a list of edges, as generated by Email.gen_edge_list, and stores
    them.

    It then updates the indexes for `EDGES_COLL`.
    """
    num_edges = len(edge_list)

    if(num_edges > 0):
        while num_edges > 0:
            edge_page = edge_list[:200] # 200 edges at a time
            db[EDGES_COLL].insert(edge_page)
            edge_list = edge_list[200:]
            num_edges = len(edge_list)

    apply_all_indexes(db, EDGES_COLL)


###
###  Graph Queries
###

def get_attributed_graph(db, vertices=None,
                         e_attributes=None,
                         v_attributes=None,
                         group_by_attribute=False,
                         **kw):
    """
    Build a graph from the database with edges attributed with attributes
    listed in `e_attributes` and vertices attributed with those in
    `v_attributes`.
    If `vertices` are specified, return only the subgraph induced on
    those vertices.
    By default, attributes are grouped by email, if `group_by_attribute`
    is True, group attributes together rather than emails.
    Further keywords (handled by `**kw` will be passed along as filters
    to `_find_by_common`)
    """

    vertex_attributes = {}
    if v_attributes:
        employees = find_employees(db,count=0)
        for employee in employees:
            this_vertex_attr = {}
            for v_attr in v_attributes:
                if v_attr in employee:
                    this_vertex_attr[v_attr] = employee[v_attr]
            vertex_attributes[employee] = this_vertex_attr

    #First, build the edgelist
    edgelist = {} #keyed by ao(v1,v2)

    def extract_email_attributes(email):
        this_email_attributes = {}
        for attr in e_attributes:
            if attr in email:
                this_email_attributes[attr] = email[attr]
        
    
    emails = _find_by_common(db[EMAIL_COLL], **kw)
    for email in emails:
        #Check first to see if it's a valid edge
        if 'to' in email and 'ffrom' in email:
            to = email['to']
            ffrom = email['ffrom']

            vertex_pair = ao(to, ffrom)
            
            if vertex_pair in edgelist:
                edgelist[vertex_pair]['weight'] += 1

                this_email_attributes = extract_email_attributes(email)
                        
                edgelist[vertex_pair]['attributes']. append(this_email_attributes)
            else:
                add_them = True
                if vertices: #If we are making an induced subgraph
                    if not to in vertices or not ffrom in vertices:
                        add_them = False
                if add_them:
                    val = {'weight':1}
                    val['attributes'] = extract_email_attributes(email)
                    edgelist[vertex_pair] = val

    #Turn the edgelist into an attributed networkx graph
    G = nx.Graph().add_edges_from( edgelist )

    #Add vertex attributes if they exist
    for vertex,attributes in vertex_attributes.items():
        if vertex in G.nodes():
            G.add_node(vertex,**attributes)
            """
            This could be accomplished by G.node[vertex]={keys,vals}, but this
            counterintuitive way actually compounds attributes instead of
            replacing them.
            """
    return G
                
        

    
