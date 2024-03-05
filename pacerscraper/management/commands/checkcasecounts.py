

import time

from django.core.management.base import BaseCommand, CommandError
from pacerscraper.models import PacerBankruptcyIndexCase

# from orders.utils import OrderUtils
from pacerscraper.utils import PacerScraperValidator


class Command(BaseCommand):
    help = 'Populates the database from the pacer system using a specified date range'
    # python manage.py checkcasecounts 2017-01-01 2017-01-31 0f5ba5ec-238d-4ff1-b0b4-6de512dbf58f.html

    def add_arguments(self, parser):
        parser.add_argument('from_date', type=str)
        parser.add_argument('to_date', type=str)
        parser.add_argument('case_file', type=str)

    def handle(self, *args, **options):
        start = time.time()
        # model operations
        if options['from_date'] and options['to_date']:
            from_date_str = options['from_date']
            to_date_str = options['to_date']
            index_cases = PacerBankruptcyIndexCase.objects\
                .filter(date_filed__gte=from_date_str)\
                .filter(date_filed__lte=to_date_str)
            case_file_str = options['case_file']
            file_case_count = PacerScraperValidator.check_index_file_case_count(case_file_str)
            print("Cases found in database and in index file: {} vs {}"
                  .format(index_cases.count(), file_case_count))
