#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import time
import sys

import aiohttp

import hippod.hasher
import hippod.ex3000

from hippod.error_object import *



def get_statistics():
    return hippod.statistic.get()


def handle(request):
	print("Resources Loading:")
	if request.method != "GET":
		msg = "Internal Error... request method: {} is not allowed".format(request.method)
		raise hippod.error_object.ApiError(msg)

	try:
		start = time.clock()
		data = get_statistics()
		end = time.clock()
	except ApiError as e:
		return e.transform()
	except Exception as e:
		return ApiError(str(e), 200).transform()

	o = hippod.ex3000.Ex3000()
	o['data'] = data
	return o.transform()


