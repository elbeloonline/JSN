from collections import namedtuple
from enum import Enum
import logging
import os
import sys
import time

from django.conf import settings
from selenium.common.exceptions import NoSuchElementException

class PacerScraperBase:

    alias_token = 'Alias'
    case_summary_token = 'Case Summary'
    party_token = 'Party'
    stop_file = os.path.join('jsnetwork_project', 'static', 'istop')

    @staticmethod
    def get_webdriver():
        """
        Get a web browser using Chrome as the driver
        :return: selenium.webdriver
        """
        import time
        from selenium import webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--crash-dumps-dir=/tmp/chromedriver')
        options.add_argument('--remote-debugging-port=9222')

        # attempt to fix problem where selenium can't connect to localhost on EC2
        driver = None
        retries = 0
        while driver is None and retries < 10:
            try:
                driver = webdriver.Chrome(chrome_options=options)
            except Exception as e:
                driver = None
                print("Unexpected error while getting webdriver:", sys.exc_info()[0])
                # print("Problem encountered while fetching webdriver: ".format(str(e)))
                time.sleep(10)
                retries += 1
                # logging.error(traceback.format_exc())

        return driver


    @staticmethod
    def check_page_has_text(browser, search_text, print_src=False):
        """
        Check to see if text is on a page. Good for figuring out if you are where you think you are.
        :param browser: selenium.webdriver
        :param search_text: Text to look for on the page
        :param print_src: If true, prints the full html page to a file for debugging
        :return:
        """
        import re
        src = browser.page_source
        text_found = re.search(search_text, src)
        if print_src:
            # print(src)
            with open('page_out.html','w') as f:
                f.write(src)
        # self.assertNotEqual(text_found, None)
        assert text_found is not None

    @staticmethod
    def navigate_to_url(url):
        """
        Open a web address with the class instance's webdriver
        :param url: web address to navigate to
        :return: webdriver
        """
        driver = PacerScraperBase.get_webdriver()
        driver.get(url)
        return driver

    @staticmethod
    def navigate_to_query_form(browser):
        """
        A convenience method for navigating to the search query form using the provided browser
        :param browser: the browser to work with
        :return:
        """
        link = browser.find_element_by_link_text('Query')
        link.click()

    @staticmethod
    def archive_case_summary_data(browser, save_to_dir, original_bk_case=None):
        """
        Archive the data collected for a BKCY case
        :param browser: the browser to work with
        :param save_to_dir: the directory to save the results to
        :param original_bk_case: the original bkcy case id
        :return: dict of page data for each report type associated with the case
        """
        link_names = [PacerScraperBase.alias_token, PacerScraperBase.case_summary_token, PacerScraperBase.party_token]
        anchors = []
        d = {}
        for link_text in link_names:
            # print('Using link text "{}" for navigation'.format(link_text))
            link = browser.find_element_by_link_text(link_text)
            anchor = link.get_attribute('href')
            anchors.append(anchor)
        for i, link_text in enumerate(link_names):
            browser.get(anchors[i])
            continue_link = browser.find_element_by_link_text('Continue')
            continue_link.click()
            # print('Got anchor {}'.format(anchor))
            if original_bk_case:
                if link_text == PacerScraperUtils.alias_token:
                    save_filename = original_bk_case.alias_file
                elif link_text == PacerScraperUtils.case_summary_token:
                    save_filename = original_bk_case.case_summary_file
                elif link_text == PacerScraperUtils.party_token:
                    save_filename = original_bk_case.party_file
                print(("Using save filename {} to store contents of type {}".format(save_filename, link_text)))
                filename = PacerScraperBase.save_contents_to_file(browser, save_to_dir, save_filename)
            else:
                filename = PacerScraperBase.save_contents_to_file(browser, save_to_dir)
            # print('Save contents of {} to {}'.format(link_text, filename))
            d[link_text] = filename
        return d

    @staticmethod
    def save_contents_to_file(browser, save_to_dir, save_filename=None):
        """
        Save contents to a file on the system with a unique identifier
        :param browser: the browser to work with
        :param save_to_dir: the directory to save to
        :param save_filename: the preferred file name. If not provided a filename is generated
        :return:
        """
        import uuid

        if not os.path.exists(save_to_dir):
            os.makedirs(save_to_dir)
        if save_filename:
            file_id = save_filename
        else:
            file_id = str(uuid.uuid4())+'.html'
        filename = os.path.join(save_to_dir, file_id)
        page_src = browser.page_source
        with open(filename, 'w') as f:
            f.write(page_src.encode('utf-8'))
        return file_id  # filename

    @staticmethod
    def stop_processing_files():
        """
        Checks to see if a stop file is present on the filesystem to indicate all processing should stop.
        The scraper can be run via a cron job, and this is a way to stop it if all of the cases haven't been processed
        :return: bool denoting whether processing should stop
        """
        stop_processing = False
        if os.path.exists(PacerScraperBase.stop_file):
            stop_processing = True
        return stop_processing

    @staticmethod
    def remove_stop_files():
        """
        Remove any stop file that may be present on the system. The scraper won't run if a stop file is present
        :return:
        """
        if os.path.exists(PacerScraperBase.stop_file):
            os.remove(PacerScraperBase.stop_file)


