#!/usr/bin/python
# catchex.py
#
#                       RBLandau 20150720
#
# Debugging decorator to make sure we catch exceptions locally.  
#  SimPy recent version seems to leave an outer exception handler
#  in the middle of nowhere that is singularly uninformative.  
#  It poisons the traceback and never shows the line that failed.  
#

from functools import wraps
import sys, traceback

def catchex(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        try:
            result = func(*args,**kwargs)
        except Exception as exc:
            type,value,tb = sys.exc_info()
            exctype = repr(value)[0:repr(value).index('(')]
            print 'Caught exception: %s: %s' % (exctype, exc)
            traceback.print_tb(tb)
            print ""
            raise 
        return result
    return wrapper 

# Example of use:
#   from catchex import catchex
#   @catchex
#   def somefunction(someargs):
#       do something that might screw up
#
