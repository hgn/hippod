import collections

import hippod.api_err_obj

from flask import jsonify

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
            if code not in [ 200, 202, 400, 404, 500 ]:
                raise hippod.api_err_obj.ApiError("internal error, http code not allowed: {}".format(code), 500)
            self._http_code = code
        return self._http_code
        


