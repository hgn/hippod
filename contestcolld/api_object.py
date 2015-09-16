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


def check_attachment(attachment):
    if type(attachment) is not dict:
        return False
    return True


def create_container_data_merge_issue_new(sha_sum, xobj):
    date = datetime.datetime.now().isoformat('T') # ISO 8601 format
    d = dict()
    d['object-id'] = sha_sum
    d['object'] = xobj['object']
    d['date-added'] = date
    d['attachment'] = { }
    d['attachment-last-modified'] = date
    d['achievements'] = []

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
    achie_path = os.path.join(obj_root_full_path, 'achievements')
    if not os.path.isdir(achie_path):
        os.makedirs(achie_path)

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


def read_obj_by_id(sha_sum):
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha_sum[0:2],
                        sha_sum,
                        'container.db')
    if not os.path.isfile(path):
        return [False]
    with open(path) as data_file:
        data = json.load(data_file)
    return [True, data]

def write_file(sha, py_object):
    data = json.dumps(py_object, sort_keys=True,indent=4, separators=(',', ': '))
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'container.db')
    fd = open(path, 'w')
    fd.write(data)
    fd.close()

def write_achievement_file(sha, id_no, py_object):
    data = json.dumps(py_object, sort_keys=True,indent=4, separators=(',', ': '))
    path = os.path.join(app.config['DB_OBJECT_PATH'],
                        sha[0:2],
                        sha,
                        'achievements',
                        '{0:04d}.db'.format(id_no))
    fd = open(path, 'w')
    fd.write(data)
    fd.close()


def post_object_update_attachment_achievement(sha1, xobj):
    # ok, the object is in database, we now update the data
    # attachments are updated (overwrite), achievements are
    # added
    rewrite_required = False
    (ret, data) = read_obj_by_id(sha1)
    if not ret:
        app.logger.error("path is not available!")
        return False

    if 'attachment' in xobj:
        if type(xobj['attachment']) is not dict:
                app.logger.error("attachment data MUST be a dict - but isn't")
                return False
        data['attachment'] = xobj['attachment']
        data['attachment-last-modified'] = datetime.datetime.now().isoformat('T')
        rewrite_required = True

    if 'achievements' in xobj:
        if type(xobj['achievements']) is not list:
                app.logger.error("achievements data MUST be a list - but isn't")
                return False
        current_achievements = data["achievements"]
        current_achievements_no = len(current_achievements)
        # add new achievements in same order
        for a in xobj['achievements']:
            new_data = dict()
            new_data['id'] = current_achievements_no
            new_data['date-added'] =  datetime.datetime.now().isoformat('T')
            current_achievements.append(new_data)

            # now we save the achievement in a seperate file
            write_achievement_file(sha1, current_achievements_no, a)
            current_achievements_no += 1

        data["achievements"] = current_achievements
        rewrite_required = True

    if rewrite_required:
        app.logger.error("rewrite object.db file")
        write_file(sha1, data)


    return True


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
        ret = post_object_update_attachment_achievement(sha1, xobj)
        if not ret:
            app.logger.warning("%s" % ("save failed"))
            return [False, None]
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
