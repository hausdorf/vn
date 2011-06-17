# Copyright 2010
# Human Language Technology Center of Excellence
# Johns Hopkins University
# Author: Glen A. Coppersmith [coppersmith@jhu.edu]

from __future__ import division
import networkx as nx

from arbreapp.hltlib.constants import *
from arbreapp.hltlib.divergences import *
from arbreapp.hltlib.wch import *
from arbreapp.hltlib.Enron_Estimation_Simulation import *

def matchedFilter_v1(G, vertex):
    candidates = getNodes2Out(G, vertex)
    candidateScores = []
    for candidate in candidates:
        score = scoreMatchedFilter_v1(G,vertex,candidate)
        candidateScores.append( [candidate, score] )
    return candidateScores

def matchedFilter_v2(G, vertex):
    candidates = getNodes2Out(G, vertex)
    candidateScores = []
    for candidate in candidates:
        score = scoreMatchedFilter_v2(G,vertex,candidate)
        candidateScores.append( [candidate, score] )
    return candidateScores
        
#Denominator = size of union of v1 and v2's neighborhood
def scoreMatchedFilter_v1(G,vertex1,vertex2):
    v1n = G.neighbors(vertex1)
    v2n = G.neighbors(vertex2)
    averageNeighborhoodSize = len(set(v1n).union(set(v2n)))
    intersectionSize = set(v1n).intersection( set(v2n))
    return len(intersectionSize) / averageNeighborhoodSize

#Denominator = size of v2's neighborhood
def scoreMatchedFilter_v2(G,vertex1,vertex2):
    v1n = G.neighbors(vertex1)
    v2n = G.neighbors(vertex2)
    intersectionSize = set(v1n).intersection( set(v2n))
    return len(intersectionSize) / len(v2n)

#############################
# Attributed Matched Filter #
#############################
def score_categorical_attributed_matched_filter_v1(G,vertex1,vertex2,edge_attributes, target_attribute):
    #G is the connection NetworkX graph
    #vertex1 and vertex2 are two vertices to score
    #edge_attributes are a dict of edge attributes [ao(v1, v2)] = [attribute list]
    #edge attributes are simply conveyed onto the vertices they connect to v1 (the centered vertex)
    v1n = G.neighbors(vertex1)
    v2n = G.neighbors(vertex2)
    intersection = set(v1n).intersection( set(v2n))
    matching_vertices = 0
    for vertex in intersection:
        if target_attribute in edge_attributes[ ao(vertex1, vertex) ]:
            matching_vertices += 1
    return matching_vertices / len(v2n)

def categorical_attributed_matched_filter_v1(G, vertex, edge_attributes, target_attribute):
    candidates = getNodes2Out(G, vertex)
    candidateScores = []
    for candidate in candidates:
        score = score_categorical_attributed_matched_filter_v1(G,vertex,candidate, edge_attributes, target_attribute)
        candidateScores.append( [candidate, score] )
    return candidateScores



###########################
# Weighted Matched Filter #
###########################
def score_weighted_matched_filter_v1(G,vertex1,vertex2,edge_weights):
    #G is the connection NetworkX graph
    #vertex1 and vertex2 are two vertices to score
    #edge_weights are a dict of edge weights [ao(v1, v2)] = edge_weight
    #edge weights are simply conveyed onto the vertices they connect to v1 (the centered vertex)
    v1n = G.neighbors(vertex1)
    v2n = G.neighbors(vertex2)
    intersection = set(v1n).intersection( set(v2n))
    matching_weight = 0
    for vertex in intersection:
        if ao(vertex1, vertex) in edge_weights: #otherwise assumed to be 0
            matching_weight += edge_weights[ao(vertex1, vertex)]
    return matching_weight / len(v2n) #Assumed that weights go from 0 to 1


def weighted_matched_filter_v1(G, vertex, edge_weights ):
    candidates = getNodes2Out(G, vertex)
    candidateScores = []
    for candidate in candidates:
        score = score_weighted_matched_filter_v1(G,vertex,candidate, edge_weights)
        candidateScores.append( [candidate, score] )
    return candidateScores

def score_weighted_matched_filter_v2(G,vertex1,vertex2,edge_weights):
    #Allows edge_weights to be a vector, which are just multiplied out
    #G is the connection NetworkX graph
    #vertex1 and vertex2 are two vertices to score
    #edge_weights are a dict of edge weights [ao(v1, v2)] = [weight list]
    #edge weights are simply conveyed onto the vertices they connect to v1 (the centered vertex)
    v1n = G.neighbors(vertex1)
    v2n = G.neighbors(vertex2)
    intersection = set(v1n).intersection( set(v2n))
    matching_weight = 0
    for vertex in intersection:
        if ao(vertex1, vertex) in edge_weights: #otherwise assumed to be 0
            ws = edge_weights[ao(vertex1, vertex)]
            product = 1
            for w in ws:
                product = product * w
            matching_weight += product
    return matching_weight / len(v2n)#Assumed that weights go from 0 to 1

