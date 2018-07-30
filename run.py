#!/usr/bin/python3
# coding: utf-8

import os
import sys
import datetime
import json
import argparse
import addict
import logging
import asyncio
import time

from aiohttp import web

from hippod import api_ping
from hippod import api_resources
from hippod import api_achievement_get
from hippod import api_users
from hippod import api_object_post
from hippod import api_object_get
from hippod import api_object_get_detail
from hippod import api_object_get_full
from hippod import api_data_get
from hippod import hippod_login
from hippod import error_handling
from hippod import user_db
from hippod import api_report
from hippod import api_get_reports
from hippod import garbage_handler_container_achievements
from hippod import garbage_handler_mime_db
from hippod import walker
from hippod import cache_categories
from hippod import cache_tags
from hippod import cache_achievements
from hippod import cache_persons
from hippod import api_cache_achievements

APP_VERSION = "002"

# exit codes for shell, failures can later be sub-devided
# if required and shell/user has benefit of this information
EXIT_OK = 0
EXIT_FAILURE = 1


log = logging.getLogger()

login = hippod_login.Login()

# get path for web-app html/js files
ABSDIR = os.path.dirname(os.path.realpath(__file__))
APP_PATH = os.path.join(ABSDIR, 'hippod/app')


# define all required files path
STATIC_FILES = APP_PATH + '/static'
ERROR_HTML = APP_PATH + '/404.html'


# 404 page not found middle ware
ERROR_MIDDLEWARE = error_handling.ErrorMiddleware(ERROR_HTML)


def db_create_initial_statistics(path):
    sys.stderr.write("create statistics db: {}\n".format(path))
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    d = dict()
    d['item-bytes-overtime'] = list()
    d['data-compression'] = dict()
    d_jsonfied = json.dumps(d,
                            sort_keys=True,
                            indent=4, separators=(',', ': '))
    with open(path, "w+") as f:
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

    obj_path = os.path.join(path, 'snippets')
    app['DB_SNIPPET_PATH'] = obj_path
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)

    obj_path = os.path.join(path, 'cache')
    app['DB_CACHE_PATH'] = obj_path
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


def check_report_path(app, path):
    if not os.path.isdir(path):
        log.warning("Create report path: {}".format(path))
        os.makedirs(path)


def set_config_defaults(app):
    app['MAX_REQUEST_SIZE'] = 5000000


def init_aiohttp(conf):
    app = web.Application(middlewares=[ERROR_MIDDLEWARE.error_middleware])

    app["CONF"] = conf

    app["VERSION"] = APP_VERSION
    app["INSTANCE_PATH"] = conf.db.path
    set_config_defaults(app)

    db_path_root = os.path.join(app["INSTANCE_PATH"], "db")
    app["DB_ROOT_PATH"] = db_path_root
    check_db_environmet(app, db_path_root)

    conf_path_root = os.path.join(app["INSTANCE_PATH"], "conf")
    app['CONF_ROOT_PATH'] = conf_path_root
    check_conf_environment(app, conf_path_root)

    report_path = os.path.join(app["INSTANCE_PATH"], "reports")
    app['REPORT_PATH'] = report_path
    check_report_path(app, report_path)

    user_db_path = os.path.join(conf_path_root, "user.db")
    print("the user db path", user_db_path)
    ldap_db_path = os.path.join(conf_path_root, "ldap.db")
    app["USER_DB"] = user_db.UserDB(conf, user_db_path, ldap_db_path)

    return app


def setup_routes(app, conf):
    app.router.add_route('*',
                         '/api/v1/achievement/{sha_major}/{sha_minor}/{achievement_id}',
                         api_achievement_get.handle)
    app.router.add_route('*',
                         '/api/v1/object/{sha_major}/{sha_minor}',
                         api_object_get_full.handle)
    app.router.add_route('*',
                         '/api/v1/data/{sha_sum}',
                         api_data_get.handle)
    app.router.add_route('*',
                         '/api/v1/data-snippet/{sha_sum}',
                         api_data_get.handle_snippet)
    app.router.add_route('POST',
                         '/api/v1/report',
                         api_report.handle)
    app.router.add_route('GET',
                         '/api/v1/get-reports/{report_name}',
                         api_get_reports.handle_concrete)
    app.router.add_route('GET',
                         '/api/v1/get-reports',
                         api_get_reports.handle)
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
    app.router.add_route('GET',
                         '/api/v1/cache/achievements',
                         api_cache_achievements.handle)
    # app.router.add_route('*',
    #                     '/api/v1/users',
    #                     api_users.handle)

    # static route
    app.router.add_static('/static', STATIC_FILES)

    # web-app routes
    app.router.add_routes([web.get('/log', login.login_page),
                           web.post('/login', login.login_required),
                           web.get('/', login.index),
                           web.get('/error', login.server_error),
                           web.get('/redirect', login.redirect_page)])


