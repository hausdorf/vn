from arbre.database import init_apply_all_indexes

import pymongo


###
### Collection Config
###
EMPLOYEES_COLL = 'employees'
EMPLOYEE_MEASURES_COLL = 'employee_measures'


###
### Index Handling
###

indexes = {
    ## Indexes for the email collection
    EMPLOYEES_COLL: [
        [('source', pymongo.ASCENDING),
         ('email_name', pymongo.ASCENDING)],
        
        [('source', pymongo.ASCENDING),
         ('full_name', pymongo.ASCENDING)],
    ],

    ## Indexes for communications collection
    EMPLOYEE_MEASURES_COLL: [
        [('source', pymongo.ASCENDING),
         ('employee_id', pymongo.ASCENDING),
         ('name', pymongo.ASCENDING)],
        
        [('source', pymongo.ASCENDING),
         ('employee', pymongo.ASCENDING),
         ('name', pymongo.ASCENDING)],
    ],
}

apply_all_indexes = init_apply_all_indexes(indexes)


###
### Employee Queries
###

def find_employees(db, source=None, email_name=None, full_name=None,
                   count=50, page=0):
    """Comments.
    """
    query_dict = dict();

    # run query and apply paging 
    db_cursor = db[EMPLOYEES_COLL].find(query_dict)
    db_cursor.limit(count) # limit(0) = no limit
    db_cursor.skip(page * count)
    
    return db_cursor

def insert_employee(db, employee):
    """Comments.
    """
    employee_id = db[EMPLOYEES_COLL].insert(employee.to_python())
    employee.id = employee_id
    apply_all_indexes(db, EMPLOYEES_COLL)
    
    return employee



###
### Employee Measure Queries
###

def find_employee_measures(db, **kwargs):
    """Comment.
    """
    pass


def insert_employee_measure(db, email):
    """Comment.
    """
    #apply_all_indexes(db, EMPLOYEE_MEASURES_COLL)
    pass
