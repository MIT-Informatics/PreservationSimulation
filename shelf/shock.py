#!/usr/bin/python
# shock.py
#
# Timing routines for economic or environmental shocks to servers.  

from    NewTraceFac     import  NTRC,ntracef,ntrace
import  simpy
import  resettabletimer
from    globaldata      import  G
import  util
import  logoutput       as lg
from    catchex         import  catchex
import  server


#===========================================================
# C l a s s  C S h o c k 
#---------------------

class CShock(object):
    ''' 
    Class intended to be instantiated once only.  
    Schedules (sequence of) shocks at random intervals based on its half-life, 
     if any.  When a shock occurs, reduce the expected lifetime of some subset
     of servers by some fraction.  A shock usually has finite lifetime itself; 
     at its end, it restores full life to all the servers that had their lives 
     shortened by the shock.  If a server's shortened life has expired during
     the shock, well, that's life; gonzo.  
    '''

    @catchex
    @ntracef("SHOK")
    def __init__(self, mynShockHalflife, mynShockSpan, mynShockImpact, 
            mynShockMaxlife):
        self.nLife = mynShockHalflife
        self.nSpan = mynShockSpan
        self.nImpact = mynShockImpact
        self.nMaxlife = mynShockMaxlife
        self.ID = "Z99"
        self.lsServersShocked = []
        
        # If there is to be any shockin' 'round here, start it.  
        #  Otherwise, nothing.
        if self.nLife:
            G.env.process(self.mWaitForShockToHappen(self.nLife))


# m W a i t F o r S h o c k T o H a p p e n 
    @catchex
    @ntracef("SHOK")
    def mWaitForShockToHappen(self, mynHalflife):
        ''' 
        Generator that waits for shock event.  
        
        Infinite loop:
        - Schedule shock event
        - Execute shock event
        - Schedule end of shock (maybe infinite)
        - Execute end of shock
        '''
        while True:
            # Schocks happen every so often, not just once.  
            fNewLife = util.makeshocklife(mynHalflife)
            lg.logInfo("SHOCK ", "t|%6.0f| waiting for shock in|%.0f| "
                "from hl|%s| at|%.0f|" 
                % (G.env.now, fNewLife, mynHalflife, (G.env.now+fNewLife)))
            # Suspend action until shock happens.
            yield G.env.timeout(fNewLife)
            # Shock has happened.
            lg.logInfo("SHOCK ", "t|%6.0f| shock happens now, maxlife|%s|" 
                % (G.env.now, self.nMaxlife))
            self.mShockHappens()
            # If maxlife nonzero, then wait and expire shock;
            #  else, never expires, so wait forever and don't 
            #  start another shock cycle.
            if self.nMaxlife > 0:
                lg.logInfo("SHOCK ", "t|%6.0f| waiting for shock to expire "
                    "in|%.0f| at|%.0f|" 
                    % (G.env.now, self.nMaxlife, (G.env.now+self.nMaxlife)))
                yield G.env.timeout(self.nMaxlife)
                self.mShockExpires()
            else:
                yield G.env.timeout(G.fInfinity)


# m S h o c k H a p p e n s 
    @catchex
    @ntracef("SHOK")
    def mShockHappens(self):
        ''' 
        Shock has happened.  Shorten server lives and schedule the 
        end of the shock cycle.
        '''
        G.nShocksTotal += 1
        lg.logInfo("SHOCK ", "t|%6.0f| start to reduce life of |%s| servers "
            "by pct|%s|" 
            % (G.env.now, self.nSpan, self.nImpact))
        self.mReduceSomeServerLifetimes(self.nSpan, self.nImpact)
        return G.env.now


# m R e d u c e S o m e S e r v e r L i f e t i m e s 
    @catchex
    @ntracef("SHOK")
    def mReduceSomeServerLifetimes(self, mynSpan, mynImpact):
        ''' 
        Find a shockspan-wide subset of servers and reduce their
        expected lifetimes by the stated reduction percentage.
        '''
        lServersToShock = server.CServer.fnlSelectServerVictims(mynSpan)
        fReduction = mynImpact * 1.0 / 100.0 
        NTRC.ntracef(3, "SHOK", "proc reduce servers|%s| by|%s|" 
            % (lServersToShock, fReduction))
        for sServerID in lServersToShock:
            lg.logInfo("SHOCK ", "t|%6.0f| reduce svr|%s| life by pct|%s|" 
                % (G.env.now, sServerID, self.nImpact))
            cServer = G.dID2Server[sServerID]
            fOriginalLife = float(cServer.mfGetMyOriginalLife())
            if fOriginalLife > 0:
                self.mReduceSingleServerLifetime(sServerID, fReduction)
                self.lsServersShocked.append(sServerID)
            else:
                lg.logInfo("SHOCK ", "t|%6.0f| cannot reduce svr|%s| life|%.0f|"
                    % (G.env.now, sServerID, fOriginalLife)) 


