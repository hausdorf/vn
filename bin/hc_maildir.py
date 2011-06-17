#!/usr/bin/env python

from arbreapp.mailman import mailman
from settings import maildir

keys_count = mailman.maildir_header_count(maildir)
print keys_count

