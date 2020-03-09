from unittest import TestCase, main

from atest.annotations import *
from atest.exceptions import *
from atest.classes.basic_suite import TestSuite
from atest.test_runner import start
from atest.classes.basic_listener import Listener


def valid():
    pass


def valid_for_data():
    return [1, 2]


def valid_for_provider(arg):
    pass


class T:
    def m(self):
        pass


class TestAnnotations(TestCase):

    def test_valid_func_works(self):
        initial_count = TestSuite.get_instance().tests_count()
        test(valid)
        self.assertEqual(initial_count + 1, TestSuite.get_instance().tests_count())

    def test_not_add_if_disabled(self):
        initial_count = TestSuite.get_instance().tests_count()
        test(enabled=False)(valid)
        self.assertEqual(initial_count, TestSuite.get_instance().tests_count())

    def test_not_add_if_enabled(self):
        initial_count = TestSuite.get_instance().tests_count()
        test(enabled=True)(valid)
        self.assertEqual(initial_count + 1, TestSuite.get_instance().tests_count())

    def test_raises_when_func_for_provider_has_no_arg(self):
        with self.assertRaises(WrongAnnotationPlacement) as e:
            test(data_provider="good")(valid)
        self.assertEqual("Function 'valid' marked with data_provider has no argument! Must be one at least!",
                         e.exception.args[0])

    def test_raises_when_no_provider(self):
        test(data_provider="missing")(valid_for_provider)
        with self.assertRaises(UnknownProviderName) as e:
            start(TestSuite.get_instance(), listener=Listener(0))
        self.assertTrue("Cant find provider with name(s) ['missing']" in e.exception.args[0])

    def test_ignore_all_if_test_disabled(self):
        test(enabled=False, data_provider="wrong")(valid)

    def test_raises_when_using_test_with_class(self):
        with self.assertRaises(WrongAnnotationPlacement) as ex:
            test(T)
        self.assertTrue('test' in ex.exception.args[0])

    def test_raises_when_using_function_with_arg(self):
        with self.assertRaises(WrongAnnotationPlacement) as ex:
            test(valid_for_provider)
        self.assertTrue('test' in ex.exception.args[0])

    def test_raises_when_using_test_with_class_methods(self):
        with self.assertRaises(WrongAnnotationPlacement) as ex:
            t = T()
            test(t.m)
        self.assertTrue('test' in ex.exception.args[0])

    def test_name_param_works(self):
        test(name='new_name')(valid)
        self.assertTrue('new_name' in [t.name for t in TestSuite.get_instance().get_or_create('annotations_test').tests])


    def test_data_works(self):
        data(name="any_name")(valid_for_data)
        self.assertTrue('valid_for_data' in TestSuite.get_instance().providers)

    def test_data_raises_when_duplicate_name(self):
        with self.assertRaises(DuplicateNameException) as e:
            data(valid_for_data)
            data(valid_for_data)
        self.assertEqual('Provider with name "valid_for_data" already exists! Only unique names allowed!',
                         e.exception.args[0])

    def test_data_name_works(self):
        data(name="another")(valid_for_data)
        self.assertTrue('another' in TestSuite.get_instance().providers)

    def test_data_ignore_if_disabled(self):
        data(enabled=False, name="no")(valid)
        self.assertFalse('no' in TestSuite.get_instance().providers)

    def test_before_all_when_before_first(self):
        before_ = lambda: None
        before(before_)
        t = Test('first', print)
        TestSuite.get_instance().get_or_create('annotations_test').add_test(t)
        self.assertTrue(t.before)
        self.assertEqual(before_, t.before[0])

    def test_before_all_when_before_last(self):
        t = Test('second', print)
        TestSuite.get_instance().get_or_create('annotations_test').add_test(t)
        bef = lambda: None
        before(bef)
        self.assertTrue(bef in t.before)


if __name__ == '__main__':
    main()
