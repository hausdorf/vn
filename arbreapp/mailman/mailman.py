"""Mailman is a python module for interacting with the Enron dataset as
provided by JHU HLTCOE's SCALE project. It aims to provide a framework for
navigating the dataset while also providing useful functions for inspecting
individual emails.
"""

import os
import fnmatch
import email
import codecs
import simplejson as json
import copy

from arbre.datafeeding import locate_by_pattern, convert_keys, GARBAGE_KEY

from models import MaildirEmail, LuceneEmail
from queries import insert_email, update_ldc_pair


###
### Email Directory Walking Functions
###

def maildir_process_dir(fun, root_dir='.', pattern='*.'):
    """Maps a function, `fun`, across all emails found in `root` and returns
    a list of the results.

    `fun` should be a function that accepts one argument, the path to an
    individual email.
    """
    for email_path in locate_by_pattern(pattern, root_dir):
        fun(email_path)

def maildir_to_mongo(db, maildir):
    """Shorthand for recursively calling `mailfile_to_mongo` on each mailfile in
    a directory.
    """
    def email_path_handler(email_path):
        mailfile_to_mongo(db, maildir, email_path)
    maildir_process_dir(email_path_handler, root_dir=maildir)

def maildir_header_count(maildir):
    """This function loops over `msg._headers` (eg. the email headers), and
    accumulates a count in keys_found.
    """
    keys_found = dict()
    
    def message_handler(email_path):
        msg = mailfile_to_message(email_path)
        for header in msg._headers:
            count_header_instances(header[0], keys_found)
            
    maildir_process_dir(message_handler, root_dir=maildir)
    return keys_found


###
### Email File Handling Functions
###

def mailfile_to_mongo(db, root_dir, email_path):
    """Runs all the steps required for loading an email fresh from the
    file system into it's representation in MongoDB.
    """
    msg = mailfile_to_message(email_path)
    folder = email_path.replace(root_dir+"/", '')
    
    email_doc = MaildirEmail.gen_from_message(msg)
    email_doc.folder = folder

    email_id = insert_email(db, email_doc)
    email_doc.id = email_id
    
    return email_doc

def mailfile_to_message(email_path):
    """Reads an email file from a particular path and returns a structure
    representing the result of calling email.message_from_file in a
    unicode safe way.
    """
    fp = codecs.open(email_path, encoding='utf-8', errors='replace')
    msg = email.message_from_file(fp) # built into python
    return msg


###
### Feed Handling
###

### Obcene Specific

def obcene_header_count(filename):
    """This function takes the keys from line_dict, eg the email headers, and
    accumulates a count in keys_found.
    """
    keys_found = dict()
    
    def line_handler(line_dict):
        """Loops over each key (eg. mail header)"""
        for header in line_dict.keys():
            count_header_instances(header, keys_found)
            
    process_json_feed(line_handler, filename)
    return keys_found
    
def obcene_to_mongo(db, filename):
    """Runs all the steps required for loading an email fresh from the
    file system into it's representation in MongoDB.
    """
    def line_handler(json_data):
        email_dict = obcene_convert_keys(json_data)
        email_doc = LuceneEmail(**email_dict)
        insert_email(db, email_doc)

    process_json_feed(line_handler, filename)


###
### K Nearest Neighbor Feed Handling
###

MESSAGEID_NAME = 'messageID'
LDCTOPIC_NAME = 'ldcTopic'
LDCKNNTOPIC_NAME = 'ldcKnnTopic'

