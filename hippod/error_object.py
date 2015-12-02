import collections

from flask import jsonify

import hippod.ex3000

# HTTP REST (Error) Codes
#
# 200 - everything is ok
# 400 - Missing parameter, Invalid format, Invalid param
# 404 - object not found (is object-id correct?)
# 500 - internal error
#
# See
# http://www.restapitutorial.com/httpstatuscodes.html


class ApiError(Exception):
    def __init__(self, message, http_code=400):
        super(Exception, self).__init__(message)
        self.dict3000 = hippod.ex3000.Ex3000()
        self.dict3000.http_code(http_code)
        self.dict3000['status'] = 'fail'
        self.dict3000['message'] = message
        self.http_code = http_code

    def msg(self):
        return message

    def transform(self):
        return self.dict3000.transform()
