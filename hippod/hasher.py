import sys
import json
import hashlib
import base64
import collections

from hippod.api_err_obj import *

def __sum_list(o):
        buf = ''
        if type(o) is not list:
                msg = "object data currupt - must be list: {}".format(str(o))
                raise ApiError(msg, 404)
        
        # a list can be - surprise - a list of dicts, sorting dict lists
        # is not that easy. Sorting by memory address is jabberwocky and
        # will not lead to an consistent view. Therefore we leave list entries
        # unsorted. This reflects the submitter/test order. Leading to a new
        # ID if things are sorted, but normally this should be an exception.
        for i in o:
                if type(i) is dict:
                        buf += __sum_dict(i)
                elif type(i) is list:
                        buf += __sum_list(i)
                else:
                        buf += "{}".format(i)
        return buf

def __sum_dict(o):
        buf = ''
        if type(o) is not dict:
                msg = "object data currupt - must be dict: {}".format(str(o))
                raise ApiError(msg, 404)

        od = collections.OrderedDict(sorted(o.items()))
        for key in od:
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
        if "version" not in o:
            msg = "object data currupt - version missing: {}".format(str(o))
            raise ApiError(msg, 404)

        # Use a sorted dictionary
        buf = __sum_dict(o)
        return hashlib.sha1(buf.encode('utf-8')).hexdigest()


def check_sum_attachment(o):
        buf = ''
        if type(o) is not dict:
            msg = "attachment currupt - must be dict: {}".format(str(o))
            raise ApiError(msg, 404)

        buf = __sum_dict(o)
        return hashlib.sha1(buf.encode('utf-8')).hexdigest()


def hash_data(data):
    return hashlib.sha1(data.encode('utf-8')).hexdigest()


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


def __calc_variety_id(variety_dict):
    if type(variety_dict) is not dict:
        msg = "variety data currupt - must be dict: {}".format(str(o))
        raise ApiError(msg, 404)
    buf = ''
    for entry_array in sorted(variety_dict.items()):
        if type(entry_array[0]) is not str or type(entry_array[1]) is not str:
            msg = "variety data currupt - must be dict: {}".format(str(o))
            raise ApiError(msg, 404)
        buf += "{}{}".format(entry_array[0], entry_array[1])
    return hashlib.sha1(buf.encode('utf-8')).hexdigest()


def calc_variety_id(achievement):
    if 'variety' not in achievement:
        return 0
    return __calc_variety_id(achievement['variety'])

