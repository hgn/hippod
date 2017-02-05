import os
import json


class Cache(object):
    def __init__(self, app, frequency):
        self.app = app
        self.frequency = frequency
        self.data = list()


    def get_manual_persons(self):
        manual_persons = list()
        conf_path = self.app['CONF_ROOT_PATH']
        db_path = os.path.join(conf_path, 'user.db')
        with open(db_path, 'r') as f:
            db = json.load(f)
        for person, data in db.items():
            entry = dict()
            entry['nick'] = person
            entry['full'] = data['fullname']
            manual_persons.append(entry)
        return manual_persons


    def get_ldap_persons(self):
        ldap_persons = list()
        conf_path = self.app['CONF_ROOT_PATH']
        db_path = os.path.join(conf_path, 'ldap.db')
        with open(db_path, 'r') as f:
            db = json.load(f)
        for person, data in db.items():
            entry = dict()
            entry['nick'] = person
            entry['full'] = data['fullname']
            ldap_persons.append(entry)
        return ldap_persons


    def update(self):
        manual_persons = self.get_manual_persons()
        ldap_persons = self.get_ldap_persons()
        persons = manual_persons + ldap_persons
        persons = list({v['nick']:v for v in persons}.values())
        self.data = persons


    def write_cache_file(self):
        cache_db = self.app['DB_CACHE_PATH']
        achievements_cache_path = os.path.join(cache_db, 'cache-persons.db')
        data = json.dumps(self.data, sort_keys=True,indent=4, separators=(',', ': '))
        with open(achievements_cache_path, 'w') as f:
            f.write(data)


