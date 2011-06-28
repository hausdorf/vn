"""This module is for moshing data. It aims to provides helpful functions for
common interactions with filesystems, json feeds, web feeds, etc.
"""

import os
import fnmatch
import simplejson as json


###
### Filesystem Helpers
###

def locate_by_pattern(pattern, root_dir):
    """This is a generator for recursively detecting files with names that
    match the given pattern in a directory.

    The pattern can be any regular expression identifying files.

    The root_dir is the directory from which to recurse.
    """
    for path, dirs, files in os.walk(os.path.abspath(root_dir)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


###
### Feed Handing
###

def process_json_feed(fun, filename):
    """Loops across each line in `filename` and converts the data from JSON to
    a Python dictionary.

    It then calls `fun` which is a function provided by the caller that takes
    one argument, the line of data.

    No return value is generated to avoid overhead, but `fun` should be a
    closure for aggregating values.
    """
    fd = open(filename, 'r')
    for line in fd:
        data = json.loads(line)
        fun(data)
    fd.close()


###
### Feed Conversions
###

"""
The garbage key is used for fields we know to be uninteresting. An example
conversion map might look like below.
#
The conversion map is intended for use with `convert_keys`.
#
    gc_key_map = {
        'to': 'toAddress',
        'time': 'sendTime'
        '---': GARBAGE_KEY,
        'date': GARBAGE_KEY, # redundant with 'time'
    }
"""
GARBAGE_KEY = '__garbage__'

def convert_keys(data_dict, alternate_key_map, conversion_map, deepcopy=False):
    """Convert keys takes a python dictionary, representing a lucene document,
    and creates a new document with the keys mapped to their maildir equivalent.
    Uses `obcene_key_map` for the mapping. If a mapping isn't present, it
    leaves the in the map.

    Deepcopy is supported, but off by default to favor speed.
    """
    if deepcopy:
        data_dict = copy.deepcopy(data_dict)
    else:
        data_dict = copy.copy(data_dict) # don't mutate the input
        
    for key, value in data_dict.items():
        if key in conversion_map:
            new_key = conversion_map[key]
            # handle unicode representations of < and >
            # TODO investigate if more work is necessary here
            value = value.replace('\u003c', '<')
            value = value.replace('\u003e', '>')
            data_dict[new_key] = value
            del data_dict[key]
            
    # dictionary based garbage collection ;)
    if GARBAGE_KEY in data_dict:
        del data_dict[GARBAGE_KEY]

    return data_dict

    
