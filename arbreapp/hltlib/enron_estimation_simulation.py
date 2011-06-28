#!/usr/bin/env python

from __future__ import division

import sys
print sys.version

from loadenron import *
import datetime
import networkx as nx
import math
import random
from optparse import OptionParser

from constants import *
from util_hltcoe import *

from settings import execs_file

def reconstituteEnron(dataLocation=execs_file, Filter=True,
                      return_filenames=False):
    IN = open(dataLocation,'r')

    # Read in the file -- This needs to be retooled for a streaming mode -GAC
    header = []
    emails = []
    for line in IN:
        if not header:
            header = line.strip().split("\t")
        else:
            # Unpack and properly cast each line
            (filepath,
             messageID,
             date,
             fromID,
             toIDs,
             ldcTopic,
             ldcKnnTopic) = line.strip().split("\t")

            # This hackery is needed for versions prior to 2.5 -GAC
            thisDate = datetime.datetime(*time.strptime(date, "%a, %d %b %Y %H")[0:5])
            
            fromID = int(fromID)
            toIDs = toIDs.strip().split(" ")
            for i in range(len(toIDs)):
                toIDs[i] = int(toIDs[i])
                
            ldcTopic = int(ldcTopic)
            ldcKnnTopic = int(ldcKnnTopic)

            # Add the reconstituted object to our (chronologically ordered)
            # list of edge-events, for the moment obscuring all we won't use
            if return_filenames:
                emails.append([thisDate, fromID, toIDs, ldcTopic, ldcKnnTopic, filepath])
            else:
                emails.append([thisDate, fromID, toIDs, ldcTopic, ldcKnnTopic])

    if filter:
        # Filter our emails that would create self-loops
        # Filter out emails with incorrect datetime stamps
        currentIndex = 0
        toPop = []
        for email in emails:
            popMe = False
            
            # Self Loops
            tos = email[2]
            froms = email[1]
            tos.append(froms)
            if len(set(tos)) <= 1: popMe = True
            
            # DateTime in 1979
            if email[0] < datetime.datetime(year=1990,day=1,month=1): popMe = True
            
            # Only do processing for weeks after August 2000
            # This is semi-arbitrary, looking at the first reasonable elbow
            # in our collection --GAC
            if email[0] < datetime.datetime(year=2000,month=7,day=31): popMe = True
            
            # Only do processing for weeks prior to April 2002
            # This is semi-arbitrary, looking at the first reasonable elbow
            # in our collection --GAC
            if email[0] >= datetime.datetime(year=2002,month=2,day=1): popMe = True
            
            if popMe:
                toPop.insert(0,currentIndex)
            currentIndex += 1
        for index in toPop:
            emails.pop(index)

    return emails

def create_edge_filepath_dict():
    edge_filepath_dict = {}
    emails = reconstituteEnron(return_filenames = True)
    for email in emails:
        (thisDate, fromID, toIDs, ldcTopic, ldcKnnTopic, filepath) = email
        for toID in toIDs:
            vertex_pair = ao(fromID, toID)
            if vertex_pair in edge_filepath_dict:
                edge_filepath_dict[vertex_pair].append(filepath)
            else:
                edge_filepath_dict[vertex_pair] = [filepath]
    return edge_filepath_dict


###
### Cache
###

emails_by_week = False
def filter_emails_by_vertices_topic_and_week( which_m, topics_of_interest, weeks):
    global emails_by_week
    
    if not emails_by_week:
        print "Creating cache"
        emails = reconstituteEnron( filter=True, return_filenames=True)
        emails_by_week = separate_Enron_emails_by_week(emails)
    else:
        print "Using cache"
    emails_of_interest = []
        
    for week in weeks:
        week_of_emails = emails_by_week[week]
        for email in week_of_emails:
            this_topic = email[4]
            if this_topic in topics_of_interest:
                emails_of_interest.append(email)
    return emails_of_interest


def split_emails_by_vertices_filtered_by_week( which_m, topics_of_interest, weeks):
    global emails_by_week
    
    if not emails_by_week:
        print "Creating cache"
        emails = reconstituteEnron( filter=True, return_filenames=True)
        emails_by_week = separate_Enron_emails_by_week(emails)
    else:
        print "Using cache"
    emails_of_m = []
    emails_of_mc = []
        
    for week in weeks:
        week_of_emails = emails_by_week[week]
        for email in week_of_emails:
            sender = email[1]
            print email, sender
            receivers = list(set(email[2]) - set([sender]))
            both_in_m = False
            if sender in which_m:
                for rec in receivers:
                    if rec in which_m:
                        both_in_m = True
                        break
            if both_in_m:
                emails_of_m.append(email)
            else:
                emails_of_mc.append(email)

            
    return (emails_of_m, emails_of_mc)


def makeGraphFromEmails( emails ):
    G = nx.Graph()

    for vertex in range(0,184):
        G.add_node(vertex)
    
    for email in emails:
        tos = email[2]
        froms = email[1]
        for to in tos:
            if froms != to:
                G.add_edge(froms,to)

    return G


def makeMultiGraphFromEmails( emails ):
    G = nx.MultiGraph()

    for vertex in range(0,184):
        G.add_node(vertex)
    
    for email in emails:
        tos = email[2]
        froms = email[1]
        for to in tos:
            if froms != to:
                
                G.add_edge(froms,to)

    return G


def totalVerticesSeen( emailsByWeek ):
    vertices = set([])
    for week in emailsByWeek:
        G = makeGraphFromEmails( week )
        vertices = vertices | set(G.nodes())
    return len(vertices)


