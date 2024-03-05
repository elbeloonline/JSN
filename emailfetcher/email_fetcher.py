
# coding: utf-8

# In[5]:

#!/usr/bin/env python

import os
import imaplib
import email
import logging
import uuid
import re

from django.conf import settings


class EmailFetcher:

    def __init__(self):
        self.data_dir = os.path.join(settings.MEDIA_ROOT, settings.EMAIL_DATA_DIR)
        self.logger = logging.getLogger(__name__)
        self.files_processed = []
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def __del__(self):
        # self.M.close()
        self.M.logout()

    def login(self):
        fetch_mail_server = settings.FETCH_MAIL_SERVER
        M = imaplib.IMAP4_SSL(fetch_mail_server)
        try:
            mail_login = settings.MAIL_LOGIN
            mail_password = settings.MAIL_PASSWORD
            M.login(mail_login, mail_password)
        except imaplib.IMAP4.error:
            self.logger.error("LOGIN FAILED!!! ")
            exit(1)
            # ... exit or deal with failure...
        self.logger.info("Login success!")
        self.M = M

    def list_mailboxes(self):
        rv, mailboxes = self.M.list()
        if rv == 'OK':
            self.logger.debug("Mailboxes:")
            self.logger.debug(mailboxes)

    def parse_uid(self, data):
        pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')
        match = pattern_uid.match(data)
        return match.group('uid')

    def do_archive_msg(self, msg_uid, debug=False):
        archive_folder = settings.EMAIL_ARCHIVE_FOLDER
        result = self.M.uid('COPY', msg_uid, archive_folder)
        if not debug:
            if result[0] == 'OK':
                # not needed for gmail, but probably so for everything else
                mov, data = self.M.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
                self.M.expunge() # gmail does this automatically when you move to Trash
                self.logger.info("Message archived")

    def process_mailbox(self, max_emails_to_parse=0, debug=False):
        M = self.M
        weekly_report_subject = 'Weekly Judgement Reports'
        iter_counter = 0
        rv, data = M.select("INBOX")
        if rv == 'OK':
            self.logger.info("Processing mailbox...")
            rv, data = M.search(None, "ALL")
            if rv != 'OK':
                self.logger.info("No messages found!")
                return
        msg_count = len(data[0].rsplit())
        if max_emails_to_parse == 0:
            max_emails_to_parse = msg_count
        for num in data[0].rsplit():
            if iter_counter >= max_emails_to_parse:
                break
            else:
                iter_counter+=1
            rv, data = M.fetch(num, '(UID)') # for archival
            msg_uid = self.parse_uid(data[0])
            rv, data = M.fetch(num, '(RFC822)') # for attachments
            if rv != 'OK':
                self.logger.info("ERROR getting message {}".format(num))
                return
            msg = email.message_from_string(data[0][1])
            if weekly_report_subject in msg['Subject']:
                # print(msg)
                self.logger.info('Message {}: {} - Date:{}'.format(num, msg['Subject'], msg['Date']))
                counter = 1
                for part in msg.walk():
                    # multipart/* are just containers
                    if part.get_content_maintype() == 'multipart':
                        continue
                    filename = part.get_filename() # @TODO: generate a unique filename
                    if filename:
                        ext = os.path.splitext(filename)[1]
                        if os.path.exists( os.path.join(self.data_dir, filename) ): # rename file
                            filename = str(uuid.uuid4()) + ext
                        filename = filename.replace(' ','_')  # no spaces in filename
                        if ext not in ('.gif', '.png', '.jpg'):
                            fp = open(os.path.join(self.data_dir, filename), 'wb')
                            fp.write(part.get_payload(decode=True))
                            fp.close()
                            self.files_processed.append(filename)
            self.do_archive_msg(msg_uid, debug=debug)

    def clean_dirs(self):
        for f in os.listdir(self.data_dir):
            if os.path.isfile(os.path.join(self.data_dir, f)) and '.txt' not in f:
                os.remove(os.path.join(self.data_dir, f))

    def list_messages(M):
        pass

    def decompress_files(self):
        import zipfile
        for file_name in self.files_processed:
            zip_file_path = os.path.join(settings.MEDIA_ROOT, self.data_dir, file_name)
            if zipfile.is_zipfile(zip_file_path):
                with zipfile.ZipFile(zip_file_path) as zf:
                    for target_file in zf.namelist():
                        target_name = file_name + '_' + target_file
                        target_path = os.path.join(settings.MEDIA_ROOT, self.data_dir, target_name)
                        with open(target_path, 'w') as nf:
                            fdata = zf.read(target_file)
                            fdata = fdata.decode('cp1252').encode('utf-8')
                            nf.write(fdata)
            os.remove(zip_file_path)
            self.logger.info('Decompressed file from {}'.format(file_name))

    def fetch_emails(self, debug=False, num_emails_to_parse=5):
        self.clean_dirs()
        self.login()
        self.process_mailbox(num_emails_to_parse, debug=debug)
        self.logger.info('Files saved during this operation: {}'.format(self.files_processed) )
        self.decompress_files()
