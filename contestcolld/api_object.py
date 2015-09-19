#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import inspect
import time
import zlib

import object_hasher
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
    return False

def decode_and_write_file_uncompressed(sha_sum, data):
    path = app.config['DB_UNCOMPRESSED_PATH']
    data_path = os.path.join(path, sha_sum)
    if os.path.isfile(data_path):
        # great, file already in the database
        # do nothing
        return

    # decode first
    decoded = object_hasher.decode_base64_data(data)
    fd = open(data_path, 'w')
    fd.write(decoded)
    fd.close()


def decode_and_write_file_compressed(sha_sum, data):
    path = app.config['DB_COMPRESSED_PATH']
    data_path = os.path.join(path, sha_sum)
    if os.path.isfile(data_path):
        # great, file already in the database
        # do nothing
        return

    # decode first
    #decoded = decode_base64_data(data['data'])
    compressed_data = zlib.compress(data)

    fd = open(data_path, 'w')
    fd.write(compressed_data)
    fd.close()


def save_object_item_data(object_item):
    if not 'data' in object_item:
        return
    for data in object_item['data']:
        if not 'mime-type' in data:
            msg = "mime type always required for data: {}".format(str(data))
            raise ApiError(msg, 404)

        if 'type' in data and data['type'] == "main":
            # the main type is not compressable
            # because main must be text or markdown
            if not "text/markdown" in data['mime-type'] and \
               not "text/plain" in data['mime-type']:
                msg = "mime type for main plain or markdown: {}".format(str(data))
                raise ApiError(msg, 404)
            # ok, fine - now skip this valid main (description) type
            continue

        # we need at least some data now:
        # - file-name
        # - data
        if not 'file-name' in data:
            msg = "for data a file-name is required: {}".format(str(data))
            raise ApiError(msg, 404)
        if not 'data' in data:
            msg = "a data section is required at least: {}".format(str(data))
            raise ApiError(msg, 404)


        # ok, data stuff
        sha = object_hasher.hash_data(data['data'])
        if not is_mime_type_compressable(data['mime-type']):
            # save the file directly but decode first
            decode_and_write_file_uncompressed(sha, data['data'])
            path = app.config['DB_UNCOMPRESSED_PATH']
        else:
            decode_and_write_file_compressed(sha, data['data'])
            path = app.config['DB_COMPRESSED_PATH']

        # update data entry
        del data['data']
        data['data-path'] = os.path.join(path, sha)
        data['data-id'] = sha



def create_container_data_merge_issue_new(sha_sum, object_item):
    date = datetime.datetime.now().isoformat('T') # ISO 8601 format
    d = dict()
    d['object-item-id'] = sha_sum
    d['date-added'] = date
    d['attachment'] = { }
    d['attachment-last-modified'] = date
    d['achievements'] = []

    # the object is a little bit special. We iterate over the
    # data section as always and compress or not compress
    # data and save it in a different path
    save_object_item_data(object_item)
    d['object-item'] = object_item

    #if 'attachment' in xobj and len(xobj['attachment']) > 0:
    #    if not check_attachment(xobj['attachment']):
    #        return [False, None]
    #    d['attachment'] = xobj['attachment']

    return json.dumps(d, sort_keys=True,indent=4, separators=(',', ': '))


def save_new_object_container(sha_sum, object_item):
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
        cd = create_container_data_merge_issue_new(sha_sum, object_item)
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


def read_obj_by_id(sha_sum):
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha_sum[0:2],
                        sha_sum,
                        'container.db')
    if not os.path.isfile(path):
        return [False]
    with open(path) as data_file:
        data = json.load(data_file)
    return [True, data]

def write_file(sha, py_object):
    data = json.dumps(py_object, sort_keys=True,indent=4, separators=(',', ': '))
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'container.db')
    fd = open(path, 'w')
    fd.write(data)
    fd.close()

def write_achievement_file(sha, id_no, py_object):
    data = json.dumps(py_object, sort_keys=True,indent=4, separators=(',', ': '))
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'achievements',
                        '{0:04d}.db'.format(id_no))
    fd = open(path, 'w')
    fd.write(data)
    fd.close()


def update_attachment_achievement(sha_sum, xobj):
    # ok, the object is in database, we now update the data
    # attachments are updated (overwrite), achievements are
    # added
    rewrite_required = False
    (ret, data) = read_obj_by_id(sha_sum)
    if not ret:
        app.logger.error("path is not available!")
        return False

    if 'attachment' in xobj:
        if type(xobj['attachment']) is not dict:
                app.logger.error("attachment data MUST be a dict - but isn't")
                return False
        data['attachment'] = xobj['attachment']
        data['attachment-last-modified'] = datetime.datetime.now().isoformat('T')
        rewrite_required = True

    if 'achievements' in xobj:
        if type(xobj['achievements']) is not list:
                app.logger.error("achievements data MUST be a list - but isn't")
                return False
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
        app.logger.error("rewrite object.db file")
        write_file(sha_sum, data)


    return True


def try_adding_xobject(xobj):
    if not 'object-item' in xobj and not 'object-item-id' in xobj:
        msg = "object data corrupt - no object-item" \
              " or object-item-id given"
        raise ApiError(msg, 404)

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
                raise ApiError(msg, 404)
    else:
        sha_sum = xobj['object-item-id']

    ret = is_obj_already_in_db(sha_sum)
    if not ret:
        # new entry
        save_new_object_container(sha_sum, xobj['object-item'])

    #update_attachment_achievement(sha_sum, xobj)



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

    o = Dict3000()
    o['data'] = data
    o['duration'] = end - start
    o.http_code(202)
    return o.transform()



