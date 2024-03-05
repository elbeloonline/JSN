

from django.core.management.base import BaseCommand, CommandError

from patriot.models import PatriotImport


class Command(BaseCommand):
    help = 'Imports Patriot data into system from source XML file'

    # def add_arguments(self, parser):
    #     parser.add_argument('quickbooks_csv_file', type=str)

    def handle(self, *args, **options):
        pd_import = PatriotImport()
        names_processed = pd_import.import_data()

        self.stdout.write(self.style.SUCCESS("Total number of names synchronized: {}"
                                             .format(names_processed)))
