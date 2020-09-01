from unittest import main, TestCase

from checking.classes.fluent_assert import verify
from checking.exceptions import TestBrokenException


class FluentAssertTest(TestCase):

    def test_is_a_ok(self):
        verify(1).same_as(1)
        verify('a').same_as('a')
        a_l = []
        verify(a_l).same_as(a_l)

    def test_is_a_fail(self):
        with self.assertRaises(AssertionError):
            verify(1).same_as(2)

    def test_is_not_ok(self):
        verify(1).not_same_as(2)
        verify(True).not_same_as(False)

    def test_is_not_failed(self):
        with self.assertRaises(AssertionError):
            a_l = []
            verify(a_l).not_same_as(a_l)

    def test_is_none(self):
        verify(None).is_none()

    def test_is_none_failed(self):
        with self.assertRaises(AssertionError):
            verify(1).is_none()

    def test_is_not_none(self):
        verify(1).is_not_none()

    def test_is_not_none_failed(self):
        with self.assertRaises(AssertionError):
            verify(None).is_not_none()

    def test_equal(self):
        verify(1).equal(1)

    def test_equal_failed(self):
        with self.assertRaises(AssertionError):
            verify(1).equal(2)

    def test_not_equal(self):
        verify(1).not_equal(2)

    def test_not_equal_failed(self):
        with self.assertRaises(AssertionError):
            verify(1).not_equal(1)

    def test_less_than(self):
        verify(1).less_than(2)

    def test_less_than_failed(self):
        with self.assertRaises(AssertionError):
            verify(2).less_than(1)

    def test_less_than_failed_if_equal(self):
        with self.assertRaises(AssertionError):
            verify(2).less_than(2)

    def test_less_than_broken(self):
        with self.assertRaises(TestBrokenException):
            verify(2).less_than('1')

    def test_greater_than(self):
        verify(1).greater_than(0)

    def test_greater_than_failed(self):
        with self.assertRaises(AssertionError):
            verify(2).greater_than(3)

    def test_greater_than_failed_if_equal(self):
        with self.assertRaises(AssertionError):
            verify(2).greater_than(2)

    def test_greater_than_broken(self):
        with self.assertRaises(TestBrokenException):
            verify(2).greater_than('1')

    def test_length_equal(self):
        verify([]).size.equal(0)

    def test_length_equal_failed(self):
        with self.assertRaises(AssertionError):
            verify([]).size.equal(1)

    def test_length_equal_broken(self):
        with self.assertRaises(TestBrokenException):
            verify(2).size.equal(2)

    def test_length_equal_broken_not_int(self):
        with self.assertRaises(TestBrokenException):
            verify([1]).size.equal_to_length_of(2)

    def test_length_equal_to_length_of(self):
        verify([1]).size.equal_to_length_of([2])

    def test_length_equal_to_length_of_failed(self):
        with self.assertRaises(AssertionError):
            verify([1]).size.equal_to_length_of([2, 3])

    def test_length_equal_to_length_of_broken(self):
        with self.assertRaises(TestBrokenException):
            verify([1]).size.equal_to_length_of(2)

    def test_is_sorted(self):
        verify([1, 2, 3]).is_sorted()

    def test_is_sorted_eq(self):
        verify([1, 2, 3, 3, 4, 4, 5]).is_sorted()

    def test_is_sorted_reverse(self):
        verify([3, 2, 1]).is_sorted(reverse_order=True)

    def test_is_sorted_reverse_long(self):
        verify([3, 2, 2, 1, 1, 1]).is_sorted(reverse_order=True)

    def test_is_sorted_failed(self):
        with self.assertRaises(AssertionError):
            verify([1, 3, 2, 3]).is_sorted()

    def test_is_sorted_failed_reverse(self):
        with self.assertRaises(AssertionError):
            verify([3, 2, 3]).is_sorted(reverse_order=True)

    def test_is_sorted_broken(self):
        with self.assertRaises(TestBrokenException):
            verify({3, 2, 3}).is_sorted(reverse_order=True)

    def test_contains_in_any_order(self):
        verify([1, 2, 3, 4]).contains_in_any_order([2, 4])

    def test_contains_in_any_order_str(self):
        verify('test').contains_in_any_order('es')

    def test_contains_in_any_order_failed(self):
        with self.assertRaises(AssertionError):
            verify([1, 2, 3, 4]).contains_in_any_order([5, 7])

    def test_child_of(self):
        verify(True).child_of(int)

    def test_child_of_same(self):
        verify(True).child_of(bool)

    def test_child_of_failed(self):
        with self.assertRaises(AssertionError):
            verify(True).child_of(str)

    def test_not_contains(self):
        verify('12').not_contains('3')

    def test_not_contains_list(self):
        verify([1, 2, 3]).not_contains(5)

    def test_not_contains_failed(self):
        with self.assertRaises(AssertionError):
            verify('12').not_contains('2')

    def test_not_contains_broken(self):
        with self.assertRaises(TestBrokenException):
            verify('12').not_contains(2)

    def test_length_less_than_length_of(self):
        verify([1]).size.less_than_length_of([1, 2])

    def test_length_less_than_length_of_failed(self):
        with self.assertRaises(AssertionError):
            verify([1, 2, 3]).size.less_than_length_of([1, 2])

    def test_length_less_than_length_of_failed_if_equal(self):
        with self.assertRaises(AssertionError):
            verify([1, 2]).size.less_than_length_of([1, 2])

    def test_length_less_than_length_of_broken(self):
        with self.assertRaises(TestBrokenException):
            verify([1, 2]).size.less_than_length_of(1)

    def test_length_less_than(self):
        verify([1]).size.less_than(2)

    def test_length_less_than_failed_if_equal(self):
        with self.assertRaises(AssertionError):
            verify([1]).size.less_than(1)

    def test_length_less_than_failed(self):
        with self.assertRaises(AssertionError):
            verify([1]).size.less_than(0)

    def test_length_less_than_broken(self):
        with self.assertRaises(TestBrokenException):
            verify([1]).size.less_than('test')

    def test_length_less_than_broken_if_no_len(self):
        with self.assertRaises(TestBrokenException):
            verify(1).size.less_than(2)

    def test_length_greater_than_length_of(self):
        verify([1]).size.greater_than_length_of([])

    def test_length_greater_than_length_of_failed(self):
        with self.assertRaises(AssertionError):
            verify([1, 2, 3]).size.greater_than_length_of([1, 2, 3])

    def test_length_greater_than_length_of_failed_if_equal(self):
        with self.assertRaises(AssertionError):
            verify([1, 2]).size.greater_than_length_of([1, 2])

    def test_length_greater_than_length_of_broken(self):
        with self.assertRaises(TestBrokenException):
            verify([1, 2]).size.greater_than_length_of(1)

    def test_length_greater_than(self):
        verify([1]).size.greater_than(0)

    def test_length_greater_than_failed_if_equal(self):
        with self.assertRaises(AssertionError):
            verify([1]).size.greater_than(1)

    def test_length_greater_than_failed(self):
        with self.assertRaises(AssertionError):
            verify([1]).size.greater_than(10)

    def test_length_greater_than_broken(self):
        with self.assertRaises(TestBrokenException):
            verify([1]).size.greater_than('test')

    def test_length_greater_than_broken_if_no_len(self):
        with self.assertRaises(TestBrokenException):
            verify(1).size.greater_than(2)

    def test_is_in_ok(self):
        verify(1).is_in([1, 2])

    def test_is_in_failed(self):
        with self.assertRaises(AssertionError):
            verify(1).is_in([2, 2])

    def test_is_not_in_ok(self):
        verify(1).is_not_in([2, 2])

    def test_is_not_in_failed(self):
        with self.assertRaises(AssertionError):
            verify(1).is_not_in([1, 2])

    def test_is_true_ok(self):
        verify(1 > 0).is_true()

    def test_is_true_failed(self):
        with self.assertRaises(AssertionError):
            verify(1 == 0).is_true()

    def test_is_false_ok(self):
        verify(1 < 0).is_false()

    def test_is_false_failed(self):
        with self.assertRaises(AssertionError):
            verify(1 == 1).is_false()

    def test_size_works(self):
        verify([1, 2]).size.equal(2)

    def test_size_failed(self):
        with self.assertRaises(TestBrokenException):
            verify(1).size

    def test_has_attribute(self):
        verify('text').has_attribute('upper')

    def test_has_attribute_failed(self):
        with self.assertRaises(AssertionError):
            verify('text').has_attribute('x')

    def test_is_empty(self):
        verify([]).is_empty()

    def test_is_not_empty(self):
        verify([1, 2]).is_not_empty()

    def test_is_zero(self):
        verify(0).is_zero()

    def test_is_positive(self):
        verify(1).is_positive()

    def test_is_positive_list(self):
        verify([1, 2]).is_positive()

    def test_is_negative(self):
        verify(-1).is_negative()

    def test_attribute(self):
        class TestClass:
            pass

        test_obj = TestClass()
        test_obj.att = 10
        verify(test_obj).attribute('att').equal(10)

    def test_attribute_failed(self):
        with self.assertRaises(AssertionError):
            verify('text').attribute('x').equal(10)

    def test_type_is(self):
        verify([1, 2]).type_is(list)
        verify('text').type_is(str)

    def test_type_is_failed(self):
        with self.assertRaises(AssertionError):
            verify('text').type_is(list)

    def test_length_less_or_equal_less(self):
        verify(1).less_or_equal_to(2)

    def test_length_less_or_equal_eq(self):
        verify(1).less_or_equal_to(1)

    def test_length_less_or_equal_failed(self):
        with self.assertRaises(AssertionError):
            verify(1).less_or_equal_to(0)

    def test_length_greater_or_equal_greater(self):
        verify(1).greater_or_equal_to(0)

    def test_length_greater_or_equal_eq(self):
        verify(1).greater_or_equal_to(1)

    def test_length_greater_or_equal_failed(self):
        with self.assertRaises(AssertionError):
            verify(1).greater_or_equal_to(2)


if __name__ == '__main__':
    main()
