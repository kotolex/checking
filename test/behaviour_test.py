from unittest import main, TestCase

from atest.runner import start
from atest.classes.basic_listener import Listener
from atest.annotations import *
from test.fixture_behaviour_test import clear


def _fn(it):
    assert it in range(3)


class BehaviourTest(TestCase):

    def test_three_success_when_data(self):
        clear()
        data(name='three')(lambda: [0, 1, 2])
        test(data_provider='three')(_fn)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(3, len(TestSuite.get_instance().success()))
        self.assertEqual(0, len(TestSuite.get_instance().failed()))
        self.assertEqual(3, TestSuite.get_instance().tests_count())

    def test_three_success_one_failed_when_data(self):
        clear()
        data(name='four')(lambda: [0, 1, 2, 3])
        test(data_provider='four')(_fn)
        start(listener=Listener(0))
        self.assertEqual(0, len(TestSuite.get_instance().broken()))
        self.assertEqual(3, len(TestSuite.get_instance().success()))
        self.assertEqual(1, len(TestSuite.get_instance().failed()))
        self.assertEqual(4, TestSuite.get_instance().tests_count())


if __name__ == '__main__':
    main()
