# Short outline for short article
#### RBLandau 20170914

---

## Executive Summary: 

- (assertion) Digital document collections cannot be safeguarded simply by making a few copies; too many copies are required.  The curator needs to audit the integrity of the several copies at intervals.  

- (technique) If a copy of a document is corrupted or lost, it can be repaired from other extant copies.  A document is permanently lost only when all of its copies have been damaged or lost.  

- (assertion) It is important that the several copies of documents be stored independently, so that no single incident -- natural disaster, regional conflict, local terrorist attack, government censorship, local economic downturn, business failure, business realignment, etc. -- is likely to affect multiple copies.  

- (scope assertion) This paper does not deal explicitly with threats posed by inimical or incompetent human agencies.  Deliberate hacking and poor management practices are beyond our current scope.  

- (motivation) The quality of digital storage media is highly variable, particularly over long periods of time.  Stored data may deteriorate slowly, in small pieces such as disk sectors, or may fail in large blocks, such as disks, disk arrays, or entire storage services.  Redundant storage techniques such as RAID protect against only some such failures.  

- (assertion) A curator cannot always assess the reliability of storage of a particular type or location.  A strategy to preserve digital documents must be robust over a wide range of reliability and physical conditions.  

- (assertion) This paper presents simulation results that suggest that a reasonably small number of copies, audited and repaired regularly, suffice to preserve digital document collections over a very wide range of error conditions.  

- (assertion) Document auditing methods must examine every document at some interval.  Methods that examine only random subsets of documents sampled with replacement leave some documents unaudited and vulnerable to loss.  

- (assertion) Moderately frequent auditing of documents, e.g., annual auditing, suffices to preserve document integrity.  

- (assertion) Document size, type, and fragility due to, e.g., encoding, compression, or encryption, need not be significant factors in the choice of storage methodology.  

- (assertion) It is possible to divide collections into subsets by, e.g., value, and choose different storage strategies for the subsets.  High value documents may be stored more widely and audited more frequently than low value documents.  

- (conclusion) To preserve collections of digital documents, store a modest number of copies on independent storage services and audit their contents at regular intervals.  This strategy can protect collections over long periods and against a wide variety of storage quality levels, short term quality variations, and large scale failures.  

---

## Outline

### The Problem

- Most digital data is stored on disks.  Disks fail, a little at a time or all at once.  Disk storage services can also fail, slightly or totally.  
- Large collections of digital documents need to be preserved perfectly, or almost perfectly, for long periods of time.  
- There is little empirical guidance available to help curators plan how to preserve their collections.

### The Approach

- Library clients make several copies of all documents in the collection.  
- Copies may be stored on commercial (cloud) storage services or private datacenters.  
- Clients audit documents on a regular schedule.  This may involve retrieving the full content of document copies, orother convincing fixity information,  from the servers.
- Auditing will be done in repeated cycles.  Each cycle may contain all documents, or several systematically chosen subsets, or several random subsets sampled with or without replacement.  
- Auditing in several segments per cycle can even out the bandwidth requirements for retrieving documents.  
- Any documents found to be corrupted or missing during an auditing cycle will be repaired by replacing the copy from other extant copies.  


### The Simulations

- The discrete event simulations operate on a collection of fixed size.  The duration of the simulation is also fixed.  
- Clients place document copies on multiple servers.  For any single simulation, all servers have the same statistical characteristics: sector lifetime, server lifetime, glitch rates, shock rates.  
- Documents suffer sector errors that occur at random times and locations.  These errors corrupt the document content.  The rate of arrival of errors is constant during the simulation.  The rate may be varied over a wide range to represent a variety of physical disks and operating conditions.  
- Servers may suffer "glitches" that increase the local sector error rate for a while in a single server.  Glitches are intended to represent temporary operational problems such as HVAC failures, noisy AC power and such.  Glitches arrive randomly at a tunable rate.  
- Servers may also suffer from "shocks" that reduce their expected lifetime.  Shocks are intended to represent economic downturns, floods, wars and such.  Shocks arrive randomly at a tunable rate.  
- Random events in the simulations all independent and identically distributed Poisson arrivals.  The arrival rates are all expressed in terms of half-lives rather than mean exponential lifetime or bit error rate.  

### Simulation Parameters

- doc size can vary but scales linearly, predictably
- storage shelf size can vary but scales linearly, predictably
- range of independent copies
- wide range of error rates, to account for disk technology, manufacturing, and batch variations; reliable, or even plausible, numbers are very difficult to obtain from industry
- variety of auditing strategies: frequency, segmentation, sampling without or with replacement
- minor glitches for short term physical problems that increase bit error rates on disks, e.g., HVAC: frequency, impact level, duration
- shocks for large scale problems that affect entire services: frequency, impact level, duration.

### Variations to Test for Robustness

- vary number of copies allocated to independent storage services
- vary error rates for small disk errors
- vary auditing strategy
- vary glitches, frequent or rare, minor or major, short or long, affecting the document error rates on single servers
- vary shocks, frequent or rare, minor or major, short or long, affecting the survival of one or more servers at a time
- vary doc size and error rate together: larger docs should predictably represent bigger targets for random errors
- simulations performed with modest sample sizes; occasionally subsampled with much larger sample sizes for validation
- simulations performed with repeatable seeds for pseudorandom number generator

### Results

- auditing essential to limit copies
- auditing should be regular and complete
- baseline auditing: five copies, annual, total (all copies each cycle), may be segmented
- excessive auditing is overkill
- moderate glitches are similar to increased error rate
- baseline auditing can protect even against moderate shocks

### Future Work

- Develop standards for 

### Software Available Soon (RSN)





