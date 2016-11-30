import json
import os
import datetime
import inspect
import time
import zlib
import sys

import aiohttp
import asyncio

import hippod.hasher
import hippod.ex3000
import hippod.api_shared

from hippod.error_object import *



def get_data_blob(app, sha_major, sha_minor, achievement_id):
    try:
        data = hippod.api_shared.get_achievement_data_by_sha_id(app, sha_major, sha_minor, achievement_id)
        print(data)
        return data
    except:
        msg = "Achievment ID {} or {} is not available".format(sha_major, sha_minor)
        raise ApiError(msg, http_code=404)


def get_achievement_int(app, sha_major, sha_minor, achievement_id):
    return get_data_blob(app, sha_major, sha_minor, achievement_id)


async def handle(request):
    if request.method != "GET" and request.method != "POST":
        msg = "Internal Error... request method: {} is not allowed".format(request.method)
        raise hippod.error_object.ApiError(msg)
    app = request.app
    sha_major = request.match_info['sha_major']
    sha_minor = request.match_info['sha_minor']
    achievement_id = request.match_info['achievement_id']


    try:
        start = time.clock()
        data = get_achievement_int(app, sha_major, sha_minor, achievement_id)
        print(data)
        end = time.clock()
    except ApiError as e:
        return e.transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()