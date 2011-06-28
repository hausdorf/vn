# Copyright HLTCOE 2010
# Author: Glen Coppersmith - coppersmith@jhu.edu


from __future__ import division

###
### Mean Average Precision #
###

def area_under_curve( points ):
    area = 0
    for index in range(len(points)-1):
        p1 = points[index]
        p2 = points[index+1]
        delta_x = p2[0]-p1[0]
        delta_y = p2[1]-p1[1]
        area += delta_x * p1[1] #rectangle
        area += delta_x * delta_y / 2
    return area
        

def area_under_curve_normalizer( n, m, mPrime):
    """Probably doesn't work quite right yet
    """
    precision_recall =[(0,0)]
    for i in range(n-m):
        if i< m-mPrime:
            precision_recall.append((i/(m-mPrime),i))
        else:
            precision_recall.append((1,i))
    return area_under_curve( precision_recall )


def calc_average_precision( ranked_list, correct_answers):
    correct_ranks = []
    for answer in correct_answers:
        try:
            this_rank = ranked_list.index(answer)+1
            correct_ranks.append(this_rank)
        except ValueError:
            # these values didn't appear in the list, and are accounted for
            # later 
            pass 
    correct_ranks.sort()
    
    sum_precision = 0
    # already sorted by previous function    
    for index, this_rank in enumerate(correct_ranks):
        # index+1 indicates the number of correct documents at this rank
        # this_rank indicates the rank
        precision_at_r = (index+1) / this_rank
        sum_precision += precision_at_r
        
    # accounts for missing values too (as mentioned above)   
    average_precision = sum_precision / len(correct_answers) 

    return average_precision


def score_ranked_list( ranked_list, correct_answers):
    correct_ranks = []
    for answer in correct_answers:
        try:
            this_rank = ranked_list.index(answer)
        except ValueError:
            this_rank = len(ranked_list)+1
        correct_ranks.append(this_rank)

    correct_ranks.sort()

    if len(correct_ranks) > 0:

        # P[ v_(2) in [m] ]
        if 1 in correct_ranks:
            correct_second = 1
        else:
            correct_second = 0
        
        # Reciprocal Min Rank
        min_rank = 1/(min(correct_ranks)+1)

        # Reciprocal Mean Rank (corrects for 0-indexed list)
        #mean_rank = 1/((sum(correct_ranks)+len(correct_ranks))/len(correct_ranks))

        average_precision = calc_average_precision(ranked_list, correct_answers)
        
        # Precision/Recall
        precision_recall = []
        precision_recall.append((0, 0))
        for i in range(1, len(correct_ranks)+1):
            pr = (correct_ranks[i-1]/len(ranked_list), i/len(correct_ranks))
            precision_recall.append(pr) 
        precision_recall.append((1,1))

        auc = area_under_curve(precision_recall)
    
        # Hits/False Alarms
        h_fa = []
        h_fa.append((0,0))
        for i in range(1, len(correct_ranks) +1):
            h_fa.append((i, correct_ranks[i-1]-i ))

    else:
        min_rank = -1
        auc = 1
        mean_rank = -1
        average_precision = 0
    #return [min_rank, auc, mean_rank, correct_second]#, precision_recall, h_fa]
    return [min_rank, auc, average_precision, correct_second]#, precision_recall, h_fa]


if __name__ == "__main__":
    # Call standalone for test
    
    a = [1,2,3,4,5,6,7,8,9]

    correct_answers=[1,2]
    print score_ranked_list( a, correct_answers)

    correct_answers=[1]
    print score_ranked_list( a, correct_answers)

    correct_answers=[4,3]
    print score_ranked_list( a, correct_answers)

    correct_answers=[9,7]
    print score_ranked_list( a, correct_answers)


