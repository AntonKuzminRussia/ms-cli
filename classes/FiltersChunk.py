#!/usr/bin/python3
"""
Class for chunk of filters
"""

from classes.Filter import Filter

class FiltersChunk(object):
    """
    Class for chunk of filters
    """
    filters = None
    db = None
    def __init__(self, db, concrete_id=None):
        """
        Build chunk
        :param db classes.Database:
        """
        self.filters = []
        self.db = db
        filters_rows = db.fetch_all(
            "SELECT id, name, target, type, content FROM filters" +
            ((" WHERE id = {0}".format(concrete_id)) if concrete_id is not None else "")
        )
        for filter_row in filters_rows:
            self.filters.append(
                Filter(
                    filter_row['id'],
                    filter_row['name'],
                    filter_row['target'],
                    filter_row['type'],
                    filter_row['content']
                )
            )

    def run(self, letter):
        """
        Run filters chunk
        :param letter classes.Letter:
        :return:
        """
        return [_filter.get_id() for _filter in self.filters if _filter.process(letter)]
