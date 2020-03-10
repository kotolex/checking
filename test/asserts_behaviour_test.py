from unittest import main, TestCase

from atest.asserts import *
from atest.annotations import test
from atest.runner import start
from atest.classes.basic_suite import TestSuite
from atest.classes.basic_listener import Listener
from test.fixture_behaviour_test import clear


def _run(func):
    clear()
    test(func)
    start(listener=Listener(3))


class TestAssertsBehaviour(TestCase):

    def test_wait_exception_test_broken_if_BaseException(self):
        def fn():
            with waiting_exception(BaseException):
                print()

        _run(fn)
        self.assertEqual(1, len(TestSuite.get_instance().broken()))

    def test_wait_success_test_if_Exception(self):
        def fn():
            with waiting_exception(Exception):
                x = 1 / 0

        _run(fn)
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))

    def test_wait_success_test_if_concrete_exception(self):
        def fn():
            with waiting_exception(ZeroDivisionError):
                x = 1 / 0

        _run(fn)
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))

    def test_wait_broken_test_if_use_non_exception_type(self):
        def fn():
            with waiting_exception('wrong'):
                x = 1 / 0

        _run(fn)
        self.assertEqual(1, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))

    def test_wait_failed_test_if_non_raised(self):
        def fn():
            with waiting_exception(Exception):
                pass

        _run(fn)
        self.assertEqual(1, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))

    def test_wait_failed_test_if_another_raised(self):
        def fn():
            with waiting_exception(ZeroDivisionError):
                int('a')

        _run(fn)
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))

    def test_equals_positive(self):
        _run(lambda: equals(1, 1))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))

    def test_equals_negative(self):
        _run(lambda: equals(1, 2))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))

    def test_equals_none_negative(self):
        _run(lambda: equals(1, None))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))

    def test_is_none_positive(self):
        _run(lambda: is_none(None))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))

    def test_is_none_negative(self):
        _run(lambda: is_none(1))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))

    def test_not_none_positive(self):
        _run(lambda: not_none(1))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))

    def test_not_none_negative(self):
        _run(lambda: not_none(None))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))


if __name__ == '__main__':
    main()
