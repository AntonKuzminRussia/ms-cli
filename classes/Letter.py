# -*- coding: utf-8 -*-
"""
Letter class
"""
import time

from classes.Attachment import Attachment
from classes.Config import Config
from libs.common import file_put_contents, file_get_contents, random_md5


class Letter(object):
    """
    Letter class
    """
    uid = 0
    hash = ""
    body = ""
    raw_body = ""
    subject = ""
    from_name = ""
    from_mail = ""
    to_mail = ""
    to_name = ""
    date = 0
    attachments = None
    filters_finds = None

    def __init__(
            self, uid=0, _hash="", subject="", from_name="", from_mail="", to_name="", to_mail="",
            date=0, body="", raw_body="", attachments=None, filters_finds=None
    ):
        self.uid = uid
        self.hash = _hash
        if len(_hash):
            self.body = file_get_contents(Config.get_value('bodies_path') + _hash)
            self.raw_body = file_get_contents(Config.get_value('bodies_path') + _hash + "-raw")
        else:
            self.body = body
            self.raw_body = raw_body
        self.subject = subject
        self.from_name = from_name
        self.from_mail = from_mail
        self.to_name = to_name
        self.to_mail = to_mail
        self.date = date
        self.attachments = attachments if attachments is not None else []
        self.filters_finds = filters_finds if filters_finds is not None else []

    @staticmethod
    def from_db(_id, db):
        """
        Letters factory for load from db
        :param id int:
        :param db classes.Database:
        :return Letter:
        """

        attachments = []
        attachments_ids = db.fetch_col("SELECT id FROM attachments WHERE letter_id = " + str(_id))
        for attachment_id in attachments_ids:
            attachments.append(Attachment.from_db(attachment_id, db))

        filters_finds = db.fetch_all("SELECT filter_id, letter_id FROM filters_finds WHERE letter_id = " + str(_id))

        letter_row = db.fetch_row("SELECT * FROM letters WHERE id = " + str(_id))
        return Letter(
            uid=letter_row['uid'],
            _hash=letter_row['hash'],
            subject=letter_row['subject'],
            from_name=letter_row['from_name'],
            from_mail=letter_row['from_mail'],
            to_name=letter_row['to_name'],
            to_mail=letter_row['to_mail'],
            date=letter_row['date'],
            body=file_get_contents(Config.get_value('bodies_path') + letter_row['hash']),
            raw_body=file_get_contents(Config.get_value('bodies_path') + letter_row['hash'] + '-raw'),
            attachments=attachments,
            filters_finds=filters_finds
        )

    def set_body(self, body):
        """
        :param body: str
        :return:
        """
        self.body = body

    def set_raw_body(self, raw_body):
        """
        :param raw_body:
        :return:
        """
        self.raw_body = raw_body

    def set_subject(self, subject):
        """
        :param subject:
        :return:
        """
        self.subject = subject

    def set_from_name(self, from_name):
        """
        :param from_name:
        :return:
        """
        self.from_name = from_name

    def set_from_mail(self, from_mail):
        """
        :param from_mail:
        :return:
        """
        self.from_mail = from_mail

    def set_to_mail(self, to_mail):
        """
        :param to_mail:
        :return:
        """
        self.to_mail = to_mail

    def set_to_name(self, to_name):
        """

        :param to_name:
        :return:
        """
        self.to_name = to_name

    def set_attachements(self, attachements):
        """
        :param attachement list[classes.Attachement]:
        :return:
        """
        self.attachments = attachements

    def get_subject(self):
        """
        :return: str
        """
        return self.subject

    def get_body(self):
        """
        :return: str
        """
        return self.body

    def get_raw_body(self):
        """
        :return: str
        """
        return self.raw_body

    def get_from_name(self):
        """
        :return: str
        """
        return self.from_name

    def get_from_mail(self):
        """
        :return: str
        """
        return self.from_mail

    def get_to_name(self):
        """
        :return: str
        """
        return self.to_name

    def get_to_mail(self):
        """
        :return: str
        """
        return self.to_mail

    def get_attachments(self):
        """
        :return: str
        """
        return self.attachments

    def set_filters_finds(self, filters_finds):
        """
        :param filters_finds:
        :return:
        """
        self.filters_finds = filters_finds

    def flush_to_db(self, db, folder_id):
        """
        :param db classes.Database:
        :return int: letter id
        """

        _hash = random_md5()

        data_for_insert = {
            'uid': self.uid,
            'folder_id': folder_id,
            'subject': str(self.subject),
            'hash': _hash,
            'from_name': self.from_name,
            'from_mail': self.from_mail,
            'to_name': self.to_name,
            'to_mail': self.to_mail,
            'has_attachments': int(bool(len(self.attachments))),
            'date': self.date,
            'when_add': int(time.time())
        }
        letter_id = db.insert("letters", data_for_insert)

        file_put_contents(Config.get_value('bodies_path') + _hash, str(self.body))
        file_put_contents(Config.get_value('bodies_path') + _hash + "-raw", str(self.raw_body))

        for attachment in self.attachments: #type: Attachment
            attachment.flus_to_db(db, letter_id)

        for filter_id in self.filters_finds:
            db.insert(
                "filters_finds",
                {
                    'letter_id': letter_id,
                    'filter_id': filter_id,
                    'when_add': int(time.time())
                }
            )
