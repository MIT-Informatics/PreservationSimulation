#!/usr/bin/python
# logoutput.py
# RBLandau 20140315

''' Wrapper for the Python logging facility.
    To log events as INFO, we want the output to look all the same.
    Use the same output format we have used forever for TRACE:
        timestamp facility level content
    To do this, we need to assign the fancy output to a single logger
     instance, and pass that instance around to various modules.  
     The Formatter is attached to the Handler, and then the Handler
     is attached to the Logger.  We would have to repeat all that 
     guff in every module to achieve the same results = similar output.  
    Modules can/will insert their own names into the logged lines, 
     so that the facility of origin can be traced. 
'''

import logging
from os import environ
from NewTraceFac import TRC,trace,tracef

# Create a single logger instance for use all over the place.
# Necessary because we use the same formatter and handler across modules.  
logger = logging.getLogger("LGOU")

''' Determine logging level.
    This can be numeric, 0 thru 5 the same as NewTrace, or string.
'''
TRC.tracef(5,"LGOU","environment vars|%s|" % (environ))
sLogLevels = 'NOTSET CRITICAL ERROR WARNING INFO DEBUG'.split()
try:                        # try integer first, convert to string
    sLogLevel = "NOTSET"
    nLogLevel = int(environ['LOG_LEVEL'])
    sLogLevel = sLogLevels[nLogLevel]
except ValueError:          # not an integer, take the string
    sLogLevel = environ['LOG_LEVEL'].upper()
except (IndexError,TypeError):  # integer out of range
    TRC.tracef(0,"LGOU","BUGCHECK: invalid logging level |%s|" % (nLogLevel))
    raise ValueError
except KeyError:            # log_level not specified in environment
    pass                    # leave it as NOTSET
finally:
    if sLogLevel not in sLogLevels:
        TRC.tracef(0,"LGOU","BUGCHECK: invalid logging level |%s|" % (sLogLevel))
        raise ValueError
    
# Set the logging level for this session.
TRC.tracef(3,"LGOU","proc sLogLevel|%s|"%(sLogLevel))
logger.setLevel(sLogLevel)

''' Set the output target for logging.
    Either to a filename in LOG_TARGET environ variable, 
    or to the console using StreamHandler.
'''
TRC.tracef(5,"LGOU","proc full environment|%s|" % (environ))
try:
    sLogTarget = environ['LOG_TARGET']
    channel = logging.FileHandler(sLogTarget)
except KeyError:
    sLogTarget = None
    channel = logging.StreamHandler()
TRC.tracef(3,"LGOU","proc sLogTarget|%s|"%(sLogTarget))
''' Adjust the format of log output to match the time stamps
    we have used in TRACE forever.  
'''
# Create formatter instance.
formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)s - %(message)s', datefmt='%Y%m%d_%H%M%S')
# Add formatter to the output channel.
channel.setFormatter(formatter)
# Finally, add the channel handler to the logger.
logger.addHandler(channel)

''' How2Uz, method 1
    First, get a pointer to the correct logger instance 
    with the correct module name (or whatever name you prefer):
        LOGME = logoutput.getLogger(__name__)
    Then log away in the usual fashion.  
    Examples: 
        LOGME.debug('debug message')
        LOGME.info('info message')
        LOGME.warn('warning message')
        LOGME.error('error message')
        LOGME.critical('critical message')
    I tend to use highly visible capitalized names for such functions.
    Remember to import getLogger.
'''

def getLogger(myname):
    logger.name = myname
    return logger

''' How2uz, method 2
    To be on the safe side, combine the name and string into a 
    single call, just in case your module calls another that 
    would change the name.  
    Remember to import logInfo.
'''
def logInfo(myname,mystring):
    logger.name = myname
    logger.info(mystring)
    return logger
    
# END
