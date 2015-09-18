#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import time

import object_hasher
from api_err_obj import *

from contestcolld import app

from flask import jsonify
from flask import request


def calc_ressource():
    raise ApiError("foobar", 404)
    return



@app.route('/api/v1.0/resources', methods=['GET'])
def get_resources():
    try:
        start = time.clock()
        data = calc_ressource()
        end = time.clock()
    except ApiError as e:
        return e.transform()
    except:
        pass


    o = Dict3000()
    o['data'] = dict()
    o['data']['overall'] = 40000
    o.http_code(202)
    return o.transform()

