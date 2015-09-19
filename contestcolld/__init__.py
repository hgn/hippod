#!/usr/bin/python
# coding: utf-8

from flask import Flask
import os
import sys


def check_db_environmet(path):
    #sys.stderr.write("relative DB path: {}\n".format(path))
    if not os.path.isdir(path):
        os.makedirs(path)
    obj_path = os.path.join(path, 'objects')
    app.config['DB_OBJECT_PATH'] = obj_path
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)

    obj_path = os.path.join(path, 'data_uncompressed')
    app.config['DB_UNCOMPRESSED_PATH'] = obj_path
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)

    obj_path = os.path.join(path, 'data_compressed')
    app.config['DB_COMPRESSED_PATH'] = obj_path
    if not os.path.isdir(obj_path):
        os.makedirs(obj_path)


app = Flask(__name__, static_folder='assets', static_url_path='')
app.config.from_pyfile('testcolld.cfg', silent=False)
app.config.from_envvar('APP_CONFIG_FILE', silent=True)

db_path_root = os.path.join(app.instance_path, app.config['RELATIVE_DB_PATH'])
app.config['DB_ROOT_PATH'] = db_path_root
check_db_environmet(db_path_root)


# application wide global variables and config parameters must be defined here
# (not in `run.py`) for being able to import them in the beginning of the
# views files but we can perfectly imagine a smarter config procedure
app.config['HELLO_WORLD'] = 'Hello Flask!'

# The views modules that contain the application's routes are imported here
# Importing views modules MUST BE in the end of the file to avoid problems
# related to circular imports http://flask.pocoo.org/docs/patterns/packages
import contestcolld.gui_dashboard
import contestcolld.gui_admin
import contestcolld.gui_items

import contestcolld.api_object
import contestcolld.api_resources