# m R e d u c e S i n g l e S e r v e r L i f e t i m e 
    @catchex
    @ntracef("SHOK")
    def mReduceSingleServerLifetime(self, mysServerID, myfReduction):
        '''
        Reduce the lifetime of a single server. 
        
        Two possible methods, selected by a globaldata const nShockType.
        - 1: lifetime, which was already a random from a distribution
             with the standard server half-life, is then reduced 
             by some percentage during the shock period.
        - 2: lifetime during the shock period is a new random 
             chosen from a distribution with half-life reduced 
             *from its current lifetime* by the shock percentage.  
        '''
        cServer = G.dID2Server[mysServerID]
        fCurrentLife = cServer.mfGetMyCurrentLife()
        fOriginalLife = cServer.mfGetMyOriginalLife()
        # Hack to experiment with the two types of shock to see if they
        #  are statistically different.  
        if G.nShockType == 1:
            # Type 1: Lifetime during the shock period is the 
            #  reduction of the original lifetime by the given 
            #  percentage.
            #  That is, the server gets a single life expectation at
            #  birth, and it may be reduced by a shock and then 
            #  restored at the end of the shock period, provided
            #  that it has not expired during the shock period.  
            fNewLifeParam = (1.0 - myfReduction) * fCurrentLife
            # Lifetime cannot actually be zero for 100% reduction, so
            #  make it just really, really small, like 2 hours.  
            fNewLifeParam = max(fNewLifeParam, 2.0)
            NTRC.ntracef(3, "SHOK", "proc shock1 at t|%8.0f| svr|%s| new"
                "lifeparam|%.0f| shocktype|%s|" 
                % (G.env.now, mysServerID, fNewLifeParam, G.nShockType))
            fNewLife = fNewLifeParam
        elif G.nShockType == 2: 
            # Type 2: lifetime during shock period is a new
            #  random chosen from a distribution with less than the lifetime
            #  of the old one.  
            fNewLifeParam = (1.0 - myfReduction) * fOriginalLife
            # Lifetime cannot actually be zero for 100% reduction, so
            #  make it just really, really small, like 2 hours.  
            fNewLifeParam = max(fNewLifeParam, 2.0)
            NTRC.ntracef(3, "SHOK", "proc shock1 at t|%8.0f| svr|%s| new"
                "lifeparam|%.0f| shocktype|%s|" 
                % (G.env.now, mysServerID, fNewLifeParam, G.nShockType))
            fNewLife = util.makeserverlife(fNewLifeParam)
        else:
            NTRC.ntrace(0, "SHOK", "proc ERROR  at t|%8.0f| svr|%s| "
                "unknown shock type|%s|" 
                % (G.env.now, mysServerID, G.nShockType))            
            # Should throw a bugcheck fatal error at this point.
            
        NTRC.ntracef(3, "SHOK", "proc shock2 at t|%8.0f| svr|%s| new"
            "life|%.0f| shocktype|%s|" 
            % (G.env.now, mysServerID, fNewLife, G.nShockType))
        lg.logInfo("SHOCK ", "t|%6.0f| reduce svr|%s| life by|%s| from|%.0f| to"
            "|%.0f| shocktype|%s|" 
            % (G.env.now, mysServerID, myfReduction, fOriginalLife, fNewLife, 
            G.nShockType))
        cServer.mRescheduleMyLife(fNewLife)
        return


# m S h o c k E x p i r e s 
    @catchex
    @ntracef("SHOK")
    def mShockExpires(self):
        ''' 
        The shock has expired.  Restore normal lifetimes for
        all the servers that were injured by the shock.
        '''
        self.mRestoreSomeServerLifetimes()
        return


# m R e s t o r e S o m e S e r v e r L i f e t i m e s 
    @catchex
    @ntracef("SHOK")
    def mRestoreSomeServerLifetimes(self):
        ''' For all the servers injured by the shock, restore life. '''
        lg.logInfo("SHOCK ", "t|%6.0f| shock end, restoring server lifetimes "
            "for ids|%s|" 
            % (G.env.now, self.lsServersShocked))
        # WARNING: list may be empty if server default life is infinite (zero).
        for sServerID in self.lsServersShocked:
            self.mRestoreSingleServerLifetime(sServerID)
        self.lsServersShocked = []
        return


