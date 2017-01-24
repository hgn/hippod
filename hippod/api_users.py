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

import aiohttp
import asyncio


def get_user_data(app, req_obj):
    if not 'filter' in req_obj:
        msg = "user data MUST contain a filter"
        raise ApiError(msg)
    user_filter = req_obj['filter']['username']
    return hippod.users.get(app, user_filter)


# async def handle(request):
#     if request.method != "GET" and request.method != "POST":
#         msg = "Internal Error... request method: {} is not allowed".format(request.method)
#         raise hippod.error_object.ApiError(msg)
#     app = request.app

#     try:
#         start = time.clock()
#         req_obj = await request.json()
#         data = get_user_data(app, req_obj)
#         end = time.clock()
#     except ApiError as e:
#         return e.transform()

#     o = hippod.ex3000.Ex3000()
#     o['data'] = data
#     o['processing-time'] = "{0:.4f}".format(end - start)
#     return o.transform()