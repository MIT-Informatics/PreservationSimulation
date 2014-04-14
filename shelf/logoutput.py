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
from NewTraceFac import TRC,trace,tracef

# Create a single logger instance for use all over the place.
# Necessary because we use the same formatter and handler across modules.  
logger = logging.getLogger("LGOU")
    
@tracef("LGOU")
def logSetConfig(mysLogLevel,mysLogFile):
    lLogLevels = 'NOTSET CRITICAL ERROR WARNING INFO DEBUG'.split()
    sLogLevel = mysLogLevel.upper()
    if sLogLevel not in lLogLevels:
        TRC.tracef(0,"LGOU","ERROR unrecognized logging level|%s|" % (mysLogLevel))
        sLogLevel = "NOTSET"

    # Set the logging level for this session.
    TRC.tracef(3,"LGOU","proc sLogLevel|%s|"%(sLogLevel))
    logger.setLevel(sLogLevel.upper())

    ''' Set the output file for logging.
        Either to a filename in LOG_FILE param or environ variable, 
        or to the console using StreamHandler.
    '''
    if  mysLogFile != ""    \
    and mysLogFile != " "   \
    and mysLogFile != "-"   \
    and mysLogFile.upper() != "NONE"    \
    and mysLogFile.upper() != "CONSOLE" \
    and mysLogFile.upper() != "STDOUT"  :
        channel = logging.FileHandler(mysLogFile)
    else:
        channel = logging.StreamHandler()
    TRC.tracef(3,"LGOU","proc set log handler mysLogFile|%s|" % (mysLogFile))

    ''' Adjust the format of log output to match the time stamps
        we have used in TRACE forever.  
    '''
    # Create formatter instance.
    formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)s - %(message)s', datefmt='%Y%m%d_%H%M%S')
    # Add formatter to the output channel.
    channel.setFormatter(formatter)
    # Finally, add the channel handler to the logger.
    logger.addHandler(channel)
    
    return logger

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

# Use debug for really, really detailed log info.  
def logDebug(myname,mystring):
    logger.name = myname
    logger.debug(mystring)
    return logger

# Use error for real errors like permanent document failures.  
def logError(myname,mystring):
    logger.name = myname
    logger.error(mystring)
    return logger

# Use critical for errors even worse than that.  What?  
def logCritical(myname,mystring):
    logger.name = myname
    logger.critical(mystring)
    return logger

# END
