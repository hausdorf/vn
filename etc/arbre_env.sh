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
    #typeset app_path="$ARBRE_DIR/arbreapp/$app_name/arbreapp/$app_name"
    typeset app_path="$ARBRE_DIR/arbreapp/$app_name"

    if [ "$app_name" = "" ]
    then
        \ls -l "$ARBRE_DIR/arbreapp" | \grep "^d" | \cut -d":" -f 2 | \cut -d" " -f 2
    elif [ -d "$app_path" ]
    then
        \cd $app_path
    fi
}    

### Updates PYTHONPATH
arbresetapppaths() {
    PYTHONPATH=$PREV_PYTHONPATH
    export PYTHONPATH=".:$PYTHONPATH"
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
    typeset app_dir="$ARBRE_APP_PATH/$app_name"

    if [ "$app_name" = "" ]
    then
        echo "Pass <name> argument to name app"
    else
        echo "Creating \`$app_name\` app in $ARBRE_APP_PATH"

        # Instantiate the necessary directory path
        \mkdir -p "$app_dir"

        # Copy the app template files into place
        \cp -R "$ARBRE_ENV_PATH/skel/app/"* "$app_dir" # Weird... "String"*
        \mv "$app_dir/app.py" "$app_dir/$app_name.py"
    fi
}


###
### Environment Adjustments
###

### `source`ing this file causes anything below here to occur
export ARBRE_ENV_SCRIPT=${BASH_SOURCE[@]}
arbreactivate
