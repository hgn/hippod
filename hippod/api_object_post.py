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
import hippod.statistic
import hippod.mime_data_db
import hippod.store_container

from hippod.error_object import *

log = logging.getLogger()



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


def is_obj_major_already_in_db(app, sha_major):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        'container.db')
    if os.path.isfile(path):
        return True
    else:
        return False


def is_obj_minor_already_in_db(app, sha_major, sha_minor):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        sha_minor,
                        'subcontainer.db')
    if os.path.isfile(path):
        return True
    else:
        return False


def write_cont_obj_by_id(app, sha_major, py_object):
    data = json.dumps(py_object, sort_keys=True,indent=4,
                      separators=(',', ': '))
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        'container.db')
    with open(path,'w') as fd:
        fd.write(data)

def write_subcont_obj_by_id(app, sha_major, sha_minor, py_object):
    data = json.dumps(py_object, sort_keys=True,indent=4,
                      separators=(',', ': '))
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        sha_minor,
                        'subcontainer.db')
    with open(path,'w') as fd:
        fd.write(data)


def write_achievement_file(app, sha_major, sha_minor, id_no, achievement):
    obj_path = os.path.join(app['DB_OBJECT_PATH'])
    path = os.path.join(obj_path, sha_major[0:2], sha_major, sha_minor, 'achievements',
                         '{}.db'.format(str(id_no)))
    # swap out data if mime types say so and modify
    # achievement inplace to reflect changes
    hippod.mime_data_db.save_object_item_data_list(app, achievement, path, 'achievement')

    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        sha_minor,
                        'achievements',
                        '{}.db'.format(id_no))
    data = json.dumps(achievement, sort_keys=True,indent=4,
                      separators=(',', ': '))
    with open(path,'w') as fd:
        fd.write(data)


def write_attachment_file(app, sha_major, id_no, attachment):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        'attachments',
                        '{}.db'.format(id_no))
    data = json.dumps(attachment, sort_keys=True,indent=4,
                      separators=(',', ': '))
    with open(path,'w') as fd:
        fd.write(data)


def add_subcontainer_list(app, sha_major, sha_minor, submitter, date_added):
    date = datetime.datetime.now().isoformat('T')
    try:
        path = app['DB_OBJECT_PATH']
        container_file = os.path.join(path, sha_major[0:2], sha_major, 'container.db')
        with open(container_file, 'r') as file:
            cntr = json.load(file)
            new_sub_cntr = dict()
            new_sub_cntr['sha-minor'] = sha_minor
            user_data = hippod.users.get(app, submitter, 'submitter')
            new_sub_cntr['submitter'] = user_data[0]['fullname']
            new_sub_cntr['date-added'] = date
            cntr['subcontainer-list'].append(new_sub_cntr)
        with open(container_file, 'w') as file:
            cntr = json.dumps(cntr, sort_keys=True, indent=4, separators=(',', ': '))
            file.write(cntr)
    except Exception:
        msg = "Internal Error...file {} maybe not available, although wanted to update?"
        msg = msg.format(path)
        raise ApiError(msg)


def validate_date(formated_data):
    # only supported format: 2015-09-15T22:24:29.158759"
    try:
        datetime.datetime.strptime(formated_data, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError as e:
        raise ApiError("date is not ISO8601 formatted")


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


def update_attachment_achievement(app, sha_major, sha_minor, xobj):
    # ok, the object is in database, we now update the data
    # attachments are updated (overwrite), achievements are
    # added
    rewrite_required = False
    date = datetime.datetime.now().isoformat('T')
    ok, data = hippod.api_shared.read_cont_obj_by_id(app, sha_major)
    ok2, data_sub = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sha_minor)
    if not ok or not ok2:
        msg = "cannot read object although it is an update!?"
        raise ApiError(msg)

    user_data = hippod.users.get(app, xobj['submitter'], 'submitter')
    submitter = user_data[0]['fullname']

    if 'attachment' in xobj:
        if type(xobj['attachment']) is not dict:
                msg = "attachment data MUST be a dict - but isn't"
                raise ApiError(msg)
        if 'categories' in xobj['attachment']:
            log.warning("Categories shouldn't be part of attachments, they belong to object-item")

        current_attachments = data['attachments']
        current_attachments_no = len(current_attachments)
        if current_attachments_no <= 0:
            new_attachment_meta = dict()
            new_attachment_meta['id'] = current_attachments_no
            new_attachment_meta['date-added'] = date
            new_attachment_meta['submitter'] = submitter

            current_attachments.append(new_attachment_meta)
            user_data = hippod.users.get(app, xobj['attachment']['responsible'], 'responsible')
            responsible = user_data[0]['fullname']
            xobj['attachment']['responsible'] = responsible
            write_attachment_file(app, sha_major, current_attachments_no, xobj['attachment'])
            data['attachments'] = current_attachments
            rewrite_required = True
        else:
            last_attachment = hippod.api_shared.get_attachment_data_by_sha_id(app, sha_major, current_attachments_no - 1)
            sha_attach_last = hippod.hasher.check_sum_attachment(last_attachment)
            sha_attach_new  = hippod.hasher.check_sum_attachment(xobj['attachment'])
            if sha_attach_last != sha_attach_new:
                new_attachment_meta = dict()
                new_attachment_meta['id'] = current_attachments_no
                new_attachment_meta['date-added'] = date
                new_attachment_meta['submitter'] = submitter

                current_attachments.append(new_attachment_meta)
                user_data = hippod.users.get(app, xobj['attachment']['responsible'], 'responsible')
                responsible = user_data[0]['fullname']
                xobj['attachment']['responsible'] = responsible
                write_attachment_file(app, sha_major, current_attachments_no, xobj['attachment'])
                data['attachments'] = current_attachments
                rewrite_required = True

    if 'achievements' in xobj:
        if type(xobj['achievements']) is not list or len(xobj['achievements']) == 0:
                msg = "achievements data MUST be a list - but isn't or is empty"
                raise ApiError(msg)
        current_achievements = data_sub["achievements"]
        current_achievements_no = len(current_achievements)
        # add new achievements in same order
        for a in xobj['achievements']:
            validate_achievement(a)
            new_data = dict()
            new_data['id'] = current_achievements_no
            new_data['date-added'] =  date
            new_data['variety-id'] = hippod.hasher.calc_variety_id(a)
            new_data['lifetime-leftover'] = hippod.store_container.get_lifetime(app, xobj)
            current_achievements.append(new_data)

            # additionally, we add the submitter to the achievement
            a['submitter'] = submitter

            # now we save the achievement in a seperate file
            write_achievement_file(app, sha_major, sha_minor, current_achievements_no, a)
            current_achievements_no += 1

        data_sub["achievements"] = current_achievements
        rewrite_required_sub = True

    if rewrite_required:
        write_cont_obj_by_id(app, sha_major, data)
    if rewrite_required_sub:
        write_subcont_obj_by_id(app, sha_major, sha_minor, data_sub)


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
    with open(object_index_db_path, 'w') as fd:
        fd.write(data)


