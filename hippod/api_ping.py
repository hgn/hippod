#!/usr/bin/python3
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



async def handle(request):
	if request.method != "GET":
		msg = "Internal Error... request method: {} is not allowed".format(request.method)
		raise hippod.error_object.ApiError(msg)
	app = request.app

	data = dict()
	data['version'] = app['VERSION']
	print("\nVersion:")
	print(data['version'])
	o = hippod.ex3000.Ex3000()
	o['data'] = data
	o.http_code(202)
	return o.transform()

