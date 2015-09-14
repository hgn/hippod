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
rt_fail = {
        "code": 400,
        "text": "foo bar message"
}

rt_success = {
        "code": 200,
        "id"  : "id",
}



@app.route('/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': "foo"})

def create_container_data_merge_issue(sha_sum, obj):
    d = dict()
    d['object-id'] = sha_sum
    d['object'] = obj
    d['date-added'] = datetime.datetime.now().isoformat('T') # ISO 8601 format
    d['object-achievements'] = []
    return json.dumps(d, sort_keys=True,indent=4, separators=(',', ': '))

def post_object_issue_db_save(sha_sum, obj):
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
        cd = create_container_data_merge_issue(sha_sum, obj)
        fd = open(file_path, 'w')
        fd.write(cd)
        fd.close()

    return True

@app.route('/api/v1/object-issue', methods=['POST'])
def post_object_issues():
    data = request.get_json(force=True)
    (ret, sha1) = object_hasher.check_sum_object_issue(data)
    if ret == False:
        r = dict()
        r['code'] = 400
        r['reason'] = 'Invalid data sent to us'
        return jsonify(r), 400

    ret = post_object_issue_db_save(sha1, data)
    app.logger.warning("%s" % (ret))

    # great, return success and sha1 (the client can
    # check that he would calculate the same one
    rt_success['code'] = 200
    rt_success['id']   = sha1
    return jsonify(rt_success)
