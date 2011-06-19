#!/usr/bin/env python
#Author: Glen Coppersmith - coppersmith@jhu.edu
#Copyright HLTCOE 2011

from __future__ import division

import sys

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
     compute_range_of_linear_fusions

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
output_loc = "/home/hltcoe/gcoppersmith/vn_optimizing_gamma/"
gammas = [x/100 for x in xrange(0,101)]
#gammas = [x/10 for x in xrange(0,11)]

# End Params

os.system("mkdir -p "+output_loc)

#Initialize a connection to the db
db = init_dbconn()
#G has one attribute value for each message on each edge
G = get_enron_exec_attributed_weighted_graph(db)

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
OUT.write("ReciprocalMinRank,AveragePrecision,NDCG,CorrectSecond,DeltaRho,DeltaTopic,Gamma\n")
OUT.close()

    
random_seed = 230948029291
random.seed(random_seed)


for result in reconstituted_results:


    topics_of_interest = result[ key_dict[ "topics_of_interest" ]]
    delta_rho = result[ key_dict[ "delta_rho" ]]
    delta_topics = result[ key_dict[ "delta_topics" ]]
    int_indexed_which_m = result[ key_dict[ "which_m" ]]

    #These are our interesting vertices
    which_m = [ employee_legacy_mapping[x] for x in int_indexed_which_m ]

    #These are the interesting vertices we know about
    which_m_prime = which_m[0:mPrime]

    #And the interesting vertices we have hidden and wish to recover
    which_m_for_eval = list(set(which_m)-set(which_m_prime))



    if len(topics_of_interest) < 1:
        print "No topics of interest for this sample, skipping."
    else:

        kw = {'content_of_interest':topics_of_interest,
              'gammas':gammas}

        #Score the vertices
        score_and_vertex_lists = compute_range_of_linear_fusions( G, which_m_prime,
                                                                 **kw)

        #Score the ranked lists according to our standard measures
        OUT = open( nominated_scores_results_filename,'a')
        for index in range(len(gammas)):
            score_and_vertex_list = score_and_vertex_lists[index]
            gamma = gammas[index]
            ranked_list = get_ranked_list(score_and_vertex_list)
            this_replicate_score = score_ranked_list( ranked_list, which_m_for_eval)        
            ranked_list_scores.append(this_replicate_score + [delta_rho, delta_topics])

            score = ranked_list_scores[-1]
            OUT.write("%s,%s,%s,%s,%s,%s\n" % list(score))
            """
            #If above fails, try this instead --GAC
            OUT.write(str(score[0])+","+str(score[1])+","+str(score[2])+","+\
                      str(score[3])+","+str(score[4])+","+str(score[5])+","+str(gamma)+"\n")
                      """
        OUT.close()



