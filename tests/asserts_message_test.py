from unittest import main, TestCase

from checking.asserts import *
from checking.context import *
from checking.exceptions import TestBrokenException, ExceptionWrapper


class AssertsTest(TestCase):

    def test_is_true(self):
        with self.assertRaises(AssertionError) as e:
            is_true(False)
        self.assertEqual(e.exception.args[0], 'Expected True, but got False! ')

    def test_is_false(self):
        with self.assertRaises(AssertionError) as e:
            is_false(True)
        self.assertEqual(e.exception.args[0], 'Expected False, but got True')

    def test_equals(self):
        with self.assertRaises(AssertionError) as e:
            equals('1', '2')
        self.assertEqual(
            e.exception.args[0],
            """Diff at element with index 0:\n    first  value="1"<class 'str'>\n    second value="2"<class 'str'>\nObjects are not equal:\nExpected: "1" <str>\nActual  : "2" <str>"""
        )

    def test_not_equals(self):
        with self.assertRaises(AssertionError) as e:
            not_equals('1', '1')
        self.assertEqual(e.exception.args[0], "Objects are equal: (1, 1)!")

    def test_is_none(self):
        with self.assertRaises(AssertionError) as e:
            is_none('1')
        self.assertEqual(e.exception.args[0], "Object 1 <str> is not None!")

    def test_is_not_none(self):
        with self.assertRaises(AssertionError) as e:
            is_not_none(None)
        self.assertEqual(e.exception.args[0], "Unexpected None!")

    def test_fail_with_no_message(self):
        with self.assertRaises(AssertionError) as e:
            test_fail()
        self.assertEqual(e.exception.args[0], "Test was intentionally failed!")

    def test_fail_with_message(self):
        with self.assertRaises(AssertionError) as e:
            test_fail('failed because reasons')
        self.assertEqual(e.exception.args[0], "failed because reasons")

    def test_break_with_no_message(self):
        with self.assertRaises(TestBrokenException) as e:
            test_break()
        self.assertEqual(e.exception.args[0], "Test was intentionally broken!")

    def test_break_with_message(self):
        with self.assertRaises(TestBrokenException) as e:
            test_break('broken because reasons')
        self.assertEqual(e.exception.args[0], "broken because reasons")

    def test_skip_with_no_message(self):
        with self.assertRaises(SkipTestException) as e:
            test_skip()
        self.assertEqual(e.exception.args[0], "Test was intentionally ignored!")

    def test_skip_with_message(self):
        with self.assertRaises(SkipTestException) as e:
            test_skip('skipped because reasons')
        self.assertEqual(e.exception.args[0], "skipped because reasons")

    def test_contains(self):
        with self.assertRaises(AssertionError) as e:
            contains('1', '234')
        self.assertEqual(e.exception.args[0], 'Object "1" <str>, is not part of \n"234" <str>!')

    def test_contains_broken(self):
        with self.assertRaises(TestBrokenException) as e:
            contains('1', 2)
        self.assertEqual(e.exception.args[0], '"2"<int> is not iterable and cant be check for contains!')

    def test_not_contains(self):
        with self.assertRaises(AssertionError) as e:
            not_contains('1', '1234')
        self.assertEqual(e.exception.args[0], 'Object "1" <str>, is a part of \n"1234" <str>!')

    def test_not_contains_broken(self):
        with self.assertRaises(TestBrokenException) as e:
            not_contains('1', 2)
        self.assertEqual(e.exception.args[0], '"2"<int> is not iterable and cant be check for contains!')

    def test_is_zero(self):
        with self.assertRaises(AssertionError) as e:
            is_zero(1)
        self.assertEqual(e.exception.args[0], '"1" <int> is not equal to zero!')

    def test_is_positive_number(self):
        with self.assertRaises(AssertionError) as e:
            is_positive(-1)
        self.assertEqual(e.exception.args[0], '-1 is not positive!')

    def test_is_positive_sequence(self):
        with self.assertRaises(AssertionError) as e:
            is_positive([])
        self.assertEqual(e.exception.args[0], 'Length of "[]" <list> is not positive!')

    def test_is_negative(self):
        with self.assertRaises(AssertionError) as e:
            is_negative(1)
        self.assertEqual(e.exception.args[0], '"1" <int> is not negative!')

    def test_is_empty(self):
        with self.assertRaises(AssertionError) as e:
            is_empty([1])
        self.assertEqual(e.exception.args[0], '"[1]" <list> is not empty!')

    def test_is_not_empty(self):
        with self.assertRaises(AssertionError) as e:
            is_not_empty([])
        self.assertEqual(e.exception.args[0], '"[]" <list> is empty!')


if __name__ == '__main__':
    main()
