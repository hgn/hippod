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

import hippod.api_object_get_detail
import hippod.api_shared
import hippod.hasher
import hippod.ex3000
import hippod.report_generator

from hippod.error_object import *

# arrange document


def get_data_by_id():
    return


def sanitize_description(description_path):
    with open(description_path, 'r') as input_text:
        in_descr = input_text.readlines()
    with open(description_path, 'w') as output_text:
        # m = re.search(r'image[.]png', descr)            # ^[![]
        # matches = re.findall(r'^#[#]*', descr, re.MULTILINE)
        for line in in_descr:
            # match = re.search(r'(^#[#]*) .* (#[#]*$)', line)
            match = re.search(r'^#[#]*', line)
            p = re.compile(r'(#[#]*)')
            if match != None:
                # newline = re.sub(r'(^#[#]*) .* (#[#]*$)', r'\1# #\2', line)
                newline = p.sub('{}#'.format(match.group(0)), line)
                output_text.write(newline)
            else:
                output_text.write(line)


def check_image_reference(description_path, attach_path):
    reference_avaible = False
    head, tail = os.path.split(attach_path)
    with open(description_path, 'r') as input_text:
        in_descr = input_text.readlines()
    with open(description_path, 'w') as output_text:
        for line in in_descr:
            match = re.search(r'(\()(.*[.]png)', line)       # jpeg,...  # enough to assume there's a reference?
            p = re.compile(r'\(.*[.]png')
            if match != None:
                if match.group(2) == tail:
                    reference_avaible = True
                    newline = p.sub('({}'.format(attach_path), line)
                    output_text.write(newline)
                else:
                    output_text.write(line)
            else:
                output_text.write(line)
    return reference_avaible

def data_from_subcontainer(app, sha_major, sha_minor):
    ok, subcont = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sha_minor)
    if not ok:
        msg = "subcontainer {} not available, although entry in subcontainer-list"
        msg = msg.format(sub_cont['sha-minor'])
        raise ApiError(msg)
    return subcont['object-item']['data']


def filter_last_achievement(app, sha_major, cont_obj):
    ret_obj = dict()
    buff_dict = dict()

    # fetch latest subcontainer (subcontainer with latest achievement) and related meta
    for sub_cont in cont_obj['subcontainer-list']:
        ok, full_sub_cont = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sub_cont['sha-minor'])
        if not ok:
            msg = "subcontainer {} not available, although entry in subcontainer-list"
            msg = msg.format(sub_cont['sha-minor'])
            raise ApiError(msg)
        data = hippod.api_object_get_full.get_all_achievement_data(app, sha_major, sub_cont['sha-minor'], full_sub_cont)
        if data:
            buff_dict[sub_cont['sha-minor']] = data[0]['date-added']
    if data:
        latest_sha_minor = max(buff_dict, key=lambda key: buff_dict[key])
        latest_subcont = next(d for (index,d) in enumerate(cont_obj['subcontainer-list']) if d['sha-minor']==latest_sha_minor)
        latest_index = next(index for (index,d) in enumerate(cont_obj['subcontainer-list']) if d['sha-minor']==latest_sha_minor)

    ret_obj['sha-major'] = sha_major

    if not data:
        sub_cont_last = cont_obj['subcontainer-list'][0]
        latest_sha_minor = sub_cont_last['sha-minor']
    else:
        sub_cont_last = cont_obj['subcontainer-list'][latest_index]
    ret_obj['sha-minor'] = sub_cont_last['sha-minor']

    db_root_path = app['DB_OBJECT_PATH']
    subcntr_path = os.path.join(db_root_path, sha_major[0:2], sha_major,\
                                latest_sha_minor, 'subcontainer.db')
    with open(subcntr_path) as file:
        full_sub_cont_last = json.load(file)

    # add last achievement with basic information
    data = hippod.api_object_get_detail.get_last_achievement_data(app, sha_major, latest_sha_minor, full_sub_cont_last)
    ret_obj['last-achievement'] = data
    ret_obj['data'] = data_from_subcontainer(app, sha_major, ret_obj['sha-minor'])
    return True, ret_obj


def object_data_by_id(app, sha_major):
    ret, cont_obj = hippod.api_shared.read_cont_obj_by_id(app, sha_major)
    if not ret:
        msg = "cannot read object by id: {}".format(sha_major)
        raise ApiError(msg)
    return filter_last_achievement(app, sha_major, cont_obj)        # decide here by filter which function is called