class PacerScraperBankruptcyUtils(PacerScraperBase):

    pacer_court_url = "https://ecf.njb.uscourts.gov/cgi-bin/login.pl"
    pacer_court_url_base = "https://ecf.njb.uscourts.gov/cgi-bin/"
    # pacer_court_url = "https://ecf.njb.uscourts.gov/cgi-bin/login.pl"
    pacer_bankruptcy_search_form_url = "https://ecf.njb.uscourts.gov/cgi-bin/iquery.pl"
    # bankruptcy_files_dir = os.path.join(settings.MEDIA_ROOT, 'pacer_bankruptcy_idx')
    bankruptcy_files_dir = os.path.join(settings.MEDIA_ROOT, 'bkcy_data', 'data_5')
    case_token = 'Case No.'

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pass

    @staticmethod
    def pacer_login(web_driver): # :selenium.webdriver
        """
        Login to the pacer system and navigate to the home page
        :param web_driver: selenium.webdriver
        """
        from time import sleep
        web_driver.get(PacerScraperUtils.pacer_court_url)
        # self.assertIn("CM/ECF LIVE", driver.title)
        username_str = 'kskinner79'
        password_str = 'zrp-CY5-aTD-Dk5'
        username = web_driver.find_element_by_name('loginForm:loginName')
        username.send_keys(username_str)
        password = web_driver.find_element_by_name('loginForm:password')
        password.send_keys(password_str)

        login_button_name = 'loginForm:fbtnLogin'
        login_button = web_driver.find_element_by_name(login_button_name)
        login_button.click()
        sleep(5)

    @staticmethod
    def load_bankruptcy_report_index(browser, from_date_str, to_date_str):
        """
        Queries the system for a list of judgments within the date range :from_date_str: to :to_date_str:
        :param browser: selenium.webdriver
        :param from_date_str: date to search from. in format MM/DD/YY
        :param to_date_str: date to search to. in format MM/DD/YY
        :return:
        """
        from_date = browser.find_element_by_name('filed_from')
        from_date.clear()
        from_date.send_keys(from_date_str)
        to_date = browser.find_element_by_name('filed_to')
        to_date.clear()
        to_date.send_keys(to_date_str)

        run_report_button_name = 'button1'
        run_report_button = browser.find_element_by_name(run_report_button_name)
        run_report_button.click()

    @staticmethod
    def query_and_archive_bankruptcy_report(date_from, date_to):
        """
        Connect to the pacer system and get a list of cases between the dates provided. Store results to the file system
        :param date_from: date to search from
        :param date_to: date to search to
        :return: a JudgmentIndexReport object
        :rtype: JudgmentIndexReport
        """
        # type: (str, str) -> BankruptcyIndexReport
        browser = PacerScraperBankruptcyUtils.get_webdriver()
        PacerScraperBankruptcyUtils.pacer_login(browser)
        # PacerScraperBankruptcyUtils.navigate_to_judgments_index_form(browser)
        import time
        time.sleep(5)  # @TODO: change next line to implicit wait
        browser.get(PacerScraperBankruptcyUtils.pacer_bankruptcy_search_form_url)
        PacerScraperBankruptcyUtils.check_page_has_text(browser, r'Live Database')
        from_date_str = date_from
        to_date_str = date_to
        PacerScraperBankruptcyUtils.load_bankruptcy_report_index(browser,
                                                                 from_date_str,
                                                                 to_date_str)
        b_report = PacerScraperBankruptcyUtils.store_bankruptcy_report(browser,
                                                                       from_date_str,
                                                                       to_date_str)
        browser.quit()
        return b_report # JudgmentIndexReport

    @staticmethod
    def store_bankruptcy_report(browser, from_date_str, to_date_str):
        """
        Store the BKCY report present in the browser based on the from and to search dates
        :param browser: the browser containing the page data to store
        :param from_date_str: search from date
        :param to_date_str: search to date
        :return: a BankruptcyIndexReport
        :rtype: BankruptcyIndexReport_2
        """
        # (Selenium.webdriver, str, str) -> BankruptcyIndexReport
        from .models import BankruptcyIndexReport_2
        import dateparser
        from django.conf import settings

        b_report = BankruptcyIndexReport_2()
        b_report.date_from = dateparser.parse(from_date_str)
        b_report.date_to = dateparser.parse(to_date_str)

        filename = PacerScraperBase.save_contents_to_file(browser, PacerScraperBankruptcyUtils.bankruptcy_files_dir)
        b_report.archive_file = filename
        b_report.save(using=settings.BKSEARCH_DB_COMB)
        return b_report

    # @staticmethod
    # def save_contents_to_file(browser):
    #     import os
    #     import uuid
    #
    #     if not os.path.exists(PacerScraperBankruptcyUtils.bankruptcy_files_dir):
    #         os.makedirs(PacerScraperBankruptcyUtils.bankruptcy_files_dir)
    #     file_id = str(uuid.uuid4())+'.html'
    #     filename = os.path.join(PacerScraperBankruptcyUtils.bankruptcy_files_dir, file_id)
    #     page_src = browser.page_source
    #     with open(filename, 'w') as f:
    #         f.write(page_src.encode('utf-8'))
    #     return file_id  # filename

    @staticmethod
    def load_local_bankruptcy_report(file_to_parse, dir, browser=None):
        """
        Load a stored BKCY report into the browser
        :param file_to_parse: the filename to load into the browser for parsing
        :param dir: the directory containing the stored files
        :param browser: the browser to laod the file into
        :return: browser with loaded file
        """
        html_source = os.path.join(dir,
                                   file_to_parse)
        assert os.path.exists(html_source) == True
        browser_filename = 'file://' + html_source
        if browser is None:
            browser = PacerScraperBankruptcyUtils.get_webdriver()
        browser.get(browser_filename)
        return browser

    @staticmethod
    def is_not_header_row(cells):
        """
        Determine if the cells provided correspond to a header role or not
        :param cells: the cells to scan for header row text
        :return: status of whether the row is not a header row. False if it is a header row
        """
        line_status = True
        for e in cells:
            text = str(e.text).strip()
            if text.find(PacerScraperBankruptcyUtils.case_token) > -1 or text.find('matching cases') > -1:
                line_status = False
        return line_status

    @staticmethod
    def make_bankruptcy_index_case(d):
        """
        Make a PacerBankruptcyIndexCase from a dict of key/value pairs extracted via _extract_row_contents function.
        Does not set the parent FK, up to the calling function to do this
        :param d: dict of relevant key/value pairs
        :return: PacerJudgmentIndexCase
        """
        import dateparser
        from .models import PacerBankruptcyIndexCase_5
        if d.get('Document') == '':
            d['Document'] = 0
        d_filed = dateparser.parse(d.get('Filed'))
        d_closed = dateparser.parse(d.get('Closed'))
        bankruptcy_object = PacerBankruptcyIndexCase_5(case_number=d.get('Case no').strip(),
                                                    case_title=d.get('Case Title'),
                                                    chapter_lead_bk_case=d.get('Chapter'),
                                                    date_filed=d_filed,
                                                    date_closed=d_closed )
        return bankruptcy_object

    @staticmethod
    def extract_row_contents(cells):
        """
        Extract key BKCY data elements from the provided row of td cells
        :param cells: a set of cells to extract data from
        :return: dict of key BKCY data including case number, case title, chapter, etc
        """
        case_number = cells[0].text.strip()
        case_title = cells[1].text.strip()
        chapter_lead_bk = cells[2].text.strip()
        date_filed = cells[3].text.strip()
        date_closed = cells[4].text.strip()

        d = {'Case no':case_number, 'Case Title':case_title, 'Chapter':chapter_lead_bk,
             'Filed':date_filed, 'Closed':date_closed}

        return d

    @staticmethod
    def get_bankruptcy_index_report_period(browser):
        """
        Extract the report period from the bankruptcy index report
        :param browser: selenium.webdriver
        :return: list of strs with dates
        """
        # cell = browser.find_element_by_css_selector('td font[size="-1" color="DARKBLUE"]')
        # report_dates = cell.text
        # report_dates = report_dates.split(':')[1].strip().split('-')
        # report_from = report_dates[0].split()[0]
        # report_to = report_dates[1].split()[0]
        # return report_from, report_to
        import re
        src = browser.page_source
        exp = "Filed From:\s*(\d+/\d+/\d+)\sFiled To:\s*(\d+/\d+/\d+)"
        m = re.search(exp, src)
        report_from = m.group(1)
        report_to = m.group(2)
        # print("{} - {}".format(report_from, report_to))
        return report_from, report_to

    @staticmethod
    def build_bankruptcy_index_report_from_local_file(local_archive_file, max_rows_to_process=-1):
        """
        Parse a local file to pull all of the bankruptcy data into the db and onto the local file system
        :param local_archive_file: the local archive file to process
        :param max_rows_to_process: optional number of rows to process from file
        :return: int number of rows processed
        """

        def do_process_row(row_count, max_rows_to_process):
            """
            Determine whether to keep processing rows based on the number processed and the max number to process
            :param row_count: number of rows processed
            :param max_rows_to_process: max rows to process
            :return: bool indicating whether another row should be processed
            """
            do_process = False
            if max_rows_to_process < 0:
                do_process = True
            elif row_count < max_rows_to_process:
                do_process = True
            return do_process

        from .models import BankruptcyIndexReport_5, PacerBankruptcyIndexCase_5
        import dateparser
        import logging
        import time
        logger = logging.getLogger(__name__)

        psutils = PacerScraperBankruptcyUtils
        # dir = os.path.join(settings.MEDIA_ROOT, 'pacer_bankruptcy_idx')
        dir = PacerScraperBankruptcyUtils.bankruptcy_files_dir
        browser = psutils.load_local_bankruptcy_report(local_archive_file, dir)
        browser2 = psutils.get_webdriver()
        psutils.pacer_login(browser2)

        # max_rows_to_process = 12
        row_count = 0

        #build top level model
        # @TODO: make implicit
        time.sleep(5)
        report_from, report_to = psutils.get_bankruptcy_index_report_period(browser)
        report_from = dateparser.parse(report_from)
        report_to = dateparser.parse(report_to)
        bankruptcy_idx_report = BankruptcyIndexReport_5(date_from=report_from,
                                                        date_to=report_to,
                                                        archive_file=local_archive_file)
        bankruptcy_idx_report.save(using=settings.BKSEARCH_DB_COMB)
        # process rows from report
        for row in browser.find_elements_by_css_selector('table[cellspacing="10"] tbody tr'):
            cells = row.find_elements_by_tag_name('td')
            if do_process_row(row_count, max_rows_to_process) and psutils.is_not_header_row(cells):
                row_contents = psutils.extract_row_contents(cells)
                bankruptcy_object = psutils.make_bankruptcy_index_case(row_contents)
                is_not_parsed = psutils.case_already_processed(bankruptcy_object.case_number)
                if not is_not_parsed:
                    logger.info(bankruptcy_object)
                    # begin addition to pull remaining data from system
                    case_link = browser.find_element_by_link_text(bankruptcy_object.case_number)
                    case_href = case_link.get_attribute("href")
                    last_idx = case_href.rfind('/')
                    case_href = case_href[last_idx+1:]
                    court_str = psutils.pacer_court_url_base
                    browser2.get(court_str+case_href)
                    psutils.check_page_has_text(browser2, 'Date filed')
                    d = psutils.archive_case_summary_data(browser2, PacerScraperBankruptcyUtils.bankruptcy_files_dir)
                    bankruptcy_object.alias_file = d[psutils.alias_token]
                    bankruptcy_object.case_summary_file = d[psutils.case_summary_token]
                    bankruptcy_object.party_file = d[psutils.party_token]
                    # end addition
                    # self.assertNotEqual(bankruptcy_object.case_number, '')
                    bankruptcy_object.bankruptcy_index_report = bankruptcy_idx_report
                    bankruptcy_object.save(using=settings.BKSEARCH_DB_COMB)
                    # self.assertNotEqual(bankruptcy_object.party_file, '')
            if psutils.stop_processing_files():
                logger.info('Received file processing stop signal')
                break
            row_count += 1
        browser2.close()
        browser.close()
        return row_count

    @staticmethod
    def case_already_processed(case_number):
        """
        @TODO: only searches table _5 at the moment, make it search all tables
        Determine if a case number be processed again or not based on cases already processed. Cuts down on expenses by
        not processing data twice
        :param case_number: the case number to look for
        :return: True if already processed
        """
        import logging
        # from .models import BankruptcyIndexReport_5
        from .models import PacerBankruptcyIndexCase_5
        from django.conf import settings
        logger = logging.getLogger(__name__)
        processed = False
        # results = BankruptcyIndexReport.objects.filter(pacerbankruptcyindexcase__case_number__exact=case_number)
        # results = BankruptcyIndexReport_5.objects.using(settings.BKSEARCH_DB_COMB).filter(pacerbankruptcyindexcase_5__case_number__exact=case_number)
        results = PacerBankruptcyIndexCase_5.objects.using(settings.BKSEARCH_DB_COMB).filter(case_number__exact=case_number)
        if len(results) > 0:
            logger.info('Case already processed! {}'.format(case_number))
            processed = True
        return processed



