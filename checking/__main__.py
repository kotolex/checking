import json
import sys
import os
import importlib
import argparse
from typing import Dict, Union

from checking.runner import start
from checking.helpers.others import is_file_exists, str_date_time

HOME_FOLDER = sys.path[0]
LOOK_FOR = ('import checking', 'from checking')


def read_parameters_from_file(file_name) -> Dict:
    """
    Reads the parameters from settings file *.json, returns as a parameter dictionary.
    """
    with open(file_name, encoding='utf-8') as file:
        result = ''.join([line.rstrip() for line in file.readlines()])
    params = _get_default_params()
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
    if 'dry_run' in parameters:
        dry_run = parameters['dry_run']
        if type(dry_run) is not bool:
            raise ValueError('Dry_run parameter must be bool (True or False)!')


def _get_default_params():
    params = {'name': 'Default Test Suite', 'verbose': 0, 'groups': [], 'params': {}, 'listener': '', 'modules': [],
              'threads': 1, 'dry_run': False}
    return params


def start_with_parameters(parameters: Dict):
    params = _get_default_params()
    params.update(parameters)
    check_parameters(params)
    verbose = params.get('verbose')
    par = params.get('params')
    groups = params.get('groups')
    modules = params.get('modules')
    listener_ = params.get('listener')
    threads = params.get('threads')
    name = params.get('name')
    dry_run = params.get('dry_run')
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
    start(verbose, listener=real_listener, groups=groups, params=par, threads=threads, suite_name=name, dry_run=dry_run)


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
            if any([element in line for element in LOOK_FOR]):
                return True
    return False


def _walk_throw_and_import():
    """
    The functions runs throw all of the modules in current and nested folder, looks up and imports modules, where is a
    mention checking, thereby forming the test-suite.
    :return: None
    """
    for root, dirs, files in os.walk(HOME_FOLDER, topdown=True):
        if root.endswith(os.sep + 'checking') or os.sep + 'checking' + os.sep in root:
            continue
        for file in (f for f in files if _is_import_in_file(f'{root}{os.sep}{f}')):
            package_ = root.replace(HOME_FOLDER, '').replace(os.sep, '')
            file_name_ = file.replace('.py', '')
            name = package_ + '.' + file_name_ if package_ else file_name_
            importlib.import_module(name, package=HOME_FOLDER)


def _generate_options():
    """
    Generates default options<date+time>.json file at current folder
    :return: None
    """
    with open(f'options_{str_date_time()}.json', 'wt') as file:
        json.dump(_get_default_params(), file)


def _get_file_name(arg: Union[str, None]) -> str:
    name = 'options.json'
    if arg:
        name = arg
        if not name.endswith('.json'):
            raise ValueError('Only <name>.json files allowed! And it must contains valid json, '
                             'you can generate it with -g option')
    return name


def _get_arg_dict(arg: Union[str, None]) -> Dict:
    dic_ = {}
    if arg:
        if '=' in args.arg:
            dic_[arg.split('=')[0]] = arg.split('=')[1]
        else:
            dic_[arg] = None
    return dic_


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--options_file', help="File with the options to run")
    parser.add_argument('-a', '--arg', help="Any argument for test-suite")
    parser.add_argument('-d', '--dry_run', help="Boolean arg for dry_run (run without actual functions executed)!",
                        type=bool)
    parser.add_argument('-g', '--generate_options',
                        help="Not doing any work, just generates options.json in current folder!", action='store_const',
                        const=True)
    return parser.parse_args()


def _main_run(file_name_: str, p_: Dict, dry_run: bool):
    # if options file exists get all from there
    if is_file_exists(file_name_):
        print(f"{file_name_} found! Work with it...")
        params_ = read_parameters_from_file(file_name_)
        if p_:
            params_.get("params").update(p_)
        start_with_parameters(params_)
    # or walk recursive and find all modules with tests
    else:
        if file_name_ == 'options.json':
            print(f"No options found! Starts to look for tests in all sub-folders")
            _walk_throw_and_import()
            start(verbose=3, threads=1, params=p_, dry_run=dry_run)
        else:
            raise ValueError(f"{file_name_} not found! Stopped")


if __name__ == '__main__':
    args = parse_arguments()
    if args.generate_options:
        _generate_options()
    else:
        file_name = _get_file_name(args.options_file)
        p_ = _get_arg_dict(args.arg)
        dry_run = args.dry_run if args.dry_run else False
        _main_run(file_name, p_, dry_run)
