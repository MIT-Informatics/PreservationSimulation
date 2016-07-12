% How Many Copies Is Enough?
% Micah Altman; Richard Landau
% 2016-07-11

# How Many Copies Is Enough?   {#title .unnumbered}

**Assessing Long-term Durability of Collections Through A Flexible, Replicable Simulation**


>**Abstract**

>* How to protect a large, valuable, digital document collection
* How many copies do you need to keep it safe?
* Where to put the copies?
* Are you sure they're still there? 
* Whether to use compression, encryption, ... ?
* Not much hard data on which to base policy decisions
* We developed a flexible, replicable simulation framework
* We aim to provide some guidance, based on some common, but not universal, calibration points.


# Motivation

# Fifty-Thousand Foot View

## Problem Definition
- Maintain large digital collections over time
- Risks to collections 

![Various Threats to Library Collections (in the square brackets)](threats.jpg "Various Threat Types (in quotes after the link addr)")

<!-- -->
    1.	Document rot on disk.
    2.	Environmental failures that accelerate document rot.
    3.	Server failures that destroy sets of documents.
    4.	Lack of independence of servers.
    5.	Attack on collection, institution, subject matter.
    6.	Et alia.

## Core Assumptions
- Documents usually fail individually, but sometimes in large batches.
- Document failures occur randomly, independently, at predictable rates.
- But the rates are not constant across storage servers.
- Nor are the rates constant through time.

## Core Motivating Problem
- Number of choices: formatting, auditing, quality, number of copies ...
- Keeping risk of object loss fixed -- what choices minimize $?
- "Dual problem" --  Keeping $ fixed,  what choices minimize risk?

## Basic Model Framework
- One client, one collection, many documents.
- Client asks some number of external servers to store a copy of the collection of documents.
- Documents may fail on the servers.  The client does not see the document failure until it tries to access the document.  
- Client may audit the external servers to test the validity of each copy of each document.  If a document is found to have failed, the client refreshes the copy on the server (provided that an intact copy remains on any other server).  
- At the end of some time period, assess how many documents have been permanently lost.  

## Illustration
 
# Simple Case -- Independent Failures
How many copies do you need if ...

## Just make copies -- no auditing? TOO MANY
- Long term -- bit rot
    o	Show results from long term simulation 
    o	[TABLE] (how long for 1% loss, based on number of copies) 
    o	Interaction  -- fragility of big documents 
    o	[FIGURE] (how long for 1% loss, based on increasing size)
    o	Cite to Rosenthal previous results on this
- Medium term -- if storage error rates are uncertain
    o	Storage error rates are difficult to verify
    o	[FIGURE] How long for failure of 1% as error rate increases?
    o	How to interpret claimed storage error rates
        - What are the limitations of how MTBF is measured? 
        - Given an MTBF, what is the possible bounded range of half-lives?

## Auditing and independent failures?  FIVE
- Key conditions for this solution
- entirely independent
- (no correlated failures, no intelligent adversaries, no institutional failures) 
- Robust to storage quality
- [FIGURE]
- Auditing is systematic 
    1.	(compare to random, usage base)
    2.	Random auditing, with replacement, is less effective.  
    3.	Systematic auditing, periodically and without replacement, is most effective.
        a.	Auditing and egress charges -- piecemeal is ok
        b.	Auditing charges would be reduced by cryptographic affordances on cloud-server side ...
    4.	Robust to audit frequency
        a. The impact of the rate of auditing is surprisingly less influential than the auditing strategy.  Auditing more frequently than annually has little impact on losses, across a wide spectrum of error rates.
        b. Systematic auditing in a small number of segments, e.g., auditing one quarter of the collection every calendar quarter, is slightly more effective than one large, annual audit, and eases bandwidth requirements.   
- [FIGURE]

# How many more copies ... ? Associated Failures

## Type of Threats

