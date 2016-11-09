#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import inspect
import time
import zlib
import sys

import aiohttp

import hippod.hasher
import hippod.ex3000
import hippod.api_shared

from hippod.error_object import *



def get_all_achievement_data(app, sha_sum, cont_obj):
    if len(cont_obj['achievements']) <= 0:
        return None

    ret_list = list()
    for achievement in reversed(cont_obj['achievements']):
        data = hippod.api_shared.get_achievement_data_by_sha_id(app, sha_sum, achievement["id"])

        r = dict()
        r['id'] = achievement["id"]
        r['variety-id'] = achievement["variety-id"]
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


def get_last_attachment_data(app, sha_sum, cont_obj):
    if len(cont_obj['attachments']) <= 0:
        return None

    last_element_id = cont_obj['attachments'][-1]["id"]
    last_date_added = cont_obj['attachments'][-1]["date-added"]
    last_submitter  = cont_obj['attachments'][-1]["submitter"]

    data = hippod.api_shared.get_attachment_data_by_sha_id(app, sha_sum, last_element_id)

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


def container_obj_to_ret_obj(app, sha_sum, cont_obj):
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
    data = get_last_attachment_data(app, sha_sum, cont_obj)
    if data:
        ret_obj['object-attachment'] = data

    # add all achievements with all data
    data = get_all_achievement_data(app, sha_sum, cont_obj)
    if data:
        ret_obj['object-achievements'] = data

    return ret_obj

def object_get_int(app, sha_sum):
    (ret, data) = hippod.api_shared.read_cont_obj_by_id(app, sha_sum)
    if not ret:
        msg = "cannot read object by id: {}".format(sha_sum)
        raise ApiError(msg)
    return container_obj_to_ret_obj(app, sha_sum, data)

def handle(request):
    print("Object Loading:")
    if request.method != "GET" and request.method != "POST":
        msg = "Internal Error... request method: {} is not allowed".format(request.method)
        raise hippod.error_object.ApiError(msg)
    app = request.app
    sha_sum = request.match_info['sha_sum']

    try:
        start = time.clock()
        data = object_get_int(app, sha_sum)
        end = time.clock()
    except ApiError as e:
        return e.transform()
    except Exception as e:
        return ApiError(str(e)).transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()



