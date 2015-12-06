import json
import os
import datetime
import inspect
import time
import zlib
import sys

import hippod.hasher
import hippod.ex3000
import hippod.api_shared

from hippod.error_object import *

from hippod import app

from flask import jsonify
from flask import request


def get_data_blob(sha_id, achievement_id):
    try:
        data = hippod.api_shared.get_attachment_data_by_sha_id(sha_sum, achievement_id)
    except:
        msg = "Achievment ID {} is not available".format(sha_sum)
        raise ApiError(msg, http_code=404)


def get_achievement_int(req_obj, sha_id, achievement_id):
    return get_data_blob(sha_id, achievement_id)


@app.route('/api/v1/achievement/<sha_id>/<achievement_id>', methods=['GET', 'POST'])
def get_achievment(sha_id, achievement_id):
    try:
        start = time.clock()
        req_obj = request.get_json(force=False)
        data = get_achievement_int(req_obj, sha_id, achievement_id)
        end = time.clock()
    except ApiError as e:
        return e.transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()

