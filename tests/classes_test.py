from unittest import TestCase as TC
from unittest import main
from random import choice
from time import sleep

from checking.classes.basic_case import TestCase
from checking.classes.basic_test import Test
from checking.classes.basic_group import TestGroup
from checking.classes.basic_suite import TestSuite
from checking.classes.timer import Timer
from tests.fixture_behaviour_test import clear
from checking.exceptions import TestIgnoredException


class TestClasses(TC):
    count = 0

    @classmethod
    def fake_runner(cls):
        cls.count += 1

    def test_init_for_Test_Case(self):
        case = TestCase('default')
        self.assertFalse(any([case.before, case.after, case.always_run_after, case.is_before_failed]))

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
        test.group = self
        test.status = 'FAILED'
        test.reason = ValueError('1')
        test.report_params = {1: '1'}
        new_test = test.clone()
        self.assertEqual(test.name, new_test.name)
        self.assertEqual(new_test.group, self)
        self.assertEqual(test.before, new_test.before)
        self.assertEqual(test.after, new_test.after)
        self.assertEqual(test.provider, new_test.provider)
        self.assertEqual(test.is_before_failed, new_test.is_before_failed)
        self.assertEqual(test.priority, new_test.priority)
        self.assertEqual(test.argument, new_test.argument)
        self.assertEqual(test.timeout, new_test.timeout)
        self.assertEqual(test.always_run_after, new_test.always_run_after)
        self.assertEqual(test.only_if, new_test.only_if)
        self.assertEqual(test.before, new_test.before)
        self.assertEqual(test.after, new_test.after)
        self.assertEqual(test.status, new_test.status)
        self.assertEqual(test.reason, new_test.reason)
        self.assertNotEqual(test.report_params, new_test.report_params)
        self.assertFalse(new_test.report_params)

    def test_init_for_TestGroup(self):
        group = TestGroup('default')
        self.assertFalse(any([group.after_all, group.before_all, group.after, group.before, group.always_run_after,
                              group.is_before_failed]))
        self.assertEqual([], group.test_results)

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
        test.status = 'success'
        self.assertFalse(group.tests_by_status('success'))
        group.add_result(test)
        self.assertEqual(1, len(group.tests_by_status('success')))

    def test_add_result_to_other(self):
        group = TestGroup('default')
        test = Test('name', print)
        stat = choice(['sucess', 'broken', 'failed', 'ignored'])
        test.status = stat
        self.assertFalse(group.tests_by_status(stat))
        group.add_result(test)
        self.assertEqual(1, len(group.tests_by_status(stat)))

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
        test.status = 'success'
        group.add_test(test)
        group.test_results = [test, test]
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
        test_.status = 'success'
        suite.get_or_create('gr_name').test_results.append(test_)
        self.assertTrue(suite.success())
        self.assertEqual(test_, suite.success()[0])

    def test_failed_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        self.assertFalse(suite.failed())
        test_ = Test('any', print)
        test_.status = 'failed'
        suite.get_or_create('gr_name').test_results.append(test_)
        self.assertTrue(suite.failed())
        self.assertEqual(test_, suite.failed()[0])

    def test_broken_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        self.assertFalse(suite.broken())
        test_ = Test('any', print)
        test_.status = 'broken'
        suite.get_or_create('gr_name').test_results.append(test_)
        self.assertTrue(suite.broken())
        self.assertEqual(test_, suite.broken()[0])

    def test_ignored_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        self.assertFalse(suite.ignored())
        test_ = Test('any', print)
        test_.status = 'ignored'
        suite.get_or_create('gr_name').test_results.append(test_)
        self.assertTrue(suite.ignored())
        self.assertEqual(test_, suite.ignored()[0])

    def test_filter_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        suite.get_or_create("a")
        suite.get_or_create("b")
        suite.filter_groups(['a'])
        self.assertEqual(list(suite.groups), ['a'])

    def test_filter_tests_TestSuite(self):
        clear()
        suite = TestSuite.get_instance()
        suite.get_or_create('gr_name').add_test(Test('a__2', print))
        suite.get_or_create('gr_name').add_test(Test('a__3', print))
        initial_count = suite.tests_count()
        suite.filter_tests('a')
        self.assertEqual(initial_count, suite.tests_count())

    def test_filter_tests_TestSuite_must_clear_if_not_present(self):
        clear()
        suite = TestSuite.get_instance()
        suite.get_or_create('gr_name').add_test(Test('a__2', print))
        suite.get_or_create('gr_name').add_test(Test('a__3', print))
        suite.filter_tests('b')
        self.assertEqual(0, suite.tests_count())

    def test_filter_tests_TestSuite_must_be_one(self):
        clear()
        suite = TestSuite.get_instance()
        suite.get_or_create('gr_name').add_test(Test('a__2', print))
        suite.get_or_create('gr_name').add_test(Test('a__3', print))
        suite.filter_tests('2')
        self.assertEqual(1, suite.tests_count())

    def test_add_test_to_group(self):
        group = TestGroup("new_group")
        test_case = Test("test1", print)
        group.add_test(test_case)
        self.assertEqual(test_case.group_name, 'new_group')
        self.assertEqual(test_case.group, group)

    def test_default_has_minus_one_timings(self):
        test_case = Test('test', print)
        self.assertEqual(test_case.duration(), -1)

    def test_run_change_start_time(self):
        test_case = Test('test', lambda: -1)
        test_case.run()
        self.assertTrue(test_case.timer.start_time > 0)

    def test_stop_change_end_time(self):
        test_case = Test('test', lambda: -1)
        test_case.run()
        test_case.stop()
        self.assertTrue(test_case.timer.end_time >= test_case.timer.start_time)
        self.assertTrue(test_case.duration() >= 0)

    def test_duration_works(self):
        test_case = Test('test', lambda: -1)
        test_case.run()
        sleep(0.2)
        test_case.stop()
        self.assertTrue(test_case.duration() >= 0.2)

    def test_created_by_default(self):
        test_case = Test('test', print)
        self.assertEqual('created', test_case.status)

    def test_if_run_set_to_success(self):
        test_case = Test('test', lambda: 1)
        test_case.run()
        test_case.stop()
        self.assertEqual('success', test_case.status)
        self.assertIsNone(test_case.reason)

    def test_if_fail_stop_time(self):
        test_case = Test('test', lambda: 1)
        test_case.stop(Exception())
        self.assertTrue(test_case.timer.end_time > 0)
        self.assertTrue(test_case.duration() >= 0)
        self.assertFalse(test_case.status == 'success')
        self.assertFalse(test_case.status == 'created')

    def test_if_fail_assert_set_failed(self):
        test_case = Test('test', lambda: 1)
        test_case.stop(AssertionError())
        self.assertEqual(test_case.status, 'failed')

    def test_if_ignored_exception_set_ignore(self):
        test_case = Test('test', lambda: 1)
        test_case.stop(TestIgnoredException())
        self.assertEqual(test_case.status, 'ignored')

    def test_if_sys_exit_exception_set_ignore(self):
        test_case = Test('test', lambda: 1)
        test_case.stop(SystemExit())
        self.assertEqual(test_case.status, 'ignored')

    def test_if_exception_set_broken(self):
        test_case = Test('test', lambda: 1)
        test_case.stop(ValueError())
        self.assertEqual(test_case.status, 'broken')

    def test_start_suite_start_timer_for_Suite(self):
        clear()
        test_suite = TestSuite.get_instance()
        test_suite.start_suite()
        self.assertTrue(test_suite.timer.start_time > 0)

    def test_stop_suite_stop_timer_for_Suite(self):
        clear()
        test_suite = TestSuite.get_instance()
        test_suite.start_suite()
        test_suite.stop_suite()
        self.assertTrue(test_suite.timer.end_time > 0)
        self.assertTrue(test_suite.suite_duration() >= 0)

    def test_timer_default(self):
        timer = Timer()
        self.assertEqual(-1, timer.start_time)
        self.assertEqual(-1, timer.end_time)
        self.assertEqual(-1, timer.duration)

    def test_timer_works(self):
        timer = Timer()
        timer.start()
        sleep(0.1)
        timer.stop()
        self.assertTrue(timer.start_time > 0)
        self.assertTrue(timer.end_time > 0)
        self.assertTrue(timer.duration > 0)

    def test_timer_reset_works(self):
        timer = Timer()
        timer.start()
        sleep(0.1)
        timer.stop()
        timer.reset()
        self.assertEqual(-1, timer.start_time)
        self.assertEqual(-1, timer.end_time)
        self.assertEqual(-1, timer.duration)

    def test_group_shuffle(self):
        group = TestGroup('name')
        t1 = Test('one', print)
        t2 = Test('two', print)
        t3 = Test('three', print)
        t4 = Test('four', print)
        t5 = Test('five', print)
        t6 = Test('six', print)
        group.add_test(t1)
        group.add_test(t2)
        group.add_test(t3)
        group.add_test(t4)
        group.add_test(t5)
        group.add_test(t6)
        self.assertEqual([t1, t2, t3, t4, t5, t6], group.tests)
        group.shuffle_tests()
        self.assertNotEqual([t1, t2, t3, t4, t5, t6], group.tests)


if __name__ == '__main__':
    main()
