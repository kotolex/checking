from unittest import main, TestCase

from checking.classes.soft_assert import SoftAssert
from checking.asserts import *

count = 0


def raise_count():
    global count
    count += 1
    return True


class SoftAssertTest(TestCase):

    def test_do_nothing_if_empty(self):
        soft = SoftAssert()
        soft.assert_all()

    def test_do_nothing_if_empty_flag(self):
        soft = SoftAssert(check_immediately=True)
        soft.assert_all()

    def test_not_fail_if_error_without_assert_all(self):
        soft = SoftAssert()
        soft.check(lambda: equals(1, 2))

    def test_not_fail_if_error_without_assert_all_flag(self):
        soft = SoftAssert(check_immediately=True)
        soft.check(lambda: equals(1, 2))

    def test_raise_on_assert_all(self):
        with self.assertRaises(AssertionError):
            soft = SoftAssert()
            soft.check(lambda: equals(1, 2))
            soft.assert_all()

    def test_raise_on_assert_all_flag(self):
        with self.assertRaises(AssertionError):
            soft = SoftAssert(check_immediately=True)
            soft.check(lambda: equals(1, 2))
            soft.assert_all()

    def test_not_raise_on_assert_all(self):
        soft = SoftAssert()
        soft.check(lambda: equals(1, 1))
        soft.assert_all()

    def test_not_raise_on_assert_all_flag(self):
        soft = SoftAssert(check_immediately=True)
        soft.check(lambda: equals(1, 1))
        soft.assert_all()

    def test_raises_if_not_lambda(self):
        soft = SoftAssert()
        with self.assertRaises(TestBrokenException):
            soft.check(equals(1, 1))

    def test_raises_if_not_lambda_flag(self):
        soft = SoftAssert(check_immediately=True)
        with self.assertRaises(TestBrokenException):
            soft.check(equals(1, 1))

    def test_without_flag_do_calc_after(self):
        count_ = count
        soft = SoftAssert()
        soft.check(lambda: raise_count())
        self.assertEqual(count_, count)
        soft.assert_all()
        self.assertEqual(count_ + 1, count)

    def test_with_flag_do_calc_before(self):
        count_ = count
        soft = SoftAssert(check_immediately=True)
        soft.check(lambda: raise_count())
        self.assertEqual(count_ + 1, count)
        soft.assert_all()
        self.assertEqual(count_ + 1, count)

    def test_equals_ok(self):
        soft = SoftAssert()
        soft.equals(1, 1)
        soft.assert_all()

    def test_equals_failed(self):
        soft = SoftAssert()
        soft.equals(1, 2)
        with self.assertRaises(AssertionError):
            soft.assert_all()

    def test_is_none_ok(self):
        soft = SoftAssert()
        soft.is_none(None)
        soft.assert_all()

    def test_is_none_failed(self):
        soft = SoftAssert()
        soft.is_none(1)
        with self.assertRaises(AssertionError):
            soft.assert_all()

    def test_not_none_ok(self):
        soft = SoftAssert()
        soft.not_none(1)
        soft.assert_all()

    def test_not_none_failed(self):
        soft = SoftAssert()
        soft.not_none(None)
        with self.assertRaises(AssertionError):
            soft.assert_all()

    def test_contains_ok(self):
        soft = SoftAssert()
        soft.contains(1, [1, 2])
        soft.assert_all()

    def test_contains_failed(self):
        soft = SoftAssert()
        soft.contains(2, [1, 0])
        with self.assertRaises(AssertionError):
            soft.assert_all()

    def test_not_contains_ok(self):
        soft = SoftAssert()
        soft.not_contains(3, [1, 2])
        soft.assert_all()

    def test_not_contains_failed(self):
        soft = SoftAssert()
        soft.not_contains(2, [1, 2])
        with self.assertRaises(AssertionError):
            soft.assert_all()

    def test_is_true_ok(self):
        soft = SoftAssert()
        soft.is_true(1)
        soft.assert_all()

    def test_is_true_failed(self):
        soft = SoftAssert()
        soft.is_true(0)
        with self.assertRaises(AssertionError):
            soft.assert_all()

    def test_is_false_ok(self):
        soft = SoftAssert()
        soft.is_false(0)
        soft.assert_all()

    def test_is_false_failed(self):
        soft = SoftAssert()
        soft.is_false(1)
        with self.assertRaises(AssertionError):
            soft.assert_all()


if __name__ == '__main__':
    main()
