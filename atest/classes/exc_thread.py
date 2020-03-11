from threading import Thread, Event

from atest.exceptions import TestBrokenException
from atest.classes.basic_test import Test


class ExceptionThread(Thread):

    def __init__(self, func, event):
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
    t = Thread(target=_start_test_at_daemon_thread, args=(test.test, event), daemon=True)
    t.start()
    t.join(test.timeout)
    if t.is_alive():
        event.set()
        raise TestBrokenException(f'Time ({test.timeout} seconds) is over for test "{test}"!')
    if hasattr(event, 'attr'):
        raise event.attr


def _start_test_at_daemon_thread(func, event: Event):
    t = ExceptionThread(func, event)
    t.start()
    while not event.is_set():
        if not t.is_alive():
            break
