import os
import shutil

from os.path import sep
from unittest import main, TestCase

from checking import test_break, TestBrokenException
from checking.annotations import test
from checking.helpers.report import _add_text, _add_img, generate
from checking.classes.basic_suite import TestSuite
from tests.fixture_behaviour_test import clear


class TestReport(TestCase):

    def test_add_text(self):
        def _():
            _add_text("A", "B")

        clear()
        test(_)
        t = list(TestSuite.get_instance().groups.values())[0].tests[0]
        t.run()
        self.assertEqual({'A': 'B'}, t.report_params)

    def test_add_img(self):
        def _():
            _add_img("A", b"B")

        clear()
        test(_)
        t = list(TestSuite.get_instance().groups.values())[0].tests[0]
        t.run()
        self.assertEqual({b'B': 'A'}, t.report_params)

    def test_generate_empty(self):
        clear()
        generate(TestSuite.get_instance())

        with open(f'{os.getcwd()}{sep}test_results{sep}index.html') as f:
            rep = ''.join([line for _, line in enumerate(f.readlines()) if _ != 64])

        shutil.rmtree(f'{os.getcwd()}{sep}test_results')

        self.assertEqual(rep, """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Results for Default Test Suite</title>
    <link rel="stylesheet" href="css/materialize.css">
    <link rel="stylesheet" href="css/roboto.css">
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
<body class="blue-grey lighten-5">
<h1 style="text-align: center;" class="card-panel teal blue-grey darken-4 z-depth-3"><span
        style="color: #eceff1; font-family: 'Roboto', sans-serif;">Info</span></h1>
<table style="width: 80%; margin-left: auto; margin-right: auto; font-family: 'Roboto', sans-serif;">
    <tbody>
    <tr>
        <td><b>Suite name:</b></td>
        <td>Default Test Suite</td>
    </tr>
    <tr>
        <td><b>Total groups:</b></td>
        <td>0</td>
    </tr>
    <tr>
        <td><b>Total tests:</b></td>
        <td>0</td>
    </tr>
    <tr>
        <td>&nbsp;&nbsp;&nbsp;<b style="color: #2e7d32">succeeded:</b></td>
        <td><span style="color: #2e7d32">0</span></td>
    </tr>
    <tr>
        <td>&nbsp;&nbsp;&nbsp;<b style="color: #d50000">failed:</b></td>
        <td><span style="color: #d50000">0</span></td>
    </tr>
    <tr>
        <td>&nbsp;&nbsp;&nbsp;<b style="color: #ff6f00">broken:</b></td>
        <td><span style="color: #ff6f00">0</span></td>
    </tr>
    <tr>
        <td>&nbsp;&nbsp;&nbsp;<b style="color: #757575">ignored:</b></td>
        <td><span style="color: #757575">0</span></td>
    </tr>
    <td>
        <b>Success percent: </b><b style='color: #d50000'>0.0 %</b><br/>
    </td>
    </tbody>
</table>

<div style="width: 80%; margin-left: auto; margin-right: auto; font-family: 'Roboto', sans-serif;">
    <h2>Statistics:</h2>
<div id='empty'>No tests found in the suite!</div>

</div>
</body>
</html>""")

    def test_generate_normal(self):
        def _1():
            assert True is True, 'pass'

        def _2():
            assert True is False, 'fail'

        def _3():
            test_break()

        clear()
        test(_1)
        test(_2)
        test(_3)
        suite = TestSuite.get_instance()
        ts = list(suite.groups.values())[0].tests

        ts[0].run()
        with self.assertRaises(AssertionError):
            ts[1].run()
        with self.assertRaises(TestBrokenException):
            ts[2].run()

        generate(suite)

        with open(f'{os.getcwd()}{sep}test_results{sep}index.html') as f:
            rep = ''.join([line for _, line in enumerate(f.readlines()) if _ != 64])

        shutil.rmtree(f'{os.getcwd()}{sep}test_results')

        self.assertEqual(rep, """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Results for Default Test Suite</title>
    <link rel="stylesheet" href="css/materialize.css">
    <link rel="stylesheet" href="css/roboto.css">
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
<body class="blue-grey lighten-5">
<h1 style="text-align: center;" class="card-panel teal blue-grey darken-4 z-depth-3"><span
        style="color: #eceff1; font-family: 'Roboto', sans-serif;">Info</span></h1>
<table style="width: 80%; margin-left: auto; margin-right: auto; font-family: 'Roboto', sans-serif;">
    <tbody>
    <tr>
        <td><b>Suite name:</b></td>
        <td>Default Test Suite</td>
    </tr>
    <tr>
        <td><b>Total groups:</b></td>
        <td>1</td>
    </tr>
    <tr>
        <td><b>Total tests:</b></td>
        <td>3</td>
    </tr>
    <tr>
        <td>&nbsp;&nbsp;&nbsp;<b style="color: #2e7d32">succeeded:</b></td>
        <td><span style="color: #2e7d32">0</span></td>
    </tr>
    <tr>
        <td>&nbsp;&nbsp;&nbsp;<b style="color: #d50000">failed:</b></td>
        <td><span style="color: #d50000">0</span></td>
    </tr>
    <tr>
        <td>&nbsp;&nbsp;&nbsp;<b style="color: #ff6f00">broken:</b></td>
        <td><span style="color: #ff6f00">0</span></td>
    </tr>
    <tr>
        <td>&nbsp;&nbsp;&nbsp;<b style="color: #757575">ignored:</b></td>
        <td><span style="color: #757575">0</span></td>
    </tr>
    <td>
        <b>Success percent: </b><b style='color: #d50000'>0.0 %</b><br/>
    </td>
    </tbody>
</table>

<div style="width: 80%; margin-left: auto; margin-right: auto; font-family: 'Roboto', sans-serif;">
    <h2>Statistics:</h2>
<h4 id='id_g_1' style='cursor: pointer;'>Group 'report_test' (elapsed 0.0 seconds), succeeded tests 0/0:
    <script>document.querySelector('#id_g_1').addEventListener('click', opclose_sibling('#id_g_1'))</script>
</h4>
<ol style='display: none;'>
</ol>
<script></script>
</div>
</body>
</html>""")


if __name__ == '__main__':
    main()
