import sys
import os
import importlib

from .runner import start

HOME_FOLDER = sys.path[0]
look_for = ('import atest', 'from atest')


def _is_import_in_file(file_name: str) -> bool:
    if '.py' not in file_name:
        return False
    with open(file_name) as file:
        for line in file.readlines():
            line = line.rstrip().replace('  ', ' ')
            if any([element in line for element in look_for]):
                return True
        return False


def _walk_throw_and_import():
    for root, dirs, files in os.walk(HOME_FOLDER, topdown=True):
        for file in (f for f in files if _is_import_in_file(f'{root}\\{f}')):
            package_ = root.replace(HOME_FOLDER, '').replace('\\', '')
            file_name = file.replace('.py', '')
            name = package_ + '.' + file_name if package_ else file_name
            importlib.import_module(name, package=HOME_FOLDER)


if __name__ == '__main__':
    _walk_throw_and_import()
    start(verbose=3)
