# Copyright 2008
# Human Language Technology Center of Excellence
# Johns Hopkins University
# Author: Glen A. Coppersmith [coppersmith@jhu.edu]


from math import sqrt
import random

from arbreapp.hltlib.constants import *

try:
    import networkx as nx
except:
    pass
from numpy import *
import scipy.linalg
import time


###
### Dot Product / Cosine Similarity
###

def dotProduct(vector1, vector2, fun=lambda x: x):
    """Sums the dot product of two lists, representing vectors. Traversal is
    short-circuited by the length of the shortest list.

    Takes an optional function argument and applies it to the dotp roduct. Check
    `sqrtDotProduct` for example use.
    """
    total = 0.0
    for x,y in zip(vector1, vector2):
        total += fun(x*y)
    return total


def sqrtDotProduct(vector1, vector2):
    """Returns the sum of the dot product squareroots. Builds on `dotProduct` by
    passing `sqrt` as the optional function.
    """
    return dotProduct(vector1, vector2, sqrt)


def calcRho(vector1, vector2):
    print "Rho calculation needed between", vector1, vector2


def attributed_edge_dot_product(vector1, vector2, normalize=False):
    k_distribution = []
    fun = lambda x: k_distribution.append(x)
    summed_mass = dotProduct(vector1, vector2, fun=fun)
        
    if normalize:
        k_distribution = [k/summed_mass for k in k_distribution]
        
    return k_distribution


###
### Float Vector Creation
###

def floatRange(start, end, step):
    """I have no idea!
    """
    return [(float(i) * step) for i in range(int(start/step), int(end/step)+1)]


def drange(start, stop, step):
    """A generator that iterates between `start` and `stop` at `step` interval
    """
    r = start
    while r < stop:
        yield r
        r += step

        
def commandLineToList(argString):
    """Assumes argstring is of the form

        [0,1,0.34,332]
        
    If you've got numbers, you are going to have to cast them after the list is returned
    """
    return argString[1:-1].split(",")


###
### cPickle2Text
###

def cPickle2text(filename):
    """Assumes filename ends in .pickle, generates a flat file of the list
    with a .txt extension.
    """
    import cPickle
    
    fh = open(filename)
    data = cPickle.load(fh)
    fh.close()

    outputFilename = filename.replace(".pickle", ".txt")
    print filename, "-->", outputFilename
    
    fh = open(outputFilename, 'w')
    for entry in data:
        fh.write(str(entry)+"\n")
    fh.close()

    
def depickleDirectory(directory):
    """Converts all `*.pickle` files in a directory from pickle to text via
    calls to cPickle2text.
    """
    import os
    
    filelist = os.listdir(directory)
    for entry in filelist:
        if entry.find(".pickle") > 0: #Force at least one character before the .
            cPickle2text(directory+"/"+entry)

            
###
### Graph to flat text file
###

def graphToText(thisGraph, n, p, m, q, epsilon, r, workingDir, header=False):
    """Stores a graph as a text file with a directory name mapped to some of the
    graph's parameters.

    Example: workingDir/FlatGraph_nx_px_mx_qx_epsx/
    """
    import os

    dir_values = (workingDir, str(n), str(p), str(m), str(q), str(epsilon))
    fullDirectory = "%sFlatGraph_n%s_p%s_m%s_q%s_eps%s/" % dir_values
    os.system("mkdir -p "+fullDirectory)
    
    filename = "%sr%s.txt" % (fullDirectory, str(r))
    FILE = open(filename, "w")
    
    if header:
        FILE.write(str(n)+"\n")
        
    for edge in thisGraph.edges():
        FILE.write(str(edge[0])+" "+str(edge[1])+"\n")
        
    FILE.close()
    return filename


###
### Results to/from flat text file
###

def writeResultsToFile(filename, resultList):
    """Writes a result list to a flat text file, one result per line.
    """
    FILE = open(filename, 'w')
    for result in resultList:
        FILE.write(str(result)+"\n")
    FILE.close()

    
