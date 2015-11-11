#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import inspect
import time
import zlib
import sys

import hippod.object_hasher
import hippod.api_comm
import hippod.api_shared

from hippod.api_err_obj import *

from hippod import app

from flask import jsonify
from flask import request


def is_compressable_size(data):
    # smaller files will not benefit from
    # compression. The CPU overhead is not
    # justified
    if len(data['data']) > 1000:
        return True
    return False


def is_compressable_mime_type(data):
    if data['mime-type'] in ("binary/octet-stream",
                             "text/html",
                             "text/markdown",
                             "text/plain"):
        return True
    return False


def is_compressable(d):
    return is_compressable_size(d) and is_compressable_mime_type(d)


def decode_and_compress(data):
    uncompressed_len = len(data)
    decoded = hippod.object_hasher.decode_base64_data(data)
    compressed_data = zlib.compress(data)
    compressed_len = len(compressed_data)
    return compressed_data


def decode_and_write_file(sha_sum, data, compress=False):
    size_stats = dict()
    path = app.config['DB_DATA_PATH']
    obj_path = os.path.join(path, sha_sum)
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)

    blob_path = os.path.join(obj_path, "blob.bin")
    if os.path.isfile(blob_path):
        # great, file already in the database
        # do nothing
        return

    size_stats['base64-encoded'] = len(data['data'])
    if compress:
        bin_data = decode_and_compress(data['data'])
    else:
        bin_data = hippod.object_hasher.decode_base64_data(data['data'])

    size_stats['stored'] = len(bin_data)

    fd = open(blob_path, 'wb')
    fd.write(bin_data)
    fd.close()

    d = dict()
    d['mime-type'] = data['mime-type']
    d['compressed'] = 'true' if compress else 'false'
    d['statistics'] = size_stats
    d_json = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))
    attr_path = os.path.join(obj_path, "attr.db")
    fd = open(attr_path, 'w')
    fd.write(d_json)
    fd.close()


def save_object_item_data(data):
    # we need at least some data now:
    # - mimetype
    # - name
    # - data
    if not 'mime-type' in data:
        msg = "mime type always required for data: {}".format(str(data))
        raise ApiError(msg, 404)
    if 'type' in data and data['type'] != 'description':
        if not 'name' in data:
            msg = "for data a name is required: {}".format(str(data))
            raise ApiError(msg, 400)
    if not 'data' in data:
        msg = "a data section is required at least: {}".format(str(data))
        raise ApiError(msg, 400)


    # ok, data stuff
    sha = hippod.object_hasher.hash_data(data['data'])
    compressable = False
    if is_compressable(data):
        compressable = True
    decode_and_write_file(sha, data, compress=compressable)

    # update data entry
    del data['data']
    del data['mime-type']
    data['data-id'] = sha


def save_object_item_data_list(object_item):
    if not 'data' in object_item:
        return
    for data in object_item['data']:
        save_object_item_data(data)

