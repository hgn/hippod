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
import asyncio

import hippod.hasher
import hippod.ex3000
import hippod.api_shared
import hippod.statistic
import hippod.mime_data_db

from hippod.error_object import *



def check_attachment(attachment):
    if type(attachment) is not dict:
        return False
    return True

def add_initial_severity_level(object_item):
    # allowed values: none, trivial, minor, major, critical
    # blocker
    data = dict()
    data['level'] = 'none'
    data['since'] = datetime.datetime.now().isoformat('T')

    object_item['severity'] = list()
    object_item['severity'].append(data)


def add_initial_maturity_level(object_item):
    data = dict()
    data['level'] = 'testing'
    data['cause'] = 'initial'
    data['since'] = datetime.datetime.now().isoformat('T')

    object_item['maturity-level'] = list()
    object_item['maturity-level'].append(data)


def create_container_data_merge_issue_new(app, sha_sum, object_item, submitter):
    date = datetime.datetime.now().isoformat('T') # ISO 8601 format
    d = dict()
    d['submitter'] = submitter
    d['object-item-id'] = sha_sum
    d['date-added'] = date
    d['attachments'] = []
    d['attachment-last-modified'] = date
    d['achievements'] = []

    add_initial_maturity_level(d)
    add_initial_severity_level(d)

    # the object is a little bit special. We iterate over the
    # data section as always and compress or not compress
    # data and save it in a different path
    hippod.mime_data_db.save_object_item_data_list(app, object_item)
    d['object-item'] = object_item

    #if 'attachment' in xobj and len(xobj['attachment']) > 0:
    #    if not check_attachment(xobj['attachment']):
    #        return [False, None]
    #    d['attachment'] = xobj['attachment']

    return json.dumps(d, sort_keys=True,indent=4, separators=(',', ': '))


def save_new_object_container(app, sha_sum, object_item, submitter):
    obj_root_path = app['DB_OBJECT_PATH']
    obj_root_pre_path = os.path.join(obj_root_path, sha_sum[0:2])
    if not os.path.isdir(obj_root_pre_path):
        os.makedirs(obj_root_pre_path)
    obj_root_full_path = os.path.join(obj_root_pre_path, sha_sum)
    if not os.path.isdir(obj_root_full_path):
        os.makedirs(obj_root_full_path)
    achie_path = os.path.join(obj_root_full_path, 'achievements')
    if not os.path.isdir(achie_path):
        os.makedirs(achie_path)
    attachie_path = os.path.join(obj_root_full_path, 'attachments')
    if not os.path.isdir(attachie_path):
        os.makedirs(attachie_path)

    file_path = os.path.join(obj_root_full_path, 'container.db')
    if os.path.isfile(file_path):
        msg = "internal error: {}".format(inspect.currentframe())
        raise ApiError(msg)
    else:
        cd = create_container_data_merge_issue_new(app, sha_sum, object_item, submitter)
        fd = open(file_path, 'w')
        fd.write(cd)
        fd.close()


def is_obj_already_in_db(app, sha_sum):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_sum[0:2],
                        sha_sum,
                        'container.db')
    if os.path.isfile(path):
        return True
    else:
        return False




def write_cont_obj_by_id(app, sha, py_object):
    data = json.dumps(py_object, sort_keys=True,indent=4,
                      separators=(',', ': '))
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'container.db')
    fd = open(path, 'w')
    fd.write(data)
    fd.close()


def write_achievement_file(app, sha, id_no, achievement):
    # swap out data if mime types say so and modify
    # achievement inplace to reflect changes
    hippod.mime_data_db.save_object_item_data_list(app, achievement)

    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'achievements',
                        '{}.db'.format(id_no))
    data = json.dumps(achievement, sort_keys=True,indent=4,
                      separators=(',', ': '))
    fd = open(path, 'w')
    fd.write(data)
    fd.close()


def write_attachment_file(app, sha, id_no, attachment):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'attachments',
                        '{}.db'.format(id_no))
    data = json.dumps(attachment, sort_keys=True,indent=4,
                      separators=(',', ': '))
    fd = open(path, 'w')
    fd.write(data)
    fd.close()


