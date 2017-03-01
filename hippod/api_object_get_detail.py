#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import inspect
import time
import zlib
import sys
import logging

import aiohttp
import asyncio

import hippod.hasher
import hippod.ex3000
import hippod.api_shared
import hippod.api_object_get_full
import hippod.status_codes

from hippod.error_object import *

log = logging.getLogger()


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
            raise ApiError(msg)
    if 'filter-by-maturity-level' in xobj:
        maturity_level = xobj['filter-by-maturity-level']
        if maturity_level not in ("all", "testing", "stable", "outdated"):
            msg = "maturity_level must be all, testing, stable or outdated "
            raise ApiError(msg)
    if 'filter-by-result' in xobj:
        filter_result = xobj['filter-by-result']
        if filter_result not in hippod.status_codes.status_list_with_all:
            status_list = " ".join(hippod.status_codes.status_list_with_all)
            msg = "result status must be {}".format(status_list)
            raise ApiError(msg)

    # fine, arguments are fime
    request_data = dict()
    request_data['ordering'] = ordering
    request_data['limit'] = limit
    request_data['filter-by-maturity-level'] = maturity_level
    request_data['filter-by-result'] = filter_result
    return request_data


def null_func(data):
    pass


def get_last_achievement_data(app, sha_major, sha_minor, sub_cont_obj):
    if len(sub_cont_obj['achievements']) <= 0:
        return None

    last_date_added = sub_cont_obj['achievements'][-1]["date-added"]
    last_element_id = sub_cont_obj['achievements'][-1]["id"]

    data = hippod.api_shared.get_achievement_data_by_sha_id(app, sha_major, sha_minor, last_element_id)
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


def scan_subcontainer(subcontainer_content):
    # returning the date of the latest achievement
    return subcontainer_content['achievements'][-1]['date-added']


def get_latest_achievement(app, container_content):
    dates = list()
    subcontainers = container_content['subcontainer-list']
    sha_major = container_content['object-item-id']
    for subcontainer in subcontainers:
        sha_minor = subcontainer['sha-minor']
        ok, data = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sha_minor)
        if not ok:
            msg = "subcontainer {} not available, although entry in subcontainer-list"
            msg = msg.format(subcontainer['sha-minor'])
            log.error(msg)
            continue
        latest_achiev_date = scan_subcontainer(data)
        latest_achiev_date = datetime.datetime.strptime(latest_achiev_date, '%Y-%m-%dT%H:%M:%S.%f')
        dates.append(latest_achiev_date)
    if not dates:
        return None
    return max(dates)


def get_latest_obj_by_achievement(app):
    object_index_data = hippod.api_shared.object_index_read(app)
    if not object_index_data:
        return None
    full_list = list()
    for obj in object_index_data:
        sha_major = obj['object-item-id']
        ok, data = hippod.api_shared.read_cont_obj_by_id(app, sha_major)
        if not ok:
            msg = "cannot read object by id: {}".format(sha_major)
            raise ApiError(msg)
        latest_achiev_date = get_latest_achievement(app, data)
        if not latest_achiev_date:
            continue
        full_list.append((sha_major, latest_achiev_date))
    full_list_sorted = sorted(full_list, key=lambda x: x[1])
    sha_majors, dates = zip(*full_list_sorted)
    return list(sha_majors)


