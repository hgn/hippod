import os
import requests
import asyncio
import functools
import logging
import json

import hippod.mime_data_db
import hippod.hasher


log = logging.getLogger()


def exchange_entry(app, sha, data, source_path, source_type):
    path = os.path.join(source_path)
    f_format = data['mime-type'].split('-')[-1]
    if 'name' not in data or data['name'] is None:
        entry = dict()
        entry['data-id'] = sha
        entry['type'] = 'snippet'
        entry['name'] = 'snippet-image-{}.{}'.format(sha, f_format)
    else:
        data['name'] = '{}.{}'.format(data['name'],f_format)
        entry = dict()
        entry['data-id'] = sha
        entry['type'] = 'snippet'
        entry['name'] = data['name']
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
    if s_type == 'python':
        snippet_tmp_path = os.path.join('/tmp', 'tmp{}.py'.format(sha))
    data_decoded = hippod.hasher.decode_base64_data(data)
    data_decoded = data_decoded.decode('utf-8')
    with open(snippet_tmp_path, 'w') as file:
        file.write(data_decoded)
    return snippet_tmp_path


def execute_snippet(app, sha, data, source_path, source_type):
    snippet_db = app['DB_SNIPPET_PATH']
    mime_type = data['mime-type']
    mime_list = mime_type.split('-')

    # get all libary requirements
    lib_list = list()
    for i in range(3, len(mime_list)-1):
        lib_list.append(mime_list[i])

    snippet_db_path = os.path.join(snippet_db, sha)
    # python specific installation of pakets?
    # os.system('python3')
    # for lib in lib_list:
    #   os.system('apt-get install {}'.format(lib))

    s_type = mime_type.split('-')[2]
    if s_type == 'python':
        snippet_tmp_path = os.path.join('/tmp', 'tmp{}.py'.format(sha))
    exec_code = os.system('python3 {} {}'.format(snippet_tmp_path, snippet_db_path))
    if exec_code == 0:
        exchange_entry(app, sha, data, source_path, source_type)
    else:
        # FIXME: handle unexecutable code
        log.error('Snippet file {} is not executable'.format(snippet_path))
        pass


def register_snippet(app, data, sha, source_path, source_type):
    preserve_data = data.copy()
    mime_type = data['mime-type']
    data_content = data['data']

    snippet_tmp_path = save_snippet(app, mime_type, sha, data_content)

    loop = asyncio.get_event_loop()
    loop.call_soon(functools.partial(execute_snippet, app, sha, preserve_data, source_path, source_type))
