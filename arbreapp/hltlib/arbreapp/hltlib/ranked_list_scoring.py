#!/usr/bin/python

# Copyright HLTCOE 2011
# Author: Glen Coppersmith - coppersmith@jhu.edu

from __future__ import division
from math import log

##########################
# Mean Average Precision #
##########################

def calc_average_precision( ranked_list, correct_answers):
    correct_ranks = []
    for answer in correct_answers:
        try:
            this_rank = ranked_list.index(answer)+1
            correct_ranks.append( this_rank )
        except ValueError:
            pass #these values didn't appear in the list, and are accounted for later (in about 10 lines)
    correct_ranks.sort()
    
    sum_precision = 0
    for index in range(len(correct_ranks)): #presorted by previous function
        this_rank = correct_ranks[index]
        #index+1 indicates the number of correct documents at this rank
        #this_rank indicates the rank
        precision_at_r = (index+1) / this_rank
        sum_precision += precision_at_r
    average_precision = sum_precision / len(correct_answers) #accounts for missing values too

    return average_precision

#########################################
# Normalized Discounted Cumulative Gain #
#########################################

def calc_ndcg( ranked_list, correct_answers, relevance_measures):
    """
    Normalized Discounted Cumulative Gain, as described at
    http://en.wikipedia.org/wiki/NDCG

    A ranked list evaluation measure where relevance judgements are
    taken into account. If no relevance measures are specified
    we assume that all correct answers have a relevance of 1.

    Higher relevance measures are considered more relevant.
    """
    dcg = 0
    def discount(rank):
        """
        This is the standard for NDCG
        """
        return log(rank, 2)
    ideal_ranking = []

    #With no supplied relevance measures, treat all as relevance=1
    if not relevance_measures:
        relevance_measures = {}
        for answer in correct_answers:
            relevance_measures[answer]=1

    #Walk down the ranked list and add for each correct answer
    for ran,vertex in enumerate(ranked_list):
        if vertex in relevance_measures:
            rank = ran+1
            ideal_ranking.append(relevance_measures[vertex])
            if rank > 1:
                dcg += relevance_measures[vertex] / discount(rank)
            else:
                dcg += relevance_measures[vertex]

    #Figure out what the ideal dcg is
    ideal_ranking.sort(reverse=True)
    idcg = 0
    for ran,relevance in enumerate(ideal_ranking):
        rank = ran+1
        if rank > 1:
            idcg += relevance / discount(rank)
        else:
            idcg += relevance
            
    return dcg / idcg
        

def score_ranked_list( ranked_list, correct_answers, relevance_measures=None, legacy=False):
    """
    Score the ranked_list according to our standard measures:
    MRR, S@1, S@2, MAP, and NDCG
    If no relevance judgements are specified, NDCG assumes that all correct
    answers are equally relevant.
    """
    correct_ranks = []
    for answer in correct_answers:
        try:
            this_rank = ranked_list.index(answer)
        except ValueError:
            this_rank = len(ranked_list)+1
        correct_ranks.append( this_rank )


    correct_ranks.sort()

    if len(correct_ranks) > 0:

        #S@2: P[ v_(2) in [m] ]
        if 1 in correct_ranks:
            correct_second = 1
        else:
            correct_second = 0
        
        #MRR
        min_rank = 1/(min(correct_ranks)+1)

        #S@1
        if min_rank == 1:
            correct_first = 1
        else:
            correct_first = 0
        
        """
        #Reciprocal Mean rank
        #mean_rank = 1/((sum(correct_ranks)+len(correct_ranks))/len(correct_ranks))#correct for 0-indexed list
        """
        
        average_precision = calc_average_precision(ranked_list, correct_answers)

        """
        #Precision/Recall
        precision_recall = []
        precision_recall.append( (0,0) )
        for i in range(1,len(correct_ranks)+1):
            precision_recall.append( (correct_ranks[i-1]/len(ranked_list),i/len(correct_ranks))) 
        precision_recall.append( (1,1) )

        #Hits/False Alarms
        h_fa = []
        h_fa.append( (0,0) )
        for i in range(1, len(correct_ranks) +1):
            h_fa.append( (i, correct_ranks[i-1]-i ) )
        """

        ndcg = calc_ndcg(ranked_list, correct_answers, relevance_measures)
        
    else:
        min_rank = -1
        average_precision = 0
        correct_second = 0

    if legacy:
        return [min_rank, average_precision, correct_second]#, precision_recall, h_fa]
    else:
        return [min_rank, correct_first, correct_second, average_precision, ndcg]


if __name__ == "__main__": #Call standalone for test
    a = [1,2,3,4,5,6,7,8,9]

    correct_answers=[1,2]
    relevance_measures = {1:10, 2:9}
    print score_ranked_list( a, correct_answers)
    print score_ranked_list( a, correct_answers, relevance_measures)
    relevance_measures = {1:1, 2:10}
    print score_ranked_list( a, correct_answers, relevance_measures)

    correct_answers=[1]
    relevance_measures = {1:9}
    print score_ranked_list( a, correct_answers)
    print score_ranked_list( a, correct_answers, relevance_measures)

    correct_answers=[1,3]
    relevance_measures = {1:1,3:2}
    print score_ranked_list( a, correct_answers)
    print score_ranked_list( a, correct_answers, relevance_measures)

    correct_answers=[9,7]
    relevance_measures = {9:1000,7:1}
    print score_ranked_list( a, correct_answers)
    print score_ranked_list( a, correct_answers, relevance_measures)

    

