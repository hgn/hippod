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
import hippod.api_comm
import hippod.api_shared
import hippod.statistic
import hippod.mime_data_db

from hippod.api_err_obj import *

from hippod import app

from flask import jsonify
from flask import request


def check_attachment(attachment):
    if type(attachment) is not dict:
        return False
    return True


def add_initial_maturity_level(object_item):
    data = dict()
    data['level'] = 'testing'
    data['cause'] = 'initial'
    data['since'] = datetime.datetime.now().isoformat('T')

    object_item['maturity-level'] = list()
    object_item['maturity-level'].append(data)


def create_container_data_merge_issue_new(sha_sum, object_item, submitter):
    date = datetime.datetime.now().isoformat('T') # ISO 8601 format
    d = dict()
    d['submitter'] = submitter
    d['object-item-id'] = sha_sum
    d['date-added'] = date
    d['attachments'] = []
    d['attachment-last-modified'] = date
    d['achievements'] = []

    add_initial_maturity_level(d)

    # the object is a little bit special. We iterate over the
    # data section as always and compress or not compress
    # data and save it in a different path
    hippod.mime_data_db.save_object_item_data_list(object_item)
    d['object-item'] = object_item

    #if 'attachment' in xobj and len(xobj['attachment']) > 0:
    #    if not check_attachment(xobj['attachment']):
    #        return [False, None]
    #    d['attachment'] = xobj['attachment']

    return json.dumps(d, sort_keys=True,indent=4, separators=(',', ': '))


def save_new_object_container(sha_sum, object_item, submitter):
    obj_root_path = app.config['DB_OBJECT_PATH']
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
        raise ApiError(msg, 404)
    else:
        cd = create_container_data_merge_issue_new(sha_sum, object_item, submitter)
        fd = open(file_path, 'w')
        fd.write(cd)
        fd.close()


def is_obj_already_in_db(sha_sum):
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha_sum[0:2],
                        sha_sum,
                        'container.db')
    if os.path.isfile(path):
        return True
    else:
        return False




def write_cont_obj_by_id(sha, py_object):
    data = json.dumps(py_object, sort_keys=True,indent=4,
                      separators=(',', ': '))
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'container.db')
    fd = open(path, 'w')
    fd.write(data)
    fd.close()


def write_achievement_file(sha, id_no, achievement):
    # swap out data if mime types say so and modify
    # achievement inplace to reflect changes
    hippod.mime_data_db.save_object_item_data_list(achievement)

    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'achievements',
                        '{}.db'.format(id_no))
    data = json.dumps(achievement, sort_keys=True,indent=4,
                      separators=(',', ': '))
    fd = open(path, 'w')
    fd.write(data)
    fd.close()


