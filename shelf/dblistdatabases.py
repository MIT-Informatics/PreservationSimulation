#!/usr/bin/python
'''
dblistdatabases.py

List all the databases Mongo holds on this system.  

@author: rblandau
'''
from NewTraceFac    import NTRC,ntrace,ntracef
import pymongo

NTRC.ntrace(0,"Begin.")
# Use naked Mongo functions not suitable for searchdatabasemongo library. 
# Since MongoDB is a system-wide singleton resource, there is no need 
#  to get any name arguments for this command.   
client = pymongo.MongoClient()
for sName in client.database_names():
    print sName
NTRC.ntrace(0,"End.")

#END