def weighted_matched_filter_v2(G, vertex, edge_weights ):
    candidates = getNodes2Out(G, vertex)
    candidateScores = []
    for candidate in candidates:
        score = score_weighted_matched_filter_v2(G,vertex,candidate, edge_weights)
        candidateScores.append( [candidate, score] )
    return candidateScores


def getNodes2Out(G, vertex):
    return list(set(getNodes2Hop(G, vertex)) - set(G.neighbors(vertex)) - set([vertex]) )

def getNodes2Hop(G, vertex):
    neighbors = []
    for entry in G.neighbors(vertex):
        neighbors.append(entry)
        for node in G.neighbors(entry):
            neighbors.append(node)
    neighbors = list(set(neighbors))
    return neighbors

def getOneAndAHalfHop(G, vertex):
    nodelist = G.neighbors(vertex)
    nodelist.append(vertex)
    return G.subgraph(nodelist)

def edgeCentric_getOneAndAHalfHop(G, edgeOfInterest):
    fromSide = G.neighbors(edgeOfInterest[0])
    toSide = G.neighbors(edgeOfInterest[1])
    GPrime = G.subgraph(list(set(toSide+fromSide)))
    return GPrime
    
def makeGraphVizFile(G, outputFilename,
                     edgesOfInterest=[], nodesOfInterest=[]):
    #Make sure the PRIMARY edge of interest comes first
    #headerString = "graph MatchedFilter {\n rankdir=LR;"
    headerString = "graph MatchedFilter {\n "
    #footerString = "label = \"\n\nMatchedFilter Test Diagram\";\nfontsize=20;\n}"
    footerString = "\n}\n"
    rankString = ""
    if edgesOfInterest:
        rankString = "{ rank = same;"
        primaryNodes = edgesOfInterest[0] #The nodes in the primary edgeOfInterest
        for node in primaryNodes:
            rankString += " "+str(node)+";"
        rankString += " }\n"
            

    #Specify the nodes of interest with a unique shape [Box]
    nodesOfInterestString = ""
    if nodesOfInterest:#So long as there is at least one
        nodesOfInterestString = "node [shape=box ];"
        for node in nodesOfInterest:
            nodesOfInterestString += " "+str(node)+";"
        for node in G.nodes():
            nodesOfInterestString += "\nnode [shape=ellipse];"
            if not node in nodesOfInterest:
                nodesOfInterestString += " "+str(node)+";"
            
            
    OUT = open(outputFilename,'w')
    OUT.write(headerString+"\n")
    OUT.write(nodesOfInterestString+"\n")
    OUT.write(rankString+"\n")
    for edge in G.edges():
        thisEdgeString = "\t"+str(edge[0])+" -- "+str(edge[1])
        if edge in edgesOfInterest:

            if edgesOfInterest.index(edge) == 0: #Primary
                thisEdgeString += "[ color = red penwidth=7]"
            else:
                thisEdgeString += "[ color = red penwidth=3]"
        thisEdgeString += ";\n"
        OUT.write(thisEdgeString)
    OUT.write(footerString+"\n")
    
#################################
# Delta Scan Statistic -- Edges #
#################################
def scanStatisticOnEdges(G, vertexHistories):
    nowMeanByVertex = {}
    maxScanStat = -1
    highestDeltaNode = False
    for node in G.nodes():
        tempNodeList = G.neighbors(node)
        tempNodeList.append(node)
        inducedSubgraph = G.subgraph(tempNodeList)

        inducedSubgraphSize = inducedSubgraph.number_of_edges()
            
        thisNodeScanStat = (inducedSubgraphSize - \
                            vertexHistories[ node ]) #Only does Tau=1 for now
        nowMeanByVertex[ node ] = inducedSubgraphSize

        if thisNodeScanStat > maxScanStat:
            maxScanStat = thisNodeScanStat
            highestDeltaNode = node
    return (maxScanStat, highestDeltaNode, nowMeanByVertex)

#####################################
# Delta Scan Statistic -- Triangles #
#####################################
def scanStatisticOnTriangles(G, vertexHistories):
    nowMeanByVertex = {}
    maxScanStat = -1
    highestDeltaNode = False
    for node in G.nodes():
        tempNodeList = G.neighbors(node)
        tempNodeList.append(node)
        inducedSubgraph = G.subgraph(tempNodeList)
        inducedSubgraphSize = sum(nx.triangles(inducedSubgraph))/3
            
        thisNodeScanStat = (inducedSubgraphSize - \
                            vertexHistories[ node ]) #Only does Tau=1 for now
        nowMeanByVertex[ node ] = inducedSubgraphSize

        if thisNodeScanStat > maxScanStat:
            maxScanStat = thisNodeScanStat
            highestDeltaNode = node
    return (maxScanStat, highestDeltaNode, nowMeanByVertex)

#Arbitrary ordering, for indexing dicts
#def ao(v1, v2):
#    if v1 > v2:
#        return (v1, v2)
#    else:
#        return (v2, v1)

