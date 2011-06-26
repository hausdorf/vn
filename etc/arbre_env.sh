# Arbre Environment

# This script sets a few environment variables and defines some functions 
# intended to make developing with Arbre easy.
#
# It's design is inspired by virtualenvwrapper [1]
#
# `cdapp` with no arguments prints a list of apps in the arbreapp directory.
# With arguments it cd's the user into the app's source directory.
#
# Shell commands are escaped with a '\' to avoid accidental use of shell aliases
# 
# 1. http://pypi.python.org/pypi/virtualenvwrapper


### Get full path to ARBRE_DIR regardless of where this file is sourced from
ARBRE_ENV_PATH=$(dirname ${BASH_SOURCE[@]}) # path to this file
ARBRE_ETC_PATH=$(cd $ARBRE_ENV_PATH; pwd)
export ARBRE_DIR=$(dirname $ARBRE_ETC_PATH)

### Hardcode paths to the apps
export PREV_PYTHONPATH=$PYTHON_PATH
export PYTHONPATH="$ARBRE_DIR:$ARBRE_DIR/arbreapp/hltlib/:$ARBRE_DIR/arbreapp/mailman/:$ARBRE_DIR/arbreapp/rolodex/:$PYTHONPATH"

### Shortcut for cd'ing to project dir
arbrecd () {
    \cd $ARBRE_DIR
}

### Shortcut for cd'ing to app path. Lists apps if no argument is given
arbreapp () {
    typeset app_name="$1"
    typeset app_path="$ARBRE_DIR/arbreapp/$app_name/arbreapp/$app_name"

    if [ "$app_name" = "" ]
    then
        \ls -l "$ARBRE_DIR/arbreapp" | \grep "^d" | \cut -d " " -f 12
    elif [ -d "$app_path" ]
    then
        \cd $app_path
    fi
}    

### Returns PYTHONPATH to normal value
arbredeactivate () {
    export PYTHONPATH=$PREV_PYTHONPATH
}
