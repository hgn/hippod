import json
import hashlib

def __sum_list(o):
        buf = ''
        if type(o) is not list:
                raise ValueError('must be a list')
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
        if type(o) is not dict:
                raise ValueError('must be a dict')
        for key in sorted(o):
                if type(o[key]) is dict:
                        buf += "{}{}".format(key, __sum_dict(o[key]))
                elif type(o[key]) is list:
                        buf += "{}{}".format(key, __sum_list(o[key]))
                else:
                        buf += "{}{}".format(key, o[key])
        return buf

def check_sum_object_issue(o):
        ''' return [[true|false], sha1-sum] '''
        buf = ''
        if type(o) is not dict:
                return [False, None]
        # check if required attributes are all available
        if "title" not in o: return [False, None]
        if "description" not in o: return [False, None]
        if "categories" not in o: return [False, None]
        if "version" not in o: return [False, None]

        try:
                buf = __sum_dict(o)
        except ValueError:
                return [False, None]
        buf_digest = hashlib.sha1(buf).hexdigest()
        return [True, buf_digest]
