from unittest import TestCase, main
from checking.classes.listeners.basic import Listener
from checking.classes.basic_test import Test
from checking import runner as r_
from checking.annotations import test, data, before, before_suite
from tests.fixture_behaviour_test import clear

COUNT = 0


def inc(*args, **kwargs):
    global COUNT
    COUNT += 1


def fake():
    pass


class ListenerTest(TestCase):

    def test_get_test_arg_short_without_new_line_returns_none(self):
        test_ = Test('name', print)
        test_.provider = '1'
        self.assertEqual('[None]', Listener._get_test_arg_short_without_new_line(test_))

    def test_get_test_arg_short_without_new_line_returns_arg(self):
        test_ = Test('name', print)
        test_.provider = '1'
        test_.argument = 1
        self.assertEqual('[1]', Listener._get_test_arg_short_without_new_line(test_))

    def test_get_test_arg_short_without_new_line_returns_empty(self):
        test_ = Test('name', print)
        test_.argument = 1
        self.assertEqual('', Listener._get_test_arg_short_without_new_line(test_))

    def test_dry_run_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_dry_run = inc
        count = COUNT
        test(fake)
        r_.start(listener=listener_, dry_run=True)
        self.assertEqual(count + 1, COUNT)

    def test_empty_suite_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_empty_suite = inc
        count = COUNT
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_start_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_suite_starts = inc
        count = COUNT
        test(fake)
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_ends_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_suite_ends = inc
        count = COUNT
        test(fake)
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_starts_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_test_starts = inc
        count = COUNT
        test(fake)
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_fixture_failed_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_fixture_failed = inc
        count = COUNT
        test(fake)
        before(lambda: int('a'))
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_ignore_with_provider_call(self):
        def wrong():
            return 1

        clear()
        listener_ = Listener(0)
        listener_.on_ignored_with_provider = inc
        count = COUNT
        data(name='prov')(wrong)
        test(data_provider='prov')(lambda x: x)
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_success_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_success = inc
        count = COUNT
        test(fake)
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_failed_call(self):
        def fail():
            assert 1 == 2

        clear()
        listener_ = Listener(0)
        listener_.on_failed = inc
        count = COUNT
        test(fail)
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_broken_call(self):
        def broke():
            int('1a')

        clear()
        listener_ = Listener(0)
        listener_.on_broken = inc
        count = COUNT
        test(broke)
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_ignored_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_ignored = inc
        count = COUNT
        test(fake)
        before(lambda: int('a'))
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_ignored_by_condition_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_ignored_by_condition = inc
        count = COUNT
        test(only_if=lambda: False)(fake)
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)

    def test_before_suite_failed_call(self):
        clear()
        listener_ = Listener(0)
        listener_.on_before_suite_failed = inc
        count = COUNT
        before_suite(lambda: int('a'))
        test(fake)
        r_.start(listener=listener_)
        self.assertEqual(count + 1, COUNT)


if __name__ == '__main__':
    main()