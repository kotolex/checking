from typing import Callable
from threading import Thread, Event

from checking.classes.basic_test import Test
from checking.exceptions import TestBrokenException


class ExceptionThread(Thread):
    """
    The sub-class of the thread, for catching exceptions, which do not catch by the usual approach with multi-threaded
    execution.
    Saves exceptions within Event container.
    """

    def __init__(self, func: Callable, event: Event):
        super().__init__(target=func, daemon=True)
        self.func = func
        self.daemon = True
        self.event = event

    def run(self):
        try:
            self.func()
        except Exception as e:
            self.event.attr = e


def run_with_timeout(test: Test):
    event = Event()
    t = Thread(target=_start_test_at_daemon_thread, args=(test, event), daemon=True)
    t.start()
    t.join(test.timeout)
    # If the thread is alive, then it had not over by time-out.
    if t.is_alive():
        # Put the notification that it is time to abort the work and give up the exception.
        event.set()
        raise TestBrokenException(f'Time ({test.timeout} seconds) is over for test "{test}"!')
    # If there is an attribute, then the exception inside the thread-demon, then raise it.
    if hasattr(event, 'attr'):
        raise event.attr


def _start_test_at_daemon_thread(test: Test, event: Event):
    t = ExceptionThread(test.run, event)
    t.start()
    # Not yet notified throw the event or the thread-demon has been working now, then work
    while not event.is_set():
        if not t.is_alive():
            break