def readResultsFromFile(filename):
    """Reads a result list formated for one result per line and returns the
    resulting array.
    """
    FILE = open(filename, 'r')
    resultList = [float(line.strip()) for line in FILE]
    FILE.close()
    
    return resultList


###
### Random Dot Product Graphs
###

def generate_R_rdpg_homogeneous(n, vec, R, randomSeedValue, invariant):
    # Generate a uniform random [0,1)
    random.seed(randomSeedValue) 

    if invariant == -1:
        doAllInvariants = True
    
    monteCarlos = []
    for r in range(0, R):
        thisReplicate = generate_rdpg_homogeneous(n, vec)
        
        thisReplicateInvariantValue = evaluate_graph(thisReplicate, invariant)
        monteCarlos.append(thisReplicateInvariantValue)

        print "["+str(r)+"]==> Invariant["+str(invariant)+"]:",monteCarlos[-1]
        
    return monteCarlos


def generate_rdpg_homogeneous(n, vec):
    # Create a new networkx graph and add n nodes, named by their index
    G = nx.Graph()
    G.add_nodes_from(range(0,n))

    # The dotProduct is the same for all pairs of nodes, so compute it once
    homogeneousDotProduct = dotProduct(vec, vec)

    # Loop through the n choose 2 possible edges, and create them with probability
    # homogeneousDotProduct
    nodes = G.nodes()
    for outerCounter,firstNode in enumerate(nodes):
        for innerCounter in range(outerCounter+1, len(nodes)):
            secondNode = nodes[innerCounter]   
            if random.random() <= homogeneousDotProduct:
                G.add_edge(firstNode, secondNode)

    return G


def generate_R_rdpg_heterogeneous(n, kidneyVec, m, eggVec, R, randomSeedValue,
                                  invariant):
    # This will produce uniform random [0,1)
    random.seed(randomSeedValue)

    monteCarlos = []
    for r in range(0, R):
        thisReplicate = generate_rdpg_heterogeneous(n, kidneyVec, m, eggVec,
                                                    random)
        
        thisReplicateInvariantValue = evaluate_graph(thisReplicate, invariant)
        monteCarlos.append(thisReplicateInvariantValue)
        
        info_line = "[" + str(r) + "]==(" + str(m) + "," + str(eggVec) 
        info_line = info_line + ")==> Invariant[" + str(invariant) + "]:"
        print info_line, monteCarlos[-1]
        
    return monteCarlos


def generate_rdpg_heterogeneous(n, kidneyVec, m, eggVec, random):
    # Create a new networkx graph and add n nodes, named by their index
    G = nx.Graph()
    G.add_nodes_from(range(0,n))

    # The dotProduct is the same for all pairs of nodes, so compute it once
    kk_dotProduct = dotProduct(kidneyVec, kidneyVec)
    ee_dotProduct = dotProduct(eggVec, eggVec)
    ke_dotProduct = dotProduct(kidneyVec, eggVec)

    # Loop through the n choose 2 possible edges, and create them with
    # probability determined by their placement (eggs are at the end)
    nodes = G.nodes()
    for outerCounter,firstNode in enumerate(nodes):
        for innerCounter in range(outerCounter+1, len(nodes)):
            secondNode = nodes[innerCounter]

            if outerCounter < n-m:                  # Outer: in kidney
                if innerCounter < n-m:              #   Inner: in kidney
                    thisDotProduct = kk_dotProduct  #     ...
                else:                               #   Inner: in egg
                    thisDotProduct = ke_dotProduct  #     ...
            else:                                   # Outer: in egg
                if innerCounter < n-m:              #   Inner: in kidney
                    thisDotProduct = ke_dotProduct  #     ...
                else:                               #   Inner: in egg
                    thisDotProduct = ee_dotProduct  #     ...

            if random.random() <= thisDotProduct:
                G.add_edge(firstNode, secondNode)

    return G


