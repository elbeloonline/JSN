

import logging
import time

from django.core.management.base import BaseCommand, CommandError

# from orders.utils import OrderUtils
from pacerscraper.utils import PacerScraperUtils


class Command(BaseCommand):
    help = 'Generates a report of the bankruptcy case counts in the system versus what was scraped'
    # date format YYYY-MM-DD

    def add_arguments(self, parser):
        parser.add_argument('from_date', type=str)
        parser.add_argument('to_date', type=str)

    def handle(self, *args, **options):

        logger = logging.getLogger(__name__)
        start = time.time()
        # model operations
        if options['from_date'] and options['to_date']:
            validator = BankruptcyDataValidation()
            bk_index_files = validator.build_case_file_list(options)
            # logger.info('Found matching files {}'.format(bk_index_files))
            validator.get_case_counts(bk_index_files)
        # logger.info("Generated dictionary: {}".format(bk_index_files))
        BankruptcyDataValidation.print_csv(bk_index_files)

        executiontime = time.time() - start
        self.stdout.write(self.style.SUCCESS("Done! Total elapsed time: {:.2f} seconds".format(executiontime)))

# --------

class BankruptcyDataValidation:

    def __init__(self):
        pass

    @staticmethod
    def print_csv(bk_index_files):
        """
        Print a CSV-friendly list of case count/date info
        :param bk_index_files: dict of case count info
        """
        for key, case_count_data in bk_index_files.items():
            # from_date = case_count_data[0]
            # to_date = case_count_data[1]
            # count = case_count_data[2]
            from_date = case_count_data.get('from_date')
            to_date = case_count_data.get('to_date')
            nj_count = case_count_data.get('count')
            local_count = case_count_data.get('local_db_count')
            print("{},{},{},{}".format(from_date, to_date, nj_count, local_count))

    def get_case_counts(self, bk_index_file_dict):
        """
        Return a dict of file case counts
        :param index_file_list: list of files on the system with case index data
        :return: None
        """
        # type: (Dict[List]) -> None
        case_count_dict = {}
        for bk_index_file, value in bk_index_file_dict.items():
            case_count = self.get_case_count_from_file(bk_index_file)
            # value.append(case_count)  # make a betterdata struct
            value['count'] = case_count
            case_count_dict[bk_index_file] = value

    def get_case_count_from_file(self, filename):
        """
        Scrape the number of cases found in the judicial system from the file
        :param filename: name of the file to parse
        :return: number of reported cases
        """
        # type: int
        from pacerscraper.utils import PacerScraperValidator

        file_case_count = PacerScraperValidator.check_index_file_case_count(filename)
        return file_case_count

    def build_case_file_list(self, options):
        """
        Search across all instances to build a list of scraped index case files
        :param options: command line options with from and to date
        :return: filenames of matched bankruptcy cases per scraping operation
        """
        # type: (Dict[str]) -> str
        from django.conf import settings

        from_date_str = options['from_date']
        to_date_str = options['to_date']

        search_dbs = [settings.NAMESEARCH_DB, settings.BKSEARCH_DB2, settings.BKSEARCH_DB3, settings.BKSEARCH_DB4]
        # search_dbs = [settings.BKSEARCH_DB2]
        bk_index_files_dict = {}
        for db_instance in search_dbs:
            matches = self.get_bankruptcy_index_file(from_date_str, to_date_str, db_instance)
            for key, match in matches.items():
                # grab the number of records in the db too
                indexed_case_count = self.get_local_bk_case_counts(match['from_date'],
                                                                   match['to_date'],
                                                                   db_instance)
                match['local_db_count'] = indexed_case_count
                bk_index_files_dict[key] = match
        return bk_index_files_dict

    def get_local_bk_case_counts(self, from_date, to_date, db):
        from pacerscraper.models import PacerBankruptcyIndexCase

        # PacerBankruptcyIndexCase.objects.using(db).filter()
        sql = """
        select idx_case.id
        from pacerscraper_bankruptcyindexreport idx_report, pacerscraper_pacerbankruptcyindexcase idx_case
        where idx_case.bankruptcy_index_report_id = idx_report.id
        and idx_report.date_from = %s
        and idx_report.date_to = %s
        """
        case_matches = PacerBankruptcyIndexCase.objects.using(db).raw(sql, [from_date, to_date])
        return len(list(case_matches))

    def get_bankruptcy_index_file(self, from_date, to_date, db):
        """
        Return a list of the physical file names used to build case data during scraping operation
        :param from_date: Date to search from
        :param to_date: Date to search to
        :param db the database instance to use
        :return: filenames of matched bankruptcy cases per scraping operation
        """
        # type: (str, str, str) -> List[str]
        from pacerscraper.models import BankruptcyIndexReport
        from django.db.models import Count
        sql = "select * from pacerscraper_bankruptcyindexreport " + \
              "where date_from >= %s " + \
              "and date_to <= %s " + \
              "GROUP BY date_from, date_to"

        report_matches = BankruptcyIndexReport.objects.using(db).raw(sql, [from_date, to_date])
        index_files_dict = {}
        for report_match in report_matches:  # type: BankruptcyIndexReport
            date_dict = {'from_date': report_match.date_from, 'to_date': report_match.date_to}
            # date_list = [report_match.date_from, report_match.date_to]
            index_files_dict[report_match.archive_file] = date_dict
        return index_files_dict
