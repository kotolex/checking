from unittest import main, TestCase
from time import sleep, time
import math

from checking.runner import start
from checking.classes.listeners.basic import Listener
from checking.classes.soft_assert import SoftAssert
from checking.annotations import *
from tests.fixture_behaviour_test import clear
from checking.asserts import *
from checking.helpers.others import short
from checking.context import *


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


def half_second():
    sleep(0.5)


def return2():
    return [0, 1, 2]


def sa_ok():
    soft = SoftAssert()
    soft.check(lambda: equals(1, 1))
    soft.check(lambda: equals(2, 2))
    soft.assert_all()


def sa_failed():
    soft = SoftAssert()
    soft.check(lambda: equals(1, 2))
    soft.check(lambda: equals(2, 2))
    soft.assert_all()


def raises():
    sleep(0.5)
    assert 1 == 2, 'Here we fail!'


class BehaviourTest(TestCase):

    def test_three_success_when_data(self):
        def _():
            return [0, 1, 2]

        clear()
        data(name='three')(_)
        test(data_provider='three')(_fn)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(3, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(3, TestSuite.get_instance().tests_count())

    def test_three_success_one_failed_when_data(self):
        def _():
            return [0, 1, 2, 3]

        clear()
        data(name='four')(_)
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
        data(name='three')(return2)
        test(timeout=1, data_provider="three")(data_time)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(3, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(3, TestSuite.get_instance().tests_count())

    def test_timeout_failed_with_data(self):
        clear()
        data(name='three')(return2)
        test(timeout=1, data_provider="three")(long_data)
        start(listener=Listener(0))
        self.assertEqual(3, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(3, TestSuite.get_instance().tests_count())

    def test_soft_ok(self):
        clear()
        test(sa_ok)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_soft_failed(self):
        clear()
        test(sa_failed)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_short(self):
        self.assertTrue(len(short(list(range(50)))) <= 55)

    def test_parallel(self):
        clear()
        test(groups=('one',))(half_second)
        test(groups=('two',))(half_second)
        st = time()
        start(listener=Listener(0), threads=2)
        self.assertTrue(time() - st < 1)

    def test_mock_print(self):
        a_list = []
        with mock_builtins('print', lambda x: a_list.append(x)):
            print(1)
        self.assertEqual([1], a_list)

    def test_mock_builtins_failed(self):
        with self.assertRaises(TestBrokenException):
            with mock_builtins('wrong', lambda: 10):
                pass

    def test_mock_math_abs(self):
        with mock(math, 'fabs', lambda x: 10):
            x = math.fabs(1234)
            self.assertEqual(10, x)

    def test_mock_failed(self):
        with self.assertRaises(TestBrokenException):
            with mock(math, 'wrong', lambda: 10):
                pass

    def test_mock_failed_if_not_module(self):
        with self.assertRaises(TestBrokenException):
            with mock('1', 'wrong', lambda: 10):
                pass

    def test_is_run_if_only_true(self):
        clear()
        test(only_if=lambda: True)(sa_ok)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_is_not_run_if_only_false(self):
        clear()
        test(only_if=lambda: False)(sa_ok)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(1, len(TestSuite.get_instance().ignored()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_ignored_on_sys_exit(self):
        clear()

        def exit_():
            import sys
            sys.exit(1)

        test(exit_)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(1, len(TestSuite.get_instance().ignored()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_name_filter(self):
        clear()
        test(name='one')(sa_ok)
        test(name='ane')(sa_ok)
        start(listener=Listener(0), filter_by_name='on')
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(1, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(0, len(TestSuite.get_instance().ignored()))
        self.assertEqual(1, TestSuite.get_instance().tests_count())

    def test_name_filter_empty(self):
        clear()
        test(name='one')(sa_ok)
        test(name='ane')(sa_ok)
        start(listener=Listener(0), filter_by_name='empty')
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(0, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(0, len(TestSuite.get_instance().ignored()))
        self.assertEqual(0, TestSuite.get_instance().tests_count())


if __name__ == '__main__':
    main()
