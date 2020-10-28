from unittest import TestCase, main

from checking.annotations import *
from checking.exceptions import *
from tests.fixture_behaviour_test import clear


class Klass:
    def method(self):
        pass


def valid_test_zero_arg():
    pass


def invalid_multiarg_test(a, b):
    pass


def valid_provider():
    return [1, 2, 3]


def invalid_provider():
    pass


class TestAnnotationMessages(TestCase):

    def test_test_only_if_guard_fails(self):
        clear()
        with self.assertRaises(ValueError) as e:
            test(valid_test_zero_arg, only_if=1)

        self.assertEqual(
            e.exception.args[0],
            "'only_if' parameter for '@test' decorator must be a callable returning <bool>."
        )

    def test_test_group_guard_fails(self):
        clear()
        with self.assertRaises(ValueError) as e:
            test(valid_test_zero_arg, groups='a')

        self.assertEqual(
            e.exception.args[0],
            "'group' parameter for '@test' decorator must be a tuple of strings <Tuple[str]>."
        )

    def test_provider_function_guard_fails(self):
        clear()
        with self.assertRaises(WrongDecoratedObject) as e:
            provider(invalid_provider)

        self.assertEqual(
            e.exception.args[0],
            "Function marked with '@provider' decorator must yield or return an <Iterable>."
        )

    def test_provider_duplicate_name_guard_fails(self):
        with self.assertRaises(DuplicateProviderNameException) as e:
            provider(valid_provider)
            provider(valid_provider)

        self.assertEqual(
            e.exception.args[0],
            "Provider named 'valid_provider' already exists. Provider names must be unique."
        )

    def test_test_decorator_class_guard_fails(self):
        clear()
        with self.assertRaises(WrongDecoratedObject) as e:
            test(Klass)

        self.assertEqual(
            e.exception.args[0],
            "Decorator 'test' must only be used with zero parameter functions. "
            "Classes, class methods and multi-parameter functions are not allowed."
        )

    def test_test_decorator_class_method_guard_fails(self):
        clear()
        with self.assertRaises(WrongDecoratedObject) as e:
            test(Klass.method)

        self.assertEqual(
            e.exception.args[0],
            "Decorator 'test' must only be used with zero parameter functions. "
            "Classes, class methods and multi-parameter functions are not allowed."
        )

    def test_test_decorator_high_arity_function_guard_fails(self):
        clear()
        with self.assertRaises(WrongDecoratedObject) as e:
            test(invalid_multiarg_test)

        self.assertEqual(
            e.exception.args[0],
            "Decorator 'test' must only be used with zero parameter functions. "
            "Classes, class methods and multi-parameter functions are not allowed."
        )

    def test_provider_decorator_zero_arg_function_guard_fails(self):
        clear()
        provider(valid_provider)
        with self.assertRaises(WrongDecoratedObject) as e:
            test(valid_test_zero_arg, data_provider='valid_provider')

        self.assertEqual(
            e.exception.args[0],
            "Test named 'valid_test_zero_arg' uses a data provider, but takes no arguments."
        )

    def test_provider_decorator_multi_arg_function_guard_fails(self):
        clear()
        provider(valid_provider)
        with self.assertRaises(WrongDecoratedObject) as e:
            test(invalid_multiarg_test, data_provider='valid_provider')

        self.assertEqual(
            e.exception.args[0],
            "Test named 'invalid_multiarg_test' uses a data provider, but takes more than one argument."
        )

    def test_provider_data_file_guard_fails(self):
        clear()

        file_path = 'dummy.txt'
        with self.assertRaises(FileNotFoundError) as e:
            DATA_FILE(file_path)

        # hack, circumvents different behavior for Windows and Linux
        self.assertIn('Data source file ', e.exception.args[0])
        self.assertIn(file_path, e.exception.args[0])
        self.assertIn(' not found.', e.exception.args[0])


if __name__ == '__main__':
    main()
