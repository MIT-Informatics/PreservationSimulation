#!/usr/bin/python
# brokerformat.py

# CFormat class for broker to use.
# Ripped out of broker.py to help de-clog that module.
# Some slight changes in calling sequence are required:
#  there are references to g and CG; those will have to 
#  be added as parameters and passed in as arguments.
# - GentlyFormat used to just reach into the global data
#    at will, and that cannot be done here.  
# - Also, fnsMaybeTest looks at a global flag, so it also
#    needs access to g.
# 

from catchex import catchex
from NewTraceFac import NTRC, ntrace, ntracef
import re
import  json


#===========================================================

# c l a s s   C F o r m a t 
class CFormat(object):

# m s G e n t l y F o r m a t 
    @ntracef("FMT", level=5)
    def msGentlyFormat(self, mysCmd, mydVals, myg, myCG):
        '''
        Like string.format() but does not raise exception if the string
         contains a name request for which the dictionary does not have 
         a value.  Leaves unfulfilled name requests in place.  
        Method: construct a dictionary that contains something for every
         name requested in the string.  The value is either a supplied 
         value from the caller or a placeholder for the name request.  
         Then use the now-defanged string.format() method.
        This is way harder than it ought to be, grumble.  
        '''
        # Make a dictionary from the names requested in the string
        #  that just replaces the request '{foo}' with itself.  
        sReNames = '(:?\{([^\}]+)\})+'
        oReNames = re.compile(sReNames)
        lNameTuples = oReNames.findall(mysCmd)
        NTRC.ntracef(3,"FMT","proc gently tuples|%s|" % (lNameTuples))
        lNames = [x[1] for x in lNameTuples]
        dNames = dict(zip(lNames, map(lambda s: "{"+s+"}", lNames)))
        # Pick up any specified values in the global object 
        #  and from CLI args.
        dNames.update(dict(vars(myCG)))
        dNames.update(dict(vars(myg)))
        # And then add values from the specific instructions.
        dNames.update(mydVals)
        NTRC.ntrace(3,"proc gently dnames|%s|" % (dNames))
        sOut = mysCmd.format(**dNames)
        return sOut

# f n d F o r m a t Q u e r y 
    @ntracef("FMT")
    def fndFormatQuery(self, mydCli, myg):
        '''
        Take all the CLI options that might specify a searchable attribute, and 
         construct a MongoDB or searchspace query dictionary.  
         This is lots nastier than it first appears to be
         because json is so bloody picky.
        '''
        dOut = dict()
        for sAttrib,sValue in mydCli.items():
            result = None
            if sValue is not None:
                # Is it something valid in json?                
                try:
                    result = json.loads(sValue)
                except ValueError:
                    # Is it a string that should be an integer, ok in json?
                    try:
                        result = int(sValue)
                    except:
                        # Is it a naked string for some string-valued var
                        #  that isn't just Y/N or a mandatory string?  
                        #  Rule out dict values that are already formatted.
                        if (isinstance(sValue, str)
                            and sAttrib not in myg.lYesNoOptions
                            and sAttrib not in myg.lMandatoryArgs
                            and '{' not in sValue
                            and '}' not in sValue
                            and ':' not in sValue
                            and ',' not in sValue
                            ):
                            result = '{"$eq":' + '"'+sValue+'"' + '}'
                        else:
                            result = sValue
                    NTRC.tracef(3, "FMT", "proc FormatQuery notjson item "
                        "key|%s| val|%s| result|%s|" 
                        % (sAttrib, sValue, result))
            NTRC.tracef(3, "FMT", "proc FormatQuery item key|%s| val|%s| result|%s|" 
                % (sAttrib, sValue, result))
            # Can't process dicts thru json twice.
            if isinstance(result, dict):
                dOut[sAttrib] = sValue
            else:
                dOut[sAttrib] = result

        # Allow only attribs that appear in the database, else will get 
        #  no results due to implied AND of all items in query dict.  
        dOutSafe = {k:v for k,v in dOut.items() if k in myg.lSearchables}
        dOutNotNone = {k:v for k,v in dOutSafe.items() if v is not None}
        NTRC.ntracef(3,"FMT","proc dict b4|%s| \nsafe|%s|\nclean|%s|" 
            % (dOut,dOutSafe,dOutNotNone))
        if "sQuery" in dOutNotNone.keys():
            # If the brave user has supplied a full, standalone query string,
            #  add its contents to the query dict so far.
            dTmp = dOutNotNone["sQuery"]
            del dOutNotNone["sQuery"]
            dOutNotNone.update(dTmp)
        return dOutNotNone

# f n s M a y b e T e s t 
    @ntracef("FMT")
    def fnsMaybeTest(self, mysCommand, myg):
        '''
        If TestCommand option is present, then change the command line to a line
         that just echos the command line instead of actually doing it.
        '''
        if myg.sTestCommand.startswith("Y"):
            sCommand = 'echo "{}"'.format(mysCommand)
        else:
            sCommand = mysCommand
        return sCommand

# Edit history:
# 20170520  RBL Original version, extracted from broker.py.  
# 
# 

#END
