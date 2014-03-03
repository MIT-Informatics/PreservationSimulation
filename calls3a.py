#!/usr/bin/python

''' calls3.py
    Blank page version of call center simulation
    Customers call, maybe get a phone line, then get put on hold, 
    then get service, then leave.
    Customer might get bored and leave while on hold, before service.  
    Create customers at random times.
    Exponentials used for all the random intervals.
'''

import simpy
import random
from NewTraceFac07 import TRC,trace,tracef
from sys import argv

class Customer(object):
    ''' Prime mover in this little play.
        Customer gets a phone line or busy signal 
        If no server available, customer gets put on hold
        Customer gets server
        Service lasts some time
        Customer exits
    '''
    @tracef("CUST")
    def __init__(self, env, ncustnum):
        self.env = env
        self.ncustnum = ncustnum
        env.process(self.run(env))

    @tracef("CUST")
    def run(self, env):
        tarrive = env.now
        (nwait,nserve) = self.getcustparams()
        TRC.tracef(3,"CUST","proc t=%04d Customer %3d arrives patience %d service %d" % (self.env.now, self.ncustnum,nwait,nserve))
        with G.rsPhonelines.request() as reqPhone:

            # If there is a phone line available, seize it.  Otherwise, 
            #  it's a busy signal; don't wait.  
            gotphone = yield reqPhone | env.timeout(0)
            if reqPhone in gotphone:

                # Phone answered.  Now get a server.
                nphonewait = env.now - tarrive
                tstarthold = env.now

                # Allocate a server.
                with G.rsServers.request() as reqServer:

                    # Wait for a server, or for patience to expire.
                    gotserver = yield env.any_of([reqServer,env.timeout(nwait)])
                    if reqServer in gotserver:

                        # Connected to server.  Record the hold time.  
                        nholdwait = env.now - tstarthold
                        if nholdwait > 0: 
                            G.nHeld += 1
                            G.nTotalHoldTime += nholdwait
                        TRC.tracef(3,"CUST","proc t=%04d Customer %3d startedhold %04d held %d startservice %d"%(env.now,self.ncustnum,tstarthold,nholdwait,nserve))
                        # Get served, and record the time served.
                        yield env.timeout(nserve)
                        G.nTotalServiceTime += nserve

                    else:
                        # Not connected to server, patience timed out; leave.
                        G.nHangups += 1
                        wastedtime = env.now - tstarthold
                        G.nWastedTime += wastedtime
                        TRC.tracef(3,"CUST","proc t=%04d Customer %3d hangs up startedhold %04d patiencelost %d" % (env.now,self.ncustnum,tstarthold,nwait))

            else:
                # No phone line available, busy signal.  Bail.  
                G.nBusySignals += 1
                TRC.tracef(3,"CUST","proc t=%04d Customer %3d rejects busy signal" % (env.now,self.ncustnum))
            TRC.tracef(3,"CUST","proc t=%04d Customer %3d leaves" % (self.env.now, self.ncustnum))

    # Characterize customer's experience parameters
    def getcustparams(self):
        nwait = nserve = makeexpo(G.p_patiencetime)
        nserve = makeexpo(G.p_servicetime)
        return (nwait,nserve)

''' Notes on things learned:
    
    Is there a test-and-set version of request()?
    Nope, but one can wait for    
        "yield any_of( event, timeout(0) )"
    and check the results to see which one triggered.  

    Note that if the number of phone lines is the same
    as the number of servers, then there is never any 
    hold time.  Always have more phones than servers.  

    Idiom for seizing a resource: 
        with someresource.request() as tempreq:
            yield tempreq
    The request() call merely creates a Request object instance, 
    and then you have to wait for that instance to be freed.  Duh.  

    Syntax for waiting for multiple events:
    any_of() and all_of() take a list of events, combined into one arg!
    | for any and & for all are apparently also acceptable syntax.
'''

def makeexpo(mean):
    ''' fn makeexpo(mean)
        return integer from exponential distribution with mean
    '''
    interval = int(random.expovariate(1.0/abs(mean)))
    return interval