def gh_container_achievements_daily(app):
    start_time = time.time()
    log.info("  Exectute Garbage Collector for Achievements")
    garb_handler_ca = garbage_handler_container_achievements.GHContainerAchievements()
    garb_handler_ca.handle_garbage(app)
    end_time = time.time()
    log.info("    Excuted in {:0.2f} seconds".format(end_time - start_time))


def gh_mime_data_daily(app):
    start_time = time.time()
    log.info("  Exectute Garbage Collector for MimeDB")
    garb_handler_md = garbage_handler_mime_db.GHMimeData()
    garb_handler_md.remove(app)
    end_time = time.time()
    log.info("    Excuted in {:0.2f} seconds".format(end_time - start_time))


def cache_update_daily(app):
    if walker.Walker.db_empty(app):
        return

    achievements_no = 0
    frequency = 'daily'
    cache_person = cache_persons.Cache(app, frequency)
    cache_tag = cache_tags.Cache(app, frequency)
    cache_category = cache_categories.Cache(app, frequency)
    cache_achievement = cache_achievements.Cache(app, frequency)

    for achievement in walker.Walker.get_achievements(app, False):
        cache_tag.update(achievement)
        cache_category.update(achievement)
        cache_achievement.update(achievement)
        achievements_no += 1

    cache_person.update()

    cache_person.write_cache_file()
    cache_tag.write_cache_file()
    cache_category.write_cache_file()
    cache_achievement.write_cache_file()
    cache_achievement.order_for_sunburn()

    log.info("  Processed {} achievements".format(achievements_no))


def timeout_daily(app):
    log.info("Execute daily execution handler")
    start_time = time.time()
    gh_container_achievements_daily(app)
    gh_mime_data_daily(app)
    cache_update_daily(app)
    end_time = time.time()
    log.info("  Excuted in {:0.2f} seconds".format(end_time - start_time))


def seconds_to_midnight():
    now = datetime.datetime.now()
    deltatime = datetime.timedelta(days=1)
    tomorrow = datetime.datetime.replace(now + deltatime, hour=0, minute=0, second=0)
    seconds = (tomorrow - now).seconds
    if seconds < 60: return 60.0 # sanity checks
    if seconds > 60 * 60 * 24: return 60.0 * 60 * 24
    return seconds


def register_timeout_handler_daily(app):
    loop = asyncio.get_event_loop()
    midnight_sec = seconds_to_midnight()
    call_time = loop.time() + midnight_sec
    msg = "Register daily timeout [scheduled in {} seconds]"
    log.warning(msg.format(midnight_sec))
    loop.call_at(call_time, register_timeout_handler_daily, app)
    timeout_daily(app)

def register_timeout_handler(app):
    # for now just a daily handler, called at midnight.
    # later we can add additional handlers for weekly, hourly,
    # ...
    register_timeout_handler_daily(app)


def main(conf):
    app = init_aiohttp(conf)
    conf_check_report(app, conf)
    setup_routes(app, conf)
    register_timeout_handler(app)
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
    if "host" not in conf.common:
        conf.common.host = '0.0.0.0'
    if "port" not in conf.common:
        conf.common.port = '8080'

    if "path" not in conf.db:
        sys.stderr.write("No path configured for database, but required! Please specify "
                         "a path in db section\n")
        sys.exit(EXIT_FAILURE)


def init_logging(conf):
    log_level_conf = "warning"
    if conf.common.logging:
        log_level_conf = conf.common.logging
    numeric_level = getattr(logging, log_level_conf.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(numeric_level))
    logging.basicConfig(level=numeric_level, format='%(message)s')
    log.error("Log level configuration: {}".format(log_level_conf))


def conf_check_report(app, conf):
    assert(conf.reports.driver == "pandoc")
    if conf.reports.export_formats:
        if not isinstance(conf.reports.export_formats, list):
            raise ValueError('Configuration error, export_formats must be array')
        if len(conf.reports.export_formats) != 1:
            raise ValueError('Configuration error, export_format must be PDF, nothing else')
        if conf.reports.export_formats[0].upper() != "PDF":
            raise ValueError('Configuration error, export_format must be PDF')
    if conf.reports.pandoc_pdf_tex_template_path:
        path = conf.reports.pandoc_pdf_tex_template_path
        if not os.path.isfile(path):
            raise ValueError('Pandoc template file not available: {}'.format(path))
        app["REPORT-PDF-TEMPLATE"] = path

    app["REPORT-TITLE"] = "Test Report"
    if not conf.reports.title:
        app["REPORT-TITLE"] = conf.reports.title


def conf_init():
    args = parse_args()
    conf = load_configuration_file(args)
    init_logging(conf)
    return conf


if __name__ == '__main__':
    sys.stdout.write("HippoD - 2015, 2016\n")
    conf = conf_init()
    main(conf)
