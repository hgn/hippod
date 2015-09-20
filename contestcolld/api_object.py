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

from contestcolld import app

from flask import jsonify
from flask import request



def check_attachment(attachment):
    if type(attachment) is not dict:
        return False
    return True


def is_mime_type_compressable(mime_type):
    if mime_type == "binary/octet-stream":
        return True
    if mime_type == "text/html":
        return True
    if mime_type == "text/plain":
        return True
    return False

def decode_and_write_file_uncompressed(sha_sum, data_type, data):
    path = app.config['DB_UNCOMPRESSED_PATH']
    type_path = os.path.join(path, data_type)
    # check that type path (png, jpg, ...) is already created
    if not os.path.isdir(type_path):
        os.makedirs(type_path)

    data_path = os.path.join(type_path, sha_sum)
    if os.path.isfile(data_path):
        # great, file already in the database
        # do nothing
        return

    # decode first
    decoded = object_hasher.decode_base64_data(data)
    fd = open(data_path, 'w')
    fd.write(decoded)
    fd.close()


def decode_and_write_file_compressed(sha_sum, data_type, data):
    path = app.config['DB_COMPRESSED_PATH']
    type_path = os.path.join(path, data_type)
    # check that type path (png, jpg, ...) is already created
    if not os.path.isdir(type_path):
        os.makedirs(type_path)

    data_path = os.path.join(type_path, sha_sum)
    if os.path.isfile(data_path):
        # great, file already in the database
        # do nothing
        return

    uncompressed_len = len(data)
    # decode first
    #decoded = decode_base64_data(data['data'])
    compressed_data = zlib.compress(data)
    compressed_len = len(compressed_data)
    msg = "compressed data from {} byte to {} byte".format(uncompressed_len,
                                                      compressed_len)
    app.logger.info(msg)

    fd = open(data_path, 'w')
    fd.write(compressed_data)
    fd.close()

def save_object_item_data_list(object_item):
    if not 'data' in object_item:
        return
    for data in object_item['data']:
        save_object_item_data(data)


def save_object_item_data(data):
    if not 'mime-type' in data:
        msg = "mime type always required for data: {}".format(str(data))
        raise ApiError(msg, 404)

    if 'type' in data and data['type'] == "main":
        # the main type is not compressable
        # because it has performance impact and is expected
        # not large. main must be text or markdown
        if not "text/markdown" in data['mime-type'] and \
           not "text/plain" in data['mime-type']:
            msg = "mime type for main plain or markdown: {}".format(str(data))
            raise ApiError(msg, 404)
        # ok, fine - now skip this valid main (description) type
        return

    # we need at least some data now:
    # - name
    # - type
    # - data
    if not 'name' in data:
        msg = "for data a name is required: {}".format(str(data))
        raise ApiError(msg, 400)
    if not 'type' in data:
        msg = "for data a file-name is required: {}".format(str(data))
        raise ApiError(msg, 400)
    if not 'data' in data:
        msg = "a data section is required at least: {}".format(str(data))
        raise ApiError(msg, 400)


    # ok, data stuff
    sha = object_hasher.hash_data(data['data'])
    if not is_mime_type_compressable(data['mime-type']):
        # save the file directly but decode first
        path = decode_and_write_file_uncompressed(sha, data['type'], data['data'])
        path = app.config['DB_UNCOMPRESSED_PATH']
    else:
        path = decode_and_write_file_compressed(sha, data['type'], data['data'])
        path = app.config['DB_COMPRESSED_PATH']

    # update data entry
    del data['data']
    data['data-path'] = os.path.join(path, sha)
    data['data-id'] = sha


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
    d['attachment'] = { }
    d['attachment-last-modified'] = date
    d['achievements'] = []

    add_initial_maturity_level(object_item)

    # the object is a little bit special. We iterate over the
    # data section as always and compress or not compress
    # data and save it in a different path
    save_object_item_data_list(object_item)
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


def read_cont_obj_by_id(sha_sum):
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha_sum[0:2],
                        sha_sum,
                        'container.db')
    if not os.path.isfile(path):
        return [False]
    with open(path) as data_file:
        data = json.load(data_file)
    return [True, data]


def write_cont_obj_by_id(sha, py_object):
    data = json.dumps(py_object, sort_keys=True,indent=4, separators=(',', ': '))
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
    save_object_item_data_list(achievement)

    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'achievements',
                        '{}.db'.format(id_no))
    data = json.dumps(achievement, sort_keys=True,indent=4, separators=(',', ': '))
    fd = open(path, 'w')
    fd.write(data)
    fd.close()


def update_attachment_achievement(sha_sum, xobj):
    # ok, the object is in database, we now update the data
    # attachments are updated (overwrite), achievements are
    # added
    rewrite_required = False
    (ret, data) = read_cont_obj_by_id(sha_sum)
    if not ret:
        msg = "cannot read object although it is an update!?"
        raise ApiError(msg, 500)

    if 'attachment' in xobj:
        if type(xobj['attachment']) is not dict:
                msg = "attachment data MUST be a dict - but isn't"
                raise ApiError(msg, 400)
        data['attachment'] = xobj['attachment']
        data['attachment-last-modified'] = datetime.datetime.now().isoformat('T')
        rewrite_required = True

    if 'achievements' in xobj:
        if type(xobj['achievements']) is not list:
                msg = "achievements data MUST be a list - but isn't"
                raise ApiError(msg, 400)
        current_achievements = data["achievements"]
        current_achievements_no = len(current_achievements)
        # add new achievements in same order
        for a in xobj['achievements']:
            new_data = dict()
            new_data['id'] = current_achievements_no
            new_data['date-added'] =  datetime.datetime.now().isoformat('T')
            current_achievements.append(new_data)

            # now we save the achievement in a seperate file
            write_achievement_file(sha_sum, current_achievements_no, a)
            current_achievements_no += 1

        data["achievements"] = current_achievements
        rewrite_required = True

    if rewrite_required:
        app.logger.info("rewrite object DB container file")
        write_cont_obj_by_id(sha_sum, data)


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
        sha_sum = object_hasher.check_sum_object_issue(xobj['object-item'])
        if 'object-item-id' in xobj:
            # this is an additional check - both should be
            # identical
            if sha_sum != xobj['object-item-id']:
                msg = "object data corrupt - object item " \
                      "sha_sum missmatch to object-item-id"
                raise ApiError(msg, 400)
    else:
        sha_sum = xobj['object-item-id']

    ret = is_obj_already_in_db(sha_sum)
    if not ret:
        # new entry, save to file
        save_new_object_container(sha_sum, xobj['object-item'], xobj['submitter'])

    update_attachment_achievement(sha_sum, xobj)


@app.route('/api/v1/object', methods=['POST'])
def post_xobject():
    try:
        start = time.clock()
        xobj = request.get_json(force=False)
        data = try_adding_xobject(xobj)
        end = time.clock()
    except ApiError as e:
        return e.transform()
    #except Exception as e:
    #    return ApiError(str(e), 202).transform()

    o = api_comm.Dict3000()
    o['data'] = data
    o['duration'] = end - start
    o.http_code(200)
    return o.transform()



