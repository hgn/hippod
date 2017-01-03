import os
import datetime
import json
import shutil
import logging

import hippod.api_shared

log = logging.getLogger()


class GarbageHandler(object):

    @staticmethod
    def convert_lifetime(conf_list):
        figure = conf_list[0]
        unit = conf_list[1]
        if unit == "seconds":
            seconds = figure
        elif unit == "minutes":
            seconds = figure * 60
        elif unit == "hours":
            seconds = figure * 3600
        elif unit == "days":
            seconds = figure * 86400
        elif unit == "months":
            seconds = figure * 2592000
        else:
            log.error("incorrect time unit...choose between 'seconds', 'minutes', 'hours', \
                      'days' and 'months'")
        return seconds

    @staticmethod
    def handle_garbage(app):
        conf = app['CONF']
        garbage = GarbageHandler()
        lifetime_default = garbage.convert_lifetime(conf.achievements_validity_lifetime.achievements)
        lifetime_anchored = garbage.convert_lifetime(conf.achievements_validity_lifetime.achievements_anchored)
        collector = GarbageHandler.GarbageHandlerCollect(lifetime_default, lifetime_anchored)
        garbage_list = collector.search(app)
        if garbage_list != None:
            garb_remover = GarbageHandler.GarbageHandlerRemove(garbage_list)
            garb_remover.remove(app)
                

    class GarbageHandlerRemove(object):
        def __init__(self, garbage_list):
            self.garbage_list = garbage_list

        def remove(self, app):
            log.debug("starting remove old and unnecessary files")
            obj_path = app['DB_OBJECT_PATH']
            for garbage in self.garbage_list:
                garbage_path = os.path.join(obj_path, garbage)
                print(garbage_path)
                if os.path.isfile(garbage_path):
                    os.remove(garbage_path)
                elif os.path.isdir(garbage_path):
                    shutil.rmtree(garbage_path)


    class GarbageHandlerCollect(object):
        def __init__(self, lifetime_default, lifetime_anchored):
            self.lifetime_default = lifetime_default
            self.lifetime_anchored = lifetime_anchored

        def search(self, app):
            object_index_data = hippod.api_shared.object_index_read(app)
            if not object_index_data:
                return None
            garbage_list = list()
            for cont in object_index_data:
                ok, cont_obj = hippod.api_shared.read_cont_obj_by_id(app, cont['object-item-id'])
                if not ok:
                    continue    # what if?
                container_garbage = GarbageHandler.GarbageHandlerCollect.check_subcontainer(self, app, cont['object-item-id'], cont_obj)
                for item in container_garbage:
                    garbage_list.append(item)
            return garbage_list


        def get_sec(time):
            time_str = str(time)
            h, m, s = time_str.split(':')
            return float(h)*3600 + float(m)*60 + float(s)


        def correct_subcontainer(app, sha_major, sha_minor, achiev_id):
            path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        sha_minor,
                        'subcontainer.db')
            with open(path) as data_file:
                data = json.load(data_file)
                for i, achiev in enumerate(data['achievements']):
                    if achiev['id'] == achiev_id:
                        del data['achievements'][i]
            with open(path, 'w') as data_file:
                data = json.dumps(data, sort_keys=True,indent=4,
                      separators=(',', ': '))
                data_file.write(data)


        def correct_container(app, sha_major, sha_minor):
            path = os.path.join(app['DB_OBJECT_PATH'],
                        sha_major[0:2],
                        sha_major,
                        'container.db')
            with open(path) as data_file:
                data = json.load(data_file)
                for i, sc in enumerate(data['subcontainer-list']):
                    if sc['sha-minor'] == sha_minor:
                        del data['subcontainer-list'][i]
            with open(path, 'w') as data_file:
                data = json.dumps(data, sort_keys=True,indent=4,
                      separators=(',', ': '))
                data_file.write(data)


        def correct_object_index(app, sha_major):
            path = os.path.join(app['DB_OBJECT_PATH'],
                        'object-index.db')
            with open(path) as data_file:
                data = json.load(data_file)
                for i, d in enumerate(data):
                    if d['object-item-id'] == sha_major:
                        del data[i]
            with open(path, 'w') as data_file:
                data = json.dumps(data, sort_keys=True,indent=4,
                      separators=(',', ': '))
                data_file.write(data)            


        def check_achiev_lifetime(self, app, sha_major, sha_minor, sc_content, sc_list):
            achiev_list = list()
            for achiev in sc_content['achievements']:
                achiev_id = str(achiev['id'])
                date_added = achiev['date-added']
                achievement = hippod.api_shared.get_achievement_data_by_sha_id(app, sha_major, sha_minor, achiev_id)
                date_added = datetime.datetime.strptime(date_added, '%Y-%m-%dT%H:%M:%S.%f')
                diff = datetime.datetime.now() - date_added
                diff = GarbageHandler.GarbageHandlerCollect.get_sec(diff)
                if 'anchor' in achievement and diff > self.lifetime_anchored:
                    path = os.path.join(sha_major[0:2], sha_major, sha_minor, 'achievements', '{}.db'.format(achiev_id))
                    achiev_list.append(path)
                    GarbageHandler.GarbageHandlerCollect.correct_subcontainer(app, sha_major, sha_minor, achiev)
                    if len(sc_content['achievements']) == 1:
                        path = os.path.join(sha_major[0:2], sha_major, sha_minor)
                        achiev_list.append(path)
                        GarbageHandler.GarbageHandlerCollect.correct_container(app, sha_major, sha_minor)
                        if len(sc_list) == 1:
                            path = os.path.join(sha_major[0:2])
                            achiev_list.append(path)
                            GarbageHandler.GarbageHandlerCollect.correct_object_index(app, sha_major)
                elif 'label' in achievement:
                    continue
                elif diff > self.lifetime_default:
                    path = os.path.join(sha_major[0:2], sha_major, sha_minor, 'achievements', '{}.db'.format(achiev_id))
                    achiev_list.append(path)
                    GarbageHandler.GarbageHandlerCollect.correct_subcontainer(app, sha_major, sha_minor, achiev['id'])
                    if len(sc_content['achievements']) == 1:
                        path = os.path.join(sha_major[0:2], sha_major, sha_minor)
                        achiev_list.append(path)
                        GarbageHandler.GarbageHandlerCollect.correct_container(app, sha_major, sha_minor)
                        if len(sc_list) == 1:
                            path = os.path.join(sha_major[0:2])
                            achiev_list.append(path)
                            GarbageHandler.GarbageHandlerCollect.correct_object_index(app, sha_major)
                else:
                    continue
            if len(sc_content['achievements']) == 0:
                path = os.path.join(sha_major[0:2], sha_major, sha_minor)
                achiev_list.append(path)
                GarbageHandler.GarbageHandlerCollect.correct_container(app, sha_major, sha_minor)
            return achiev_list


        def check_subcontainer(self, app, sha_major, cont_obj):
            ret_list = list()
            sc_list = cont_obj['subcontainer-list']
            for subcont in sc_list:
                sha_minor = subcont['sha-minor']
                ok, sc_content = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sha_minor)
                if not ok:
                    # what then? also remove?
                    continue
                achiev_list = GarbageHandler.GarbageHandlerCollect.check_achiev_lifetime(self, app, sha_major, sha_minor, sc_content, sc_list)
                for achievement in achiev_list:
                    ret_list.append(achievement)
            if len(sc_list) == 0:
                path = os.path.join(sha_major[0:2])
                ret_list.append(path)
                GarbageHandler.GarbageHandlerCollect.correct_object_index(app, sha_major)
            return ret_list