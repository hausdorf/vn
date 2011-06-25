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

from models import MaildirEmail, LuceneEmail
from queries import insert_email, update_ldc_pair


###
### Email Directory Walking Functions
###

def locate_by_pattern(pattern, root_dir):
    """This is a generator for recursively detecting files with names that
    match the given pattern in a directory.

    The root directory defaults to the current directory.
    """
    for path, dirs, files in os.walk(os.path.abspath(root_dir)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

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

def obcene_process_feed(fun, filename):
    """Loops across each line in `filename` and converts the data from JSON to
    a Python dictionary.

    It then calls `fun` which is a function provided by the caller, designed for
    a Python dictionary, not JSON.

    No return value is generated to avoid overhead, but `fun` can be a closure
    for aggregating values.
    """
    fd = open(filename, 'r')
    for line in fd:
        data = json.loads(line)
        fun(data)

def obcene_header_count(filename):
    """This function takes the keys from line_dict, eg the email headers, and
    accumulates a count in keys_found.
    """
    keys_found = dict()
    
    def line_handler(line_dict):
        """Loops over each key (eg. mail header)"""
        for header in line_dict.keys():
            count_header_instances(header, keys_found)
            
    obcene_process_feed(line_handler, filename)
    return keys_found
    
def obcene_to_mongo(db, filename):
    """Runs all the steps required for loading an email fresh from the
    file system into it's representation in MongoDB.
    """
    def line_handler(json_data):
        email_dict = obcene_convert_keys(json_data)
        email_doc = LuceneEmail(**email_dict)
        insert_email(db, email_doc)

    obcene_process_feed(line_handler, filename)


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

# This key should never map to a document field
GARBAGE_KEY = '__garbage'

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
    
def _convert_keys(email_dict, alternate_key_map, deepcopy=False):
    """Convert keys takes a python dictionary, representing a lucene document,
    and creates a new document with the keys mapped to their maildir equivalent.
    Uses `obcene_key_map` for the mapping. If a mapping isn't present, it
    leaves the in the map.

    Deepcopy is supported, but off by default to favor speed.
    """
    if deepcopy:
        email_dict = copy.deepcopy(email_dict)
    else:
        email_dict = copy.copy(email_dict) # don't mutate the input
        
    for key, value in email_dict.items():
        if key in obcene_key_map:
            new_key = obcene_key_map[key]
            # handle unicode representations of < and >
            # TODO investigate if more work is necessary here
            value = value.replace('\u003c', '<')
            value = value.replace('\u003e', '>')
            email_dict[new_key] = value
            del email_dict[key]
            
    # dictionary based garbage collection ;)
    if GARBAGE_KEY in email_dict:
        del email_dict[GARBAGE_KEY]

    return email_dict

def obcene_convert_keys(email_dict, deepcopy=False):
    """Short hand for converting keys in a dictionary from obcene to maildir.
    """
    return _convert_keys(email_dict, obcene_key_map, deepcopy=deepcopy)


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


