import json
import os
import datetime
import inspect
import time
import zlib
import sys

import flask

import hippod
import hippod.object_hasher
import hippod.api_comm
import hippod.api_shared
import hippod.api_err_obj
import hippod.mime_data_db


def get_data(sha_sum):
    if not hippod.mime_data_db.obj_available(sha_sum):
        msg = "File not available"
        raise hippod.api_err_obj.ApiError(msg, 400)
    attr_obj = hippod.mime_data_db.get_attr_obj(sha_sum)
    decompressed = hippod.mime_data_db.is_attr_compressed(attr_obj)
    data = hippod.mime_data_db.get_data(sha_sum, decompress=decompressed, encode_base64=False)
    return attr_obj['mime-type'], data


def object_data_get_int(sha_sum):
    return get_data(sha_sum)
    

@hippod.app.route('/api/v1/data/<sha_id>', methods=['GET', 'POST'])
def object_data_get(sha_id):
    try:
        start = time.clock()
        mime_type, data = object_data_get_int(sha_id)
        end = time.clock()
    except hippod.api_err_obj.ApiError as e:
        return e.transform()
    #except Exception as e:
    #    return ApiError(str(e), 500).transform()

    return flask.Response(data, mimetype=mime_type)
