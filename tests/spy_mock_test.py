from unittest import TestCase, main

from checking.classes.spy import Spy


class SpyTest(TestCase):

    def test_create_spy_empty(self):
        spy = Spy()

    def test_create_spy_on_str(self):
        s = 'string'
        spy = Spy(s)

    def test_can_call_empty_spy(self):
        spy = Spy()
        spy()

    def test_can_call_str_func_on_spy(self):
        s = "string"
        spy = Spy(s)
        spy.upper()

    def test_was_called_works(self):
        spy = Spy()
        self.assertFalse(spy.was_called())
        spy()
        self.assertTrue(spy.was_called())

    def test_was_called_empty_with_arg(self):
        spy = Spy()
        spy(10)
        self.assertTrue(spy.was_called())
        self.assertTrue(spy.was_called_with_argument(10))

    def test_returns_on_called_empty(self):
        spy = Spy()
        spy.when_call_returns(11)
        self.assertEqual(11, spy())

    def test_str_on_empty(self):
        spy = Spy()
        self.assertEqual('Empty Test Spy', str(spy))

    def test_str_(self):
        spy = Spy('string')
        self.assertEqual("Test spy of the \"string\" <class 'str'>", str(spy))

    def test_all_calls(self):
        spy = Spy('string')
        self.assertEqual([], spy.all_calls())
        spy.upper()
        self.assertTrue(len(spy.all_calls()) == 1)

    def test_was_func_called(self):
        spy = Spy('string')
        spy.upper()
        self.assertTrue(spy.was_function_called('upper'))

    def test_was_func_called_with_arg(self):
        spy = Spy('string')
        spy.upper(1)
        self.assertTrue(spy.was_function_with_argument_called('upper', 1))

    def test_was_exact_func_called(self):
        spy = Spy('string')
        spy.upper(1)
        self.assertTrue(spy.was_exact_function_called('upper', 1))

    def test_returns_when_func_called(self):
        spy = Spy('string')
        spy.when_call_function_returns('upper', 22)
        self.assertEqual(22, spy.upper())


if __name__ == '__main__':
    main()