@tracef("MAKE")
def makecustomers(env):
    ''' fn makecustomers(environment)
        Every so often, create a new caller.  Poisson arrivals.
    '''
    icust = 0
    while True:
        ntime = makeexpo(G.p_createtime)
        yield env.timeout(ntime)
        icust += 1
        G.nCallers = icust
        TRC.tracef(3,"MAKE","proc t=%04d Customer %3d to be created" % (env.now, icust))
        foo = Customer(env,icust)

# Global data items
class G(object):
    ''' class G for global data
    '''
    nCallers = 0        # How many callers
    nBusySignals = 0    # Callers that got a busy signal
    nHangups = 0        # Callers who impatiently hung up on hold
    nWastedTime = 0     # Total time impatient callers wasted waiting
    nHeld = 0           # Callers who held for nonzero time
    nTotalHoldTime = 0  # Total hold time for all callers
    nTotalServiceTime = 0   # Time callers spent getting actual service
    nRandomSeed = 1     # Fixed seed for randoms, for reproducibility
    env = None          # Simulation environment not allocated yet

def initparameters(env):
    # Default constants
    RANDCREATETIME = 10
    NPHONELINES = 2
    NSERVERS = 1
    RANDSERVICETIME = 10
    RANDPATIENCETIME = 10
    SIMLENGTH = 100
    RANDOMSEED = 1

    # Usage: calls2.py [runtime [nphones [nservers [createtime [servicetime [patiencetime [randomseed]]]]]]]
    # Pick up (positional, sorry) command line arguments if any as params
    G.p_runtime = SIMLENGTH if len(argv) <=1 else int(argv[1])
    G.p_nphones = NPHONELINES if len(argv) <= 2 else int(argv[2])
    G.p_nservers = NSERVERS if len(argv) <= 3 else int(argv[3])
    G.p_createtime = RANDCREATETIME if len(argv) <= 4 else int(argv[4])
    G.p_servicetime = RANDSERVICETIME if len(argv) <= 5 else int(argv[5])
    G.p_patiencetime = RANDPATIENCETIME if len(argv) <= 6 else int(argv[6])
    G.p_randomseed = RANDOMSEED if len(argv) <= 7 else int(argv[7])

    # We use a fixed value of randomseed to guarantee reproducibility 
    #  of results across trials.  If we do not set the seed value, then
    #  the library uses the system clock value to encourage really random
    #  random numbers.  
    # If the randomseed command line argument is explicitly zero, 
    #  then we will allow the system to use the current system time
    #  as the seed.  
    if G.p_randomseed != 0:
        random.seed(G.p_randomseed)

def initresources(env):
    # Allocate resrouces for phone lines and servers
    G.rsPhonelines = simpy.Resource(env, capacity=G.p_nphones)
    G.rsServers = simpy.Resource(env, capacity=G.p_nservers)

if __name__ == "__main__":
    # Initialize stuff.
    # Create simulation environment
    env = simpy.Environment()
    G.env = env
    initparameters(env)
    initresources(env)

    # Report simulation parameters
    TRC.tracef(0,"MAIN","proc Call center simulation lines|%d| servers|%d| arrival|%d| service|%d| patience|%d| seed|%d|" % (G.p_nphones,G.p_nservers,G.p_createtime,G.p_servicetime,G.p_patiencetime,G.p_randomseed))

    # Start the process to create customers
    env.process(makecustomers(env))
    # Run the simulation for a while
    env.run(until=G.p_runtime)

    # Report results    
    TRC.tracef(0,"MAIN","proc End simulation time|%d| callers|%d| busy|%d| hangups|%d| wastedtime|%d| held|%d| totalholdtime|%d| totalservicetime|%d|" % (env.now,G.nCallers,G.nBusySignals,G.nHangups,G.nWastedTime,G.nHeld,G.nTotalHoldTime,G.nTotalServiceTime))

#END
