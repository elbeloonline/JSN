from django.test import TestCase
from .email_fetcher import EmailFetcher

class EmailFetcherTest(TestCase):

    def test_fetch_single_email(self):
        em = EmailFetcher()
        em.fetch_emails(debug=True, num_emails_to_parse=1)
