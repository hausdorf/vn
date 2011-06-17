#!/usr/bin/env python

from arbre.database import init_dbconn
from arbreapp.mailman import mailman
from settings import lucene_json

db = init_dbconn()
mailman.obcene_to_mongo(db, lucene_json)
