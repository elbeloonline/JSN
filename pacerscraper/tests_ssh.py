# from django.conf import settings
from django.test import TestCase

import paramiko

from .utils import SSHManager

# Create your tests here.


class ScraperTestCase(TestCase):

    def setUp(self):
        self.k = paramiko.RSAKey.from_private_key_file("/Users/kwan/Desktop/Dropbox/local/Projects/JSNetwork/bitnami-aws-879738187445.pem")
        self.c = paramiko.SSHClient()
        self.c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("connecting")
        self.c.connect(hostname="ec2-34-226-215-155.compute-1.amazonaws.com", username="bitnami", pkey=self.k)
        print("connected")

    def test_generic_connect(self):
        # commands = ["/home/ubuntu/firstscript.sh", "/home/ubuntu/secondscript.sh"]
        commands = ["ls -aFl"]
        for command in commands:
            print("Executing {}".format(command))
            stdin, stdout, stderr = self.c.exec_command(command)
            print(stdout.read())
            print("Errors")
            print(stderr.read())
        self.c.close()

    def test_get_file_contents(self):
        # https://stackoverflow.com/questions/1596963/read-a-file-from-server-with-ssh-using-python
        import os
        from pacerscraper.utils import SSHManager
        filename = "fffd91a9-88c9-4a70-87b7-e1e605d724fe.html"
        file_dir = "/opt/bitnami/apps/django/django_projects/jsnetwork_project/jsnetwork_project/media/pacer_bankruptcy_idx"
        file_path = os.path.join(file_dir, filename)
        remote_file_contents = SSHManager.get_file_contents_from_ssh(self.c, file_path)
        # print(remote_file_contents)
        self.assertGreater(len(remote_file_contents), 0)

    def test_parse_party_file_details(self):
        import os
        from pacerscraper.utils import SSHManager, PacerScraperUtils, PacerScraperBase
        filename = "fffd91a9-88c9-4a70-87b7-e1e605d724fe.html"
        file_dir = "/opt/bitnami/apps/django/django_projects/jsnetwork_project/jsnetwork_project/media/pacer_bankruptcy_idx"
        file_path = os.path.join(file_dir, filename)
        remote_file_contents = SSHManager.get_file_contents_from_ssh(self.c, file_path)

        # parse files
        import tempfile
        fd, tmp_file_path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.write(remote_file_contents)
            browser = PacerScraperUtils.load_local_judgment_report(tmp_file_path)
            tmp_text = browser.find_element_by_css_selector("table tbody tr td:nth-of-type(3)").text
            print(tmp_text)
        finally:
            os.remove(tmp_file_path)
        self.assertGreater(len(tmp_text), 0)

    def test_parse_party_file_details2(self):
        import os
        import tempfile
        from pacerscraper.utils import SSHManager, PacerScraperUtils, ReportHelper

        filename = "fffd91a9-88c9-4a70-87b7-e1e605d724fe.html"
        file_dir = "/opt/bitnami/apps/django/django_projects/jsnetwork_project/jsnetwork_project/media/pacer_bankruptcy_idx"
        file_path = os.path.join(file_dir, filename)
        remote_file_contents = SSHManager.get_file_contents_from_ssh(self.c, file_path)
        # parse data needed from files
        fd, tmp_file_path = tempfile.mkstemp()
        # party_details = []
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.write(remote_file_contents)
            browser = PacerScraperUtils.load_local_judgment_report(tmp_file_path)
            tbody_element = browser.find_element_by_css_selector("table tbody")
            rows = tbody_element.find_elements_by_tag_name('tr')
            for row in rows:
                party_cell = row.find_elements_by_tag_name('td')[0]
                if '(Debtor)' in party_cell.text:
                    # print(party_cell.text)
                    party_details = ReportHelper.parse_debtor_details(row)
                    print(party_details)
        finally:
            os.remove(tmp_file_path)
