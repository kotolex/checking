from unittest import TestCase as TC
from unittest import main
from random import randint

from atest.test_case import TestCase
from atest.basic_test import Test
from atest.test_group import TestGroup


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
        test = Test('name', print)
        self.assertEqual('__main__.name', str(test))

    def test_run_for_Test(self):
        test = Test('name', self.fake_runner)
        before_count = TestClasses.count
        test.run()
        self.assertEqual(before_count + 1, TestClasses.count)

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


if __name__ == '__main__':
    main()
