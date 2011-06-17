# INSTALLING SCALEDB

At it's most basic, Python and MongoDB are necessary. Java is required for using
obcene.

ScaleDB requires some python modules too. The necessary packages are listed in 
`etc/requirements.txt`. This list can be installed using pip or each item can be
installed by hand with easy_install.


# Python

If you are on a mac, you already have Python. If you'd like to use a specific
version, consider using either Homebrew or Mac Ports to manage that. 

I use Mac Ports, so installing looks like this:

    $ sudo port install python26 python_select
    ...
    $ sudo python_select python26

Mac Ports supports flipping back and forth between the system Python and other
ones installed by using the `python_select` tool.

    $ python_select -l
    Available versions:
    current python26 python26-apple python27 python32


# MongoDB

Installing MongoDB on Mac Ports. 

    $ sudo port install mongodb

[Installing on Ubuntu](http://www.mongodb.org/display/DOCS/Ubuntu+and+Debian+packages)


# Python Module Dependencies

In ScaleDB's requirements file, we see DictShield, PyMongo, Dateutil and
SimpleJSON. The versions I have had success with are listed there too. All of 
these modules should be installable using `easy_install`, but I recommend `pip`.

In short: `easy_install dictshield pymongo python-dateutil simplejson`

## Pip

pip is like easy_install but better. For example, installing that requirements
file looks like this with pip.

    $ cat etc/requirements.txt
    dictshield==0.2.1
    pymongo==1.10
    python-dateutil==1.5
    simplejson

    $ pip install -I -r etc/requirements.txt

Pip let's us manage the specific module versions we care about by listing them
in a file. You can create a requirements file out of your current environment
by using `pip freeze`.

Installing pip:
* Ubuntu: `apt-get install python-pip`
* Fedora: yum install python-pip.noarch
* Mac Ports: port install py26-pip

