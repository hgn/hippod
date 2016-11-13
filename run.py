#!/usr/bin/python3
# coding: utf-8

import os
import sys
import datetime
import json
import random
import argparse
import addict

from aiohttp import web

from hippod import aiohttp_index

from hippod import api_ping
from hippod import api_resources
from hippod import api_achievement_get
from hippod import api_users
from hippod import api_object_post
from hippod import api_object_get
from hippod import api_object_get_full
from hippod import api_data_get

APP_VERSION = "002"

# exit codes for shell, failures can later be sub-devided
# if required and shell/user has benefit of this information
EXIT_OK      = 0
EXIT_FAILURE = 1


def db_create_initial_statistics(path):
    sys.stderr.write("create statistics db: {}\n".format(path))
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    d = dict()
    d['item-bytes-overtime'] = list()
    d['data-compression'] = dict()
    d_jsonfied =  json.dumps(d, sort_keys=True,indent=4, separators=(',', ': '))
    with open(path,"w+") as f:
        f.write(d_jsonfied)

def conf_create_user_statistics(path):
    sys.stderr.write("create user db: {}\n".format(path))
    d = list()
    entry = dict()
    entry['username'] = "john_doe"
    entry['fullname'] = "John Doe"
    entry['email']    = "john@example.coa"
    entry['color']    = '#{:02X}'.format(random.randint(0, 0xFFFFFF))
    d.append(entry)
    d_jsonfied =  json.dumps(d, sort_keys=True,indent=4, separators=(',', ': '))
    with open(path,"w+") as f:
        f.write(d_jsonfied)

def check_db_environmet(app, path):
    if not os.path.isdir(path):
        os.makedirs(path)
    obj_path = os.path.join(path, 'objects')
    app['DB_OBJECT_PATH'] = obj_path
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)

    obj_path = os.path.join(path, 'data')
    app['DB_DATA_PATH'] = obj_path
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)

    obj_path = os.path.join(path, 'statistics.db')
    app['DB_STATISTICS_FILEPATH'] = obj_path
    if not os.path.isfile(obj_path):
        db_create_initial_statistics(obj_path)

def check_conf_environmet(app, path):
    if not os.path.isdir(path):
        os.makedirs(path)
    obj_path = os.path.join(path, 'user.conf')
    app['CONF_USER_FILEPATH'] = obj_path
    if not os.path.isfile(obj_path):
        conf_create_user_statistics(obj_path)

def set_config_defaults(app):
    app['MAX_REQUEST_SIZE'] = 5000000



# building instance of Web Application
# IndexMiddleware from aiohttp_index helps to serve static files, e.g. index.html

app = web.Application(middlewares=[aiohttp_index.IndexMiddleware()])

app["VERSION"] = APP_VERSION
app["instance_path"] = "instance"
set_config_defaults(app)


db_path_root = os.path.join(app["instance_path"], "db")
app["DB_ROOT_PATH"] = db_path_root
check_db_environmet(app, db_path_root)

conf_path_root = os.path.join(app["instance_path"], "conf")
app['CONF_ROOT_PATH'] = conf_path_root
check_conf_environmet(app, conf_path_root)



def main(conf): 
    app.router.add_route('*',
                        '/api/v1/achievement/{sha_id}/{achievement_id}',
                        api_achievement_get.handle)
    app.router.add_route('*',
                        '/api/v1/object/{sha_sum}',
                        api_object_get_full.handle)
    app.router.add_route('*',
                        '/api/v1/data/{sha_id}',
                        api_data_get.handle)
    app.router.add_route('GET',
                        '/api/v1/ping',
                        api_ping.handle)
    app.router.add_route('GET',
                        '/api/v1.0/resources',
                        api_resources.handle)
    app.router.add_route('*',
                        '/api/v1/objects',
                        api_object_get.handle)
    app.router.add_route('POST',
                        '/api/v1/object',
                        api_object_post.handle)
    app.router.add_route('*',
                        '/api/v1/users',
                        api_users.handle)    

    absdir = os.path.dirname(os.path.realpath(__file__))
    app_path = os.path.join(absdir, 'hippod/app')
    app.router.add_static('/', app_path)

    web.run_app(app, host='0.0.0.0', port=8080)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--configuration", help="configuration", type=str, default=None)
    parser.add_argument("-v", "--verbose", help="verbose", action='store_true', default=False)
    args = parser.parse_args()
    if not args.configuration:
        sys.stderr.write("Configuration required, please specify a valid file path, exiting now\n")
        sys.exit(EXIT_FAILURE)
    return args

def load_configuration_file(args):
    with open(args.configuration) as json_data:
        return addict.Dict(json.load(json_data))

def conf_init():
    args = parse_args()
    conf = load_configuration_file(args)
    return conf


if __name__ == '__main__':
    sys.stdout.write("HippoD - 2015, 2016\n")
    conf = conf_init()
    main(conf)
