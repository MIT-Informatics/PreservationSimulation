#!/usr/bin/python
# logoutput.py
# RBL

import logging
from os import environ
from NewTraceFac import TRC,trace,tracef

# create logger instance
logger = logging.getLogger("LGOU")

''' Determine logging level.
    This can be numeric, 1 thru 5 the same as NewTrace, or string.
'''
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
TRC.tracef(5,"LGOU","proc sLogLevel|%s|"%(sLogLevel))
logger.setLevel(sLogLevel)

''' Set the target output for logging.
    Either a filename in LOG_TARGET environ variable, 
    or console using StreamHandler.
'''
try:
    sLogTarget = environ['LOG_TARGET']
    channel = logging.FileHandler(sLogTarget)
except KeyError:
    sLogTarget = None
    channel = logging.StreamHandler()

''' Adjust the format of log output to match the time stamps
    we have used in TRACE forever.  
'''
# create formatter
formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)s - %(message)s', datefmt='%Y%m%d_%H%M%S')
# add formatter to channel
channel.setFormatter(formatter)
# add channel handler to logger
logger.addHandler(channel)

''' How2Uz
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
'''

def getLogger(myname):
    logger.name = myname
    return logger

# END
