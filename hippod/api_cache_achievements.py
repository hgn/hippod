import json
import os
import datetime
import time
import sys

import aiohttp

import hippod.hasher
import hippod.ex3000

from hippod.error_object import *



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