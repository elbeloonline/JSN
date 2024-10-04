# from django.test import TestCase
from io import StringIO
import mock
import os
import unittest

from orders.models import Client

# Create your tests here.
class QBClientTestCase(unittest.TestCase):

    def setUp(self):
        import os
        from django.conf import settings
        self.accounts_file = os.path.join(settings.MEDIA_ROOT, 'accounts.csv')

    def test_model_client(self):
        client_mock = mock.Mock(spec=Client)
        client_mock.client_id = '000-2201-211'
        client_mock.client_name = 'Main Street Title'
        # client_mock.client_id = self.quickbooks_csv[0][0]
        # client_mock.client_name = self.quickbooks_csv[0][1]
        self.assertEqual(Client.__str__(client_mock), 'Main Street Title')

    def test_qb_sync_file_format(self):
        import csv
        csv_filename = self.accounts_file
        with open(csv_filename,'r') as csvfile:
            qb_account_reader = csv.reader(csvfile)
            row = next(qb_account_reader)
            self.assertEqual(len(row), 2)

    def test_qb_sync_find_file(self):
        from django.conf import settings
        from orders.utils import OrderUtils
        csv_filename = os.path.join(settings.MEDIA_ROOT, self.accounts_file)
        self.assertTrue(os.path.isfile(csv_filename), True)



