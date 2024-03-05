import collections
import logging

from django.conf import settings

from dobscraper.models import ScnjDebtorDob
from dobscraper.scnjscraper import SCNJScraper
from statereport.models import Party


PartyName = collections.namedtuple('PartyName', 'last_name first_name')
JudgmentNumberData = collections.namedtuple('JudgmentNumberData', 'docketed_judg_num formatted_judg_num')


class NameIdentifierManager:

    @staticmethod
    def get_common_names():
        """
        Opens the top_scnj_names_reader.csv file to
        :return: list of PartyName objects last and first names
        """
        import csv

        party_names = []
        csv_filename = settings.MEDIA_ROOT + '/' + 'top-500-scnj-names.csv'
        with open(csv_filename,'r') as csvfile:
            top_scnj_names_reader = csv.reader(csvfile)
            for row in top_scnj_names_reader:
                _, party_last_name, party_first_name = row
                party_names.append(PartyName(party_last_name, party_first_name))
        return party_names


class JudgmentsManager:

    @staticmethod
    def get_judgments_for_single_name(party_list, idx_in_list=0):
        """
        Get the list of judgments from the system based on a name in the list of supplied names
        Uses the first name at index 0 if none supplied
        :return: List of JudgmentNumberData
        """
        if not party_list:
            return
        pname = party_list[idx_in_list]  # type: PartyName
        inner_qs = ScnjDebtorDob.objects.values_list('judgment_number',flat=True)
        # https://stackoverflow.com/questions/14105660/select-values-which-not-in-another-table-with-django
        queryset_judgments = Party.objects.filter(party_last_name=pname.last_name,
                                                  party_first_name=pname.first_name).exclude(docketed_judgment_number__in=inner_qs)
        search_name = "{}, {}".format(pname.last_name, pname.first_name)
        logging.info('Matched {} objects for name {}'.format(len(queryset_judgments), search_name))
        judgment_list = []
        for judgment in queryset_judgments:
            jud_num = '{}-{}-{}'.format(judgment.docketed_judgment_type_code,
                                        judgment.docketed_judgment_seq_num,
                                        judgment.docketed_judgment_year)
            # judgment_list.append(judgment.docketed_judgment_number)
            jud_data = JudgmentNumberData(docketed_judg_num=judgment.docketed_judgment_number, formatted_judg_num=jud_num)
            judgment_list.append(jud_data)
        return judgment_list

    @staticmethod
    def write_case_judgments(party_judgments, filename):
        """
        Dump a list of judgments to a CSV with one column
        :param party_judgments: List of JudgmentNumberData
        :param filename: filename to use for creating the judgment list file
        :return:
        """
        import csv

        with open(filename, 'w', ) as judgments_file:
            wr = csv.writer(judgments_file, delimiter='\n')
            judgments_list = [j.formatted_judg_num for j in party_judgments]
            wr.writerow(judgments_list)


class DobScraperManager:

    @staticmethod
    def scrape_judgment_dobs(self, judgments):
        """

        :param judgments: List of JudgmentNumberData
        :return:
        """
        scraper = SCNJScraper(self.browser)
        scraper.login_and_solve(scraper)
        # tab navigation
        scraped_judgment_names = []
        logging.debug('Working on judgments: {}'.format(judgments))
        try:
            for i, judg in enumerate(judgments):
                if (i + 1) % 7 == 0:
                    scraper.login_and_solve(scraper)  # @TODO: remove scraper parameter to function call
                scraper.navigate_to_judgment_tab()
                judgment = SCNJScraper.split_judgment_by_dash(judg.formatted_judg_num)
                scraper.enter_judgment_and_search(judgment)
                assert('Judgment Record Search Results' in scraper.browser.page_source)
                scraper.navigate_to_judgment_details()
                assert('Judgment Search Result Details' in scraper.browser.page_source)
                # move to new test for date of birth scrape
                # matched_name = scraper.click_debtor_link()
                # dob, _ = scraper.scrape_date_of_birth()
                matched_names = scraper.click_debtor_link()
                for name in matched_names:
                    name = name._replace(judgment_num=judg.docketed_judg_num)  # non-split judgment number
                    scraped_judgment_names.append(name)
                logging.info('DOB number {} scraped'.format(i))
                # if i >= 5:
                #     self._orm_bulk_create(scraped_judgment_names)
                #     break
        finally:
            self._orm_bulk_create(scraped_judgment_names)
