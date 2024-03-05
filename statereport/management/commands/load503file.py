

from django.core.management.base import BaseCommand, CommandError

from statereport.models import StateReportDataLoader, Debt


class Command(BaseCommand):
    help = 'Loads a 503 file into the database'

    def add_arguments(self, parser):
        parser.add_argument('state_data_file', type=str)

    def handle(self, *args, **options):
        # data_file = "FFSITE.TAPE.Y2010"
        data_file = options['state_data_file']
        loader = StateReportDataLoader(data_file)
        loader.import_file_to_db(num_lines=100000000)  # load everything

        num_debts_loaded = Debt.objects.count()
        # self.assertGreater(num_debts_loaded, 1)
        # print("Number of debts loaded from {}: {}".format(data_file, num_debts_loaded))
        self.stdout.write(self.style.SUCCESS("Total number of debts loaded in file table after parsing file {}: {}"
                                             .format(data_file, num_debts_loaded)))
