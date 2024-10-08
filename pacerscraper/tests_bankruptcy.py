# from django.conf import settings
from django.test import TestCase, SimpleTestCase

from .utils import PacerScraperBankruptcyUtils as psutils
from orders.models import SearchName
# Create your tests here.


class BankruptcyScraperTestCase(TestCase):

    def setUp(self):
        # import os
        # self.pacer_bankruptcy_court_url = "https://ecf.njd.uscourts.gov/cgi-bin/login.pl"
        # self.pacer_files_dir = os.path.join(settings.MEDIA_ROOT, 'pacer_judgment_idx')
        self.file_to_parse = '82ba9a6e-e8f1-4d1b-b8bd-6d031db9b56f.html'
        self.single_case_number = '1:13-cr-00167-JBS'
        # self.alias_token = 'Alias'
        # self.case_summary_token = 'Case Summary'
        # self.party_token = 'Party'
        from pyvirtualdisplay import Display
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()

    def tearDown(self):
        # browser.close()
        self.display.stop()

    def test_generic_connect(self):
        driver = psutils.get_webdriver()
        psutils.pacer_login(driver)
        driver.get("https://www.pacer.gov/psco/cgi-bin/links.pl")
        self.assertIn("Public Access to Court", driver.title)

    def test_pacer_connect(self):
        driver = psutils.get_webdriver()
        url = "https://www.pacer.gov/psco/cgi-bin/links.pl"
        driver.get(url)
        self.assertIn("PACER Login", driver.title)

    def test_pacer_login(self):
        driver = psutils.get_webdriver()
        psutils.pacer_login(driver)
        psutils.check_page_has_text(driver, r'PACER Service Center.')

    def test_navigate_to_bankruptcy_search_form(self):
        browser = psutils.get_webdriver()
        psutils.pacer_login(browser)
        browser.get(psutils.pacer_bankruptcy_search_form_url)
        psutils.check_page_has_text(browser, r'Live Database')

    def test_load_bankruptcy_index_by_date(self):
        browser = psutils.get_webdriver()
        psutils.pacer_login(browser)
        browser.get(psutils.pacer_bankruptcy_search_form_url)
        psutils.check_page_has_text(browser, r'Live Database')
        from_date_str = '11/1/2017'
        to_date_str = '11/3/2017'
        psutils.load_bankruptcy_report_index(browser, from_date_str, to_date_str)
        psutils.check_page_has_text(browser, r'Select a Case')

    def test_query_and_archive_bankruptcy_report(self):
        """
        This is a main function for the general workflow
        :return:
        """
        # browser = PacerScraperUtils.get_webdriver()
        # PacerScraperUtils.pacer_login(browser)
        # PacerScraperUtils.navigate_to_judgments_index_form(browser)
        # PacerScraperUtils.check_page_has_text(browser, r'Judgment Index Report')
        from_date_str = '1/4/2017'
        to_date_str = '1/5/2017'
        # PacerScraperUtils.load_judment_report_index(browser, from_date_str, to_date_str)
        # PacerScraperUtils.store_judgment_report(browser, from_date_str, to_date_str)
        b_report = psutils.query_and_archive_bankruptcy_report(from_date_str, to_date_str)
        print(('Index report saved to: {}'.format(b_report.archive_file)))
        self.assertNotEqual(b_report.archive_file, '')

    def test_load_local_judgment_report(self):
        # file_to_parse = '82ba9a6e-e8f1-4d1b-b8bd-6d031db9b56f.html'
        browser = psutils.load_local_bankruptcy_report(self.file_to_parse)
        psutils.check_page_has_text(browser, r'Select a Case')

    def test_parse_local_judgment_report(self):
        """
        Parse local bankruptcy index report and make PacerBankruptcyIndexCase models out of data
        :return:
        """
        browser = psutils.load_local_bankruptcy_report(self.file_to_parse)
        max_rows_to_process = 5  # 10
        row_count = 0
        for row in browser.find_elements_by_css_selector('table[width="100%"] tbody tr'):
            cells = row.find_elements_by_tag_name('td')
            if row_count < max_rows_to_process and len(cells) > 0 and psutils.is_not_header_row(cells):
                row_contents = psutils.extract_row_contents(cells)
                bankruptcy_object = psutils.make_bankruptcy_index_case(row_contents)
                print(("Case number: {}; date filed: {}".format(bankruptcy_object.case_number,
                                                               bankruptcy_object.date_filed)))
                self.assertNotEqual(bankruptcy_object.case_number, '')
                row_count += 1
        self.assertGreaterEqual(row_count, 1)

    def test_build_bankruptcy_index_report(self):
        """
        Parse a local file to build individual bankruptcies and save to db
        but do not attach case summary. alias and party files.
        Now part of PacerScraperUtils to be called from command line.
        :return:
    #     """
        from .models import BankruptcyIndexReport
        import dateparser

        browser = psutils.load_local_bankruptcy_report(self.file_to_parse)
        max_rows_to_process = 5
        row_count = 0
        #build top level model
        report_from, report_to = psutils.get_bankruptcy_index_report_period(browser)
        report_from = dateparser.parse(report_from)
        report_to = dateparser.parse(report_to)
        bankruptcy_idx_report = BankruptcyIndexReport(date_from=report_from,
                                                    date_to=report_to,
                                                    archive_file=self.file_to_parse)
        bankruptcy_idx_report.save()
        #process rows from report
        for row in browser.find_elements_by_css_selector('table tbody tr'):
            cells = row.find_elements_by_tag_name('td')
            if row_count < max_rows_to_process and psutils.is_not_header_row(cells):
                print((cells[0].text))
                row_contents = psutils.extract_row_contents(cells)
                bankruptcy_object = psutils.make_bankruptcy_index_case(row_contents)
                print(bankruptcy_object)
                self.assertNotEqual(bankruptcy_object.case_number, '')
                bankruptcy_object.bankruptcy_index_report = bankruptcy_idx_report
                bankruptcy_object.save()
            row_count += 1

    def test_build_bankruptcy_index_report_from_local_file(self):
        """
        Parse a local file to pull all of the judgment data into the db and onto the local file system
        :return:
        """
        psutils.build_bankruptcy_index_report_from_local_file(self.file_to_parse, max_rows_to_process=12)

    def test_parse_report_dates_from_local_bankruptcy_report(self):
        browser = psutils.load_local_bankruptcy_report(self.file_to_parse)
        report_from, report_to = psutils.get_bankruptcy_index_report_period(browser)
        self.assertNotEqual(report_from, '')
        self.assertNotEqual(report_to, '')
        # print(report_to)

    # # def test_find_query_page_link(self):
    # #     browser = PacerScraperUtils.get_webdriver()
    # #     PacerScraperUtils.navigate_to_query_form(browser)
    # #     PacerScraperUtils.check_page_has_text(browser, r'Search Clues')
    #
    # def test_get_case_page_no_subcases(self):
    #     browser = PacerScraperUtils.get_webdriver()
    #     PacerScraperUtils.pacer_login(browser)
    #     PacerScraperUtils.navigate_to_query_form(browser)
    #     # case_number = '1:13-cr-00167-JBS'
    #     # case_num_str = '1:13-cr-00074-RMB'
    #     PacerScraperUtils.enter_case_data_on_form(browser, self.single_case_number)
    #     PacerScraperUtils.check_page_has_text(browser, 'All Defendants')
    #
    # def test_get_case_page_with_subcases(self):
    #     browser = PacerScraperUtils.get_webdriver()
    #     PacerScraperUtils.pacer_login(browser)
    #     PacerScraperUtils.navigate_to_query_form(browser)
    #     case_number = '1:13-cr-00074-RMB'
    #     PacerScraperUtils.enter_case_data_on_form(browser, case_number)
    #     PacerScraperUtils.check_page_has_text(browser, 'All Defendants')
    #
    # def test_get_jsn_case_summary_data(self):
    #     browser = PacerScraperUtils.get_webdriver()
    #     PacerScraperUtils.pacer_login(browser)
    #     PacerScraperUtils.navigate_to_query_form(browser)
    #     PacerScraperUtils.enter_case_data_on_form(browser, self.single_case_number)
    #     PacerScraperUtils.check_page_has_text(browser, 'All Defendants')
    #     d = PacerScraperUtils.archive_case_summary_data(browser)
    #     print(d)

    def test_get_full_bankruptcy_report_data(self):
        """
        This is the main function for the general workflow
        :return:
        """
        import logging
        logger = logging.getLogger(__name__)

        from_date_str = '1/4/2017'
        to_date_str = '1/4/2017'
        bankruptcy_report_contents = psutils.query_and_archive_bankruptcy_report(from_date_str, to_date_str)
        logger.info("Bankruptcy file generated: {}".format(bankruptcy_report_contents.archive_file))
        psutils.build_bankruptcy_index_report_from_local_file(bankruptcy_report_contents.archive_file, max_rows_to_process=12)
        print("Done!")

    def test_check_stop_file_terminates_execution(self):
        """
        This is the main function for the general workflow
        :return:
        """
        import logging
        logger = logging.getLogger(__name__)
        import os

        from_date_str = '1/4/2017'
        to_date_str = '1/4/2017'
        # psutils.remove_stop_files()
        if not os.path.exists(psutils.stop_file):
            open(psutils.stop_file,'a').close()  # touch file
        bankruptcy_report_contents = psutils.query_and_archive_bankruptcy_report(from_date_str, to_date_str)
        logger.info("Bankruptcy file generated: {}".format(bankruptcy_report_contents.archive_file))
        row_count = psutils.build_bankruptcy_index_report_from_local_file(bankruptcy_report_contents.archive_file, max_rows_to_process=12)
        self.assertEqual(row_count, 0)
        print("Done!")

    def test_build_scrape_commands(self):
        command_str = "python manage.py buildbankruptcydata {} {}\n"
        from_date = "1/1/17"
        to_date = "1/5/17"
        command_file = "bankruptcy_commands.sh"
        command_lines = []
        command_lines.append(command_str.format(from_date, to_date))

        with open(command_file,'w') as f:
            f.writelines(command_lines)
            f.close()

    def test_generate_dates(self):
        from .utils import ScraperCommandGenerator
        dates_generated = ScraperCommandGenerator.generate_year_of_dates(2017)
        self.assertEqual(len(dates_generated), 36)

    def test_generate_scraper_commands(self):
        from .utils import ScraperCommandGenerator
        dates_generated = ScraperCommandGenerator.generate_year_of_dates(2006)
        command_str = "python manage.py buildusdcjudgmentdata {} {}\n"
        command_file = "bankruptcy_commands.sh"
        start_date_idx = 0
        end_date_idx = 1
        with open(command_file, 'w') as f:
            for gen_date in dates_generated:
                f.writelines(command_str.format(gen_date[start_date_idx], gen_date[end_date_idx]))
        f.close()

    def test_logging(self):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Log this message...#2!")

    # party build tests

    def test_build_party_from_file(self):
        from .utils import PacerScraperPartyBuilder
        # party_file = 'b3db43f8-326b-412f-b9b2-6a702a2330d6.html'
        party_file = '60bb0e78-0d1f-4263-8aa7-e75c4fea7ec4.html'
        party_list = PacerScraperPartyBuilder.\
            build_party_list_from_party_file(party_file)
        # @TODO: add aliases
        # print(party_list[0].party_name)
        for party in party_list:
            print(party)
            self.assertNotEqual('PRO SE', party.party_type)

    def test_build_party_alias_from_file(self):
        from .utils import PacerScraperPartyBuilder
        alias_file = '74526d97-849f-4220-aa7c-c316b82c1f8f.html'
        alias_list = PacerScraperPartyBuilder.\
            build_alias_list_from_alias_file(alias_file)
        self.assertGreater(len(alias_list), 0)

    def test_build_party_from_db(self):
        pass


