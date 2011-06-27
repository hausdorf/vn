# Arbre Environment
#
# This script sets a few environment variables and defines some functions 
# intended to make development with Arbre easy.
#
# The top of this file must be functions. The functions that affect your shell
# environment are called after the function definitions shell commands are
# escaped with a '\' to avoid accidental use of shell aliases.
#
# It's design is inspired by virtualenvwrapper:
# * http://pypi.python.org/pypi/virtualenvwrapper
# * http://j2labs.tumblr.com/post/5181438807/quick-dirty-virtualenv-virtualenvwrapper


###
### Functions
###

### Shortcut for cd'ing to project dir
arbre () {
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

### Updates PYTHONPATH to include any directories in $ARBRE_APP_PATH
arbresetapppaths() {
    PYTHONPATH=$PREV_PYTHONPATH
    for app in `\ls -l "$ARBRE_APP_PATH" | \grep "^d" | \cut -d " " -f 12`:
    do
        PYTHONPATH="$ARBRE_APP_PATH/$app:$PYTHONPATH"
    done
    export PYTHONPATH
}

### Initializes the environment for Arbre
arbreactivate() {
    ### Figure out the path to Arbre based on where this file `arbre_env.sh` lives
    export ARBRE_ENV_PATH=$(dirname $ARBRE_ENV_SCRIPT)

    ### Set project directory path
    export ARBRE_DIR=$(dirname $ARBRE_ENV_PATH)

    ### Set var for app path
    export ARBRE_APP_PATH=$(cd "$ARBRE_DIR/arbreapp"; pwd)

    ### Hardcode paths to the apps
    export PREV_PYTHONPATH=$PYTHON_PATH # Modify this value and pay with yer liiife!

    ### Update PYTHONPATH with a call to arbresetapppaths
    arbresetapppaths
}

### Returns PYTHONPATH to normal value
arbredeactivate () {
    export PYTHONPATH=$PREV_PYTHONPATH
}


###
### Environment Adjustments
###

### `source`ing this file causes anything below here to occur
export ARBRE_ENV_SCRIPT=${BASH_SOURCE[@]}
arbreactivate