def generate_R_rdpg(n, kidneyVec, m, eggVec, R, epsilon, randomSeedValue,
                    invariant):
    random.seed(randomSeedValue)

    monteCarlos = []
    for r in range(0, R):
        theseVectors = generate_uniformly_varying_vectors(n, kidneyVec, m,
                                                          eggVec, epsilon)
        thisReplicate = generate_rdpg(theseVectors)
        thisReplicateInvariantValue = evaluate_graph(thisReplicate, invariant)
        monteCarlos.append(thisReplicateInvariantValue)
        
        string_args = (str(r), str(m), str(eggVec), str(invariant))
        info_line = "[%s]==(%s,%s)==> Invariant[%s]:" % string_args
        print info_line, monteCarlos[-1]
        
    return monteCarlos


def generate_R_rdpg_noseed(n, kidneyVec, m, eggVec, R, epsilon, invariant,
                           random):

    # print "RANDOM:",random.random()
    # print "======================================"
    # print kidneyVec, eggVec
    # print "KK", dotProduct(kidneyVec, kidneyVec)
    # print "KE", dotProduct(kidneyVec, eggVec)
    # print "EE", dotProduct(eggVec, eggVec)
    
    monteCarlos = []
    for r in range(0, R):
        theseVectors = generate_uniformly_varying_vectors(n, kidneyVec, m,
                                                          eggVec, epsilon,
                                                          random)
        
        thisReplicate = generate_rdpg(theseVectors, random)
        thisReplicateInvariantValue = evaluate_graph( thisReplicate, invariant)
        monteCarlos.append( thisReplicateInvariantValue)
        
        string_args = (str(r), str(m), str(eggVec), str(invariant))
        info_line = "[%s]==(%s,%s)==> Invariant[%s]:" % string_args
        print info_line, monteCarlos[-1]

    return monteCarlos


def generate_R_rdpg_gaussian_noseed(n, kidneyVec, kidneyCov, m, eggVec, eggCov,
                                    R, epsilon, invariant, random, workingDir,
                                    graphTextOutputOn=False, nullState0=False):
    # Epsilon Here is the SD of the normal from which we draw the random
    # numbers, rather than a hard boundary
    monteCarlos = []
    
    for r in range(0, R):
        theseVectors = generate_gaussian_varying_vectors(n, kidneyVec,
                                                         kidneyCov, m, eggVec,
                                                         eggCov, epsilon,
                                                         random, workingDir,
                                                         nullState0=nullState0)
        thisReplicate = generate_rdpg(theseVectors, random)
        
        if graphTextOutputOn:
            graphToText(thisReplicate, n, dotProduct(kidneyVec,kidneyVec), m,
                        dotProduct(eggVec,eggVec), epsilon, r, workingDir)
            
        thisReplicateInvariantValue = evaluate_graph( thisReplicate, invariant)
        monteCarlos.append( thisReplicateInvariantValue)
        
        string_args = (str(r), str(m), str(eggVec), str(invariant))
        info_line = "[%s]==(%s,%s)==> Invariant[%s]:" % string_args
        print info_line, monteCarlos[-1]

    return monteCarlos


def generate_1_rdpg_from_vectors(vectors, invariant, random ):
    thisReplicate = generate_rdpg(vectors, random)
    thisReplicateInvariantValue = evaluate_graph(thisReplicate, invariant)
    return thisReplicateInvariantValue


def generate_rdpg(vectors, random ):
    # Each entry is the vector for a node, so make that many nodes in the graph
    n = len(vectors)
    
    # Create a new networkx graph and add n nodes, named by their index
    G = nx.Graph()
    G.add_nodes_from( range(0,n) )

    # Loop through the n choose 2 possible edges, and create them with
    # probability determined by their dot product
    size = 0
    nonSize = 0
    nodes = G.nodes()
    for outerCounter,node in enumerate(nodes):
        for innerCounter in range(outerCounter+1, len(nodes) ):
            thisDotProduct = dotProduct(vectors[outerCounter], vectors[innerCounter])

            if random.random() < thisDotProduct:
                G.add_edge(outerCounter, innerCounter)
                size += 1
            else:
                nonSize += 1
                
    # print "----------------------------"
    # print "Size/Nonsize:", size, nonSize, G.number_of_edges(), G.number_of_nodes()
    # for i in vectors:
    #   print i
    # print "----------------------------"
    
    return G


