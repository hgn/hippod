import json
import os
import datetime
import inspect
import time
import zlib
import sys
import shutil
import logging

import hippod.hasher
import hippod.api_shared
import hippod.snippet_db

from hippod.error_object import *

log = logging.getLogger()


def obj_available(app, sha_sum):
    path = app['DB_DATA_PATH']
    obj_path  = os.path.join(path, sha_sum, "blob.bin")
    attr_path = os.path.join(path, sha_sum, "attr.db")

    if not os.path.isfile(obj_path) or not os.path.isfile(attr_path):
        return False
    return True


def get_attr_obj(app, sha_sum):
    path = app['DB_DATA_PATH']
    attr_path = os.path.join(path, sha_sum, "attr.db")
    with open(attr_path) as data_file:
        return json.load(data_file)


def is_attr_compressed(obj):
    return obj['compressed'] == 'true'


def get_data(app, sha_sum, decompress=None, encode_base64=False):
    if decompress == None:
        msg = "decompres True or False required"
        raise ApiError(msg)

    path = app['DB_DATA_PATH']
    obj_path  = os.path.join(path, sha_sum, "blob.bin")
    with open(obj_path, 'rb') as f:
        data = f.read()
        if decompress == True:
            data = zlib.decompress(data)
        return data
    msg = "failed to open {}".format(obj_path)
    raise ApiError(msg)


def get_snippet_data(app, sha_sum, mimetype):
    snippet_db = app['DB_SNIPPET_PATH']
    d_type = mimetype.split('-')[-1]
    image_path = os.path.join(snippet_db, '{}.{}'.format(sha_sum, d_type))
    with open(image_path, 'rb') as f:
        data = f.read()
        return data
    msg = "failed to open {}".format(obj_path)


def is_compressable_size(data):
    # smaller files will not benefit from compression. The CPU overhead is not
    # justified. Additionally, standard file systems will at least consume one
    # block anyway, so there is no gain to compress these small files. (yes
    # there are FS exceptions where file system may store tiny files more
    # efficiently). Assume blocksize of 4096 for now. 
    if len(data['data']) > 4096:
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
    byte_array = data.encode(encoding='UTF-8')
    decoded = hippod.hasher.decode_base64_data(byte_array)
    size_real = len(decoded)
    compressed_data = zlib.compress(decoded)
    compressed_len = len(compressed_data)
    return compressed_data, size_real


def decode_and_write_file(app, sha_sum, data, compress=False):
    size_stats = dict()
    snippet_available = False
    path = app['DB_DATA_PATH']
    obj_path = os.path.join(path, sha_sum)
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)

    blob_path = os.path.join(obj_path, "blob.bin")
    if os.path.isfile(blob_path):
        # great, file already in the database
        # return original attr.db
        return get_attr_obj(app, sha_sum)

    size_stats['base64-encoded'] = len(data['data'])
    if compress:
        bin_data, size_real = decode_and_compress(data['data'])
    else:
        byte_array = data['data'].encode(encoding='UTF-8')
        bin_data = hippod.hasher.decode_base64_data(byte_array)
        size_real = len(bin_data)
    size_stats['size-stored'] = len(bin_data)
    size_stats['size-real'] = size_real
    hippod.statistic.update_mimetype_data_store(app,
                                                data['mime-type'],
                                                size_real,
                                                len(bin_data),
                                                compress)

    with open(blob_path, 'wb') as fd:
        fd.write(bin_data)

    d = dict()
    d['mime-type'] = data['mime-type']
    d['compressed'] = 'true' if compress else 'false'
    d['statistics'] = size_stats
    d_json = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))
    attr_path = os.path.join(obj_path, "attr.db")
    with open(attr_path, 'w') as fd:
        fd.write(d_json)
    return d


def save_object_item_data(app, data, source_path, source_type):
    # we need at least some data now:
    # - mimetype
    # - name
    # - data
    if not 'mime-type' in data:
        msg = "mime type always required for data: {}".format(str(data))
        raise ApiError(msg)
    if 'type' in data and data['type'] != 'description':
        if not 'name' in data:
            msg = "for data a name is required: {}".format(str(data))
            raise ApiError(msg)
    if not 'data' in data:
        msg = "a data section is required at least: {}".format(str(data))
        raise ApiError(msg)

    # ok, data stuff
    sha = hippod.hasher.hash_data(data['data'])
    if data['mime-type'].startswith('x-snippet'):
        hippod.snippet_db.register_snippet(app, data, sha, source_path, source_type)
        # FIXME: truncate possible format endings png, jpg and so on?
        # hardcoded formats
        if 'name' in data and data['name'] is not None and '.' not in data['name']:
            data['name'] = '{}.py'.format(data['name'])
        elif 'name' in data and data['name'] is not None and '.' in data['name']:
            data['name'] = '{}.py'.format(data['name'].split('.')[0])
        else:
            data['name'] = 'snippet-{}.py'.format(sha)


    compressable = False
    if is_compressable(data):
        compressable = True
    attr_data = decode_and_write_file(app, sha, data, compress=compressable)
    # update data entry
    del data['data']
    del data['mime-type']
    data['data-id'] = sha
    # data['size-real'] = attr_data['statistics']['size-real']


def save_object_item_data_list(app, object_item, source_path, source_type):
    if not 'data' in object_item:
        return
    for data in object_item['data']:
        save_object_item_data(app, data, source_path, source_type)


def get_saved_data(app):
    db_path = app['DB_DATA_PATH']
    data_list = os.listdir(db_path)
    return data_list


def remove_data(app, data_list):
    db_path = app['DB_DATA_PATH']
    for data in data_list:
        data_path = os.path.join(db_path, data)
        if os.path.isdir(data_path):
            shutil.rmtree(data_path)
        else:
            log.error('data path {} is not a directory, ignore for now'.format(data_path))
            continue