class PacerScraperUtils(PacerScraperBase):

    pacer_court_url = "https://ecf.njd.uscourts.gov/cgi-bin/login.pl"
    pacer_files_dir = os.path.join(settings.MEDIA_ROOT, 'pacer_judgment_idx')
    case_number_token = 'Case Number'
    no_payment_token = 'No Payment'

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pass

    @staticmethod
    def pacer_login(web_driver): # :selenium.webdriver
        """
        Login to the pacer system and navigate to the home page
        :param web_driver: selenium.webdriver
        """
        web_driver.get(PacerScraperUtils.pacer_court_url)
        # self.assertIn("CM/ECF LIVE", driver.title)
        username_str = 'kskinner79'
        password_str = 'zrp-CY5-aTD-Dk5'
        username = web_driver.find_element_by_name('login')
        username.send_keys(username_str)
        password = web_driver.find_element_by_name('key')
        password.send_keys(password_str)

        login_button_name = 'button1'
        login_button = web_driver.find_element_by_name(login_button_name)
        login_button.click()

    @staticmethod
    def navigate_to_judgments_index_form(browser):
        """
        Navigates to the judgments index form page within the Pacer system.
        :param browser: selenium.webdriver
        :return:
        """
        # browser.find_elements_by_partial_link_text()
        # print('Waiting for page to load...')
        # browser.implicitly_wait(10)
        link = browser.find_element_by_link_text('Reports')
        link.click()
        link = browser.find_element_by_link_text('Judgment Index')
        link.click()

    @staticmethod
    def load_judment_report_index(browser, from_date_str, to_date_str):
        """
        Queries the system for a list of judgments within the date range :from_date_str: to :to_date_str:
        :param browser: selenium.webdriver
        :param from_date_str: date to search from. in format MM/DD/YY
        :param to_date_str: date to search to. in format MM/DD/YY
        :return:
        """
        from_date = browser.find_element_by_name('StartDate')
        from_date.clear()
        from_date.send_keys(from_date_str)
        to_date = browser.find_element_by_name('EndDate')
        to_date.clear()
        to_date.send_keys(to_date_str)

        run_report_button_name = 'button1'
        run_report_button = browser.find_element_by_name(run_report_button_name)
        run_report_button.click()

    @staticmethod
    def extract_row_contents(cells):
        """
        Extract key data from provided row
        :param cells: the cells to parse obtained from BKCY report
        :return: data extracted from the cells in a more accessible dict format
        """
        def clean_dict(d):
            amt = d.get('Amount')
            # print("Amount field value before cleaning field: {}".format(amt))
            # sometimes there's no space between the $ and the amount, add one if this is true
            if amt.find('$ ') < 0:
                amt = amt.replace('$', '$ ', 1)
                # print('Malformed amount field, fixing...')
            d['Amount'] = amt.split(' ')[1]
            d['Court Cost'] = d['Court Cost'].split(' ')[1]
        case_number = cells[0].text.strip()
        # print('Got case number midway through function: {}'.format(case_number))
        # print('Cells data beore splitting for Case status field : {}'.format(cells))
        case_status = str(cells[2].text).split('<br>')[0]
        case_status = case_status.splitlines()
        d = {'Case number':case_number, 'Case status':case_status[0].strip(), 'Last updated date':case_status[1].strip()}

        unparsed = str(cells[1].text).split('<br>')[0]
        unparsed = unparsed.splitlines()
        for row in unparsed:
            k, v = row.split(':')
            d[k] = v.strip()
        clean_dict(d)

        return d

    @staticmethod
    def store_judgment_report(browser, from_date_str, to_date_str):
        """
        Store the data to a report that's presently in the browser
        :param browser: web browser containing data
        :param from_date_str: date search was conducted from
        :param to_date_str: date the search was conducted to
        :return: a judgment index report
        :rtype: JudgmentIndexReport
        """
        # (Selenium.webdriver, str, str) -> JudgmentIndexReport
        from .models import JudgmentIndexReport
        import dateparser

        j_report = JudgmentIndexReport()
        j_report.date_from = dateparser.parse(from_date_str)
        j_report.date_to = dateparser.parse(to_date_str)

        filename = PacerScraperBase.save_contents_to_file(browser, PacerScraperUtils.pacer_files_dir)
        j_report.archive_file = filename
        j_report.save()
        return j_report

    @staticmethod
    def load_local_judgment_report(file_to_parse):
        """
        Load a file into a new browser
        :param file_to_parse: full path to the file to parse
        :return: a selenium browser object
        """
        html_source = os.path.join(PacerScraperUtils.pacer_files_dir, file_to_parse)
        assert os.path.exists(html_source) == True
        browser_filename = 'file://' + html_source
        browser = PacerScraperBase.get_webdriver()
        browser.get(browser_filename)
        return browser

    @staticmethod
    def make_judgment_index_case(d):
        """
        Make a PacerJudgmentIndexCase from a dict of key/value pairs extracted via _extract_row_contents function.
        Does not set the parent FK, up to the calling function to do this
        :param d: dict of relevant key/value pairs
        :return: PacerJudgmentIndexCase
        """
        import dateparser
        from .models import PacerJudgmentIndexCase
        if d.get('Document') == '':
            d['Document'] = 0
        judgment_object = PacerJudgmentIndexCase(case_number=d.get('Case number').strip(),
                                                 in_favor=d.get('In favor of'),
                                                 against=d.get('Against'),
                                                 amount=d.get('Amount'),
                                                 judgment_date=dateparser.parse(d.get('Date')),
                                                 document=d.get('Document'),
                                                 interest=d.get('Interest')[:-1],
                                                 court_cost=d.get('Court Cost'),
                                                 case_status=d.get('Case status'),
                                                 satisfication_date=dateparser.parse(d.get('Last updated date')))
        return judgment_object

    @staticmethod
    def get_judgment_index_report_period(browser):
        """
        Extract the report period from the judgment index report
        :param browser: selenium.webdriver
        :return: list of strs with dates
        """
        cell = browser.find_element_by_css_selector('body div#cmecfMainContent center center font b')
        report_dates = cell.text
        report_dates = report_dates.split(':')[1].strip().split('-')
        report_from = report_dates[0].split()[0]
        report_to = report_dates[1].split()[0]
        return report_from, report_to

    @staticmethod
    def enter_case_data_on_form(browser, case_num_str):
        """
        Enter a case number into the browser to conduct a search
        :param browser: the browser to work with with the page already loaded. This form will be submitted
        :param case_num_str: the case number to search on
        :return: None
        """
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as Ec
        from selenium.webdriver.support.ui import WebDriverWait
        import time

        case_num_str = case_num_str.split(' ')[0]  # parse out names and extra info after case numbers if they exists
        print(('Using case number: {}'.format(case_num_str)))
        print("Finding case number input box and clearing field!")
        time.sleep(1)
        case_num = browser.find_element_by_name('case_num')
        case_num.clear()
        print("Entering case number into form!")
        # time.sleep(3)
        case_num.send_keys(case_num_str)
        # time.sleep(3)
        find_case_btn = browser.find_element_by_id('case_number_find_button_0')
        find_case_btn.click()
        # time.sleep(3)

        try:  # not the best construct for this, but make it work first...
            cases_checkbox = WebDriverWait(browser, 1).until(Ec.presence_of_element_located((By.NAME, 'checkbox_0')))
            # time.sleep(3)
            cases_checkbox.send_keys(Keys.SPACE)
            # time.sleep(3)
        except:
            # print("couldn't find subcases - continuung")
            pass

        run_report_button_name = 'button1'
        run_report_button = browser.find_element_by_name(run_report_button_name)
        run_report_button.click()

    ###############

    @staticmethod
    def query_and_archive_judgment_report(date_from, date_to):
        """
        Run a search and archive the results to a file
        :param date_from: from date to use for search
        :param date_to: to date to use from search
        :return:
        """
        # type: (str, str) -> JudgmentIndexReport
        browser = PacerScraperBase.get_webdriver()
        PacerScraperUtils.pacer_login(browser)
        PacerScraperUtils.navigate_to_judgments_index_form(browser)
        PacerScraperBase.check_page_has_text(browser, r'Judgment Index Report')
        from_date_str = date_from
        to_date_str = date_to
        PacerScraperUtils.load_judment_report_index(browser, from_date_str, to_date_str)
        j_report = PacerScraperUtils.store_judgment_report(browser, from_date_str, to_date_str)
        return j_report # JudgmentIndexReport

    @staticmethod
    def case_already_processed(case_number):
        """
        Determine if the supplied case number has already been processed
        :param case_number: the case number to check
        :return: bool True if the case is processed
        """
        from .models import JudgmentIndexReport
        processed = False
        results = JudgmentIndexReport.objects.filter(pacerjudgmentindexcase__case_number__exact=case_number)
        if len(results) > 0:
            print(('Case already processed! {}'.format(case_number)))
            processed = True
        else:
            print('Did not find case. Processing...')
        return processed

    @staticmethod
    def build_judgment_index_report_from_local_file(local_archive_file):
        """
        Parse a local file to pull all of the judgment data into the db and onto the local file system
        :param local_archive_file: file to use for buulding the index report
        :return:
        """
        import dateparser
        import traceback
        from .models import JudgmentIndexReport
        import logging
        logger = logging.getLogger(__name__)

        browser = PacerScraperUtils.load_local_judgment_report(local_archive_file)
        browser2 = PacerScraperBase.get_webdriver()
        PacerScraperUtils.pacer_login(browser2)

        row_count = 0

        #build top level model
        report_from, report_to = PacerScraperUtils.get_judgment_index_report_period(browser)
        report_from = dateparser.parse(report_from)
        report_to = dateparser.parse(report_to)
        # judgment_idx_report = JudgmentIndexReport(date_from=report_from,
        #                                           date_to=report_to,
        #                                           archive_file=local_archive_file)
        # judgment_idx_report.save()
        judgment_idx_report = JudgmentIndexReport.objects.filter(date_from__exact=report_from,
                                                                date_to__exact=report_to)[0]

        #process rows from report
        for row in browser.find_elements_by_css_selector('div#cmecfMainContent center center table[width="100%"] tbody tr'):
            try:
                cells = row.find_elements_by_tag_name('td')
                if len(cells) > 0 and PacerScraperUtils.is_not_header_row(cells):  # and row_count < max_rows_to_process:
                    row_contents = PacerScraperUtils.extract_row_contents(cells)
                    is_case_of_interest = row_contents.get('Case status').strip() == PacerScraperUtils.no_payment_token
                    case_number = row_contents['Case number'].strip()
                    is_not_parsed = PacerScraperUtils.case_already_processed(case_number)
                    if case_number != '' and is_case_of_interest and not is_not_parsed:
                        judgment_object = PacerScraperUtils.make_judgment_index_case(row_contents)
                        logger.info("Parsed case number: {}".format(judgment_object.case_number))
                        # begin addition to pull remaining data from system
                        PacerScraperBase.navigate_to_query_form(browser2)
                        PacerScraperUtils.enter_case_data_on_form(browser2, judgment_object.case_number)
                        d = PacerScraperBase.archive_case_summary_data(browser2, PacerScraperUtils.pacer_files_dir)
                        judgment_object.alias_file = d[PacerScraperBase.alias_token]
                        judgment_object.case_summary_file = d[PacerScraperBase.case_summary_token]
                        judgment_object.party_file = d[PacerScraperBase.party_token]
                        # end addition
                        # print(judgment_object)
                        # self.assertNotEqual(judgment_object.case_number, '')
                        # log the above to a file if it happens
                        judgment_object.judgment_index_report = judgment_idx_report
                        judgment_object.save()
                        # self.assertNotEqual(judgment_object.party_file, '')
                        # log the above to a file if it happens
            # except IndexError as (errno, strerror):
            #     print("IndexError({}): {}".format(errno, strerror))
            except Exception as e:
                # import logging
                print("Unexpected error:", sys.exc_info()[0])
                logging.error(traceback.format_exc())
            if PacerScraperUtils.stop_processing_files():
                logger.info('Received file processing stop signal')
                return row_count
        row_count += 1
        return row_count

    @staticmethod
    def is_not_header_row(cells):
        """
        Determine if the row provided is a header row for a data set
        :param cells: the cells to check
        :return: true if the row does not contain header data
        """
        line_status = True
        for e in cells:
            if str(e.text).strip().find(PacerScraperUtils.case_number_token) > -1:
                line_status = False
        return line_status


