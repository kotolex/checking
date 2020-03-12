from unittest import main, TestCase
from time import sleep

from atest.runner import start
from atest.classes.basic_listener import Listener
from atest.annotations import *
from test.fixture_behaviour_test import clear


def _fn(it):
    assert it in range(3)


def data_time(it):
    sleep(0.1)
    assert 1 == 1


def simple():
    assert 1 == 1


def long():
    sleep(1.5)

def long_data(it):
    sleep(1.5)


def raises():
    sleep(0.5)
    assert 1 == 2, 'Here we fail!'


class BehaviourTest(TestCase):

    def test_three_success_when_data(self):
        clear()
        data(name='three')(lambda: [0, 1, 2])
        test(data_provider='three')(_fn)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(3, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(3, TestSuite.get_instance().tests_count())

    def test_three_success_one_failed_when_data(self):
        clear()
        data(name='four')(lambda: [0, 1, 2, 3])
        test(data_provider='four')(_fn)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(3, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))
        self.assertEqual(4, TestSuite.get_instance().tests_count())

    def test_timeout_ok_if_less(self):
        clear()
        test(timeout=10)(simple)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_timeout_failed_if_bigger(self):
        clear()
        test(timeout=1)(long)
        start(listener=Listener(0))
        self.assertEqual(1, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_timeout_failed_if_exception(self):
        clear()
        test(timeout=1)(raises)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_timeout_ok_with_data(self):
        clear()
        data(name='three')(lambda: [0, 1, 2])
        test(timeout=1, data_provider="three")(data_time)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(3, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(3, TestSuite.get_instance().tests_count())

    def test_timeout_failed_with_data(self):
        clear()
        data(name='three')(lambda: [0, 1, 2])
        test(timeout=1, data_provider="three")(long_data)
        start(listener=Listener(0))
        self.assertEqual(3, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(3, TestSuite.get_instance().tests_count())


if __name__ == '__main__':
    main()
