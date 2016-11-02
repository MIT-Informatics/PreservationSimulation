#!/usr/bin/python
#testtimer1.py

'''
start a server, life infinity
start a shock, life something short

wait for shock
when shock occurs, interrupt server, set new lifetime, start server

then try it with two or three servers



'''

import  resettabletimer     as rt
from    NewTraceFac         import NTRC, ntrace, ntracef
import  simpy
import  util
from    catchex             import catchex

class ImaServer(object):
    @catchex
    @ntrace
    def __init__(self, name, life):
        self.ID = name
        self.life = life
        self._timer = rt.CResettableTimer(G.env, life, servercall, serverinter, self)
        self._timer.start()
        self.oldevent = self.   _timer.event

        G.env.process(self.ageserver(life))
    
    @catchex
    @ntrace
    def ageserver(self,life):
        NTRC.ntrace(0, "proc server.age before yield id|%s| t|%s|" 
            % (self.ID, G.env.now))
        result = None
        while not result or result == "RESCHEDULED":
            result = yield self._timer.event
            NTRC.ntrace(0, "proc serverage after  yield id|%s| t|%s| result|%s|" 
                % (self.ID, G.env.now, result))
        NTRC.ntrace(0, "proc server.age end of yield id|%s| t|%s| result|%s|" 
            % (self.ID, G.env.now, result))

    @property
    def timer(self):
        return self._timer

@catchex
@ntrace
def servercall(timerobj, context):
    NTRC.ntrace(0, "proc servercall before setevent id|%s| t|%s|" 
        % (context.ID, G.env.now))
    timerobj.setevent("OK")

@catchex
@ntrace
def serverinter(timerobj, context):
    NTRC.ntrace(0, "proc serverinter id|%s| t|%s|" 
        % (context.ID, G.env.now))
    context.oldevent.succeed("RESCHEDULED")



class ImaShock(object):
    @catchex
    @ntrace
    def __init__(self, name, life):
        self.ID = name
        self.life = life
        self._timer = rt.CResettableTimer(G.env, life, shockcall, shockinter, self.ID)
        NTRC.ntrace(0, "proc shock before wait t|%s|" % G.env.now)
        self._timer.start()
        G.env.process(self.waitforshock())
        NTRC.ntrace(0, "proc shock after  wait t|%s|" % G.env.now)
        
    @catchex
    @ntrace
    def waitforshock(self):
        NTRC.ntrace(0, "proc shock.waitforit before yield t|%s|" % G.env.now)
        yield self._timer.event
        NTRC.ntrace(0, "proc shock.waitforit after  yield t|%s|" % G.env.now)
        
        NTRC.ntrace(0, "proc shock.waitforit reset the server timer here!")
        G.sa.timer.stop()
        G.sa.timer.setdelay(33333).start()
        NTRC.ntrace(0, "proc shock.waitforit done reset server timer")

@catchex
@ntrace
def shockcall(timerobj, context):
    timerobj.setevent()
    pass

@catchex
@ntrace
def shockinter(timerobj, context):
    pass


class G(object):
    env = None
    sa = None


@catchex
@ntrace
def main():
    G.env = simpy.Environment()
    sa = ImaServer("A", 1E6)
    G.sa = sa
    sb = ImaServer("B", 2E6)
    shock = ImaShock("SA", 1000)
    
    G.env.run()


if __name__ == "__main__":
    main()    

