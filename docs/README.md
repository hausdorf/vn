# Arbre

Arbre is a project for JHU HLTCOE's SCALE project. It initially started out as
a mail database, but is growing into a project that stores relationships of many 
forms. 

The project currently contains multiple parts:

* arbre
* the environment
* apps: mailman, rolodex, hltlib
* obcene
* command line tools

## Arbre Module

Arbre itself is framework that provides a lot of wiring for working with data
and building experiments. The functionality is contained in the `arbre` module
itself.

Logic that is generic and/or shareable exists in the `arbre` module. We 
currently provide: 

* _database.py_: Generic database handling
* _datafeeding.py_: Functions commonly useful to consuming / generating feeds
* _graphs.py_: Functions useful for handling `networkx` graphs
* _models.py_: Common shapes of data. Subclass these for compatibility.
* _timestamping.py_: Functions for simple date handling


## The Environment

Before you start working with Arbre, you should source the environment file.
That looks like this:

    source /path/to/project/etc/arbre_env.sh

That prepares your environment with the `PYTHONPATH` and provides some helpful
shell functions for developing with Arbre.

To change your directory to the Arbre source directory, type `arbre`

    jd@gibson : 19:03:59 : ~
    $ arbre

    jd@gibson : 19:04:01 : ~/Projects/arbre
    $ 
    
To list the currently available apps, type `arbreapp` with no arguments

    jd@gibson : 19:04:01 : ~/Projects/arbre
    $ arbreapp
    hltlib
    mailman
    rolodex
    
To navigate to an app's source directory, type `arbreapp <appname>`.

    jd@gibson : 19:04:06 : ~/Projects/arbre
    $ arbreapp rolodex
    
    jd@gibson : 19:04:09 : ~/Projects/arbre/arbreapp/rolodex
    $

To create a new app, type `arbremkapp <appname>`

    jd@gibson : 19:06:45 : ~/Projects/arbre
    $ arbremkapp newapp
    Creating `newapp` app in /Users/jd/Projects/arbre/arbreapp
    
    jd@gibson : 19:06:48 : ~/Projects/arbre
    $ arbreapp
    hltlib
    mailman
    newapp
    rolodex
    
    jd@gibson : 19:06:54 : ~/Projects/arbre
    $ arbreapp newapp
    
    jd@gibson : 19:06:56 : ~/Projects/arbre/arbreapp/newapp
    $ ls
    __init__.py  models.py    newapp.py    queries.py


## Apps

Arbre comes with a few apps, visible in the `arbreapp` directory. Each app
contains logic for handling less generic data, like Emails or People.

The basic idea is that we store the shapes of data in `models.py` and the 
queries used for retrieving data from mongo in `queries.py`. If the data is
generic enough, we'd like to represent it in `arbre` with everything else
stored in an app.


## Mailman

Mailman is a Python module for mapping email structures into ScaleDB. It 
consists of the model design: `models.py`, the email handling code: 
`mailman.py`, and the query designs: `queries.py`.


### Email Models

The data shapes are modeled in `models.py` using
[DictShield](https://github.com/j2labs/dictshield).

A simplified form of the email model looks like this:

    class Email(Document):
        source = StringField(required=True, default='Email')
        folder = StringField()
        date = MillisecondField(required=True, default=0)
        subject = StringField()
        to = StringField()
        ffrom = EmailField() # from is a keyword
        cc = StringField()
        bcc = StringField()
        body = StringField()


### Email Handling

`mailmail.py` offers three general types of functions. Functions handling:

* Reading emails from a file system
* Processing a list of JSON documents representing emails
* Basic facilities for reading meta data from email headers


### Query Designs

ScaleDB uses MongoDB. MongoDB offers much to like in terms of speed and 
flexibility. The queries offer excellent performance if index structures are
maintained and queries are designed to always have an associated index.

The logic for this is stored in `queries.py`.


## Obcene

Obcene is Java code for reading a lucene index file. It iterates over every 
Document in the index and uses Google's GSON library to write the object as JSON
to a file.

The lucene index path used here: 
/home/hltcoe/bvandurme/Enron/FromDoug/umdex_v3.00/collection/index/enron-duplicate-free/

### Using It

Using it looks like this.

    $ cd arbre/obcene
    $ source ./classpath.sh
    $ ./compile.sh 
    ... might print warnings, my java is rusty ...
    $ ./run.sh /path/to/lucene/index > email_list.json


## Command Line Tools

The command line tools are kept in the `bin/` directory. At the time of this 
writing there are four scripts: `hc_lucene.py`, `hc_maildir.py`, 
`import_lucene.py` and `import_maildir.py`. 

The hc_* scripts will read a data source and do a header count. This has been 
useful for determining, somewhat comprehensively, how to model the emails.

The import_* scripts know how to read data created from some source. They 
generate two types of Python models, `MaildirEmail` and `LuceneEmail`. The 
`import_maildir.py` script reads a path from settings.py and iterates it's way
through the directory recursively creating a `MaildirEmail` instance for each 
one. The `import_lucene.py` script iterates of a list of JSON documents.

The list of JSON documents for a lucene import comes from using Obcene.

Both import scripts map the import data into `DictShield` documents. The 
document is initially modeled after the `MaildirEmail`. The lucene import script
makes use of conversion functions to map it's format into a structure similar to 
`MaildirEmail` by renaming fields. 

Both emails have roughly the same fields so actual changes were minimal. Common
fields are modeled in `Email`.


### Using Them

This is what using it looks like:

    jd@gibson : 12:41:58 : ~/Projects/arbre
    $ source ./etc/arbre_env.sh # ensures python path includes cwd
    
    jd@gibson : 12:42:07 : ~/Projects/arbre
    $ workon arbre # turn on virtual environment
    
    (arbre)
    jd@gibson : 12:42:10 : ~/Projects/arbre
    $ ./bin/hc_lucene.py 
    {'ccAddress': 6, 'ea-from': 22, 'quoted': 76, 'cc': 6, 'sal-line': 1, '---': 76, 'bccName': 6, 'bccAddress': 6, 'fromAddress': 100, 'contents': 100, 'subject': 100, 'contents-lines': 100, 'x-cc': 16, 'from': 19, 'fromName': 100, 'unstemmed-contents': 100, 'num-quoted': 100, 'to': 14, 'ccName': 6, 'folder': 100, 'inReplyTo': 100, 'ea-to': 1, 'quoted-lines': 76, 'sig-block-lines': 7, 'messageID': 100, 'date': 100, 'x-to': 74, 'toName': 100, 'toAddress': 100, 'x-list-from': 1, 'sig-block': 7, 'quote-type': 76, 'length': 100, 'sal-line-lines': 1, 'x-from': 46}
    
    (arbre)
    jd@gibson : 12:42:13 : ~/Projects/arbre
    $ ./bin/import_lucene.py 
    
    (arbre)
    jd@gibson : 12:44:17 : ~/Projects/arbre
    $ ./bin/import_ldcfile.py

    (arbre)
    jd@gibson : 12:46:27 : ~/Projects/arbre
    $
