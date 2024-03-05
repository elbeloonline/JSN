

from datetime import datetime, timedelta
import time

from django.core.management.base import BaseCommand, CommandError

# from orders.utils import OrderUtils
from pacerscraper.utils import PacerScraperBankruptcyUtils


class Command(BaseCommand):
    help = 'Populates the BK database from the pacer system using a date range going back to num_days_prior from today'
    # invoke with python manage.py buildbankruptcydata num_days_prior

    def add_arguments(self, parser):
        parser.add_argument('--num_days_prior', type=int)
        parser.add_argument('--date_from', type=str)
        parser.add_argument('--date_to', type=str)

    def handle(self, *args, **options):
        from pyvirtualdisplay import Display
        from django.conf import settings

        display = None
        from_date_str = None
        to_date_str = None
        if 'gunicorn' in settings.INSTALLED_APPS:
            running_local = False
        else:
            running_local = True
        if not running_local:
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
            self.stdout.write(self.style.SUCCESS("Using date range {}, {} for bankruptcy data pull".format(from_date_str, to_date_str)))
        elif options['date_from'] and options['date_to']:
            from_date_str = options['date_from']
            to_date_str = options['date_to']
        else:
            executiontime = time.time() - start
            self.stdout.write(self.style.SUCCESS("Done! Total elapsed time: {:.2f} seconds".format(executiontime)))
            exit(1)
        bankruptcy_report_contents = \
            PacerScraperBankruptcyUtils.query_and_archive_bankruptcy_report(from_date_str, to_date_str)
        print("Bankruptcy file generated: {}".format(bankruptcy_report_contents.archive_file))
        PacerScraperBankruptcyUtils.build_bankruptcy_index_report_from_local_file(bankruptcy_report_contents.archive_file)

        executiontime = time.time() - start
        self.stdout.write(self.style.SUCCESS("Done! Total elapsed time: {:.2f} seconds".format(executiontime)))
        if not running_local:
            display.stop()
