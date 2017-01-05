import logging

import hippod.container_db
import hippod.mime_data_db

log = logging.getLogger()


class GHMimeData(object):

    @staticmethod
    def remove(app):
        referenced_data = hippod.container_db.all_referenced_mime_ids(app)
        stored_data = hippod.mime_data_db.get_saved_data(app)
        set_rd = set(referenced_data)
        set_sd = set(stored_data)
        outdated_data = list(set_rd.union(set_sd) - set_rd.intersection(set_sd))
        if len(outdated_data) != 0:
            log.info('remove {} outdated data elements'.format(len(outdated_data)))
            hippod.mime_data_db.remove_data(app, outdated_data)