#####################################
# Scan Based on Attributed Vertices #
#####################################
def scan_vertex_attributes_v1(G, vertex_attributes, target_attribute):
    #G is the NetworkX connection graph
    #vertex_attributes is a dict ['vertex_name'] --> attribute
    #----- This assumes that each vertex can only be singly colored.
    #target_attribute is the attribute of interest
    max_scan = -1
    max_vertex = False
    max_proportional_scan = -1
    max_proportional_vertex = False
    for vertex in G.nodes():
        this_scan = 0
        neighborhood = G.neighbors(vertex)
        neighborhood.append(vertex)
        for v in neighborhood:
            if vertex_attributes[v] == target_attribute:
                this_scan += 1
        if this_scan > max_scan:
            max_scan = this_scan
            max_vertex = vertex
        this_proportional_scan = this_scan / len(neighborhood)
        if this_proportional_scan > max_proportional_scan:
            max_proportional_scan = this_proportional_scan
            max_proportional_vertex = vertex
    return [ max_scan, max_vertex, max_proportional_scan, max_proportional_vertex ]

##################################
# Scan Based on Attributed Edges #
##################################
def scan_edge_attributes_v1(G, edge_attributes, target_attribute):
    #G is the NetworkX connection graph
    #edge_attributes is a dict [ ('vertex_1_name','vertex_2_name') ] --> [attribute list]
    #----- This assumes that each edge can be multiply colored
    #target_attribute is the attribute of interest
    max_scan = -1
    max_vertex = False
    max_proportional_scan = -1
    max_proportional_vertex = False
    for vertex in G.nodes():
        this_scan = 0
        neighborhood = G.neighbors(vertex)
        neighborhood.append(vertex)
        induced_subgraph = G.subgraph( neighborhood )
        #For each pair of edges possibly present
        for edge in induced_subgraph.edges():
            #if target_attribute in edge_attributes[ao(edge[0],edge[1])]:
            if target_attribute == edge_attributes[ao(edge[0],edge[1])]: #simplistic integer case
                this_scan += 1
        if this_scan > max_scan:
            max_scan = this_scan
            max_vertex = vertex
        this_proportional_scan = this_scan / induced_subgraph.size()
        if this_proportional_scan > max_proportional_scan:
            max_proportional_scan = this_proportional_scan
            max_proportional_vertex = vertex
    return [ max_scan, max_vertex, max_proportional_scan, max_proportional_vertex ]


def get_content_from_vertex( G, edge_content, vertex):
    content = []
    for neighbor in G.neighbors(vertex):
        pairing = ao(neighbor, vertex)
        if pairing in edge_content:
            content.append( edge_content[pairing] )
    return content


###################################
# Importance Sampling Test: REDUX #
###################################


def average_vectors(vs):
    summed = [0]*len(vs[0])
    for v in vs:
        for i in range(len(v)):
            summed[i] += v[i]
    for i in range(len(summed)):
        summed[i] = summed[i] / float(len(v))
    return summed


def calculate_delta_topic_distribution_from_distribution(G, edge_topic_distributions, vertices_m, return_distributions = False, return_topics_of_interest=False):

    #Calculate average topic vector (centroid of all present edges in the set)
    m_topic_distributions = []
    for m1 in vertices_m:
        for m2 in vertices_m:
            vertex_pair = ao(m1,m2)
            if vertex_pair in edge_topic_distributions:
                m_topic_distributions.append( edge_topic_distributions[ vertex_pair ] )
    this_m_average_topic = average_vectors( m_topic_distributions)
                
    m_c_topic_distributions = []
    vertices_m_c = list(set(G.nodes())-set(vertices_m)) #M Complement
    for notm1 in vertices_m_c:
        for notm2 in vertices_m_c:
            vertex_pair = ao(notm1,notm2)
            if vertex_pair in edge_topic_distributions:
                m_c_topic_distributions.append( edge_topic_distributions[ vertex_pair ] )
    this_m_c_average_topic = average_vectors( m_c_topic_distributions)

    delta_topic_vector = [0] * len(this_m_average_topic)
    delta = 0
    for i in range(len(delta_topic_vector)):
        delta_topic_vector[i] = this_m_average_topic[i] - this_m_c_average_topic[i]

        delta += abs(delta_topic_vector[i])

    topics_of_interest = []
    if return_topics_of_interest:
        for i in range(len(this_m_average_topic)):
            if delta_topic_vector[i] > 0:
                topics_of_interest.append(i-1) # -1 accounts for us starting at -1 and going to 33 in indexing of probabilty vector

        
    if return_distributions:
        if return_topics_of_interest:
            return (delta, this_m_average_topic, this_m_c_average_topic, topics_of_interest)
        else:
            return (delta, this_m_average_topic, this_m_c_average_topic)
    elif return_topics_of_interest:
        return (delta, topics_of_interest)
    else:
        return delta


