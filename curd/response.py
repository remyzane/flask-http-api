# -*- coding: utf-8 -*-

import json
import logging
from flask import Response

log = logging.getLogger(__name__)

JSON = 'application/json; charset=utf-8'
JSON_P = 'application/javascript; charset=utf-8'


class ResponseRaise(Exception):

    def __init__(self, view, code, data=None, status=None, exception=False):
        self.view = view
        self.code = code
        self.data = data
        self.status = status
        self.exception = exception

    def response(self):
        print('aabbccd112233')
        return 'aa'
        return self.data


class JsonRaise(ResponseRaise):

    def response(self):
        # rollback the current transaction
        # if self.auto_rollback and code != 'success':
        #     self.db.rollback()
        # data of return
        ret = {'code': self.code, 'message': self.view.codes[self.code], 'data': self.data}
        # log output
        # self.log(code, ret, exception)
        # return result
        # json_p = self.params.get(self.json_p) if self.json_p else None
        # if json_p:
        #     return Response(json_p + '(' + json.dumps(ret) + ')', content_type=JSON_P, status=status)
        # else:
        #     return Response(json.dumps(ret), content_type=JSON, status=status)
        return Response(json.dumps(ret), content_type=JSON, status=self.status)

    # log output
    def log(self, code, data, exception):
        if self.process_log:
            self.process_log = '''
Process Flow: -------------------------------------------
%s
---------------------------------------------------------''' % self.process_log
        debug_info = '''%s
Return Data: --------------------------------------------
%s
---------------------------------------------------------''' % (self.process_log, str(data))
        if code == 'success':
            # different log output for performance
            if log.parent.level == logging.DEBUG:
                log.info('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
            else:
                log.info('%s %s %s', request.path, self.codes[code], self.params_log)
        else:
            if exception:
                log.exception('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)
            else:
                log.error('%s %s %s %s', request.path, self.codes[code], self.params_log, debug_info)


class JsonPRaise(ResponseRaise):

    def response(self):
        return '5555'