class BankruptcySearchTestCase(TestCase):

    def test_load_raw_sql(self):
        from django.db import connection
        from pacerscraper.models import PacerBankruptcyParty

        cursor = connection.cursor()
        cursor.execute('SET FOREIGN_KEY_CHECKS=0;')  # ignore refs to case index for test
        test_file = 'test_bankruptcy_party_insert.sql'
        self._load_parties_from_sql_file(cursor, test_file)

        # check party count
        parties = PacerBankruptcyParty.objects.filter(party_type='Defendant')
        party_count = len(parties)
        print(('Found {} defendants'.format(party_count)))
        self.assertGreater(party_count, 0)

    def test_search_for_party(self):
        from django.db import connection
        from nameviewer.utils import PacerSearchUtils

        cursor = connection.cursor()
        cursor.execute('SET FOREIGN_KEY_CHECKS=0;')  # ignore refs to case index for test
        test_file = 'test_bankruptcy_party_insert.sql'
        PacerSearchUtils.load_parties_from_sql_file(cursor, test_file)
        search_results = PacerSearchUtils.search_bankruptcy_party_name('Soon', 'Jang')
        match_count = len(search_results)
        self.assertGreaterEqual(match_count, 1)
        search_results = PacerSearchUtils.search_bankruptcy_party_name('Soon', 'Jang', 'Plaintiff')
        match_count = len(search_results)
        self.assertEqual(match_count, 0)

    def test_search_for_alias(self):
        from django.db import connection
        from nameviewer.utils import PacerSearchUtils

        cursor = connection.cursor()
        cursor.execute('SET FOREIGN_KEY_CHECKS=0;')  # ignore refs to case index for test
        test_file = 'test_bankruptcy_alias_insert.sql'
        PacerSearchUtils.load_parties_from_sql_file(cursor, test_file)
        search_results = PacerSearchUtils.search_bankruptcy_alias_name('Michael', 'Hagood')
        match_count = len(search_results)
        self.assertGreaterEqual(match_count, 1)
        search_results = PacerSearchUtils.search_bankruptcy_alias_name('Michael', 'Henry')
        match_count = len(search_results)
        self.assertGreaterEqual(match_count, 1)

    def test_search_for_filtered_party(self):
        from django.db import connection
        from nameviewer.utils import PacerSearchUtils

        cursor = connection.cursor()
        cursor.execute('SET FOREIGN_KEY_CHECKS=0;')  # ignore refs to case index for test
        # test_file = 'test_bankruptcy_party_insert.sql'
        test_file = ''
        # @TODO: make a new test file with the party matches
        PacerSearchUtils.load_parties_from_sql_file(cursor, test_file)
        # search_results = PacerSearchUtils.search_bankruptcy_party_name('Robert', 'Kane')
        sn = SearchName(first_name='Robert', last_name='Kane', search_from='2008-09-12',
                        search_to='2010-09-12')
        search_results = PacerSearchUtils.search_bankruptcy_party_name(searchname=sn)
        match_count = len(search_results)
        self.assertGreaterEqual(match_count, 2)


class BankruptcySearchDictTestCase(SimpleTestCase):
    allow_database_queries = True

    #run this with the following
    #python manage.py test pacerscraper.tests_bankruptcy.BankruptcySearchDictTestCase.test_query_bankruptcy_with_namesearch_dict --testrunner=nameviewer.scripts.testrunner.NoDbTestRunner
    def test_query_bankruptcy_with_namesearch_dict(self):
        from pacerscraper.models import BankruptcyReportQueryManager as bq
        from orders.models import SearchName
        fn = 'Max'
        ln = 'Parangi'
        searchname = SearchName(first_name=fn, last_name=ln)
        matches = bq.query_database_by_searchname_details2(searchname)
        self.assertGreater(len(matches), 0)
        fn = 'Soon'
        ln = 'Jang'
        searchname = SearchName(first_name=fn, last_name=ln)
        matches = bq.query_database_by_searchname_details2(searchname)
        self.assertGreater(len(matches), 0)
        fn = 'Melinda'
        ln = 'Newmark'
        searchname = SearchName(first_name=fn, last_name=ln)
        matches = bq.query_database_by_searchname_details2(searchname)
        self.assertGreater(len(matches), 0)