def does_partition_work(G, edge_topic_distributions, vertices_m, tau_rho, tau_topic, boolean_only_return=False):
        
    this_delta_rho = calculate_delta_rho(G, vertices_m)
    print "DeltaRho:",this_delta_rho
    if this_delta_rho <= tau_rho: #[m] is not more connected than the rest of the graph
        return( [ False, [], [], [], this_delta_rho, 0 ] )

    #If [m] is more connected than would be expected by the rest of the graph,
    #then proceed to see if the differences in topics distributions 
    
    this_delta_topic_returned = calculate_delta_topic_distribution_from_distribution(G, edge_topic_distributions, vertices_m, return_distributions = True, return_topics_of_interest=True)
    (this_delta_topic, m_average_topic_vector, m_c_average_topic_vector, topics_of_interest) = this_delta_topic_returned
    print "DeltaTopic:",this_delta_topic
    if boolean_only_return:
        if this_delta_topic > tau_topic:
            return True
        else:
            return False
        
    return( [ this_delta_topic > tau_topic, m_average_topic_vector, m_c_average_topic_vector, topics_of_interest, this_delta_rho, this_delta_topic])



#################################
# Simulation Similarity Metrics #
#################################
def simple_content_similarity( x1, x2):
    if x1 == x2:
        return 1
    else:
        return 0


cached_content_similarity = {}
cached_content_of_interest = [] #Must get blown away when we change mPrime
def simulation_content_similarity(G, edge_content, target_vertex, which_m_prime):

    #Short circuit to just count proportion of content that has edge type 1 [Target Type]
    """
    if cached_content_of_interest:
        content_of_interest = cached_content_of_interest
    else:
        #Get all content from the mPrime
        for v in which_m_prime:
            content_of_interest += get_content_from_vertex( G, edge_content, v)
            cached_content_of_interest = content_of_interest
            """

    #Get all the content for the vertex
    target_content = []
    target_content = get_content_from_vertex(G, edge_content, target_vertex)
    if target_content:
        content_score = sum(target_content) / len(target_content) #Assuming interest=1 and other = 0
    else:
        content_score = 0
    return content_score
        
    
cached_context_single_vertex_similarity = {} #Persistant
def simulation_context_single_vertex_similarity( G, v1, v2,
                                                 cached_context_similarity = cached_context_single_vertex_similarity):
    pairing = ao(v1,v2)

    #If we've seen them before, don't compute, just use the cache
    if pairing in cached_context_similarity:
        return cached_context_similarity[pairing]

    #If we haven't seen them before, compute and store in the cache
    #value = nx.shortest_path_length(G, source=v1, target=v2)
    #value = nx.shortest_path_length(G, source=v1, target=v2)
    value = 1/nx.shortest_path_length(G, source=v1, target=v2)
    cached_context_similarity[pairing] = value
    return value


def score_matched_filter_to_set( G, target_vertex, mPrime):
    target_vertex_neighbors = G.neighbors( target_vertex )
    union_neighborhood_size = len(set(target_vertex_neighbors).union(set(mPrime)))
    intersect_neighborhood_size= set(target_vertex_neighbors).intersection( set(mPrime))
    return len(intersect_neighborhood_size) / union_neighborhood_size
    

def simulation_context_similarity( G, vertex, mPrime):
    return score_matched_filter_to_set(G, vertex, mPrime)

###########################################################################
# Content Similarity from JS Divergence from omega(\mM'), TF/IDF weighted #
###########################################################################

cached_wch_lists = {} #indexed by ao(edges)
def get_wchs_from_induced_subgraph( vertex_list, edge_filepath_dict,
                                   data_directory_location="/export/projects/tto6/EnronSimulations/maildir/"):
    wchs = []
    for m1_index in range(len(vertex_list)-1):
        for m2_index in range(m1_index+1,len(vertex_list)):
            vertex_pair = ao(vertex_list[m1_index],vertex_list[m2_index])
            if vertex_pair in cached_wch_lists:
                wchs.append( cached_wch_lists[vertex_pair] )
            elif vertex_pair in edge_filepath_dict:
                for filename in edge_filepath_dict[vertex_pair]:
                    this_wch = filename_to_wch( data_directory_location+filename, return_probability=True)
                    wchs.append(this_wch)
                    cached_wch_lists[ vertex_pair] = this_wch
    return wchs

# We make WCHs of interest for the entire neighborhood of \mM'
# We then compute 1/js_divergence between each vertex's messages and each of the WCH of interest.
# this WCH, returning the average 1/js_divergence
#There are MANY knobs to be tuned here -- GAC
#v1
def wch_similarity_to_mPrime_neighborhood( G, edge_filepath_dict, target_vertex, which_m_prime,
                                           divergence=js_divergence,
                                           data_directory_location="/export/projects/tto6/EnronSimulations/maildir/" ):
    #caching the content of interest may be a useful speedup, if needed.
    #Probably will be inelegant though, using globals.
    wchs_of_interest = get_wchs_from_induced_subgraph( which_m_prime, edge_filepath_dict, data_directory_location = data_directory_location)

    wchs_of_target_vertex = get_wchs_from_induced_subgraph( G.neighbors(target_vertex)+[target_vertex], edge_filepath_dict, data_directory_location = data_directory_location)

    total_dissimilarities = 0
    if not wchs_of_interest or not wchs_of_target_vertex:
        return 0
    for wch1 in wchs_of_interest:
        for wch2 in wchs_of_target_vertex:
            these_vecs = dicts_to_vectors(wch1, wch2)
            js = js_divergence( these_vecs[0], these_vecs[1])
            total_dissimilarities += js
    if total_dissimilarities > 0:
        similarity = (len(wchs_of_interest)*len(wchs_of_target_vertex))/total_dissimilarities #Average distance
    else:
        similarity = 0

    return(similarity)



