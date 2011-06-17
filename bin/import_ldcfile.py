#!/usr/bin/env python

from arbre.database import init_dbconn
from arbreapp.mailman import mailman
from settings import ldc_file, dups_file

db = init_dbconn()
mailman.process_ldc_file(db, ldc_file, dups_file=dups_file)
