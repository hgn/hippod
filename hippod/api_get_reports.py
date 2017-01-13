import os
import time
import aiohttp
import mimetypes

import hippod.ex3000
import hippod.error_object

def get_reports(app):
    report_list = list()
    reports_path = app['REPORT_PATH']
    # dir_list = os.listdir(reports_path)
    mtime = lambda f: os.stat(os.path.join(reports_path, f)).st_mtime
    dir_list = list(sorted(os.listdir(reports_path), key=mtime, reverse=True))
    for file in dir_list:
        report = dict()
        report_file_path = os.path.join(reports_path, file)
        report['name'] = file
        report['size'] = "{} KB".format(os.path.getsize(report_file_path)>>10)
        report_list.append(report)
    return report_list


def get_concrete_report(app, report_name):
    reports_path = app['REPORT_PATH']
    report_path = os.path.join(reports_path, report_name)
    mime_type, enconding = mimetypes.guess_type(report_name)
    with open(report_path, 'rb') as file:
        data = file.read()
        return mime_type, data


def handle(request):
    if request.method != "GET":
        msg = "Internal Error...request method: {} is not allowed".format(request.method)
        raise ApiError(msg)
    app = request.app
    try:
        start = time.clock()
        data = get_reports(app)
        end = time.clock()
    except ApiError as e:
        return e.transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    o.http_code(200)
    return o.transform()

def handle_concrete(request):
    if request.method != "GET":
        msg = "Internal Error...request method: {} is not allowed".format(request.method)
        raise ApiError(msg)
    app = request.app
    report_name = request.match_info['report_name']

    try:
        start = time.clock()
        mime_type, data = get_concrete_report(app, report_name)
        end = time.clock()
    except hippod.error_object.ApiError as e:
        return e.transform()
    # data = str(data)
    return aiohttp.web.Response(body=data, content_type=mime_type)