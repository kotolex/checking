from os import sep
from os import mkdir
from sys import _getframe
from datetime import datetime
from typing import List, Union
from checking.helpers.others import is_file_exists

from checking.classes.basic_test import Test
from checking.classes.basic_suite import TestSuite
from checking.helpers.exception_traceback import get_trace_filtered_by_filename as filtered

BASE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Results for #suite_name</title>
    <script>
        function opclose(locator) {
            return function () {
                if (document.querySelector(locator).childNodes[3].style.display === 'none') {
                    document.querySelector(locator).childNodes[3].style = 'display:block';
                } else {
                    document.querySelector(locator).childNodes[3].style = 'display:none';
                }
            }
        }
        
        function opclose_sibling(locator) {
            return function () {
                if (document.querySelector(locator).nextElementSibling.style.display === 'none') {
                    document.querySelector(locator).nextElementSibling.style = 'display:block';
                } else {
                    document.querySelector(locator).nextElementSibling.style = 'display:none';
                }
            }
        }
    </script>
</head>
<body>
<h1>Info</h1>
<p><b>Suite name:</b> #suite_name</p>
'''
FOLDER = 'test_results'


def add_text(name: str, value: str):
    """
    Add some text to test in report
    :param name: name of the parameter
    :param value: value of the parameter
    :return: None
    """
    _add_to_test(name, value)


def add_img(name: str, bytes_: bytes):
    """
    Add some picture(screenshot) to test in report
    :param name: name of parameter
    :param bytes_: bytes of picture (will be saved as png)
    :return: None
    """
    _add_to_test(name, bytes_)


def _add_to_test(name: str, value: Union[bytes, str]):
    """
    Looks for 5 frames deep in call stack to find current test and put data there
    :param name: name of parameter to add
    :param value: value of str or bytes
    :return: None
    """
    try:
        for _ in range(5):
            frame = _getframe(_)
            current_test = frame.f_locals.get('self')
            if current_test:
                if type(value) is bytes:
                    current_test.report_params[value] = str(name)
                else:
                    current_test.report_params[str(name)] = str(value)
                break
    except ValueError:
        pass  # ignored, just deletes frame
    finally:
        del frame


def generate(test_suite: TestSuite, folder_name: str = 'test_results'):
    """
    The only public method to generate html report with all test results
    :param folder_name: name for folder with results
    :param test_suite: suite to save results to report
    :return: None
    """
    global FOLDER
    if folder_name != FOLDER:
        FOLDER = folder_name
    if not is_file_exists(FOLDER):
        mkdir(FOLDER)
    html = _generate_html(test_suite)
    _write_file(html)


def _create_info(html_lines: List[str], suite: TestSuite):
    """
    Generates Info section (header) of the report. Changes in-place list argument!
    :param html_lines: list of stings of the html report
    :param suite: suite to get results from
    :return: None
    """
    html_lines[0] = html_lines[0].replace('#suite_name', suite.name)
    html_lines.append(f"<p><b>Total groups:</b> {len(suite.groups)}</p>\n")
    html_lines.append(f"<p><b>Total tests:</b> {suite.tests_count()}</p>\n<ul>\n")
    html_lines.append(f"\t<li style='color:green'>success tests: {len(suite.success())}</li>\n"
                      f"\t<li style='color:red'>failed tests: {len(suite.failed())}</li>\n"
                      f"\t<li style='color:orange'>broken tests: {len(suite.broken())}</li>\n"
                      f"\t<li style='color:grey'>ignored tests: {len(suite.ignored())}</li>\n</ul>\n")
    per_col = 'green'
    percent = len(suite.success()) / (suite.tests_count() / 100) if suite.tests_count() else 0.0
    if percent < 99:
        per_col = 'orange'
    if percent < 75:
        per_col = 'red'
    start = datetime.fromtimestamp(suite.timer.start_time).strftime('%Y-%m-%d %H:%M:%S')
    end = datetime.fromtimestamp(suite.timer.end_time).strftime('%Y-%m-%d %H:%M:%S')
    html_lines.append(f"<p><b>Success percent:</b> <b style='color:{per_col}'>{percent:.4} %</b></p>\n")
    html_lines.append(f"<p><b>Total time:</b> {suite.suite_duration():.2} seconds ({start} - {end})</p>\n")


def _generate_html(test_suite: TestSuite) -> List[str]:
    """
    Generates html in list of strings
    :param test_suite: suite to get all results from
    :return: list of strings (html code)
    """
    html_lines = [BASE, ]
    _create_info(html_lines, test_suite)
    if test_suite.is_empty():
        html_lines.append("<div id='empty'>Suite is empty! There are no tests!</div>\n")
        html_lines.append('</body>\n</html>')
        return html_lines
    count = 1
    html_lines.append('<h2>Statistics:</h2>\n')
    for group in test_suite.groups:
        group_time = float(sum(t.duration() for t in test_suite.groups.get(group).test_results))
        results = test_suite.groups.get(group).test_results
        succ = len(test_suite.groups.get(group).tests_by_status('success'))
        html_lines.append(f"<h3 id='id_g_{count}'>Group '{group}' (elapsed {group_time:.2} seconds), "
                          f"success tests {succ}/{len(results)}:\n"
                          f"\t<script>document.querySelector('#id_g_{count}')."
                          f"addEventListener('click', opclose_sibling('#id_g_{count}'))</script>\n</h3>\n"
                          f"<ol style='display: none;'>\n")
        for test in results:
            _add_test_info(test, html_lines, count)
            count += 1
        html_lines.append('</ol>\n')
    _add_all_listeners(html_lines, count)
    html_lines.append('\n</body>\n</html>')
    return html_lines


def _write_file(lines: list):
    with open(f'{FOLDER}{sep}index.html', 'wt') as file:
        file.write(''.join(lines))


def _add_all_listeners(lines: List[str], count: int):
    a_l = [f"document.querySelector('#id_{_}').addEventListener('click',opclose('#id_{_}'));" for _ in range(1, count)]
    joined = '\n'.join(a_l)
    lines.append(f"<script>{joined}</script>")


def _add_test_info(test: Test, lines: List[str], count: int):
    """
    Add info about specific test
    :param test: test to ger info from
    :param lines: list of strings og html file
    :param count: id for html tag
    :return: None
    """
    time_ = 0.0 if test.duration() < 0.01 else test.duration()
    add_ = f'[{test.argument}]' if test.provider else ''
    traceback = '' if test.reason is None else ''.join([f"<p>{_}</p>" for _ in filtered(test.reason).split('\n')])
    st_col = 'green'
    if test.status == 'broken':
        st_col = 'orange'
    if test.status == 'failed':
        st_col = 'red'
    if test.status == 'ignored':
        st_col = 'grey'
    rep_params = _get_rep_params(test, count)
    lines.append(
        f"\t<li id='id_{count}'>Test '{test.name}' {add_}: elapsed time {time_:.2} seconds, "
        f"status <b style='color:{st_col}'>{test.status}</b>\n"
        f"\t\t<div style='display: none;'>\n"
        f"\t\t\t<p><b>Description:</b> '{test.description}'</p>\n"
        f"\t\t\t<p><b>Argument:</b> {test.argument}</p>\n"
        f"\t\t\t<p><b>Attempt number:</b> {test.retries}</p>\n"
        f"\t\t\t<p><b>Status:</b> <b style='color:{st_col}'>{test.status.upper()}</b></p>\n"
        f"\t\t\t<p><b>Duration:</b> {time_:.3} seconds</p>\n"
        f"\t\t\t{'-' * 30}\n"
        f"{traceback}\n"
        f"\t\t\t<p style='color:red'><b>Exception:</b> {str(test.reason).replace('<', '&lt;')}</p>\n"
        f"\t\t\t{'-' * 30}\n"
        f"{rep_params}"
        f"\t\t</div>\n\t</li>\n")


def _get_rep_params(test, count):
    """
    Add info attached to test (text ot image)
    :param test: test to get info from
    :param count: id for element
    :return: None
    """
    rep_params = ''
    if not test.report_params:
        return ''
    for key, value in test.report_params.items():
        if type(key) is str:
            rep_params += f"\t\t\t<p>Report parameter <b>'{key}'</b>: {value}</p>\n"
        else:
            with open(f'{FOLDER}{sep}test_id_count_{count}.png', 'wb') as f:
                f.write(key)
            rep_params += f"\t\t\t<p>Report parameter <b>'{value}'</b>:</p>\n\t\t\t" \
                          f"<img src='test_id_count_{count}.png' alt='{value}'>\n"
    return rep_params
