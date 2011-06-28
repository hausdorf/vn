# Author: Glen Coppersmith
# Johns Hopkins University Human Language Technology Center of Excellence
# Created: December 2010

from __future__ import division

from arbreapp.hltlib.divergences import *

idf_vector_location = "/export/projects/tto6/EnronSimulations/wch_idf.dict"
#idf_vector_location = "/Users/gcoppersmith/Desktop/text_collectionSCRATCH/wch_idf.dict"
idf_vector = False

def assert_idf_vector_loaded():
    global idf_vector
    if not idf_vector:
        idf_vector = eval(open(idf_vector_location).read())
    return idf_vector

def filename_to_wch( filename, return_probability=False):
    return text_to_wch( open(filename).read(), return_probability=return_probability)

def text_to_wch( text, return_probability=False):
    count_dict = {}
    total_words = 0
    print text
    text = text.replace("\r"," ").replace("\n"," ").replace(")","").replace("(","").replace("[","").replace("]","").replace("."," ").replace(","," ").replace("_"," ").replace(":"," ").replace(";"," ").replace("="," ").lower().replace("\\"," ").replace("/"," ").replace(">"," ").replace("<"," ").replace("?"," ").replace("\t","")
    text = text.split(" ")
    for word in text:
        if word:
            try:
                count_dict[ word ] += 1
            except:
                count_dict[ word ] = 1
            total_words += 1
    if return_probability:
        for key in count_dict.keys():
            count_dict[key] = count_dict[key]/total_words
    return count_dict

def filename_to_idf_weighted_wch( filename, return_probability=False):
    idf_vector = assert_idf_vector_loaded()
    #try:
    if True:
        count_dict = {}
        total_words = 0
        text = open(filename,'r').read().replace("\r"," ").replace("\n"," ").replace(")","").replace("(","").replace("[","").replace("]","").replace("."," ").replace(","," ").replace("!"," ").replace("?"," ").replace("_"," ").replace(":"," ").replace(";"," ").replace("="," ").lower().replace("\\"," ").replace("/"," ").replace(">"," ").replace("<"," ").replace("?"," ").replace("\t","")
        text = text.split(" ")
        for word in text:
            if word and word in idf_vector:
                try:
                    count_dict[ word ] += 1
                except:
                    count_dict[ word ] = 1

        total_weight = 0
        for key in count_dict.keys():
            count_dict[key] = idf_vector[key] * count_dict[key]
            total_weight += count_dict[key]
        if return_probability:
            for key in count_dict.keys():
                count_dict[key] = count_dict[key]/total_weight
        return count_dict
    #except:
    #    return False

def average_wchs( wchs ): #WCHs come as dicts
    overall_wch = {}
    for wch in wchs:
        for key in wch.keys():
            if key in overall_wch:
                overall_wch[key] += wch[key]
            else:
                overall_wch[key] = wch[key]
    for key in overall_wch.keys():
        overall_wch[key] = overall_wch[key] / len(wchs)
    return overall_wch
        
    
def filelist_to_idf_weighted_wch( filenames ):
    idf_wchs = []
    for f in filenames:
        idf_wchs.append( filename_to_idf_weighted_wch(f, return_probability=True))
    return average_wchs( idf_wchs )

def filelist_to_unweighted_wch( filenames ):
    wchs = []
    for f in filenames:
        wchs.append( filename_to_wch(f, return_probability=True))
    return average_wchs( wchs )
    
if __name__ == "__main__":
    files = []
    for num in range(1,100):
        this_wch = filename_to_idf_weighted_wch( "/Users/gcoppersmith/Desktop/text_collectionSCRATCH/%s." % (num),return_probability=True)
        if this_wch:
            files.append(this_wch)
        print this_wch

    for this_file in files:
        total_weight = 0
        for key in this_file.keys():
            total_weight += this_file[key]
        print "Should be 1.0:", total_weight
    

            
            


