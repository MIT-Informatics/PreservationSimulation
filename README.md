# PreservationSimulation Project

## Abstract

Libraries, academic and corporate, have large collections of documents that they wish to preserve for long periods.  A common strategy for preserving documents of any kind is to make multiple copies and distribute the copies geographically.  Increasingly, library collections come in digital form rather than dead-tree form, which makes them easier to copy and distribute.  But digital documents are relatively fragile: small errors in storage can corrupt or destroy a document.  To balance this risk, we record and distribute multiple copies of digital documents.  

A first question that needs to be answered is how many copies to keep.  For a variety of conditions -- document sizes and types, storage error rates, auditing strategies, etc. -- we need to know how many copies we should keep, how many copies we can afford to keep economically.  We can also deal with various strategies for "auditing" a collection, that is, checking on its status, verifying the validity of document copies, and repairing damaged copies if necessary.  

The purpose of this project is to provide baseline data for librarians and researchers about long-term survival rates of document collections.  We have developed computer simulations to estimate document failure rates over a wide variety of conditions.  The data from these simulations should be useful to stewards of such collections in planning and budgeting for storage and bandwidth needs to protect their collections.  

The simulations are necessarily schematic in that they don't attempt to model the details of real-life situations.  Instead, the simulations are targeted at specific points in a huge sample space, providing bases from which users can extrapolate to approximate their actual environments.  

        ". . . let us save what remains not by vaults and locks which fence them 
        from the public eye and use in consigning them to the waste of time, 
        but by such a multiplication of copies, as shall place them 
        beyond the reach of accident."  
        --Thomas Jefferson, Feb. 18, 1791

Results of this project was presented at the IDCC20 conference in February, 2020.  
A draft of the paper is available on arXiv.org at https://arxiv.org/abs/1912.07908 .  
The published paper is available at http://www.ijdc.net/article/view/727/598 or 
DOI: https://doi.org/10.2218/ijdc.v15i1.727 


## Contact Information

Micah Altman: escience@mit.edu, for topics related to digital curation.

Richard Landau: landau@ricksoft.com, for topics related to the contents of this repository.


## Overview of Process

The basic process of a simulation is as follows:

- A client (library) forms a collection of some number of documents.  

- The client decides on a level of redundancy for the collection and asks a number of servers to store and maintain a copy of the entire collection.  

- Documents age, and they may be damaged by storage errors in the servers.  (This simulation does not attempt to look at the error rates of individual disks.)

- The client may audit the collection copies on the several servers.  If the client finds that a document on a server has been damaged, the client will repair that copy by replacing it on the server with new data from another extant copy, if there is one.  

- If there is no other extant copy, then the document is considered to be permanently lost.

- It is also possible for one or more servers to fail due to economic, environmental, or political shocks.  In this case, all the document copies in a failed server are unavailable.  To maintain the desired level of redundancy, the client must acquire and provision a new server with a copy of the collection.  

- If no other server is available from which to provision a replacement server, then the entire collection is considered to be permanently lost. 

- At the end of the simulation time, the client looks at all copies of all documents on all servers and determines if any documents have been permanently lost, and how many.  

- All simulation runs were replicated at least twenty-one times with known random seeds.  Aggregate numbers given here are medians and midmeans of the several runs. 

- The simulations keep summary logs for analysis of document damage and repair, and server failure and replacement.  Detailed logs of individual document activity are also available if desired.  

## Study Questions

This study attempts to provide some baseline data that can be used to assess the risks of preserving digital document collections, and the efficacy of storing multiple copies on servers with known or assumed error rates.  These are the basic questions to be asked related to storage of multiple copies of documents under varying conditions.

1. Document loss rates with no auditing?  Store multiple copies on servers, and examine document losses after some period.  Examine various numbers of copies and a range of error rates.  

1. Loss rates with regularly scheduled auditing?  At regular intervals, examine the health of some or all documents on all servers.  If a document has been lost on one or more servers, effect repairs where possible.  Examine several intervals for auditing and various strategies for choosing the documents to be audited at each interval.  

1. Loss rates with increases in storage error rates?  At random intervals, errors of some magnitude and duration impact the error rate of a storage structure, possibly causing a higher loss rate on that server, or even a total loss on a server.  Examine ranges of frequencies, severities, and durations.  

1. Loss rates as servers age?  Servers, as enterprises that offer a storage service, are not immortal.  They die, merge, change business, and so forth.  When they cease to function or lose their independence, they need to be replaced.  Examine ranges of server failure rates, redundancies, and auditing strategies.  

1. Loss rates with correlated server failures?  At random intervals, major exogenous shocks increase the likelihood of total failure of one or more servers.  Examine ranges of frequency of shock and span of the impact of a shock, levels of redundancy, and auditing strategies.


## The Programs

All the code to run the simulations, and the results of simulations, are published on github at github.com/MIT-Informatics/PreservationSimulation and are accessible to the public under the MIT license.  The code consists of several parts.

- Python programs using Python v2.7 and v3.5 run the actual simulations and collect the result data.  The main program comprises twenty-four modules currently.  Six additional modules decode the instructions for a series of simulations and run computations in parallel to take advantage of multiple cores available in a computer.  The programs have been tested on 2-, 4-, 8-, and 32-core systems.  Additional modules are used to create databases of instructions to guide the simulations.  