#Each wch given equal weight -- assuming they each sum to 1
def create_average_wch( wchs ):
    average_wch = {}
    total_weight = 0
    for wch in wchs:
        try:
            for key in wch.keys():
                total_weight += wch[key]
                if key in average_wch:
                    average_wch[key] += wch[key]
                else:
                    average_wch[key] = wch[key]
        except AttributeError:
            pass

    if total_weight > 0:
        for key in average_wch.keys():
            average_wch[key] = average_wch[key]/total_weight
    
    return average_wch

#v2
def wch_similarity_to_mPrime_neighborhood_min_Mavg_Vind( G, edge_filepath_dict, target_vertex, which_m_prime,
                                                         divergence=js_divergence,
                                                         data_directory_location="/export/projects/tto6/EnronSimulations/maildir/" ):
    #caching the content of interest may be a useful speedup, if needed.
    #Probably will be inelegant though, using globals.
    wchs_of_interest = get_wchs_from_induced_subgraph( which_m_prime, edge_filepath_dict, data_directory_location = data_directory_location)

    average_wch_of_interest = create_average_wch( wchs_of_interest)

    wchs_of_target_vertex = get_wchs_from_induced_subgraph( G.neighbors(target_vertex)+[target_vertex], edge_filepath_dict, data_directory_location = data_directory_location)

    total_dissimilarities = 0
    if not wchs_of_interest or not wchs_of_target_vertex:
        return 0
    #for wch1 in wchs_of_interest:
    min_dissimilarity = 9999
    if average_wch_of_interest:
        for wch2 in wchs_of_target_vertex:
            these_vecs = dicts_to_vectors(average_wch_of_interest, wch2)
            js = js_divergence( these_vecs[0], these_vecs[1])
            if js < min_dissimilarity:
                min_dissimilarity = js
    if min_dissimilarity < 9999:
        if min_dissimilarity > 0:
            return 1/min_dissimilarity
        else:
            print "We have a 0 dissimilarity to the average vector -- suspicious?"
            return 1
    return 0

#v3
def wch_similarity_to_mPrime_neighborhood_min_Mavg_Vavg( G, edge_filepath_dict, target_vertex, which_m_prime,
                                                         divergence=js_divergence,
                                                         data_directory_location="/export/projects/tto6/EnronSimulations/maildir/" ):
    #caching the content of interest may be a useful speedup, if needed.
    #Probably will be inelegant though, using globals.
    wchs_of_interest = get_wchs_from_induced_subgraph( which_m_prime, edge_filepath_dict, data_directory_location = data_directory_location)

    average_wch_of_interest = create_average_wch( wchs_of_interest)

    wchs_of_target_vertex = get_wchs_from_induced_subgraph( G.neighbors(target_vertex)+[target_vertex], edge_filepath_dict, data_directory_location = data_directory_location)

    average_wch_of_target_vertex = create_average_wch( wchs_of_target_vertex )
    
    total_dissimilarities = 0
    if not wchs_of_interest or not wchs_of_target_vertex:
        return 0
    #for wch1 in wchs_of_interest:
    min_dissimilarity = 9999
    if average_wch_of_interest and average_wch_of_target_vertex:
        these_vecs = dicts_to_vectors(average_wch_of_interest, average_wch_of_target_vertex)
        js = js_divergence( these_vecs[0], these_vecs[1])
        if js > 0:
            return 1/js
        else:
            return 1
    return 0



##################################
# Carey's Proof Equivalent Metrics
##################################

#Equivalent to Carey's proof -- simply count the number of neighbors in mPrime
def simulation_context_similarity_magnitude_only( G, vertex, mPrime):
    return len(set(G.neighbors(vertex)).intersection(set(mPrime)))

#Equivalent to Carey's proof -- simply count the number of red edges incident to v
def simulation_content_similarity_magnitude_only(G, edge_content, target_vertex, which_m_prime):

    #Get all the content for the vertex
    target_content = []
    target_content = get_content_from_vertex(G, edge_content, target_vertex)
    content_score = sum(target_content) #Assuming interest=1 and other = 0
    return content_score

##########################################
# Estimate p1,p2,s1,s2 from observed graph
##########################################

def choose2( num ):
    if num > 2:
        return num * (num-1) / 2
    return 0

def estimate_vector( induced_subgraph, edge_attributes, target_attribute=1):
    possible_edges = choose2(len(induced_subgraph.nodes()))
    green_edges = 0 #Edge_attributes have this as _0, paper has this as _2
    red_edges = 0#Edge_attributes have this as _1, paper has this as _1
    for edge in induced_subgraph.edges():
        if edge_attributes[ ao(edge[0], edge[1]) ] == 1:
            red_edges += 1
        else:
            green_edges += 1
    prob_red = red_edges / possible_edges
    prob_green = green_edges / possible_edges

    return [prob_red, prob_green]
    
    
