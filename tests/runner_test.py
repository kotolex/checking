from unittest import TestCase
from unittest import main

from checking import runner as r
from checking.classes.basic_test import Test
from checking.classes.basic_group import TestGroup
from checking.classes.basic_suite import TestSuite
from checking.classes.listeners.basic import Listener
from checking.exceptions import UnknownProviderName, TestIgnoredException
from checking.helpers.others import fake
from checking.asserts import equals

from tests.fixture_behaviour_test import clear


class TestListener(Listener):
    def on_failed(self, test: Test, exception_: Exception):
        global COUNT
        COUNT = COUNT + 2

    def on_broken(self, test: Test, exception_: Exception):
        global COUNT
        COUNT = COUNT + 3

    def on_ignored_by_condition(self, test: Test, exc: Exception):
        global COUNT
        COUNT = COUNT + 4


COUNT = 0


def inc():
    global COUNT
    COUNT += 1


def fail_assert():
    raise AssertionError()


def fail_exception():
    raise ValueError()


def fail_test():
    raise TestIgnoredException


class RunnerTest(TestCase):
    r._listener = TestListener()

    def test_run_fixture_true(self):
        result = r._run_fixture(fake, 'test', 'test')
        self.assertFalse(result)

    def test_run_fixture_false(self):
        result = r._run_fixture(lambda: int('a'), 'test', 'test')
        self.assertTrue(result)

    def test_run_after_runs_for_test(self):
        test_case = Test('test', inc)
        test_case.add_after(inc)
        count = COUNT
        r._run_after(test_case)
        self.assertEqual(count + 1, COUNT)

    def test_run_after_runs_for_group(self):
        test_case = TestGroup('test')
        test_case.add_after(inc)
        count = COUNT
        r._run_after(test_case)
        self.assertEqual(count + 1, COUNT)

    def test_run_after_runs_for_test_if_before_failed(self):
        test_case = Test('test', inc)
        test_case.add_after(inc)
        test_case.is_before_failed = True
        count = COUNT
        r._run_after(test_case)
        self.assertEqual(count, COUNT)

    def test_run_after_runs_for_group_if_before_failed(self):
        test_case = TestGroup('test')
        test_case.add_after(inc)
        test_case.is_before_failed = True
        count = COUNT
        r._run_after(test_case)
        self.assertEqual(count, COUNT)

    def test_run_after_runs_for_test_if_before_failed_but_always_run(self):
        test_case = Test('test', inc)
        test_case.add_after(inc)
        test_case.is_before_failed = True
        test_case.always_run_after = True
        count = COUNT
        r._run_after(test_case)
        self.assertEqual(count + 1, COUNT)

    def test_run_after_runs_for_group_if_before_failed_but_always_run(self):
        test_case = TestGroup('test')
        test_case.add_after(inc)
        test_case.is_before_failed = True
        test_case.always_run_after = True
        count = COUNT
        r._run_after(test_case)
        self.assertEqual(count + 1, COUNT)

    def test_run_before_for_test_be_false(self):
        test_case = Test('test', inc)
        test_case.add_before(fake)
        r._run_before(test_case)
        self.assertFalse(test_case.is_before_failed)

    def test_run_before_for_group_be_false(self):
        test_case = TestGroup('test')
        test_case.add_before(fake)
        r._run_before(test_case)
        self.assertFalse(test_case.is_before_failed)

    def test_run_before_for_test_be_true(self):
        test_case = Test('test', inc)
        test_case.add_before(lambda: int('a'))
        r._run_before(test_case)
        self.assertTrue(test_case.is_before_failed)

    def test_run_before_for_group_be_true(self):
        test_case = TestGroup('test')
        test_case.add_before(lambda: int('a'))
        r._run_before(test_case)
        self.assertTrue(test_case.is_before_failed)

    def test_check_providers_returns_if_empty(self):
        clear()
        suite = TestSuite.get_instance()
        r._check_data_providers(suite)

    def test_check_providers_returns_ok_if_exists(self):
        clear()
        suite = TestSuite.get_instance()
        suite.providers['test'] = print
        test_case = Test('test', inc)
        test_case.provider = 'test'
        suite.get_or_create("group").add_test(test_case)
        r._check_data_providers(suite)

    def test_check_providers_returns_failed_if_not_exists(self):
        clear()
        suite = TestSuite.get_instance()
        suite.providers['test'] = print
        test_case = Test('test', inc)
        test_case.provider = 'test2'
        suite.get_or_create("group").add_test(test_case)
        with self.assertRaises(UnknownProviderName):
            r._check_data_providers(suite)

    def test_run_test_ok(self):
        test_case = Test('test', inc)
        group = TestGroup('group')
        group.add_test(test_case)
        count = COUNT
        self.assertTrue(r._run_test(test_case))
        self.assertEqual(count + 1, COUNT)

    def test_run_test_assert_fail(self):
        test_case = Test('test', fail_assert)
        group = TestGroup('group')
        group.add_test(test_case)
        self.assertFalse(r._run_test(test_case))

    def test_run_test_assert_broken(self):
        test_case = Test('test', fail_exception)
        group = TestGroup('group')
        group.add_test(test_case)
        self.assertFalse(r._run_test(test_case))

    def test_run_test_assert_ignored(self):
        test_case = Test('test', fail_test)
        group = TestGroup('group')
        group.add_test(test_case)
        self.assertFalse(r._run_test(test_case))

    def test_provider_next_iter(self):
        clear()
        TestSuite.get_instance().providers['test2'] = lambda: [1, 2, 3]
        cycle = r._provider_next('test2')
        self.assertEqual('123', ''.join([str(_) for _ in cycle]))

    def test_provider_next_closeable(self):
        class Fake:
            def __next__(self):
                return 1

            def __iter__(self):
                return iter([1])

            def close(self):
                global COUNT
                COUNT = COUNT + 6

        clear()
        count = COUNT
        TestSuite.get_instance().providers['test2'] = Fake
        cycle = r._provider_next('test2')
        self.assertEqual('1', ''.join([str(_) for _ in cycle]))
        self.assertEqual(count + 6, COUNT)

    def test_run_all_test_in_group(self):
        test_case = Test('one', inc)
        test_case2 = Test('two', inc)
        group = TestGroup('group')
        count = COUNT
        group.add_test(test_case)
        group.add_test(test_case2)
        r._run_all_tests_in_group(group)
        self.assertEqual(count + 2, COUNT)

    def test_dry_run(self):
        clear()
        count = COUNT
        suite = TestSuite.get_instance()
        test_case = Test('test', inc)
        suite.get_or_create("group").add_test(test_case)
        r._dry_run(suite)
        self.assertEqual(count, COUNT)
        self.assertFalse(any([suite.before, suite.after,
                              suite.get_or_create("group").before, suite.get_or_create("group").after]))

    def test_run_all_test_in_group_random(self):
        clear()
        test_case = Test('one', inc)
        test_case2 = Test('two', inc)
        test_case3 = Test('three', inc)
        test_case4 = Test('four', inc)
        test_case5 = Test('five', inc)
        group = TestGroup('group')
        group.add_test(test_case)
        group.add_test(test_case2)
        group.add_test(test_case3)
        group.add_test(test_case4)
        group.add_test(test_case5)
        TestSuite.get_instance().groups['group'] = group
        r._run(TestSuite.get_instance(), 1, random_order=True)
        runned = [test.name for test in group.test_results]
        self.assertNotEqual(['one', 'two', 'three', 'four', 'five'], runned)

    def test_check_max_fail(self):
        clear()
        suite = TestSuite.get_instance()
        test_case = Test('some', lambda: equals(1, 2))
        suite.get_or_create("group").add_test(test_case)
        suite.get_or_create("group").add_test(test_case)
        suite.get_or_create("group").add_test(test_case)
        r.start(max_fail=1, listener=TestListener())
        self.assertEqual(len(suite.failed()), 1)
        self.assertEqual(suite.tests_count(), 1)

    def test_check_max_fail_with_provider(self):
        clear()
        suite = TestSuite.get_instance()
        test_case = Test('some', lambda z: equals(z, 3))
        test_case.provider = 'test2'
        suite.providers['test2'] = lambda: [1, 2, 4, 5]
        suite.get_or_create("group").add_test(test_case)
        r.start(max_fail=1, listener=TestListener())
        self.assertEqual(len(suite.failed()), 1)
        self.assertEqual(suite.tests_count(), 1)

    def test_check_max_fail_not_reached(self):
        clear()
        suite = TestSuite.get_instance()
        test_case = Test('some', lambda: equals(1, 2))
        suite.get_or_create("group").add_test(test_case)
        suite.get_or_create("group").add_test(test_case)
        r.start(max_fail=3, listener=TestListener())
        self.assertEqual(len(suite.failed()), 2)
        self.assertEqual(suite.tests_count(), 2)


if __name__ == '__main__':
    main()
