#!/usr/bin/env python

from arbreapp.mailman import mailman
from settings import lucene_json

keys_count = mailman.obcene_header_count(lucene_json)
print keys_count
