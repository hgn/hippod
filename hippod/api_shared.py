#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import inspect
import time
import zlib
import sys

from hippod import app

from flask import jsonify
from flask import request

def read_cont_obj_by_id(sha_sum):
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha_sum[0:2],
                        sha_sum,
                        'container.db')
    if not os.path.isfile(path):
        return [False]
    with open(path) as data_file:
        data = json.load(data_file)
    return [True, data]


def get_achievement_data_by_sha_id(sha, id_no):
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'achievements',
                        '{}.db'.format(id_no))
    with open(path) as data_file:
        data = json.load(data_file)
    return data
