import glob
import json
import sys
import os
import importlib
import argparse
from typing import Dict

from checking.runner import start

HOME_FOLDER = sys.path[0]
look_for = ('import checking', 'from checking')


def is_options_exists(file_name: str) -> bool:
    """
    Tells, if there is settings file called options.json inside the start folder.
    :return: True, if the file exists
    """
    return len(glob.glob(file_name)) == 1


def read_parameters_from_file(file_name) -> Dict:
    """
    Reads the parameters from settings file called options.json, returns as a parameter dictionary.
    """
    with open(file_name, encoding='utf-8') as file:
        result = ''.join([line.rstrip() for line in file.readlines()])
    params = {'verbose': 0, 'groups': [], 'params': {}, 'listener': '', 'modules': [], 'threads': 1}
    params.update(json.loads(result))
    return params


def check_parameters(parameters: Dict):
    """
    Checks the validation of start parameters.
    :param parameters: the dictionary with parameters
    :return: None
    :raises ValueError if the parameters are invalid
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
    threads = parameters['threads']
    if type(threads) is not int:
        raise ValueError('Threads parameter must be int (>=1)!')


def start_with_parameters(parameters: Dict):
    params = {'name': 'Default Test Suite', 'verbose': 0, 'groups': [], 'params': {}, 'listener': '', 'modules': [],
              'threads': 1}
    params.update(parameters)
    check_parameters(params)
    verbose = params.get('verbose')
    par = params.get('params')
    groups = params.get('groups')
    modules = params.get('modules')
    listener_ = params.get('listener')
    threads = params.get('threads')
    name = params.get('name')
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
    start(verbose, listener=real_listener, groups=groups, params=par, threads=threads, suite_name = name)


def _is_import_in_file(file_name: str) -> bool:
    """
    If there checking import within the file.
    :param file_name: is the name of the module
    :return: True, if asserts imports inside the module
    """
    if not file_name.endswith('.py'):
        return False
    with open(file_name, encoding='utf-8') as file:
        for line in file.readlines():
            line = line.rstrip().replace('  ', ' ')
            if any([element in line for element in look_for]):
                return True
        return False


def _walk_throw_and_import():
    """
    The functions runs throw all of the modules in current and nested folder, looks up and imports modules, where is a
    mention checking, thereby forming the test-suite.
    :return: None
    """
    for root, dirs, files in os.walk(HOME_FOLDER, topdown=True):
        for file in (f for f in files if _is_import_in_file(f'{root}\\{f}')):
            package_ = root.replace(HOME_FOLDER, '').replace('\\', '')
            file_name = file.replace('.py', '')
            name = package_ + '.' + file_name if package_ else file_name
            importlib.import_module(name, package=HOME_FOLDER)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--options_file', help="File with the options to run")
    args = parser.parse_args()
    file_name = 'options.json'
    if args.options_file:
        file_name = args.options_file
    # если есть файл настроек то берем все оттуда
    if is_options_exists(file_name):
        print(f"{file_name} found! Work with it...")
        params_ = read_parameters_from_file(file_name)
        start_with_parameters(params_)
    # иначе проходим по всем модулям в поисках тестов
    else:
        print(f"No options found! Starts to look for tests in all sub-folders")
        _walk_throw_and_import()
        start(verbose=3, threads=1)
