

from django.core.management.base import BaseCommand, CommandError

# from orders.utils import OrderUtils
from pacerscraper.utils import PacerScraperUtils


class Command(BaseCommand):
    help = 'Syncs a csv file exported from Quickbooks using the qodbc.py script to extract data'

    # def add_arguments(self, parser):
    #     parser.add_argument('quickbooks_csv_file', type=str)

    def handle(self, *args, **options):
        archive_file = '/Applications/djangostack-1.10.2-0/apps/django/django_projects/jsnetwork_project/jsnetwork_project/media/pacer_judgment_idx/868f5236-cf8c-4762-a810-5e517c67a3a5.html'
        PacerScraperUtils.build_judgment_index_report_from_local_file(archive_file)
        self.stdout.write(self.style.SUCCESS("Done!"))