def estimate_p_and_s_vectors( G, which_m, edge_attributes ):

    #Estimate p vector alone
    m_complement = list(set(G.nodes()) - set(which_m))
    p_vector = estimate_vector(G.subgraph(m_complement),
                               edge_attributes)

    s_vector = estimate_vector(G.subgraph(which_m),
                               edge_attributes)
    
    return [p_vector,s_vector]

#####################
# Vertex Nomination #        
#####################
def vertex_nomination( G, mPrime, edge_content,
                       fusion_index = MULTIPLICATIVE_FUSION,
                       content_similarity=simulation_content_similarity,
                       context_similarity=simulation_context_similarity,
                       return_ranked_list=False,
                       return_ranked_list_and_scores=False,
                       condition_on_neighbors=False,
                       edge_filepath_dict=False):
    
    
    nominated_vertex = False
    nominated_fusion_score = -1
    nominated_content_sim = -1
    nominated_context_sim = -1

    ranked_list = []

    if condition_on_neighbors:
        potential_vertices = []
        for vertex in mPrime:
            potential_vertices += G.neighbors(vertex)
        potential_vertices = set(potential_vertices) - set(mPrime)
    else:
        potential_vertices = set(G.nodes()) - set(mPrime) #For all non-nominated vertices
    
    for vertex in potential_vertices:
        this_context_sim = context_similarity( G, vertex, mPrime)
        if edge_filepath_dict:
            this_content_sim = content_similarity( G, edge_filepath_dict, vertex, mPrime)
        else:
            this_content_sim = content_similarity( G, edge_content, vertex, mPrime)
        
        if fusion_index == CONTEXT_ONLY: #Conditionals for fusion go here when we decide what they will be
            this_fusion_score = this_context_sim 
        elif fusion_index == EDGE_CONTENT_ONLY:
            this_fusion_score = this_content_sim
        elif fusion_index == VERTEX_CONTENT_ONLY:
            #this_fusion_score = this_content_sim
            print "Vertex Content Only metric not yet implemented... Failing."
            sys.exit()
        elif fusion_index == MULTIPLICATIVE_FUSION:
            this_fusion_score = this_context_sim * this_content_sim
        elif fusion_index == ADDITIVE_FUSION:
            this_fusion_score = this_context_sim + this_content_sim
        else:
            print "Not a recognized Fusion... Failing."
            sys.exit()

        #print "....",vertex,this_context_sim, this_content_sim, this_fusion_score
        ranked_list.append( [this_fusion_score, vertex] )
        if this_fusion_score > nominated_fusion_score:
            nominated_content_sim = this_content_sim
            nominated_context_sim = this_context_sim
            nominated_vertex = vertex
            nominated_fusion_score = this_fusion_score
    #print nominated_vertex, "N:",nominated_content_sim, "X",nominated_context_sim

    #attach the rest of the ranked list in a random order
    if condition_on_neighbors:
        import random as rnd
        remaining_vertices = list(set(G.nodes()) - set(potential_vertices) - set(mPrime))
        rnd.shuffle(remaining_vertices)
        for vertex in remaining_vertices:
            ranked_list.append([0, vertex])
    
    ranked_list.sort()
    ranked_list.reverse()

    print ranked_list[0:5]
    
    if return_ranked_list_and_scores:
        return ranked_list 
    elif return_ranked_list:
        return [v[-1] for v in ranked_list] #removes the leading scores, leaving only the vertex as ranked lits
    else:
        return nominated_vertex

def iterative_vertex_nomination( G, mPrime, edge_content,
                                 iterations,
                                 fusion_index = ADDITIVE_FUSION,
                                 content_similarity=simulation_content_similarity,
                                 context_similarity=simulation_context_similarity,
                                 return_ranked_list=False,
                                 return_ranked_list_and_scores=False,
                                 condition_on_neighbors=False,
                                 edge_filepath_dict= False):
    progressive_ranked_list = []
    this_result = []
    for iteration in range(iterations):
        this_result = vertex_nomination(G, mPrime, edge_content,
                                        fusion_index = fusion_index,
                                        content_similarity = content_similarity,
                                        context_similarity = context_similarity,
                                        return_ranked_list = return_ranked_list,
                                        return_ranked_list_and_scores = return_ranked_list_and_scores,
                                        condition_on_neighbors=condition_on_neighbors,
                                        edge_filepath_dict = edge_filepath_dict)
        mPrime.append(this_result[0][-1])
        print mPrime
        
        if return_ranked_list or return_ranked_list_and_scores:
            progressive_ranked_list.append(this_result[0])
        else: #Just the vertex is getting returned
            progressive_ranked_list.append(this_result)
        
    if return_ranked_list_and_scores or return_ranked_list:
        return progressive_ranked_list[0:-1] + this_result
    else:
        return progressive_ranked_list