def write_attachment_file(sha, id_no, attachment):
    path = os.path.join(app.config['DB_OBJECT_PATH'],
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
        return ApiError("date is not ISO8601 formatted", 400).transform()


def validate_achievement(achievement):
    if not "result" in achievement:
        msg = "achievements has no result!"
        raise ApiError(msg, 400)

    if achievement['result'] not in ['passed', 'failed', 'nonapplicable']:
        msg = "achievements result MUST be passed, failed, nonapplicable"
        raise ApiError(msg, 400)

    if not "test-date" in achievement:
        msg = "achievements has no test-date!"
        raise ApiError(msg, 400)

    validate_date(achievement['test-date'])


def update_attachment_achievement(sha_sum, xobj):
    # ok, the object is in database, we now update the data
    # attachments are updated (overwrite), achievements are
    # added
    rewrite_required = False
    date = datetime.datetime.now().isoformat('T')
    (ret, data) = hippod.api_shared.read_cont_obj_by_id(sha_sum)
    if not ret:
        msg = "cannot read object although it is an update!?"
        raise ApiError(msg, 500)

    if 'attachment' in xobj:
        if type(xobj['attachment']) is not dict:
                msg = "attachment data MUST be a dict - but isn't"
                raise ApiError(msg, 400)

        current_attachments = data['attachments']
        current_attachments_no = len(current_attachments)
        if current_attachments_no <= 0:
            new_attachment_meta = dict()
            new_attachment_meta['id'] = current_attachments_no
            new_attachment_meta['date-added'] = date
            new_attachment_meta['submitter'] = xobj['submitter']

            current_attachments.append(new_attachment_meta)
            write_attachment_file(sha_sum, current_attachments_no, xobj['attachment'])
            data['attachments'] = current_attachments
            rewrite_required = True
        else:
            last_attachment = hippod.api_shared.get_attachment_data_by_sha_id(sha_sum, current_attachments_no - 1)
            sha_sum_last = hippod.hasher.check_sum_attachment(last_attachment)
            sha_sum_new  = hippod.hasher.check_sum_attachment(xobj['attachment'])
            if sha_sum_last != sha_sum_new:
                new_attachment_meta = dict()
                new_attachment_meta['id'] = current_attachments_no
                new_attachment_meta['date-added'] = date
                new_attachment_meta['submitter'] = xobj['submitter']

                current_attachments.append(new_attachment_meta)
                write_attachment_file(sha_sum, current_attachments_no, xobj['attachment'])
                data['attachments'] = current_attachments
                rewrite_required = True

    if 'achievements' in xobj:
        if type(xobj['achievements']) is not list:
                msg = "achievements data MUST be a list - but isn't"
                raise ApiError(msg, 400)
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
            write_achievement_file(sha_sum, current_achievements_no, a)
            current_achievements_no += 1

        data["achievements"] = current_achievements
        rewrite_required = True

    if rewrite_required:
        write_cont_obj_by_id(sha_sum, data)


def object_index_init():
    db_path = app.config['DB_OBJECT_PATH']
    object_index_db_path = os.path.join(db_path, "object-index.db")
    if not os.path.isfile(object_index_db_path):
        return list()
    with open(object_index_db_path) as data_file:
        return json.load(data_file)


def object_index_update(d):
    db_path = app.config['DB_OBJECT_PATH']
    object_index_db_path = os.path.join(db_path, "object-index.db")
    data = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))
    fd = open(object_index_db_path, 'w')
    fd.write(data)
    fd.close()


def object_index_initial_add(sha_sum, xobj):
    # read existing data set
    object_index = object_index_init()
    # create new data set
    d = dict()
    d['object-item-id'] = sha_sum
    # append new data set
    object_index.append(d)
    # update the object index
    object_index_update(object_index)


def try_adding_xobject(xobj):
    if not 'submitter' in xobj:
        msg = "No submitter in xobject given!"
        raise ApiError(msg, 400)

    if not 'object-item' in xobj and not 'object-item-id' in xobj:
        msg = "object data corrupt - no object-item" \
              " or object-item-id given"
        raise ApiError(msg, 400)

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
                raise ApiError(msg, 400)
    elif 'object-item-id' in xobj:
        sha_sum = xobj['object-item-id']
    else:
        msg = "Need at least a Full Object Item or Object Item ID"
        raise ApiError(msg, 400)

    # FIXME: in the remaining paragraph there is a race condition
    # leads to data corruption. Problem is that data is writen
    # to file partly and later the achievement can be miss-formated.
    # object container file write should be delayed until everything
    # is sane.
    ret = is_obj_already_in_db(sha_sum)
    if not ret:
        # new entry, save to file
        save_new_object_container(sha_sum, xobj['object-item'], xobj['submitter'])
        object_index_initial_add(sha_sum, xobj)

    update_attachment_achievement(sha_sum, xobj)

    ret_data = dict()
    ret_data['id'] = sha_sum
    return ret_data

def check_request_size_limit(request):
    cl = request.content_length
    if cl is not None and cl > app.config['MAX_REQUEST_SIZE']:
        msg = "Request data size {} > limit ({})".format(
                cl, app.config['MAX_REQUEST_SIZE'])
        raise ApiError(msg, 400)



@app.route('/api/v1/object', methods=['POST'])
def object_post():
    try:
        start = time.clock()
        check_request_size_limit(request)
        xobj = request.get_json(force=False)
        data = try_adding_xobject(xobj)
        hippod.statistic.update_global_db_stats()
        end = time.clock()
    except ApiError as e:
        return e.transform()
    #except Exception as e:
    #    return ApiError(str(e), 500).transform()

    o = hippod.api_comm.Dict3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()



