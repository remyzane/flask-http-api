import os
import json
from flask import request
from fair.plugin.jsonp import JsonP
from . import to_html


class TestsUI(object):

    def get_case(self, user, view, method):
        raise NotImplementedError

    def save_case(self, user, api_path, method, param_mode, params, code):
        raise NotImplementedError

    def save_config(self, user, api_path, method, post_type, json_p, params):
        raise NotImplementedError

    @staticmethod
    def params_not_equal(old_params, new_params):
        for param in old_params:
            if old_params[param] != new_params.get(param):
                return True
        for param in new_params:
            if new_params[param] != old_params.get(param):
                return True
        return False


class TestsStandaloneUI(TestsUI):

    def __init__(self, workspace, params=None):
        self.workspace = workspace

    def get_case(self, user, view, method):
        context = {'curr_api_config': {}, 'curr_api_json_p': None}
        api_config_path = os.path.join(self.curr_case_dir(user, view.uri, method.__name__.upper()), '__config__')
        if os.path.exists(api_config_path):
            with open(api_config_path, 'r') as config:
                context['curr_api_config'] = json.load(config)

        title, description = method.element.title, method.element.description
        context['curr_api_uri'] = view.uri
        context['curr_api_path'] = 'http://' + request.environ['HTTP_HOST'] + view.uri
        context['curr_api_method'] = method.__name__.upper()
        context['curr_api_params'] = get_curr_api_params(method.element.param_list, context.get('curr_api_config'))
        context['curr_api_description'] = to_html(title + (os.linesep*2 if description else '') + description)
        context['curr_api_params_config'] = {}
        context['curr_api_codes'] = self.get_sorted_code(user, view, method)

        for plugin in method.element.plugins:
            if isinstance(plugin, JsonP):
                context['curr_api_json_p'] = plugin.callback_field_name
        return context

    def curr_case_dir(self, user, curr_api_uri, method_name):
        api_path = '_'.join(curr_api_uri[1:].split('/'))
        case_dir = os.path.realpath(os.path.join(self.workspace, 'test_ui', user, api_path, method_name))
        if not os.path.exists(case_dir):
            os.makedirs(case_dir)
        return case_dir

    def save_case(self, user, api_path, method, param_mode, params, code):
        result = []
        case_path = os.path.join(self.curr_case_dir(user, api_path, method), code)
        new_data = json.dumps({
            'param_mode': param_mode,
            'params': params
        }) + os.linesep
        # read old record
        if os.path.exists(case_path):
            data_file = open(case_path, 'r')
            for line in data_file.readlines():
                line_data = json.loads(line)
                if line_data['param_mode'] != param_mode or self.params_not_equal(line_data['params'], params):
                    result.append(line)
            data_file.close()
        # add new record
        result.append(new_data)

        # save the latest 10 record
        data_file = open(case_path, 'w')
        for line in result[-10:]:
            data_file.write(line)
        data_file.close()
        return {'result': 'success'}

    def save_config(self, user, api_path, method, post_type, json_p, params):
        config_path = os.path.join(self.curr_case_dir(user, api_path, method), '__config__')
        # save configure
        data_file = open(config_path, 'w')
        data_file.write(json.dumps({'method': method, 'post_type': post_type, 'json_p': json_p, 'params': params}))
        data_file.close()
        return {'result': 'success'}

    def get_sorted_code(self, user, view, method):
        codes = []
        is_param_type = False
        for error_code in method.element.code_index:
            error_message = method.element.code_dict[error_code]

            if error_code.startswith('param_type_error_') and not is_param_type:
                codes.append(('----', None, None))
                is_param_type = True

            if is_param_type and not error_code.startswith('param_type_error_'):
                codes.append(('----', None, None))
                is_param_type = False

            codes.append((error_code, to_html(error_message),
                          self.get_test_case(user, view, method, error_code)))

        return codes

    def get_test_case(self, user, view, method, code):
        use_cases = ''
        case_path = os.path.join(self.curr_case_dir(user, view.uri, method.__name__.upper()), code)
        if os.path.exists(case_path):
            data_file = open(case_path, 'r')
            for line in data_file.readlines():
                line = line.replace(os.linesep, '')
                if use_cases:
                    use_cases += ', ' + line
                else:
                    use_cases += line
            data_file.close()
        return '[%s]' % use_cases


def get_curr_api_params(param_list, config):
    params = []
    params_config = config['params'] if config else {}
    for param in param_list:
        name = param['name']
        requisite = b'\xe2\x97\x8f'.decode() if param['requisite'] else ''
        if param['type'].has_sub_type:
            type_name = '%s[%s]' % (param['type'].__name__, param['type'].type.__name__)
            type_display = '''<span message="%s">%s</span>[<span message="%s">%s</span>]''' % (
                param['type'].description, param['type'].__name__,
                param['type'].type.description, param['type'].type.__name__)
        else:
            type_name = param['type'].__name__
            type_display = '''<span class="show-message" message="%s">%s</span>''' % \
                           (to_html(param['type'].description), param['type'].__name__)
        pure_auto = 'checked="checked"' if name in params_config and params_config[name]['pure_auto'] else ''
        param_url = params_config[name]['url'] if name in params_config else ''
        params.append((name, requisite, to_html(param['description']), type_name, type_display, pure_auto, param_url))
    return params