# m R e s t o r e S i n g l e S e r v e r L i f e t i m e 
    @catchex
    @ntracef("SHOK")
    def mRestoreSingleServerLifetime(self, mysServerID):
        ''' Restore normal lifetime to a single server. '''
        bDeadAlready = CShock.cmbShouldServerDieNow(mysServerID)

        cServer = G.dID2Server[mysServerID]
        if cServer.mbIsServerDead() or bDeadAlready:
            lg.logInfo("SHOCK ", "t|%6.0f| cannot restore dead server|%s| life" 
                % (G.env.now, mysServerID))
        else:
            fOriginalLifespan = cServer.mfGetMyOriginalLife()
            lg.logInfo("SHOCK ", "t|%6.0f| restoring server|%s| life to |%.0f|" 
                % (G.env.now, mysServerID, fOriginalLifespan))
            cServer.mRescheduleMyLife(fOriginalLifespan)
        return mysServerID


# C S h o c k . c m B e f o r e A u d i t 
    @classmethod
    @catchex
    @ntracef("SHOK")
    def cmBeforeAudit(self):
        '''
        Before each audit cycle, check to see if any servers
         have exceeded their lifetimes.
        '''
        for (sServerID, cServer) in (util.fnttSortIDDict(G.dID2Server)):
            fCurrentLife = cServer.mfGetMyCurrentLife()
            bServerAlive = not cServer.mbIsServerDead()

            # Log that we are examining this server, 
            #  but note if it's already dead.
            sStatus = "" if bServerAlive else "dead"
            lg.logInfo("SHOCK ", "t|%6.0f| audit+end checking server|%s| "
                "life|%.0f|=|%.1f|yr %s" 
                % (G.env.now, sServerID, fCurrentLife, fCurrentLife/10000, 
                sStatus))
            NTRC.ntracef(3, "SHOK", "proc t|%6.0f| check expir? svr|%s| "
                "svrdefaulthalflife|%s| currlife|%s|" 
                % (G.env.now, sServerID, G.fServerDefaultHalflife, 
                fCurrentLife))
            # Check to see if the server's lifetime has expired. 
            bDeadAlready = CShock.cmbShouldServerDieNow(sServerID)

        return G.nDeadOldServers


# C S h o c k . c m A t E n d O f R u n 
    @classmethod
    @catchex
    @ntracef("SHOK")
    def cmAtEndOfRun(self):
        '''
        At end of run, check to see if any servers have exceeded
         their lifetimes.  It is possible for servers to die from
         shocks even if there is no auditing, and that counts
         because we evaluate every doc at the end of run.
        '''
        lg.logInfo("SHOCK ", "t|%6.0f| end of run checking all server lifetimes" 
            % (G.env.now))
        nResult = CShock.cmBeforeAudit()
        return


# C S h o c k . c m b S h o u l d S e r v e r D i e N o w 
    @classmethod
    @catchex
    @ntracef("SHOK")
    def cmbShouldServerDieNow(self, mysServerID):
        ''' 
        If the server's (possibly reduced) lifetime has expired, 
         kill it rather than restoring it to a full life.
        '''
        cServer = G.dID2Server[mysServerID]
        fCurrentLife = cServer.mfGetMyCurrentLife()
        bServerAlive = not cServer.mbIsServerDead()
        if (G.fServerDefaultHalflife > 0
            and fCurrentLife > 0
            and fCurrentLife <= G.env.now
            and bServerAlive
            ):
            # Server has overstayed its welcome.  Kill it.  
            sInUse = "currently in use" if cServer.mbIsServerInUse() else ""
            lg.logInfo("SHOCK ", "t|%6.0f| kill server|%s| life|%.0f|=|%.1f|yr"
                " expired %s" 
                % (G.env.now, mysServerID, fCurrentLife, fCurrentLife/10000, 
                sInUse))
            NTRC.ntracef(3, "SHOK", "proc t|%6.0f| expired svr|%s| "
                "svrdefaulthalflife|%s| currlife|%.0f|" 
                % (G.env.now, mysServerID, G.fServerDefaultHalflife, 
                fCurrentLife))
            result = cServer.mKillServer()
            G.nDeadOldServers += 1
            bResult = True
            # Now check to see if the server died because of the shock.
            #  Is the current life less than the original life?
            # Philosophical question: if the shock type 2 caused your new, 
            #  recalculated life to be longer than your original life, 
            #  can your death reasonably be attributed to the shock?
            #  Answer = no, because without the shock you would have
            #  died even earlier.  Tricky, though.  
            fOriginalLife = cServer.mfGetMyOriginalLife()
            if fCurrentLife < fOriginalLife:
                G.nDeathsDueToShock += 1
                G.lDeathsDueToShock.append(mysServerID)
        else:
            bResult = False
        return bResult

