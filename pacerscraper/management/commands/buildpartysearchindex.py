

import time

from django.core.management.base import BaseCommand, CommandError
from pacerscraper.models import PacerBankruptcyIndexCase

from pacerscraper.utils import PacerScraperBankruptcyUtils, PacerScraperPartyBuilder


class Command(BaseCommand):
    help = 'Populates the party index with names so that it is searchable in database'
    # python manage.py checkcasecounts 2017-01-01 2017-01-31 0f5ba5ec-238d-4ff1-b0b4-6de512dbf58f.html

    def handle(self, *args, **options):
        import os
        import logging
        from django.conf import settings
        logger = logging.getLogger(__name__)

        start = time.time()
        bankruptcy_files_dir = PacerScraperBankruptcyUtils.bankruptcy_files_dir
        # model operations
        from pacerscraper.utils import PacerScraperPartyBuilder
        case_limit = 256
        party_index_limit = 64
        cases = PacerBankruptcyIndexCase.objects.filter(party_file_processed='N')[:case_limit]
        logger.info('Matched {} cases.'.format(len(cases)))
        logger.info('Using {} for data directory'.format(bankruptcy_files_dir))
        # webdriver = psutils.load_local_bankruptcy_report(party_file)
        i = 0
        try:
            webdriver = PacerScraperBankruptcyUtils.get_webdriver()
            for case in cases:
                # # @TODO: add aliases
                # print(party_list[0].party_name)
                # print(case.party_file)
                if os.path.exists(os.path.join(bankruptcy_files_dir, case.party_file)):
                    # print('Found party file for case {}'.format(case))
                    logger.info('Found party file for case {}'.format(case))
                    PacerScraperPartyBuilder.archive_file_dir = bankruptcy_files_dir
                    party_list = PacerScraperPartyBuilder.\
                        build_party_list_from_party_file(case.party_file, webdriver)
                    # print("Party list scraped from file: {}".format(party_list))
                    for party in party_list:
                        PacerScraperPartyBuilder.save_bankruptcy_party(case.case_number, party)
                # else:
                    # print("Couldn't find case file: {}".format(case.party_file))
                i += 1
                if i % party_index_limit == 0:
                    webdriver.close()
                    # webdriver = None
                    webdriver = PacerScraperBankruptcyUtils.get_webdriver()
        finally:
            webdriver.close()

