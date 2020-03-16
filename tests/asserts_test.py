from unittest import main, TestCase

from atest.asserts import *
from atest.exceptions import TestBrokenException, ExceptionWrapper


class AssertsTest(TestCase):

    def test_equals_ok(self):
        equals(1, 1)

    def test_equals_failed(self):
        with self.assertRaises(AssertionError) as e:
            equals(1, 2)
        self.assertEqual('Expected "1" <int>, but got "2"<int>!', e.exception.args[0])

    def test_equals_failed_with_message(self):
        with self.assertRaises(AssertionError) as e:
            equals(1, 2, 'message')
        self.assertEqual('message\nExpected "1" <int>, but got "2"<int>!', e.exception.args[0])

    def test_is_none_ok(self):
        is_none(None)

    def test_is_none_failed(self):
        with self.assertRaises(AssertionError) as e:
            is_none(1)
        self.assertEqual('Object 1<int> is not None!', e.exception.args[0])

    def test_is_none_failed_with_message(self):
        with self.assertRaises(AssertionError) as e:
            is_none(1, 'message')
        self.assertEqual('message\nObject 1<int> is not None!', e.exception.args[0])

    def test_not_none_ok(self):
        not_none(1)

    def test_not_none_failed(self):
        with self.assertRaises(AssertionError) as e:
            not_none(None)
        self.assertEqual('Unexpected None!', e.exception.args[0])

    def test_not_none_failed_with_message(self):
        with self.assertRaises(AssertionError) as e:
            not_none(None, 'message')
        self.assertEqual('message\nUnexpected None!', e.exception.args[0])

    def test_waiting_exception_with_BaseException_failed(self):
        with self.assertRaises(TestBrokenException) as e:
            with waiting_exception(BaseException):
                pass
        self.assertEqual('You must use concrete exception, except of BaseException!', e.exception.args[0])

    def test_waiting_exception_with_not_Exception_failed(self):
        with self.assertRaises(TestBrokenException) as e:
            with waiting_exception('wrong'):
                pass
        self.assertEqual('Exception or its subclasses expected, but got "wrong"<str>', e.exception.args[0])

    def test_waiting_exception_ok_with_Exception(self):
        with waiting_exception(Exception) as e:
            x = 1 / 0
        self.assertEqual(e.message, 'division by zero')
        self.assertEqual(type(e.value.__class__), type(ZeroDivisionError))

    def test_waiting_exception_ok_with_concrete_exception(self):
        with waiting_exception(ZeroDivisionError) as e:
            x = 1 / 0
        self.assertEqual(e.message, 'division by zero')
        self.assertEqual(type(e.value.__class__), type(ZeroDivisionError))

    def test_waiting_exception_with_wrong_Exception_failed(self):
        with self.assertRaises(AssertionError) as e:
            with waiting_exception(ZeroDivisionError):
                int('a')
        self.assertEqual("Expect <class 'ZeroDivisionError'>, but raised ValueError"
                         " (\"invalid literal for int() with base 10: 'a'\")", e.exception.args[0])

    def test_waiting_exception_with_no_Exception_failed(self):
        with self.assertRaises(ExceptionWrapper) as e:
            with waiting_exception(ZeroDivisionError):
                pass
        self.assertEqual("Expect exception, but none raised!", e.exception.args[0])

    def test_failing_test_default(self):
        with self.assertRaises(AssertionError) as e:
            test_fail()
        self.assertEqual("Test was forcibly failed!", e.exception.args[0])

    def test_failing_test_with_message(self):
        with self.assertRaises(AssertionError) as e:
            test_fail('message')
        self.assertEqual("message", e.exception.args[0])

    def test_braking_test_default(self):
        with self.assertRaises(TestBrokenException) as e:
            test_brake()
        self.assertEqual("Test was forcibly broken!", e.exception.args[0])

    def test_braking_test_with_message(self):
        with self.assertRaises(TestBrokenException) as e:
            test_brake('message')
        self.assertEqual("message", e.exception.args[0])

    def test_no_exception_expected_ok(self):
        with no_exception_expected():
            pass

    def test_no_exception_expected_failed(self):
        with self.assertRaises(AssertionError) as e:
            with no_exception_expected():
                raise ValueError('message')
        self.assertEqual("Expect no exception, but raised ValueError (\"message\")", e.exception.args[0])

    def test_contains_ok_for_str(self):
        contains('1', '123')

    def test_contains_ok_for_list(self):
        contains('1', ['1', '2'])

    def test_contains_ok_for_tuple(self):
        contains('1', ('123', '1'))

    def test_contains_ok_for_dict(self):
        contains('1', {'1': 1})

    def test_contains_failed_for_None(self):
        with self.assertRaises(TestBrokenException) as e:
            contains('1', None)
        self.assertEqual("\"None\"<NoneType> is not iterable and cant be check for contains!", e.exception.args[0])

    def test_contains_failed_for_not_iterable(self):
        with self.assertRaises(TestBrokenException) as e:
            contains('1', 1)
        self.assertEqual("\"1\"<int> is not iterable and cant be check for contains!", e.exception.args[0])

    def test_contains_failed_if_not_contains_str(self):
        with self.assertRaises(AssertionError) as e:
            contains('1', '234')
        self.assertEqual("Object \"1\" <str>, is not part of \"234\"<str>!", e.exception.args[0])

    def test_contains_failed_if_not_contains_list(self):
        with self.assertRaises(AssertionError) as e:
            contains('1', [2, 3])
        self.assertEqual("Object \"1\" <str>, is not part of \"[2, 3]\"<list>!", e.exception.args[0])

    def test_contains_failed_if_wrong_types(self):
        with self.assertRaises(TestBrokenException) as e:
            contains(1, '123')
        self.assertEqual("Object \"1\" <int> and \"123\"<str> are of different types and cant be check for contains!",
                         e.exception.args[0])

    def test_is_true(self):
        is_true(True)
        is_true(1 == 1)
        is_true([1, 2])

    def test_is_true_failed(self):
        with self.assertRaises(AssertionError):
            is_true(False)

    def test_is_false(self):
        is_false(False)
        is_false(1 == 2)
        is_false([])

    def is_false_failed(self):
        with self.assertRaises(AssertionError):
            is_false(True)


if __name__ == '__main__':
    main()
