import traceback
import os
from typing import List, Tuple

SEPARATOR = os.path.sep


def _is_need_to_hide(name: str) -> bool:
    parts = (f'atest{SEPARATOR}asserts.py', f'atest{SEPARATOR}classes{SEPARATOR}', f'{SEPARATOR}contextlib.py',)
    """
    Проверяем строки трейсбека на содержание внутренних модулей проекта и некоторых модулей стандартной библиотеки, 
    чтобы не выводить трейсы ошибок (которые юзеру не интересны)
    :param name: имя
    :return: True если является именем одного из внутренних модулей
    """
    return any([part in name for part in parts])


def get_trace(exception_: Exception) -> List[Tuple]:
    """
    Возвращает весь трейс ошибки в виде списка, состоящего из кортежей (расположение строки с ошибкой, ошибка)
    :param exception_: исключение, чей трейс нужен
    :return: список кортежей
    """
    result = []
    for tb in (e for e in traceback.extract_tb(exception_.__traceback__)):
        first = f'File "{tb.filename}", line {tb.lineno}, in {tb.name}'
        second = f'-->    {tb.line}'
        result.append((first, second))
    return result


def get_trace_filtered_by_filename(exception_: Exception) -> str:
    """
    Возвращает строковое представление трейса ошибки, отфильтрованного по имени модуля, то есть остаются только строки,
    не принадлежащие основным классам atest
    :param exception_: исключение, чей стектрейс нужен
    :return: строку, где каждая запись отделена \n
    """
    return '\n'.join([f'{a}\n{b}' for a, b in get_trace(exception_) if not _is_need_to_hide(a)])
