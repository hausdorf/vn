#!/usr/bin/env python

from arbre.database import init_dbconn
from arbreapp.rolodex import rolodex
from settings import employees_file

db = init_dbconn()
rolodex.employees_process_feed(db, employees_file)
