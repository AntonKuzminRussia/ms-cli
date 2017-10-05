# -*- coding: utf-8 -*-
"""
Attachmnent class
"""

from libs.common import random_md5
from classes.Config import Config


class Attachment(object):
    """
    Attachmnent class
    """
    file_name = ""
    content = None
    mime_type = ""
    ext = ""
    size = 0

    def __init__(self, file_name="", content="", mime_type="", ext="", size=0):
        """
        :param file_name:
        :param content:
        :param mime_type:
        :param ext:
        :param size:
        """
        self.file_name = file_name
        self.content = content
        self.mime_type = mime_type
        self.ext = ext
        self.size = size
        self.attachments_path = Config.get_value('attachments_dir')

    @staticmethod
    def from_db(_id, db):
        """
        Attachments factory for load from db. !Without! file content, db only
        :param id int:
        :param db classes.Database:
        :return Attachment:
        """
        attachment_row = db.fetch_row("SELECT * FROM attachments WHERE id = " + str(_id))
        return Attachment(
            attachment_row['file_name'], "", attachment_row['mime_type'], attachment_row['ext'], attachment_row['size'])

    def set_file_name(self, file_name):
        """
        :param file_name:
        :return:
        """
        self.file_name = file_name

    def set_ext(self, ext):
        """
        :param ext:
        :return:
        """
        self.ext = ext

    def set_content(self, content):
        """
        :param content:
        :return:
        """
        self.content = content
        self.size = len(content) if content else 0

    def set_mime_type(self, mime_type):
        """
        :param mime_type:
        :return:
        """
        self.mime_type = mime_type

    def get_file_name(self):
        """
        :return: str
        """
        return self.file_name

    def get_content(self):
        """
        :return: str
        """
        return self.content

    def get_mime_type(self):
        """
        :return: str
        """
        return self.mime_type

    def get_size(self):
        """
        :return: int
        """
        return self.size

    def flus_to_db(self, db, letter_id):
        """
        :param db classes.Database:
        :param letter_id int:
        :return int: attach id
        """
        _hash = random_md5()

        fh = open(self.attachments_path + "/" + _hash, 'wb')
        fh.write(self.content if self.content is not None else "")
        fh.close()

        data_for_insert = {
            'letter_id': letter_id,
            'file_name': self.file_name,
            'mime_type': self.mime_type[0:50],
            'ext': self.ext,
            'size': self.size,
            'hash': _hash,
        }
        return db.insert("attachments", data_for_insert)
