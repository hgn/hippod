import os
import hippod.api_shared
from datetime import datetime as dt

class Walker(object):

    @staticmethod
    def walk_container(app, container, a):
        subcontainer_list = list()
        ok, cont_content = hippod.api_shared.read_cont_obj_by_id(app, container)
        if not ok:
            msg = "couldn't open container {} although listed in directoy. ignore for now".format(container)
            log.error(msg)
            return None
        for subc in cont_content['subcontainer-list']:
            subcontainer_list.append(subc['sha-minor'])
        attachment_id = cont_content['attachments'][-1]['id']
        a.container.title = cont_content['title']
        a.container.categories = cont_content['categories']
        return subcontainer_list, attachment_id, a


    @staticmethod
    def walk_achievement(app, container, subcontainer, achievement, a, limit_to_last_achievement):
        content = hippod.api_shared.get_achievement_data_by_sha_id(app, container, subcontainer, achievement)
        if limit_to_last_achievement == False:
            a.result = content['result']
            return a
        else:
            return content['test-date']


    @staticmethod
    def walk_attachment(app, container, attachment_id, a):
        content = hippod.api_shared.get_attachment_data_by_sha_id(app, container, attachment_id)
        a.container.attachment.tags = content['tags']
        return a


    @staticmethod
    def get_container_list(app):
        container_list = list()
        obj_list = hippod.api_shared.object_index_read(app)
        for obj in obj_list:
            container_list.append(obj['object-item-id'])
        return container_list


    @staticmethod
    def get_achievement_list(app, container, subcontainer, limit_to_last_achievement):
        achievement_list = list()
        ok, content = hippod.api_shared.read_subcont_obj_by_id(app, container, subcontainer)
        if not ok:
            msg = "couldn't open container {} although listed in directoy. ignore for now".format(container)
            log.error(msg)
            return None
        if limit_to_last_achievement == False:
            for achievement in content['achievements']:
                achievement_list.append(achievement['id'])
            return achievement_list
        else:
            return content['achievements'][-1]['id']


    @staticmethod
    def get_last_achievement(app, container, subcontainer, a):
        # fetches last achievement with date to compare with last achievement of other subcontainers
        last_achiev_id = Walker.get_achievement_list(app, container, subcontainer, True)
        achievement_date = Walker.walk_achievement(app, container, subcontainer, last_achiev_id, a, True)
        achievement = dict()
        achievement_date = dt.strptime(achievement_date, '%Y-%m-%dT%H:%M:%S.%f')
        achievement['date'] = achievement_date
        achievement['id'] = last_achiev_id
        achievement['subcontainer'] = subcontainer
        return achievement


    @staticmethod
    def get_latest_index_of_subcontainer(achievement_list):
        # compare dates of all last achievements of all subcontainers of the container
        index = max(range(len(achievement_list)), key=lambda index: \
                    achievement_list[index]['date'])
        return index


    @staticmethod
    def get_achievements(app, limit_to_last_achievement=False):
        # in case of limit_to_last_achievement the iteration process only returns the data
        # from the subcontainer with the latest achievement, else every subcontainer and achievement
        a = Walker.AchievementData()
        container_list = Walker.get_container_list(app)
        # FIXME: what if None?
        for container in container_list:
            last_achievements_of_subcontainer = list()
            subcontainer_list, attachment_id, a = Walker.walk_container(app, container, a)
            a = Walker.walk_attachment(app, container, attachment_id, a)
            for subcontainer in subcontainer_list:
                if limit_to_last_achievement == False:
                    achievements = Walker.get_achievement_list(app, container, subcontainer, limit_to_last_achievement)
                    for achievement in achievements:
                        a = Walker.walk_achievement(app, container, subcontainer, achievement, a, limit_to_last_achievement)
                        yield a
                else:
                    achievement = Walker.get_last_achievement(app, container, subcontainer, a)
                    last_achievements_of_subcontainer.append(achievement)
            if limit_to_last_achievement:
                latest_index = Walker.get_latest_index_of_subcontainer(last_achievements_of_subcontainer)
                subcontainer = last_achievements_of_subcontainer[latest_index]['subcontainer']
                achiev_id = last_achievements_of_subcontainer[latest_index]['id']
                a = Walker.walk_achievement(app, container, subcontainer, achiev_id, a , False)
                yield a


    class AchievementData(object):

        class ObjectData(object):
            pass

            class AttachmentData(object):
                pass

        def __init__(self):
            self.container = self.ObjectData()
            self.container.attachment = self.container.AttachmentData()