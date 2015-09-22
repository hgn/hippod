#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import inspect
import time
import zlib
import sys

import object_hasher
import api_comm
from api_err_obj import *

from hippod import app

from flask import jsonify
from flask import request

def object_index_read():
    db_path = app.config['DB_OBJECT_PATH']
    object_index_db_path = os.path.join(db_path, "object-index.db")
    assert os.path.isfile(object_index_db_path)
    with open(object_index_db_path) as data_file:
        return json.load(data_file)


def check_request_data(xobj):
    ordering = "by-submitting-date-reverse"
    limit = 0 # "unlimited"
    maturity_level = "all"
    if 'ordering' in xobj:
        ordering = xobj['ordering']
    if 'limit' in xobj:
        limit = int(xobj['limit'])
        if limit < 0 or limit > 1000000:
            msg = "limit must be between 0 and 1000000"
            raise ApiError(msg, 400)
    if 'maturity-level' in xobj:
        maturity_level = xobj['maturity-level']
        if maturity_level not in ("all", "testing", "stable", "outdated"):
            msg = "maturity_level must be all, testing, stable or outdated "
            raise ApiError(msg, 400)

    # fine, arguments are fime
    request_data = dict()
    request_data['ordering'] = ordering
    request_data['limit'] = limit
    request_data['maturity-level'] = maturity_level
    return request_data


def null_func(data):
    pass


def object_data_by_id(sha_sum):
    d = dict()
    d['object-item-id'] = sha_sum
    return d


def object_get_by_sub_data_rev(request_data, reverse=True):
    object_index_data = object_index_read()
    limit = request_data['limit']
    limit_enabled = True if limit > 0 else False
    ret_data = list()
    list_sort_func = (null_func, reversed)[bool(reverse)]
    for i in list_sort_func(object_index_data):
        data = object_data_by_id(i['object-item-id'])
        ret_data.append(data)
        if limit_enabled:
            limit -= 1
            if limit <= 0:
                break
    return ret_data


def object_get_int(xobj):
    request_data = check_request_data(xobj)
    if request_data['ordering'] == "by-submitting-date-reverse":
        return object_get_by_sub_data_rev(request_data, reverse=True)
    elif request_data['ordering'] == "by-submitting-date":
        return object_get_by_sub_data_rev(request_data, reverse=False)
    else:
        msg = "ordering not supported"
        raise ApiError(msg, 400)
    


@app.route('/api/v1/object', methods=['GET'])
def object_get():
    try:
        start = time.clock()
        xobj = request.get_json(force=False)
        data = object_get_int(xobj)
        end = time.clock()
    except ApiError as e:
        return e.transform()
    except Exception as e:
        return ApiError(str(e), 500).transform()

    o = api_comm.Dict3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()



