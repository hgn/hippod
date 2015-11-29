#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import time
import sys

import hippod.object_hasher
import hippod.api_comm

from hippod.api_err_obj import *

from hippod import app

from flask import jsonify
from flask import request


def get_statistics():
    return hippod.statistic.get()

@app.route('/api/v1.0/resources', methods=['GET'])
def get_resources():
    try:
        start = time.clock()
        data = get_statistics()
        end = time.clock()
    except ApiError as e:
        return e.transform()
    #except Exception as e:
    #    return ApiError(str(e), 200).transform()

    o = hippod.api_comm.Dict3000()
    o['data'] = data
    o.http_code(202)
    return o.transform()

