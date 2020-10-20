from unittest import TestCase, main

from checking.helpers.others import fake, diff


class OthersTest(TestCase):

    def test_fake_returns_none(self):
        self.assertIsNone(fake())

    def test_fake_returns_none_with_params(self):
        self.assertIsNone(fake(1, 2, 3))

    def test_diff_types(self):
        self.assertEqual('', diff('1', 1))

    def test_diff_no_lens(self):
        self.assertEqual('', diff((e for e in '1'), (e for e in '1')))

    def test_diff_lengths(self):
        self.assertEqual("Length of '12' <str> == 2 but length of '1' <str> == 1", diff('12', '1'))

    def test_diff_sets(self):
        self.assertEqual('Different elements in two sets: {1, 4}', diff({1, 2, 3}, {2, 3, 4}))

    def test_diff_dicts(self):
        self.assertEqual('''Diff in entry under key='1' <int>:
    first  value='1' <int>
    second value='2' <int>''', diff({1: 1}, {1: 2}))

    def test_diff_dicts_keys(self):
        self.assertEqual('''Dict {1: 1, 3: 3} has no key='2' <int>, but contains key(s) {3}''',
                         diff({1: 1, 2: 2}, {1: 1, 3: 3}))

    def test_diff_iter_values(self):
        self.assertEqual('''Diff at element index 1:
    first  value='2' <int>
    second value='3' <int>''', diff([1, 2], [1, 3]))

    def test_diff_iter_types(self):
        self.assertEqual('''Different types at element index 1:
    first  value='2' <int>
    second value='3' <str>''', diff([1, 2], [1, '3']))

    def test_diff_equal_obj(self):
        self.assertEqual('', diff(1, 1))
        self.assertEqual('', diff('1', '1'))
        self.assertEqual('', diff({1, 2}, {1, 2}))
        self.assertEqual('', diff([1, 2], [1, 2]))
        self.assertEqual('', diff(None, None))


if __name__ == '__main__':
    main()
