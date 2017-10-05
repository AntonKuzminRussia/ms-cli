# -*- coding: utf-8 -*-
"""
Mail worker`s thread. Collect mail, refresh folders, etc. All work with mail.
"""

import time
import imaplib
import threading

from classes.ImapTools import ImapTools
from classes.FiltersChunk import FiltersChunk
from classes.Logger import Logger


class MailWorkerThread(threading.Thread):
    """
    Mail worker`s thread. Collect mail, refresh folders, etc. All work with mail.
    """
    db = None
    account_data = None
    daemon = True
    done = False
    filters_chunk = None
    LETTER_GET_REPEATS_LIMIT = 5

    def __init__(self, db, account_data):
        """
        :param db classes.Database:
        :param account_data nameddict:
        """
        threading.Thread.__init__(self)

        self.db = db
        self.account_data = account_data
        self.filters_chunk = FiltersChunk(self.db)

        self.db.update("accounts", {"in_work": 1}, "id = {0}".format(account_data['id']))

    def get_letter(self, imap, uid, folder, repeat_counter=0):
        """
        Get concrete letter by UID and folder. Repeat some counts (self.LETTER_GET_REPEATS_LIMIT) if
        connection problems exists
        :param imap: imaplib.IMAP4
        :param uid: int
        :param folder: nameddict
        :param repeat_counter: int
        :return:
        """
        if repeat_counter >= self.LETTER_GET_REPEATS_LIMIT:
            Logger.log_err("UID {0} from folder {1}/{2} can`t be fetched".format(
                uid, folder['id'], folder['full_name']))
            return None

        try:
            Logger.log_info(
                "Start fetch uid {0} from {1}/{2}/{3}/{4}".format(uid, folder['id'], folder['full_name'],
                                                                  self.account_data['host'],
                                                                  self.account_data['login']))
            letter = ImapTools.fetch_mail_from_folder_by_uid(imap, int(uid), self.filters_chunk, folder)

            if letter is not None:
                letter.flush_to_db(self.db, folder['id'])
                Logger.log_info("Successfully fetched uid {0} from {1}/{2}/{3}/{4}".format(
                    uid, folder['id'], folder['full_name'], self.account_data['host'], self.account_data['login']))
        except imaplib.IMAP4.abort:
            time.sleep(3)
            return self.get_letter(imap, uid, folder, repeat_counter+1)

    def run(self):
        try:
            imap = imaplib.IMAP4_SSL(self.account_data['host']) if \
                int(self.account_data['ssl']) else \
                imaplib.IMAP4(self.account_data['host'])
            imap.login(self.account_data['login'], self.account_data['password'])
        except imaplib.IMAP4.error as ex:
            if str(ex).count('AUTHENTICATIONFAILED') or str(ex).count('Invalid login or password'):
                self.db.update("accounts", {'active': 0}, "id = {0}".format(self.account_data['id']))
                Logger.log_err(
                    "Auth failed for {0}/{1} disable it".format(
                        self.account_data['host'], self.account_data['login']))
            else:
                Logger.log_ex(
                    ex, "Account {0}/{1}".format(
                        self.account_data['host'], self.account_data['login']))

            self.db.insert("accounts_errors",
                           {"account_id": self.account_data['id'], "error": str(ex), "when_add": int(time.time())})
            try:
                imap.close()
            except BaseException:
                pass

            return

        last_uid = 0
        try:
            ImapTools.refresh_account_folders_list(self.db, imap, self.account_data['id'])
            Logger.log_info("Folders list for {0}/{1} successfully refreshed".format(
                self.account_data['host'], self.account_data['login']))

            common_count = 0
            folders = self.db.fetch_all("SELECT * FROM folders WHERE account_id = {0} AND removed = 0".format(
                self.account_data['id']))
            for folder in folders:
                uids = ImapTools.get_all_letters_uids_from_folder(imap, folder)
                already_done_uids = ImapTools.get_already_done_uids_of_folder(self.db, folder['id'])

                for uid in uids:
                    if int(uid) not in already_done_uids:
                        last_uid = uid
                        self.get_letter(imap, uid, folder)
                        common_count += 1

                self.db.update("folders", {'last_checked': int(time.time())}, "id = {0}".format(folder['id']))

            Logger.log_info("Mail refresh for {0}/{1} done, {2} letters loaded".format(
                self.account_data['host'], self.account_data['login'], common_count))

            self.db.update(
                "accounts",
                {'last_checked': int(time.time()), 'in_work': '0'},
                "id = {0}".format(self.account_data['id'])
            )
        except BaseException as ex:
            Logger.log_ex(
                ex, "Mail fetch process exception of {0}/{1}/{2}".format(
                    self.account_data['host'], self.account_data['login'], last_uid))

        Logger.log_info("Start update attachments types/exts")
        self.update_attachments_txts()
        Logger.log_info("Done update attachments types/exts")

        self.done = True

        self.db.close()

    def update_attachments_txts(self):
        """
        Method update ext`s and unknown attachments by mime-type info
        :return:
        """
        mime_types = self.db.fetch_pairs(
            "SELECT DISTINCT mime_type, ext FROM `attachments` WHERE ext <> 'unknown'") #type: dict
        unknown_attachments = self.db.fetch_all("SELECT * FROM `attachments` WHERE LOCATE('.', file_name) = 0")

        for unknown_attachment in unknown_attachments:
            if unknown_attachment['mime_type'] in mime_types.keys():
                self.db.q(
                    "UPDATE attachments SET ext = {0}, file_name = CONCAT(file_name, '.', {0}) "
                    "WHERE id = {1}".format(
                        self.db.quote(mime_types[unknown_attachment['mime_type']]),
                        unknown_attachment['id']
                    )
                )
