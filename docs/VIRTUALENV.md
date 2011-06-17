# VirtualEnv

Virtualenv lets us create isolated python environments and control what
versions of software is used for each environment we create. 

It is also easy to install. I recommend using pip. It's like easy_install,
but better.

   pip virtualenv virtualenvwrapper

You will need to source a shell script provided by virtualenvwrapper and
configure a directory for where your virtualenv's are stored.

That looks like this:

    $ mkdir ~/.virtualenvs
    $ export WORKON_HOME="$HOME/.virtualenvs"
    $ source /usr/local/bin/virtualenvwrapper.sh

I put that in my .bashrc. 

Once the shell script is sourced, you get access to a some new commands. I 
primarily use three: `mkvirtualenv`, `deactivate` and `workon`.

## Using It

To create a virtualenv, use: `mkvirtualenv <some name>`

After creating a virtualenv, notice that it's automatically activated. If you
open a new shell and need to activate a virtualenv, you would use `workon`. 
Type `workon` on it's own and you get a list of every virtualenv. 

To activate a virtualenv: `workon <some name>`

To deactivate a virtualenv: `deactivate <some name>`

## Installing ScaleDB's env

    $ mkvirtualenv arbre
    Running virtualenv with interpreter /usr/local/bin/python
    New python executable in arbre/bin/python
    Installing setuptools............................done.
    ...
    
    (arbre)
    $ cd Projects/arbre/
    
    (arbre)
    $ ls
    bin/  demo.py*  etc/  INSTALL.md  arbreapp.mailman/  obcene/  README.md  settings.py  setup.py
    
    (arbre)
    $ pip install -I -r ./etc/requirements.txt 
    Downloading/unpacking dictshield==0.2.1 (from -r ./etc/requirements.txt (line 1))
    ...
    Installing collected packages: dictshield, pymongo, python-dateutil, simplejson
    ...
    Successfully installed dictshield pymongo python-dateutil simplejson
    Cleaning up...

    (arbre)
    $
