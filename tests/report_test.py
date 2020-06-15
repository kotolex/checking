from unittest import main, TestCase

import checking.helpers.report as rep
from checking.annotations import test
from checking.helpers.report import add_text, add_img
from checking.classes.basic_suite import TestSuite
from checking.classes.basic_test import Test
from tests.fixture_behaviour_test import clear


class TestReport(TestCase):
    def test_base(self):
        self.assertTrue('utf-8' in rep.BASE)
        self.assertTrue('Suite name:' in rep.BASE)
        self.assertTrue('Test Results for' in rep.BASE)

    def test_create_info_replace_suite(self):
        clear()
        t = TestSuite.get_instance()
        test = Test('test', print)
        test.status = 'success'
        t.start_suite()
        t.get_or_create("one").test_results.append(test)
        t.get_or_create("one").tests.append(test)
        t.name = "Test"
        lines = ['#suite_name']
        t.stop_suite()
        rep._create_info(lines, t)
        self.assertEqual(t.name, lines[0])
        result = ''.join(lines)
        self.assertTrue('Total groups' in result)
        self.assertTrue('Total tests' in result)
        self.assertTrue('success tests' in result)
        self.assertTrue('failed tests' in result)
        self.assertTrue('broken tests' in result)
        self.assertTrue('ignored tests' in result)
        self.assertTrue('Success percent' in result)
        self.assertTrue('Total time' in result)

    def test_empty_suite(self):
        clear()
        t = TestSuite.get_instance()
        t.start_suite()
        t.stop_suite()
        lines = rep._generate_html(t)
        self.assertTrue('Suite is empty! There are no tests!' in ''.join(lines))

    def test_non_empty_suite(self):
        clear()
        t = TestSuite.get_instance()
        test = Test('test', print)
        test.status = 'success'
        t.start_suite()
        t.get_or_create("one").test_results.append(test)
        t.get_or_create("one").tests.append(test)
        t.name = "Test"
        t.stop_suite()
        lines = rep._generate_html(t)
        result = ''.join(lines)
        self.assertFalse('Suite is empty! There are no tests!' in result)
        self.assertTrue('Statistics' in result)
        self.assertTrue("Group 'one'" in result)
        self.assertTrue("test" in result)

    def test_add_text(self):
        def _():
            add_text("A", "B")

        clear()
        test(_)
        t = list(TestSuite.get_instance().groups.values())[0].tests[0]
        t.run()
        self.assertEqual({'A': 'B'}, t.report_params)

    def test_add_img(self):
        def _():
            add_img("A", b"B")

        clear()
        test(_)
        t = list(TestSuite.get_instance().groups.values())[0].tests[0]
        t.run()
        self.assertEqual({b'B': 'A'}, t.report_params)

    def test_non_empty_suite_with_text(self):
        clear()
        t = TestSuite.get_instance()
        test = Test('test', print)
        test.status = 'success'
        test.report_params['A']='B'
        t.start_suite()
        t.get_or_create("one").test_results.append(test)
        t.get_or_create("one").tests.append(test)
        t.name = "Test"
        t.stop_suite()
        lines = rep._generate_html(t)
        result = ''.join(lines)
        self.assertTrue("test" in result)
        self.assertTrue("Report parameter <b>'A'</b>: B" in result)


if __name__ == '__main__':
    main()
