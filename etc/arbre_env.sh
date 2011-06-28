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
    ### Figure out the absolute path to Arbre based on where this file 
    ### `arbre_env.sh` lives
    export ARBRE_ENV_PATH=$(cd $(dirname $ARBRE_ENV_SCRIPT); pwd) # total hack :)

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
arbredeactivate() {
    export PYTHONPATH=$PREV_PYTHONPATH
}

### Constructs the necessary and generic components of an Arbre app
arbremkapp() {
    typeset app_name="$1"
    echo $app_name
    typeset app_dir="$ARBRE_APP_PATH/$app_name/arbreapp/$app_name"
    echo $app_dir

    if [ "$app_name" = "" ]
    then
        echo "Pass <name> argument to name app"
    else
        # Instantiate the necessary directory path
        \mkdir -p "$app_dir"

        # Copy the namespace sharing __init__
        # http://docs.python.org/library/pkgutil.html#pkgutil.extend_path
        \cp "$ARBRE_ENV_PATH/skel/appfiles/__init__.py" "$ARBRE_DIR/arbreapp/$app_name/"

        # Touch the other necessary __init__'s
        \touch "$ARBRE_DIR/arbreapp/$app_name/__init__.py"
        \touch "$ARBRE_DIR/arbreapp/$app_name/arbreapp/__init__.py"
        \touch "$ARBRE_DIR/arbreapp/$app_name/arbreapp/$app_name/__init__.py"
    fi
}


###
### Environment Adjustments
###

### `source`ing this file causes anything below here to occur
export ARBRE_ENV_SCRIPT=${BASH_SOURCE[@]}
arbreactivate
