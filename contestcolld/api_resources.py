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
    return jsonify({'tasks': "foo"})

