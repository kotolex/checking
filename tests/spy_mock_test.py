from unittest import TestCase, main

from checking.classes.mocking import Spy, Double, Call


class SpyTest(TestCase):

    def test_call_str_arg(self):
        call = Call('name', 1)
        self.assertEqual('Call of "name" with (1,), no keyword args', str(call))

    def test_call_str_arg_kwarg(self):
        call = Call('name', 1, **{"z": 1})
        self.assertEqual('Call of "name" with (1,), {\'z\': 1}', str(call))

    def test_call_equal(self):
        call = Call('name', 1)
        call2 = Call('name', 1)
        self.assertEqual(call, call2)

    def test_call_not_equal(self):
        call = Call('name', 1)
        call2 = Call('name', 2)
        self.assertNotEqual(call, call2)

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
        spy.returns(11)
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
        spy.upper.returns(22)
        self.assertEqual(22, spy.upper())

    def test_double_str(self):
        d = Double('str')
        self.assertEqual('Test Double of the "str" <class \'str\'>', str(d))

    def test_double_has_same_behaviour(self):
        d = Double('str')
        self.assertEqual('STR', d.upper())

    def test_double_record_calls(self):
        d = Double('str')
        d.upper()
        self.assertTrue(len(d.all_calls()) == 1)
        self.assertEqual(d.all_calls(), [Call('upper')])

    def test_double_replace_returns(self):
        d = Double('str')
        d.upper.returns('UPS')
        self.assertEqual('UPS', d.upper())

    def test_all_calls_args(self):
        s = Spy('str')
        s.replace('t', 'T')
        s.upper()
        s.lower(1)
        self.assertEqual([('t', 'T'), (), (1,)], s.all_calls_args())

    def test_all_calls_args_flatten(self):
        s = Spy('str')
        s.replace('t', 'T')
        s.upper()
        s.lower(1)
        self.assertEqual(['t', 'T', 1], s.all_calls_args_flatten())

    def test_call_count(self):
        s = Spy('str')
        s.upper()
        self.assertEqual(1, s.upper.call_count())
        s.lower()
        self.assertEqual(1, s.upper.call_count())
        s.upper()
        self.assertEqual(2, s.upper.call_count())

    def test_len_for_str(self):
        s = Double('str')
        self.assertEqual(3, len(s))

    def test_len_for_str_with_mock(self):
        s = Double('str')
        s.len.returns(120)
        self.assertEqual(120, len(s))

    def test_bool_for_str(self):
        s = Double('str')
        self.assertEqual(True, bool(s))

    def test_bool_for_str_with_mock(self):
        s = Double('str')
        s.bool.returns(False)
        self.assertEqual(False, bool(s))

    def test_iter_for_str(self):
        s = Double('str')
        self.assertEqual('str', ''.join(iter(s)))

    def test_iter_for_str_with_mock(self):
        s = Double('str')
        s.iter.returns(iter('test'))
        self.assertEqual('test', ''.join(iter(s)))

    def test_spy_raises(self):
        s = Spy()
        s.raises(ValueError("Text"))
        with self.assertRaises(ValueError) as e:
            s()

        self.assertEqual(str(e.exception), 'Text')


if __name__ == '__main__':
    main()
