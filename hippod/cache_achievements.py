import os
import json


class Cache(object):
    def __init__(self, app, frequency):
        self.app = app
        self.frequency = frequency
        self.data = self.init_data()


    def init_data(self):
        d = dict()
        d['achievement-results-by-category'] = dict()
        return d


    def write_cache_file(self):
        cache_db = self.app['DB_CACHE_PATH']
        achievements_cache_path = os.path.join(cache_db, 'cache-achievements.db')
        data = json.dumps(self.data, sort_keys=True,indent=4, separators=(',', ': '))
        with open(achievements_cache_path, 'w') as f:
            f.write(data)


    def update(self, achievement):
        if self.frequency != "daily":
            # FIXME: daily or maybe hourly?
            return None
        category = str(achievement.container.categories)
        result = achievement.result
        if category not in self.data['achievement-results-by-category']:
            self.data['achievement-results-by-category'][category] = list()
        self.data['achievement-results-by-category'][category].append(result)
