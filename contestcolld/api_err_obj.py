import collections

from flask import jsonify


class Dict3000(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.store['status'] = 'ok'
        self.store['message'] = 'shizzle dizzle'
        self._http_code = 666
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def transform(self):
        return jsonify(self.store), self._http_code

    def http_code(self, code=None):
        if code != None:
            self._http_code = code
        return self._http_code
        


class ApiError(Exception):
    def __init__(self, message, http_code):
        super(Exception, self).__init__(message)
        self.dict3000 = Dict3000()
        self.dict3000.http_code(http_code)
        self.dict3000['status'] = 'fail'
        self.dict3000['message'] = message

        self.http_code = http_code

    def msg(self):
        return message

    def transform(self):
        return self.dict3000.transform()