def validate_date(formated_data):
    # only supported format: 2015-09-15T22:24:29.158759"
    try:
        datetime.datetime.strptime(formated_data, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError as e:
        return ApiError("date is not ISO8601 formatted").transform()


def validate_achievement(achievement):
    if not "result" in achievement:
        msg = "achievements has no result!"
        raise ApiError(msg)

    if achievement['result'] not in ['passed', 'failed', 'nonapplicable']:
        msg = "achievements result MUST be passed, failed, nonapplicable"
        raise ApiError(msg)

    if not "test-date" in achievement:
        msg = "achievements has no test-date!"
        raise ApiError(msg)

    validate_date(achievement['test-date'])


def update_attachment_achievement(app, sha_sum, xobj):
    # ok, the object is in database, we now update the data
    # attachments are updated (overwrite), achievements are
    # added
    rewrite_required = False
    date = datetime.datetime.now().isoformat('T')
    (ret, data) = hippod.api_shared.read_cont_obj_by_id(app, sha_sum)
    if not ret:
        msg = "cannot read object although it is an update!?"
        raise ApiError(msg)

    if 'attachment' in xobj:
        if type(xobj['attachment']) is not dict:
                msg = "attachment data MUST be a dict - but isn't"
                raise ApiError(msg)

        current_attachments = data['attachments']
        current_attachments_no = len(current_attachments)
        if current_attachments_no <= 0:
            new_attachment_meta = dict()
            new_attachment_meta['id'] = current_attachments_no
            new_attachment_meta['date-added'] = date
            new_attachment_meta['submitter'] = xobj['submitter']

            current_attachments.append(new_attachment_meta)
            write_attachment_file(app, sha_sum, current_attachments_no, xobj['attachment'])
            data['attachments'] = current_attachments
            rewrite_required = True
        else:
            last_attachment = hippod.api_shared.get_attachment_data_by_sha_id(app, sha_sum, current_attachments_no - 1)
            sha_sum_last = hippod.hasher.check_sum_attachment(last_attachment)
            sha_sum_new  = hippod.hasher.check_sum_attachment(xobj['attachment'])
            if sha_sum_last != sha_sum_new:
                new_attachment_meta = dict()
                new_attachment_meta['id'] = current_attachments_no
                new_attachment_meta['date-added'] = date
                new_attachment_meta['submitter'] = xobj['submitter']

                current_attachments.append(new_attachment_meta)
                write_attachment_file(app, sha_sum, current_attachments_no, xobj['attachment'])
                data['attachments'] = current_attachments
                rewrite_required = True

    if 'achievements' in xobj:
        if type(xobj['achievements']) is not list:
                msg = "achievements data MUST be a list - but isn't"
                raise ApiError(msg)
        current_achievements = data["achievements"]
        current_achievements_no = len(current_achievements)
        # add new achievements in same order
        for a in xobj['achievements']:
            validate_achievement(a)
            new_data = dict()
            new_data['id'] = current_achievements_no
            new_data['date-added'] =  date
            new_data['variety-id'] = hippod.hasher.calc_variety_id(a)
            current_achievements.append(new_data)

            # additionally, we add the submitter to the achievement
            a['submitter'] = xobj['submitter']

            # now we save the achievement in a seperate file
            write_achievement_file(app, sha_sum, current_achievements_no, a)
            current_achievements_no += 1

        data["achievements"] = current_achievements
        rewrite_required = True

    if rewrite_required:
        write_cont_obj_by_id(app, sha_sum, data)


def object_index_init(app):
    db_path = app['DB_OBJECT_PATH']
    object_index_db_path = os.path.join(db_path, "object-index.db")
    if not os.path.isfile(object_index_db_path):
        return list()
    with open(object_index_db_path) as data_file:
        return json.load(data_file)


def object_index_update(app, d):
    db_path = app['DB_OBJECT_PATH']
    object_index_db_path = os.path.join(db_path, "object-index.db")
    data = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))
    fd = open(object_index_db_path, 'w')
    fd.write(data)
    fd.close()


def object_index_initial_add(app, sha_sum, xobj):
    # read existing data set
    object_index = object_index_init(app)
    # create new data set
    d = dict()
    d['object-item-id'] = sha_sum
    # append new data set
    object_index.append(d)
    # update the object index
    object_index_update(app, object_index)


def try_adding_xobject(app, xobj):
    if not 'submitter' in xobj:
        msg = "No submitter in xobject given!"
        raise ApiError(msg)

    if not 'object-item' in xobj and not 'object-item-id' in xobj:
        msg = "object data corrupt - no object-item" \
              " or object-item-id given"
        raise ApiError(msg)

    sha_sum=""
    if 'object-item' in xobj:
        # calculate the ID now
        sha_sum = hippod.hasher.check_sum_object_issue(xobj['object-item'])
        if 'object-item-id' in xobj:
            # this is an additional check - both should be
            # identical
            if sha_sum != xobj['object-item-id']:
                msg = "object data corrupt - object item " \
                      "sha_sum missmatch to object-item-id"
                raise ApiError(msg)
    elif 'object-item-id' in xobj:
        sha_sum = xobj['object-item-id']
    else:
        msg = "Need at least a Full Object Item or Object Item ID"
        raise ApiError(msg)

    # FIXME: in the remaining paragraph there is a race condition
    # leads to data corruption. Problem is that data is writen
    # to file partly and later the achievement can be miss-formated.
    # object container file write should be delayed until everything
    # is sane.
    ret = is_obj_already_in_db(app, sha_sum)
    if not ret:
        # new entry, save to file
        save_new_object_container(app, sha_sum, xobj['object-item'], xobj['submitter'])
        object_index_initial_add(app, sha_sum, xobj)

    update_attachment_achievement(app, sha_sum, xobj)

    ret_data = dict()
    ret_data['id'] = sha_sum
    return ret_data

def check_request_size_limit(app, request):
    cl = request.content_length
    if cl is not None and cl > app['MAX_REQUEST_SIZE']:
        msg = "Request data size {} > limit ({})".format(
                cl, app['MAX_REQUEST_SIZE'])
        raise ApiError(msg)


async def handle(request):
    if request.method != "POST":
        msg = "Internal Error... request method: {} is not allowed".format(request.method)
        raise hippod.error_object.ApiError(msg)
    app = request.app

    try:
        start = time.clock()
        check_request_size_limit(app, request)
        xobj = await request.json()
        data = try_adding_xobject(app, xobj)
        hippod.statistic.update_global_db_stats(app)
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