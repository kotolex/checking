from unittest import TestCase as TC
from unittest import main
from atest.test_case import TestCase
from atest.basic_test import Test


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
        test = Test('name', print)
        self.assertEqual('__main__.name', str(test))

    def test_run_for_Test(self):
        test = Test('name', self.fake_runner)
        before_count = TestClasses.count
        test.run()
        self.assertEqual(before_count + 1, TestClasses.count)


if __name__ == '__main__':
    main()
