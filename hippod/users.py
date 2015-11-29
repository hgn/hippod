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


def x_ray_safety_check(data):
    """ in user.db we store sensitive data, make sure
        these data is never ever leave the system """
    ret = list()
    for item in data['users']:
        entry = dict()
        for i in ('abbr', 'color', 'email', 'full'):
            entry[i] = item[i]
        ret.append(entry)
    return ret


def get(limit=None):
    path = app.config['DB_USER_FILEPATH']
    return x_ray_safety_check(load_data(path))

