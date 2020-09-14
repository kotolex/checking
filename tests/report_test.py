from unittest import main, TestCase

from checking.annotations import test
from checking.helpers.report import add_text, add_img
from checking.classes.basic_suite import TestSuite
from tests.fixture_behaviour_test import clear


class TestReport(TestCase):

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


if __name__ == '__main__':
    main()
