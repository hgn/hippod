#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import time
import sys

import hippod.hasher
import hippod.api_comm
import hippod.users

from hippod.api_err_obj import *

from hippod import app

from flask import jsonify
from flask import request


@app.route('/api/v1/ping', methods=['GET'])
def handle_ping():
    data = dict()
    data['version'] = app.config['VERSION']

    o = hippod.api_comm.Dict3000()
    o['data'] = data
    o.http_code(202)
    return o.transform()