def generate_uniformly_varying_vectors(n, kidneyAverageVector, m, eggAverageVector, epsilon, random):

    print "----------------------------"
    print "KK", dotProduct(kidneyAverageVector, kidneyAverageVector)
    print "KE", dotProduct(kidneyAverageVector, eggAverageVector)
    print "EE", dotProduct(eggAverageVector, eggAverageVector)
    print "----------------------------"

    #eggVertices = range(0,n)
    #random.shuffle(eggVertices)
    #eggVertices = eggVertices[0:m]

    eggCounter = 0

    vectors = []
    for i in range(0, n):
        #if (i in eggVertices):
        if (i < m):
            baseVector = eggAverageVector
        else:
            baseVector = kidneyAverageVector
        newVector = range(0, len(baseVector) )
        for entry in range(0, len(baseVector)):
            delta = random.random()
            if (int(delta *10000) % 2) >0:
                #if (random.random() >0.5):
                newVector[ entry ] = baseVector[ entry ] + (delta * epsilon)
                if newVector[ entry ] >= 1:
                    newVector[ entry ] = 1.0
                    print "Vector hit 1, probably need to revisit that"
                    
            else:
                newVector[ entry ] = baseVector[ entry ] - (delta * epsilon)
                if newVector[ entry ] < 0:
                    newVector[ entry ] = 0
        vectors.append(newVector)

##     print "Tug of War:", tugOfWar
        
##     print vectors[0:10]
##     print "--==--"
##     print vectors[-10:-1]
##     print "--==--"

##     print "***********************"
##     for outer in range(0, len(vectors)):
##         for inner in range(outer, len(vectors)):
##             dotp = dotProduct(vectors[outer], vectors[inner])
##             if 0.09 > dotp or 0.11 < dotp < 0.34 or dotp > .36:
##                 print outer,inner,dotProduct(vectors[outer],vectors[inner])
##     print "***********************", epsilon

    
    return vectors

def generate_gaussian_varying_vectors(n, kidneyAverageVector, kidneyCovariance, m, eggAverageVector, eggCovariance, \
                                      epsilon, random, workingDir, nullState0=False):

##     print "----------------------------"
##     print "KK", dotProduct(kidneyAverageVector, kidneyAverageVector)
##     print "KE", dotProduct(kidneyAverageVector, eggAverageVector)
##     print "EE", dotProduct(eggAverageVector, eggAverageVector)
## #    print "Kidney Covariance:", kidneyCovariance
## #    print "Egg Covariance:", eggCovariance
##     print "----------------------------"

    eggCounter = 0
    
    #This assumes we have the full covariance matrix, so it constrains the calculations to the length of the vectors
    
    vectors = []
    outOfBounds = 0
    for i in range(0, n):
        #if (i in eggVertices):
        if (i < m):
            baseVector = eggAverageVector
            baseCov = eggCovariance
        else:
            baseVector = kidneyAverageVector
            baseCov = kidneyCovariance
        newVector = range(0, len(baseVector))
        for c in range(0, len(baseVector) ):
            newVector[c] = baseVector[c]
        for entry in range(0, len(baseVector)):
            delta = random.gauss(0,epsilon)
            if nullState0:
                for iterate in range(0, len(baseVector)):
                    newVector[iterate] += delta * baseCov[entry+1][iterate+1]
            else:
                for iterate in range(0, len(baseVector)):
                    newVector[iterate] += delta * baseCov[entry][iterate]
            
            if newVector[ entry ] >= 1:
                newVector[ entry ] = 1.0
                outOfBounds += 1
                print "Vector hit 1, probably need to revisit that"
                    
            if newVector[ entry ] < 0:
                newVector[ entry ] = 0
                outOfBounds += 1
                print "Vector hit 0, probably need to revisit that"
        vectorSum = 0
        for entry in range(0, len(baseVector)):
            vectorSum += newVector[entry]
        if vectorSum >= 1:
            print "VectorSum hit 1"
            outOfBounds += 1
        vectors.append(newVector)

    #Append the number of vectors outrunning the simplex to a file in the working directory
    oobFile = open(workingDir+"OutOfBounds_eps"+str(epsilon)+".txt", 'a')
    oobFile.write(str(outOfBounds)+"\n")
    oobFile.close()
    
        
    return vectors