class ScraperCommandGenerator:

    @staticmethod
    def generate_year_of_dates(year):
        """
        Generate a dates for the year provided. Generates three sets of dates for every month with 10 days each for each set
        :param year: the year to generate date ranges for
        :return:list of start and end dates
        """
        import calendar

        # year = 2017
        list_of_date_commands = []
        for month in range(1, 13):
            num_days = calendar.monthrange(year, month)[1]  # returns list with first weekday of month and number of days in month
            # print("{}/{}/{}".format(month, num_days, year))
            start_date = "{}/1/{}".format(month, year)
            end_date = "{}/10/{}".format(month, year)
            list_of_date_commands.append([start_date, end_date])
            start_date = "{}/11/{}".format(month, year)
            end_date = "{}/20/{}".format(month, year)
            list_of_date_commands.append([start_date, end_date])
            start_date = "{}/21/{}".format(month, year)
            end_date = "{}/{}/{}".format(month, num_days, year)
            list_of_date_commands.append([start_date, end_date])
        return list_of_date_commands


class PacerScraperValidator:

    @staticmethod
    def get_bankruptcy_index_report_num_cases_found(browser):
        # type: (selenium.webdriver) -> int
        """
        Extract the number of cases from the bankruptcy index report
        :param browser: selenium.webdriver
        :return: number of cases in report
        """
        import re
        src = browser.page_source
        exp = "There were\s*(\d+)\smatching cases"
        m = re.search(exp, src)
        try:
            num_cases = m.group(1)
        except AttributeError:
            num_cases = -1
        return num_cases

    @staticmethod
    def check_index_file_case_count(case_filename):
        """
        Determine the number of cases in the provided bankrupcy index case file
        :param case_filename: name of the file to parse
        :return: int number of cases found in the files
        """
        # type: (str) -> int
        import os

        bankruptcy_files_dir = PacerScraperBankruptcyUtils.bankruptcy_files_dir
        bankruptcy_file = os.path.join(bankruptcy_files_dir, case_filename)
        psutils = PacerScraperBankruptcyUtils
        dir = os.path.join(settings.MEDIA_ROOT, 'pacer_bankruptcy_idx')
        browser = psutils.load_local_bankruptcy_report(bankruptcy_file, dir)
        num_cases = PacerScraperValidator.get_bankruptcy_index_report_num_cases_found(browser)
        return num_cases

    @staticmethod
    def get_bankruptcy_index_report_period(case_filename):
        # type: (str) -> (str, str)
        """
        Alias of sorts for a function in scraper utils, returns date from and date to
        :param browser:
        :return: from_date, to_date
        """
        bankruptcy_files_dir = PacerScraperBankruptcyUtils.bankruptcy_files_dir
        bankruptcy_file = os.path.join(bankruptcy_files_dir, case_filename)
        psutils = PacerScraperBankruptcyUtils
        browser = psutils.load_local_bankruptcy_report(bankruptcy_file)

        return PacerScraperBankruptcyUtils.get_bankruptcy_index_report_period(browser)


