#!/usr/bin/python
#testtimer1.py

'''
start a server, life infinity
start a shock, life something short

wait for shock
when shock occurs, interrupt server, set new lifetime, start server

then try it with two or three servers



'''
from __future__ import absolute_import

from . import  resettabletimer     as rt
from    .NewTraceFac         import NTRC, ntrace, ntracef
import  simpy
from . import  util
from    .catchex             import catchex

# e l   f a k o   S e r v e r 
class ImaServer(object):
    @catchex
    @ntrace
    def __init__(self, name, life):
        self.ID = name
        self.life = life
        self._timer = rt.CResettableTimer(G.env, life, servercall, serverinter, self)
        self._timer.start()
        self.oldevent = self._timer.event

        G.env.process(self.ageserver(life))
    
    @catchex
    @ntrace
    def ageserver(self,life):
        NTRC.ntrace(0, "proc server.age before yield id|%s| t|%s|" 
            % (self.ID, G.env.now))
        result = None
        while not result or result == "CANCELED":
            NTRC.ntrace(3,"proc server.age |%s| waiting for event |%s|" 
                % (self, self._timer.event))
            result = yield self._timer.event
            NTRC.ntrace(0, "proc server.age after  yield id|%s| t|%s| result|%s|" 
                % (self.ID, G.env.now, result))
        NTRC.ntrace(0, "proc server.age end of yield id|%s| t|%s| result|%s|" 
            % (self.ID, G.env.now, result))

    @property
    def timer(self):
        return self._timer

    def __str__(self):
        '''Return a sensible printable string for this object'''
        return ('<%s object ID=%s at 0x%x>' 
            % (self.__class__.__name__, self.ID, id(self)))

@catchex
@ntrace
def servercall(timerobj, context):
    NTRC.ntrace(0, "proc server.call before setevent id|%s| t|%s|" 
        % (context.ID, G.env.now))
    NTRC.ntrace(3,"proc server.call |%s| setting timer|%s| event|%s|" 
        % (context, timerobj, timerobj.event))
    timerobj.setevent("OK")

@catchex
@ntrace
def serverinter(timerobj, context):
    NTRC.ntrace(0, "proc server.inter id|%s| t|%s|" 
        % (context.ID, G.env.now))
    NTRC.ntrace(3,"proc server.inter |%s| canceling timer|%s| event|%s|" 
        % (context, timerobj, context.oldevent))
    context.oldevent.succeed("CANCELED")


# e l   f a k o   S h o c k 
class ImaShock(object):
    @catchex
    @ntrace
    def __init__(self, name, life):
        self.ID = name
        self.life = life
        self._timer = rt.CResettableTimer(G.env, life, shockcall, shockinter, self.ID)
        NTRC.ntrace(0, "proc shock.init before waitfor t|%s|" % G.env.now)
        self._timer.start()
        G.env.process(self.waitforshock())
        NTRC.ntrace(0, "proc shock.init after  waitfor t|%s|" % G.env.now)
        
    @catchex
    @ntrace
    def waitforshock(self):
        NTRC.ntrace(0, "proc shock.waitfor before yield t|%s|" % G.env.now)
        yield self._timer.event
        NTRC.ntrace(0, "proc shock.waitfor after  yield t|%s|" % G.env.now)
        
        NTRC.ntrace(0, "proc shock.waitfor reset the server timer here!")
        G.sa.timer.stop()
        G.sa.timer.setdelay(33333).start()
        NTRC.ntrace(0, "proc shock.waitfor done reset server timer")

    def __str__(self):
        '''Return a sensible printable string for this object'''
        return ('<%s object ID=%s at 0x%x>' 
            % (self.__class__.__name__, self.ID, id(self)))

@catchex
@ntrace
def shockcall(timerobj, context):
    NTRC.ntrace(0, "proc shock.call before setevent id|%s| t|%s|" 
        % (context, G.env.now))
    timerobj.setevent()

@catchex
@ntrace
def shockinter(timerobj, context):
    NTRC.ntrace(0, "proc shock.inter id|%s| t|%s|" 
        % (context, G.env.now))


# A little bit of global data
class G(object):
    env = None
    sa = None


# M a i n 
@catchex
@ntrace
def main():
    G.env = simpy.Environment()
    sa = ImaServer("ServerA", 1E6)
    G.sa = sa
    sb = ImaServer("ServerB", 2E6)
    shock = ImaShock("ShockA", 1000)
    
    G.env.run()


if __name__ == "__main__":
    main()    