#################
## Erdos Renyi ##
#################

def generate_R_er_noseed(n, p, m, q, R, invariant, random, workingDir="", graphTextOutputOn=False):

    RunMADExactCode = True
    import os
    
    monteCarlos = []
    for r in range(0,R):
        #Create a new networkx graph and add n nodes, named by their index
        G = nx.Graph()
        G.add_nodes_from( range(0,n) )

        #This accounts for the random numbers eaten by the epsilon generation
        for i in range(0,n):
            for j in range(0, 3):#HARDCODED size of vector
                random.random()
        
        #Loop through the n choose 2 possible edges, and create them with probability
        #determined by their placement (eggs are at the beginning)
        innerCounter = 0
        outerCounter = 0
        thisDotProduct = 0.0
        for outerCounter in range(0, len(G.nodes()) ):
            for innerCounter in range(outerCounter+1, len(G.nodes()) ):

                #If the inner counter is in the egg, then the outer counter is too
                if (innerCounter < m): 
                    thisConnectionProbability = q
                else:
                    thisConnectionProbability = p
                
                if random.random() <= thisConnectionProbability:
                    G.add_edge(outerCounter, innerCounter)

        thisReplicateInvariantValue = -1

        if graphTextOutputOn:
            flatGraphFilename = graphToText(G,n,p,m,q,0,r,workingDir,header=True)

        if graphTextOutputOn and RunMADExactCode: #Run the MAD exact code on it too
            MADExactFilename = workingDir+"MAD_Exact_n"+str(n)+"_p"+str(p)+\
                               "_m"+str(m)+"_q"+str(q)+"_eps0.txt"
            #MaxDensityCall = "/home/hltcoe/gcoppersmith/maxdensity_1_1/maxdensity "+flatGraphFilename+\
            MaxDensityCall = "/Users/glen/Desktop/maxdensity_1_1/maxdensity "+flatGraphFilename+\
                             "| grep density= >> "+MADExactFilename
            print MaxDensityCall
            time.sleep(0.25)
            os.system(MaxDensityCall)
            
        thisReplicateInvariantValue = evaluate_graph( G, invariant)
        
        monteCarlos.append( thisReplicateInvariantValue)
        print "["+str(r)+"]==("+str(m)+","+str(q)+")==> Invariant["+str(invariant)+"]:",monteCarlos[-1]
    return monteCarlos


def get_critical_from_null_graph(thisNull, alpha, verbose=False):

    R = len(thisNull)

    thisNull.sort()
    if verbose:
        print "Null select values:", thisNull[0], thisNull[1], thisNull[R/2], thisNull[-2], thisNull[-1]
    criticalPlace = int(alpha * R) + 1
    if verbose:
        print "Alpha, CritPlace:", alpha, criticalPlace 
    if (criticalPlace <= 1):
        print "Critical Place is too small to be correct, criticalPlace being set to the length of the vector"
        criticalPlace = 1
    criticalValue = thisNull[ -1 * criticalPlace ] #Counts criticalPlace places from the end of the array

    if verbose:
        print "Crit:", criticalValue

    #Test: How many are strictly greater than the crit value
    strictlyGreater = 0
    equalTo = 0
    for i in thisNull:
        if i > criticalValue:
            strictlyGreater += 1
        if i == criticalValue:
            equalTo += 1
    if verbose:
        print "Strictly Greater in Null:", strictlyGreater
        print "Strictly Equal To in Null:", equalTo

    alpha_d_hat = strictlyGreater / float(R)
    
    discreteCounter = 0.0
    for entry in thisNull:
        if entry == criticalValue:
            discreteCounter += 1.0

    if verbose:
        print "DiscCounter:", discreteCounter
        print "Alpha D Hat:", alpha_d_hat

    randomizedRejectionLevel = (alpha - alpha_d_hat) / ((1.0 / float(R)) * equalTo)

    if verbose:
        print "RandomizedRejectLevel:", randomizedRejectionLevel

    return [criticalValue, randomizedRejectionLevel]

