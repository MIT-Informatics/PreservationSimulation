#!/usr/bin/python
# lifetime.py

from __future__ import division
from __future__ import absolute_import
from builtins import object
import  simpy
from    .NewTraceFac     import  NTRC, ntrace, ntracef
import  itertools
from    .globaldata      import  G
from    math            import  exp, log
from . import  util
from . import  logoutput       as lg
from    .catchex         import  catchex


#===========================================================
# C l a s s  L I F E T I M E 
#---------------------------

class CLifetime(object):

    @ntracef("LIFE")
    def __init__(self,mysShelfID, myfLifetime, mynGlitchFreq, mynGlitchImpact, mynGlitchHalflife, mynGlitchMaxlife, mynGlitchSpan):
        self.fOriginalLifetime = float(myfLifetime)
        self.fCurrentLifetime = float(self.fOriginalLifetime)
        self.sShelfID = mysShelfID
        
        # Store glitch params. 
        self.nGlitchFreq = mynGlitchFreq
        self.nImpactReductionPct = mynGlitchImpact
        self.nGlitchDecayHalflife = mynGlitchHalflife if mynGlitchHalflife > 0 else G.fInfinity
        self.nGlitchMaxlife = mynGlitchMaxlife if mynGlitchMaxlife > 0 else G.fInfinity
        self.nGlitchSpan = mynGlitchSpan if mynGlitchSpan > 1 else 1
        
        # Glitch currently running?
        self.bGlitchActive = False
        self.fGlitchBegin = 0           # Not yet.
        self.nGlitches = 0              # Count glitches on this shelf.
        self.fGlitchTime = 0            # Total time glitches active at some level.

        self.fLn2 = log(2.0)
        self.ID = "LIFE-" + self.sShelfID
        G.dID2Lifetime[self.ID] = self

        # If there are to be any glitches, start the timer. 
        if self.nGlitchFreq > 0:
            G.env.process(self.mScheduleGlitch())

# BTW, after using this property for a while, I find that I don't like
#  the appearance that it gives in the code.  Yes, it hides the translation, 
#  but it makes it appear that there is actually a static class property.  
#  Not sure I like the tradeoff.  
    @property
    def cShelf(self):
        return G.dID2Shelf[self.sShelfID]

# L i f e t i m e . m S c h e d u l e G l i t c h 
    @catchex
    @ntracef("LIFE")
    def mScheduleGlitch(self):
        '''Wait for a glitch lifetime on this shelf.
        If the shelf died as a result of the glitch, stop
        rescheduling.  
        '''
        fNow = G.env.now
        NTRC.ntracef(3,"LIFE","proc schedule glitch t|%d| shelf|%s| alive|%s|" %
            (fNow, self.sShelfID, self.cShelf.mbIsShelfAlive()))
        while 1:
            fNow = G.env.now
            bAlive = self.cShelf.mbIsShelfAlive()
            if bAlive:
                self.fShelfLife = self.mfCalcCurrentGlitchLifetime(fNow)
                if self.fShelfLife > 0 and bAlive:
                    self.fShelfInterval = util.makeexpo(self.fShelfLife)
                    lg.logInfo("LIFETIME","schedule  t|%6.0f| for shelf|%s| "
                        "interval|%.3f| freq|%d| life|%.3f|" % 
                        (fNow, self.sShelfID, self.fShelfInterval, 
                        self.nGlitchFreq, self.fShelfLife))
                    NTRC.ntracef(3,"LIFE","proc schedule glitch shelf|%s| "
                        "interval|%.3f| based on life|%.3f| alive|%s| "
                        "waiting..." % 
                        (self.sShelfID, self.fShelfInterval, 
                        self.fShelfLife, bAlive))
                    yield G.env.timeout(self.fShelfInterval)
                    
                    # ****** Glitch has now occurred. ******
                    # If correlated failure, step entirely outside the 
                    #  Lifetime-Shelf-Server context to signal several servers.
                    if self.nGlitchSpan > 1:
                        from .server import CServer
                        CServer.fnCorrFailHappensToAll(self.nGlitchSpan)
                    else:
                        self.mGlitchHappensNow()
                else:
                    NTRC.ntracef(3,"LIFE","proc glitch no freq or not alive, "
                        "set wait to infinity shelf|%s| freq|%d| life|%.3f| "
                        "interval|%.3f|" % 
                        (self.sShelfID, self.nGlitchFreq, self.fShelfLife, 
                        self.fShelfInterval))
                    yield G.env.timeout(G.fInfinity)
            else:
                break       # Because we have to use fako "while 1".
        # When shelf is not alive anymore, wait forever
        NTRC.ntracef(3,"LIFE","proc glitch shelf no longer alive, set wait "
            "to infinity shelf|%s| freq|%d| life|%.3f| interval|%.3f|" % 
            (self.sShelfID, self.nGlitchFreq, self.fShelfLife, 
            self.fShelfInterval))
        yield G.env.timeout(G.fInfinity)

