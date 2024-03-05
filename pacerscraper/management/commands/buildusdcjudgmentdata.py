

import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError

# from orders.utils import OrderUtils
from pacerscraper.utils import PacerScraperUtils


class Command(BaseCommand):
    help = 'Populates the database with usdc data from the pacer system using a specified date range'
    # invoke with python manage.py buildbankruptcydata num_days_prior

    def add_arguments(self, parser):
        parser.add_argument('num_days_prior', type=int)

    def handle(self, *args, **options):
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1024, 768))
        display.start()
        start = time.time()
        # model operations
        if options['num_days_prior']:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=options['num_days_prior'])
            date_format_str = '%-m/%-d/%Y'
            to_date_str = to_date.strftime(date_format_str)
            from_date_str = from_date.strftime(date_format_str)
            self.stdout.write(self.style.SUCCESS("Using date range {}, {} for USDC data pull".format(from_date_str, to_date_str)))
            usdc_report_contents = \
                PacerScraperUtils.query_and_archive_judgment_report(from_date_str, to_date_str)
            print("Bankruptcy file generated: {}".format(usdc_report_contents.archive_file))
            PacerScraperUtils.build_judgment_index_report_from_local_file(usdc_report_contents.archive_file)
        executiontime = time.time() - start
        self.stdout.write(self.style.SUCCESS("Done! Total elapsed time: {:.2f} seconds".format(executiontime)))
        display.stop()
