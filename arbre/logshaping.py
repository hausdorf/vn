import logging
import time


###
### Log Handling
###

def init_log(level=logging.DEBUG, filename='arbre.log', **kwargs):
    """Function that initializes logging. It currently exists as a place holder
    for a potentially more robust alternative.

    Will accept keyword arguments that it passes along to the logging module.

    More info: http://docs.python.org/library/logging.html
    """
    logging.basicConfig(level=level, filename=filename, **kwargs)


###
### Logging Decorators
###

def log_call(method):
    """Decorator that logs the name and time of any wrapped functions.
    """
    def wrapper(*a, **kw):
        now = time.time()
        logging.debug('%s called at %s' % (method.__name__, time.time()))
        return method(*a, **kw)
    return wrapper

    
def log_runtime(method):
    """Decorator that logs the duration of any wrapped function.
    """
    def wrapper(*a, **kw):
        start = time.time()
        retval = method(*a, **kw)
        finish = time.time()

        logging.debug('%s took %s seconds to run'
                      % (method.__name__, (finish - start)))
        return retval
    return wrapper