# L i f e t i m e . m G l i t c h H a p p e n s N o w 
    @catchex
    @ntracef("LIFE")
    def mGlitchHappensNow(self):
        """Start a glitch happening right now.
        May be invoked from outside a CLifetime instance as well as 
        from inside."""
        fNow = G.env.now
        NTRC.ntracef(3,"LIFE","proc glitch wait expired t|%6.0f| "
            "for shelf|%s| freq|%d| life|%.3f| interval|%.3f|" % 
            (fNow, self.sShelfID, self.nGlitchFreq, self.fShelfLife, 
            self.fShelfInterval))
        self.mGlitchHappens(fNow)
        lg.logInfo("LIFETIME","glitchnow t|%6.0f| for shelf|%s| active|%s|" %
            (fNow, self.sShelfID, self.bGlitchActive))

# L i f e t i m e . m C o r r F a i l H a p p e n s T o M e 
    @catchex
    @ntracef("LIFE")
    def mCorrFailHappensToMe(self):
        self.mGlitchHappensNow()

# L i f e t i m e . m G l i t c h H a p p e n s 
    @catchex
    @ntracef("LIFE")
    def mGlitchHappens(self,myfNow):
        self.bGlitchActive = True
        self.nGlitches += 1
        G.nGlitchesTotal += 1
        lg.logInfo("LIFETIME","glitch    t|%6.0f|  on shelf|%s| num|%s| "
            "impactpct|%d| decayhalflife|%d| span|%d| maxlife|%d| gtotal|%s|" 
            % (myfNow, self.sShelfID,  self.nGlitches, 
            self.nImpactReductionPct, self.nGlitchDecayHalflife, 
            self.nGlitchSpan, self.nGlitchMaxlife, G.nGlitchesTotal))
        self.fGlitchBegin = float(G.env.now)
        NTRC.ntracef(3,"LIFE","proc happens1 t|%.3f| shelf|%s| num|%s| impact|%d| "
            "decayhalflife|%d| span|%d| maxlife|%d|" % (myfNow, 
            self.sShelfID, self.nGlitches, self.nImpactReductionPct, 
            self.nGlitchDecayHalflife, self.nGlitchSpan, self.nGlitchMaxlife))
        ''' If this is a 100% glitch:
            - Declare server, not just shelf, to be dead.
            - Auditor will eventually discover the problem and 
               call client to inform that server is dead.  
        '''
        sServerID = self.cShelf.sServerID
        if G.dID2Server[sServerID].bDead or self.nImpactReductionPct == 100:
            self.cShelf.bAlive = False
            #sServerID = self.cShelf.sServerID
            cServer = G.dID2Server[sServerID]
            NTRC.ntracef(3,"LIFE","proc happens2 glitch 100pct or server dead "
                "id|%s| shelf|%s| svr|%s|" % 
                (self.ID, self.cShelf.ID, sServerID))
            cServer.mServerDies()
            NTRC.ntracef(3,"LIFE","proc happens3 life|%s| killed server |%s|" % 
                (self.ID, sServerID))
            lg.logInfo("LIFETIME", "100pct glitch on shelf |%s| "
                "of server|%s| - all docs lost" % 
                (self.sShelfID, sServerID))
        else:
            self.mInjectError(self.nImpactReductionPct, 
                self.nGlitchDecayHalflife, self.nGlitchMaxlife)
        return (self.nGlitches, self.sShelfID)

