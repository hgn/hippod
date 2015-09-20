import collections

from flask import jsonify
import api_comm


class ApiError(Exception):
    def __init__(self, message, http_code):
        super(Exception, self).__init__(message)
        self.dict3000 = api_comm.Dict3000()
        self.dict3000.http_code(http_code)
        self.dict3000['status'] = 'fail'
        self.dict3000['message'] = message

        self.http_code = http_code
        msg = "message: {}, code: {}".format(message, http_code)
        app.logger.error("Exception raised: {}".format(msg))

    def msg(self):
        return message

    def transform(self):
        return self.dict3000.transform()
