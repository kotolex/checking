import glob
import json
import sys
import os
import importlib
from typing import Dict

from .runner import start

HOME_FOLDER = sys.path[0]
look_for = ('import atest', 'from atest')


def is_options_exists() -> bool:
    """
    Сообщает есть ли в папке запуска файл с настройками options.json
    :return: True, если файл присутствует
    """
    return len(glob.glob('options.json')) == 1


def read_parameters_from_file() -> Dict:
    """
    Читает параметры из файла настроек options.json, возвращает в виде словаря параметров
    """
    with open('options.json') as file:
        result = ''.join([line.rstrip() for line in file.readlines()])
    params = {'verbose': 0, 'groups': [], 'params': {}, 'listener': '', 'modules': []}
    params.update(json.loads(result))
    return params


def check_parameters(parameters: Dict):
    """
    Проверяет валидность параметров запуска
    :param parameters: словарь с параметрами
    :return: None
    :raises ValueError если параметры неверного типа
    """
    if 'verbose' in parameters:
        verbose = parameters['verbose']
        if type(verbose) is not int:
            raise ValueError('Verbose parameter must be int!')
    groups = parameters['groups']
    if type(groups) is not list:
        raise ValueError('Groups parameter must be list of strings (List[str])!')
    modules = parameters['modules']
    if type(modules) is not list:
        raise ValueError('Modules parameter must be list of strings (List[str])!')
    params = parameters['params']
    if type(params) is not dict:
        raise ValueError('Params parameter must be dict (even empty)!')
    listener = parameters['listener']
    if type(listener) is not str:
        raise ValueError('Listener parameter must be str (even empty)!')


def start_with_parameters(parameters: Dict):
    params = {'verbose': 0, 'groups': [], 'params': {}, 'listener': '', 'modules': []}
    params.update(parameters)
    check_parameters(params)
    verbose = params.get('verbose')
    par = params.get('params')
    groups = params.get('groups')
    modules = params.get('modules')
    listener_ = params.get('listener')
    real_listener = None
    try:
        if listener_:
            pack = '.'.join(listener_.split('.')[:-1])
            cl_ = listener_.split('.')[-1]
            mod = importlib.import_module(pack)
            class_ = getattr(mod, cl_)
            real_listener = class_(verbose)
        if modules:
            for mod in modules:
                importlib.import_module(mod)
        else:
            _walk_throw_and_import()
    except Exception:
        print(f'Something wrong with importing! Is that an existing path - {mod}?', file=sys.stderr)
        raise
    start(verbose, listener=real_listener, groups=groups, params=par)


def _is_import_in_file(file_name: str) -> bool:
    """
    Есть ли в файле импорт атеста
    :param file_name: имя модуля
    :return: True, если в модуле импортируется атест
    """
    if '.py' not in file_name:
        return False
    with open(file_name) as file:
        for line in file.readlines():
            line = line.rstrip().replace('  ', ' ')
            if any([element in line for element in look_for]):
                return True
        return False


def _walk_throw_and_import():
    """
    Функция проходит по всем модулям в текущей папке и вложенных, ищет и импортирует те модули, где есть упоминание
    атест, тем самым  формируя тест-сьют
    :return: None
    """
    for root, dirs, files in os.walk(HOME_FOLDER, topdown=True):
        for file in (f for f in files if _is_import_in_file(f'{root}\\{f}')):
            package_ = root.replace(HOME_FOLDER, '').replace('\\', '')
            file_name = file.replace('.py', '')
            name = package_ + '.' + file_name if package_ else file_name
            importlib.import_module(name, package=HOME_FOLDER)


if __name__ == '__main__':
    # если есть файл настроек то берем все оттуда
    if is_options_exists():
        params_ = read_parameters_from_file()
        start_with_parameters(params_)
    # иначе проходим по всем модулям в поисках тестов
    else:
        _walk_throw_and_import()
        start(verbose=3)
