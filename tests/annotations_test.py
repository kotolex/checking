from unittest import TestCase, main

from checking.annotations import *
from checking.exceptions import *
from checking.classes.basic_suite import TestSuite
from checking.runner import start
from checking.classes.listeners.basic import Listener
from tests.fixture_behaviour_test import clear


def valid():
    pass


def valid_for_data():
    return [1, 2]


def valid_for_provider(arg):
    pass


def non_valid_for_provider(arg, arg1):
    pass


class T:
    def m(self):
        pass


def f():
    """Test"""
    pass


class TestAnnotations(TestCase):
    _listener = Listener(0)

    def test_valid_func_works(self):
        clear()
        initial_count = TestSuite.get_instance().tests_count()
        test(valid)
        self.assertEqual(initial_count + 1, TestSuite.get_instance().tests_count())

    def test_not_add_if_disabled(self):
        clear()
        initial_count = TestSuite.get_instance().tests_count()
        test(enabled=False)(valid)
        self.assertEqual(initial_count, TestSuite.get_instance().tests_count())

    def test_not_add_if_enabled(self):
        clear()
        initial_count = TestSuite.get_instance().tests_count()
        test(enabled=True)(valid)
        self.assertEqual(initial_count + 1, TestSuite.get_instance().tests_count())

    def test_raises_when_func_for_provider_has_no_arg(self):
        with self.assertRaises(WrongDecoratedObject) as e:
            test(data_provider="good")(valid)
        self.assertEqual("Function 'valid' marked with data_provider has no argument!", e.exception.args[0])

    def test_raises_when_no_provider(self):
        clear()
        test(data_provider="missing")(valid_for_provider)
        with self.assertRaises(UnknownProviderName) as e:
            start(TestSuite.get_instance(), listener=Listener(0))
        self.assertTrue("Cant find provider with name(s) ['missing']" in e.exception.args[0])

    def test_ignore_all_if_test_disabled(self):
        test(enabled=False, data_provider="wrong")(valid)

    def test_raises_when_using_test_with_class(self):
        with self.assertRaises(WrongDecoratedObject) as ex:
            test(T)
        self.assertTrue('test' in ex.exception.args[0])

    def test_raises_when_using_function_with_arg(self):
        with self.assertRaises(WrongDecoratedObject) as ex:
            test(valid_for_provider)
        self.assertTrue('test' in ex.exception.args[0])

    def test_raises_when_using_test_with_class_methods(self):
        with self.assertRaises(WrongDecoratedObject) as ex:
            t = T()
            test(t.m)
        self.assertTrue('test' in ex.exception.args[0])

    def test_name_param_works(self):
        clear()
        test(name='new_name')(valid)
        self.assertTrue('new_name' in [t.name for t in list(TestSuite.get_instance().groups.values())[0].tests])

    def test_raises_if_only_is_not_callable(self):
        clear()
        with self.assertRaises(ValueError):
            test(only_if=False)(valid)

    def test_data_works(self):
        clear()
        provider(name="any_name")(valid_for_data)
        self.assertTrue('any_name' in TestSuite.get_instance().providers)

    def test_data_raises_when_duplicate_name(self):
        with self.assertRaises(DuplicateNameException) as e:
            provider(valid_for_data)
            provider(valid_for_data)
        self.assertEqual('Provider with name "valid_for_data" already exists! Only unique names allowed!',
                         e.exception.args[0])

    def test_data_raises_when_two_args(self):
        def _():
            return [1, 2]

        with self.assertRaises(WrongDecoratedObject) as e:
            provider(name='another2')(_)
            test(data_provider='another2')(non_valid_for_provider)
        self.assertEqual("Function 'non_valid_for_provider' marked with data_provider has more than 1 argument!",
                         e.exception.args[0])

    def test_data_name_works(self):
        clear()
        provider(name="another")(valid_for_data)
        self.assertTrue('another' in TestSuite.get_instance().providers)

    def test_data_ignore_if_disabled(self):
        clear()
        provider(enabled=False, name="no")(valid)
        self.assertFalse('no' in TestSuite.get_instance().providers)

    def test_before_all_when_before_first(self):
        clear()
        before_ = valid
        before(before_)
        t = Test('first', print)
        list(TestSuite.get_instance().groups.values())[0].add_test(t)
        self.assertTrue(t.before)
        self.assertEqual(before_, t.before[0])

    def test_before_all_when_before_last(self):
        clear()
        t = Test('second', print)
        TestSuite.get_instance().get_or_create("new").add_test(t)
        bef = lambda: None
        before(group_name='new')(bef)
        self.assertTrue(bef in t.before)

    def test_no_timeout_default(self):
        clear()
        test(valid)
        self.assertEqual(0, list(TestSuite.get_instance().groups.values())[0].tests[0].timeout)

    def test_timeout_same(self):
        clear()
        test(timeout=10)(valid)
        self.assertEqual(10, list(TestSuite.get_instance().groups.values())[0].tests[0].timeout)

    def test_timeout_same_float(self):
        clear()
        test(timeout=10.02)(valid)
        self.assertEqual(10, list(TestSuite.get_instance().groups.values())[0].tests[0].timeout)

    def test_timeout_same_negative(self):
        clear()
        test(timeout=-1)(valid)
        self.assertEqual(0, list(TestSuite.get_instance().groups.values())[0].tests[0].timeout)

    def test_description_empty(self):
        clear()
        test(valid)
        self.assertIsNone(list(TestSuite.get_instance().groups.values())[0].tests[0].description)
        self.assertEqual('annotations_test.valid', str(list(TestSuite.get_instance().groups.values())[0].tests[0]))

    def test_description_from_param(self):
        clear()
        test(description='test')(valid)
        self.assertEqual(list(TestSuite.get_instance().groups.values())[0].tests[0].description, 'test')
        self.assertEqual("annotations_test.valid ('test')",
                         str(list(TestSuite.get_instance().groups.values())[0].tests[0]))

    def test_description_from_docs(self):
        clear()
        test(f)
        self.assertEqual(list(TestSuite.get_instance().groups.values())[0].tests[0].description, 'Test')
        self.assertEqual("annotations_test.f ('Test')", str(list(TestSuite.get_instance().groups.values())[0].tests[0]))

    def test_description_from_param_wins_docs(self):
        clear()
        test(description='test')(f)
        self.assertEqual(list(TestSuite.get_instance().groups.values())[0].tests[0].description, 'test')
        self.assertEqual("annotations_test.f ('test')", str(list(TestSuite.get_instance().groups.values())[0].tests[0]))

    def test_data_file(self):
        clear()
        DATA_FILE('test_data.txt', name='new')
        test(data_provider='new')(valid_for_provider)
        self.assertTrue('new' in TestSuite.get_instance().providers)

    def test_data_file_has_three_tests(self):
        clear()
        DATA_FILE('test_data.txt', name='new')
        test(data_provider='new')(valid_for_provider)
        start(listener=self._listener)
        self.assertEqual(3, TestSuite.tests_count())

    def test_data_file_has_three_tests_with_long_path(self):
        clear()
        DATA_FILE('files/test_data.txt', name='new')
        test(data_provider='new')(valid_for_provider)
        start(listener=self._listener)
        self.assertEqual(3, TestSuite.tests_count())

    def test_data_file_when_no_name(self):
        clear()
        DATA_FILE('files/test_data.txt')
        test(data_provider='files/test_data.txt')(valid_for_provider)
        start(listener=self._listener)
        self.assertEqual(3, TestSuite.tests_count())

    def test_container_has_three_tests_default(self):
        clear()
        CONTAINER([_ for _ in range(3)])
        test(data_provider='container')(valid_for_provider)
        start(listener=self._listener)
        self.assertEqual(3, TestSuite.tests_count())

    def test_container_has_three_tests_generator(self):
        clear()
        CONTAINER((_ for _ in range(3)))
        test(data_provider='container')(valid_for_provider)
        start(listener=self._listener)
        self.assertEqual(3, TestSuite.tests_count())

    def test_container_has_three_tests_str(self):
        clear()
        CONTAINER('123')
        test(data_provider='container')(valid_for_provider)
        start(listener=self._listener)
        self.assertEqual(3, TestSuite.tests_count())

    def test_container_has_three_tests_with_name(self):
        clear()
        CONTAINER('123', name='text')
        test(data_provider='text')(valid_for_provider)
        start(listener=self._listener)
        self.assertEqual(3, TestSuite.tests_count())

    def test_data_function_must_have_return_fail(self):
        def fail():
            pass

        clear()
        with self.assertRaises(WrongDecoratedObject):
            provider(name='text')(fail)


if __name__ == '__main__':
    main()
