import sys
import json
import hashlib
import base64
import datetime
import os

from hippod import app


def folder_size(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += folder_size(itempath)
    return total_size


def stats_are_uptodate(path, today):
    with open(path) as data_file:
        data = json.load(data_file)
        if not len(data['item-bytes-overtime']) > 0:
            return False, data
        last_written_date = data['item-bytes-overtime'][-1][0]
        if last_written_date == today:
            return True, None
        return False, data


def update_global_db_stats():
    stat_path = app.config['DB_STATISTICS_FILEPATH']
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    uptodate, data = stats_are_uptodate(stat_path, today)
    if uptodate:
        return

    db_path = app.config['DB_OBJECT_PATH']
    comulative_size = folder_size(db_path)
    data['item-bytes-overtime'].append([today, comulative_size, 0])
    d_jsonfied =  json.dumps(data, sort_keys=True,indent=4, separators=(',', ': '))
    with open(stat_path, "w+") as f:
        f.write(d_jsonfied)

