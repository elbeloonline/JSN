

import time

from django.core.management.base import BaseCommand, CommandError
from pacerscraper.utils import PacerScraperLive


class Command(BaseCommand):
    help = 'Scrape the pacer system in real time for a given name'

    def handle(self, *args, **options):
        # firstname = 'James'  # multiple matches
        # lastname = 'Kim'
        # firstname = 'Austin'  # no match
        # lastname = 'Fisher'
        firstname = 'Benita'  # one match
        lastname = 'Vasquez'

        start = time.time()
        psl = PacerScraperLive()
        matched_cases = psl._scrape_live_name(firstname, lastname)
        executiontime = time.time() - start
        print(matched_cases)

        self.stdout.write(self.style.SUCCESS("Done! Total elapsed time: {:.2f} seconds".format(executiontime)))