def get_reversed_critical_from_null_graph(thisNull, alpha, verbose=False):

    R = len(thisNull)

    thisNull.sort()
    thisNull.reverse()
    if verbose:
        print "Null select values:", thisNull[0], thisNull[1], thisNull[R/2], thisNull[-2], thisNull[-1]
    criticalPlace = int(alpha * R) + 1
    if verbose:
        print "Alpha, CritPlace:", alpha, criticalPlace 
    if (criticalPlace <= 1):
        print "Critical Place is too small to be correct, criticalPlace being set to the length of the vector"
        criticalPlace = 1
    criticalValue = thisNull[ -1 * criticalPlace ] #Counts criticalPlace places from the end of the array

    if verbose:
        print "Crit:", criticalValue

    #Test: How many are strictly greater than the crit value
    strictlyGreater = 0
    equalTo = 0
    for i in thisNull:
        if i > criticalValue:
            strictlyGreater += 1
        if i == criticalValue:
            equalTo += 1
    if verbose:
        print "Strictly Greater in Null:", strictlyGreater
        print "Strictly Equal To in Null:", equalTo

    alpha_d_hat = strictlyGreater / float(R)
    
    discreteCounter = 0.0
    for entry in thisNull:
        if entry == criticalValue:
            discreteCounter += 1.0

    if verbose:
        print "DiscCounter:", discreteCounter
        print "Alpha D Hat:", alpha_d_hat

    randomizedRejectionLevel = (alpha - alpha_d_hat) / ((1.0 / float(R)) * equalTo)

    if verbose:
        print "RandomizedRejectLevel:", randomizedRejectionLevel

    return [criticalValue, randomizedRejectionLevel]

################################
# Calculating Rho and DeltaRho #
################################

#The portion of possible edges present in the graph
def calculate_rho (G, vertices):
    observed_edges = G.subgraph(vertices).size()
        
    possible_edges = (len(vertices)*(len(vertices)-1))/2
    print "OE", observed_edges, len(G.subgraph(vertices).edges()), possible_edges #, G.subgraph(vertices).nodes()


    #return observed_edges/possible_edges #Rho
    return float(observed_edges)/possible_edges #Rho

def calculate_delta_rho(G, vertices_m):
    rho_m = calculate_rho(G,vertices_m)
    
    vertices_m_c = list(set(G.nodes())-set(vertices_m)) #M Complement
    rho_m_c = calculate_rho(G, vertices_m_c)

    print "Rho_m:",rho_m, "Rho_m_c", rho_m_c
    
    return( rho_m - rho_m_c )

###############################################################
# Calculating topic distribution and delta topic distribution #
###############################################################

def calculate_topic_distribution (raw_G, edge_topic_labels, vertex_subset=False, topic_label_set = False):
    if vertex_subset:
        G = raw_G.subgraph(vertex_subset)
    else:
        G = raw_G
        
    if not topic_label_set: #For speedups, predefine for an experiment and pass each time this is called
        topic_label_set = list(set(edge_topic_labels.values()))

    topic_distribution = {}        
    for label in topic_label_set:
        topic_distribution[label]=0
        
    #Get all the edges from the (sub)graph
    for edge in G.edges():
        topic_distribution[ edge_topic_labels[ ao(edge[0],edge[1]) ] ] += 1

    #Normalize
    if len(G.edges())>0:
        for key in topic_distribution.keys():
            topic_distribution[ key ] = float(topic_distribution[key]) / len(G.edges())
        
    return topic_distribution
        
