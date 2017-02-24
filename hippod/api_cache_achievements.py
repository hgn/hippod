import json
import os
import datetime
import time
import sys

import aiohttp

import hippod.hasher
import hippod.ex3000

from hippod.error_object import *


def check_already_listed(buffer_stat, cat):
    listed = False
    for i, name in enumerate(d['name'] for d in buffer_stat['children']):
        if cat == name:
            listed = True
    return listed

def is_end_of_hierarchy(j, cat):
    end = False
    if j == len(cat)-1:
            end = True
    return end


def next_stat_in_hierarchy(buffer_stat, cat):
    for d in buffer_stat['children']:
        if d['name'] == cat:
            return d 


def get_results_by_category(app):
    cache_db = app['DB_CACHE_PATH']
    results_path = os.path.join(cache_db, 'cache-achievements.db')
    with open(results_path, 'r') as f:
        content = json.load(f)
    return content
    

def handle(request):
    if request.method != "GET":
        msg = "Internal Error... request method: {} is not allowed".format(request.method)
        raise hippod.error_object.ApiError(msg)
    app = request.app

    try:
        start = time.clock()
        data = get_results_by_category(app)
        end = time.clock()
    except ApiError as e:
        return e.transform()
    except Exception as e:
        return ApiError(str(e), 200).transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    return o.transform()