class PacerScraperPartyBuilder:
    BkParty = namedtuple('BkParty', 'party_name party_type')
    archive_file_dir = None

    @staticmethod
    def build_party_list_from_party_file(party_file, browser=None):
        # type: (str) -> list
        """
        Build a list of party name and party type tuples from a supplied party file
        :param party_file: filename in the BK index folder containing the party data
        :return: list of BkParty
        """
        import traceback
        import re
        import logging
        from selenium.common.exceptions import TimeoutException

        logger = logging.getLogger(__name__)
        psutils = PacerScraperBankruptcyUtils
        if browser is None:
            browser = PacerScraperBankruptcyUtils.get_webdriver()
        party_list = []
        dir = PacerScraperBankruptcyUtils.bankruptcy_files_dir
        if not PacerScraperPartyBuilder.archive_file_dir is None:
            dir = PacerScraperPartyBuilder.archive_file_dir
        # logger.info('***** Using dir for parsing: {} *****'.format(dir))
        try:
            browser = psutils.load_local_bankruptcy_report(party_file, dir)
            for row in browser.find_elements_by_css_selector('table[cellspacing="10"] tbody tr'):
                try:
                    cells = row.find_elements_by_tag_name('td')
                    cell_data = cells[0].text
                    cell_data_list = cell_data.split('\n')
                    party_name = cell_data_list[0]
                    # party_type = cell_data_list[-1]
                    party_type = 'not parsed'
                    exp = "\(([A-Z].+)\)"
                    m = re.search(exp, cell_data)
                    if not m is None and (len(m.group(1))) > 0:
                        party_type = m.group(1)
                    bk_party = PacerScraperPartyBuilder.BkParty(party_name, party_type)
                    party_list.append(bk_party)
                    logger.info("------> Found party in file: {}".format(party_name))

                except Exception as e:
                    # import logging
                    print(("Unexpected error:", sys.exc_info()[0]))
                    logging.error(traceback.format_exc())
        except TimeoutException as e:
            logger.error('Encountered timeout exception while processing {}'.format(party_file))
        logger.info('>>>>>>>>> Returning this party list: {}'.format(party_list))
        return party_list

    @staticmethod
    def save_bankruptcy_party(case_number, bk_party):
        """
        Save data to the database related to a bankruptcy party information
        :param case_number: the case number the party belongs to
        :param bk_party: a PackerBankruptcyParty object
        :return: None
        """
        from django.db import transaction
        # type: (str, BkParty) -> None
        from .models import PacerBankruptcyIndexCase, PacerBankruptcyParty

        bk_case = PacerBankruptcyIndexCase.objects.filter(case_number=case_number)[0]
        with transaction.atomic():
            bk_case_party = PacerBankruptcyParty()
            bk_case_party.party_name = bk_party.party_name
            bk_case_party.party_type = bk_party.party_type
            bk_case_party.bankruptcy_index_case = bk_case
            bk_case_party.save()
            bk_case.party_file_processed = 'Y'
            bk_case.save()


    @staticmethod
    def save_bankruptcy_alias(case, alias):
        """
        Save an alias object for a case to a database
        :param case: The bankruptcy case
        :param alias: the alias associated with the provided case
        :return: None
        """
        # type: (str, str) -> None
        from .models import PacerBankruptcyIndexCase, PacerBankruptcyAlias

        bk_case = case  # PacerBankruptcyIndexCase.objects.filter(case_number=case_number)[0]
        bk_case_alias = PacerBankruptcyAlias()
        bk_case_alias.alias_name = alias
        bk_case_alias.bankruptcy_index_case = bk_case
        bk_case_alias.save()
        bk_case.alias_file_processed = 'Y'
        bk_case.save()

    @staticmethod
    def build_alias_list_from_alias_file(alias_file):
        # type: (str) -> list
        """
        Build a list of alias strings from a supplied party file
        :param alias_file: filename in the BK index folder containing the alias data
        :return: list of BkParty
        """
        import traceback
        psutils = PacerScraperBankruptcyUtils
        browser = psutils.load_local_bankruptcy_report(alias_file)
        alias_list = []
        for row in browser.find_elements_by_css_selector('table[cellpadding="0"] tbody tr'):
            try:
                alias = row.find_element_by_css_selector('td:nth-of-type(2)').text
                # print(alias)
                alias_list.append(alias)

            except Exception as e:
                # import logging
                print("Unexpected error:", sys.exc_info()[0])
                logging.error(traceback.format_exc())
        # print(alias_list)
        return alias_list

