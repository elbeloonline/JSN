

import logging
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from emailfetcher.email_fetcher import EmailFetcher


class Command(BaseCommand):
    help = 'Pulls emails from the judgment search data account and decompresses any zip files found'

    def __init__(self):
        self.data_dir = os.path.join(settings.MEDIA_ROOT, settings.EMAIL_DATA_DIR)
        self.logger = logging.getLogger(__name__)
        self.logger.info('Using {} as the data directory'.format(self.data_dir))

    def add_arguments(self, parser):
        parser.add_argument('num_emails_to_fetch', type=int)

    def handle(self, *args, **options):
        num_emails = options['num_emails_to_fetch']
        em = EmailFetcher()
        em.fetch_emails(debug=False, num_emails_to_parse=num_emails)


