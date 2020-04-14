from unittest import TestCase as TC
from unittest import main
from random import randint

from checking.classes.basic_case import TestCase
from checking.classes.basic_test import Test
from checking.classes.basic_group import TestGroup
from checking.classes.basic_suite import TestSuite
from tests.fixture_behaviour_test import clear


class TestClasses(TC):
    count = 0

    @classmethod
    def fake_runner(cls):
        cls.count += 1

    def test_init_for_Test_Case(self):
        case = TestCase('default')
        self.assertFalse(any([case.before, case.after, case.always_run_after, case.is_before_failed, case.provider]))

    def test_add_before_Test_Case(self):
        test_case = TestCase('default')
        test_case.add_before(print)
        self.assertTrue(test_case.before)
        self.assertEqual(1, len(test_case.before))

    def test_add_after_Test_Case(self):
        test_case = TestCase('default')
        test_case.add_after(print)
        self.assertTrue(test_case.after)
        self.assertEqual(1, len(test_case.after))

    def test_init_for_Test(self):
        print_func = print
        test = Test('default', print_func)
        self.assertEqual(print_func, test.test)
        self.assertEqual('__main__', test.group_name)

    def test_str_for_Test(self):
        def f():
            pass
        test = Test('name', f)
        self.assertEqual('__main__.name', str(test))

    def test_run_for_Test(self):
        test = Test('name', self.fake_runner)
        before_count = TestClasses.count
        test.run()
        self.assertEqual(before_count + 1, TestClasses.count)

    def test_clone_for_Test(self):
        test = Test('name', self.fake_runner)
        test.add_before(print)
        test.add_after(self.fake_runner)
        test.provider = "provider"
        test.is_before_failed = True
        test.always_run_after = True
        test.priority = 3
        test.argument = '1'
        test.timeout = 1
        test.only_if = print
        new_test = test.clone()
        self.assertEqual(test.name, new_test.name)
        self.assertEqual(test.before, new_test.before)
        self.assertEqual(test.after, new_test.after)
        self.assertEqual(test.provider, new_test.provider)
        self.assertEqual(test.is_before_failed, new_test.is_before_failed)
        self.assertEqual(test.priority, new_test.priority)
        self.assertEqual(test.argument, new_test.argument)
        self.assertEqual(test.timeout, new_test.timeout)
        self.assertEqual(test.always_run_after, new_test.always_run_after)
        self.assertEqual(test.only_if, new_test.only_if)
        self.assertFalse(test.before is new_test.before)
        self.assertFalse(test.after is new_test.after)

    def test_init_for_TestGroup(self):
        group = TestGroup('default')
        self.assertFalse(any([group.after_all, group.before_all, group.after, group.before, group.always_run_after,
                              group.is_before_failed]))
        self.assertEqual({'success': [], 'broken': [], 'failed': [], 'ignored': []}, group.test_results)

    def test_add_test_for_TestGroup(self):
        group = TestGroup('default')
        test = Test('name', self.fake_runner)
        group.add_test(test)
        self.assertEqual(test, group.tests[0])
        self.assertEqual('default.name', str(test))
        self.assertFalse(any([group.after_all, group.before_all, group.after, group.before, test.after, test.before]))

    def test_add_test_to_group_with_before_test(self):
        group = TestGroup('default')
        group.add_before_test(TestClasses.fake_runner)
        test = Test('name', print)
        group.add_test(test)
        self.assertEqual(TestClasses.fake_runner, test.before[0])

    def test_add_test_to_group_with_after_test(self):
        group = TestGroup('default')
        group.add_after_test(TestClasses.fake_runner)
        test = Test('name', print)
        group.add_test(test)
        self.assertEqual(TestClasses.fake_runner, test.after[0])

    def test_add_test_and_add_before_test(self):
        group = TestGroup('default')
        test = Test('name', print)
        group.add_test(test)
        self.assertFalse(test.before)
        group.add_before_test(TestClasses.fake_runner)
        self.assertEqual(TestClasses.fake_runner, test.before[0])

    def test_add_result_to_default(self):
        group = TestGroup('default')
        test = Test('name', print)
        self.assertFalse(group.test_results['success'])
        group.add_result_to(test)
        self.assertEqual(1, len(group.test_results['success']))

    def test_add_result_to_other(self):
        group = TestGroup('default')
        test = Test('name', print)
        index = randint(1, 3)
        name = list(group.test_results.keys())[index]
        self.assertFalse(group.test_results[name])
        group.add_result_to(test, name)
        self.assertEqual(1, len(group.test_results[name]))

    def test_is_empty_default(self):
        group = TestGroup('default')
        self.assertTrue(group.is_empty())

    def test_is_empty_with_test(self):
        group = TestGroup('default')
        test = Test('name', print)
        group.add_test(test)
        self.assertFalse(group.is_empty())

    def test_count_returns_tests_if_not_run(self):
        group = TestGroup('empty')
        test = Test('name', print)
        group.add_test(test)
        self.assertEqual(1, group.tests_count())

    def test_count_returns_tests_if_run(self):
        group = TestGroup('empty')
        test = Test('name', print)
        group.add_test(test)
        group.test_results['success'] = [1, 2]
        self.assertEqual(2, group.tests_count())

    def test_sort_by_priority(self):
        group = TestGroup('empty')
        test = Test('name2', print)
        test1 = Test('name1', print)
        test2 = Test('name', print)
        test1.priority = 2
        test2.priority = 1
        group.add_test(test)
        group.add_test(test1)
        group.add_test(test2)
        self.assertEqual(group.tests, [test, test1, test2])
        group.sort_test_by_priority()
        self.assertEqual(group.tests, [test, test2, test1])

    def test_singleton_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        suite2 = TestSuite()
        self.assertEqual(suite, suite2)

    def test_add_before_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        self.assertFalse(suite.before)
        suite.add_before(print)
        self.assertEqual(1, len(suite.before))

    def test_add_after_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        self.assertFalse(suite.after)
        suite.add_after(print)
        self.assertEqual(1, len(suite.after))

    def test_get_or_create_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        suite.get_or_create("group_name")
        self.assertIsNotNone(suite.groups.get('group_name'))

    def test_is_empty_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        suite.groups.clear()
        self.assertTrue(suite.is_empty())
        suite.get_or_create('gr_name').add_test(Test('test', print))
        self.assertFalse(suite.is_empty())

    def test_tests_count_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        initial_count = suite.tests_count()
        suite.get_or_create('gr_name').add_test(Test('2', print))
        self.assertEqual(initial_count + 1, suite.tests_count())

    def test_success_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        self.assertFalse(suite.success())
        test_ = Test('any', print)
        suite.get_or_create('gr_name').test_results['success'].append(test_)
        self.assertTrue(suite.success())
        self.assertEqual(test_, suite.success()[0])

    def test_failed_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        self.assertFalse(suite.failed())
        test_ = Test('any', print)
        suite.get_or_create('gr_name').test_results['failed'].append(test_)
        self.assertTrue(suite.failed())
        self.assertEqual(test_, suite.failed()[0])

    def test_broken_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        self.assertFalse(suite.broken())
        test_ = Test('any', print)
        suite.get_or_create('gr_name').test_results['broken'].append(test_)
        self.assertTrue(suite.broken())
        self.assertEqual(test_, suite.broken()[0])

    def test_ignored_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        self.assertFalse(suite.ignored())
        test_ = Test('any', print)
        suite.get_or_create('gr_name').test_results['ignored'].append(test_)
        self.assertTrue(suite.ignored())
        self.assertEqual(test_, suite.ignored()[0])

    def test_filter_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        suite.get_or_create("a")
        suite.get_or_create("b")
        suite.filter_groups(['a'])
        self.assertEqual(list(suite.groups), ['a'])


if __name__ == '__main__':
    main()