class PacerScraperUSDCPartyBuilder:
    BkParty = namedtuple('BkParty', 'party_name party_type')  # @TODO: fix BkParty def

    @staticmethod
    def build_party_list_from_party_file(party_file, browser=None):
        # type: (str) -> list
        """
        Build a list of party name and party type tuples from a supplied party file
        :param party_file: filename in the BK index folder containing the party data
        :return: list of BkParty
        """
        import traceback
        import re
        import logging
        from selenium.common.exceptions import TimeoutException

        logger = logging.getLogger(__name__)
        psutils = PacerScraperBankruptcyUtils
        if browser is None:
            browser = PacerScraperBankruptcyUtils.get_webdriver()
        dir = PacerScraperUtils.pacer_files_dir # @TODO: fix sister class's changes to dir defn
        # logger.info('***** Using dir for parsing: {} *****'.format(dir))
        party_list = []
        dir = PacerScraperUtils.pacer_files_dir
        if not PacerScraperPartyBuilder.archive_file_dir is None:
            dir = PacerScraperPartyBuilder.archive_file_dir
        try:
            browser = psutils.load_local_bankruptcy_report(party_file, dir, browser)
            for row in browser.find_elements_by_css_selector('table[cellpadding="15"] tbody tr'):
                try:
                    cells = row.find_elements_by_tag_name('td')
                    cell_data = cells[0].text
                    # logger.info('Parsing.......................................')
                    cell_data_list = cell_data.split('\n')
                    # logger.info("---------->>>>>>{}".format(cell_data_list))
                    party_name = cell_data_list[0]
                    # logger.info("Party name: {}".format(party_name))
                    # party_type = cell_data_list[-1]
                    party_type = 'not parsed'
                    exp = "\(([A-Z].+)\)"
                    m = re.search(exp, cell_data)
                    if not m is None and (len(m.group(1))) > 0:
                        party_type = m.group(1)
                    # logger.info("Party type: {}".format(party_type))
                    bk_party = PacerScraperPartyBuilder.BkParty(party_name, party_type)
                    logger.info("BkParty data struct: {}".format(bk_party))
                    party_list.append(bk_party)

                except Exception as e:
                    # import logging
                    print("Unexpected error:", sys.exc_info()[0])
                    logging.error(traceback.format_exc())
        except TimeoutException as e:
            print(('Encountered timeout exception while processing {}'.format(party_file)))
        # logger.info("Elements in list being returned after parsing doc: {}".format(party_list))
        return party_list


    @staticmethod
    def save_usdc_party(usdc_case, usdc_party):
        """
        Save info about a USDC party to the database
        :param usdc_case: the usdc case number associated with the party
        :param usdc_party: the party info to store to the database
        :return: None
        """
        from django.db import transaction
        # type: (str, BkParty) -> None
        from .models import PacerJudgmentIndexCase, PacerJudgmentParty

        # usdc_case = PacerJudgmentIndexCase.objects.filter(case_number=case_number)[0]
        usdc_case_party = PacerJudgmentParty()
        usdc_case_party.judgment_index_case = usdc_case
        usdc_case_party.party_name = usdc_party.party_name
        usdc_case_party.party_type = usdc_party.party_type
        usdc_case_party.bankruptcy_index_case = usdc_case
        usdc_case_party.save(using=settings.USDCSEARCH_DB)
        # usdc_case.party_file_processed = 'Y'
        # usdc_case.save(using=settings.USDCSEARCH_DB)


    @staticmethod
    def save_usdc_alias(case, alias):
        """
        Save an alias with a case
        :param case: The USDC case to associate with the alias
        :param alias: the alias to store to the database
        :return: None
        """
        # type: (str, str) -> None
        from .models import PacerJudgmentIndexCase, PacerJudgmentAlias

        usdc_case = case  # PacerJudgmentIndexCase.objects.filter(case_number=case_number)[0]
        usdc_case_alias = PacerJudgmentAlias()
        usdc_case_alias.alias_name = alias
        usdc_case_alias.judgment_index_case = usdc_case
        usdc_case_alias.save()
        usdc_case.alias_file_processed = 'Y'
        usdc_case.save()

    @staticmethod
    def build_alias_list_from_alias_file(alias_file):
        # type: (str) -> list
        """
        Build a list of alias strings from a supplied party file
        :param alias_file: filename in the BK index folder containing the alias data
        :return: list of BkParty
        """
        import traceback
        psutils = PacerScraperBankruptcyUtils
        browser = psutils.load_local_bankruptcy_report(alias_file)
        alias_list = []
        for row in browser.find_elements_by_css_selector('table[cellpadding="0"] tbody tr'):
            try:
                alias = row.find_element_by_css_selector('td:nth-of-type(2)').text
                # print(alias)
                alias_list.append(alias)

            except Exception as e:
                # import logging
                print("Unexpected error:", sys.exc_info()[0])
                logging.error(traceback.format_exc())
        # print(alias_list)
        return alias_list


