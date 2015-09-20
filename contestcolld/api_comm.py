import collections

from flask import jsonify

# HTTP REST (Error) Codes
#
# 200 - everything is ok
# 400 - Missing parameter, Invalid format, Invalid param
# 404 - object not found (is object-id correct?)
# 500 - internal error


class Dict3000(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.store['status'] = 'ok'
        self.store['message'] = 'shizzle dizzle'
        self._http_code = 200
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
            if code not in [ 200, 400, 404, 500 ]:
                raise ApiError("internal error, http code not allowed: {}".format(code))
            self._http_code = code
        return self._http_code
        


