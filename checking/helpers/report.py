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
    </script>
  </head>
  <body>
    <h1>Info</h1>
    <p>Suite name: #suite_name</p>
'''

html_lines = [BASE, ]


def generate(file_name: str, test_suite: TestSuite):
    html_lines[0] = html_lines[0].replace('#suite_name', test_suite.name)
    html_lines.append(f"<p>Total groups: {len(test_suite.groups)}</p>")
    html_lines.append(f"<p>Total tests: {test_suite.tests_count()}</p>\n<ul>")
    html_lines.append(f"<li>success tests: {len(test_suite.success())}</li>\n"
                      f"<li>failed tests: {len(test_suite.failed())}</li>\n"
                      f"<li>broken tests: {len(test_suite.broken())}</li>\n"
                      f"<li>ignored tests: {len(test_suite.ignored())}</li></ul>\n")

    html_lines.append(f"<p>Success percent: {len(test_suite.success()) / (test_suite.tests_count() / 100):.4} %</p>\n")
    html_lines.append(f"<p>Total time: {test_suite.suite_duration():.2} seconds</p>\n")
    if test_suite.is_empty():
        html_lines.append("<div id='empty'>Suite is empty! There are no tests!</div>\n")
    else:
        count = 1
        html_lines.append('<h2>Statistics:</h2>\n')
        for group in test_suite.groups:
            group_time = sum(t.duration() for t in test_suite.groups.get(group).test_results)
            html_lines.append(f"<h3>Group '{group}' (elapsed {group_time:.2} seconds):</h3>\n<ol>\n")
            for test in test_suite.groups.get(group).test_results:
                time_ = test.duration()
                if time_ < 0.01:
                    time_ = 0.0
                html_lines.append(
                    f"<li id='id_{count}'>Test '{test.name}': elapsed time {time_:.2} seconds, status <b>{test.status}</b>\n"
                    f"<div style='display: none;'>\n"
                    f"<p>Description:'{test.description}'</p>"
                    f"<p>Argument: {test.argument}</p>"
                    f"<p>Attempt number: {test.retries}</p>"
                    f"<p>Status: {test.status.upper()}</p>"
                    f"<p>Duration: {time_:.3} seconds</p>"
                    f"<p>Exception: {str(test.reason).replace('<', '&lt;')}</p>"
                    f"</div>\n"
                    f"</li>\n")
                count += 1
            html_lines.append('</ol>\n')
        for _ in range(1, count):
            html_lines.append(f"<script>document.querySelector('#id_{_}').addEventListener('click', "
                              f"opclose('#id_{_}'))</script>")
    html_lines.append('</body>\n</html>')
    with open(f'{file_name}.html', 'wt') as file:
        file.write(''.join(html_lines))
