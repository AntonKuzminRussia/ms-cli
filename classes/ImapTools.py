#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Common class with static methods for all work
"""
import datetime
import time
import re
import pprint
import email
from email import header

from imapclient import imap_utf7

from classes.Letter import Letter
from classes.Attachment import Attachment
from classes.FiltersChunk import FiltersChunk
from classes.Logger import Logger
from libs.common import random_md5


class ImapTools(object):
    """
    Common class with static methods for all work
    """
    @staticmethod
    def get_folders_names(imap):
        """
        Return list of imap account`s folders
        :param imap: imaplib.IMAP4
        :return: list
        """
        folders = []
        result_code, folders_records = imap.list()
        for folder_record in folders_records:
            folder_record = imap_utf7.decode(folder_record)
            #folder_server_name = folder_record.encode('utf8').decode('utf8').split('"|"')[1].strip(' "')
            folder_server_name = folder_record.encode('utf8').decode('utf8').split(' ')[-1].strip(' \'"')
            folders.append(
                {
                    'name': folder_server_name.replace('\xa0', ' '),
                    'server_name': folder_server_name,
                }
            )
        return folders

    @staticmethod
    def refresh_account_folders_list(db, imap, account_id):
        """
        Refresh list of account`s folders in DB.
        New folders marks so, old folders not change
        :param db: classes.Database
        :param imap: imaplib.IMAP4
        :param account_id: int
        :return:
        """
        last_updated = int(time.time())

        for folder_data in ImapTools.get_folders_names(imap): #type: str
            parent_id = 0
            for folder_name in folder_data['name'].split("|"):
                folder_id = db.fetch_one(
                    "SELECT id FROM folders WHERE account_id={0} AND parent_id={1} AND name={2}".format(
                        int(account_id), parent_id, db.quote(folder_name))
                )
                if folder_id:
                    parent_id = folder_id
                    db.update("folders", {'last_updated': last_updated}, "id = {0}".format(folder_id))
                    continue
                else:
                    parent_id = db.insert(
                        "folders",
                        {
                            'account_id': account_id,
                            'parent_id': parent_id,
                            'name': folder_name,
                            'full_name': folder_data['name'],
                            'server_name': folder_data['server_name'],
                            'last_updated': last_updated
                        }
                    )
        db.q(
            "UPDATE folders SET removed=1, name=CONCAT(name, '_REMOVED_{0}') "
            "WHERE account_id = {1} AND last_updated < {2}".format(
                time.strftime("%Y%m%d", time.localtime()), account_id, last_updated)
        )

    @staticmethod
    def get_all_letters_uids_from_folder(imap, folder):
        """
        Get list of all letters from folder
        :param imap: imaplib.IMAP4
        :param folder: str
        :return: list
        """
        uids = []
        try:
            imap.select(imap_utf7.encode('"' + folder['server_name'] + '"'))
            uids = imap.uid('SEARCH', 'UID 1:*')[1][0].split()
        except BaseException as ex:
            Logger.log_ex(ex, "Get folder`s uids {0}/{1}".format(folder['id'], folder['name']))
        return uids

    @staticmethod
    def get_fresh_letters_uids_from_folder(imap, folder, last_uid):
        """
        Get list of letters from folder, later last_checked time
        :param imap: imaplib.IMAP4
        :param folder: str
        :param last_uid: int
        :return: list
        """
        uids = []
        try:
            imap.select(imap_utf7.encode('"' + folder + '"'))
            uids = imap.uid('SEARCH', 'UID {0}:*'.format(last_uid + 1))[1][0].split()
        except BaseException as ex:
            Logger.log_ex(ex, "Get fresh folder`s uids {0}/{1}".format(folder['id'], folder['name']))
        return uids

    @staticmethod
    def _decode_header(_s, email_charset):
        """
        Encoding letter`s headers and return it in utf8
        :param _s: str
        :return:
        """
        if _s is None:
            return ""

        raw_content = ""
        for _s_raw, _subj_encoding in header.decode_header(_s):
            if isinstance(_s_raw, bytes):
                _s_raw = _s_raw.decode(_subj_encoding if _subj_encoding else email_charset)
            else:
                _s_raw = str(_s_raw)

            raw_content += _s_raw

        return raw_content.encode('utf8').decode('utf8')

    @staticmethod
    def detect_internal_mail_encoding_from_bytes(email_raw):
        """
        Method search first message part with encoding in content-type header, and return this encoding
        :param email_raw:
        :return: str
        """
        default_charset = 'utf-8'
        charset = None
        parsed_body = email.message_from_string(email_raw[0][1].decode('utf8', errors='ignore'))
        if parsed_body.get_content_maintype() == 'multipart':  # multipart messages only
            for parsed_body_part in parsed_body.walk():
                if parsed_body_part.get_content_charset() is not None:
                    charset = parsed_body_part.get_content_charset()
                    break
        else:
            charset = parsed_body.get_content_charset()

        return charset if charset is not None else default_charset

    @staticmethod
    def decode_email_parsed_body_text(parsed_body, email_charset):
        """
        Get raw pased email body and decode it to utf8 text
        :param parsed_body:
        :param email_charset:
        :return: str
        """
        need_decode = False
        if parsed_body.get('Content-Transfer-Encoding') and \
            parsed_body.get('Content-Transfer-Encoding').lower() in ['base64', 'quoted-printable']:
            need_decode = True

        if need_decode:
            decode_charset = parsed_body.get_content_charset() if parsed_body.get_content_charset() else email_charset
            ready_text = parsed_body.get_payload(decode=True).decode(decode_charset, errors="ignore")
        else:
            ready_text = parsed_body.get_payload(decode=False)

        return ready_text.encode('utf8', errors="ignore").decode('utf8', errors="ignore")

    @staticmethod
    def convert_date_str_to_unixtime(date_str):
        """
        Get Date-header contents and return unixtime by it
        :param date_str:
        :return: int
        """
        if date_str is None:
            return 0

        while date_str.count('  '):
            date_str = date_str.replace('  ', ' ')

        # Tue, 19 Sep 2017 16:42:44 +0300
        if re.match(r"^[A-Za-z]{3}, \d{1,2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2} [\+-]\d{4}$", date_str):
            unixtime = int(time.mktime(datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").timetuple()))
        # Thu, 29 Jan 2015 10:52:53 +0300 (MSK)
        elif re.match(r"^[A-Za-z]{3}, \d{1,2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2} [\+-]\d{4} \(.*\)$", date_str):
            unixtime = int(time.mktime(
                datetime.datetime.strptime(re.sub(r" \(.*\)$", "", date_str), "%a, %d %b %Y %H:%M:%S %z").timetuple()))
        # 12 Jun 2013 09:53:39 -0000
        elif re.match(r"^\d{1,2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2} [\+-]\d{4}$", date_str):
            unixtime = int(time.mktime(datetime.datetime.strptime(date_str, "%d %b %Y %H:%M:%S %z").timetuple()))
        # Mon, 24 Jul 2017 08:08:16 GMT
        elif re.match(r"^[A-Za-z]{3}, \d{1,2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2} [A-Z]{3,4}$", date_str):
            unixtime = int(time.mktime(datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z").timetuple()))
        else:
            raise BaseException("Unknown date format: " + date_str)
        return unixtime

    @staticmethod
    def fetch_mail_from_folder_by_uid(imap, uid, filters_chunk, folder):
        """
        Fetch email from ALREADY selected folder
        :param imap: imaplib.IMAP4
        :param uid: int
        :param filters_chunk: classes.FiltersChunk
        :param folder: nameddict
        :return: classes.Letter
        """
        uid = str(uid)
        result_code, flags_raw = imap.uid('FETCH', uid, '(FLAGS)')
        is_letter_unseen = (str(flags_raw[0]).count('\\Seen') == 0)


        result_code, raw_body = imap.uid('FETCH', uid, '(RFC822)')

        email_charset = ImapTools.detect_internal_mail_encoding_from_bytes(raw_body)
        try:
            parsed_body = email.message_from_string(raw_body[0][1].decode(email_charset, errors='ignore'))
        except TypeError:
            Logger.log_err("Parse letter body error\n" + "\n".join(
                [str(uid), str(folder['id']), str(flags_raw), str(raw_body)]))
            return None
        subject = ImapTools._decode_header(parsed_body['Subject'], email_charset)

        from_name, from_mail = email.utils.parseaddr(parsed_body['From'])
        to_name, to_mail = email.utils.parseaddr(parsed_body['To'])

        from_name = ImapTools._decode_header(from_name, email_charset)
        to_name = ImapTools._decode_header(to_name, email_charset)

        try:
            date = ImapTools.convert_date_str_to_unixtime(parsed_body.get('Date'))
        except BaseException as ex:
            Logger.log_ex(ex, "Failed to parse date {0} uid {1} folder {2}, use 0".format(
                parsed_body.get('Date'), uid, folder['id']))
            date = 0

        body = ""
        attachements = []
        try:
            if parsed_body.get_content_maintype() == 'multipart':  # multipart messages only
                for parsed_body_part in parsed_body.walk():
                    if parsed_body_part.get_content_maintype() == 'multipart':
                        continue

                    if parsed_body_part.get('Content-Disposition') in [None, 'inline'] and \
                            not parsed_body_part.get_filename() and \
                            parsed_body_part.get_content_type().count('text/'):
                        body += ImapTools.decode_email_parsed_body_text(parsed_body_part, email_charset)
                        continue

                    file_name = ImapTools._decode_header(parsed_body_part.get_filename() if
                                                         parsed_body_part.get_filename() else
                                                         "unknown_" + random_md5(), email_charset)
                    attachement = Attachment()
                    attachement.set_ext(file_name[file_name.rfind('.')+1:] if file_name.count('.') else "unknown")
                    attachement.set_file_name(file_name)
                    attachement.set_content(parsed_body_part.get_payload(decode=True))
                    attachement.set_mime_type(parsed_body_part.get('Content-Type').split(";")[0])

                    attachements.append(attachement)
            else:
                body = ImapTools.decode_email_parsed_body_text(parsed_body, email_charset)
        except BaseException as ex:
            Logger.log_ex(ex, "Failed to parse letter uid {0} folder {1}".format(uid, folder['id']))
            return None

        letter = Letter(
            uid=uid,
            _hash="",
            subject=subject,
            from_name=from_name,
            from_mail=from_mail,
            to_name=to_name,
            to_mail=to_mail,
            date=date,
            body=body,
            raw_body=raw_body[0][1],
            attachments=attachements
        )
        letter.set_filters_finds(filters_chunk.run(letter))

        try:
            if is_letter_unseen:
                imap.uid('STORE', uid, '-FLAGS', r'\Seen')
        except BaseException as ex:
            Logger.log_ex(ex, "Flag seen delete, uid {0} folder_id {1}".format(uid, folder['id']))

        return letter

    @staticmethod
    def refresh_filter_results(db, _filter):
        """
        Re-Run filter by all letters in db
        :param db: classes.Database
        :return:
        """

        filters_chunk = FiltersChunk(db, _filter['id'])

        filters_finds = {}
        letters_ids = db.fetch_col("SELECT id FROM letters WHERE when_add <= {0}".format(_filter['when_add']))
        for letter_id in letters_ids:
            filters_finds[letter_id] = filters_chunk.run(Letter.from_db(letter_id, db))

        data_for_mass_insert = []
        for letter_id in filters_finds:
            for filter_find in filters_finds[letter_id]:
                data_for_mass_insert.append(
                    {
                        'letter_id': letter_id,
                        'filter_id': filter_find,
                        'when_add': int(time.time())
                    }
                )
                if len(data_for_mass_insert) % 500 == 0:
                    db.insert_mass("filters_finds", data_for_mass_insert, True)
                    data_for_mass_insert = []

        if len(data_for_mass_insert):
            db.insert_mass("filters_finds", data_for_mass_insert, True)

    @staticmethod
    def get_already_done_uids_of_folder(db, folder_id):
        """
        Return list of already fetched UIDs by filder id
        :param db:
        :param folder_id:
        :return:
        """
        return db.fetch_col("SELECT uid FROM letters WHERE folder_id = {0}".format(folder_id))
