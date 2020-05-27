from unittest import TestCase, main

from checking.helpers.others import fake


class OthersTest(TestCase):

    def test_fake_returns_none(self):
        self.assertIsNone(fake())

    def test_fake_returns_none_with_params(self):
        self.assertIsNone(fake(1, 2, 3))


if __name__ == '__main__':
    main()
