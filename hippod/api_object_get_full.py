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


def get_all_achievement_data(sha_sum, cont_obj):
    if len(cont_obj['achievements']) <= 0:
        return None

    ret_list = list()
    for achievement in reversed(cont_obj['achievements']):
        data = hippod.api_shared.get_achievement_data_by_sha_id(sha_sum, achievement["id"])

        r = dict()
        r['id'] = achievement["id"]
        r['variety-id'] = achievement["id"]
        r['date-added'] = achievement["date-added"]
        # we make sure these data is always in the database
        # if not a python key exception is raised and the
        # DB can be fixed
        for req_attr in ("test-date", "result", "submitter"):
            r[req_attr] = data[req_attr]

        # data is optional, make sure NO exception is raised
        for opt_attr in ("data", "variety", "anchor"):
            if opt_attr in data:
                r[opt_attr] = data[opt_attr]

        ret_list.append(r)
    return ret_list


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


def container_obj_to_ret_obj(sha_sum, cont_obj):
    ret_obj = dict()

    # add object item ID
    ret_obj['object-item-id'] = sha_sum

    # add some object items
    ret_obj['object-item'] = dict()
    ret_obj['object-item']['title'] = cont_obj['object-item']['title'] 
    ret_obj['object-item']['version'] = cont_obj['object-item']['version']
    if 'data' in cont_obj['object-item']:
        ret_obj['object-item']['data'] = cont_obj['object-item']['data']

    ret_obj['maturity-level'] = cont_obj['maturity-level'][-1]

    # add last attachment
    data = get_last_attachment_data(sha_sum, cont_obj)
    if data:
        ret_obj['object-attachment'] = data

    # add all achievements with all data
    data = get_all_achievement_data(sha_sum, cont_obj)
    if data:
        ret_obj['object-achievements'] = data

    return ret_obj



def object_get_int(sha_sum):
    (ret, data) = hippod.api_shared.read_cont_obj_by_id(sha_sum)
    if not ret:
        msg = "cannot read object by id: {}".format(sha_sum)
        raise ApiError(msg)
    return container_obj_to_ret_obj(sha_sum, data)
    

@app.route('/api/v1/object/<sha_sum>', methods=['GET', 'POST'])
def object_get_id(sha_sum):
    try:
        start = time.clock()
        #xobj = request.get_json(force=False)
        data = object_get_int(sha_sum)
        end = time.clock()
    except ApiError as e:
        return e.transform()
    #except Exception as e:
    #    return ApiError(str(e)).transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()



