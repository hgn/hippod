import json
import os
import datetime
import inspect
import time
import zlib
import sys

import aiohttp



def read_cont_obj_by_id(app, sha_sum):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_sum[0:2],
                        sha_sum,
                        'container.db')
    if not os.path.isfile(path):
        return [False, None]
    with open(path) as data_file:
        data = json.load(data_file)
    return [True, data]


def get_achievement_data_by_sha_id(app, sha, id_no):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'achievements',
                        '{}.db'.format(id_no))
    with open(path) as data_file:
        data = json.load(data_file)
    return data


def get_attachment_data_by_sha_id(app, sha, id_no):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'attachments',
                        '{}.db'.format(id_no))
    with open(path) as data_file:
        data = json.load(data_file)
    return data