def calculate_delta_topic_distribution(G, edge_topic_labels, vertices_m, topic_label_set = False, return_distributions = False, return_topics_of_interest=False):

    if not topic_label_set: #For speedups, predefine for an experiment and pass each time this is called
        topic_label_set = list(set(edge_topic_labels.values()))

    topic_distribution_m=calculate_topic_distribution(G, edge_topic_labels, vertices_m, topic_label_set)
    vertices_m_c = list(set(G.nodes())-set(vertices_m)) #M Complement
    topic_distribution_m_c=calculate_topic_distribution(G, edge_topic_labels, vertices_m_c, topic_label_set)

    delta = 0
    for key in topic_distribution_m.keys():#Should be the same for TD_c
        delta += abs(topic_distribution_m[key] - topic_distribution_m_c[key])
    if return_distributions:
        return (delta, topic_distribution_m, topic_distribution_m_c)
    elif return_topics_of_interest:
        topics_of_interest = []
        for key in topic_distribution_m.keys():
            if topic_distribution_m[key] > topic_distribution_m_c[key]: #We may want a threshold here instead of strictly gt. --GAC
                topics_of_interest.append(key)
        return (delta, topics_of_interest)
    else:
        return delta



#Returns (Boolean, [topics more prevalent between m])
def is_sample_important(G, edge_topic_labels, vertices_m, tau_rho, tau_topic, topic_label_set=False, return_distributions=False, return_topics_of_interest=False):
    if return_distributions:
        print "Unfinished code, probably breaking!!! -- UtilHLTCOE.is_sample_important(.)"
        sys.exit()

    this_delta_rho = calculate_delta_rho(G, vertices_m)
    #print "Edges:",G.edges()
    print "DeltaRho:",this_delta_rho
    if this_delta_rho < tau_rho: #[m] is not more connected than the rest of the graph
        if return_topics_of_interest:
            return( [ False, [], this_delta_rho, 0 ] )
        else:
            return False
    #If [m] is more connected than would be expected by the rest of the graph,
    #then proceed to see if the differences in topics needed are present
    
    #this_delta_topic_returned = calculate_delta_topic_distribution(G, edge_topic_labels, vertices_m, topic_label_set, return_distributions = return_distributions, return_topics_of_interest=return_topics_of_interest)
    this_delta_topic_returned = calculate_delta_topic_distribution(G, edge_topic_labels, vertices_m, topic_label_set, return_distributions = return_distributions, return_topics_of_interest=True)
    if return_topics_of_interest:
        (this_delta_topic, topics_of_interest) = this_delta_topic_returned
        print "DeltaTopic:",this_delta_topic
        #        if this_delta_topic > tau_topic:
        #            return( [ True, topics_of_interest, this_delta_rho, this_delta_topic])
        return( [ this_delta_topic > tau_topic, topics_of_interest, this_delta_rho, this_delta_topic])
    
    else:
        if this_delta_topic > tau_topic:
            return True
        
    
####################
####################
## EVALUATE GRAPH ##
####################
####################

                
def evaluate_graph( thisReplicate, invariant, return_argmax=False):

    doAllInvariants = False
    if invariant == -1:
        doAllInvariants = True
        print "Doing all invariants for some reason..."
        system.exit(1)
    

    ########
    # SIZE #
    ########
    if (invariant == 1 or doAllInvariants):
        thisReplicateInvariantValue = thisReplicate.number_of_edges()

    ##############
    # MAX DEGREE #
    ##############
    if (invariant == 2 or doAllInvariants):
        maxDegree = -1
        replicateDegree = thisReplicate.degree()
        for entry in replicateDegree:
            if maxDegree < entry:
                maxDegree = entry
        thisReplicateInvariantValue = maxDegree

    ##################
    # EIGENVALUE MAD #
    ##################
    if (invariant == 4 or doAllInvariants):
        thisEigenvalues, thisEigenvectors = linalg.eig(nx.adj_matrix(thisReplicate) )
        thisEigenvalues.sort()
        if len(thisEigenvalues) > 0:
            thisReplicateInvariantValue = float(thisEigenvalues[-1])
        else:
            thisReplicateInvariantValue = 0 #Not sure if this is right... --GAC
    
    ##################
    # SCAN STATISTIC #
    ##################
    if (invariant == 5 or doAllInvariants):
        maxScanStat = -1
        argmax = False
        for node in thisReplicate.nodes():
            tempNodeList = thisReplicate.neighbors(node)
            tempNodeList.append(node)
            inducedSubgraph = thisReplicate.subgraph(tempNodeList)
