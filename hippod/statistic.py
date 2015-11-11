import sys
import json
import hashlib
import base64
import datetime
import os

from hippod import app

def dir_size(path):
    sys.stderr.write("path {}\n".format(path))
    total_size = os.path.getsize(path)
    for item in os.listdir(path):
        itempath = os.path.join(path, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += dir_size(itempath)
    return total_size


def folder_size(db_path):
    root_size = os.path.getsize(db_path)
    data_size = dir_size(os.path.join(db_path, "data_compressed"))
    object_db_size = dir_size(os.path.join(db_path, "objects"))
    cumulative = root_size + data_size + object_db_size
    return cumulative, object_db_size, data_size


def stats_written_today(path, today):
    with open(path) as data_file:
        data = json.load(data_file)
        if not len(data['item-bytes-overtime']) > 0:
            return False, data
        last_written_date = data['item-bytes-overtime'][-1][0]
        if last_written_date == today:
            return True, data
        return False, data


def update_global_db_stats():
    stat_path = app.config['DB_STATISTICS_FILEPATH']
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    uptodate, data = stats_written_today(stat_path, today)
    if uptodate:
        return

    db_path = app.config['DB_ROOT_PATH']
    cumulative, object_db_size, data_size = folder_size(db_path)

    # XXX: this assumes that the DB can grow *only*
    if len(data['item-bytes-overtime']) > 0 and \
       cumulative <= data['item-bytes-overtime'][-1][1] + 1000:
        # the size do not differ greatly (1K) from the last one
        # we do *not* write tiny changes here to keep bookkepping
        # information smaller. Sammler writtes are usually from new
        # tests results, but no new data objects.
        return

    data['item-bytes-overtime'].append([today, cumulative, object_db_size, data_size])
    d_jsonfied =  json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    with open(stat_path, "w+") as f:
        f.write(d_jsonfied)

