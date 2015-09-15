#!/usr/bin/python
# coding: utf-8

import object_hasher
import json
import os
import datetime

from contestcolld import app

from flask import jsonify
from flask import request

# common return type - always incluced in every
# returned data set
xobject_ret = {
        "code": 400,
        "id"  : 'id',
        "text": "foo bar message"
}

rt_success = {
        "code": 200,
        "id"  : "id",
}



@app.route('/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': "foo"})


def add_attachment_to_object_container_object(container_obj, attachment_obj):
    pass


def check_attachment(attachment):
    if type(attachment) is not list:
        return False
    return True


def create_container_data_merge_issue_new(sha_sum, xobj):
    date = datetime.datetime.now().isoformat('T') # ISO 8601 format
    d = dict()
    d['object-id'] = sha_sum
    d['object'] = obj['object']
    d['date-added'] = date
    d['attachment'] = { }
    d['attachment-last-modified'] = date
    d['achievements'] = []
    d['achievements-last-added'] = date

    if 'attachment' in xobj and len(xobj['attachment']) > 0:
        if not check_attachment(xobj['attachment']):
            return [False, None]
        d['attachment'] = xobj['attachment']


    return [True, json.dumps(d, sort_keys=True,indent=4, separators=(',', ': '))]


def post_object_issue_db_save_new(sha_sum, xobj):
    obj_root_path = app.config['DB_OBJECT_PATH']
    obj_root_pre_path = os.path.join(obj_root_path, sha_sum[0:2])
    if not os.path.isdir(obj_root_pre_path):
        os.makedirs(obj_root_pre_path)
    obj_root_full_path = os.path.join(obj_root_pre_path, sha_sum)
    if not os.path.isdir(obj_root_full_path):
        os.makedirs(obj_root_full_path)

    file_path = os.path.join(obj_root_full_path, 'container.db')
    if os.path.isfile(file_path):
        # file already available, we normally should check the sha1
        #return True
        pass
    else:
        (ret, cd) = create_container_data_merge_issue_new(sha_sum, xobj)
        if ret == False:
            return False
        fd = open(file_path, 'w')
        fd.write(cd)
        fd.close()

    return True


def is_obj_already_in_db(sha_sum):
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha_sum[0:2],
                        sha_sum,
                        'container.db')
    if os.path.isfile(path):
        return [True, path]
    return [False, None]


def process_post_object_issues(xobj):
    ret = object_hasher.check_xobject(xobj)
    if ret == False:
        app.logger.warning("%s" % ("check xobject failed"))
        return [False, None]

    if not 'object-id' in xobj:
        (ret, sha1) = object_hasher.check_sum_object_issue(xobj)
        if ret == False:
            app.logger.warning("%s" % ("internal format failed"))
            return [False, None]
    else:
        sha1 = xobj['object-id']
        app.logger.warning("sha1: {}".format(sha1))

    (ret, path) = is_obj_already_in_db(sha1)
    if not ret:
        ret = post_object_issue_db_save_new(sha1, xobj)
        if not ret:
            app.logger.warning("%s" % ("save failed"))
            return [False, None]
        app.logger.warning("%s" % (ret))
    else:
        app.logger.warning("{} already in DB".format(sha1))
        pass

    # great, return success and sha1 (the client can
    # check that he would calculate the same one
    return [True, sha1]


@app.route('/api/v1/object-issue', methods=['POST'])
def post_object_issues():
    xobj = request.get_json(force=False)
    (ret, obj_id) = process_post_object_issues(xobj)
    if ret == False:
        r = dict()
        r['code'] = 400
        r['reason'] = 'Invalid data sent to us'
        return jsonify(r), 400
    else:
        rt_success['code'] = 200
        rt_success['id']   = obj_id
        return jsonify(rt_success)