# L i f e t i m e . m I n j e c t E r r o r 
    @catchex
    @ntracef("LIFE")
    def mInjectError(self, mynReduction, mynDecayHalflife, mynGlitchMaxlife):
        '''\
        When a glitch occurs, decrease lifetime by some amount, percentage.
        The decrease decays exponentially at some rate until negligible.  
        '''
        self.nReductionPercentage = mynReduction
        self.fDecayHalflife = float(mynDecayHalflife)
        self.fDecayRate = (self.fLn2 / self.fDecayHalflife)
        self.fMaxlife = float(mynGlitchMaxlife)
        NTRC.ntracef(3,"LIFE","proc inject reduct|%s| decayhalflife|%s| " 
            "decayrate|%s| maxlife|%s|" % (self.nReductionPercentage, 
            self.fDecayHalflife, self.fDecayRate, self.fMaxlife))
        return self.fDecayRate

# L i f e t i m e . m f C a l c C u r r e n t S e c t o r L i f e t i m e 
    @ntracef("LIFE")
    def mfCalcCurrentSectorLifetime(self,myfNow):
        '''
        if glitch in progress
          if glitch is too old
            turn it off
            log expired
            normal lifetime
          else 
            calc reduced lifetime
            if decay below ignore limit
              turn it off
              log below limit
        '''
        if self.bGlitchActive:
            fTimeDiff = myfNow - self.fGlitchBegin
            fDuration = (float(self.nGlitchMaxlife))
            # If the glitch lifetime has expired, turn it off.
            if fTimeDiff > fDuration:
                NTRC.ntracef(3,"LIFE","proc glitch lifetime expired "
                    "id|%s| num|%s| start|%.3f| now|%.3f| maxlife|%s|" % 
                    (self.ID, self.nGlitches, self.fGlitchBegin, myfNow, 
                    self.nGlitchMaxlife))
                lg.logInfo("LIFETIME","expired   t|%6.0f| shelf|%s| "
                    "id|%s| num|%s| start|%.3f| now|%.3f| maxlife|%s|" % 
                    (myfNow, self.sShelfID, self.ID, self.nGlitches, 
                    self.fGlitchBegin, myfNow, self.nGlitchMaxlife))
                self.bGlitchActive = False
                self.fGlitchTime += fTimeDiff
                self.fCurrentLifetime = self.fOriginalLifetime
            else:            
                # The glitch is still current.
                # Carefully calculate the new sector lifetime based on 
                #  some reduction due to glitch and the age of the glitch.
#                fTimeDiff = myfNow - self.fGlitchBegin
                fAgeInHalflives = (fTimeDiff / self.nGlitchDecayHalflife)
                fExponentialDecay = exp(- self.fLn2 * fAgeInHalflives )
                fReductionFraction= 1.0 * self.nReductionPercentage / 100.0
                self.fCurrentLifetime = (1.0 * self.fOriginalLifetime * 
                    (1.0 - fReductionFraction * fExponentialDecay))
                NTRC.ntracef(3,"LIFE","proc calcsectorlife num|%s| "
                    "started|%.3f| age|%.3f| decay|%.3f| reduct|%.3f| "
                    "currlife|%.3f|" % 
                    (self.nGlitches, self.fGlitchBegin, fAgeInHalflives, 
                    fExponentialDecay, fReductionFraction, 
                    self.fCurrentLifetime))
                # If the glitch has diminished to a low level, 
                #  turn it off.  
                if fExponentialDecay < G.fGlitchIgnoreLimit:
                    self.bGlitchActive = False
                    self.fGlitchTime += fTimeDiff
                    NTRC.ntracef(3,"LIFE","proc glitch turned off lifeid|%s| "
                        "num|%s| started|%.3f| age|%.3f| decay|%.3f|" % 
                        (self.ID, self.nGlitches, self.fGlitchBegin, 
                        fAgeInHalflives, fExponentialDecay))
        else:
            # No current glitch active.  Lifetime is as usual.  
            self.fCurrentLifetime = self.fOriginalLifetime
        return self.fCurrentLifetime

