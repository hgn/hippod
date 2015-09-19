#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import time

import object_hasher
from api_err_obj import *

from contestcolld import app

from flask import jsonify
from flask import request


def folder_size(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += folder_size(itempath)
    return total_size


def calc_ressource():
    db_path = app.config['DB_OBJECT_PATH']
    if not os.path.isdir(db_path):
        raise ApiError("internal error - db path do not exist", 404)
    ret_data = dict()
    ret_data['overall'] = folder_size(db_path)
    return ret_data


@app.route('/api/v1.0/resources', methods=['GET'])
def get_resources():
    try:
        start = time.clock()
        data = calc_ressource()
        end = time.clock()
    except apierror as e:
        return e.transform()
    except exception as e:
        return apierror(str(e), 202).transform()

    o = dict3000()
    o['data'] = data
    o.http_code(202)
    return o.transform()

