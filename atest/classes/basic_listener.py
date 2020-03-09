from .test_case import TestCase
from .test_group import TestGroup
import traceback

# TODO find another way for modules. Docs!
_MODULES = ('annotations', 'asserts', 'runner', "classes")


def _print_splitter_line():
    print('-' * 10)


def _is_module(name: str) -> bool:
    """
    Проверяем на модуль атеста, чтобы не выводить трейсы ошибок самой библиотеки (которые юзеру не интересны)
    :param name: имя
    :return: является ли это именем одного из модулей проекта
    """
    for module_name in _MODULES:
        if name.endswith(module_name + '.py'):
            return True
    return False


class Listener:

    def on_fixture_failed(self, group_name:str, fixture_type:str, exception_:Exception):
        pass

    def on_ignored_with_provider(self, test:TestCase, group:TestGroup):
        self._to_results(group, test, 'ignored')

    def on_success(self, group: TestGroup, test: TestCase, verbose: int = 0):
        self._to_results(group, test, 'success')

    def on_failed(self, group: TestGroup, test: TestCase, exception_: Exception, verbose: int = 0):
        self._to_results(group, test, 'failed')

    def on_broken(self, group: TestGroup, test: TestCase, exception_: Exception, verbose: int = 0):
        self._to_results(group, test, 'broken')

    def on_ignored(self, group: TestGroup, test: TestCase, fixture_type: str, verbose: int = 0):
        self._to_results(group, test, 'ignored')

    def _to_results(self, group: TestGroup, test: TestCase, result: str):
        group.add_result_to(test, result)


class DefaultListener(Listener):

    def on_success(self, group: TestGroup, test: TestCase, verbose: int = 0):
        super().on_success(group, test, verbose)
        if not verbose:
            print('.', end='')
        elif verbose > 1:
            _print_splitter_line()
            print(f'{test} SUCCESS!')

    def on_broken(self, group: TestGroup, test: TestCase, exception_: Exception, verbose: int = 0):
        super().on_broken(group, test, exception_, verbose)
        self._failed_or_broken(test, exception_, verbose, 'broken')

    def on_failed(self, group: TestGroup, test: TestCase, exception_: Exception, verbose: int = 0):
        super().on_failed(group, test, exception_, verbose)
        self._failed_or_broken(test, exception_, verbose, 'failed')

    def on_ignored(self, group: TestGroup, test: TestCase, fixture_type: str, verbose: int = 0):
        super().on_ignored(group, test, fixture_type, verbose)
        print(f'Because of fixture "{fixture_type}" test {test} was IGNORED!')
        _print_splitter_line()

    def on_fixture_failed(self, group_name:str, fixture_type:str, exception_:Exception):
        super().on_fixture_failed(group_name,fixture_type, exception_)
        _print_splitter_line()
        print(f'Fixture {fixture_type} "{group_name}" failed!')
        for tb in (e for e in traceback.extract_tb(exception_.__traceback__)):
            print(f'File "{tb.filename}", line {tb.lineno}, in {tb.name}')
        print(exception_)

    def on_ignored_with_provider(self, test:TestCase, group:TestGroup):
        super().on_ignored_with_provider(test, group)
        print(f'Provider "{test.provider}" for {test} not returns iterable! All tests with provider were IGNORED!')

    def _failed_or_broken(self, test, exception_, verbose, _result):
        _letter = f'{_result.upper()}!'
        if not verbose:
            print(_letter[0], end='')
        else:
            if verbose > 0:
                _print_splitter_line()
            print(f'Test {test} {_letter}')
            for tb in (e for e in traceback.extract_tb(exception_.__traceback__) if not _is_module(e.filename)):
                print(f'File "{tb.filename}", line {tb.lineno}, in {tb.name}')
                print(f'-->    {tb.line}')
            print(exception_)
