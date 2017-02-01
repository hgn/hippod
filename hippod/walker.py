import os
import hippod.api_shared

class Walker(object):

    def __init__(self, app):
        self. app = app
        self.obj_db = app['DB_OBJECT_PATH']


    def get_subcontainer_list(self, container_path):
        subcontainer_list = list()
        for file in os.listdir(container_path):
            path = os.path.join(container_path, file)
            if os.path.isdir(path) and os.path.basename(path) != "attachments":
                subcontainer_list.append(file)
        return subcontainer_list


    def get_pre_container_list(self):
        pre_container_list = list()
        for file in os.listdir(self.obj_db):
            path = os.path.join(self.obj_db, file)
            if os.path.isdir(path):
                pre_container_list.append(file)
        return pre_container_list


    def get_all_achievements(self):
        pre_container_list = self.get_pre_container_list()
        a = self.AchievementData()
        for pre_container in pre_container_list:
            pre_container_path = os.path.join(self.obj_db, pre_container)
            container_list = os.listdir(pre_container_path)
            for container in container_list:
                container_path = os.path.join(self.obj_db, pre_container, container)
                ok, cont_content = hippod.api_shared.read_cont_obj_by_id(self.app, container)
                a.container.title = cont_content['title']
                a.container.categories = cont_content['categories']
                subcontainer_list = self.get_subcontainer_list(container_path)
                for subcontainer in subcontainer_list:
                    achievements_path = os.path.join(self.obj_db, pre_container, container, subcontainer, 'achievements')
                    achievements = os.listdir(achievements_path)
                    for achievement in achievements:
                        achiev_id = achievement.split('.')[0]
                        content = hippod.api_shared.get_achievement_data_by_sha_id(self.app, container, subcontainer, achiev_id)
                        a.result = content['result']
                        yield a


    class AchievementData(object):

        class ObjectData(object):
            pass

        def __init__(self):
            self.container = self.ObjectData()