def null_func(data):
    pass


def object_get_int(app):
    object_index_data = hippod.api_shared.object_index_read(app)
    if not object_index_data:
        return None
    # maybe specify limit in filter?
    ret_data = list()
    list_sort_func = (null_func, reversed)[bool(True)]          # here variable reversed instead of hardcoded True
    for cont in list_sort_func(object_index_data):
        ok, data = object_data_by_id(app, cont['object-item-id'])
        if not ok:
            continue
        ret_data.append(data)
    return ret_data


def create_report(app, generator, collected_data, date):
    report_name = '{} - report.pdf'.format(date)
    report_path = os.path.join(app['TMP_PATH'], report_name)
    report_creator = generator.ReportGeneratorDocument('pdf', report_path)
    sub_reports = list()
    for key, item in collected_data.items():
        for d in item:
            name, data_type = os.path.splitext(d)
            if data_type == '.md':
                sanitize_description(d)
                description_path = d
            else:
                continue
        for d in item:
            name, data_type = os.path.splitext(d)
            if data_type == '.png':                                 # what about other formats?
                attach_path = d
            else: continue
            ok = check_image_reference(description_path, attach_path)
            if not ok:
                report_creator.add_data(description_path, attach_path)
        sub_reports.append(description_path)
    for i in range(len(sub_reports) - 1):
            with open(sub_reports[i+1], 'r') as text2:
                description2 = text2.read()
            with open(sub_reports[0], 'r') as text1:
                description1 = text1.read()
                description1 = str(description1) + '\n \n \n' + str(description2)
            with open(sub_reports[0], 'w') as text1:
                text1.write(description1)
    report_creator.convert(sub_reports[0])
    return


def collect_data(app, generator):
    files_catalog = dict()
    date = str(datetime.datetime.now().replace(second=0, microsecond=0))
    # date = str(datetime.date.today())
    report_dir = os.path.join(app['TMP_PATH'], date)    # other name?
    collector = generator.ReportGeneratorCollector(app['TMP_PATH'], report_dir)
    data = object_get_int(app)
    # print(data)
    for i, container in enumerate(data):
        sub_dir = os.path.join(app['TMP_PATH'], report_dir, 'item{}'.format(i))
        files_catalog[sub_dir] = list()
        if not os.path.isdir(sub_dir):
            os.mkdir(sub_dir)

        for d in container['data']:
            src_path = os.path.join(app['DB_DATA_PATH'], d['data-id'], 'blob.bin')

            if 'type' not in d:
                head, tail = os.path.split(d['name'])
                name, data_type = os.path.splitext(tail)
                if data_type == '.png':
                    dst_path = os.path.join(sub_dir, '{}.png'.format(name))
                elif data_type == '.pcap':
                    dst_path = os.path.join(sub_dir, 'trace.pcap')
                else:
                    print('type not supported')                                 # error handling, more types?

                with open(src_path, 'rb') as file:
                    data = file.read()
                    #data = zlib.decompress(data)
                    data += b'==='                                              # arrange that correctly!
                    decoded = hippod.hasher.decode_base64_data(data)
                with open(dst_path, 'wb') as file:
                    file.write(decoded)
                collector.store_file(src_path, dst_path)

            else:
                dst_path = os.path.join(sub_dir, 'description.md')
                collector.store_file(src_path, dst_path)
            files_catalog[sub_dir].append(dst_path)
    return True, files_catalog, date


def trigger_report(app):
    obj_path = os.path.join(app["DB_ROOT_PATH"], 'tmp')
    app['TMP_PATH'] = obj_path
    if not os.path.isdir(obj_path):
        os.mkdir(obj_path)
    generator = hippod.report_generator.ReportGenerator()
    ok, collected_data, date = collect_data(app, generator)
    if not ok:
        msg = "cannot find any data by given filter"
        raise ApiError(msg)
    return create_report(app, generator, collected_data, date)


def handle(request):
    if request.method != "GET" and request.method != "POST":
        msg = "Internal Error...request method: {} is not allowed".format(request.method)
        raise hippod.error_object.ApiError(msg)
    app = request.app
    #report_filter = request.match_info['filter']
                                        # reverse info in filter also maybe?
    try:
        start = time.clock()
        data = trigger_report(app)      # filter?
        end = time.clock()
    except ApiError as e:
        return e.transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()