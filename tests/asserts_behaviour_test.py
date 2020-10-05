from unittest import main, TestCase

from checking.asserts import *
from checking.context import *
from checking.annotations import test
from checking.runner import start
from checking.classes.basic_suite import TestSuite
from checking.classes.listeners.basic import Listener
from tests.fixture_behaviour_test import clear


def _run(func):
    clear()
    test(func)
    start(listener=Listener(3))


class TestAssertsBehaviour(TestCase):

    def test_wait_exception_test_broken_if_BaseException(self):
        def fn():
            with should_raise(BaseException):
                print()

        _run(fn)
        self.assertEqual(1, len(TestSuite.get_instance().broken()))

    def test_wait_success_test_if_Exception(self):
        def fn():
            with should_raise(Exception):
                x = 1 / 0

        _run(fn)
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))

    def test_wait_success_test_if_concrete_exception(self):
        def fn():
            with should_raise(ZeroDivisionError):
                x = 1 / 0

        _run(fn)
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))

    def test_wait_broken_test_if_use_non_exception_type(self):
        def fn():
            with should_raise('wrong'):
                x = 1 / 0

        _run(fn)
        self.assertEqual(1, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))

    def test_wait_failed_test_if_non_raised(self):
        def fn():
            with should_raise(Exception):
                pass

        _run(fn)
        self.assertEqual(1, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))

    def test_wait_failed_test_if_another_raised(self):
        def fn():
            with should_raise(ZeroDivisionError):
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
        _run(lambda: is_not_none(1))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))

    def test_not_none_negative(self):
        _run(lambda: is_not_none(None))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))


if __name__ == '__main__':
    main()