class SSHManager:

    def __init__(self):
        pass

    @staticmethod
    def get_file_contents_from_ssh(ssh_client, file_path):
        """
        Connect to a remote server via ssh to get the file contents
        :param ssh_client: the ssh cclient to use
        :param file_path: the file path/name on the remote server
        :return: contents of the remote file
        """
        sftp_client = ssh_client.open_sftp()
        remote_file = sftp_client.open(file_path)
        try:
            remote_file_contents = remote_file.read()
        finally:
            remote_file.close()
        # ssh_client.close()
        return remote_file_contents


class ReportHelper:

    @staticmethod
    def add_bkcy_exact_match_only(cases, searchname):
        """
        Fukter a list of cases down to exact match only. For company names this request returns the original case list
        :param cases: the list of cases to parse
        :param searchname: the search name to use for processing the list
        :return: a list of filtered results
        """

        exact_match_cases = []
        if searchname.first_name:
            # party_name_match_list = searchname.full_search_party_name.split()
            searchname_first_name = searchname.first_name.upper().split()[0]
            searchname_last_name = searchname.last_name.upper().split()[-1]
            for case in cases:
                for party_name in case.name_list:
                    party_name = party_name.upper()
                    if searchname_first_name in party_name and searchname_last_name in party_name:
                        exact_match_cases.append(case)
                        break
        else:
            exact_match_cases = cases  # for company names search everything
        return exact_match_cases

    @staticmethod
    def parse_attorney_from_debtor_details(party_row_element):
        """
        Extract any attorney info present from a string containing debtor info
        :param party_row_element: the row element to parse for attorney data
        :return: parsed lines containing attorney data
        """
        relevant_lines = []
        attorney_cell = party_row_element.find_elements_by_tag_name('td')
        if len(attorney_cell) > 2:
            attorney_info = attorney_cell[2].text
            attorney_lines = attorney_info.split('\n')
            not_found_phone = True
            for line in attorney_lines:
                if not_found_phone:
                    relevant_lines.append(line)
                    if '(' in line:
                        not_found_phone = False
        if not relevant_lines:
            relevant_lines = ['No attorney listed']
        return relevant_lines

    @staticmethod
    def parse_party_from_debtor_details(party_row_element):
        """
        Parse party info from debtor details
        :param party_row_element: the lines of debtor data to parse
        :return: any relevant party info detected
        """
        import re
        party_info = party_row_element.find_elements_by_tag_name('td')[0].text
        # party_info_split = party_info.split('\n')[0]  # just grab the party name, skip date and party type fields

        party_info_split = party_info.split('\n')  # just grab the party name, skip date and party type fields
        party_info_cleaned = []
        for line in party_info_split:
            non_name_match = None
            m = re.search('\(.+\)', line)
            if m:
                non_name_match = m.group(0)
            # if '(' in line and ')' in line:
            if m and len(non_name_match) > 4:  # this is a date; sometimes see text like ALFONSO GOMEZ (1)
                pass
            elif 'added' in line.lower():
                pass
            else:
                party_info_cleaned.append(line)

        if len(party_info_cleaned) == 1:
            party_info_cleaned.append("(No Address)")
        return '\n'.join(party_info_cleaned)

    @staticmethod
    def parse_creditor_from_party_details(party_row_element):
        """
        Parse creditor info from the provided party details
        :param party_row_element: the party data to parse
        :return: creditor data detected from the provided row data
        """
        party_info = party_row_element.find_elements_by_tag_name('td')[0].text
        # party_info_split = party_info.split('\n')[0]  # just grab the party name, skip date and party type fields

        party_info_split = party_info.split('\n')  # just grab the party name, skip date and party type fields
        party_info_cleaned = []
        for line in party_info_split:
            if '(' in line and ')' in line:
                pass
            elif 'added' in line.lower():
                pass
            else:
                party_info_cleaned.append(line)

        # if len(party_info_cleaned) == 1:
        #     party_info_cleaned.append("(No Address)")
        return '\n'.join(party_info_cleaned)

    @staticmethod
    def parse_trustee_from_party_details(party_row_element):
        """
        Parse trustee info from the provided party details
        :param party_row_element: the party data to parse
        :return: trustee data detected from the provided row data
        """
        trustee_cell = party_row_element.find_elements_by_tag_name('td')
        if len(trustee_cell) > 0:
            trustee_info = trustee_cell[0].text
        extracted_trustee_data = None
        if not 'TERMINATED' in trustee_info:
            extracted_trustee_data = trustee_info.split('\n')[0]
            # print('******** Extracted trustee data: {} ********'.format(extracted_trustee_data))
        else:
            xx = trustee_info.split('\n')[0]
            # print('******** This trustee {} has been terminated, skipping... ********'.format(xx))
        # print('Returning {} for trustee data'.format(extracted_trustee_data))
        return extracted_trustee_data