def reconstitute_importance_sampled_archive(tauP, tauRho, m=10, mPrime=5, \
                                            archive_directory = \
                                            "/export/projects/tto6/EnronSimulations/VN_importance_sampling_graphs/", \
                                            return_key_dict = True,
                                            return_filepaths = False):
    try:
        filename = archive_directory + "VN_IS_m%s_mPrime%s_tauP%s_tauRho%s_overall.lst" \
                   % (m, mPrime, tauP, tauRho)
        data = eval(open(filename,'r').read())
    except: #Means we didn't get 1000 of them
        filename = archive_directory + "VN_IS_m%s_mPrime%s_tauP%s_tauRho%s_incomplete.lst" \
                   % (m, mPrime, tauP, tauRho)
        data = eval(open(filename,'r').read())

    key_dict = {}
    if return_key_dict:
        key_dict["delta_rho"] = 0
        key_dict["delta_topics"] = 1
        key_dict["topics_of_interest"] = 2
        key_dict["which_m"] = 3
        key_dict["this_edge_attributes"] = 4
        key_dict["binary_edge_attributes"] = 5
        key_dict["weekNum"] = 6
        key_dict["unacceptable_configurations"] = 7


    if return_filepaths:
        print "Extracting filepaths not yet implemented. Should be soon, though --GAC"
        edge_filepath_dict = create_edge_filepath_dict()
        
    to_return = [data]
        
    if return_key_dict:
        to_return.append(key_dict)
    if return_filepaths:
        to_return.append(edge_filepath_dict)

    return to_return

def reconstitute_importance_sampled_redux_archive(tauP, tauRho, m=10, mPrime=5, \
                                                  archive_directory = \
                                                  "/export/projects/tto6/EnronSimulations/VN_importance_sampling_graphs/", \
                                                  return_key_dict = True,
                                                  return_filepaths = False):
    try:
        filename = archive_directory + "VN_IS_Redux_m%s_mPrime%s_tauP%s_tauRho%s_overall.lst" \
                   % (m, mPrime, tauP, tauRho)
        data = eval(open(filename,'r').read())
    except: #Means we didn't get 1000 of them
        filename = archive_directory + "VN_IS_Redux_m%s_mPrime%s_tauP%s_tauRho%s_incomplete.lst" \
                   % (m, mPrime, tauP, tauRho)
        data = eval(open(filename,'r').read())

    key_dict = {}
    if return_key_dict:
        key_dict["delta_rho"] = 0
        key_dict["delta_topics"] = 1
        key_dict["topics_of_interest"] = 2
        key_dict["which_m"] = 3
        key_dict["m_avg_topic_vector"] = 4
        key_dict["m_c_avg_topic_vector"] = 5
        key_dict["weekNum"] = 6
        key_dict["unacceptable_configurations"] = 7


    if return_filepaths:
        print "Extracting filepaths not yet implemented. Should be soon, though --GAC"
        edge_filepath_dict = create_edge_filepath_dict()
        
    to_return = [data]
        
    if return_key_dict:
        to_return.append(key_dict)
    if return_filepaths:
        to_return.append(edge_filepath_dict)

    return to_return

#This will work for 'binary' or the generic 'edge_attributes, dictionary'
def create_graph_from_edge_attributes( edge_attributes ):
    G = nx.Graph()
    G.add_edges_from( edge_attributes.keys())
    return G

#If this is ran as a standalone, assume it is to test it.

if __name__ == "__main__":
    vertex_attributes = {}
    for i in range(10):
        vertex_attributes[i] = True
    for i in range(10,40):
        vertex_attributes[i] = False
    G = nx.Graph()
    G.add_edge(0,1)
    G.add_edge(0,2)
    G.add_edge(0,3)
    G.add_edge(1,2)
    G.add_edge(1,10)
    G.add_edge(2,10)
    G.add_edge(2,11)
    G.add_edge(2,12)
    G.add_edge(3,13)
    G.add_edge(10,20)
    G.add_edge(10,21)
    G.add_edge(12,21)
    G.add_edge(12,22)
    G.add_edge(13,23)
    G.add_edge(23,33)
    G.add_edge(21,33)
    G.add_edge(22,33)

    edge_attributes = {}
    for edge in G.edges()[0:5]:
        edge_attributes[ ao(edge[0], edge[1]) ] = 1
    for edge in G.edges()[5:]:
        edge_attributes[ ao(edge[0], edge[1]) ] = 0

    for which_m_prime in [ [0,1], [0], [1], [2], [3], [1,2], [1,2,3], [0,1,2,3], [10], [33] ]:
        print which_m_prime,"---->"
        vtx = vertex_nomination( G, which_m_prime, edge_attributes, fusion_index=EDGE_CONTENT_ONLY)
        print "N-->",vtx
        vtx = vertex_nomination( G, which_m_prime, edge_attributes, fusion_index=CONTEXT_ONLY)
        print "X-->",vtx
        vtx = vertex_nomination( G, which_m_prime, edge_attributes )
        print "F-->",vtx
        

    
