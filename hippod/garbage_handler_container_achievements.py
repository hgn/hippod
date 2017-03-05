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
            log.error("incorrect time unit...choose between 'seconds', 'minutes', 'hours',"
                      "'days' and 'months'")
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
                    continue


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
                ret_data = data
            with open(path, 'w') as data_file:
                data = json.dumps(data, sort_keys=True,indent=4,
                      separators=(',', ': '))
                data_file.write(data)
            return ret_data


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
                ret_data = data
            with open(path, 'w') as data_file:
                data = json.dumps(data, sort_keys=True,indent=4,
                      separators=(',', ': '))
                data_file.write(data)
            return ret_data['subcontainer-list']


        def correct_object_index(self, app, sha_major):
            path = os.path.join(app['DB_OBJECT_PATH'],
                        'object-index.db')
            with open(path) as data_file:
                data = json.load(data_file)
                for i, d in enumerate(data):
                    if d['object-item-id'] == sha_major:
                        del data[i]
                ret_data = data
            with open(path, 'w') as data_file:
                data = json.dumps(data, sort_keys=True,indent=4,
                      separators=(',', ': '))
                data_file.write(data)
            return ret_data


        def write_lifetime_subcontainer(self, app, sha_major, sha_minor, diff_lifetime, achiev_id):
            obj_path = app['DB_OBJECT_PATH']
            ok, cont_content = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sha_minor)
            if not ok:
                log.error("cannot read container {}/{} by sha, ignore for now".format(sha_major, sha_minor))
                return
            lifetimes = list()
            for achievement in cont_content['achievements']:
                if str(achievement['id']) == achiev_id:
                    achievement['lifetime-leftover'] = diff_lifetime
                lifetimes.append(achievement['lifetime-leftover'])
            cont_content['lifetime-leftover'] = min(lifetimes)
            subc_path = os.path.join(obj_path, sha_major[0:2], sha_major, sha_minor, 'subcontainer.db')
            with open(subc_path, 'w') as f:
                content = json.dumps(cont_content, sort_keys=True,indent=4, separators=(',', ': '))
                f.write(content)


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
                    path = os.path.join(sha_major[0:2], sha_major)
                    return_list.append(path)
                    self.correct_object_index(app, sha_major)
            return return_list


        def check_achiev_lifetime(self, app, sha_major, sha_minor, sc_content, sc_list):
            garbage_list = list()
            achiev_path = os.path.join(app['DB_OBJECT_PATH'], sha_major[0:2], sha_major, sha_minor, 'achievements')
            for achiev in sc_content['achievements']:
                achiev_id = str(achiev['id'])
                date_added = hippod.utils_date.string_to_datetime(achiev['date-added'])
                achievement = hippod.api_shared.get_achievement_data_by_sha_id(app, sha_major, sha_minor, achiev_id)
                if not achievement:
                    continue
                deltatime = (datetime.datetime.now() - date_added).total_seconds()
                diff = deltatime
                # labled tests shouldn't be removed, so continue
                if 'label' in achievement:
                    continue
                elif 'anchor' in achievement and diff > self.lifetime_anchored:
                    path = os.path.join(sha_major[0:2], sha_major, sha_minor, 'achievements', '{}.db'.format(achiev_id))
                    garbage_list.append(path)
                    sc_content = self.correct_subcontainer(app, sha_major, sha_minor, achiev['id'])
                elif 'anchor' not in achievement and diff > self.lifetime_default:
                    path = os.path.join(sha_major[0:2], sha_major, sha_minor, 'achievements', '{}.db'.format(achiev_id))
                    garbage_list.append(path)
                    sc_content = self.correct_subcontainer(app, sha_major, sha_minor, achiev['id'])
                else:
                    if 'anchor' in achievement:
                        diff_lifetime = self.lifetime_anchored - diff
                    else:
                        diff_lifetime = self.lifetime_default - diff
                    self.write_lifetime_subcontainer(app, sha_major, sha_minor, diff_lifetime, achiev_id)
                    continue
            if len(sc_content['achievements']) == 0:
                path = os.path.join(sha_major[0:2], sha_major, sha_minor)
                garbage_list.append(path)
                sc_list = self.correct_container(app, sha_major, sha_minor)
            # elif len(sc_content['achievements']) != 0 and len(os.listdir(achiev_path)) == 0:
            #     log.error('meta data in subcontainer is not up to date with achievements directory')
            return garbage_list, sc_list


        def check_subcontainer(self, app, sha_major, cont_obj):
            ret_list = list()
            sc_list = cont_obj['subcontainer-list']
            for subcont in sc_list:
                sha_minor = subcont['sha-minor']
                ok, sc_content = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sha_minor)
                if not ok:
                    log.error("cannot read container {}/{} by sha, ignore for now".format(sha_major, sha_minor))
                    continue
                achiev_list, sc_list = self.check_achiev_lifetime(app, sha_major, sha_minor, sc_content, sc_list)
                for achievement in achiev_list:
                    ret_list.append(achievement)
            if len(sc_list) == 0:
                path = os.path.join(sha_major[0:2], sha_major)
                ret_list.append(path)
                self.correct_object_index(app, sha_major)
            return ret_list