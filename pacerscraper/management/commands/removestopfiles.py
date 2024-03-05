

import time

from django.core.management.base import BaseCommand, CommandError

# from orders.utils import OrderUtils
from pacerscraper.utils import PacerScraperBase


class Command(BaseCommand):
    help = 'Removes the istop file before scraping from Pacer websit'

    def handle(self, *args, **options):
        # model operations
        PacerScraperBase.remove_stop_files()