- Server-side Billing Failure  
- Server-side Financial Failure  
- Unsophisticated adversary outsider attacker  
- HVAC Failure/anticipated environmental problem  
- Unanticipated Environmental Catastrophe (including local war)  
- Local software failure  
- Admin failure  
- Hardware batch quality  
- Formal Government Action  
- Powerful External Adversary  
- Economic Recession  
- Limited Internal Adversary  
- Curatorial Failure/Client error  
- Common software failure  

## Modeling Associated Failures
Sources of failures are modeled as a stochastic processes, in a hierarchical  model


|  |	Logical Block |	Server (Provider) Glitch |	Global Shock |
|-----|--------------|--------------|--------------|
| Represents	| failure of logical block within physically raided storage |	event affecting reliability of single provider |	event affecting reliability of multiple providers |
| Distribution |	Poisson IID |	Poisson IID	| Poisson IID |
| Duration	| Instantaneous and permanent	| Bounded Duration %GLITCH_MAX_LIFE%, Exponential Decay 	| instantaneous| 
|Effect |	loss of single block of single copy of document	| Increases logical block failure rate |	(Immediately) inject  glitch in k servers |
| Detection |	Loss is detected on audit	| Server error itself detected on audit iff. block error rate > %CLIENT_SENSITIVITY |	Invisible (detected only through effects on block failure and server glitch) |
| Notes	| Failure rate is not known precisely to client	| Induces additional block failures, correlations among block failures. 	| Induces server glitches, and correlations among server |

A number of sources are not modeled, but are assumed to be addressed through storage practices:

- Bathtub curve, accelerate start and end-of-life failures. The model is conditioned on good systems administration practice is in place, including equipment burn-in and scheduled replacement within the expected service life. Thus the error rate observed during the service life of the equipment should not be subject to these failure. 
- Raid configuration characteristics, internal raid errors.   Standard storage practice may include low-level physical redundancy. Thus the reliability of a logical block will be better than that of an underlying physical storage. When using the model, one should calibrate error rates based on the implied or observed failure rates of logical blocks -- each of which may be represented by redundant physical storage.
- Media format obsolence -- we assume good practice -- migration to new media bewfore end of life. 
- Unmanaged File Format obsolescence. 
    - Management can mitigate file format obsolescence where documents are stored in multiple formats (or multiple indepent readers)  and tested for format characteristics at audit. Failures occur at the level an entire document, but the threat of loss could be modeled as with a block error rate implying a certain document failure rate for fixed size documents, where the number of servers represents the number of independent formats stored. 
    - Unmanaged format obsolescence cannot be addressed through redundancy, etc. -- will not show on audits

What are are not modeling
- Sophisticated adversaries that attack the auditing mechanism
- Cascading failure/contagion
- Environmental glitch that directly affect background rate of server glitch
- Server characteristics are in a steady -state equlibrium -- characteristic of servers remain the same over time. 

A wide range of real-world threats may be modeled through varying the parameterization of the model

## Threat Matrix
A wide range of real-world threats may be modeled through varying the parameterization of the model

[table]
Model Level	Real World Threat Source	Used to predict ..	Use to derive ... 
Logical Block	- loss due to media failure
loss due to raid/internal replication characteristics and failure	Document loss rate as a function of 
{number of replicas, auditing strategy, auditing frequency, block error rate}	Document loss as a function of
- document size
- format fragility 
- file compression
- managed format obsolescence

Server	- Server-side Billing Failure
- Server-side Financial Failure
- Unsophisticated adversary outsider attacker
- HVAC Failure/anticipated environmental problem
- Unanticipated Environmental Catastrophe (including local war)
- Local software failure
- Admin failure
- Hardware batch quality	Document loss rate rate as a function of server error characteristics, given a fixed choice of {replicas, auditing, block error}	Increased redundancy needed to maintain fixed loss rate in presence of server errors, given recommended auditing and repair strategy
Global	- Formal Government Action
- Powerful External Adversary 
- Economic Recession
- Limited Internal Adversary
- Curatorial Failure/Client error
- Common software failure	Document loss rate rate as a function of global error characteristics, given a fixed choice of {replicas, auditing, block error}	Increased redundancy needed to maintain fixed loss rate in presence of global errors

