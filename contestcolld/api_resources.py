#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime

from contestcolld import app

from flask import jsonify
from flask import request



@app.route('/api/v1.0/resources', methods=['GET'])
def get_resources():
    data = dict()
    data['overall'] = 10030303
    data['subgroup-a'] = 4919223
    data['subgroup-b'] = 391922
    data['subgroup-c'] = 54922
    data['subgroup-d'] = 395914
    return jsonify(data)

