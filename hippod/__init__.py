from flask import Flask
from flask import jsonify

import os
import sys
import datetime
import json
import random

APP_VERSION = "001"

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


def check_db_environmet(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    obj_path = os.path.join(path, 'objects')
    app.config['DB_OBJECT_PATH'] = obj_path
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)

    obj_path = os.path.join(path, 'data')
    app.config['DB_DATA_PATH'] = obj_path
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)

    obj_path = os.path.join(path, 'statistics.db')
    app.config['DB_STATISTICS_FILEPATH'] = obj_path
    if not os.path.isfile(obj_path):
        db_create_initial_statistics(obj_path)


def check_conf_environmet(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    obj_path = os.path.join(path, 'user.conf')
    app.config['CONF_USER_FILEPATH'] = obj_path
    if not os.path.isfile(obj_path):
        conf_create_user_statistics(obj_path)


def set_config_defaults():
    app.config['MAX_REQUEST_SIZE'] = 5000000


app = Flask(__name__, static_folder='app', static_url_path='')

app.config['VERSION'] = APP_VERSION
set_config_defaults()
app.config.from_pyfile('testcolld.cfg', silent=False)
app.config.from_envvar('APP_CONFIG_FILE', silent=True)

# log to stderr
import logging
from logging import StreamHandler
del app.logger.handlers[:]
file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

db_path_root = os.path.join(app.instance_path, "db")
app.config['DB_ROOT_PATH'] = db_path_root
check_db_environmet(db_path_root)

conf_path_root = os.path.join(app.instance_path, "conf")
app.config['CONF_ROOT_PATH'] = conf_path_root
check_conf_environmet(conf_path_root)

# The views modules that contain the application's routes are imported here
# Importing views modules MUST BE in the end of the file to avoid problems
# related to circular imports http://flask.pocoo.org/docs/patterns/packages
import hippod.gui_app

import hippod.api_object_post
import hippod.api_object_get
import hippod.api_object_get_full
import hippod.api_resources
import hippod.api_data_get
import hippod.api_users
import hippod.api_ping
