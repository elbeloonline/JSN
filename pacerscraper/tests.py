# from django.conf import settings
from django.test import TestCase

from .utils import PacerScraperUtils
# Create your tests here.


class ScraperTestCase(TestCase):

    def setUp(self):
        # import os
        # self.pacer_court_url = "https://ecf.njd.uscourts.gov/cgi-bin/login.pl"
        # self.pacer_files_dir = os.path.join(settings.MEDIA_ROOT, 'pacer_judgment_idx')
        self.file_to_parse = '5fd8e643-1742-4a07-a853-a2f3f91c333c.html'
        self.single_case_number = '1:13-cr-00167-JBS'
        # self.alias_token = 'Alias'
        # self.case_summary_token = 'Case Summary'
        # self.party_token = 'Party'
        from pyvirtualdisplay import Display
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()

    def tearDown(self):
        # browser.close()
        if self.display is not None:
            self.display.stop()

    def test_generic_connect(self):
        driver = PacerScraperUtils.get_webdriver()
        driver.get("http://www.python.org")
        self.assertIn("Python", driver.title)

    def test_pacer_connect(self):
        driver = PacerScraperUtils.get_webdriver()
        driver.get(PacerScraperUtils.pacer_court_url)
        self.assertIn("CM/ECF LIVE", driver.title)

    def test_pacer_login(self):
        driver = PacerScraperUtils.get_webdriver()
        PacerScraperUtils.pacer_login(driver)
        PacerScraperUtils.check_page_has_text(driver, r'3June2013')

    def test_find_judgment_index_link(self):
        browser = PacerScraperUtils.get_webdriver()
        PacerScraperUtils.pacer_login(browser)
        PacerScraperUtils.navigate_to_judgments_index_form(browser)
        PacerScraperUtils.check_page_has_text(browser, r'Judgment Index Report')

    def test_load_judgment_index_by_date(self):
        browser = PacerScraperUtils.get_webdriver()
        PacerScraperUtils.pacer_login(browser)
        PacerScraperUtils.navigate_to_judgments_index_form(browser)
        PacerScraperUtils.check_page_has_text(browser, r'Judgment Index Report')
        from_date_str = '1/3/2017'
        to_date_str = '1/13/2017'
        PacerScraperUtils.load_judment_report_index(browser, from_date_str, to_date_str)
        PacerScraperUtils.check_page_has_text(browser, r'Report Period')

    def test_query_and_archive_judgment_report(self):
        """
        This is a main function for the general workflow
        :return:
        """
        # browser = PacerScraperUtils.get_webdriver()
        # PacerScraperUtils.pacer_login(browser)
        # PacerScraperUtils.navigate_to_judgments_index_form(browser)
        # PacerScraperUtils.check_page_has_text(browser, r'Judgment Index Report')
        from_date_str = '1/4/2017'
        to_date_str = '1/13/2017'
        # PacerScraperUtils.load_judment_report_index(browser, from_date_str, to_date_str)
        # PacerScraperUtils.store_judgment_report(browser, from_date_str, to_date_str)
        PacerScraperUtils.query_and_archive_judgment_report(from_date_str, to_date_str)

    def test_load_local_judgment_report(self):
        browser = PacerScraperUtils.load_local_judgment_report(self.file_to_parse)
        PacerScraperUtils.check_page_has_text(browser, 'Judgment Index Report')

    def test_parse_local_judgment_report(self):
        """
        Parse local judgment index report and make PacerJudgmentIndexCase models out of data
        :return:
        """
        browser = PacerScraperUtils.load_local_judgment_report(self.file_to_parse)
        max_rows_to_process = 999  # 10
        row_count = 0
        last_case_number = None
        case_num_token = 'Case number'
        for row in browser.find_elements_by_css_selector('div#cmecfMainContent center center table[width="100%"] tbody tr'):
            cells = row.find_elements_by_tag_name('td')
            if row_count < max_rows_to_process and len(cells) > 0 and PacerScraperUtils.is_not_header_row(cells):
                row_contents = PacerScraperUtils.extract_row_contents(cells)
                if last_case_number is None:
                    last_case_number = row_contents.get(case_num_token)
                elif row_contents.get(case_num_token) != '':
                    last_case_number = row_contents.get(case_num_token)
                judgment_object = PacerScraperUtils.make_judgment_index_case(row_contents)
                print(("Case number: {}; last case number: {}".format(judgment_object.case_number, last_case_number)))
                # self.assertNotEqual(judgment_object.case_number, '')
                row_count += 1
        self.assertGreaterEqual(row_count, 1)

    def test_build_judgment_index_report(self):
        """
        Parse a local file to build individual judgments and save to db but do not attach case summary. alias and party files.
        Now part of PacerScraperUtils to be called from command line.
        :return:
        """
        from .models import JudgmentIndexReport, PacerJudgmentIndexCase
        import dateparser

        browser = PacerScraperUtils.load_local_judgment_report(self.file_to_parse)
        max_rows_to_process = 10
        row_count = 0
        last_case_number = None
        case_num_token = 'Case number'

        #build top level model
        report_from, report_to = PacerScraperUtils.get_judgment_index_report_period(browser)
        report_from = dateparser.parse(report_from)
        report_to = dateparser.parse(report_to)
        judgment_idx_report = JudgmentIndexReport(date_from=report_from,
                                                  date_to=report_to,
                                                  archive_file=self.file_to_parse)
        judgment_idx_report.save()

        #process rows from report
        for row in browser.find_elements_by_css_selector('table tbody tr'):
            cells = row.find_elements_by_tag_name('td')
            if row_count < max_rows_to_process and len(cells) > 0:
                row_contents = PacerScraperUtils.extract_row_contents(cells)
                if last_case_number is None:
                    last_case_number = row_contents.get(case_num_token)
                elif row_contents.get(case_num_token) != '':
                    last_case_number = row_contents.get(case_num_token)
                judgment_object = PacerScraperUtils.make_judgment_index_case(row_contents)
                # print(judgment_object)
                print(("Case number: {}; last case number: {}".format(judgment_object.case_number, last_case_number)))
                # self.assertNotEqual(judgment_object.case_number, '')
                judgment_object.judgment_index_report = judgment_idx_report
                judgment_object.save()
            row_count += 1

    def test_build_judgment_index_report_from_local_file(self):
        """
        Parse a local file to pull all of the judgment data into the db and onto the local file system
        :return:
        """
        from .models import JudgmentIndexReport, PacerJudgmentIndexCase
        import dateparser

        browser = PacerScraperUtils.load_local_judgment_report(self.file_to_parse)
        browser2 = PacerScraperUtils.get_webdriver()
        PacerScraperUtils.pacer_login(browser2)

        max_rows_to_process = 14
        row_count = 0
        case_num_token = 'Case number'

        #build top level model
        report_from, report_to = PacerScraperUtils.get_judgment_index_report_period(browser)
        report_from = dateparser.parse(report_from)
        report_to = dateparser.parse(report_to)
        judgment_idx_report = JudgmentIndexReport(date_from=report_from,
                                                  date_to=report_to,
                                                  archive_file=self.file_to_parse)
        judgment_idx_report.save()

        #process rows from report
        for row in browser.find_elements_by_css_selector('table tbody tr'):
            cells = row.find_elements_by_tag_name('td')
            if row_count < max_rows_to_process and len(cells) > 0:
                row_contents = PacerScraperUtils.extract_row_contents(cells)
                is_case_of_interest = row_contents.get('Case status').strip() == PacerScraperUtils.no_payment_token
                if row_contents['Case number'].strip() != '' and is_case_of_interest:
                    judgment_object = PacerScraperUtils.make_judgment_index_case(row_contents)
                    print(("Parsed case number: {}".format(judgment_object.case_number)))
                    # begin addition to pull remaining data from system
                    PacerScraperUtils.navigate_to_query_form(browser2)
                    PacerScraperUtils.enter_case_data_on_form(browser2, judgment_object.case_number)
                    # self._check_page_has_text(browser2, 'All Defendants')
                    d = PacerScraperUtils.archive_case_summary_data(browser2, PacerScraperUtils.pacer_files_dir)
                    # print(d)
                    judgment_object.alias_file = d[PacerScraperUtils.alias_token]
                    judgment_object.case_summary_file = d[PacerScraperUtils.case_summary_token]
                    judgment_object.party_file = d[PacerScraperUtils.party_token]
                    # end addition
                    print(judgment_object)
                    self.assertNotEqual(judgment_object.case_number, '')
                    judgment_object.judgment_index_report = judgment_idx_report
                    judgment_object.save()
                    self.assertNotEqual(judgment_object.party_file, '')
            row_count += 1
        # self.assertGreaterEqual(row_count, 1)

    def test_parse_report_dates_from_local_judgment_report(self):
        browser = PacerScraperUtils.load_local_judgment_report(self.file_to_parse)
        report_from, report_to = PacerScraperUtils.get_judgment_index_report_period(browser)
        self.assertNotEqual(report_from, '')
        self.assertNotEqual(report_to, '')

    # def test_find_query_page_link(self):
    #     browser = PacerScraperUtils.get_webdriver()
    #     PacerScraperUtils.navigate_to_query_form(browser)
    #     PacerScraperUtils.check_page_has_text(browser, r'Search Clues')

    def test_get_case_page_no_subcases(self):
        browser = PacerScraperUtils.get_webdriver()
        PacerScraperUtils.pacer_login(browser)
        PacerScraperUtils.navigate_to_query_form(browser)
        # case_number = '1:13-cr-00167-JBS'
        # case_num_str = '1:13-cr-00074-RMB'
        PacerScraperUtils.enter_case_data_on_form(browser, self.single_case_number)
        PacerScraperUtils.check_page_has_text(browser, 'All Defendants')

    def test_get_case_page_with_subcases(self):
        browser = PacerScraperUtils.get_webdriver()
        PacerScraperUtils.pacer_login(browser)
        PacerScraperUtils.navigate_to_query_form(browser)
        case_number = '1:13-cr-00074-RMB'
        PacerScraperUtils.enter_case_data_on_form(browser, case_number)
        PacerScraperUtils.check_page_has_text(browser, 'All Defendants')

    def test_get_jsn_case_summary_data(self):
        browser = PacerScraperUtils.get_webdriver()
        PacerScraperUtils.pacer_login(browser)
        PacerScraperUtils.navigate_to_query_form(browser)
        PacerScraperUtils.enter_case_data_on_form(browser, self.single_case_number)
        PacerScraperUtils.check_page_has_text(browser, 'All Defendants')
        d = PacerScraperUtils.archive_case_summary_data(browser, PacerScraperUtils.pacer_files_dir)
        print(d)

    ###
    def test_get_full_pacer_report_data(self):
        """
        This is the main function for the general workflow
        :return:
        """
        from_date_str = '1/5/2017'
        to_date_str = '1/11/2017'
        judgment_report_contents = PacerScraperUtils.query_and_archive_judgment_report(from_date_str, to_date_str)
        print(("Judgment file generated: {}".format(judgment_report_contents.archive_file)))
        PacerScraperUtils.build_judgment_index_report_from_local_file(judgment_report_contents.archive_file)
        print("Done!")

    def test_loggers(self):
        import logging
        # logging.basicConfig()
        # logger = logging.getLogger(__name__)
        logging.error('Testing error logging in a test case')
        pass
