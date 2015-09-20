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


def object_get_int(xobj):
    ordering = "by-submitting-date-reverse"
    limit = sys.maxsize # "unlimited"
    if 'ordering' in xobj:
        ordering = xobj['ordering']
    if 'limit' in xobj:
        limit = int(xobj['limit'])
    



@app.route('/api/v1/object', methods=['GET'])
def object_get():
    try:
        start = time.clock()
        xobj = request.get_json(force=False)
        data = object_get_int(xobj)
        end = time.clock()
    except ApiError as e:
        return e.transform()
    except Exception as e:
        return ApiError(str(e), 500).transform()

    o = api_comm.Dict3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()