Effects of encryption key escrow policies

Tradeoff between regional diversification and adding servers. 


Server Error Parameterizations

Type	frequency	Impact	lifetime	Notes
Server Billing	Medium	High ((> sensitivity rate)	Permanent loss  of content	Loss of entire collection on server
Financial	Low	High	Permanent -> simulation period	Bankruptcy
- loss of collection
Low Resource External Adversary	Low	Medium	Medium	Assume that adversary does not subvert audit
HVAC	high	small	medium	
Unanticipated Environmental Catastrophe	low	high 	short	
Local Software	medium	medium	long	
Administrator Error	medium	small	short	
Hardware batch quality	Medium 	Medium	Long
	

## How Many More for 
- Environmental
- Institutional Final Failure
- Recession

 
# Generalizations

## Overview

## Large vs Small documents

 
## Large vs Small collections

## Compression
- Documents are fragile
Compressed, encrypted: small failure makes document unreadable
Variation: Repairable documents
Small failure damages only one segment
Model this as a set of smaller docs
- 


## Encryption

Deriving encryption key loss: 

- Assume that your expected collection loss with N_S servers is L% , without encryption
- Assume N_K copies of keys with 
- Assume loss of all keys yields 100% loss of collection
- Assume availability and integrity of key is verified on audit

	For example:

Suppose there are only 2 copies of keys. Is the expected document rate due to encryption key loss is equivalent to the expected document loss in the following scenario?
- there are two servers 
- logical block failure is 0 
- audits are annual
- servers are subject to glitches of the *financial failure* form -- permanent, total loss
- What is L*= E(L|KL,N_K)
- Can this be derived from failure rate of N_S servers with a rate of KL financial failures
## Format Obsolescence

# Replication And Extension

## Value of replicability

## Calibration with real world data -- how to calibrate

## Extension and parameterization

# Recommendation

## For collection owner
- Use at least 5 copies
- Use systematic annual auditing
- Do not trust MTBF and other similar measures
- Use compression, with known algorithms
 
## For digital preservation commons
- Develop standards 
    1.	with cloud vendors for cryptographic auditing that does not require data egress
    2.	Reporting  of failure rates
- Sharing reliability of cloud vendors
- Sharing information on correlated failures?
## Recommendations for research
- Detailed cost models
- Strong adversaries
- Erasure codes...

# References

# Supplementary Materials -- Hideous Details

## Statistical Modeling Detail

## Simplifying assumptions and scaling
- One client
- Fixed number of docs
- Fixed length of simulation; metric years, quarters, months
- Identical servers
- Simple document failures: bad sector = dead
- Doc size, sector size, shelf size
- Scaling of doc size and error rate
    1.	Implications for compression
- Logarithmic scaling of error rates and number of copies for efficiency and easy comparisons
- Everything arrives Poisson, rates are exponential, rates stated as half-lives
    1.	Sector errors, server failures
    2.	Glitches that impact error rate on a server
    3.	Shocks that impact life expectancy of servers

## Simulation Runs
- Random number generation, fixed seeds
- Small-ish to medium repetitions with seed sequences for repeatability
- Statistics extracted: median, midmean, trimean

## Software Architecture Details
- Main program for a single run, produces detailed log file
- Broker program, and associated shell scripts, to schedule many runs across available compute cores
- Extraction program to pull important data from log files
- R scripts to summarize data into tables
- R scripts to produce graphs 
- All programs CLI-based, run on Linux (Ubuntu server and Cygwin on Windows)
- How-to documentation

## Instructions for Installation and Software Execution
- How to Install on Amazon Web Services

## How to Model Various Scenario
