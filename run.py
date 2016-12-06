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
from hippod import api_object_get_detail
from hippod import api_object_get_full
from hippod import api_data_get
from hippod import user_db

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


def check_conf_environment(app, path):
    if not os.path.isdir(path):
        os.makedirs(path)
    obj_path = os.path.join(path, 'user.conf')
    app['CONF_USER_FILEPATH'] = obj_path



def set_config_defaults(app):
    app['MAX_REQUEST_SIZE'] = 5000000



def init_aiohttp(conf):
    app = web.Application(middlewares=[aiohttp_index.IndexMiddleware()])

    app["VERSION"] = APP_VERSION
    app["instance_path"] = conf.db.path
    set_config_defaults(app)

    db_path_root = os.path.join(app["instance_path"], "db")
    app["DB_ROOT_PATH"] = db_path_root
    check_db_environmet(app, db_path_root)

    conf_path_root = os.path.join(app["instance_path"], "conf")
    app['CONF_ROOT_PATH'] = conf_path_root
    check_conf_environment(app, conf_path_root)

    db_path = os.path.join(conf_path_root, "user.db")
    app["userdb"] = user_db.UserDB(conf, db_path)

    return app


def setup_routes(app, conf):
    app.router.add_route('*',
                        '/api/v1/achievement/{sha_major}/{sha_minor}/{achievement_id}',
                        api_achievement_get.handle)
    app.router.add_route('*',
                        '/api/v1/object/{sha_major}',
                        api_object_get_full.handle)
    app.router.add_route('*',
                        '/api/v1/object/{sha_major}/{sha_minor}',
                        api_object_get_full.handle_minor)
    app.router.add_route('*',
                        '/api/v1/data/{sha_sum}',
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
    app.router.add_route('*',
                        '/api/v1/objects-detail-last',
                        api_object_get_detail.handle)
    app.router.add_route('POST',
                        '/api/v1/object',
                        api_object_post.handle)
    app.router.add_route('*',
                        '/api/v1/users',
                        api_users.handle)    

    absdir = os.path.dirname(os.path.realpath(__file__))
    app_path = os.path.join(absdir, 'hippod/app')
    app.router.add_static('/', app_path)


def main(conf):
    app = init_aiohttp(conf)
    setup_routes(app, conf)
    web.run_app(app, host=conf.common.host, port=conf.common.port)


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

def configuration_check(conf):
    # this function check for variables, if required
    # we should exit here with a proper message. If a
    # configuration knob is not required we set here a
    # proper default
    if not "host" in conf.common:
        conf.common.host = '0.0.0.0'
    if not "port" in conf.common:
        conf.common.port = '8080'

    if not "path" in conf.db:
        sys.stderr.write("No path configured for database, but required! Please specify "
                         "a path in db section\n")
        sys.exit(EXIT_FAILURE)

def conf_init():
    args = parse_args()
    conf = load_configuration_file(args)
    return conf


if __name__ == '__main__':
    sys.stdout.write("HippoD - 2015, 2016\n")
    conf = conf_init()
    main(conf)
