import json
import os
import datetime
import inspect
import time
import zlib
import sys

import hippod.api_object_post
import hippod.users

def create_container_data_merge_issue_new(app, sha_major, sha_minor, object_item):
    date = datetime.datetime.now().isoformat('T') # ISO 8601 format
    d = dict()
    d['title'] = object_item['object-item']['title']
    d['version'] = object_item['object-item']['version']
    d['categories'] = object_item['object-item']['categories']
    d['object-item-id'] = sha_major
    d['date-added'] = date
    d['attachments'] = []
    d['attachment-last-modified'] = date
    d['subcontainer-list'] = list()
    sub_cntr_init = dict()
    sub_cntr_init['sha-minor'] = sha_minor
    user_data = hippod.users.get(app, object_item['submitter'], 'submitter')
    sub_cntr_init['submitter'] = user_data[0]['fullname']
    sub_cntr_init['date-added'] = date
    d['subcontainer-list'].append(sub_cntr_init)

    hippod.api_object_post.add_initial_severity_level(d)

    # the object is a little bit special. We iterate over the
    # data section as always and compress or not compress
    # data and save it in a different path

    return json.dumps(d, sort_keys=True,indent=4, separators=(',', ': '))


# init token reflects whether first subcontainer created or not
def create_subcontainer_data_merge_issue_new(app, sha_major, sha_minor, object_item):
    obj_path = os.path.join(app['DB_OBJECT_PATH'])
    path = os.path.join(obj_path, sha_major[0:2], sha_major, sha_minor, 'subcontainer.db')
    date = datetime.datetime.now().isoformat('T')
    obj_root_path = app['DB_OBJECT_PATH']
    cntr_path = os.path.join(obj_root_path, sha_major[0:2], sha_major, 'container.db')
    d_sub = dict()
    user_data = hippod.users.get(app, object_item['submitter'], 'submitter')
    d_sub['submitter'] = user_data[0]['fullname']
    d_sub['achievements'] = []
    d_sub['object-item'] = dict()
    if 'data' in object_item['object-item']:
        d_sub['object-item']['data'] = object_item['object-item']['data']
        # for i, v in enumerate(d_sub['object-item']['data']):
        #     if 'size-real' in d_sub['object-item']['data'][i]:
        #         del d_sub['object-item']['data'][i]['size-real']
    hippod.mime_data_db.save_object_item_data_list(app, object_item['object-item'], path, 'subcontainer')
    
    return json.dumps(d_sub, sort_keys=True,indent=4, separators=(',', ': '))


def save_new_object_container(app, sha_major, sha_minor, object_item):
    obj_root_path = app['DB_OBJECT_PATH']
    obj_root_pre_path = os.path.join(obj_root_path, sha_major[0:2])
    if not os.path.isdir(obj_root_pre_path):
        os.makedirs(obj_root_pre_path)
    obj_root_major_path = os.path.join(obj_root_pre_path, sha_major)
    if not os.path.isdir(obj_root_major_path):
        os.makedirs(obj_root_major_path)
    obj_minor_path = os.path.join(obj_root_major_path, sha_minor)
    if not os.path.isdir(obj_minor_path):
        os.makedirs(obj_minor_path)
    achie_path = os.path.join(obj_minor_path, 'achievements')
    if not os.path.isdir(achie_path):
        os.makedirs(achie_path)
    attachie_path = os.path.join(obj_root_major_path, 'attachments')
    if not os.path.isdir(attachie_path):
        os.makedirs(attachie_path)

    file_path = os.path.join(obj_root_major_path, 'container.db')
    minor_file_path = os.path.join(obj_minor_path, 'subcontainer.db')

    if os.path.isfile(file_path) or os.path.isfile(minor_file_path):
        msg = "internal error: {}".format(inspect.currentframe())
        raise ApiError(msg)
    cd = create_container_data_merge_issue_new(app, sha_major, sha_minor, object_item)
    with open(file_path, 'w') as fd:
        fd.write(cd)
    cd_minor = create_subcontainer_data_merge_issue_new(app, sha_major, sha_minor, object_item)
    with open(minor_file_path, 'w') as fd_minor:
    	fd_minor.write(cd_minor)


def save_new_object_minor_container(app, sha_major, sha_minor, object_item):
    obj_root_path = app['DB_OBJECT_PATH']
    obj_minor_path = os.path.join(obj_root_path, sha_major[0:2], sha_major, sha_minor)
    if not os.path.isdir(obj_minor_path):
        os.makedirs(obj_minor_path)
    achie_path = os.path.join(obj_minor_path, 'achievements')
    if not os.path.isdir(achie_path):
        os.makedirs(achie_path)

    minor_file_path = os.path.join(obj_minor_path, 'subcontainer.db')

    if os.path.isfile(minor_file_path):
        msg = "internal error: {}".format(inspect.currentframe())
        raise ApiError(msg)
    cd_minor = create_subcontainer_data_merge_issue_new(app, sha_major, sha_minor, object_item)
    with open(minor_file_path, 'w') as fd_minor:
    	fd_minor.write(cd_minor)