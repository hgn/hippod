import sys
import json
import hashlib
import base64
import datetime
import os

import aiohttp



from hippod.error_object import *


def load_data(path):
    with open(path) as data_file:
        return json.load(data_file)


def filter_data(userdb, username):
    data = userdb.query_user(username)
    entry = dict()
    ret = list()
    # probably sensitive data, we opt-in here explicetly
    publ_data = ['department', 'fullname', 'email', 'telephone']
    for i, item in enumerate(publ_data):
        print(data)
        if item in data:
            # patch entries
            if item == "full_name":
                entry["fullname"] = data[item]
            else:
                entry[item] = data[item]
    entry["username"] = username
    ret.append(entry)
    if len(ret) == 0:
        msg = "user DB do not contain valid user for given filter {}".format(filter_str)
        raise ApiError(msg, http_code=404)
    return ret



def get(app, username):
    userdb = app['USER_DB']
    return filter_data(userdb, username)
