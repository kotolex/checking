from typing import List

from checking.classes.basic_test import Test
from checking.classes.basic_suite import TestSuite

BASE = '''
<!DOCTYPE html>
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
    <p>Suite name: #suite_name</p>
'''


def _create_info(html_lines: List[str], test_suite: TestSuite):
    html_lines[0] = html_lines[0].replace('#suite_name', test_suite.name)
    html_lines.append(f"<p>Total groups: {len(test_suite.groups)}</p>")
    html_lines.append(f"<p>Total tests: {test_suite.tests_count()}</p>\n<ul>")
    html_lines.append(f"<li>success tests: {len(test_suite.success())}</li>\n"
                      f"<li>failed tests: {len(test_suite.failed())}</li>\n"
                      f"<li>broken tests: {len(test_suite.broken())}</li>\n"
                      f"<li>ignored tests: {len(test_suite.ignored())}</li></ul>\n")
    html_lines.append(f"<p>Success percent: {len(test_suite.success()) / (test_suite.tests_count() / 100):.4} %</p>\n")
    html_lines.append(f"<p>Total time: {test_suite.suite_duration():.2} seconds</p>\n")


def generate(file_name: str, test_suite: TestSuite):
    html_lines = [BASE, ]
    _create_info(html_lines, test_suite)
    if test_suite.is_empty():
        html_lines.append("<div id='empty'>Suite is empty! There are no tests!</div>\n")
        html_lines.append('</body>\n</html>')
        _write_file(file_name, html_lines)
        return
    count = 1
    html_lines.append('<h2>Statistics:</h2>\n')
    for group in test_suite.groups:
        group_time = sum(t.duration() for t in test_suite.groups.get(group).test_results)
        results = test_suite.groups.get(group).test_results
        succ = len(test_suite.groups.get(group).tests_by_status('success'))
        html_lines.append(f"<h3 id='id_g_{count}'>Group '{group}' (elapsed {group_time:.2} seconds), "
                          f"success tests {succ}/{len(results)}:\n"
                          f"<script>document.querySelector('#id_g_{count}')."
                          f"addEventListener('click',opclose_sibling('#id_g_{count}'))</script>\n</h3>\n"
                          f"<ol style='display: none;'>\n")
        for test in results:
            _add_test_info(test, html_lines, count)
            count += 1
        html_lines.append('</ol>\n')
    _add_all_listeners(html_lines, count)
    html_lines.append('</body>\n</html>')
    _write_file(file_name, html_lines)


def _write_file(file_name: str, lines: list):
    with open(f'{file_name}.html', 'wt') as file:
        file.write(''.join(lines))


def _add_all_listeners(lines: List[str], count: int):
    for _ in range(1, count):
        lines.append(f"<script>document.querySelector('#id_{_}').addEventListener('click',opclose('#id_{_}'))</script>")


def _add_test_info(test: Test, lines: List[str], count: int):
    time_ = test.duration()
    if time_ < 0.01:
        time_ = 0.0
    add_ = ''
    if test.provider:
        add_ = f'[{test.argument}]'
    lines.append(
        f"<li id='id_{count}'>Test '{test.name}' {add_}: elapsed time {time_:.2} seconds, status <b>{test.status}</b>\n"
        f"<div style='display: none;'>\n"
        f"<p>Description:'{test.description}'</p>"
        f"<p>Argument: {test.argument}</p>"
        f"<p>Attempt number: {test.retries}</p>"
        f"<p>Status: {test.status.upper()}</p>"
        f"<p>Duration: {time_:.3} seconds</p>"
        f"<p>Exception: {str(test.reason).replace('<', '&lt;')}</p>"
        f"</div>\n"
        f"</li>\n")
