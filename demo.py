#!/usr/bin/env python

from arbre.database import init_dbconn
from arbreapp.mailman.queries import find_emails, find_communications

### Some basics on querying

# We first initialize our database connection
db = init_dbconn()

# count=0 means no limit on query size
# cursor = find_emails(source='lucene', count=0)
cursor = find_emails(db, source='maildir') # defaults to limit of 50 emails

senders = list()
for email in cursor:
    if 'to' in email and 'ffrom' in email:
        senders.append((email['to'], email['ffrom']))
print 'An example list:\n%s\n' % (senders)

### Generating the list of recipients between 1/1/2001 and 1/5/2001

start_datetext = "January 1, 2001"
end_datetext = "1/5/2001"
cursor = find_communications(db, source='maildir', start_date=start_datetext,
                             end_date=end_datetext)

early_january_recips = [email['to'] for email in cursor]
print 'Recipients of email between %s and %s:' % (start_datetext, end_datetext)
print early_january_recips
print ''


