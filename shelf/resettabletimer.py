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
    callbackfn  Function to call when timer instance fires.
                 Called with two args, the timer instance object and
                  the context (probably string or object).
                  (The context object can, e.g., be a tuple, and one
                  might include instance pointers that would not be 
                  available to the callbackfn.)  
                 If None, no callbackfn will be invoked.
    interruptfn Function to call when timer is interrupted with stop().
                 Called with two args, the timer instance object and
                  the context (probably string or object).
                 If None, no interruptfn will be invoked.
    context     String or object to identify the timer instance to the 
                 callback function.
                Also used in debug ntrace messages.
                (There could also be an interruptfn, but I don't see
                a need for one yet.)
start       Schedule a SimPy event for delay units from now.
stop        Interrupt a scheduled event.  The timer will not fire.  
reset       Stop and start an event now.  
             If there is one scheduled by this instance, interrupt it now.
             Start a new timer (with this same instance) with the same delay.
setdelay    Store a new delay time to be used by future start calls.  
            Note that it returns self, so that one can chain calls, 
             e.g., timerobject.setdelay(5).start()
    newdelay    New delay value to be used for this instance.  
wait        Internal routine that schedules the event, invokes the 
             callbackfn function, or handles the Interrupt exception.  
'''

class CResettableTimer(object):

    @ntrace
    def __init__(self, env, delay, callbackfn, interruptfn, context):
        '''
        Store params for timer but don't start one yet.
        '''
        self.env        = env 
        self.delay      = delay
        self.action     = None
        self.callbackfn = callbackfn
        self.interruptfn= interruptfn
        self.running    = False
        self.canceled   = False
        self.context    = context
        self.starttime  = None
        self.stoptime   = None

    @ntrace
    def wait(self):
        """
        Calls a callback function after time has elapsed. 
        Also handles Interrupt exception.
         This could invoke an interrupt notification function 
         in the same way.  NYI.  
        """
        try:
            yield self.env.timeout(self.delay)
            if self.callbackfn:
                self.callbackfn(self, self.context)
            self.running  = False
        except simpy.Interrupt as i:
            NTRC.trace(3,"Interrupted %s at %s!" % (self.context, env.now))
            if self.interruptfn:
                self.interruptfn(self, self.context)
            self.canceled = True
            self.running  = False
        NTRC.trace(3,"proc exit wait action|%s| running|%s| canceled|%s| t=%s" 
            % (self.action, self.running, self.canceled, self.env.now))

    @ntrace
    def start(self):
        """
        Starts the timer using the stored delay interval. 
        """
        if not self.running:
            self.running = True
            self.canceled = False
            self.action  = self.env.process(self.wait())
            self.starttime = self.env.now
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
        self.delay = newdelay
        return self


if 1:
    @ntrace
    def callback4(timerobj, context):
        NTRC.trace(0,"callback4 %s called from %s at %s." 
            % (context, timerobj, env.now))

    @ntrace
    def interrupt4(timerobj, context):
        NTRC.trace(0,"interrupt4 %s called from %s at %s." 
            % (context, timerobj, env.now))

    @ntrace
    def starter4e(env, event):
        NTRC.trace(3,"4e.starter4e: before callwait at %s." % env.now)
        event.start()
        NTRC.trace(3,"4e.starter4e: after callwait at %s." % env.now)
        yield env.timeout(3)
        NTRC.trace(3,"4e.starter4e: after yield at %s." % env.now)
        event.reset()
        NTRC.trace(3,"4e.starter4e: after stop at %s." % env.now)

    @ntrace
    def starter4f(env, event):
        NTRC.trace(3,"4f.starter4f: before callwait at %s." % env.now)
        event.start()
        NTRC.trace(3,"4f.starter4f: after callwait at %s." % env.now)
        yield env.timeout(5)
        NTRC.trace(3,"4f.starter4f: after yield at %s." % env.now)
        event.stop()
        event.start()
        NTRC.trace(3,"4f.starter4f: after stop at %s." % env.now)

    @ntrace
    def starter4g(env, event):
        NTRC.trace(3,"4g.starter4g: before callwait at %s." % env.now)
        event.start()
        NTRC.trace(3,"4g.starter4g: after callwait at %s." % env.now)
        yield env.timeout(5)
        NTRC.trace(3,"4g.starter4g: after yield at %s." % env.now)
        event.stop()
        event.stop()
        event.setdelay(17).start()
        yield env.timeout(1)
        event.reset()
        yield env.timeout(1)
        event.reset()
        NTRC.trace(3,"4g.starter4g: after stop at %s." % env.now)

    if __name__ == '__main__':
        NTRC.trace(3,"4.Begin.")
        env = simpy.Environment()
        event1 = CResettableTimer(env, 7, callback4, interrupt4, "ev1")
        event2 = CResettableTimer(env, 11, callback4, interrupt4, "ev2")
        event3 = CResettableTimer(env, 13, callback4, interrupt4, "ev3")
        NTRC.trace(0,"4.Starting simulation.")
        env.process(starter4e(env, event1))
        env.process(starter4f(env, event2))
        env.process(starter4g(env, event3))
        env.run(40)
        NTRC.trace(0,"4.End of simulation.")
    ''' Should give
$ python resettabletimer-02.py
20160617_134858 0       4.Starting simulation.
20160617_134858 0       interrupt4 ev1 called from <__main__.CResettableTimer object at 0x6ffffdffd90> at 3.
20160617_134858 0       interrupt4 ev2 called from <__main__.CResettableTimer object at 0x6ffffdffdd0> at 5.
20160617_134858 0       interrupt4 ev3 called from <__main__.CResettableTimer object at 0x6ffffdffe10> at 5.
20160617_134858 0       interrupt4 ev3 called from <__main__.CResettableTimer object at 0x6ffffdffe10> at 6.
20160617_134858 0       interrupt4 ev3 called from <__main__.CResettableTimer object at 0x6ffffdffe10> at 7.
20160617_134858 0       callback4 ev1 called from <__main__.CResettableTimer object at 0x6ffffdffd90> at 10.
20160617_134858 0       callback4 ev2 called from <__main__.CResettableTimer object at 0x6ffffdffdd0> at 16.
20160617_134858 0       callback4 ev3 called from <__main__.CResettableTimer object at 0x6ffffdffe10> at 24.
20160617_134858 0       4.End of simulation.

    '''

# Edit history:
# 20160531  RBL Original version modeled after the stackoverflow listing.
# 20160609  RBL Add interrupt function, start and stop (SimPy) times.
#               Add timer instance obj arg to callbacks.
# 