def process_ldc_file(db, ldc_file, delimiter='\t', dups_file=None):
    """Maps a function, `fun`, across each json document in a lucene export
    file and returns a list of the results.

    `fun` should be a function that accepts one argument, the path to an
    individual email.

    I usually use `coe_enron_master.csv`
    """
    f = open(ldc_file)

    # Get headers from first line
    header_line = f.readline().strip()
    headers = header_line.split(delimiter)
    
    # Find column indexes for:
    message_id_col = -1    # messageID
    ldc_topic_col = -1     # ldcTopic
    ldc_knn_topic_col = -1 # ldcKnnTopic
    
    for idx,header_name in enumerate(headers):
        if header_name == MESSAGEID_NAME:
            message_id_col = idx
        elif header_name == LDCTOPIC_NAME:
            ldc_topic_col = idx
        elif header_name == LDCKNNTOPIC_NAME:
            ldc_knn_topic_col = idx

    # We'll call this to update each field
    def update_fun(db, message_id, ldc_topic, ldc_knn_topic):
        update_ldc_pair(db, message_id, ldc_topic, ldc_knn_topic)

    # If a dups file is provided, modify `update_fun` to use the dups_map
    if dups_file is not None:
        dups_map = dups_to_map(dups_file)
        def update_fun(db, message_id, ldc_topic, ldc_knn_topic):
            update_ldc_pair(db, message_id, ldc_topic, ldc_knn_topic)
            dup_str = dups_map.get(message_id, None)
            if dup_str is not None:
                # pull value out of dub_str box
                update_ldc_pair(db, dup_str[0], ldc_topic, ldc_knn_topic)

    # Find values in each line and call `update_fun`
    for csv_line in f: # iterates after head line
        csvalues = csv_line.split(delimiter)
        message_id = csvalues[message_id_col]
        ldc_topic = csvalues[ldc_topic_col]
        ldc_knn_topic = csvalues[ldc_knn_topic_col]
        update_fun(db, message_id, ldc_topic, ldc_knn_topic)
            

###
### Key Conversion
###

obcene_key_map = {
    'toName': 'x_to',
    'inReplyTo': 're',
    'toAddress': 'to',
    'quoted': 'body', # TODO not sure about this
    'fromName': 'x_from',
    'messageID': 'message_id',
    'fromAddress': 'ffrom',

    # These two fields appear to collect bad data...
    # Not sure why, so I'm marking them dirty
    'x-from': 'dirty_x_from',
    'x-to': 'dirty_x_to',

    # The garbage key is used for fields we know to be uninteresting
    # There are cases where the document design in lucene uses multiple
    # fields 
    '---': GARBAGE_KEY,
    'date': GARBAGE_KEY, # different format for same thing
}

def obcene_convert_keys(email_dict, deepcopy=False):
    """Short hand for converting keys in a dictionary from obcene to maildir.
    """
    return convert_keys(email_dict, obcene_key_map, deepcopy=deepcopy)


###
### Message ID Functions
###

def dups_to_map(dups_file, delimiter=' '):
    """Takes a filename and returns a map with multiple keys pointing at the
    same value. The value, however, is stored as a single item list. This lets
    map use a pointer reference to a shared container instead of duplicating
    values.
    """
    f = open(dups_file, 'r')
    dups_map = dict()
    for line in f:
        line = line.strip()
        message_ids = line.split(delimiter)
        csv_line = line.replace(' ', ', ')
        value = [csv_line] # single item list - save memory with a pointer ref
        for message_id in message_ids:
            dups_map[message_id] = value
    return dups_map


###
### Basic Inspection Functions
###

def count_header_instances(header, keys_found):
    """Simply a counter for each time a header is found. This function is
    intended for use in a loop where keys_found is created before calling.
    """
    if header not in keys_found:
        keys_found[header] = 0
    keys_found[header] = keys_found[header] + 1

def map_by_values(header_count_map):
    """Processes the header count produced by `count_header_instances` and
    creates a new structures of count => [header, header, header]. The count
    points to the list of headers that appeared `count` times.
    """
    freq_map = dict()
    for header,count in header_count_map.items():
        if count not in freq_map:
            freq_map[count] = list()
        freq_map[count].append(header)
    return freq_map

def sort_map_by_values(header_count_map):
    """Receives a frequency map, as generated by `map_by_values`, and returns a
    sorted list tuples that look like where the first element is occurrence and
    the second is the list of headers that occurred.
    """
    freq_map = map_by_values(header_count_map)
    import operator
    return sorted(freq_map.iteritems(), key=operator.itemgetter(0))


