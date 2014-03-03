#!/usr/bin/python

''' shelf5.py
Blank page version of bookshelf preservation of documents.
Vague beginning of document preservation simulation.  

The plan: 

Library
    collection of shelves
    find a shelf for document
        if out of space, create a shelf
    aging process for institutional failure

Shelf
    capacity
    free space
    reliability class
    birthdate
    list of documents
    aging process for small errors that damage a document
        pick a victim document to be damaged
    aging process for disk failure that can be rebuilt
    aging process for array failure that kills all documents

Document
    size
    value class
        determines shelf policy
        determines audit policy
    log of actions
    audit process

Collection
    create set of documents
    value class
    storage policy
    audit policy
    budget
    list of libraries used

Client
    create set of collections
        different value classes
        distribution of document sizes

start logs
create libraries
create client
run

Recent changes in terminology:
- A Library has a number of Sites where documents may be stored.  A Library may become unavailable due to failure of the institution, e.g., budget cut to zero.  
- A Site is a physical location.  A Site may become unavailable due to a physical catastrophe, such as fire, flood, earthquake, a plane falling on it, war, terrorism, etc.  Sites NYI.  
- A Site contains a number of Shelves on which documents are stored.  
- Shelves vary in their reliability characteristics; some are more reliable than others, and therefore more expensive to maintain and occupy.  (A Shelf is probably roughly equivalent to a RAID storage system including all its servers, controllers, and disks.  I prefer not to use a storage term such as "array" because of the implication of underlying technology.  "Shelf" is a fairly neutral term for a place where you put books to store them.)  
- A Shelf may contain a number of redundant components to enhance its reliability.  Generally, failure of a redundant component is handled internally by the Shelf and not reported to the outside, though internal repair of a redundant component may place the Shelf at a higher risk of total failure for a limited time.  A Shelf may become unavailable due to failure of a non-redundant component or simultaneous failure of a fatal number of redundant components.  
- A Shelf stores a set of documents.  
- A Document is a blob of data.  It has a size, a value, and a sensitivity to corruption.  Some documents are more sensitive to small corruptions than others, e.g., highly compressed or encrypted documents may become unavailable due to errors in small regions of data.  
- A Document may be encrypted or licensed, and therefore may become unavailable due to the loss of the encryption key or license key, generally a much smaller piece of data that may be stored elsewhere.  

Aging processes and their consequences:
- Shelf: small hidden failure.  Affects part(s) of one or more documents depending on error size and doc size.  Rate: cover range from manufacturers' MTBF dodwn one order of magnitude.  
- Shelf: device failure.  Does not impact documents, but renders the shelf vulnerable to total failure if another happens before it is repaired.  Rate: cover range from manufacturers' device MTBF numbers down an order of magnitude. 
- Shelf: total failure.  The entire shelf of documents is lost.  Rate: range based on server and controller MTBFs.  
- Site: temporary outage, e.g., due to power failure, major commnication outage, or similar transient condition.  Makes all Shelves in the site unavailable for some time.  Rate: range based on power and weather incident history.  
- Site: total permanent failure, due to physical loss.  Makes all Shelves in the site unavailable permanently.  
- Library: total permanent loss.  Makes all sites unavailable permanently.  

Implemented in the short term:
- One or more clients.  A client has one or more collections.
- A collection has a name, a value, and a target size.  The actual size is a random close to the target size.  Some number of documents get created, all with the stated value, and placed in the collection.  
- One or more libraries.  A library has a quality rating and a shelf size.  The quality rating determines the value of documents that get placed in it.  The shelf size is a storage unit that can fail completely at some rate.  
- Currently libraries have no size limit.
- The several libraries can represent either (a) one institution with a number of sites with different quality (failure) characteristics, or (b) a number of institutions with one site each.  The choice of interpretations depends on whether one is modelling media quality risks, geographic risks, or institutional risks.  
- Several quality levels, which specify the MTTF of a sector and the MTTF of an entire shelf.  (Later this will include values for altering the failure rates of nearby sectors and shelves.)  
- Distribution policy?  Nothing fancy yet.  A client will send distributions only to libraries (sites) with adequate quality ratings.  Currently a collection is sent to one site.
- Most early experiments will probably be done with one client, one collection, stored at one site with one quality rating.
- Storing a collection in multiple locations, repairing, and auditing come later.

'''

import simpy
import random
from NewTraceFac07 import TRC,trace,tracef
from sys import argv
from globaldata import *
from client import *
from server import *
import readin


# M A I N   L I N E
#------------------

def main():

    TRC.tracef(0,"MAIN","proc Call center simulation " % ())

    # Read parameter files for simulation.
    P.dClientParams =   readin.fdGetClientParams("clients.csv")
    P.dLibraryParams =  readin.fdGetLibraryParams("libraries.csv")
    P.dShelfParams =    readin.fdGetQualityParams("quality.csv")
    P.dParamsParams =   readin.fdGetParamsParams("params.csv")

    # Allow CLI arguments to override some params.
    G.runtime = int(P.dParamsParams["SIMLENGTH"][0][0]) if len(argv) <=1 else int(argv[1])
    G.randomseed = int(P.dParamsParams["RANDOMSEED"][0][0]) if len(argv) <=2 else int(argv[2])

    random.seed(G.randomseed)
    env = simpy.Environment()
    G.env = env

    # Populate libraries, clients, collections of documents.
    makeLibraries(P.dLibraryParams)
    makeClients(P.dClientParams)

    # Run the simulation. 
    TRC.tracef(0,"MAIN","proc Begin run time|%d|" % (env.now))
    env.run(until=G.runtime)

    TRC.tracef(0,"MAIN","proc End simulation time|%d| hidoc|%s| hicoll|%s| hishelf|%s|" % (env.now,G.nDocLastID,G.nCollLastID,G.nShelfLastID))


if __name__ == "__main__":
    main()

# END
