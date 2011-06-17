#!/usr/bin/env python

from arbre.database import init_dbconn
from arbreapp.mailman import mailman
from settings import maildir

db = init_dbconn()
mailman.maildir_to_mongo(db, maildir)
