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
        rep_gen.generate(app, outputs=[rep_gen.PDF], report_filter=rep_gen.LAST_ACHIEVEMENTS, report_meta=None)
    elif own_filter['filter-type'] == 'Anchored Tests':
        rep_gen.generate(app, outputs=[rep_gen.PDF], report_filter=rep_gen.FILTER_BY_ANCHOR, report_meta=None)
    elif own_filter['filter-type'] == 'Special Tests':
        rep_gen.generate(app, outputs=[rep_gen.PDF], report_filter=rep_gen.FILTER_BY_SPECIAL, report_meta=own_filter['filter-meta'])


def generate_doc_later(app, report_filter):
    own_filter = dict()

    if report_filter['type'] == 'Latest Tests':
        own_filter['filter-type'] = 'Latest Tests'
    elif report_filter['type'] == 'Anchored Tests':
        own_filter['filter-type'] = 'Anchored Tests'
    elif report_filter['type'] == 'Special Tests':
        own_filter['filter-type'] = 'Special Tests'
        own_filter['filter-meta'] = report_filter['filter-meta']
        # FIXME: filter check for keys here!
    else:
        msg = "No valid Filter"
        raise ApiError(msg)                                          # arrange filter check!
    loop = asyncio.get_event_loop()
    loop.call_soon(functools.partial(generate_doc, app, own_filter))


async def handle(request):
    if request.method != "POST":
        msg = "Internal Error...request method: {} is not allowed".format(request.method)
        raise ApiError(msg)
    app = request.app
    try:
        start = time.clock()
        report_filter = await request.json()
        # report_filter = dict()
        # report_filter['type'] = 'Special Tests'
        # report_filter['filter-meta'] = dict()
        # report_filter['filter-meta']['anchors'] = ['c4a8c', 'a5adb']
        # report_filter['filter-meta']['submitter'] = ['John Doe', 'Marie Curie', 'Charles Darwin']
        generate_doc_later(app, report_filter)
        end = time.clock()
    except ApiError as e:
        return e.transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = None
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()