def factorial(n):
    """A procedural approach to factorial calculations is actually faster, in
    Python, than a recursive approach.

    This method calls `reduce` to build the factorial equation iteratively, like
    below:

       ((((x1) * x2) * ...) * xn)

    This implementation also does not have a built in ceiling due to overflowing
    the execution stack. Python is not tail-call optimized, therefore recursion
    is not cheap and easy to blow up.
    """
    if n == 0: return 1  
    return reduce(lambda x, y: x * y, range(1, n + 1))  
    

def estimateP_mean( emailsByWeek, numberOfVertices=184 ):
    sizeByWeek = []
    for week in emailsByWeek:
        G = makeGraphFromEmails( week )
        sizeByWeek.append(G.size())
    possibleConnections = factorial(numberOfVertices) / \
                          (2 * factorial(numberOfVertices - 2))
    totalP = 0
    for index in range(len(sizeByWeek)):
        sizeByWeek[index] = sizeByWeek[index] / possibleConnections
        totalP += sizeByWeek[index]
    averageP = sizeByWeek[index] / len(emailsByWeek)
    return averageP


def estimateP_median( emailsByWeek, numberOfVertices=184 ):
    sizeByWeek = []
    for week in emailsByWeek:
        G = makeGraphFromEmails( week )
        sizeByWeek.append(G.size())
    possibleConnections = factorial(numberOfVertices) / \
                          (2 * factorial(numberOfVertices - 2))
    totalP = 0
    for index in range(len(sizeByWeek)):
        sizeByWeek[index] = sizeByWeek[index] / possibleConnections
        totalP += sizeByWeek[index]
    sizeByWeek.sort()
    averageP = sizeByWeek[int(math.floor(len(sizeByWeek)/2))]
    return averageP
        

def seedEnronGraph( G, m, q, p, random, totalVertices=184):
    #Copy the graph so we can modify it without destroying the original
    G = G.copy()
    #Randomly select m vertices
    eggVertices = range(totalVertices)
    random.shuffle(eggVertices)
    eggVertices = eggVertices[0:m]
    #Seed edges with probability q - p [to increase from p to q]
    for i in range(len(eggVertices)):
        for j in range(i, len(eggVertices)):
            if not G.has_edge(i,j):
                if random.random() < q-p:
                    G.add_edge(i,j)
    return G


def get_active_vertices(G):
    vertices = []
    for edge in G.edges():
        vertices.append(edge[0])
        vertices.append(edge[1])
    return list(set(vertices))


def separate_Enron_emails_by_week(emails, verbose=False):
    #Separate emails by week
    emailsByWeek = []
    staringTimeByWeek = []
    thisWeek = []
    ourDelta = datetime.timedelta(weeks=1)
    ourStoppingPoint = ""
    for currentIndex,email in enumerate(emails):
        if not ourStoppingPoint:
            # Thankfully starts on a Monday
            ourStoppingPoint = email[0] + ourDelta
            
        if email[0] < ourStoppingPoint:
            thisWeek.append(email)
            currentIndex += 1
        else:
            # We've reached the end of our week, start a fresh one
            ourStoppingPoint = ourStoppingPoint + ourDelta
            print "Week:", len(emailsByWeek), "Date:", ourStoppingPoint
            emailsByWeek.append(thisWeek)
            thisWeek = []
            if verbose:
                print "Week prior to:", ourStoppingPoint, "in index", \
                      len(emailsByWeek)-1
    emailsByWeek.append(thisWeek) #To catch the last straggling week

    return emailsByWeek


def get_Enron_graph_by_week(weekNum, dataLoc=execs_file, verbose=False):
    emails = reconstituteEnron(dataLocation = dataLoc, filter=True)

    emailsByWeek = separate_Enron_emails_by_week(emails)
    
    totalVertices = totalVerticesSeen( emailsByWeek )
    pHat = estimateP_median(emailsByWeek, totalVertices)

    G = makeGraphFromEmails( emailsByWeek[weekNum] )
    return G


def get_Enron_topic_distribution_by_week_span(week_span, dataLoc=execs_file,
                                              verbose=False):
    
    emails = reconstituteEnron(dataLocation = dataLoc, filter=True)
    emails_by_week = separate_Enron_emails_by_week(emails)
    
    topic_by_edge = {} # indexed by ao(v1, v2)
    # internal values are [topicNum, topicNum, topicNum,...]
    for week_index in week_span:
        this_week_emails = emails_by_week[ week_index ]
        for email in this_week_emails:
            # print email
            (date,fro,to_vertices,hand_topic,knn_topic) = email
            for to in to_vertices:
                if not fro == to:
                    vertex_pair = ao(to,fro)
                    # print vertex_pair
                    if vertex_pair in topic_by_edge:
                        topic_by_edge[ vertex_pair ].append(knn_topic)
                    else:
                        topic_by_edge[ vertex_pair ] = [ knn_topic ]

    normalized_topic_by_edge = {}
    
    # Normalize to distribution over topics
    for edge in topic_by_edge.keys():
        email_topics = topic_by_edge[edge]
        these_summed_topics = [0]*(32+2) # Starts from -1 and goes to 32
        for topic in email_topics:
            these_summed_topics[topic + 1] += 1 # +1 accounts for starting at -1

        # Normalize            
        normalized_topic_by_edge[edge] = [x / len(email_topics)
                                          for x in these_summed_topics]
    return normalized_topic_by_edge


def get_Enron_graph_by_week_span(week_span):
    G = get_Enron_graph_by_week(week_span[0])
    if len(week_span) < 2:
        return G
    else:
        for week_index in range(1,len(week_span)):
            index_graph = get_Enron_graph_by_week(week_span[week_index])
            G.add_edges_from(index_graph.edges())
    return G

