import sys
import os
import requests
import asyncio
import functools
import logging
import json
import base64

import hippod.mime_data_db
import hippod.hasher


log = logging.getLogger()


def get_size(snippet_db_path):
    image_path = os.path.join(snippet_db_path)
    with open(image_path, 'rb') as f:
        content = f.read()
        data = base64.b64encode(content)
        bin_data = base64.b64decode(data)
        size_real = len(bin_data)
    return size_real


def add_entry_in_container_achievement_meta(app, sha, data, source_path, source_type, snippet_db_path):
    path = os.path.join(source_path)
    f_format = data['mime-type'].split('-')[-1]
    if 'name' not in data or data['name'] is None:
        entry = dict()
        entry['data-id'] = sha
        entry['type'] = 'snippet'
        entry['name'] = 'snippet-image-{}.{}'.format(sha, f_format)
        entry['size-real'] = get_size(snippet_db_path)
    else:
        if '.' in data['name']:
            data['name'] = data['name'].split('.')[0]
        data['name'] = '{}.{}'.format(data['name'],f_format)
        entry = dict()
        entry['data-id'] = sha
        entry['type'] = 'snippet'
        entry['name'] = data['name']
        entry['size-real'] = get_size(snippet_db_path)
    with open(path, 'r') as f:
        content = json.load(f)
        if source_type == 'subcontainer':
            content['object-item']['data'].append(entry)
        elif source_type == 'achievement':
            content['data'].append(entry)
    with open(path, 'w') as f:
        new_content = json.dumps(content, sort_keys=True, indent=4, separators=(',', ': '))
        f.write(new_content)


def save_snippet(app, mime_type, sha, data):
    s_type = mime_type.split('-')[2]
    snippet_tmp_path = os.path.join('/tmp', 'tmp{}.py'.format(sha))
    data_decoded = hippod.hasher.decode_base64_data(data)
    data_decoded = data_decoded.decode('utf-8')
    with open(snippet_tmp_path, 'w') as file:
        file.write(data_decoded)
    return snippet_tmp_path


def execute_snippet(app, sha, data, source_path, source_type, snippet_tmp_path):
    snippet_db = app['DB_SNIPPET_PATH']
    mime_type = data['mime-type']
    mime_list = mime_type.split('-')
    image_format = mime_list[-1]
    # get all libary requirements

    snippet_db_path = os.path.join(snippet_db, '{}.{}'.format(sha, image_format))

    s_type = mime_type.split('-')[2]
    try:
        exec_code = os.system('python3 {} {}'.format(snippet_tmp_path, snippet_db_path))
        if exec_code == 0:
            add_entry_in_container_achievement_meta(app, sha, data, source_path,
                                                    source_type, snippet_db_path)
        else:
            log.error('Snippet file {} is not executable'.format(snippet_db_path))
    finally:
        os.remove(snippet_tmp_path)


def register_snippet(app, data, sha, source_path, source_type):
    preserve_data = data.copy()
    mime_type = data['mime-type']
    data_content = data['data']

    snippet_tmp_path = save_snippet(app, mime_type, sha, data_content)
    loop = asyncio.get_event_loop()
    loop.call_soon(functools.partial(execute_snippet, app, sha, preserve_data,
                                     source_path, source_type, snippet_tmp_path))
