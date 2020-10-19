from unittest import main, TestCase

from checking.asserts import *
from checking.context import *
from checking.exceptions import TestBrokenException, ExceptionWrapper


class AssertsTest(TestCase):

    def test_is_zero(self):
        is_zero(0)

    def test_is_zero_float(self):
        is_zero(0.0)

    def test_is_zero_fails_if_wrong_type(self):
        with self.assertRaises(TestBrokenException):
            is_zero("0")

    def test_is_zero_fails_if_positive(self):
        with self.assertRaises(AssertionError):
            is_zero(1)

    def test_is_zero_fails_if_negative(self):
        with self.assertRaises(AssertionError):
            is_zero(-1)

    def test_is_zero_fails_if_positive_float(self):
        with self.assertRaises(AssertionError):
            is_zero(0.1)

    def test_is_positive(self):
        is_positive(1)

    def test_is_positive_str(self):
        is_positive('1')

    def test_is_positive_list(self):
        is_positive([1, 2])

    def test_is_positive_fail(self):
        with self.assertRaises(AssertionError):
            is_positive(0)

    def test_is_positive_fail_if_not_seq(self):
        with self.assertRaises(TestBrokenException):
            is_positive((g for g in range(2)))

    def test_is_positive_fail_str(self):
        with self.assertRaises(AssertionError):
            is_positive('')

    def test_is_negative(self):
        is_negative(-1)

    def test_is_negative_float(self):
        is_negative(-0.213)

    def test_is_negative_fail_zero(self):
        with self.assertRaises(AssertionError):
            is_negative(0)

    def test_is_negative_fail(self):
        with self.assertRaises(AssertionError):
            is_negative(5)

    def test_is_negative_fail_if_wrong_type(self):
        with self.assertRaises(TestBrokenException):
            is_negative('1')

    def test_equals_ok(self):
        equals(1, 1)

    def test_equals_failed(self):
        with self.assertRaises(AssertionError) as e:
            equals(1, 2)
        self.assertEqual('Objects are not equal!\nExpected:"1" <int>\nActual  :"2" <int>!', e.exception.args[0])

    def test_equals_failed_with_message(self):
        with self.assertRaises(AssertionError) as e:
            equals(1, 2, 'message')
        self.assertEqual('message\nObjects are not equal!\nExpected:"1" <int>\nActual  :"2" <int>!',
                         e.exception.args[0])

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
        is_not_none(1)

    def test_not_none_failed(self):
        with self.assertRaises(AssertionError) as e:
            is_not_none(None)
        self.assertEqual('Unexpected None!', e.exception.args[0])

    def test_not_none_failed_with_message(self):
        with self.assertRaises(AssertionError) as e:
            is_not_none(None, 'message')
        self.assertEqual('message\nUnexpected None!', e.exception.args[0])

    def test_waiting_exception_with_BaseException_failed(self):
        with self.assertRaises(TestBrokenException) as e:
            with should_raise(BaseException):
                pass
        self.assertEqual('BaseException is forbidden, you must use concrete exception types.', e.exception.args[0])

    def test_waiting_exception_with_not_Exception_failed(self):
        with self.assertRaises(TestBrokenException) as e:
            with should_raise('wrong'):
                pass
        self.assertEqual('Expected Exception or a subclass, got "wrong"<str>', e.exception.args[0])

    def test_waiting_exception_ok_with_Exception(self):
        with should_raise(Exception) as e:
            x = 1 / 0
        self.assertEqual(e.message, 'division by zero')
        self.assertEqual(type(e.value.__class__), type(ZeroDivisionError))

    def test_waiting_exception_ok_with_concrete_exception(self):
        with should_raise(ZeroDivisionError) as e:
            x = 1 / 0
        self.assertEqual(e.message, 'division by zero')
        self.assertEqual(type(e.value.__class__), type(ZeroDivisionError))

    def test_waiting_exception_with_wrong_Exception_failed(self):
        with self.assertRaises(AssertionError) as e:
            with should_raise(ZeroDivisionError):
                int('a')
        self.assertEqual('Expected <class \'ZeroDivisionError\'>, '
                         'got ValueError ("invalid literal for int() with base 10: \'a\'")', e.exception.args[0])

    def test_waiting_exception_with_no_Exception_failed(self):
        with self.assertRaises(ExceptionWrapper) as e:
            with should_raise(ZeroDivisionError):
                pass
        self.assertEqual("Expected an exception, but none was raised!", e.exception.args[0])

    def test_failing_test_default(self):
        with self.assertRaises(AssertionError) as e:
            test_fail()
        self.assertEqual("Test was intentionally failed!", e.exception.args[0])

    def test_failing_test_with_message(self):
        with self.assertRaises(AssertionError) as e:
            test_fail('message')
        self.assertEqual("message", e.exception.args[0])

    def test_skip_test_default(self):
        with self.assertRaises(SkipTestException) as e:
            test_skip()
        self.assertEqual("Test was intentionally ignored!", e.exception.args[0])

    def test_skip_test_with_message(self):
        with self.assertRaises(SkipTestException) as e:
            test_skip('message')
        self.assertEqual("message", e.exception.args[0])

    def test_braking_test_default(self):
        with self.assertRaises(TestBrokenException) as e:
            test_break()
        self.assertEqual("Test was intentionally broken!", e.exception.args[0])

    def test_braking_test_with_message(self):
        with self.assertRaises(TestBrokenException) as e:
            test_break('message')
        self.assertEqual("message", e.exception.args[0])

    def test_no_exception_expected_ok(self):
        with no_exception_expected():
            pass

    def test_no_exception_expected_failed(self):
        with self.assertRaises(AssertionError) as e:
            with no_exception_expected():
                raise ValueError('message')
        self.assertEqual("Expect no exception, but raised ValueError (\"message\")!", e.exception.args[0])

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
        self.assertEqual("Object \"1\" <str>, is not part of \n\"234\"<str>!", e.exception.args[0])

    def test_contains_failed_if_not_contains_list(self):
        with self.assertRaises(AssertionError) as e:
            contains('1', [2, 3])
        self.assertEqual("Object \"1\" <str>, is not part of \n\"[2, 3]\"<list>!", e.exception.args[0])

    def test_contains_failed_if_wrong_types(self):
        with self.assertRaises(TestBrokenException) as e:
            contains(1, '123')
        self.assertEqual("Object \"1\" <int> and \"123\"<str> are of different types and cant be check for contains!",
                         e.exception.args[0])

    def test_is_true(self):
        is_true(True)
        is_true(1 == 1)
        is_true([1, 2])
        is_true(1)
        is_true(-1)
        is_true({'a': 1})
        is_true({1, })
        is_true(' ')

    def test_is_true_failed_false(self):
        with self.assertRaises(AssertionError):
            is_true(False)

    def test_is_true_failed_None(self):
        with self.assertRaises(AssertionError):
            is_true(None)

    def test_is_true_failed_empty_str(self):
        with self.assertRaises(AssertionError):
            is_true('')

    def test_is_true_failed_empty_list(self):
        with self.assertRaises(AssertionError):
            is_true([])

    def test_is_true_failed_zero(self):
        with self.assertRaises(AssertionError):
            is_true(0)

    def test_is_false(self):
        is_false(False)
        is_false(1 == 2)
        is_false([])
        is_false('')
        is_false(0)
        is_false(0.0)
        is_false({})
        is_false(set())
        is_false(None)

    def test_is_false_failed_true(self):
        with self.assertRaises(AssertionError):
            is_false(True)

    def test_is_false_failed_positive(self):
        with self.assertRaises(AssertionError):
            is_false(1)

    def test_is_false_failed_negative(self):
        with self.assertRaises(AssertionError):
            is_false(-1)

    def test_is_false_failed_non_empty_str(self):
        with self.assertRaises(AssertionError):
            is_false(' ')

    def test_is_false_failed_non_empty_list(self):
        with self.assertRaises(AssertionError):
            is_false([1, ])

    def test_is_false_failed_some_class(self):
        class NonNone:
            pass

        with self.assertRaises(AssertionError):
            is_false(NonNone())

    def test_is_empty(self):
        is_empty([])

    def test_is_empty_fail(self):
        with self.assertRaises(AssertionError):
            is_empty([1, ])

    def test_is_empty_broken(self):
        with self.assertRaises(TestBrokenException):
            is_empty(1)

    def test_is_not_empty(self):
        is_not_empty([1, ])

    def test_is_not_empty_fail(self):
        with self.assertRaises(AssertionError):
            is_not_empty([])

    def test_is_not_empty_broken(self):
        with self.assertRaises(TestBrokenException):
            is_not_empty(1)


if __name__ == '__main__':
    main()
