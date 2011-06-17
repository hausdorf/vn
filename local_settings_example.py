###
### Settings Override Example
###
### If you need to override any default settings, create a file called
### `local_settings.py` and override values like you see below
###

maildir = '/Users/jd/Projects/scale/data/maildir'
#maildir = '%s%s' % (maildir, '/skilling-j/')
lucene_json = '/Users/jd/Projects/scale/data/lucene/lucene_data.json'
#lucene_json = '/Users/jd/Projects/scale/data/lucene/lucene_top100.json'
ldc_file = '/Users/jd/Projects/scale/data/coe_enron_master.csv'
employees_file = '/Users/jd/Projects/scale/data/employees'
execs_file = '/Users/jd/Projects/scale/data/coe_enron_execs.csv'
dups_file = '/Users/jd/Projects/scale/data/lucene/dups-ids.txt'
graphs_dir = '/Users/jd/Projects/scale/data/graphs'

DB_HOST = 'localhost'
