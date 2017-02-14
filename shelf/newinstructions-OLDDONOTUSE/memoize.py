# memoize.py
#
# Fairly trivial memoize decorator for use with more or less any function.
# Works with *args, **kwargs, and unhashable types.  
# Perhaps not the most efficient, but fairly bulletproof.  
# From PythonWiki.
# With apologies to Clorox Bleachman, the actress not the drag queen.
#                   RBLandau 20151124

import functools
def memoize(rememberme):
    cache = {}
    @functools.wraps(rememberme)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if not key in cache:
            cache[key] = rememberme(*args, **kwargs)
        return cache[key]
    return memoizer
