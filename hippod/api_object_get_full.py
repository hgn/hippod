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



def get_all_achievement_data(app, sha_major, sha_minor, subcont_obj):
    if len(subcont_obj['achievements']) <= 0:
        return None

    ret_list = list()
    for achievement in reversed(subcont_obj['achievements']):
        data = hippod.api_shared.get_achievement_data_by_sha_id(app, sha_major, sha_minor, achievement["id"])
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


def get_last_attachment_data(app, sha_major, cont_obj):
    if len(cont_obj['attachments']) <= 0:
        return None

    last_element_id = cont_obj['attachments'][-1]["id"]
    last_date_added = cont_obj['attachments'][-1]["date-added"]
    last_submitter  = cont_obj['attachments'][-1]["submitter"]

    data = hippod.api_shared.get_attachment_data_by_sha_id(app, sha_major, last_element_id)

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


def container_obj_to_ret_obj(app, sha_major, cont_obj):
    ret_obj = dict()
    # add object item ID
    ret_obj['object-item-id'] = sha_major

    # add some object items
    ret_obj['object-item'] = dict()
    ret_obj['object-item']['title'] = cont_obj['title']
    ret_obj['subcontainer'] = list()

    for sub_cont in cont_obj['subcontainer-list']:
        sub_dict = dict()
        sub_dict['object-item'] = dict()
        sub_dict['sha-minor'] = sub_cont['sha-minor']
        sub_dict['object-item']['data'] = list()
        ok, full_sub_cont = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sub_cont['sha-minor'])
        if not ok:
            msg = "subcontainer {} not available, although entry in subcontainer-list"
            msg = msg.format(sub_cont['sha-minor'])
            raise ApiError(msg)
        data = get_all_achievement_data(app, sha_major, sub_cont['sha-minor'], full_sub_cont)
        if data:
            sub_dict['object-achievements'] = data
        if 'data' in full_sub_cont['object-item']:
            sub_dict['object-item']['data'].append(full_sub_cont['object-item']['data'])
        # error handling not required?
        ret_obj['subcontainer'].append(sub_dict)

    # add last attachment
    data = get_last_attachment_data(app, sha_major, cont_obj)
    if data:
        ret_obj['object-attachment'] = data
    return ret_obj


def object_get_int(app, sha_major):
    ok, data = hippod.api_shared.read_cont_obj_by_id(app, sha_major)
    if not ok:
        msg = "cannot read object by id: {}".format(sha_major)
        raise ApiError(msg)
    return container_obj_to_ret_obj(app, sha_major, data)


def handle(request):
    if request.method != "GET" and request.method != "POST":
        msg = "Internal Error... request method: {} is not allowed".format(request.method)
        raise hippod.error_object.ApiError(msg)
    app = request.app
    sha_major = request.match_info['sha_major']

    try:
        start = time.clock()
        data = object_get_int(app, sha_major)
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