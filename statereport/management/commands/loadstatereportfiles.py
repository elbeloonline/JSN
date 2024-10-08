

import logging
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from statereport.models import StateReportDataLoader, Debt
from statereport.models import StateClosingsDataLoader, StateClosingsReport


class Command(BaseCommand):
    help = 'Loads both 501 and 503 files into the database from the email data directory'

    def __init__(self):
        self.data_dir = os.path.join(settings.MEDIA_ROOT, settings.EMAIL_DATA_DIR)
        self.logger = logging.getLogger(__name__)
        self.logger.info('Using {} as the data directory'.format(self.data_dir))
        self.data_file_501 = 'JDC501D'
        self.data_file_503 = 'JDC503D'
        self.data_file_503_weekly = 'JDC0503'

    def generate_file_list(self):
        file_list = []
        for f in os.listdir(self.data_dir):
            if os.path.isfile(os.path.join(self.data_dir, f)):
                if self.data_file_501 in f or self.data_file_503 in f or self.data_file_503_weekly in f.upper():
                    print('Examinig file {}'.format(f))
                    file_list.append(f)
        return file_list

    def process_file_list(self, file_list):
        for f in file_list:
            file_path = os.path.join(self.data_dir, f)
            self.logger.info('Parsing file {}'.format(file_path))
            if self.data_file_501 in f:
                # self.logger.info('Skipping 501 file: {}'.format(f))
                loader = StateClosingsDataLoader(file_path)
                loader.import_file_to_db(num_lines=100000000)  # load everything)
                self.logger.info('Counting objects in Closings table')
                num_closings = StateClosingsReport.objects.count()
                self.logger.info('Closings table now contains {} objects'.format(num_closings))
                os.remove(file_path)

            elif self.data_file_503 in f or self.data_file_503_weekly in f.upper():
                loader = StateReportDataLoader(file_path)
                loader.import_file_to_db(num_lines=100000000)  # load everything
                self.logger.info('Counting objects in Debts table')
                num_debts_loaded = Debt.objects.count()
                self.logger.info('Debts table now contains {} objects'.format(num_debts_loaded))
                os.remove(file_path)

    def handle(self, *args, **options):
        file_list = self.generate_file_list()
        self.process_file_list(file_list)

