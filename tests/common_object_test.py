from unittest import main, TestCase

from checking.classes.common import Common


class TestCommon(TestCase):
    def test_empty_without_params(self):
        common = Common()
        self.assertFalse(common.__dict__)

    def test_not_empty_with_params(self):
        common = Common({'1': 1})
        self.assertTrue(common.__dict__)
        self.assertEqual(1, common.__dict__['1'])

    def test_get_item(self):
        common = Common({'1': 1})
        self.assertEqual(1, common['1'])

    def test_set_item(self):
        common = Common()
        self.assertFalse(common.__dict__)
        common['a'] = 1
        self.assertEqual(1, common.__dict__['a'])

    def test_dot_notation(self):
        common = Common({'a': 10})
        self.assertEqual(10, common.a)

    def test_contains(self):
        common = Common({'a': 10})
        self.assertTrue('a' in common)
        self.assertFalse('b' in common)

    def test_str(self):
        common = Common({'a': 10})
        self.assertEqual("Common dictionary: {'a': 10}", str(common))

    def test_update(self):
        common = Common({'a': 10})
        self.assertEqual({'a': 10}, common.__dict__)
        common.update({'b': 20})
        self.assertEqual({'a': 10, 'b': 20}, common.__dict__)

    def test_clear(self):
        common = Common({'a': 10})
        self.assertEqual({'a': 10}, common.__dict__)
        common.clear()
        self.assertEqual({}, common.__dict__)

    def test_as_dict(self):
        common = Common({'a': 10})
        self.assertEqual({'a': 10}, common.as_dict())

    def test_bool(self):
        common = Common()
        self.assertFalse(common)
        common = Common({'a': 10})
        self.assertTrue(common)


if __name__ == '__main__':
    main()