- Bash scripts run many aspects of the processes.  All programs, the Python and the scripts, were developed using the Cygwin library on Windows 7 and 10.  Some programs and scripts have been tested also on various versions of Linux and on Mac OS/X.  

- An installation procedure (bash script) can install the simulation programs on an Ubuntu Linux server, intended primarily for use on Amazon's AWS EC2 web services.  This has been used to generate many of the results on large, multi-core machines.  Complete testing is still required for OS/X and other versions of Linux.  

- Bash scripts and Python programs extract data from large log files, using regex-based instruction files to guide the extractions.  

- Basic R scripts are used to organize the data into more easily accessible tables and graphs.  

------------------------- needs work from here on ----------------------

- Several programs and scripts create instruction sequences for the many cases to be examined.  There are two separate mechanisms to construct, extract, and execute instructions: one for simple cases only (up to and including total auditing); and one for all cases, including auditing and glitches and shocks of all kinds.  The complex mechanism uses a MongoDB database to store and query the instruction parameters.  

- A number of how-to documents describe, we hope, the detailed process to reproduce the simulations and results.  

- The SimPy library v3.0.7 or later is required for the main simulation program.  This library should be obtained from the Python Package Index (PyPI) at python.org, and thus is not included in the github repository for this project.  
The data results from the many simulation runs is also included in the github repository in a set of zip archives.  

- The Python code of the project may be translated to Python version 3 after the bulk of the simulations have been completed.  

- web ui using bottle web server, not pretty but functional


## Simulation Data Output

The output of a single simulation run is a long log file listing details of the run: parameters, storage assignments, errors, document losses, auditing cycles, and final results.  These log files range from a few hundred KB to many MB.  A program is used to extract the few critical data items from the log file, according to specific instructions given, and reduce that data to a single (long) line of data in CSV or blank-separated format.  

For a given question, the set of single-line summary results are collected into a single file, with a header line, that can then be read by any common statistical packages, such as R.  The repository includes sample R scripts to process the one-dimensional data into two-dimensional summary tables that are easier to understand.  


## Different Kinds of Document Failures

A copy of a document can be lost in several ways.  Note that all document failures are silent; that is, the client is not actively informed of the failure.  The client learns about the absence of a document, or of all the documents in a server, only when the client tries to retrieve a document from the server, presumably during an audit.  

1. A single copy of a document dies on a single server.  Maybe a cosmic ray hits a disk, maybe there's a bus corruption in the RAID controller, whatever.  The loss of a single copy will be found in auditing (if performed) and can be repaired if any other copies remain intact on other servers.  

1. A "glitch" of some sort impacts the storage at a server site.  This causes the error rate (for errors of the first type, above) to increase by some factor for some amount of time.  Such problems exist for a while and either fade away or are ameliorated.  Examples could be a problem in environmental controls such as temperature and humidity for a server farm; noisy electrical systems; seasonal dust, dirt, and pollens getting through air filters; and so forth.  
    
    Temporary increases in error rates are not distinguishable from overall increases in the error rate for the duration of an inter-audit interval.  The client cannot tell if the error rate was lumpy during the period or just slightly higher.  

1. An institution can fail and lose all the documents it contains, 

    - through natural catastrophe such as fire, flood, or earthquake; 
    - through man-made catastrophe such as war, attack, or vandalism; 
    - through financial failure such as bankruptcy or broken credit arrangements;
    - or simply through changes in an institution's goals and purpose.  

    In this case, the institutional failure loses all the documents in the collection, and the client must find and provision a new server to take its place.  The risk to the client is that, between the time the institution failed and the time the failure was discovered in the next audit, the actual number of copies of all documents was reduced, and thus the risk of permanent document loss is increased for that period.  

    If more than one institution were to fail during a short interval, say, due to regional problems, widespread severe economic downturn, or financial interconnection between two institutions, then the number of copies actually present would be further reduced and the risk of permanent loss further sharply increased.  
    
    We are particularly concerned about economic shocks that remove multiple copies of a collection.  Of special concern are corporate realignments (e.g., mergers, acquisitions) that reduce the independence of multiple servers that a client may be using, and thus make multiple servers vulnerable to economic shock.  


## Ten-Cent Tour of Conclusions

- Across a wide range of error rates, maintaining multiple copies of documents improves the survival rate of documents, much as expected.  

- For moderate storage error rates, in the range that one would expect from commercial products, small numbers of copies suffice to minimize or eliminate document losses.  

- Auditing document collections dramatically improves the survival rate of documents using substantially fewer copies (than are required without auditing).

- Auditing is expensive in bandwidth.  As an interested group, we should work on (cryptographic) methods of auditing that do not require retrieving the entire document from a server. 

- Auditing does not need to be performed very frequently.  

- Glitches increase document loss more or less in proportion to their frequency and impact.  They cannot readily be distinguished from overall increases in error rate.  

- Institutional failures are dangerous in that they remove entire collections and expose client collections to higher risks of permanent document loss.  

- Correlated failures of institutions could be particularly dangerous in this regard by removing more than one copy from the set of copies for long periods.  

- We need more information on plausible ranges of document error rates and on institutional failure rates.  