"""
=============================
BZZZT!  Major change of plan!
=============================

The death of a server does not really affect anything much UNTIL 
the next audit cycle.  Then the dead server is detected when a repair
is attempted and all the usual crap happens.  There is, admittedly, a
small waste of time processing sector errors in the server which should
be dead, but this is a very minor waste of CPU time.  

Soooo, the theory goes like this:
- Server is born with an expiration date.  Random, derived from some
distribution or other.  The boss wants to generalize from exponential
to maybe-something-else.  What?  Gamma?  Beta with a max (ha, ha, 
Beta-Max, get it?)?  Weibull?  The routine to get server lifetimes
is isolated in util, so easy to change.
- If default server halflife is zero (= infinite), no expiration.  
This is important so that we don't disturb the random number stream.
- Server deaths are silent when they occur.  They will not be noticed 
until the next audit cycle.  
- At the beginning of each audit cycle, and at the end of the simulation, 
check all servers to see if the expiration date is less than the current 
time.
- If the server has expired, kill it and all its documents.  Standard
functions already available, or used to be.  
- When a shock occurs, immediately downgrade the life expectancies of 
some number of servers based on shockspan.  And set an event for the 
shock end date.
- When the shock expires, restore the life expectancies of all servers
to their original values.  Doesn't matter if the value is now less than 
the next audit time, because the death will be discovered then.  

Before each audit and at end of run, check for servers that might have
died in the meantime.  
- Servers may have finite lifetimes even if there are no shocks during
the run.  Check for servers with expired lifetimes at end of run.
- Servers may die from aging even if there is no shock, of course, 
just from having bad genes (a short random initial lifetime).  
- Server deaths from aging are not detected until the next audit cycle 
or the end of the run.  Deaths are always silent.  Deaths occur even if
there is no auditing.  
- Be careful with servers that have zero lifetimes or if default 
server lifetime is zero.  There is no server aging in that case, 
which was always the normal case previously.  And there is no lifetime
reduction or restoration at begin or end of shock.  
NB: The broker's instruction generator has been specifically wired 
to avoid these pathological cases.  If the server default lifetime 
is zero, then no shocks are permitted.  Still need paranoid 
protective code here, though, to protect against future maintenance 
and modifications.  
- If a server's lifetime has expired, declare the server to be dead, 
using at least CServer.mKillServer.
- Server is dead if its lifetime is <= now
                and its lifetime is > 0
                and server default life is > 0
(probably change the order of evaluation for efficiency).
- Do I need to do anything else to kill a server?
- Ignore anything that happens between the time that the 
server *should* die and the time it is actually detected
during the next audit cycle or at end of run.  
This would be a nice optinization that is not currently 
implemented; we still accept sector errors in servers
that have expired (but whose expiry has not been detected).
"""


# Edit history:
# 20160411  RBL Begin.
# 20161121  RBL Describe plan in comments.  Real code to follow.
# 20161205  RBL Insert stubs.
# 21061212  RBL Flesh out most of the stubs.
# 20161218  RBL Debug, and revise GUI.  Still need to fix CLI->G.
# 20161222  RBL Simplify (and correct) shock expiration.  
#                Limitation: cannot start shock2 while shock1 is
#                still in progress.  Not too serious, but maybe
#                noticeable to some.
#               Make sure that reducing and restoring lifetime works.
# 20161224  RBL Flesh out audit and end routines to check for server
#                lifetime expirations.  
# 20161231  RBL If server is already dead, don't kill it again, and 
#                if it should be dead now, kill it now and 
#                don't try to restore its lifetime to normal.  
# 20170109  RBL Careful not to try to reduce a zero (=infinite) lifetime
#                of a server, nor to restore it later.  
#               Slightly improve reporting of changed lifetimes.
#               Add type 2 shock, which generates a new random lifetime 
#                based on the same distribution shape but with a reduced
#                half-life.  In both shock types, the original life is 
#                restored at the end of the shock if the server has 
#                not died during the shock.  
# 20170317  RBL On 100% shock impact, do not permit the lifetime to go
#                quite to zero; causes an div-zero exception in util.
# 20171130  RBL Clarify shock type calcs with some comments.
#                PEP8-ify some of the spacing.  
# 20171204  RBL More clearly document the two types of shock.
#               Clean up formatting and comments some more.  
# 

#END
