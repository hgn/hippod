import sys
import json
import hashlib
import base64
import datetime
import os

from hippod import app


def load_data(path):
    with open(path) as data_file:
        return json.load(data_file)


def filter_data(data, user_filter):
    if type(data) != list:
        # empty list
        return ret

    ret = list()
    for item in data:
        skip_entry = False
        if user_filter:
            for key, value in user_filter.items():
                if key not in item:
                    skip_entry = True
                    break
                if key in item and item[key] != value:
                    skip_entry = True
                    break
        if skip_entry:
            continue

        entry = dict()
        # probably sensitive data, we opt-in here explicetly
        for i in ('username', 'color', 'email', 'fullname'):
            if i in item:
                entry[i] = item[i]
        ret.append(entry)
    return ret



def get(user_filter=None):
    path = app.config['CONF_USER_FILEPATH']
    data = load_data(path)
    return filter_data(data, user_filter)

