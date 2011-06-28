"""Rolodex is a module for catalog
"""

from models import Employee
from queries import insert_employee


###
### Email File Handling Functions
###

def line_to_employee(db, feed_line):
    data = {}
    
    # Every line starts with a field, then a tab
    (email_name, tail) = feed_line.split('\t')
    data['email_name'] = email_name

    # Split tail by double spaces and find any fields with data
    def keep_it(s):
        s = s.strip()
        return s != "" and s != "xxx"
    tail_items = [x.strip() for x in tail.split('  ') if keep_it(x)]

    # Try to match fields with known headers
    tail_cols = ['full_name', 'position', 'comments']
    for field,value in zip(tail_cols, tail_items):
        data[field] = value

    employee_doc = Employee(**data) 
    employee_id = insert_employee(db, employee_doc)
    employee_doc.id = employee_id
    
    return employee_doc

def employees_process_feed(db, filename):
    fd = open(filename, 'r')
    for line in fd:
        line_to_employee(db, line)