class LiveBkcySearchMatchResults(Enum):
    MATCH_MULTIPLE = 'match_multiple'
    MATCH_SINGLE = 'match_single'
    NO_MATCHES = 'no_matches'


class PacerScraperLive:

    def _enter_case_data_on_form(self, browser, first_name, last_name):
        """
        Enter the last name and first name on the search form
        :param browser: selenium.webdriver instance
        :param first_name: the first name to enter on the form
        :param last_name: the last name to enter on the form
        :return: None
        """

        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as Ec
        from selenium.webdriver.support.ui import WebDriverWait
        print(('Name used for search: {} {}'.format(first_name, last_name)))
        last_name_input = browser.find_element_by_name('last_name')
        last_name_input.send_keys(last_name)
        time.sleep(1)
        first_name_input = browser.find_element_by_name('first_name')
        first_name_input.send_keys(first_name)
        time.sleep(2)

        print('Selecting party only for input')
        type_input = browser.find_element_by_name('person_type')
        type_input.send_keys('P')
        time.sleep(2)

        print('Submitting form')
        run_query_button = browser.find_element_by_name('button1')
        run_query_button.click()
        time.sleep(5)

    def _determine_search_results_type(self, browser):
        """
        Determine what type of results were returned from a search based on the browser contents
        :param browser: a selenium.webdriver instance
        :return: an Enum of LiveBkcySearchMatchResults indicating what type of results were detected
        """
        page_text = browser.page_source
        if "Select a Case" in page_text:
            # print('Got results page containing multiple cases')
            return LiveBkcySearchMatchResults.MATCH_MULTIPLE
        elif "No match found" in page_text:
            # print('No matches found')
            return LiveBkcySearchMatchResults.NO_MATCHES
        # elif "Judge" in page_text:
        else:
            # print('Matched single case')
            return LiveBkcySearchMatchResults.MATCH_SINGLE


    def _extract_row_contents(self, cells, last_party_name_block):
        """
        Extracts the row contents for a case into a dict.
        Row contents comes from the case summary index
        :param cells: td elements pulled from a tr from the report
        :return: dict of cells
        """
        d = None
        last_party_name = ''

        if len(cells) > 6:
            party_name = cells[0].text.strip()
            case_number = cells[1].text.strip()
            case_title = cells[2].text.strip()
            chapter_lead_bk = cells[3].text.strip()
            date_filed = cells[4].text.strip()
            party_role = cells[5].text.strip()
            date_closed = cells[6].text.strip()

            if '(pty)' in last_party_name_block:
                d = {'Party Name': party_name, 'Party Role': party_role, 'Case no':case_number, 'Case Title':case_title,
                     'Chapter':chapter_lead_bk, 'Filed':date_filed, 'Closed':date_closed}
        return d


    def _extract_from_case_list(self, browser):
        """
        Assumes the browser is on the case list page and extracts case numbers and other data from page
        :param browser:
        :return: list of dicts containing matched case data
        """
        from pacerscraper.utils import PacerScraperBankruptcyUtils as psutils

        last_party_name_block = None
        matched_case_list = []
        for row in browser.find_elements_by_css_selector('table[cellspacing="10"] tbody tr')[3:]:
            cells = row.find_elements_by_tag_name('td')
            # if do_process_row(row_count, max_rows_to_process) and psutils.is_not_header_row(cells):
            if psutils.is_not_header_row(cells):
                stripped_party_name_block = cells[0].text.strip()
                if last_party_name_block is None:  # handle first iteration
                    last_party_name_block = stripped_party_name_block
                if last_party_name_block:
                    case_summary_dict = self._extract_row_contents(cells, last_party_name_block)
                    print(('Extracted row contents: {}'.format(case_summary_dict)))
                    matched_case_list.append(case_summary_dict)
                if stripped_party_name_block:
                    last_party_name_block = stripped_party_name_block
        return matched_case_list

    def _extract_case_from_page(self, browser):
        """
        Extracts info from the page for a single judgment. Returns a list to be consistent with other function
        :param browser2:
        :return:
        """
        import re

        case_list = []
        d = {}
        case_number_element = browser.find_elements_by_css_selector('center b')
        d['Case no'] = case_number_element[0].text
        # extract case filed date in case it's needed
        full_case_header_text = browser.find_elements_by_css_selector('center')[0].text

        case_filed_date = None
        regex = 'Date filed:\s+(\d+\/\d+\/)(\d+)'
        m = re.search(regex, full_case_header_text)
        if m and len(m.group(0)) > 0:
            case_filed_date = m.group(1).strip() + m.group(2).strip()[:2]  # make the date look like the case list date
            d['Filed'] = case_filed_date

        case_list.append(d)
        return case_list

    def _scrape_live_name(self, firstname, lastname):
        """
        Run a live search on Pacer to look for matching debtor cases with first and last names provided
        :param firstname:
        :param lastname:
        :return:
        """
        # type: (str, str) -> []
        browser2 = None
        matched_case_list = []
        try:
            browser2 = PacerScraperBankruptcyUtils.get_webdriver()
            time.sleep(2)
            PacerScraperBankruptcyUtils.pacer_login(browser2)
            time.sleep(2)
            # PacerScraperBankruptcyUtils.navigate_to_query_form(browser2)

            browser2.get(PacerScraperBankruptcyUtils.pacer_bankruptcy_search_form_url)
            time.sleep(2)

            self._enter_case_data_on_form(browser2, firstname, lastname)
            search_match_type = self._determine_search_results_type(browser2)
            print(("Type of results page matched {}".format(search_match_type)))

            if search_match_type == LiveBkcySearchMatchResults.MATCH_MULTIPLE:
                matched_case_list = self._extract_from_case_list(browser2)
            elif search_match_type == LiveBkcySearchMatchResults.MATCH_SINGLE:
                matched_case_list = self._extract_case_from_page(browser2)

        except NoSuchElementException:
            print('Encountered error while trying to fetch data from server.')
            raise
        finally:
            browser2.close()
        return matched_case_list
