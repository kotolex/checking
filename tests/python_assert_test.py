from unittest import main, TestCase

import checking.runner as runner
from checking.annotations import *
from checking.classes.listeners.basic import Listener
from tests.fixture_behaviour_test import clear

a_list = []
_listener = Listener(0)
_listener.on_failed = lambda t, e: a_list.append(e)


class AssertTest(TestCase):

    def setUp(self) -> None:
        clear()
        a_list.clear()

    def test_assert_equal(self):
        def _():
            assert 1 == 2

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], 'Objects are not equals (1 != 2)')

    def test_assert_not_equal(self):
        def _():
            assert 1 != 1

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], 'Objects are equal (1 == 1)')

    def test_assert_greater_or_equal(self):
        def _():
            assert 1 >= 2

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], '1 is less than 2')

    def test_assert_less_or_equal(self):
        def _():
            assert 2 <= 1

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], '2 is greater than 1')

    def test_assert_greater(self):
        def _():
            assert 1 > 2

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], '1 is less or equal to 2')

    def test_assert_less(self):
        def _():
            assert 2 < 1

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], '2 is greater or equal to 1')

    def test_assert_is_not(self):
        def _():
            assert False is not False

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], 'False is False (points to one object)')

    def test_assert_is(self):
        def _():
            assert False is True

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], 'False is not True (points to different objects)')

    def test_assert_simple_not(self):
        def _():
            assert not True

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], '"not True" returns False but True was expected')

    def test_assert_simple(self):
        def _():
            assert False

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], '"False" returns False but True was expected')

    def test_assert_with_message(self):
        def _():
            assert bool(0), 'test'

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], 'test\n"bool(0)" returns False but True was expected')

    def test_assert_with_func_and_apos(self):
        def _():
            assert 'text'.replace('x', '') == 'test', 'test'

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], "test\nObjects are not equals ('text'.replace('x', '') != 'test')")

    def test_assert_with_func_and_quotes(self):
        def _():
            assert "text".replace("x", "") == "test", "test"

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], 'test\nObjects are not equals ("text".replace("x", "") != "test")')

    def test_assert_with_func_and_comma(self):
        def _():
            assert "text".replace("x", "") == ",t\'est"

        test(_)
        runner.start(listener=_listener)
        self.assertTrue(type(a_list[0]) is AssertionError)
        self.assertEqual(a_list[0].args[0], 'Objects are not equals ("text".replace("x", "") != ",t\\\'est")')


if __name__ == '__main__':
    main()
