from unittest import main as main_unit
from unittest import TestCase

from checking import __main__ as m

PARAMETERS = {'suite_name': 'Default Test Suite', 'verbose': 0, 'groups': [], 'params': {}, 'listener': '',
              'modules': [], 'threads': 1, 'dry_run': False, 'filter_by_name': ''}


class MainTest(TestCase):

    def test_read_parameters_from_file_name_field(self):
        dic_ = m.read_parameters_from_file('tests/files/op.json')
        self.assertEqual(dic_.get('suite_name'), "Test")

    def test_read_parameters_from_file_full_dict(self):
        dic_ = m.read_parameters_from_file('tests/files/op2.json')
        self.assertEqual(dic_, PARAMETERS)

    def test_read_parameters_from_file_full_changed_dict(self):
        expect = {'suite_name': 'Test', 'verbose': 3, 'groups': ['one'], 'params': {'1': 1}, 'listener': 'default',
                  'modules': ['test'], 'threads': 2, 'dry_run': True, 'filter_by_name': 'test'}
        dic_ = m.read_parameters_from_file('tests/files/op3.json')
        self.assertEqual(dic_, expect)

    def test_get_default_parameters(self):
        self.assertEqual(PARAMETERS, m._get_default_params())

    def test_check_param_verbose(self):
        dic_ = {'verbose': 'a'}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_verbose_ok(self):
        dic_ = {'verbose': 3}
        m.check_parameters(dic_)

    def test_check_param_verbose_None(self):
        dic_ = {'verbose': None}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_name(self):
        dic_ = {'suite_name': 1}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_name_ok(self):
        dic_ = {'suite_name': '1'}
        m.check_parameters(dic_)

    def test_check_param_groups_ok(self):
        dic_ = {'groups': []}
        m.check_parameters(dic_)

    def test_check_param_groups_failed(self):
        dic_ = {'groups': 'sdsd'}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_groups_only_str_failed(self):
        dic_ = {'groups': [1, 2]}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_groups_only_str_ok(self):
        dic_ = {'groups': ['1', '2']}
        m.check_parameters(dic_)

    def test_check_param_mod_ok(self):
        dic_ = {'modules': []}
        m.check_parameters(dic_)

    def test_check_param_mod_failed(self):
        dic_ = {'modules': 'sdsd'}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_mod_only_str_failed(self):
        dic_ = {'modules': [1, 2]}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_mod_only_str_ok(self):
        dic_ = {'modules': ['1', '2']}
        m.check_parameters(dic_)

    def test_check_param_params_ok(self):
        dic_ = {'params': {}}
        m.check_parameters(dic_)

    def test_check_param_params_failed(self):
        dic_ = {'params': 1}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_params_failed_str(self):
        dic_ = {'params': "1"}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_params_list(self):
        dic_ = {'params': [1]}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_params_failed_None(self):
        dic_ = {'params': None}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_mod_failed_None(self):
        dic_ = {'modules': 1}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_groups_failed_None(self):
        dic_ = {'groups': None}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_listener_failed_None(self):
        dic_ = {'listener': None}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_listener_failed_int(self):
        dic_ = {'listener': 1}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_listener_fail_if_no_module(self):
        with self.assertRaises(ValueError):
            dic_ = {'listener': "1"}
            m.check_parameters(dic_)

    def test_check_param_listener_ok(self):
        dic_ = {'listener': "module.1"}
        m.check_parameters(dic_)

    def test_check_param_threads_failed_None(self):
        dic_ = {'threads': None}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_threads_failed_str(self):
        dic_ = {'threads': "1"}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_threads_listener_ok(self):
        dic_ = {'threads': 1}
        m.check_parameters(dic_)

    def test_check_param_dry_run_failed_None(self):
        dic_ = {'dry_run': None}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_dry_run_failed_int(self):
        dic_ = {'dry_run': 1}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_dry_run_listener_ok(self):
        dic_ = {'dry_run': False}
        m.check_parameters(dic_)

    def test_check_param_filter_by_name_failed_None(self):
        dic_ = {'filter_by_name': None}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_param_filter_by_name_failed_int(self):
        dic_ = {'filter_by_name': 1}
        with self.assertRaises(ValueError):
            m.check_parameters(dic_)

    def test_check_filter_by_name_listener_ok(self):
        dic_ = {'filter_by_name': "False"}
        m.check_parameters(dic_)

    def test_check_filter_by_name_listener_ok_empty(self):
        dic_ = {'filter_by_name': ""}
        m.check_parameters(dic_)

    def test_check_import_in_file_false(self):
        self.assertFalse(m._is_import_in_file('tests/files/test_data.txt'))

    def test_check_import_in_file_ok(self):
        self.assertTrue(m._is_import_in_file('tests/files/_not_.py'))

    def test_check_import_from_in_file_ok(self):
        self.assertTrue(m._is_import_in_file('tests/files/_not_2.py'))

    def test_get_file_name_ok(self):
        self.assertEqual('options.json', m._get_file_name(None))

    def test_get_file_name_ok_full(self):
        self.assertEqual('options2.json', m._get_file_name('options2.json'))

    def test_get_file_name_ok_failed(self):
        with self.assertRaises(ValueError):
            m._get_file_name('options2.js')

    def test_get_arg_dict(self):
        self.assertEqual({}, m._get_arg_dict(None))

    def test_get_arg_dict_simple(self):
        self.assertEqual({"1": None}, m._get_arg_dict("1"))

    def test_get_arg_dict_simple_value(self):
        self.assertEqual({"1": "1"}, m._get_arg_dict("1=1"))


if __name__ == '__main__':
    main_unit()
