#!/usr/bin/python
#Author: Glen Coppersmith - coppersmith@jhu.edu
#Copyright HLTCOE 2010

from __future__ import division

import sys

#sys.path += ['/Users/gcoppersmith/Dropbox/code/VertexNomination/']
#sys.path += ['/Users/gcoppersmith/Dropbox/code/vn_system/arbre/']
sys.path += ['/home/hltcoe/gcoppersmith/VertexNominationCode/']
print sys.path

import networkx as nx
from UtilHLTCOE import *
from constants import *
from RankedListScoring import *
from VertexNomination import *
import random
import os

from Enron_Estimation_Simulation import *
from constants import ao
from analytics_gac import get_enron_exec_attributed_weighted_graph, \
     compute_linear_fusion, get_enron_employees, get_ranked_list, \
     compute_range_of_linear_fusions, get_enron_exec_attributed_edgelist, \
     get_enron_graph_cache, write_enron_graph_cache, \
     compute_interesting_adjacent_content_from_wch

from arbre.database import init_dbconn
from arbre.timestamping import datestring_to_millis
from arbreapp.mailman.queries import find_emails, find_communications


#TODO: Params files
# Begin Params

tau_topic = 0.2
tau_rho = 0.2
mPrime = 5
m = 10
n=184
#output_loc = "/Users/gcoppersmith/results/optimizing_gamma/"
output_loc = "/home/hltcoe/gcoppersmith/vn_optimizing_gamma_wch/"
gammas = [x/100 for x in xrange(0,101)]
#gammas = [x/10 for x in xrange(0,11)]

# End Params

os.system("mkdir -p "+output_loc)

#Initialize a connection to the db
db = init_dbconn()
#G has one attribute value for each message on each edge

#Graph caching does not appear trivial, sadly. --GAC
"""
graph_cache_filename = 'optimizing_gamma_wch_cached_graph.txt'

try:
    G = get_enron_graph_cache(fp= graph_cache_filename )

except:
    #Original non-caching call
    #G = get_enron_exec_attributed_weighted_graph(db, \
    #    edge_attributes=['body'])

    edgelist = get_enron_exec_attributed_edgelist(db, edge_attributes=['body'])
    G = nx.Graph()
    G.add_edges_from(edgelist)
    write_enron_graph_cache(edgelist, fp= graph_cache_filename )

"""

G = get_enron_exec_attributed_weighted_graph(db, edge_attributes=['body'])


#Legacy expermients use the index of the employees instead of their email address,
#this mapping allows for direct comparison --GAC
employees = get_enron_employees()
employee_legacy_mapping = dict(zip(range(len(employees)),employees)) 



(reconstituted_results, key_dict) = reconstitute_importance_sampled_redux_archive( tau_topic, tau_rho, m=m, mPrime=mPrime,
                                                                                   archive_directory='/export/projects/tto6/EnronSimulations/VN_importance_sampling_redux_partitions/')

ranked_list_scores = []


nominated_scores_results_filename = output_loc + \
                                    "VN_IS_varyingGamma_n"+str(n)+\
                                    "_m"+str(m)+"_mPrime"+str(mPrime)+\
                                    "_tauP"+str(tau_topic)+\
                                    "_tauRho"+str(tau_rho)+\
                                    ".lst"


OUT = open( nominated_scores_results_filename,'w')
OUT.write("ReciprocalMinRank,AveragePrecision,ReciprocalMeanRank,CorrectSecond,DeltaRho,DeltaTopic,Gamma\n")
OUT.close()

if True:
#for gamma in gammas:
    
    random_seed = 230948029291
    random_seed = int(tau_topic*tau_rho*random_seed)
    random.seed(random_seed)


    for result in reconstituted_results:

        #TODO: collapse down Graph to single-attribute-per-edge, if we want to match the old experiments --GAC

        #Begin old funcitonality
        #this_edge_attributes = result[ key_dict[ "this_edge_attributes"]]
        #G = create_graph_from_edge_attributes( this_edge_attributes )
        #binary_edge_attributes = result[ key_dict[ "binary_edge_attributes"]]
        #active_vertices = get_active_vertices(G)
        #possible_edges = (len(active_vertices) * (len(active_vertices)-1))/2
        #p_hat = len(G.edges())/possible_edges
        #print "p^hat for this week:",p_hat
        #vertices = active_vertices
        #this_random = random.random()
        #End old functionality

        
        #Getting attributes of interest from the importance-sampling tables
        #print "Result:",result
        
        topics_of_interest = result[ key_dict[ "topics_of_interest" ]]
        delta_rho = result[ key_dict[ "delta_rho" ]]
        delta_topics = result[ key_dict[ "delta_topics" ]]
        int_indexed_which_m = result[ key_dict[ "which_m" ]]

        which_m = [ employee_legacy_mapping[x] for x in int_indexed_which_m ]
    
        which_m_prime = which_m[0:mPrime]            
        which_m_for_eval = list(set(which_m)-set(which_m_prime))


        #print "Topics:",topics_of_interest

        #if len(topics_of_interest) < 1:
        #    print "No topics of interest for this sample, skipping."
        #else:
        if True:
            
            kw = {'content_of_interest':topics_of_interest,
                  'gammas':gammas,
                  'content_analytic':compute_interesting_adjacent_content_from_wch}

                  #'gamma':gamma}
        

            print "Keywords in optimGamma:", kw
                    
            score_and_vertex_lists = compute_range_of_linear_fusions( G, which_m_prime,
                                                                     **kw)
            """
            score_and_ranked_list = iterative_vertex_nomination( G, which_m_prime,
                                                         binary_edge_attributes,
                                                         iterations=iterations,
                                                         fusion_index = fusion_index,
                                                         content_similarity=simulation_content_similarity_magnitude_only,
                                                         context_similarity=simulation_context_similarity_magnitude_only,
                                                         return_ranked_list_and_scores=True)
                                                         """
            OUT = open( nominated_scores_results_filename,'a')
            for index in range(len(gammas)):
                score_and_vertex_list = score_and_vertex_lists[index]
                gamma = gammas[index]
                ranked_list = get_ranked_list(score_and_vertex_list)
                this_replicate_score = score_ranked_list( ranked_list, which_m_for_eval)        
                ranked_list_scores.append(this_replicate_score + [delta_rho, delta_topics])
                
                score = ranked_list_scores[-1]
                if index in [0,25,50,99,100]:
                    print score
                #OUT.write("%s,%s,%s,%s,%s,%s\n" % score) #Still don't know why this doesn't work --GAC
                OUT.write(str(score[0])+","+str(score[1])+","+str(score[2])+","+\
                          str(score[3])+","+str(score[4])+","+str(score[5])+","+str(gamma)+"\n")
            OUT.close()

    
            
