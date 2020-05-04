import os
import sys
import json
import argparse
import importlib
from typing import Dict, Union

from checking.runner import start
from checking.helpers.others import str_date_time
from checking.helpers.others import is_file_exists

HOME_FOLDER = sys.path[0]
LOOK_FOR = ('import checking', 'from checking')


def read_parameters_from_file(file_name_: str) -> Dict:
    """
    Reads the parameters from settings file *.json, returns as a parameter dictionary.
    """
    with open(file_name_, encoding='utf-8') as file:
        result = ''.join([line.rstrip() for line in file.readlines()])
    parameters = _get_default_params()
    parameters.update(json.loads(result))
    return parameters


def check_parameters(parameters: Dict):
    """
    Checks the validation of start parameters.
    :param parameters: the dictionary with parameters
    :return: None
    :raises ValueError if the parameters are invalid
    """
    schema = {bool: ['dry_run'], str: ['suite_name', 'listener', 'filter_by_name'], int: ['threads', 'verbose'],
              list: ['modules', 'groups'], dict: ['params']}
    for key, value in schema.items():
        for element in value:
            if element not in parameters:
                continue
            if type(parameters[element]) is not key:
                raise ValueError(f'{element.capitalize()} parameter must be {key}!')
    for name in schema.get(list):
        if name not in parameters:
            continue
        if any(filter(lambda x: type(x) is not str, parameters[name])):
            raise ValueError(f'{name.capitalize()} parameter must be list of strings (List[str])!')


def _get_default_params():
    parameters = {'suite_name': 'Default Test Suite', 'verbose': 0, 'groups': [], 'params': {}, 'listener': '',
                  'modules': [], 'threads': 1, 'dry_run': False, 'filter_by_name': ''}
    return parameters


def start_with_parameters(parameters: Dict):
    params_ = _get_default_params()
    params_.update(parameters)
    check_parameters(params_)
    modules = params_.get('modules')
    listener_ = params_.get('listener')
    try:
        if listener_:
            pack = '.'.join(listener_.split('.')[:-1])
            cl_ = listener_.split('.')[-1]
            mod = importlib.import_module(pack)
            class_ = getattr(mod, cl_)
            params_['listener'] = class_(params_['verbose'])
        if modules:
            for mod in modules:
                importlib.import_module(mod)
        else:
            _walk_throw_and_import()
    except Exception:
        print(f'Something wrong with importing! Is that an existing path - {mod}?', file=sys.stderr)
        raise
    start(**params_)


def _is_import_in_file(file_name_: str) -> bool:
    """
    If there checking import within the file.
    :param file_name_: is the name of the module
    :return: True, if asserts imports inside the module
    """
    with open(file_name_, encoding='utf-8') as file:
        for line in file:
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
        if root.endswith(os.sep + 'checking') or (os.sep + 'checking' + os.sep in root):
            continue
        files = (file for file in files if file.endswith(".py"))
        for file in (f for f in files if _is_import_in_file(f'{root}{os.sep}{f}')):
            file_name_ = file.replace('.py', '')
            try:
                package_ = root.replace(HOME_FOLDER, '').replace(os.sep, '')
                name = package_ + '.' + file_name_ if package_ else file_name_
                importlib.import_module(name, package=HOME_FOLDER)
            except ModuleNotFoundError:
                sys.path.append(root)
                importlib.import_module(file_name_)


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
        if '=' in arg:
            key, value = arg.split("=")
            dic_[key] = value
        else:
            dic_[arg] = None
    return dic_


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--options_file', help="File with the options to run. "
                                                     "If specified, -d and -f options will be ignored!")
    parser.add_argument('-f', '--filter_test', help="Filter tests by name, only tests, whose names"
                                                    " contain this value will run!")
    parser.add_argument('-a', '--arg', help="Any argument for your test-suite")
    parser.add_argument('-d', '--dry_run', help="Dry-run for test-suite(run without actual functions executed)!",
                        action='store_const', const=True)
    parser.add_argument('-g', '--generate_options',
                        help="Not doing any work, just generates options.json in current folder!", action='store_const',
                        const=True)
    return parser.parse_args()


def _main_run(file_name_: str, p_: Dict, dry_run_: bool, filter_by_name_: str):
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
            start(verbose=3, threads=1, params=p_, dry_run=dry_run_, filter_by_name=filter_by_name_)
        # if options file was specified and not exists, than stop
        else:
            raise ValueError(f"{file_name_} not found! Stopped")


if __name__ == '__main__':
    args = parse_arguments()
    if args.generate_options:
        _generate_options()
    else:
        file_name = _get_file_name(args.options_file)
        params = _get_arg_dict(args.arg)
        dry_run = args.dry_run if args.dry_run else False
        filter_by_name = args.filter_test if args.filter_test else ''
        _main_run(file_name, params, dry_run, filter_by_name)
