# -*- coding: utf-8 -*-

import json
import logging
from flask import Response

log = logging.getLogger(__name__)

JSON = 'application/json; charset=utf-8'
JSON_P = 'application/javascript; charset=utf-8'


class ResponseRaise(Exception):

    def __init__(self, view, code, data=None, status=None):
        self.view = view
        self.code = code
        self.data = data
        self.status = status

    def response(self):
        raise NotImplementedError()


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
        return self.code, ret, Response(json.dumps(ret), content_type=JSON, status=self.status)


class JsonPRaise(ResponseRaise):

    def response(self):
        ret = {'code': self.code, 'message': self.view.codes[self.code], 'data': self.data}
        # log output
        # self.log(code, ret, exception)
        # return result
        # json_p = self.params.get(self.json_p) if self.json_p else None
        # if json_p:
        #
        # else:
        #     return Response(json.dumps(ret), content_type=JSON, status=status)
        content = self.view.json_p_callback_name + '(' + json.dumps(ret) + ')'
        return self.code, ret, Response(content, content_type=JSON_P, status=self.status)
