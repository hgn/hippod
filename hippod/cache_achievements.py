import os
import json
import datetime

import pprint

import logging

log = logging.getLogger()

pp = pprint.PrettyPrinter()


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
        self.stored_data['exception'].insert(len(self.stored_data['exception']), [self.date, 0])


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
            self.data['achievements-by-time'] = dict()
            self.data['achievements-by-time']['passed'] = list()
            self.data['achievements-by-time']['failed'] = list()
            self.data['achievements-by-time']['nonapplicable'] = list()
            self.data['achievements-by-time']['exception'] = list()
            return self.data['achievements-by-time']
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


    def update_sunburn_size_entry(self, buffer_stat, sub_category):
        updated = False
        for d in buffer_stat['children']:
            if d['name'] == sub_category and 'size' in d:
                d['size'] += 1
                updated = True
        return buffer_stat['children'], updated


    def add_new_sunburn_child_entry(self, root, sub_category):
        entry = dict()
        entry['name'] = str(sub_category)
        entry['root'] = root
        entry['children'] = list()
        return entry


    def initiate_new_sunburn_size_entry(self, root, sub_category):
        entry = dict()
        entry['name'] = str(sub_category)
        entry['root'] = root
        entry['size'] = 1
        return entry


    def next_hierarchy_level(self, buffer_stat, sub_category):
        for d in buffer_stat['children']:
            if d['name'] == sub_category and 'children' in d:
                buffer_stat = d
                return True, buffer_stat
        return False, None


    def update(self, achievement):
        if self.frequency != "daily":
            # FIXME: daily or maybe hourly?
            return None
        category = str(achievement.container.categories)
        result = achievement.result
        if category not in self.data['achievement-results-by-category']:
            self.data['achievement-results-by-category'][category] = list()
        self.data['achievement-results-by-category'][category].append(result)

        self.update_sunburn_data(category, result)

        # achievements saved by date/time
        # index '-1' is the latest date entry
        # at the end is a list with [date, amount_of_results]
        if result == 'passed':
            self.stored_data['passed'][-1][1] += 1
        elif result == 'failed':
            self.stored_data['failed'][-1][1] += 1
        elif result == 'nonapplicable':
            self.stored_data['nonapplicable'][-1][1] += 1
        elif result == 'exception':
            self.stored_data['exception'][-1][1] += 1
        else:
            log.error('unassignable result: {}'.format(result))


    def update_sunburn_data(self, category, result):
        # save here results for sunburn data structre which is specified
        # with keys like name, children, size (root is added for color selection method)
        # children-parent-hierarchy based on categories levels e.g. team->topic->subtopic
        # data structure (for input category ['team:bar'] and ['team:foo', 'topic:ip'])
        # is looking like (size is here the amount of tests):
        #
        # "children": [
        #     {
        #         "name": "team:bar",
        #         "root": "team:bar",
        #         "size": 1
        #     },
        #     {
        #         "name": "team:foo",
        #         "root": "team:foo",
        #         "children": [
        #             {
        #                 "name": "topic:ip",
        #                 "root": "team:foo",
        #                 "size": 1
        #             }
        #         ]
        #     }
        # ]
        buffer_stat = self.data['achievement-results-sunburn-chart']
        cat = eval(category)
        root = cat[0]
        # cat is a list of categories ordered in a hierarchy
        # e.g. ['team:red', 'topic:foo', 'subtopic:foobar']
        # root is the very first sub category
        for j in range(0,len(cat)):
            if j < len(cat)-1:
                # when there are more levels of categories
                # going deeper inside the hierarchy
                found, next_level_entry = self.next_hierarchy_level(buffer_stat, cat[j])
                if found:
                    buffer_stat = next_level_entry
                    continue
                entry = self.add_new_sunburn_child_entry(root, cat[j])
                buffer_stat['children'].append(entry)
                buffer_stat = entry
                continue
            else:
                # in the last level of the category hierarchy size have to be
                # added or updated when a size entry is already available
                updated_entry, updated = self.update_sunburn_size_entry(buffer_stat, cat[j])
                if updated:
                    buffer_stat['children'] = updated_entry
                    continue
                entry = self.initiate_new_sunburn_size_entry(root, cat[j])
                buffer_stat['children'].append(entry)


    def sort(self, data):
        data = sorted(data, key=lambda k: k['name'])
        for d in data:
            if 'children' in d:
                d['children'] = self.sort(d['children'])
            else:
                continue
        return data


    def order_for_sunburn(self):
        # ordering categories by name so if a category has only one level, it is not seperated
        # from the same root category with more than one level in the list
        # e.g. ['team:red'] and ['team:red', 'topic:ip']
        all_categories = self.data['achievement-results-sunburn-chart']['children']
        self.data['achievement-results-sunburn-chart']['children'] = self.sort(all_categories)
        cache_db = self.app['DB_CACHE_PATH']
        achievements_cache_path = os.path.join(cache_db, 'cache-achievements.db')
        data = json.dumps(self.data, sort_keys=True,indent=4, separators=(',', ': '))
        with open(achievements_cache_path, 'w') as f:
            f.write(data)
