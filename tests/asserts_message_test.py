from unittest import main, TestCase

from checking.asserts import *
from checking.context import *
from checking.exceptions import TestBrokenException, ExceptionWrapper


class AssertsTest(TestCase):

    def test_is_true(self):
        with self.assertRaises(AssertionError) as e:
            is_true(False)
        self.assertEqual(
            e.exception.args[0],
            'Expected: True'
            '\nActual  : False'
        )

    def test_is_true_with_message(self):
        with self.assertRaises(AssertionError) as e:
            is_true(False, 'should be true')
        self.assertEqual(
            e.exception.args[0],
            'should be true'
            '\nExpected: True'
            '\nActual  : False'
        )

    def test_is_false(self):
        with self.assertRaises(AssertionError) as e:
            is_false(True)
        self.assertEqual(
            e.exception.args[0],
            'Expected: False'
            '\nActual  : True'
        )

    def test_is_false_with_message(self):
        with self.assertRaises(AssertionError) as e:
            is_false(True, 'should be false')
        self.assertEqual(
            e.exception.args[0],
            'should be false'
            '\nExpected: False'
            '\nActual  : True'
        )

    def test_equals_string(self):
        with self.assertRaises(AssertionError) as e:
            equals('1', '2')
        self.assertEqual(
            e.exception.args[0],
            "Diff at element index 0:"
            "\n    first  value='1' <str>"
            "\n    second value='2' <str>"
            "\nObjects are not equal:"
            "\nExpected: '1' <str>"
            "\nActual  : '2' <str>"
        )

    def test_equals_long_string(self):
        with self.assertRaises(AssertionError) as e:
            equals('11', '12')
        self.assertEqual(
            e.exception.args[0],
            "Diff at element index 1:"
            "\n    first  value='1' <str>"
            "\n    second value='2' <str>"
            "\nObjects are not equal:"
            "\nExpected: '11' <str>"
            "\nActual  : '12' <str>"
        )

    def test_equals_number(self):
        with self.assertRaises(AssertionError) as e:
            equals(1.1, 1.2)
        self.assertEqual(
            e.exception.args[0],
            "Objects are not equal:"
            "\nExpected: '1.1' <float>"
            "\nActual  : '1.2' <float>"
        )

    def test_equals_mismatched_type(self):
        with self.assertRaises(AssertionError) as e:
            equals(1, '1')
        self.assertEqual(
            e.exception.args[0],
            "Objects are not equal:"
            "\nExpected: '1' <int>"
            "\nActual  : '1' <str>"
        )

    def test_equals_mismatched_length(self):
        with self.assertRaises(AssertionError) as e:
            equals('1', '11')
        self.assertEqual(
            e.exception.args[0],
            "Length of '1' <str> == 1 but length of '11' <str> == 2"
            "\nObjects are not equal:"
            "\nExpected: '1' <str>"
            "\nActual  : '11' <str>"
        )

    def test_equals_set(self):
        with self.assertRaises(AssertionError) as e:
            equals({1, 2}, {1, 3})
        self.assertEqual(
            e.exception.args[0],
            "Different elements in two sets: {2, 3}"
            "\nObjects are not equal:"
            "\nExpected: '{1, 2}' <set>"
            "\nActual  : '{1, 3}' <set>"
        )

    def test_equals_dict_missing_key(self):
        with self.assertRaises(AssertionError) as e:
            equals({1: 1, 2: 2}, {1: 1, 3: 3})
        self.assertEqual(
            e.exception.args[0],
            "Dict {1: 1, 3: 3} has no key='2' <int>, but contains key(s) {3}"
            "\nObjects are not equal:"
            "\nExpected: '{1: 1, 2: 2}' <dict>"
            "\nActual  : '{1: 1, 3: 3}' <dict>"
        )

    def test_equals_dict_wrong_value(self):
        with self.assertRaises(AssertionError) as e:
            equals({1: 1, 2: 2, 3: 3}, {1: 1, 2: 3, 3: 4})
        self.assertEqual(
            e.exception.args[0],
            "Diff in entry under key='2' <int>:"
            "\n    first  value='2' <int>" 
            "\n    second value='3' <int>"
            "\nObjects are not equal:"
            "\nExpected: '{1: 1, 2: 2, 3: 3}' <dict>"
            "\nActual  : '{1: 1, 2: 3, 3: 4}' <dict>"
        )

    def test_equals_list_mismatched_type(self):
        with self.assertRaises(AssertionError) as e:
            equals([1, 2], [1, '2'])
        self.assertEqual(
            e.exception.args[0],
            "Different types at element index 1:"
            "\n    first  value='2' <int>" 
            "\n    second value='2' <str>"
            "\nObjects are not equal:"
            "\nExpected: '[1, 2]' <list>"
            "\nActual  : '[1, '2']' <list>"
        )

    def test_equals_with_message(self):
        with self.assertRaises(AssertionError) as e:
            equals('1', '2', 'should be equal')
        self.assertEqual(
            e.exception.args[0],
            "should be equal"
            "\nDiff at element index 0:"
            "\n    first  value='1' <str>"
            "\n    second value='2' <str>"
            "\nObjects are not equal:"
            "\nExpected: '1' <str>"
            "\nActual  : '2' <str>"
        )

    def test_not_equals(self):
        with self.assertRaises(AssertionError) as e:
            not_equals('1', '1')
        self.assertEqual(
            e.exception.args[0],
            "Objects are equal:"
            "\nExpected: 1"
            "\nActual  : 1"
        )

    def test_not_equals_with_message(self):
        with self.assertRaises(AssertionError) as e:
            not_equals('1', '1', 'should not be equal')
        self.assertEqual(
            e.exception.args[0],
            "Objects are equal:"
            "\nExpected: 1"
            "\nActual  : 1"
        )

    def test_is_none(self):
        with self.assertRaises(AssertionError) as e:
            is_none('1')
        self.assertEqual(e.exception.args[0], "Object '1' <str> is not None!")

    def test_is_none_with_message(self):
        with self.assertRaises(AssertionError) as e:
            is_none('1', 'should be None')
        self.assertEqual(e.exception.args[0], "should be None\nObject '1' <str> is not None!")

    def test_is_not_none(self):
        with self.assertRaises(AssertionError) as e:
            is_not_none(None)
        self.assertEqual(e.exception.args[0], "Unexpected None!")

    def test_is_not_none_with_message(self):
        with self.assertRaises(AssertionError) as e:
            is_not_none(None, 'should not be None')
        self.assertEqual(e.exception.args[0], "should not be None\nUnexpected None!")

    def test_fail(self):
        with self.assertRaises(AssertionError) as e:
            test_fail()
        self.assertEqual(e.exception.args[0], "Test was failed intentionally!")

    def test_fail_with_message(self):
        with self.assertRaises(AssertionError) as e:
            test_fail('failed because reasons')
        self.assertEqual(e.exception.args[0], "failed because reasons")

    def test_break(self):
        with self.assertRaises(TestBrokenException) as e:
            test_break()
        self.assertEqual(e.exception.args[0], "Test was broken intentionally!")

    def test_break_with_message(self):
        with self.assertRaises(TestBrokenException) as e:
            test_break('broken because reasons')
        self.assertEqual(e.exception.args[0], "broken because reasons")

    def test_skip(self):
        with self.assertRaises(SkipTestException) as e:
            test_skip()
        self.assertEqual(e.exception.args[0], "Test was ignored intentionally!")

    def test_skip_with_message(self):
        with self.assertRaises(SkipTestException) as e:
            test_skip('skipped because reasons')
        self.assertEqual(e.exception.args[0], "skipped because reasons")

    def test_contains(self):
        with self.assertRaises(AssertionError) as e:
            contains('1', '234')
        self.assertEqual(e.exception.args[0], "Object '234' <str> doesn't contain object '1' <str>!")

    def test_contains_with_message(self):
        with self.assertRaises(AssertionError) as e:
            contains('1', '234', 'should present in')
        self.assertEqual(e.exception.args[0], "should present in\nObject '234' <str> doesn't contain object '1' <str>!")

    def test_contains_contains_no_action(self):
        contains('1', '1234')

    def test_not_contains_contains_no_action(self):
        with self.assertRaises(TestBrokenException) as e:
            not_contains(1, '1234')
        self.assertEqual(
            e.exception.args[0],
            "Cannot execute 'contains' check, incompatible objects:"
            "\nPart : '1' <int>"
            "\nWhole: '1234' <str>"
        )

    def test_contains_broken(self):
        with self.assertRaises(TestBrokenException) as e:
            contains('1', 2)
        self.assertEqual(
            e.exception.args[0],
            "Cannot execute 'contains' check, 'whole' is not an iterable:"
            "\nWhole: '2' <int>"
        )

    def test_contains_broken_with_message(self):
        with self.assertRaises(TestBrokenException) as e:
            contains('1', 2, 'should present in')
        self.assertEqual(
            e.exception.args[0],
            "Cannot execute 'contains' check, 'whole' is not an iterable:"
            "\nWhole: '2' <int>"
        )

    def test_not_contains(self):
        with self.assertRaises(AssertionError) as e:
            not_contains('1', '1234')
        self.assertEqual(e.exception.args[0], "Object '1234' <str> contains object '1' <str>!")

    def test_not_contains_with_message(self):
        with self.assertRaises(AssertionError) as e:
            not_contains('1', '1234', 'should not be in')
        self.assertEqual(e.exception.args[0], "should not be in\nObject '1234' <str> contains object '1' <str>!")

    def test_not_contains_broken(self):
        with self.assertRaises(TestBrokenException) as e:
            not_contains('1', 2)
        self.assertEqual(
            e.exception.args[0],
            "Cannot execute 'contains' check, 'whole' is not an iterable:"
            "\nWhole: '2' <int>"
        )

    def test_not_contains_broken_with_message(self):
        with self.assertRaises(TestBrokenException) as e:
            not_contains('1', 2, 'should not be in')
        self.assertEqual(
            e.exception.args[0],
            "Cannot execute 'contains' check, 'whole' is not an iterable:"
            "\nWhole: '2' <int>"
        )

    def test_is_zero(self):
        with self.assertRaises(AssertionError) as e:
            is_zero(1)
        self.assertEqual(e.exception.args[0], "'1' <int> is not equal to zero!")

    def test_is_positive_number(self):
        with self.assertRaises(AssertionError) as e:
            is_positive(-1)
        self.assertEqual(e.exception.args[0], "'-1' <int> is not positive!")

    def test_is_positive_sequence(self):
        with self.assertRaises(AssertionError) as e:
            is_positive([])
        self.assertEqual(e.exception.args[0], "Length of '[]' <list> is not positive!")

    def test_is_negative(self):
        with self.assertRaises(AssertionError) as e:
            is_negative(1)
        self.assertEqual(e.exception.args[0], "'1' <int> is not negative!")

    def test_is_empty(self):
        with self.assertRaises(AssertionError) as e:
            is_empty([1])
        self.assertEqual(e.exception.args[0], "'[1]' <list> is not empty!")

    def test_is_empty_with_message(self):
        with self.assertRaises(AssertionError) as e:
            is_empty([1], 'should be empty')
        self.assertEqual(e.exception.args[0], "should be empty\n'[1]' <list> is not empty!")

    def test_is_empty_broken(self):
        with self.assertRaises(TestBrokenException) as e:
            is_empty(1)
        self.assertEqual(e.exception.args[0], "'1' <int> has no len and cant be checked for emptiness!")

    def test_is_empty_broken_with_message(self):
        with self.assertRaises(TestBrokenException) as e:
            is_empty(1, 'should be empty')
        self.assertEqual(e.exception.args[0], "'1' <int> has no len and cant be checked for emptiness!")

    def test_is_not_empty(self):
        with self.assertRaises(AssertionError) as e:
            is_not_empty([])
        self.assertEqual(e.exception.args[0], "'[]' <list> is empty!")

    def test_is_not_empty_with_message(self):
        with self.assertRaises(AssertionError) as e:
            is_not_empty([], 'should not be empty')
        self.assertEqual(e.exception.args[0], "should not be empty\n'[]' <list> is empty!")

    def test_is_not_empty_broken(self):
        with self.assertRaises(TestBrokenException) as e:
            is_not_empty(1)
        self.assertEqual(e.exception.args[0], "'1' <int> has no len and cant be checked for emptiness!")

    def test_is_not_empty_broken_with_message(self):
        with self.assertRaises(TestBrokenException) as e:
            is_not_empty(1, 'should not be empty')
        self.assertEqual(e.exception.args[0], "'1' <int> has no len and cant be checked for emptiness!")


if __name__ == '__main__':
    main()
