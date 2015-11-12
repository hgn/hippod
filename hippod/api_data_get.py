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
import hippod.api_err_obj

from hippod import app

from flask import jsonify
from flask import request


def get_data(sha_sum):
    if not data_obj_avail(sha_sum):
        msg = "File not available"
        raise ApiError(msg, 400)
    attr_obj = mime_data_db.get_attr_obj(sha_sum)
    decompressed = True if mime_data_db.is_data_compressed(attr_obj) else False 
    data = mime_data_db.get_data(sha_sum, decompress=decompressed, encode_base64=False)
    return attr_obj['mime-type'], data


def object_data_get_int(sha_sum):
    return get_data(sha_sum)
    

@app.route('/api/v1/data/<sha_id>', methods=['GET', 'POST'])
def object_data_get(sha_id):
    try:
        start = time.clock()
        data = object_data_get_int(sha_id)
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