if False:
    vertex_attributes = {}
    for i in range(10):
        vertex_attributes[i] = True
    for i in range(10,40):
        vertex_attributes[i] = False
    G = nx.Graph()
    G.add_edge(0,1)
    G.add_edge(0,2)
    G.add_edge(0,3)
    G.add_edge(1,2)
    G.add_edge(1,10)
    G.add_edge(2,10)
    G.add_edge(2,11)
    G.add_edge(2,12)
    G.add_edge(3,13)
    G.add_edge(10,20)
    G.add_edge(10,21)
    G.add_edge(12,21)
    G.add_edge(12,22)
    G.add_edge(13,23)
    G.add_edge(23,33)
    G.add_edge(21,33)
    G.add_edge(22,33)
    
    print "Testing Scan based on vertex attributes:", scan_vertex_attributes_v1( G, vertex_attributes, True)
    vertex_attributes[1] = False
    vertex_attributes[2] = False
    print "Testing Scan based on vertex attributes:", scan_vertex_attributes_v1( G, vertex_attributes, True)

    edge_attributes = {}
    for edge in G.edges()[0:5]:
        edge_attributes[ ao(edge[0], edge[1]) ] = [True,False]
    for edge in G.edges()[5:]:
        edge_attributes[ ao(edge[0], edge[1]) ] = [False]

    edge_weights = {}
    for edge in G.edges()[0:5]:
        edge_weights[ ao(edge[0], edge[1]) ] = .75
    for edge in G.edges()[5:]:
        edge_weights[ ao(edge[0], edge[1]) ] = .5
    print "Testing Scan based on edge attributes:", scan_edge_attributes_v1( G, edge_attributes, True)

    print "Categorical:", categorical_attributed_matched_filter_v1(G, 0, edge_attributes, True)
    print "Weighted:", weighted_matched_filter_v1(G, 0, edge_weights)

    edge_weights = {}
    for edge in G.edges()[0:5]:
        edge_weights[ ao(edge[0], edge[1]) ] = [.75,.25]
    for edge in G.edges()[5:]:
        edge_weights[ ao(edge[0], edge[1]) ] = [.5,.25]
    print "Weighted:", weighted_matched_filter_v2(G, 0, edge_weights)
        
    for edge in G.edges()[0:5]:
        edge_attributes[ ao(edge[0], edge[1]) ] = [False]
    for edge in G.edges()[5:]:
        edge_attributes[ ao(edge[0], edge[1]) ] = [True, False]
    print "Testing Scan based on edge attributes:", scan_edge_attributes_v1( G, edge_attributes, True)
    print "Categorical:", categorical_attributed_matched_filter_v1(G, 0, edge_attributes, True)

    
#Old test code
if False:
    print "Testing Matched Filter..."
    G = nx.Graph()
    G.add_node( 0)
    G.add_node( 10)
    print "Should be 0:", matchedFilter_v1(G, 0)
    G.add_edge( 0,1)
    G.add_edge( 0,2)
    G.add_edge( 10,1)
    G.add_edge( 10,2)
    print "Should be 1:", matchedFilter_v1(G, 0)
    G.add_edge( 10,3)
    G.add_edge( 0,4)
    print "Should be less than 1",matchedFilter_v1(G, 0)
    G.add_edge( 5, 2)
    print "Should be less than 1",matchedFilter_v1(G, 0)

    G = nx.Graph()
    G.add_edge(0,1)
    G.add_edge(0,2)
    G.add_edge(0,3)
    G.add_edge(1,2)
    G.add_edge(1,10)
    G.add_edge(2,10)
    G.add_edge(2,11)
    G.add_edge(2,12)
    G.add_edge(3,13)
    G.add_edge(10,20)
    G.add_edge(10,21)
    G.add_edge(12,21)
    G.add_edge(12,22)
    G.add_edge(13,23)
    G.add_edge(23,33)
    G.add_edge(21,33)
    G.add_edge(22,33)

    print "Testing 1.5 Hop, centered on 10"
    Gprime = getOneAndAHalfHop(G, 10)
    print Gprime.nodes()
    print Gprime.edges()
    
    print "Testing 1.5 Hop, centered on 21"
    Gprime = getOneAndAHalfHop(G, 21)
    print Gprime.nodes()
    print Gprime.edges()

    print "Testing 1.5 Hop centered on an edge"
    edgeOfInterest = (10,21)
    Gprime = edgeCentric_getOneAndAHalfHop(G, edgeOfInterest)
    print Gprime.nodes()
    print Gprime.edges()

    makeGraphVizFile(Gprime, "/Users/glen/Desktop/MatchedFilterTest1.dot",
                     edgesOfInterest=[edgeOfInterest])
    makeGraphVizFile(Gprime, "/Users/glen/Desktop/MatchedFilterTest2.dot",
                     edgesOfInterest=[edgeOfInterest,(1,10)],
                     nodesOfInterest=[21,33])

    vertexHistory = {} 
    for node in G.nodes():
        vertexHistory[ node ] = 0

    print "Edges:", scanStatisticOnEdges( G, vertexHistory )[0:2]
    print "Triangles:", scanStatisticOnTriangles( G, vertexHistory )[0:2]
    
