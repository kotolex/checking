from threading import Thread, Event
from typing import Callable

from atest.exceptions import TestBrokenException
from atest.classes.basic_test import Test


class ExceptionThread(Thread):
    """
    Класс-потомок потока, для перехватат исключений, которые не поймать обычным способом при многопоочном выполнении.
    Сохраняет исключение в контейнер Event
    """

    def __init__(self, func:Callable, event:Event):
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
    # Если поток жив, значит он не завершился по таймауту
    if t.is_alive():
        # Ставим уведомление что пора прервать работу и бросаем исключение
        event.set()
        raise TestBrokenException(f'Time ({test.timeout} seconds) is over for test "{test}"!')
    # Если есть атрибут, значит в потоке-демоне упало исключение, бросаем его
    if hasattr(event, 'attr'):
        raise event.attr


def _start_test_at_daemon_thread(test: Test, event: Event):
    t = ExceptionThread(test.run, event)
    t.start()
    # Пока не уведомили через ивент или не завершен поток-демон, работаем
    while not event.is_set():
        if not t.is_alive():
            break
