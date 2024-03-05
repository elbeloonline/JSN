

import time

from django.core.management.base import BaseCommand, CommandError

# from orders.utils import OrderUtils
from pacerscraper.utils import PacerScraperUtils


class Command(BaseCommand):
    help = 'Populates the database from the pacer system using a specified date range'

    def add_arguments(self, parser):
        parser.add_argument('from_date', type=str)
        parser.add_argument('to_date', type=str)

    def handle(self, *args, **options):
        start = time.time()
        # model operations
        if options['from_date'] and options['to_date']:
            from_date_str = options['from_date']
            to_date_str = options['to_date']
            judgment_report_contents = \
                PacerScraperUtils.query_and_archive_judgment_report(from_date_str, to_date_str)
            print("Judgment file generated: {}".format(judgment_report_contents.archive_file))
            PacerScraperUtils.build_judgment_index_report_from_local_file(judgment_report_contents.archive_file)
        executiontime = time.time() - start
        self.stdout.write(self.style.SUCCESS("Done! Total elapsed time: {:.2f} seconds".format(executiontime)))
