#!/usr/bin/python
# resettabletimer.py
# Vaguely based on original from stackoverflow.
# Timer using SimPy that can be scheduled, reset, and rescheduled.
# Create an instance for each separate timing sequence.  

import simpy
from NewTraceFac import ntrace, ntracef, NTRC

'''
Class CResettableTimer
__init__:   constructor
    env         SimPy Environment object.
    delay       Duration of timer interval, in SimPy time units.
                 Integer or floating point.
    callbackfn  Function to call when timer instance fires.
                 Called with two args, the timer instance object and
                  the context (probably string or object).
                  (The context object can, e.g., be a tuple, and one
                  might include instance pointers that would not be 
                  available to the callbackfn.)  
                 If None, no callbackfn will be invoked.
    interruptfn Function to call when timer is interrupted with stop().
                 Note that reset() also calls stop() to interrupt.
                 Called with two args, the timer instance object and
                  the context (probably string or object).
                 If None, no interruptfn will be invoked.
    context     String or object to identify the timer instance to the 
                 callback function.
                Also used in debug ntrace messages.

start       Schedule a SimPy event for delay units from now.

stop        Interrupt a scheduled event.  The timer will not fire.  
             Calls the interrupt function, if any.

reset       stop() and re-start() an event now.  
             If this timer instance is running, interrupt it now.
             Call the interrupt function, if any.  
             Start a new timer, with this same instance and the same delay.

setdelay    Store a new delay time to be used by future start() calls.  
            Note that this function returns self, so that one can chain 
             calls, e.g., timerobject.setdelay(5).start()
    newdelay    New delay value >0 to be used for this instance.  

_wait       Internal routine that schedules the event and invokes the 
             callbackfn function or handles the Interrupt exception.  

setevent    Trigger (actually, succeed()) the proxy event in the 
             timer object.  This should be called from the user's
             callback function to trigger the event.

event       A property of the timer object that the user can yield to 
             wait for the timer in-line, provided that the event has been 
             triggered (by setevent()) in the callback function.
             Actually, the event can be triggered at any time, but
             doing this in the callback guarantees that the timer expired. 
             A new proxyevent is created every time the timer is started. 

Readonly properties to get at attributes carefully:
event       The proxyevent to wait for (with yield).
oldevent    The previous proxy event, which someone might be waiting
             for while the new event is being rescheduled.  
context     The caller-supplied context string or object.
delay       Current delay value.  This is changed with setdelay().
'''
# c l a s s   C R e s e t t a b l e T i m e r 
class CResettableTimer(object):

    @ntrace
    def __init__(self, env, delay, callbackfn, interruptfn, context):
        '''
        Store params for timer but don't start one yet.
        '''
        self.env        = env 
        self._delay     = delay
        self.action     = None
        self.callbackfn = callbackfn
        self.interruptfn= interruptfn
        self.running    = False
        self.canceled   = False
        self._context   = context
        self.starttime  = None
        self.stoptime   = None
        self._proxyevent = None
        self._oldevent  = None
        self.ID         = context       # special for debug traces

    @ntrace
    def _wait(self):
        """
        Calls a callback function after time has elapsed. 
        Also handles Interrupt exception.
         This also invokes an interrupt notification function 
         in the same way.  
        Note that the yield here doesn't cause its caller to wait, but
         only delays calling the callback routine.  
        """
        try:
            yield self.env.timeout(self._delay)
            if self.callbackfn:
                self.callbackfn(self, self._context)
            self.running  = False
        except simpy.Interrupt as i:
            NTRC.trace(3,"Interrupted %s at %s!" % (self.__repr__, self.env.now))
            if self.interruptfn:
                self.interruptfn(self, self._context)
            self.canceled = True
            self.running  = False
        NTRC.trace(3,"proc exit _wait action|%s| running|%s| canceled|%s| t=%s" 
            % (self.action, self.running, self.canceled, self.env.now))

    @ntrace
    def start(self):
        """
        Starts the timer using the stored delay interval. 
         Saves the old proxy event, if any, in case someone
         is already waiting for it and needs to be released
         with a bad value.
        """
        if not self.running:
            self.running = True
            self.canceled = False
            self.action  = self.env.process(self._wait())
            self.starttime = self.env.now
            self._oldevent = self._proxyevent
            self._proxyevent = self.env.event()
        return (self.action, self.running, self.canceled)

    @ntrace
    def stop(self):
        """
        Stops the timer using SimPy's interrupt() function.
        Note that it also calls SimPy's step() function to ensure
         that the Interrupt exception is processed right now, in 
         correct order.
        """
        if self.running:
            self.action.interrupt()
            self.action = None
            self.stoptime = self.env.now
            self.env.step()
        return (self.action, self.running, self.canceled)

    @ntrace
    def reset(self):
        """
        Interrupts the current timer and re-starts it with the same delay. 
        """
        self.stop()
        self.start()
        return (self.action, self.running, self.canceled)

    @ntrace
    def setdelay(self, newdelay):
        """
        Changes the delay interval to be used for future start()s. 
        """
        if newdelay > 0:
            self._delay = newdelay
        else:
            raise ValueError("bad new delay|%s| for %s %s" % (newdelay, self, self.context))
        return self

    @ntrace
    def setevent(self, value=None):
        """
        Turn on the proxy event so that anyone waiting for it (yield-ing it)
         can proceed.
        """
        self._proxyevent.succeed(self.env.now if value==None else value)
        return self

    @property
    def event(self):
        '''Give the caller the proxy event so he can wait for it'''
        return self._proxyevent

    @property
    def oldevent(self):
        '''Give the caller the previous proxy event so he can 
        force it to exit with a bad value if it is interrupted.'''
        return self._oldevent

    @property
    def context(self):
        return self._context

    @property
    def delay(self):
        return self._delay

    def __str__(self):
        '''Return a sensible printable string for this object'''
        return '<%s object ID=%s at 0x%x>' % (self._desc(), self.context, id(self))

    def _desc(self):
        '''Return class name'''
        return '%s()' % self.__class__.__name__