def object_index_initial_add_major(app, sha_major, xobj):
    # read existing data set
    object_index = object_index_init(app)
    # create new data set
    d = dict()
    d['object-item-id'] = sha_major
    # append new data set
    object_index.append(d)
    # update the object index
    object_index_update(app, object_index)


def check_anchor(app, xobj):
    achievements = xobj['achievements']
    for achievement in achievements:
        if 'anchor' in achievement:
            return True
    return False

def prove_bigger_lifetime_overwritten(listed_lifetime, new_lifetime):
    # in case older test was anchored, new test not anchored and older lifetime
    # bigger than new one...would be wrong to overwrite the lifetime
    if listed_lifetime < new_lifetime:
        return new_lifetime
    else:
        return listed_lifetime


def update_lifetime(app, sha_major, sha_minor, xobj):
    anchor_available = check_anchor(app, xobj)
    conf = app['CONF']
    garbage = hippod.garbage_handler_container_achievements.GHContainerAchievements()
    ok, subcontainer = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sha_minor)
    if not ok:
        msg = "can not read subcontainer by id '{}/{}'. Although it is an update and subcontainer\
               should be available.".format(sha_major, sha_minor)
        log.error(msg)
        return
    default_lifetime = garbage.convert_lifetime(conf.achievements_validity_lifetime.achievements)
    anchor_lifetime = garbage.convert_lifetime(conf.achievements_validity_lifetime.achievements_anchored)
    if anchor_available:
        subcontainer['lifetime-leftover'] = anchor_lifetime
    else:
        subcontainer['lifetime-leftover'] = prove_bigger_lifetime_overwritten(subcontainer['lifetime-leftover'], 
                                                                            default_lifetime)
    subc_path = os.path.join(app['DB_OBJECT_PATH'], sha_major[0:2], sha_major, sha_minor, 'subcontainer.db')
    with open(subc_path, 'w') as f:
        json_cont = json.dumps(subcontainer, sort_keys=True, indent=4, separators=(',', ': '))
        f.write(json_cont)


def try_adding_xobject(app, xobj):
    if not 'submitter' in xobj:
        msg = "No submitter in xobject given!"
        raise ApiError(msg)

    if not 'object-item' in xobj and not 'object-item-id' in xobj:
        msg = "object data corrupt - no object-item" \
              " or object-item-id given"
        raise ApiError(msg)

    if not 'achievements' in xobj:
        msg = "test has no achievements array, not allowed"
        raise ApiError(msg)

    if type(xobj['achievements']) is not list or len(xobj['achievements']) == 0:
        msg = "achievements data MUST be a list - but isn't or is empty"
        raise ApiError(msg)

    if 'object-item' in xobj:
        # calculate the ID now
        sha_major, sha_minor = hippod.hasher.check_sum_object_issue(xobj['object-item'])

    else:
        msg = "Need at least a Full Object Item or Object Item ID"
        raise ApiError(msg)

    # FIXME: in the remaining paragraph there is a race condition
    # leads to data corruption. Problem is that data is writen
    # to file partly and later the achievement can be miss-formated.
    # object container file write should be delayed until everything
    # is sane.
    ok = is_obj_major_already_in_db(app, sha_major)
    # check whether anchor is in achievement to add correct initial lifetime of the object
    if not ok:
        # new entry, save to file container.db
        # FULL update
        hippod.store_container.save_new_object_container(app, sha_major, sha_minor, xobj)
        object_index_initial_add_major(app, sha_major, xobj)

    ok2 = is_obj_minor_already_in_db(app, sha_major, sha_minor)
    if not ok2:
        # new entry, save to file subcontainer.db
        date_added = hippod.store_container.save_new_object_minor_container(app, sha_major, sha_minor, xobj)
        add_subcontainer_list(app, sha_major, sha_minor, xobj['submitter'], date_added)

    update_lifetime(app, sha_major, sha_minor, xobj)

    update_attachment_achievement(app, sha_major, sha_minor, xobj)

    ret_data = dict()
    ret_data['id'] = sha_major
    ret_data['sub_id'] = sha_minor
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
        print(e)
        return e.transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()
