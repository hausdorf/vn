###
### Default settings
###

### Path to logging output, if used
log_file = './arbre.log'

### Path to the root directory of the raw emails
maildir = "/export/projects/tto6/EnronSimulations/maildir"

### Path to obcene json feed from lucene data
lucene_json = '/home/hltcoe/jdennis/Projects/umdex/lucene_data.json'

### Path to ldc feed
ldc_file = '/export/projects/tto6/EnronSimulations/coe_enron_master.csv'

### Execs file
execs_file = '/export/projects/tto6/EnronSimulations/coe_enron_execs.csv'

### Path to employees feed
employees_file = '/export/projects/tto6/EnronSimulations/employees' # no ext

### Path to lucene project's duplicate id feed
dups_file = '/export/projects/tto6/EnronSimulations/dups-ids.txt'

### Path to location of pickled graphs
graphs_dir = '/home/hltcoe/jdennis/Projects/data/graphs'

### Database settings
DB_HOST = 'gpsrv5'
DB_PORT = 27017
DB_NAME = 'arbre'

### Allows easy override of default settings
try:
    from local_settings import *
except:
    pass
