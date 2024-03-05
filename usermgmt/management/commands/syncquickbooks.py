

from django.core.management.base import BaseCommand, CommandError

from orders.utils import OrderUtils


class Command(BaseCommand):
    help = 'Syncs a csv file exported from Quickbooks using the qodbc.py script to extract data'

    # def add_arguments(self, parser):
    #     parser.add_argument('quickbooks_csv_file', type=str)

    def handle(self, *args, **options):
        # data_file = "FFSITE.TAPE.Y2010"
        # data_file = options['quickbooks_csv_file']
        rows_processed = OrderUtils.sync_qb_clients()

        self.stdout.write(self.style.SUCCESS("Total number of accounts synchronized: {}"
                                             .format(rows_processed)))
