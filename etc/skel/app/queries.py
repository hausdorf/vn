from arbre.database import init_apply_all_indexes, gen_date_args

import pymongo


###
### Sample Collection Config
###

SAMPLE_COLL = 'sample'


###
### Index Handling - http://www.mongodb.org/display/DOCS/Indexes
###

indexes = {
    ## Indexes for the email collection
    SAMPLE_COLL: [
        [('some_string', pymongo.ASCENDING),
         ('timestamp', pymongo.ASCENDING)],
        
        [('timestamp', pymongo.ASCENDING)],
    ],
}

### Generate a function that handles index management.
apply_all_indexes = init_apply_all_indexes(indexes)


###
### Query Functions - http://www.mongodb.org/display/DOCS/Querying
###

def find_samples(db, some_string=None, start_date=None, end_date=None,
                 count=50, page=0):
    """An example of how a Mongo Query might look for the sample project.
    """
    query_dict = {}

    if some_string:
        query_dict['some_string'] = some_string

    # Date arguments have some complexity. 
    date_args = gen_date_args(start_date, end_date)
    if len(date_args.keys()) > 0:
        query_dict = {
            'timestamp': date_args,
        }

    # Run the query on Mongo and get a cursor
    db_cursor = collection.find(query_dict)
    db_cursor.limit(count) # limit(0) = no limit
    db_cursor.skip(page * count)

    # The cursor is iterable for a caller, so just hand it over
    return db_cursor
