#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import time
import sys

import hippod.hasher
import hippod.ex3000
import hippod.users

from hippod.error_object import *

from hippod import app

from flask import jsonify
from flask import request


@app.route('/api/v1/ping', methods=['GET'])
def handle_ping():
    data = dict()
    data['version'] = app.config['VERSION']

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o.http_code(202)
    return o.transform()

