from unittest import TestCase, main

from checking.classes.mocking import AttributeWrapper,Spy


class WrapperTest(TestCase):

    def test_str(self):
        wrapper = AttributeWrapper('name', Spy())
        self.assertTrue('Wrapper for method "name" on object:' in str(wrapper))

    def test_default_returns_none(self):
        wrapper = AttributeWrapper('name', Spy())
        self.assertIsNone(wrapper())

    def test_returns(self):
        wrapper = AttributeWrapper('name', Spy())
        wrapper.returns(5)
        self.assertEqual(5, wrapper())

    def test_returns_function_result(self):
        wrapper = AttributeWrapper('name', Spy())
        wrapper.use_function(bool)
        self.assertTrue(wrapper(1))

    def test_returns_value_if_specified_after_function(self):
        wrapper = AttributeWrapper('name', Spy())
        wrapper.use_function(bool)
        wrapper.returns(False)
        self.assertFalse(wrapper(1))

    def test_raises(self):
        wrapper = AttributeWrapper('name', Spy())
        wrapper.raises(ValueError, 'Message')
        with self.assertRaises(ValueError) as e:
            wrapper()

        self.assertEqual(str(e.exception), 'Message')

    def test_raises_with_condition(self):
        wrapper = AttributeWrapper('name', Spy())
        wrapper.raises_if_args(lambda x: x == 2, ValueError, 'Message')
        with self.assertRaises(ValueError) as e:
            wrapper(2)

        self.assertEqual(str(e.exception), 'Message')

    def test_raises_with_condition_not_raise_if_no_arg(self):
        wrapper = AttributeWrapper('name', Spy())
        wrapper.raises_if_args(lambda x: x == 2, ValueError, 'Message')
        wrapper()

    def test_was_called(self):
        wrapper = AttributeWrapper('name', Spy())
        self.assertFalse(wrapper.was_called())
        wrapper()
        self.assertTrue(wrapper.was_called())

    def test_call_count(self):
        wrapper = AttributeWrapper('name', Spy())
        self.assertEqual(0, wrapper.call_count())
        wrapper()
        self.assertEqual(1, wrapper.call_count())

    def test_all_calls(self):
        wrapper = AttributeWrapper('name', Spy())
        self.assertEqual([], wrapper.all_calls())
        wrapper()
        self.assertEqual([((), {})], wrapper.all_calls())


if __name__ == '__main__':
    main()
