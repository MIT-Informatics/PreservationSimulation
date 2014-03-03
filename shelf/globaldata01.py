#!/usr/bin/python

    
# G L O B A L  D A T A 
#---------------------

class G(object):
    ''' Global r/w data, of which we are sure there is only one copy.
        Use this only for truly global data that would be just
        too painful to pass around all the time.  
        Never instantiated; used only as a dictionary.
        Not everything is pre-declared here; some is added later.  
    '''
    env = None
    lLibraries = list()
    nLibraries = 1
    nClients = 1
    lAllClients = list()
    dQual2Libs = dict()
    nDocLastID = None
    nCollLastID = None
    nShelfLastID = None
    dID2Document = dict()
    dID2Shelf = dict()
    dID2Collection = dict()
    dID2Library = dict()
    dID2Client = dict()
    dQual2Libs = dict()

class P(object):
    ''' Parameters r/o for the simulation run. 
        In an adult world, all this would be read from txt or json files.
        This area might not be quite 100% read-only.  For instance, we might 
        overwrite these from a file or command-line arguments.  
    '''
    # Client has a name and a list of collections.
    # Collection has a name, a value, and a target size.
    dClientParams =   { "MIT":[ ["Mags",1,10], ["Books",2,5] ]
                        , "Harvard":[ ["Cheap",1,20], ["Rare",3,10] ]
                        }
    # Library has a name, a quality rating, and a shelf size.
    dLibraryParams =  { "Barker":[1,2000]
                        , "Dewey":[1,3000]
                        , "Widener":[2,4000]
                        , "Houghton":[3,2000]
                        }
    # Shelf has an MTTF for each quality level.
    # quality : [ sector error rate, shelf error rate ] 
    dShelfParams =    { 1 : [ 10, 100 ]
                        , 2 : [ 20, 200 ]
                        }

# END
