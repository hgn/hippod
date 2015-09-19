import json
import hashlib
import base64

from api_err_obj import *

def __sum_list(o):
        buf = ''
        if type(o) is not list:
                msg = "object data currupt - must be list: {}".format(str(o))
                raise ApiError(msg, 404)
        for i in sorted(o):
                if type(i) is dict:
                        buf += __sum_dict(i)
                elif type(i) is list:
                        buf += __sum_list(i)
                else:
                        buf += "{}".format(i)
        return buf

def __sum_dict(o):
        buf = ''
        return buf
        if type(o) is not dict:
                msg = "object data currupt - must be dict: {}".format(str(o))
                raise ApiError(msg, 404)
        for key in sorted(o):
                if type(o[key]) is dict:
                        buf += "{}{}".format(key, __sum_dict(o[key]))
                elif type(o[key]) is list:
                        buf += "{}{}".format(key, __sum_list(o[key]))
                else:
                        buf += "{}{}".format(key, o[key])
        return buf


def check_sum_object_issue(o):
        ''' reurns SHA1 sum'''
        buf = ''
        if type(o) is not dict:
            msg = "object data currupt - must be dict: {}".format(str(o))
            raise ApiError(msg, 404)
        # check if required attributes are all available
        if "title" not in o:
            msg = "object data currupt - title missing: {}".format(str(o))
            raise ApiError(msg, 404)
        if "categories" not in o:
            msg = "object data currupt - categories missing: {}".format(str(o))
            raise ApiError(msg, 404)
        if "version" not in o:
            msg = "object data currupt - version missing: {}".format(str(o))
            raise ApiError(msg, 404)

        buf = __sum_dict(o)
        return hashlib.sha1(buf).hexdigest()


def hash_data(data):
    return hashlib.sha1(data).hexdigest()


def decode_base64_data(data):
    return base64.b64decode(data)


def encode_base64_data(data):
    return base64.b64encode(data)


def check_xobject(o):
        if type(o) is not dict:
            return False
        if "object" not in o and 'object-id' not in o:
            return False
        if 'object' in o and 'object-id' in o:
            return False
        return True

