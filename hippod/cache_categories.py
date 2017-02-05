import os
import json


class Cache(object):
    def __init__(self, app, frequency):
        self.app = app
        self.frequency = frequency
        self.data = self.init_data()


    def init_data(self):
        d = dict()
        d['categories-full'] = list()
        d['categories-single'] = list()
        return d


    def write_cache_file(self):
        cache_db = self.app['DB_CACHE_PATH']
        categories_cache_path = os.path.join(cache_db, 'cache-categories.db')
        data = json.dumps(self.data, sort_keys=True,indent=4, separators=(',', ': '))
        with open(categories_cache_path, 'w') as f:
            f.write(data)


    def update(self, achievement):
        if self.frequency != "daily":
            # a daily updating for categories cache is optimal...weekly or hourly not
            return None
        category = achievement.container.categories
        self.data['categories-full'].append(category)
        self.data['categories-single'] = self.data['categories-single'] + category
