import os
import datetime
import json
import shutil
import logging

import hippod.api_shared
import hippod.utils_date

log = logging.getLogger()


class GHContainerAchievements(object):

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
        garbage = GHContainerAchievements()
        lifetime_default = garbage.convert_lifetime(conf.achievements_validity_lifetime.achievements)
        lifetime_anchored = garbage.convert_lifetime(conf.achievements_validity_lifetime.achievements_anchored)
        collector = GHContainerAchievements.GHContainerAchievementsCollect(lifetime_default, lifetime_anchored)
        garbage_list = collector.search(app)
        if garbage_list != None:
            log.info("remove now {} outdated elements".format(len(garbage_list)))
            garb_remover = GHContainerAchievements.GHContainerAchievementsRemove(garbage_list)
            garb_remover.remove(app)
                

    class GHContainerAchievementsRemove(object):
        def __init__(self, garbage_list):
            self.garbage_list = garbage_list

        def remove(self, app):
            log.debug("starting remove old and unnecessary files")
            obj_path = app['DB_OBJECT_PATH']
            for garbage in self.garbage_list:
                garbage_path = os.path.join(obj_path, garbage)
                if os.path.isfile(garbage_path):
                    os.remove(garbage_path)
                elif os.path.isdir(garbage_path):
                    shutil.rmtree(garbage_path)
                else:
                    log.error("unexpected file format discovered, ignore for now")


    class GHContainerAchievementsCollect(object):
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
                    log.error("cannot read container {} by sha, ignore for now".format(cont['object-item-id']))
                    continue
                container_garbage = self.check_subcontainer(app, cont['object-item-id'], cont_obj)
                for item in container_garbage:
                    garbage_list.append(item)
            return garbage_list


        def correct_subcontainer(self, app, sha_major, sha_minor, achiev_id):
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


        def correct_container(self, app, sha_major, sha_minor):
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


        def correct_object_index(self, app, sha_major):
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


        # if the achievement added to the garbage_list was the last one in subcontainer,
        # the subcontainer is empty/useless
        # same for subcontainer...if was the last one, container can be also removed
        def check_for_last_element(self, app, sha_major, sha_minor, achievements, sc_list):
            return_list = list()
            if len(achievements) == 1:
                path = os.path.join(sha_major[0:2], sha_major, sha_minor)
                return_list.append(path)
                self.correct_container(app, sha_major, sha_minor)
                if len(sc_list) == 1:
                    path = os.path.join(sha_major[0:2])
                    return_list.append(path)
                    self.correct_object_index(app, sha_major)
            return return_list


        def check_achiev_lifetime(self, app, sha_major, sha_minor, sc_content, sc_list):
            achiev_list = list()
            for achiev in sc_content['achievements']:
                achiev_id = str(achiev['id'])
                date_added = hippod.utils_date.string_to_datetime(achiev['date-added'])
                achievement = hippod.api_shared.get_achievement_data_by_sha_id(app, sha_major, sha_minor, achiev_id)
                deltatime = (datetime.datetime.now() - date_added).total_seconds()
                diff = deltatime
                # labled tests shouldn't be removed
                if 'label' in achievement:
                    continue
                elif 'anchor' in achievement and diff > self.lifetime_anchored:
                    path = os.path.join(sha_major[0:2], sha_major, sha_minor, 'achievements', '{}.db'.format(achiev_id))
                    achiev_list.append(path)
                    self.correct_subcontainer(app, sha_major, sha_minor, achiev)
                    waste_list = self.check_for_last_element(app, sha_major, sha_minor, sc_content['achievements'], sc_list)
                    for waste_path in waste_list:
                        achiev_list.append(waste_path)
                elif 'anchor' not in achievement and diff > self.lifetime_default:
                    path = os.path.join(sha_major[0:2], sha_major, sha_minor, 'achievements', '{}.db'.format(achiev_id))
                    achiev_list.append(path)
                    self.correct_subcontainer(app, sha_major, sha_minor, achiev['id'])
                    waste_list = self.check_for_last_element(app, sha_major, sha_minor, sc_content['achievements'], sc_list)
                    for waste_path in waste_list:
                        achiev_list.append(waste_path)
                else:
                    continue
            if len(sc_content['achievements']) == 0:
                path = os.path.join(sha_major[0:2], sha_major, sha_minor)
                achiev_list.append(path)
                self.correct_container(app, sha_major, sha_minor)
            return achiev_list


        def check_subcontainer(self, app, sha_major, cont_obj):
            ret_list = list()
            sc_list = cont_obj['subcontainer-list']
            for subcont in sc_list:
                sha_minor = subcont['sha-minor']
                ok, sc_content = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sha_minor)
                if not ok:
                    log.error("cannot read container {} by sha, ignore for now".format(cont['object-item-id']))
                    continue
                achiev_list = self.check_achiev_lifetime(app, sha_major, sha_minor, sc_content, sc_list)
                for achievement in achiev_list:
                    ret_list.append(achievement)
            if len(sc_list) == 0:
                path = os.path.join(sha_major[0:2])
                ret_list.append(path)
                self.correct_object_index(app, sha_major)
            return ret_list