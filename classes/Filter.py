#!/usr/bin/python3
"""
Filter class
"""

import re


class Filter(object):
    """
    Filter class
    """
    id = None
    name = ""
    target = ""
    type = ""
    content = ""

    def __init__(self, _id, name, target, _type, content):
        self.id = _id
        self.name = name
        self.target = target
        self.type = _type
        self.content = content

    def get_id(self):
        """
        :return: int
        """
        return self.id

    def match(self, source):
        """
        Find filter`s matching in str
        :param source str: string for found match
        :return:
        """
        if self.type == 'str':
            return bool(str(source).count(self.content))
        if self.type == 'regex':
            return bool(re.match(self.content, source))
        raise Exception("Wrong filter type '{0}'! {1}".format(self.type, self.name))

    def process(self, letter):
        """
        Process letter
        :param letter classes.Letter:
        :return:
        """
        if self.target == "subject":
            return self.match(letter.get_subject())
        if self.target == "content":
            return self.match(letter.get_body())
        if self.target == "from":
            if self.match(letter.get_from_name()) or self.match(letter.get_from_mail()):
                return True
            return False
        if self.target == "to":
            if self.match(letter.get_to_name()) or self.match(letter.get_to_mail()):
                return True
            return False
        if self.target == "attachment":
            for attachment in letter.get_attachments(): #type: classes.Attachment
                if self.match(attachment.get_file_name()) or self.match(attachment.get_mime_type()):
                    return True
            return False
        raise Exception("Wrong filter target '{0}'! {1}".format(self.target, self.name))
