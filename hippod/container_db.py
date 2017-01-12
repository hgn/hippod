import logging

import hippod.api_shared

log = logging.getLogger()


def check_subcontainer(app, sha_major, sha_minor, sc_content):
    ref_list = list()
    achievements = sc_content['achievements']
    for achiev in achievements:
        id_no = str(achiev['id'])
        achievement = hippod.api_shared.get_achievement_data_by_sha_id(app, sha_major, sha_minor, id_no)
        if 'data' not in achievement:
            continue
        for data in achievement['data']:
            ref_list.append(data['data-id'])
    if 'data' not in sc_content['object-item']:
        return ref_list
    data_list = sc_content['object-item']['data']
    for data in data_list:
        ref_list.append(data['data-id'])
    return ref_list


def check_container(app, cont_obj):
    ref_list = list()
    sha_major = cont_obj['object-item-id']
    sc_list = cont_obj['subcontainer-list']
    for sc in sc_list:
        sha_minor = sc['sha-minor']
        ok, sc_content = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sha_minor)
        if not ok:
            log.error("cannot read container {} by sha, ignore for now".format(cont['object-item-id']))
            continue
        ref_subcontainer_list = check_subcontainer(app, sha_major, sha_minor, sc_content)
        for reference in ref_subcontainer_list:
            ref_list.append(reference)
    return ref_list


def all_referenced_mime_ids(app):
    reference_list = list()
    object_index_data = hippod.api_shared.object_index_read(app)
    if not object_index_data:
        return []
    for container in object_index_data:
        ok, cont_obj = hippod.api_shared.read_cont_obj_by_id(app, container['object-item-id'])
        if not ok:
            log.error("cannot read container {} by sha, ignore for now".format(cont['object-item-id']))
            continue
        ref_container_list = check_container(app, cont_obj)
        for reference in ref_container_list:
            reference_list.append(reference)
    return reference_list