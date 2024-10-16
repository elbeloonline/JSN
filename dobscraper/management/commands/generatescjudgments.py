

import logging
import time
import os

from selenium import webdriver

from django.conf import settings
from django.core.management.base import BaseCommand

from dobscraper.models import ScnjDebtorDob

# from pacerscraper.utils import PacerScraperBankruptcyUtils, PacerScraperPartyBuilder

class Command(BaseCommand):
    help = 'Populates the SCNJ DoB table based on missing judgments'
    # python manage.py checkcasecounts 2017-01-01 2017-01-31 0f5ba5ec-238d-4ff1-b0b4-6de512dbf58f.html

    # def __init__(self, *args, **kwargs):
    #     super(Command, self).__init__(*args, **kwargs)
    #     gecko_path = os.path.join(str(settings.ROOT_DIR), 'bin', 'geckodriver')
    #     self.browser = webdriver.Firefox(executable_path=gecko_path)
    #
    # def __del__(self):
    #     self.browser.quit()

    def handle(self, *args, **options):
        from dobscraper.helpers import NameIdentifierManager, JudgmentsManager, DobScraperManager
        start_time = time.time()

        party_names = NameIdentifierManager.get_common_names()
        name_idx = 0
        party_judgments = JudgmentsManager.get_judgments_for_single_name(party_names, name_idx)
        new_judgments_filename = os.path.join(settings.MEDIA_ROOT, "dob_judgments_list.csv")
        JudgmentsManager.write_case_judgments(party_judgments, new_judgments_filename)

        end_time = time.time()
        logging.info('Done!')


    # def _orm_bulk_create(self, n_records):
    #     """
    #     Bulk insert a list of
    #
    #     :param n_records: list of MatchedDebtor
    #     :return:
    #     """
    #     instances = [
    #         ScnjDebtorDob(
    #             case_number=x.judgment_num,
    #             dob=x.dob,
    #             name=x.debtor_name,
    #         )
    #         for x in n_records
    #     ]
    #     ScnjDebtorDob.objects.bulk_create(instances)