def container_obj_to_ret_obj(app, request_data, sha_major, cont_obj):
    ret_obj = dict()
    buff_dict = dict()

    # fetch latest subcontainer (subcontainer with latest achievement) and related meta
    for sub_cont in cont_obj['subcontainer-list']:
        ok, full_sub_cont = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sub_cont['sha-minor'])
        if not ok:
            msg = "subcontainer {} not available, although entry in subcontainer-list"
            msg = msg.format(sub_cont['sha-minor'])
            raise ApiError(msg)
        data = hippod.api_object_get_full.get_all_achievement_data(app, sha_major, sub_cont['sha-minor'], full_sub_cont)
        if data:
            buff_dict[sub_cont['sha-minor']] = data[0]['date-added']
    if data:
        latest_sha_minor = max(buff_dict, key=lambda key: buff_dict[key])
        latest_subcont = next(d for (index,d) in enumerate(cont_obj['subcontainer-list']) if d['sha-minor']==latest_sha_minor)
        latest_index = next(index for (index,d) in enumerate(cont_obj['subcontainer-list']) if d['sha-minor']==latest_sha_minor)

    # add object item ID
    ret_obj['object-item-id'] = sha_major

    # add some object items
    ret_obj['object-item'] = dict()
    ret_obj['object-item']['title'] = cont_obj['title']
    ret_obj['object-item']['categories'] = cont_obj['categories']

    # sub_cont_last = cont_obj['subcontainer-list'][-1]
    if not data:
        sub_cont_last = cont_obj['subcontainer-list'][0]
        latest_sha_minor = sub_cont_last['sha-minor']
    else:
        sub_cont_last = cont_obj['subcontainer-list'][latest_index]
    ret_obj['object-item']['date'] = sub_cont_last['date-added']
    ret_obj['object-item']['last-submitter'] = sub_cont_last['submitter']
    ret_obj['object-item']['sha-minor'] = sub_cont_last['sha-minor']

    if len(cont_obj['subcontainer-list']) > 1:
        ret_obj['conflict'] = True
    else: ret_obj['conflict'] = False

    # add last attachment
    data = get_last_attachment_data(app, sha_major, cont_obj)
    if data:
        ret_obj['object-attachment'] = data

    db_root_path = app['DB_OBJECT_PATH']
    subcntr_path = os.path.join(db_root_path, sha_major[0:2], sha_major,\
                                latest_sha_minor, 'subcontainer.db')
    with open(subcntr_path) as file:
        full_sub_cont_last = json.load(file)

    # add last achievement with basic information
    data = get_last_achievement_data(app, sha_major, latest_sha_minor, full_sub_cont_last)
    if data:
        ret_obj['object-achievements'] = data
        if request_data['filter-by-result'] != "all":
            if request_data['filter-by-result'] != data['test-result']:
                return False, None

    # filter checks
    if request_data['filter-by-maturity-level'] != "all":
        if request_data['filter-by-maturity-level'] != \
                ret_obj['maturity-level']['level']:
            return False, None

    return True, ret_obj


def object_data_by_id(app, request_data, sha_major):
    ret, data = hippod.api_shared.read_cont_obj_by_id(app, sha_major)
    if not ret:
        msg = "cannot read object by id: {}".format(sha_major)
        raise ApiError(msg)
    return container_obj_to_ret_obj(app, request_data, sha_major, data)


def object_get_by_sub_data_rev(app, request_data, reverse=True):
    object_index_data = get_latest_obj_by_achievement(app)
    if not object_index_data:
        return None
    limit = request_data['limit']
    limit_enabled = True if limit > 0 else False
    ret_data = list()
    list_sort_func = (null_func, reversed)[bool(reverse)]
    for sha_major in list_sort_func(object_index_data):
        success, data = object_data_by_id(app, request_data, sha_major)
        if not success:
            # probably a filter (status, maturity_level, ..)
            continue
        ret_data.append(data)
        if limit_enabled:
            limit -= 1
            if limit <= 0:
                break
    return ret_data


def object_get_int(app, xobj):
    request_data = check_request_data(xobj)
    if request_data['ordering'] == "by-submitting-date-reverse":
        return object_get_by_sub_data_rev(app, request_data, reverse=True)
    elif request_data['ordering'] == "by-submitting-date":
        return object_get_by_sub_data_rev(app, request_data, reverse=False)
    else:
        msg = "ordering not supported"
        raise ApiError(msg)


async def handle(request):
    if request.method != "GET" and request.method != "POST":
        msg = "Internal Error... request method: {} is not allowed".format(request.method)
        raise hippod.error_object.ApiError(msg)
    app = request.app

    try:
        start = time.clock()
        xobj = await request.json()
        data = object_get_int(app, xobj)
        end = time.clock()
    except ApiError as e:
        return e.transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()