##             print "Node:", node, thisReplicate.neighbors(node), \
##                   thisReplicate.subgraph(thisReplicate.neighbors(node)).number_of_edges(), \
##                   thisReplicate.subgraph(thisReplicate.neighbors(node)).number_of_nodes(),\
##                   sum(nx.triangles(thisReplicate.subgraph(thisReplicate.neighbors(node)))), \
##                   sum(nx.triangles(thisReplicate))
##             print "TSub:", node, inducedSubgraph.nodes(), \
##                   inducedSubgraph.number_of_edges(), \
##                   inducedSubgraph.number_of_nodes(),\
##                   sum(nx.triangles(inducedSubgraph))
            
##             thisNodeScanStat = (thisReplicate.subgraph( thisReplicate.neighbors(node) )).number_of_edges()
##             print "OldScanStat:", thisNodeScanStat
            thisNodeScanStat = inducedSubgraph.number_of_edges()
            #print "NewScanStat:", thisNodeScanStat
            if thisNodeScanStat > maxScanStat:
                argmax = node
                maxScanStat = thisNodeScanStat
        if return_argmax:
            thisReplicateInvariantValue = [maxScanStat, argmax] #Hacky, I know.
        else:
            thisReplicateInvariantValue = maxScanStat
        
        
    #################
    # NUM TRIANGLES #
    #################
    if (invariant == 6 or doAllInvariants):
        triangleList = nx.triangles(thisReplicate) #This returns a list with the number of triangles each node participates in
        sumOfTriangles = 0
        for entry in triangleList:
            sumOfTriangles += entry
        thisReplicateInvariantValue = sumOfTriangles / 3 #Correct for each triangle being counted 3 times        


    ##########################
    # Clustering Coefficient #
    ##########################
    if (invariant==8 or doAllInvariants):
        try:
            thisReplicateInvariantValue = nx.average_clustering( thisReplicate )
        except ZeroDivisionError:
            thisReplicateInvariantValue=-999

    #######################
    # Average Path Length #
    #######################
    if (invariant == 9 or doAllInvariants):
        thisReplicateInvariantValue = nx.average_shortest_path_length( thisReplicate )
        
        
    ##############
    # GREEDY MAD #
    ##############
    # We put this last because it actually deconstructs the Graph
    if (invariant == 3 or doAllInvariants):
        maxAverageDensity = -1
        nodeList = thisReplicate.nodes()
        while nodeList: #While there's something left
            degreeList = thisReplicate.degree(nodeList)
            smallestDegree = len(nodeList)+3
            smallestID = -1
            #print "================"
            #print "degreeList", degreeList
            #print "nodeList", nodeList
            for nodeID in range(0, len(degreeList)): #Search for the smallest Node
                if thisReplicate.degree( nodeList[nodeID] ) < smallestDegree:
                    #print nodeID, nodeList[nodeID], thisReplicate.degree(nodeID), thisReplicate.degree(nodeList[nodeID])
                    smallestID = nodeList[nodeID]
                    smallestDegree = thisReplicate.degree( nodeList[nodeID] )

            sumDegree = 0.0
            for degree in degreeList:
                sumDegree += degree
            if sumDegree > 0:
                thisAverageDensity = sumDegree / float(len(nodeList))
            else:
                thisAverageDensity = 0

            #print "AntiDivide:", sumDegree, "/", len(nodeList), "=", thisAverageDegree

            if thisAverageDensity > maxAverageDensity:
                maxAverageDensity = thisAverageDensity
            #print len(nodeList), len(degreeList), thisAverageDegree, maxAverageDegree, " Removing", smallestID, smallestDegree

            thisReplicate.remove_node(smallestID)
            nodeList.remove(smallestID)
            
        thisReplicateInvariantValue = maxAverageDensity
        


        
    return thisReplicateInvariantValue
    

