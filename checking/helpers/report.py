from os import sep, chdir, mkdir, path
from sys import _getframe
from datetime import datetime
from typing import List, Union

from checking.helpers.others import is_file_exists
from checking.classes.basic_test import Test
from checking.classes.basic_suite import TestSuite
from checking.helpers.exception_traceback import get_trace_filtered_by_filename as filtered

__all__ = [
    'generate',
]

# HTML report output folder
FOLDER = 'test_results'


def _add_text(name: str, value: str):
    """
    Convenience wrapper for **_add_to_test()**, handles textual data.

    :param name: text parameter name
    :param value: text parameter value
    :return: None
    """
    _add_to_test(name, value)


def _add_img(name: str, bytes_: bytes):
    """
    Convenience wrapper for **_add_to_test()**, handles binary (image) data.

    :param name: image parameter name
    :param bytes_: image parameter data
    :return: None
    """
    _add_to_test(name, bytes_)


def _add_to_test(name: str, value: Union[bytes, str]):
    """
    Helper, locates the current test instance by searching the last five stack frames,
    then adds the specified report parameter data to the located test instance.
    Data is added via the **Test** class **report_params** property.

    :param name: parameter name
    :param value: parameter data
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
        pass    # ran out of stack frames, ignore the error and delete the frame reference
    finally:
        del frame


def generate(test_suite: TestSuite):
    """
    Generates an HTML report containing the test suite execution results.

    :param test_suite: TestSuite instance to build the report for
    :return: None
    """
    path_to_template = is_file_exists.__globals__['__spec__'].origin
    full_path = path.join(path.split(path_to_template)[0], 'index_real.html')
    css_path = path.join(path.split(path_to_template)[0], 'materialize.css')
    roboto_path = path.join(path.split(path_to_template)[0], 'roboto.css')
    if not is_file_exists(FOLDER):
        mkdir(FOLDER)
        chdir(FOLDER)
        if not is_file_exists('css'):
            mkdir('css')
        chdir('..')
    with open(f'{FOLDER}{sep}index.html', 'wt') as file, open(full_path) as template:
        file.write(template.read())
    with open(f'{FOLDER}{sep}css{sep}materialize.css', 'wt') as file, open(css_path) as template:
        file.write(template.read())
    with open(f'{FOLDER}{sep}css{sep}roboto.css', 'wt') as file, open(roboto_path) as template:
        file.write(template.read())
    html = _generate_html(test_suite)
    _write_file(html)


def _create_info(html: str, suite: TestSuite) -> str:
    """
    Helper, generates the report header (info section).

    :param html: html report string
    :param suite: TestSuite instance to generate the report for
    :return: HTML string with the added report header
    """
    per_col = '#2e7d32'
    percent = len(suite.success()) / (suite.tests_count() / 100) if suite.tests_count() else 0.0
    if percent < 99:
        per_col = '#ff6f00'
    if percent < 75:
        per_col = '#d50000'
    start = datetime.fromtimestamp(suite.timer.start_time).strftime('%Y-%m-%d %H:%M:%S')
    end = datetime.fromtimestamp(suite.timer.end_time).strftime('%Y-%m-%d %H:%M:%S')
    html = html.replace('#suite_name', suite.name) \
        .replace('#total_groups', str(len(suite.groups))) \
        .replace('#total_tests', str(suite.tests_count())) \
        .replace('#success_tests', str(len(suite.success()))) \
        .replace('#failed_tests', str(len(suite.failed()))) \
        .replace('#broken_tests', str(len(suite.broken()))) \
        .replace('#ignored_tests', str(len(suite.ignored()))) \
        .replace('#percent', f"<b style='color: {per_col}'>0.0 %</b>") \
        .replace('#total_time', f"{suite.suite_duration():.2} seconds ({start} - {end})")
    return html


def _generate_html(test_suite: TestSuite) -> List[str]:
    """
    Helper, generates HTML strings for each test group in a suite.

    :param test_suite: TestSuite instance to generate the report for
    :return: list of HTML strings, each containing the test results for a test group
    """
    with open(f'{FOLDER}{sep}index.html') as template:
        base = ''.join(template.readlines())
    base = _create_info(base, test_suite)
    html_lines = [base, ]
    if test_suite.is_empty():
        html_lines.append("<div id='empty'>Suite is empty! There are no tests!</div>\n")
        html_lines.append('</body>\n</html>')
        return html_lines
    count = 1
    for group in test_suite.groups:
        group_time = float(sum(t.duration() for t in test_suite.groups.get(group).test_results))
        results = test_suite.groups.get(group).test_results
        succ = len(test_suite.groups.get(group).tests_by_status('success'))
        html_lines.append(
            f"<h4 id='id_g_{count}' style='cursor: pointer;'>Group '{group}' (elapsed {group_time:.2} seconds), "
            f"success tests {succ}/{len(results)}:\n"
            f"\t<script>document.querySelector('#id_g_{count}')."
            f"addEventListener('click', opclose_sibling('#id_g_{count}'))</script>\n</h4>\n"
            f"<ol style='display: none;'>\n")
        for test in results:
            _add_test_info(test, html_lines, count)
            count += 1
        html_lines.append('</ol>\n')
    _add_all_listeners(html_lines, count)
    html_lines.append('\n</body>\n</html>')
    return html_lines


def _write_file(lines: List[str]):
    """
    Helper, writes a list of strings to report's index.html file.

    :param lines: list of prepared report HTML strings
    :return:
    """
    with open(f'{FOLDER}{sep}index.html', 'wt') as file:
        file.write(''.join(lines))


def _add_all_listeners(lines: List[str], count: int):
    """
    Helper, adds JavaScript event listeners to the report.

    :param lines: list of report HTML strings
    :param count: number of sections to add listeners to
    :return:
    """
    a_l = [f"document.querySelector('#id_{_}').addEventListener('click',opclose('#id_{_}'));" for _ in range(1, count)]
    joined = '\n'.join(a_l)
    lines.append(f"<script>{joined}</script>")


def _add_test_info(test: Test, lines: List[str], count: int):
    """
    Helper, adds info header for a specific test.

    :param test: Test instance to generate info for
    :param lines: list of report HTML strings
    :param count: test case id number to use in the HTML tag
    :return: None
    """
    time_ = 0.0 if test.duration() < 0.01 else test.duration()
    add_ = f'[{test.argument}]' if test.provider else ''
    traceback = '' if test.reason is None else ''.join([f"<p>{_}</p>" for _ in filtered(test.reason).split('\n')])
    st_col = '#2e7d32'
    if test.status == 'broken':
        st_col = '#ff6f00'
    if test.status == 'failed':
        st_col = '#d50000'
    if test.status == 'ignored':
        st_col = 'grey'
    rep_params = _get_rep_params(test, count)
    lines.append(
        f"\t<li id='id_{count}' style='cursor: pointer;'>Test '{test.name}' {add_}: elapsed time {time_:.2} seconds, "
        f"status <b style='color:{st_col}'>{test.status}</b>\n"
        f"\t\t<div style='display: none;'>\n<table style='width: 80%; margin-left: auto; margin-right: auto; font-family: 'Roboto', sans-serif;'>\n<tbody>\n"
        f"\t\t\t<tr><td><b>Description:</b></td><td>'{test.description}'</td></tr>\n"
        f"\t\t\t<tr><td><b>Argument:</b></td><td> {test.argument}</td></tr>\n"
        f"\t\t\t<tr><td><b>Attempt number:</b></td><td> {test.retries}</td></tr>\n"
        f"\t\t\t<tr><td><b>Status:</b></td><td><b style='color:{st_col}'>{test.status.upper()}</b></td></tr>\n"
        f"\t\t\t<tr><td><b>Duration:</b></td><td> {time_:.3} seconds</td></tr>\n</tbody>\n</table>\n"
        f"{traceback}\n"
        f"\t\t\t<p style='color: {st_col}'><b>Exception:</b> {str(test.reason).replace('<', '&lt;')}</p><hr/>\n"
        f"{rep_params}"
        f"\t\t</div>\n\t</li>\n")


def _get_rep_params(test: Test, count: int) -> str:
    """
    Helper, adds additional data (text or image to the test's HTML string.

    :param test: Test instance to generate info for
    :param count: test case id number to use in the HTML tags and image file names.
    :return: test case additional info HTML string
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
