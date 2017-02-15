import json
import os
import datetime
import inspect
import time
import zlib
import sys

import aiohttp



def read_cont_obj_by_id(app, sha_major):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        'container.db')
    if not os.path.isfile(path):
        return [False, None]
    with open(path) as data_file:
        data = json.load(data_file)
    return [True, data]

def read_subcont_obj_by_id(app, sha_major, sha_minor):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        sha_minor,
                        'subcontainer.db')
    if not os.path.isfile(path):
        return [False, None]
    with open(path) as data_file:
        data = json.load(data_file)
    return [True, data]


def get_achievement_data_by_sha_id(app, sha_major, sha_minor, id_no):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        sha_minor,
                        'achievements',
                        '{}.db'.format(id_no))
    if not os.path.isfile(path):
        return None
    with open(path) as data_file:
        data = json.load(data_file)
    return data


def get_attachment_data_by_sha_id(app, sha_major, id_no):
    path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        'attachments',
                        '{}.db'.format(id_no))
    if not os.path.isfile(path):
        return None
    with open(path) as data_file:
        data = json.load(data_file)
    return data


def object_index_read(app):
    db_path = app['DB_OBJECT_PATH']
    object_index_db_path = os.path.join(db_path, "object-index.db")
    if not os.path.isfile(object_index_db_path):
        return None
    with open(object_index_db_path) as data_file:
        return json.load(data_file)
