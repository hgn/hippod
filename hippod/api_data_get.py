import json
import os
import datetime
import inspect
import time
import zlib
import sys

import flask

import hippod
import hippod.hasher
import hippod.api_comm
import hippod.api_shared
import hippod.error_object
import hippod.mime_data_db
import hippod.mime_renderer


def object_data_get_int(sha_sum, req_data):
    if not hippod.mime_data_db.obj_available(sha_sum):
        msg = "Data ({}) not available".format(sha_sum)
        raise hippod.error_object.ApiError(msg, 400)
    attr_obj = hippod.mime_data_db.get_attr_obj(sha_sum)
    decompressed = hippod.mime_data_db.is_attr_compressed(attr_obj)
    data = hippod.mime_data_db.get_data(sha_sum, decompress=decompressed, encode_base64=False)
    if attr_obj['mime-type'] == 'text/markdown':
        data = hippod.mime_renderer.mime_markdown(data)

    return attr_obj['mime-type'], data
    

@hippod.app.route('/api/v1/data/<sha_id>', methods=['GET', 'POST'])
def object_data_get(sha_id):
    try:
        start = time.clock()
        requested_encoding = flask.request.args.get('encoding')
        req_obj = flask.request.get_json(force=False)
        mime_type, data = object_data_get_int(sha_id, req_obj)
        end = time.clock()
    except hippod.error_object.ApiError as e:
        return e.transform()

    return flask.Response(data, mimetype=mime_type)