# L i f e t i m e . m f C a l c C u r r e n t G l i t c h L i f e t i m e 
    @catchex
    @ntracef("LIFE")
    def mfCalcCurrentGlitchLifetime(self,myfNow):
        """
        fDuration = (float(self.nGlitchMaxlife) 
            if self.nGlitchMaxlife > 0 else float(G.fInfinity))
        NTRC.ntracef(3,"LIFE","proc glitchlife num|%d| now|%.3f| "
            "begin|%.3f| duration|%.3f|" % 
            (self.nGlitches, myfNow, self.fGlitchBegin, fDuration))
        if (myfNow - self.fGlitchBegin) < fDuration:
            fLifetime = self.nGlitchFreq / self.fLn2
        else:
            fLifetime = 0
            if self.bGlitchActive:
                NTRC.ntracef(3,"LIFE","proc glitch lifetime expired id|%s| num|%s| start|%.3f| now|%.3f| maxlife|%s|" % (self.ID, self.nGlitches, self.fGlitchBegin, myfNow, self.nGlitchMaxlife))
                lg.logInfo("LIFETIME","expired   t|%6.0f| shelf|%s| id|%s| num|%s| start|%.3f| now|%.3f| maxlife|%s|" % (myfNow, self.sShelfID, self.ID, self.nGlitches, self.fGlitchBegin, myfNow, self.nGlitchMaxlife))
            self.bGlitchActive = False
        """
        fLifetime = float(self.nGlitchFreq) / self.fLn2
        return fLifetime

    '''
    How to calculate current sector lifetime?
    decay rates
    0.10 = 0.5 ^ 3.3 => decay to 5% in 3.3 half-life intervals
    0.05 = 0.5 ^ 4.3
    0.01 = 0.5 ^ 6.6
    0.5 = exp(-0.7) (Note: 0.7=0.693=ln(2), not sqrt(2)=0.707)
    halflife = ln(2) / rate    and v-v    rate = ln(2) / halflife
    halflife = ln(2) * exponentiallifetime
    exponentiallifetime = halflife / ln(2)
    lifetime = 1 / rate    and v-v    rate = 1 / lifetime
    E.g., half-life of 1000 causes arrivals at 1443 intervals; 
    HL 2500 causes arrivals at 3540 intervals.  So
    HL 693 should cause arrivals at 1000 intervals.  Verified.  
    
    decaylevel = exp(-ln(2) * (timediff / glitchhalflife))
    losspct = impactpct * decaylevel
    remainpart = (1 - losspct/100)
    currlife = origlife * remainpart
    i.e., 
    currlife = origlife * (1 - ((impactpct/100) * (exp(-ln(2) * time))))
    currlife = origlife * (1 - (impactfraction * decaylevel))
    
    old invocation:
        fLifeParam = util.fnfCalcBlockLifetime(self.nSectorLife*1000, self.nCapacity)
        fSectorLife = util.makeexpo(fLifeParam)
    '''

# L i f e t i m e . m R e p o r t G l i t c h S t a t s 
    @catchex
    @ntracef("LIFE")
    def mReportGlitchStats(self):
        dd = dict()
        dd["sShelfID"] = self.sShelfID
        dd["sLifetimeID"] = self.ID
        dd["nGlitchFreq"] = self.nGlitchFreq
        dd["nImpactReductionPct"] = self.nImpactReductionPct
        dd["nGlitchDecayHalflife"] = self.nGlitchDecayHalflife
        dd["nGlitchMaxlife"] = self.nGlitchMaxlife
        dd["nGlitchSpan"] = self.nGlitchSpan
        dd["nGlitches"] = self.nGlitches
        dd["fGlitchTime"] = self.fGlitchTime
        return dd
 
@catchex   
@ntracef("LIFE")
def fnlGetGlitchParams(mysShelfID):
    '''\
    Do this through a function in case some calculation is 
     necessary someday, e.g., if shelves differ.  
    '''
    freq = G.nGlitchFreq
    impact = G.nGlitchImpact
    halflife = G.nGlitchDecay
    maxlife = G.nGlitchMaxlife
    span = G.nGlitchSpan
    return [freq, impact, halflife, maxlife, span]


''' TODO
- correlated failures: much trickier calculation of error rate
   depending on number of failures, time of last failure, 
   exponential decay of increased rate since failure, etc.
   I think something this complex belongs here, not in util.py.  
'''

# Edit history:
# 20150812  RBL Move CLifetime from server.py to its own file.  
# 20160216  RBL Add span to glitch stats.
# 20160219  RBL Add possibility of correlated failures when glitch occurs.
#                Because this is initiated from a shelf on a single server 
#                but affects multiple servers, this code is a bit of a swamp 
#                to avoid recursion.  
# 20160224  RBL Correct calling sequence and invocation of mInjectError.
# 20170420  RBL Fix fatal typo in trace.
#               Change log wording slightly to indicate glitch active.
# 20180516  RBL Update to use ntrace, ntracef, NTRC.
# 20180531  RBL Update to use only NTRC, ntrace, ntracef.
#               Remove use of old_div.
# 
# 

#END

