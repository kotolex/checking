from unittest import main, TestCase

from checking.context import mock_readfile


def read_lines():
    f = open('wrong_path.txt', encoding='utf-8')
    temp = f.readlines()
    f.close()
    return temp


def with_read_lines():
    with open('wrong_path.txt') as f:
        return [line for line in f]


def read_line():
    f = open('wrong_path.txt')
    temp = f.readline()
    f.close()
    return temp


def read():
    f = open('wrong_path.txt')
    temp = f.read(1)
    f.close()
    return temp


class ContextTest(TestCase):

    def test_no_raises_on_wrong_param_but_raises_arg(self):
        with mock_readfile(None, raises=ValueError()):
            pass

    def test_raises_on_wrong_param(self):
        with self.assertRaises(ValueError):
            with mock_readfile(123):
                pass

    def test_raises_on_wrong_container(self):
        with self.assertRaises(ValueError):
            with mock_readfile(['1', 2, '3']):
                pass

    def test_work_readlines(self):
        with mock_readfile('123\n456'):
            answer = read_lines()
        self.assertEqual(['123\n', '456'], answer)

    def test_work_readline(self):
        with mock_readfile('123\n456'):
            answer = read_line()
        self.assertEqual('123\n', answer)

    def test_work_read(self):
        with mock_readfile('123\n456'):
            answer = read()
        self.assertEqual('1', answer)

    def test_work_readlines_with_tuple(self):
        with mock_readfile(('123', '456')):
            answer = read_lines()
        self.assertEqual(['123\n', '456'], answer)

    def test_work_readlines_with_context(self):
        with mock_readfile(['123', '456']):
            answer = read_lines()
        self.assertEqual(['123\n', '456'], answer)

    def test_raises_on_param(self):
        with self.assertRaises(IOError) as e:
            with mock_readfile("None", raises=IOError("File not found!")):
                read_lines()

        self.assertEqual('File not found!', e.exception.args[0])

    def test_returns_list_of_calls(self):
        with mock_readfile(['123', '456']) as calls:
            read_lines()
        self.assertEqual('wrong_path.txt', calls[0].args[0])
        self.assertEqual('utf-8', calls[0].kwargs['encoding'])


if __name__ == '__main__':
    main()
