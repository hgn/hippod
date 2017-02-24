import os
import json
import datetime

import pprint



class Cache(object):
    def __init__(self, app, frequency):
        self.app = app
        self.frequency = frequency
        self.data = self.init_data()
        self.stored_data = self.read_old_cache()
        dt = datetime.datetime.now()
        dt = dt.replace(hour=0, minute=0, second=0, microsecond= 0)
        self.date = dt.timestamp()
        self.stored_data['passed'].insert(len(self.stored_data['passed']), [self.date, 0])
        self.stored_data['failed'].insert(len(self.stored_data['failed']), [self.date, 0])
        self.stored_data['nonapplicable'].insert(len(self.stored_data['nonapplicable']), [self.date, 0])


    def init_data(self):
        d = dict()
        d['achievement-results-by-category'] = dict()
        d['achievement-results-sunburn-chart'] = dict()
        d['achievement-results-sunburn-chart']['name'] = 'init'
        d['achievement-results-sunburn-chart']['children'] = list()
        d['achievement-results-sunburn-chart']['root'] = 'root'
        return d


    def read_old_cache(self):
        cache_db = os.path.join(self.app['DB_CACHE_PATH'])
        achievements_cache_path = os.path.join(cache_db, 'cache-achievements.db')
        if not os.path.isfile(achievements_cache_path):
            with open(achievements_cache_path, 'w') as file:
                data = dict()
                data = json.dumps(data, sort_keys=True,indent=4, separators=(',', ': '))
                file.write(data)
        with open(achievements_cache_path, 'r') as file:
            data = json.load(file)
        if 'achievements-by-time' not in data:
            data['achievements-by-time'] = dict()
            date['achievements-by-time']['passed'] = list()
            date['achievements-by-time']['failed'] = list()
            date['achievements-by-time']['nonapplicable'] = list()
        return data['achievements-by-time']


    def write_cache_file(self):
        cache_db = self.app['DB_CACHE_PATH']
        achievements_cache_path = os.path.join(cache_db, 'cache-achievements.db')
        self.data['achievements-by-time'] = dict()
        self.data['achievements-by-time'] = self.stored_data
        # self.data = {**self.data, **self.stored_data}
        data = json.dumps(self.data, sort_keys=True,indent=4, separators=(',', ': '))
        with open(achievements_cache_path, 'w') as f:
            f.write(data)

    def check_already_listed(self, buffer_stat, cat):
        listed = False
        for i, name in enumerate(d['name'] for d in buffer_stat['children']):
            if cat == name:
                listed = True
        return listed

    def is_end_of_hierarchy(self, j, cat):
        end = False
        if j == len(cat)-1:
                end = True
        return end


    def next_stat_in_hierarchy(self, buffer_stat, cat):
        for d in buffer_stat['children']:
            if d['name'] == cat:
                return d


    def update_sub_cat(self, buffer_stat, sub_cat):
        if not buffer_stat['children']:
            return None, False
        try:
            for child in buffer_stat['children']:
                if child['name'] == sub_cat:
                    child['size'] += 1
                    return child, True
                continue
            return None, False
        except:
            return None, False


    def update(self, achievement):
        if self.frequency != "daily":
            # FIXME: daily or maybe hourly?
            return None
        category = str(achievement.container.categories)
        result = achievement.result
        if category not in self.data['achievement-results-by-category']:
            self.data['achievement-results-by-category'][category] = list()
        self.data['achievement-results-by-category'][category].append(result)

        # save here results for sunburn data structre which is special
        # with keys like name, children, size
        # children-parent-hierarchy based on categories levels e.g. team->topic-subtopic
        buffer_stat = self.data['achievement-results-sunburn-chart']
        cat = eval(category)
        root = cat[0]
        for j in range(0,len(cat)):
            listed = self.check_already_listed(buffer_stat, cat[j])
            end = self.is_end_of_hierarchy(j, cat)
            if j < len(cat)-1 and not listed:
                sub_stat = dict()
                sub_stat['name'] = str(cat[j])
                sub_stat['root'] = root
                sub_stat['children'] = list()
                buffer_stat['children'].append(sub_stat)
                buffer_stat = sub_stat
            elif end:
                size_token = False
                for d in buffer_stat['children']:
                    if d['name'] == cat[j] and 'size' in d:
                        d['size'] += 1
                        size_token = True
                if size_token:
                    continue
                add_stat, update = self.update_sub_cat(buffer_stat, cat[j])
                if not update:
                    add_stat = dict()
                    add_stat['name'] = str(cat[j])
                    add_stat['root'] = root
                    add_stat['size'] = 1
                    buffer_stat['children'].append(add_stat)
            else:
                found = False
                for d in buffer_stat['children']:
                    if d['name'] == cat[j] and 'children' in d:
                        buffer_stat = d
                        found = True
                if not found:
                    dct = dict()
                    dct['name'] = cat[j]
                    dct['root'] = cat[0]
                    dct['children'] = list()
                    buffer_stat['children'].append(dct)
                    buffer_stat = dct
                continue

        # achievements by date/time
        # index '-1' is the latest date entry
        # at the end is a list with [date, amount_of_results]
        result = achievement.result
        if result == 'passed':
            self.stored_data['passed'][-1][1] += 1
        elif result == 'failed':
            self.stored_data['failed'][-1][1] += 1
        elif result == 'nonapplicable':
            self.stored_data['nonapplicable'][-1][1] += 1


    def sort(self, data):
        data = sorted(data, key=lambda k: k['name'])
        for d in data:
            if 'children' in d:
                d['children'] = self.sort(d['children'])
            else:
                continue        return data


    def order_for_sunburn(self):
        all_categories = self.data['achievement-results-sunburn-chart']['children']
        self.data['achievement-results-sunburn-chart']['children'] = self.sort(all_categories)
        cache_db = self.app['DB_CACHE_PATH']
        achievements_cache_path = os.path.join(cache_db, 'cache-achievements.db')
        data = json.dumps(self.data, sort_keys=True,indent=4, separators=(',', ': '))
        with open(achievements_cache_path, 'w') as f:
            f.write(data)