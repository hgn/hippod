#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import inspect
import time
import zlib
import sys

import hippod.hasher
import hippod.ex3000
import hippod.api_shared

from hippod.error_object import *

from hippod import app

from flask import jsonify
from flask import request

def object_index_read():
    db_path = app.config['DB_OBJECT_PATH']
    object_index_db_path = os.path.join(db_path, "object-index.db")
    if not os.path.isfile(object_index_db_path):
        return None
    with open(object_index_db_path) as data_file:
        return json.load(data_file)


def check_request_data(xobj):
    ordering = "by-submitting-date-reverse"
    limit = 0 # "unlimited"
    maturity_level = "all"
    filter_result = "all"

    if 'ordering' in xobj:
        ordering = xobj['ordering']
    if 'limit' in xobj:
        limit = int(xobj['limit'])
        if limit < 0 or limit > 1000000:
            msg = "limit must be between 0 and 1000000"
            raise ApiError(msg, 400)
    if 'filter-by-maturity-level' in xobj:
        maturity_level = xobj['filter-by-maturity-level']
        if maturity_level not in ("all", "testing", "stable", "outdated"):
            msg = "maturity_level must be all, testing, stable or outdated "
            raise ApiError(msg, 400)
    if 'filter-by-result' in xobj:
        filter_result = xobj['filter-by-result']
        if filter_result not in ("all", "passed", "failed", "inapplicable"):
            msg = "maturity_level must be all, passed, failed or inapplicable "
            raise ApiError(msg, 400)

    # fine, arguments are fime
    request_data = dict()
    request_data['ordering'] = ordering
    request_data['limit'] = limit
    request_data['filter-by-maturity-level'] = maturity_level
    request_data['filter-by-result'] = filter_result
    return request_data


def null_func(data):
    pass


def get_last_achievement_data(sha_sum, cont_obj):
    if len(cont_obj['achievements']) <= 0:
        return None

    last_date_added = cont_obj['achievements'][-1]["date-added"]
    last_element_id = cont_obj['achievements'][-1]["id"]

    data = hippod.api_shared.get_achievement_data_by_sha_id(sha_sum, last_element_id)
    test_result = data["result"]
    test_date   = data["test-date"]
    submitter   = data["submitter"]

    r = dict()
    r['test-date']= test_date
    r['test-result']= test_result
    r['id']= last_element_id
    r['date-added']= last_date_added
    r['submitter']= submitter

    return r


def get_last_attachment_data(sha_sum, cont_obj):
    if len(cont_obj['attachments']) <= 0:
        return None

    last_element_id = cont_obj['attachments'][-1]["id"]
    last_date_added = cont_obj['attachments'][-1]["date-added"]
    last_submitter  = cont_obj['attachments'][-1]["submitter"]

    data = hippod.api_shared.get_attachment_data_by_sha_id(sha_sum, last_element_id)

    r = dict()
    for key, value in data.items():
        r[key] = data[key]

    for i in ('references', 'responsible', 'tags'):
        if i not in data:
            continue
        r[i] = data[i]

    r['id'] = last_element_id
    r['date-added'] = last_date_added
    r['last-submitter'] = last_submitter

    return r


def container_obj_to_ret_obj(request_data, sha_sum, cont_obj):
    ret_obj = dict()

    # add object item ID
    ret_obj['object-item-id'] = sha_sum

    # add some object items
    ret_obj['object-item'] = dict()
    ret_obj['object-item']['title'] = cont_obj['object-item']['title'] 
    ret_obj['object-item']['version'] = cont_obj['object-item']['version'] 

    ret_obj['maturity-level'] = cont_obj['maturity-level'][-1]

    # add last attachment
    data = get_last_attachment_data(sha_sum, cont_obj)
    if data:
        ret_obj['object-attachment'] = data

    # add last achievement with basic information
    data = get_last_achievement_data(sha_sum, cont_obj)
    if data:
        ret_obj['object-achievements'] = data
        if request_data['filter-by-result'] != "all":
            if request_data['filter-by-result'] != data['test-result']:
                return false, none

    # filter checks
    if request_data['filter-by-maturity-level'] != "all":
        if request_data['filter-by-maturity-level'] != \
                ret_obj['maturity-level']['level']:
            return False, None

    return True, ret_obj


def object_data_by_id(request_data, sha_sum):
    (ret, data) = hippod.api_shared.read_cont_obj_by_id(sha_sum)
    if not ret:
        msg = "cannot read object by id: {}".format(sha_sum)
        raise ApiError(msg, 500)
    return container_obj_to_ret_obj(request_data, sha_sum, data)


def object_get_by_sub_data_rev(request_data, reverse=True):
    object_index_data = object_index_read()
    if not object_index_data:
        return None
    limit = request_data['limit']
    limit_enabled = True if limit > 0 else False
    ret_data = list()
    list_sort_func = (null_func, reversed)[bool(reverse)]
    for i in list_sort_func(object_index_data):
        success, data = object_data_by_id(request_data, i['object-item-id'])
        if not success:
            # probably a filter (status, maturity_level, ..)
            continue
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
    


@app.route('/api/v1/objects', methods=['GET', 'POST'])
def object_get():
    try:
        start = time.clock()
        xobj = request.get_json(force=False)
        data = object_get_int(xobj)
        end = time.clock()
    except ApiError as e:
        return e.transform()
    #except Exception as e:
    #    return ApiError(str(e), 500).transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()



