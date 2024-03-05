

import time

from django.core.management.base import BaseCommand, CommandError
from pacerscraper.models import PacerJudgmentIndexCase

from pacerscraper.utils import PacerScraperUtils


class Command(BaseCommand):
    help = 'Populates the usdc tables party index with names so that it is searchable in database'
    # python manage.py checkcasecounts 2017-01-01 2017-01-31 0f5ba5ec-238d-4ff1-b0b4-6de512dbf58f.html

    def handle(self, *args, **options):
        import os
        import logging
        from django.conf import settings
        from django.db import transaction
        logger = logging.getLogger(__name__)

        start = time.time()
        pacer_files_dir = PacerScraperUtils.pacer_files_dir
        # model operations
        from pacerscraper.utils import PacerScraperUSDCPartyBuilder
        case_limit = 1000000
        party_index_limit = 128
        # cases = PacerBankruptcyIndexCase.objects.filter(party_file_processed='N')[:case_limit]
        # cases = PacerJudgmentIndexCase.objects.using(settings.USDCSEARCH_DB).filter(party_file_processed='N')[:case_limit]
        # only need the local instance here
        cases = PacerJudgmentIndexCase.objects.filter(party_file_processed='N')[:case_limit]
        # cases = PacerJudgmentIndexCase.objects.filter(party_file_processed='N')\
        #             .exclude(id=10013)[:case_limit]
        logger.info('Matched {} cases.'.format(len(cases)))
        logger.info('Using {} for data directory'.format(pacer_files_dir))
        # webdriver = psutils.load_local_bankruptcy_report(party_file)
        webdriver = PacerScraperUtils.get_webdriver()
        i = 0
        for case in cases:
            # # @TODO: add aliases
            # print(party_list[0].party_name)
            # print(case.party_file)
            if os.path.exists(os.path.join(pacer_files_dir, case.party_file)):
                # print('Found party file for case {}'.format(case))
                logger.info('Found party file for case {}'.format(case))
                party_list = PacerScraperUSDCPartyBuilder.\
                    build_party_list_from_party_file(case.party_file, webdriver)
                # print("Party list scraped from file: {}".format(party_list))
                with transaction.atomic():
                    for party in party_list:
                        logger.info('Saving case {} to db'.format(case.case_number))
                        PacerScraperUSDCPartyBuilder.save_usdc_party(case, party)
                    # now update the case once ALL parties have been processed
                    case.party_file_processed = 'Y'
                    case.save(using=settings.USDCSEARCH_DB)
            # else:
                # print("Couldn't find case file: {}".format(case.party_file))
            i += 1
            if i % party_index_limit == 0:
                webdriver.close()
                # webdriver = None
                webdriver = PacerScraperUtils.get_webdriver()

