from unittest import main, TestCase

from atest.classes.fluent_assert import FluentAssert, verify
from atest.exceptions import TestBrokenException


class FluentAssertTest(TestCase):

    def test_is_a_ok(self):
        verify(1).is_a(int)
        verify('a').is_a(str)
        verify([]).is_a(list)

    def test_is_a_fail(self):
        with self.assertRaises(AssertionError):
            verify(1).is_a(str)

    def test_is_a_fail_wrong_type(self):
        with self.assertRaises(TestBrokenException):
            verify(1).is_a(2)

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

    def test_less_than_broken(self):
        with self.assertRaises(TestBrokenException):
            verify(2).less_than('1')

    def test_greater_than(self):
        verify(1).greater_than(0)

    def test_greater_than_failed(self):
        with self.assertRaises(AssertionError):
            verify(2).greater_than(3)

    def test_greater_than_broken(self):
        with self.assertRaises(TestBrokenException):
            verify(2).greater_than('1')

    def test_length_equal(self):
        verify([]).length_equal_to(0)

    def test_length_equal_failed(self):
        with self.assertRaises(AssertionError):
            verify([]).length_equal_to(1)

    def test_length_equal_broken(self):
        with self.assertRaises(TestBrokenException):
            verify(2).length_equal_to(2)

    def test_length_equal_broken_not_int(self):
        with self.assertRaises(TestBrokenException):
            verify([1]).length_equal_to('s')

    def test_length_equal_to_length_of(self):
        verify([1]).length_equal_to_length_of([2])

    def test_length_equal_to_length_of_failed(self):
        with self.assertRaises(AssertionError):
            verify([1]).length_equal_to_length_of([2, 3])

    def test_length_equal_to_length_of_broken(self):
        with self.assertRaises(TestBrokenException):
            verify([1]).length_equal_to_length_of(2)

    def test_is_sorted(self):
        verify([1, 2, 3]).is_sorted()

    def test_is_sorted_eq(self):
        verify([1, 2, 3, 3, 4, 4, 5]).is_sorted()

    def test_is_sorted_reverse(self):
        verify([3, 2, 1]).is_sorted(reverse_order=True)

    def test_is_sorted_reverse(self):
        verify([3, 2, 2, 1, 1, 1]).is_sorted(reverse_order=True)

    def test_is_sorted_failed(self):
        with self.assertRaises(AssertionError):
            verify([1, 3, 2, 3]).is_sorted()

    def test_is_sorted_failed_reverse(self):
        with self.assertRaises(AssertionError):
            verify([3, 2, 3]).is_sorted(reverse_order=True)

    def test_contains_in_any_order(self):
        verify([1, 2, 3, 4]).contains_in_any_order([2, 4])

    def test_contains_in_any_order_str(self):
        verify('test').contains_in_any_order('es')

    def test_contains_in_any_order_failed(self):
        with self.assertRaises(AssertionError):
            verify([1, 2, 3, 4]).contains_in_any_order([5, 7])


if __name__ == '__main__':
    main()
