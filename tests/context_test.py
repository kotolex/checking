from unittest import main, TestCase

from checking.context import mock_open, mock_print, mock_input


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


def read_bytes():
    f = open('wrong_path.by', 'rb')
    temp = f.read(1)
    f.close()
    return temp


def read_lines_bytes():
    f = open('wrong_path.by', 'rb')
    temp = f.readline(3)
    f.close()
    return temp


def write_bytes():
    f = open('wrong_path.by', 'wb')
    f.write(b'test')
    f.close()


def write_bytes_mode_and_flush():
    f = open('wrong_path.by', mode='wb')
    f.write(b'test')
    f.flush()
    f.close()


def both_context():
    with open('my_file.txt', encoding='utf-8') as f, open('anoter.txt', 'wt') as f2:
        f2.write(f.read(1))


def my_input():
    d = input()
    return d.upper()


def use_both():
    while True:
        word = input('text>>>')
        if word == 'exit':
            break
        print(word)


def my_print(x):
    print(x)


class ContextTest(TestCase):

    def test_no_raises_on_wrong_param_but_raises_arg(self):
        with mock_open(None, raises=ValueError()):
            pass

    def test_raises_on_wrong_param_text(self):
        with self.assertRaises(ValueError):
            with mock_open(on_read_text=123):
                pass

    def test_raises_on_wrong_param_bytes(self):
        with self.assertRaises(ValueError):
            with mock_open(on_read_bytes=123):
                pass

    def test_work_readlines(self):
        with mock_open(on_read_text='123\n456'):
            answer = read_lines()
        self.assertEqual(['123\n', '456'], answer)

    def test_work_readline(self):
        with mock_open('123\n456'):
            answer = read_line()
        self.assertEqual('123\n', answer)

    def test_work_read(self):
        with mock_open('123\n456'):
            answer = read()
        self.assertEqual('1', answer)

    def test_work_readlines_with_context(self):
        with mock_open(on_read_text='123\n456'):
            answer = read_lines()
        self.assertEqual(['123\n', '456'], answer)

    def test_raises_on_param(self):
        with self.assertRaises(IOError) as e:
            with mock_open("None", raises=IOError("File not found!")):
                read_lines()

        self.assertEqual('File not found!', e.exception.args[0])

    def test_work_read_bytes(self):
        with mock_open(on_read_bytes=b'123\n456'):
            answer = read_bytes()
        self.assertEqual(b'1', answer)

    def test_both_contexts(self):
        with mock_open(on_read_text='123\n456') as a_l:
            both_context()
        self.assertEqual(a_l, ['1'])

    def test_write_bytes(self):
        with mock_open() as a_list:
            write_bytes()
        self.assertEqual(b'test', a_list[0])

    def test_mode_and_flush(self):
        with mock_open() as a_list:
            write_bytes_mode_and_flush()
        self.assertEqual(b'test', a_list[0])

    def test_mock_input(self):
        with mock_input(['test']):
            result = my_input()
        self.assertEqual('TEST', result)

    def test_mock_print(self):
        with mock_print([]) as result:
            my_print(1)
            my_print('1')
        self.assertEqual([(1,), ('1',)], result)

    def test_mock_print_args_kwargs(self):
        def _():
            print(1, 2, end=",")

        with mock_print([]) as result:
            _()
        self.assertEqual([(1, 2,)], result)

    def test_both_input_and_print(self):
        with mock_input(['a', 'b', 'exit']), mock_print([]) as result:
            use_both()
        self.assertEqual([('a',), ('b',)], result)


if __name__ == '__main__':
    main()
