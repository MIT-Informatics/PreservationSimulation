from __future__ import print_function

# simpypatch1.py
# 
# Instrument the step() method a little more to get useful information
#  out of errors in the events.  The "raise exc" line fails 100% of the
#  time without revealing anything about the problem; all we get is 
#  "not enough arguments for format string."


def step(self):
    """Process the next event.

    Raise an :exc:`EmptySchedule` if no further events are available.

    """
    print("\nENTERING step:")
    try:
        self._now, _, _, event = heappop(self._queue)
        print(("now:", self._now, "event:", event))
    except IndexError:
        raise EmptySchedule()

    # Process callbacks of the event. Set the events callbacks to None
    # immediately to prevent concurrent modifications.
    callbacks, event.callbacks = event.callbacks, None
    print(("callbacks:", callbacks))
    for callback in callbacks:
        callback(event)

    print(("event.ok", event.ok))
    if not event.ok and not hasattr(event, 'defused'):
        # The event has failed and has not been defused. Crash the
        # environment.
        # Create a copy of the failure exception with a new traceback.
        exc = type(event._value)(*event._value.args)
        exc.__cause__ = event._value
        raise exc

from simpy import Environment
from heapq import heappush, heappop

Environment.step = step


