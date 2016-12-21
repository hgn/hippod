#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import inspect
import time
import zlib
import sys
import re
import asyncio
import functools

import hippod.hasher
import hippod.ex3000
import hippod.report_generator


from hippod.error_object import *


def generate_doc(app, own_filter):
    rep_gen = hippod.report_generator.ReportGenerator()
    if own_filter['filter-type'] == 'Latest Tests':
        rep_gen.generate(app, outputs=[rep_gen.PDF], report_filter=rep_gen.LAST_ACHIEVEMENTS)
    if own_filter['filter-type'] == 'Anchored Tests':
        rep_gen.generate(app, outputs=[rep_gen.PDF], report_filter=rep_gen.FILTER_BY_ANCHOR)


def generate_doc_later(app, report_filter):
    own_filter = dict()

    if report_filter == 'Latest Tests':
        own_filter['filter-type'] = 'Latest Tests'
    elif report_filter == 'Anchored Tests':
        own_filter['filter-type'] = 'Anchored Tests'
    else:
        msg = "No valid Filter"
        raise ApiError(msg)                                          # arrange filter check!
    loop = asyncio.get_event_loop()
    loop.call_soon(functools.partial(generate_doc, app, own_filter))
    generate_doc(app, own_filter)


async def handle(request):
    # if request.method != "GET":
    #     msg = "Internal Error...request method: {} is not allowed".format(request.method)
    #     raise ApiError(msg)
    app = request.app
    try:
        start = time.clock()
        report_filter = await request.json()
        print(report_filter)
        generate_doc_later(app, report_filter)
        end = time.clock()
    except ApiError as e:
        return e.transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = None
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()