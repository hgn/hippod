import os
import hippod.api_shared

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
    def walk_achievement(app, container, subcontainer, achievement, a):
        content = hippod.api_shared.get_achievement_data_by_sha_id(app, container, subcontainer, achievement)
        a.result = content['result']
        return a


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
    def get_achievement_list(app, container, subcontainer):
        achievement_list = list()
        ok, content = hippod.api_shared.read_subcont_obj_by_id(app, container, subcontainer)
        if not ok:
            msg = "couldn't open container {} although listed in directoy. ignore for now".format(container)
            log.error(msg)
            return None
        for achievement in content['achievements']:
            achievement_list.append(achievement['id'])
        return achievement_list


    @staticmethod
    def get_all_achievements(app):
        a = Walker.AchievementData()
        container_list = Walker.get_container_list(app)
        # FIXME: what if None?
        for container in container_list:
            subcontainer_list, attachment_id, a = Walker.walk_container(app, container, a)
            a = Walker.walk_attachment(app, container, attachment_id, a)
            for subcontainer in subcontainer_list:
                achievements = Walker.get_achievement_list(app, container, subcontainer)
                for achievement in achievements:
                    a = Walker.walk_achievement(app, container, subcontainer, achievement, a)
                    yield a


    class AchievementData(object):

        class ObjectData(object):
            pass

            class AttachmentData(object):
                pass

        def __init__(self):
            self.container = self.ObjectData()
            self.container.attachment = self.container.AttachmentData()