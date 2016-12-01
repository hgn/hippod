import json
import os
import datetime
import inspect
import time
import zlib
import sys

import aiohttp
import asyncio

import hippod
import hippod.hasher
import hippod.ex3000
import hippod.api_shared
import hippod.error_object
import hippod.mime_data_db
import hippod.mime_renderer


def object_data_get_int(app, sha_sum):
    if not hippod.mime_data_db.obj_available(app, sha_sum):
        msg = "Data ({}) not available".format(sha_sum)
        raise hippod.error_object.ApiError(msg)
    attr_obj = hippod.mime_data_db.get_attr_obj(app, sha_sum)
    decompressed = hippod.mime_data_db.is_attr_compressed(attr_obj)
    data = hippod.mime_data_db.get_data(app, sha_sum, decompress=decompressed, encode_base64=False)
    if attr_obj['mime-type'] == 'text/markdown':
        data = hippod.mime_renderer.mime_markdown(data)

    return attr_obj['mime-type'], data


def handle(request):
    if request.method != "GET" and request.method != "POST":
        msg = "Internal Error... request method: {} is not allowed".format(request.method)
        raise hippod.error_object.ApiError(msg)
    app = request.app
    sha_sum = request.match_info['sha_sum']

    try:
        start = time.clock()
        mime_type, data = object_data_get_int(app, sha_sum)
        end = time.clock()
    except hippod.error_object.ApiError as e:
        return e.transform()
    data = str(data)
    return aiohttp.web.Response(body=data.encode('utf-8'), content_type=mime_type)