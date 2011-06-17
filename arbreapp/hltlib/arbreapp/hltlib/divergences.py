# Author: Glen Coppersmith
# Email: coppersmith@jhu.edu
# Johns Hopkins University Human Language Technology Center of Excellence
# Created: December 2010

from __future__ import division
from math import log

def kl_divergence(v1, v2):
    running_sum = 0
    for i in range(len(v1)):
        if v2[i] > 0 and v1[i] > 0:
            running_sum += v1[i] * log(v1[i] / v2[i])
    return running_sum

def dicts_to_vectors(d1, d2):
    keys = set(d1.keys()).union(set(d2.keys()))
    v1 = []
    v2 = []
    for key in keys:
        if key in d1:
            v1.append(d1[key])
        else:
            v1.append(0)
        if key in d2:
            v2.append(d2[key])
        else:
            v2.append(0)
    return((v1, v2))

def avg(x, y): return ((x+y)/2)

def js_divergence(v1, v2):
    M = map(avg, v1, v2)
    return 0.5 * kl_divergence(v1, M) + 0.5 * kl_divergence(v2, M)
    
if __name__ == "__main__":
    v1 = [0.2, 0.2, 0.6]
    v2 = [0.1, 0.2, 0.7]
    print kl_divergence(v1, v2), kl_divergence(v2, v1)
    print js_divergence(v1, v2)
    
    v2 = [0.2, 0.2, 0.6]
    v1 = [0.1, 0.2, 0.7]
    print kl_divergence(v1, v2), kl_divergence(v2, v1)
    print js_divergence(v1, v2)