if 1:

    # C a l l b a c k   a n d   I n t e r r u p t   r o u t i n e s 
    @ntrace
    def callback(timerobj, context):
        NTRC.trace(0,"callback %s delay %s called from %s at %s." 
            % (context, timerobj.delay, timerobj, env.now))
        timerobj.setevent()
        return (timerobj, context)

    @ntrace
    def interrupt(timerobj, context):
        NTRC.trace(0,"interrupt %s delay %s called from %s at %s." 
            % (context, timerobj.delay, timerobj, env.now))
        return (timerobj, context)


    # E x e r c i s e   r o u t i n e s 
    @ntrace
    def starter4e(env, event):
        NTRC.trace(3,"4e.starter4e: before callstart at %s." % env.now)
        event.start()
        NTRC.trace(3,"4e.starter4e: before yieldtimeout at %s." % env.now)
        yield env.timeout(3)
        NTRC.trace(3,"4e.starter4e: after yieldtimeout at %s." % env.now)
        event.reset()
        NTRC.trace(3,"4e.starter4e: after callreset at %s." % env.now)

    @ntrace
    def starter4f(env, event):
        NTRC.trace(3,"4f.starter4f: before callstart at %s." % env.now)
        event.start()
        NTRC.trace(3,"4f.starter4f: before yieldtimeout at %s." % env.now)
        yield env.timeout(5)
        NTRC.trace(3,"4f.starter4f: after yieldtimeout at %s." % env.now)
        event.stop()
        event.start()
        NTRC.trace(3,"4f.starter4f: after stop/start at %s." % env.now)

    @ntrace
    def starter4g(env, event):
        NTRC.trace(3,"4g.starter4g: before callstart at %s." % env.now)
        event.start()
        NTRC.trace(3,"4g.starter4g: before yieldtimeout at %s." % env.now)
        yield env.timeout(5)
        NTRC.trace(3,"4g.starter4g: after yieldtimeout at %s." % env.now)
        event.stop()
        event.stop()        # can you stop a stopped timer?  yes.
        event.setdelay(17).start()
        yield env.timeout(1)
        event.reset()
        yield env.timeout(1)
        event.reset()
        NTRC.trace(3,"4g.starter4g: after change delay and reset twice at %s." % env.now)

    @ntrace
    def starter4h(env, event):
        NTRC.trace(3,"4h.starter4h: before callstart at %s." % env.now)
        event.start()
        NTRC.trace(3,"4h.starter4h: before yieldtimeout at %s." % env.now)
        yield env.timeout(23)
        NTRC.trace(3,"4h.starter4h: after yieldtimeout at %s." % env.now)
        event.reset()
        NTRC.trace(3,"4h.starter4h: after reset at %s." % env.now)
        yield event.event
        NTRC.trace(3,"4h.starter4h: after yieldevent at %s." % env.now)
        NTRC.trace(0,"yieldevent %s completed at %s." % (event.context,env.now))

    # M a i n
    if __name__ == '__main__':
        NTRC.trace(3,"4.Begin.")
        env = simpy.Environment()
        event1 = CResettableTimer(env, 7, callback, interrupt, "ev1")
        event2 = CResettableTimer(env, 11.123, callback, interrupt, "ev2")
        event3 = CResettableTimer(env, 13, callback, interrupt, "ev3")
        event4 = CResettableTimer(env, 31, callback, interrupt, "ev4")
        event5 = CResettableTimer(env, 37, callback, interrupt, "ev5")
        NTRC.trace(0,"4.Starting simulation.")
        env.process(starter4e(env, event1))
        env.process(starter4f(env, event2))
        env.process(starter4g(env, event3))
        env.process(starter4h(env, event4))
        env.run(1000)
        NTRC.trace(0,"4.End of simulation.")

    ''' Should give results like this:
$ python resettabletimer.py 2>&1
20161101_195053 0       4.Starting simulation.
20161101_195053 0       interrupt ev1 delay 7 called from <CResettableTimer() object ID=ev1 at 0x6ffffe29e10> at 3.
20161101_195053 0       interrupt ev2 delay 11.123 called from <CResettableTimer() object ID=ev2 at 0x6ffffe29e50> at 5.
20161101_195053 0       interrupt ev3 delay 13 called from <CResettableTimer() object ID=ev3 at 0x6ffffe29e90> at 5.
20161101_195053 0       interrupt ev3 delay 17 called from <CResettableTimer() object ID=ev3 at 0x6ffffe29e90> at 6.
20161101_195053 0       interrupt ev3 delay 17 called from <CResettableTimer() object ID=ev3 at 0x6ffffe29e90> at 7.
20161101_195053 0       callback ev1 delay 7 called from <CResettableTimer() object ID=ev1 at 0x6ffffe29e10> at 10.
20161101_195053 0       callback ev2 delay 11.123 called from <CResettableTimer() object ID=ev2 at 0x6ffffe29e50> at 16.123.
20161101_195053 0       interrupt ev4 delay 31 called from <CResettableTimer() object ID=ev4 at 0x6ffffe29ed0> at 23.
20161101_195053 0       callback ev3 delay 17 called from <CResettableTimer() object ID=ev3 at 0x6ffffe29e90> at 24.
20161101_195053 0       callback ev4 delay 31 called from <CResettableTimer() object ID=ev4 at 0x6ffffe29ed0> at 54.
20161101_195053 0       yieldevent ev4 completed at 54.
20161101_195053 0       4.End of simulation.

    '''

# Edit history:
# 20160531  RBL Original version modeled after the stackoverflow listing.
# 20160609  RBL Add interrupt function, start and stop (SimPy) times.
#               Add timer instance obj arg to callbacks.
# 20161030  RBL Add proxyevent so that the caller can actually wait for
#                the timer in-line by having the callback routine
#                setevent() the timer.  
#                (Otherwise, the caller would have to do everything
#                inside the callback function, which would be icky.)
#               Add readable __str__ for timer class.
# 
