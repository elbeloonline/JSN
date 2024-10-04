from collections import namedtuple
from enum import Enum

from django.conf import settings
from selenium import webdriver

from dobscraper.scnjscraper import SCNJScraper


class SpecCodes(Enum):
    CIVIL = 'CIVIL'
    VENUE = 'VENUE'


class DocketListTypes:
    STATE = 'STATE_DOCKET_LIST'
    BANKRUPTCY = 'BANKRUPTCY_DOCKET_LIST'
    USDC = 'USDC_DOCKET_LIST'


class JSNCacheKeys:
    SCNJ_RESULTS_CACHE_KEY = 'state_query_results'
    BKCY_RESULTS_CACHE_KEY = 'bkcy_query_results'
    USDC_RESULTS_CACHE_KEY = 'usdc_query_results'

class SCNJSearchUtils:
    # def __init__(self):
    #     """
    #     Use Firefox instead of Chrome to address compatibility issue with current drivers installed
    #     https://stackoverflow.com/questions/54558321/webdriverexception-message-newsession-with-geckodriver-firefox-v65-and-seleniu
    #     :return:
    #     """
    #     import os
    #     gecko_path = os.path.join('.', 'bin', 'geckodriver')
    #     self.browser = webdriver.Firefox(executable_path=gecko_path)

    # def __del__(self):
    #     self.browser.quit()

    def _match_dob_search_cases(self, cases, scraped_judgment_dobs):
        """
        Figure out which cases need to be searched to retrieve DOBs
        :param cases: Queryset of cases.
        :return List: Judgments that need to be searched for DOBs, in format XX-XXXXXX-XX
        """
        live_scrape_dob_cases = []
        for case_instance in cases:
            tagged_case = False
            if case_instance.docketed_judgment_type_code[:2] == 'PD':  # public defender
                tagged_case = True
            elif case_instance.docketed_judgment_type_code[:2] == 'CS':  # child support
                tagged_case = True
            elif 'MOTOR VEHICLE' in str(case_instance.case_title).upper():  # motor vehicle
                tagged_case = True
            elif 'PROBATION' in str(case_instance.case_title).upper():  # probation
                tagged_case = True

            if int(case_instance.docketed_judgment_yy) < 91 and int(case_instance.docketed_judgment_cc) == 19:
                tagged_case = False  # state site doesn't have years before 1990
            import time
            current_yy = int(time.strftime("%y", time.localtime()))
            yy_difference_threshold = current_yy - int(case_instance.docketed_judgment_yy)  # @TODO: reference case__party__ptydebt_status_code for revived cases (03)
            if int(case_instance.docketed_judgment_cc) == 20 and yy_difference_threshold <= 20:
                tagged_case = True  # 20 year cutoff for scraping DOBs


            if tagged_case:
                j_num = '{}{}{}'.format(case_instance.docketed_judgment_type_code,
                                          case_instance.docketed_judgment_seq_num,
                                          case_instance.docketed_judgment_yy)
                if not scraped_judgment_dobs.get(j_num, None):  # redundant check - done in external function
                    j_num_dash = '{}-{}-{}'.format(case_instance.docketed_judgment_type_code,
                                              case_instance.docketed_judgment_seq_num,
                                              case_instance.docketed_judgment_yy)
                    print(('Running DOB search for judgment {}'.format(j_num_dash)))
                    live_scrape_dob_cases.append(j_num_dash)
        print(('Here is the final list of cases to be scraped: {}'.format(live_scrape_dob_cases)))
        return live_scrape_dob_cases

    def run_dob_search(self, cases, order_id, scraped_judgment_dobs):
        """
        Gets DOBs for a judgment by running a search on the SCNJ system
        :param cases: Queryset of cases.
        :param order_id:
        :param judgment_dobs: dict of judgment nums without dashes and dobs
        :return: dictionary of judgment numbers without dashes and matching DOB
        """
        judgment_dobs = {}  # @TODO: make sure this doesn't inadvertently break something
        dob_live_scrape_cases = self._match_dob_search_cases(cases, scraped_judgment_dobs)
        if len(dob_live_scrape_cases) > 0:
            print('Getting ready to execute _parse_multiple_judgments2')
            judgment_dobs = self._parse_multiple_judgments2(dob_live_scrape_cases, order_id)
            print('Finished executing _parse_multiple_judgments2')
        # merge pdf scraped judgments dict and live scraped dict
        z = scraped_judgment_dobs.copy()
        z.update(judgment_dobs)
        # return judgment_dobs
        return z

    def _submit_dob_scrape_job(self, judgments, order_id):
        """
        Submits a list of judgments to scrape for DOBs
        :param judgments:
        :param order_id:
        :return:
        """
        import json
        import requests

        api_post_job_endpoint = settings.DOB_POST_JOB_ENDPOINT
        print(('API post endpoint is {}'.format(api_post_job_endpoint)))
        PARAMS = {
            "order_id": order_id,
            "judgments": ','.join(judgments)
        }
        headers = {'Content-type': 'application/json'}
        r = requests.post(url=api_post_job_endpoint, data=json.dumps(PARAMS), headers=headers )
        # @TODO: assert job was submitted successfully

    def _get_dob_scrape_complete(self, order_id):
        """
        Checks status of job to see if scraping is complete
        :param order_id:
        :return:
        """
        import requests

        api_get_job_status_endpoint = settings.DOB_JOB_STATUS_ENDPOINT.format(order_id)
        r = requests.get(url=api_get_job_status_endpoint)
        data = r.json()
        if data['message'] == 'waiting':
            return False
        else:
            return True

    def _get_dob_scrape_results(self, order_id):
        """
        Gets the results from a DOB scraping run attached to user supplied order id
        Returns a list of judgments and dobs
        :param order_id:
        :return:
        """
        import requests
        api_get_job_results_endpoint = settings.DOB_JOB_RESULT_ENDPOINT.format(order_id)
        r = requests.get(url=api_get_job_results_endpoint)
        data = r.json()
        parsed_dobs = {}
        for k,v in list(data.get('dob_data', {}).items()):
            new_key = k.replace('-','')  # remove hyphens
            parsed_dobs[new_key] = v

        return parsed_dobs

    def _parse_multiple_judgments2(self, judgments, order_id):
        """
        Return DOBs for list of SCNJ judgments
        :param judgments: list of judgments, formatted like PD-003074-09
        :return: dictionary of judgment numbers without dashes and matching DOB
        """
        from time import sleep
        judgment_dobs = {}
        l = judgments
        n = 50  # want lists of this size
        split_judgments = [l[i:i + n] for i in range(0, len(l), n)]

        for judgments_part in split_judgments:
            self._submit_dob_scrape_job(judgments_part, order_id)
            while not self._get_dob_scrape_complete(order_id):
                sleep(5)
            # judgment_dobs = self._get_dob_scrape_results(order_id)
            judgment_dobs.update(self._get_dob_scrape_results(order_id))
        return judgment_dobs

    # def _parse_multiple_judgments(self, judgments):
    #     """
    #     Return DOBs for list of SCNJ judgments
    #     :param judgments: list of judgments, formatted like PD-003074-09
    #     :return: dictionary of judgment numbers without dashes and matching DOB
    #     """
    #     scraper = SCNJScraper(self.browser)
    #     scraper.login_and_solve(scraper)
    #     # tab navigation
    #     judgment_dobs = {}
    #     for i, judg in enumerate(judgments):
    #         if (i+1) % 7 == 0:
    #             scraper.login_and_solve(scraper)
    #         scraper.navigate_to_judgment_tab()
    #         judgment = SCNJScraper.split_judgment_by_dash(judg)
    #         scraper.enter_judgment_and_search(judgment)
    #         # self.assertIn('Judgment Record Search Results', scraper.browser.page_source)
    #         scraper.navigate_to_judgment_details()
    #         # self.assertIn('Judgment Search Result Details', scraper.browser.page_source)
    #         # move to new test for date of birth scrape
    #         matched_names = scraper.click_debtor_link()
    #         # dob = scraper.scrape_date_of_birth()
    #         dob = ""
    #         if len(matched_names) > 0:
    #             dob = matched_names[0].dob
    #         # self.assertIsNotNone(dob)
    #         print('DOB number {} scraped - {}'.format(i, dob))
    #         judgment_dobs[''.join(judgment)] = dob
    #     return judgment_dobs


class PacerSearchUtils:
    BkNameMatch = namedtuple('BkNameMatch', 'case_number party_name')
    BkNameMatchCaseList = namedtuple('BkNameMatchCaseList', 'case_number name_list')

    @staticmethod
    def load_parties_from_sql_file(cursor, filename):
        """
        Previously used for bkcy tests
        :param cursor:
        :param filename:
        :return:
        """
        import os
        from django.conf import settings

        filename = os.path.join(settings.MEDIA_ROOT, filename)
        f = open(filename)
        cursor.execute(f.read())
        cursor.close()  # VERY IMPORTANT!
        f.close()

    @staticmethod
    def search_bankruptcy_party_name(searchname, party_type='Defendant'):
        """
        Search for a bkcy party name in the relational or elasticsearch database
        :param searchname: orders.models.SearchName used for lookup
        :param party_type: the str to match on in the data file describing the party type
        :return: tuple, list of matches and a dict containing bkcy data
        """
        # type: (orders.models.SearchName, str) -> nameviewer.utils.PacerSearchUtils.BkNameMatch[], dict

        # search_party = PacerBankruptcyParty.objects\
        #     .filter(party_type=party_type)\
        #     .filter(party_name__contains=first_name)\
        #     .filter(party_name__contains=last_name)
        from pacerscraper.models import BankruptcyReportQueryManager as bq
        from django.conf import settings

        first_name = searchname.first_name
        last_name = searchname.last_name
        print(("First and last name supplied for query: {} {}".format(first_name, last_name)))
        # searchname = SearchName(first_name=first_name, last_name=last_name)
        print(("Search name used for query: {}".format(searchname.first_name + " " + searchname.last_name)))
        if settings.USE_ELASTICSEARCH_BKCY:
            search_party, bk_case_dict = bq.query_database_by_searchname_details4(searchname)
        else:
            search_party, bk_case_dict = bq.query_database_by_searchname_details3(searchname)
        print(("Search party details: {}".format(search_party)))

        matches = []
        for name_match in search_party:
            party_name = name_match.party_name
            print('match.')
            case_number = name_match.bankruptcy_index_case.case_number
            matched_name_case = PacerSearchUtils.BkNameMatch(case_number, party_name)
            matches.append(matched_name_case)
        return matches, bk_case_dict  # bk_case_dict contains a dict of db_ref and case_model

    @staticmethod
    def search_patriot_party_name(searchname):
        """
        Search for a patriot party name in the database
        :param searchname: orders.models.SearchName used for lookup
        :return: patriot.models.
        """
        import logging
        from patriot.models import PatriotReportQueryManager as pq
        from orders.models import SearchName

        logger = logging.getLogger(__name__)
        first_name = searchname.first_name
        last_name = searchname.last_name
        logging.info("First and last name supplied for query: {} {}".format(first_name, last_name))
        searchname = SearchName(first_name=first_name, last_name=last_name)
        search_results = pq.query_database_by_searchname_details(searchname)
        logging.info("Search results details: {}".format(search_results))
        return search_results

    @staticmethod
    def search_usdc_party_name(searchname, party_type='Defendant'):
        """
        Look for a USDC party name
        :param searchname: orders.models.SearchName used for lookup
        :param party_type: the str to match on in the data file describing the party type
        :return:
        """
        # type: (orders.models.SearchName, str) -> nameviewer.utils.PacerSearchUtils.BkNameMatch[], dict

        # search_party = PacerBankruptcyParty.objects\
        #     .filter(party_type=party_type)\
        #     .filter(party_name__contains=first_name)\
        #     .filter(party_name__contains=last_name)
        from pacerscraper.models import UsdcReportQueryManager as uq, PacerJudgmentParty
        from django.conf import settings

        first_name = searchname.first_name
        last_name = searchname.last_name
        print(("First and last name supplied for query: {} {}".format(first_name, last_name)))
        # searchname = SearchName(first_name=first_name, last_name=last_name)
        print(("Search name used for query: {}".format(searchname.first_name + " " + searchname.last_name)))
        search_party, bk_case_dict = uq.query_database_by_searchname_details3(searchname)
        print(("Search party details: {}".format(search_party)))
        print(("Search party details (dict): {}".format(bk_case_dict)))

        matches = []
        for name_match in search_party:
            print('match.')
            # case_number = name_match.judgment_index_case.case_number
            # party_name = name_match.party_name
            # matched_name_case = PacerSearchUtils.BkNameMatch(case_number, party_name)
            # matches.append(matched_name_case)
            case_id = name_match.judgment_index_case.id
            print(('Using case id {} for query'.format(case_id)))
            case_number = name_match.judgment_index_case.case_number
            # case_parties =  PacerJudgmentParty.objects.filter(judgment_index_case_id=case_id)\
            #     .filter(Q(party_type__icontains='debtor') | Q(party_type__icontains='defendant'))
            case_parties =  PacerJudgmentParty.objects.using(settings.USDCSEARCH_DB).\
                filter(judgment_index_case_id=case_id)
            print(('Filter on matched name returned {} parties.'.format(len(case_parties))))
            for party in case_parties:
                print('Adding party to new name match list.')
                matched_name_case = PacerSearchUtils.BkNameMatch(case_number, party.party_name)
                matches.append(matched_name_case)

        return matches, bk_case_dict  # bk_case_dict contains a dict of db_ref and case_model

    @staticmethod
    def search_bankruptcy_alias_name(searchname):
        """
        Run a BKCY search on an alias
        :param searchname: the first and last name to use for the search
        :return: list of BkNameMatch matches
        :rtype: list[BkNameMatch]
        """
        from pacerscraper.models import PacerBankruptcyAlias

        search_party = PacerBankruptcyAlias.objects\
            .filter(alias_name__contains=searchname.first_name)\
            .filter(alias_name__contains=searchname.last_name)
        # return search_party
        matches = []
        for name_match in search_party:
            print('match.')
            case_number = name_match.bankruptcy_index_case.case_number
            alias_name = name_match.alias_name
            matched_name_case = PacerSearchUtils.BkNameMatch(case_number, alias_name)
            matches.append(matched_name_case)
        return matches

    @staticmethod
    def name_from_order_id(order_id):
        """
        Return search names associated with an order id
        :param order_id: the id of the order to use for the lookup
        :return: set of search names
        """
        from orders.models import Order
        order = Order.objects.get(id=order_id)
        # search_name = order.searchname_set.first()  # @TODO: process all rows
        # first_name = search_name.first_name
        # last_name = search_name.last_name
        # company_name = search_name.company_name
        #
        # return first_name, last_name, company_name
        return order.searchname_set

    @staticmethod
    def run_name_search(searchname, search_type):
        """
        Run a name search of type search_type for searchname
        :param searchname: Name to search by
        :param search_type: type of search to run
        :return: tuple of a dict with namesearch results and a list of matched cases
        """
        from django.core.cache import cache
        from statereport.models import StateReportQueryManager
        from nameviewer.windward import ReportTypes
        bankruptcy_list = []  # temp to produce final dict
        bankruptcy_dict = {}
        matched_cases_dict = {}
        usdc_list = []  # temp to produce final dict
        usdc_dict = {}
        state_list = []
        state_hv_list = []
        patriot_dict = {}

        if search_type == ReportTypes.PATRIOT:
            if searchname.first_name != '':
                patriot_results = PacerSearchUtils.search_patriot_party_name(searchname)
                patriot_dict[str(searchname)] = patriot_results

        if search_type == ReportTypes.BANKRUPTCY or search_type == ReportTypes.BKCY_XLSX:
            if searchname.first_name != '':
                # can't pickle querysets (in this version of django?)
                # PicklingError: Can't pickle <class 'nameviewer.utils.BkNameMatch'>: attribute lookup nameviewer.utils.BkNameMatch failed
                bk_party_results, matched_cases_dict = PacerSearchUtils.search_bankruptcy_party_name(searchname)
                ordered_party_results = PacerSearchUtils.order_bk_party_results(bk_party_results, searchname)
                bankruptcy_list.extend(ordered_party_results)
                bk_alias_results = PacerSearchUtils.search_bankruptcy_alias_name(searchname)
                bankruptcy_list.extend(bk_alias_results)
                bankruptcy_dict = PacerSearchUtils.condense_case_list(bankruptcy_list)

        if search_type == ReportTypes.USDC or search_type == ReportTypes.USDC_XLSX:
            if searchname.first_name != '':
                usdc_party_results, matched_cases_dict = PacerSearchUtils.search_usdc_party_name(searchname)
                usdc_list.extend(usdc_party_results)
                # @TODO: need to handle aliases
                # bk_alias_results = PacerSearchUtils.search_bankruptcy_alias_name(searchname)
                # usdc_list.extend(bk_alias_results)
                usdc_dict = PacerSearchUtils.condense_case_list(usdc_list)
                print(('Final dict for defendant names after condensing list: {}'.format(usdc_dict)))

        if search_type == ReportTypes.STATE or search_type == ReportTypes.XLSX:
            # @TODO: don't call this a second time for XLSX tasks
            # use https://testdriven.io/blog/django-caching/
            print(('Processing name: {}'.format(searchname)))
            # if search_type == ReportTypes.STATE:
            #     state_list = StateReportQueryManager.query_database_by_searchname_details(searchname, True)
            #     cache.set(JSNCacheKeys.SCNJ_RESULTS_CACHE_KEY, state_list)
            # else:
            #     state_list = cache.get(JSNCacheKeys.SCNJ_RESULTS_CACHE_KEY, None)
            state_list = StateReportQueryManager.query_database_by_searchname_details(searchname, True)

        if search_type == ReportTypes.STATE_HIGH_VALUE:
            from statereport.utils import StateReportNameSearchUtils
            print(('Processing name: {}'.format(searchname)))
            # state_hv_list = StateReportQueryManager.query_database_by_searchname_details_high_value(searchname, True)
            state_hv_list = StateReportNameSearchUtils.query_high_value_judgments(searchname)

        name_search_results = {
            'search_name': "{} {}".format(searchname.first_name, searchname.last_name),
            'bankruptcy_names': bankruptcy_dict,  # dict of PacerSearchUtils.BkNameMatch[],
            'usdc_names': usdc_dict,
            'state_names': state_list,
            'state_names_hv': state_hv_list,
            'patriot_names': patriot_dict,
        }
        return name_search_results, matched_cases_dict  # bk_case_dict contains a dict of db_ref and case_model

    @staticmethod
    def condense_case_list(namematch_case_list):
        """
        Condense a list of potentially duplicate cases into a set and maintain their original order
        :param namematch_case_list: a list of cases to process
        :return: a list of condensed cases
        """
        from collections import OrderedDict
        # d = {}
        d = OrderedDict()
        for match in namematch_case_list:
            matched_names = d.get(match.case_number, [])
            matched_names.append(match.party_name)
            d[match.case_number] = matched_names
        # return d
        condensed_list = []
        for k,v in list(d.items()):
            condensed_list.append(PacerSearchUtils.BkNameMatchCaseList(k, v))
        return condensed_list

    @staticmethod
    def order_bk_party_results(bk_party_results, searchname):
        """
        Order Bankruptcy party results by exact name match then everything else
        :param bk_party_results: List[PacerSearchUtils.BkNameMatch]
        :param searchname: search name object used when generating the original order
        :return:
        """
        first_name = searchname.first_name.upper().split()[0]
        last_name = searchname.last_name.upper().split()[-1]
        exact_match_names = []
        variation_match_names = []
        for party in bk_party_results:
            party_split_name_list = party.party_name.upper().split()
            if first_name in party_split_name_list:
                party_split_name_list.remove(first_name)
            if last_name in party_split_name_list:
                party_split_name_list.remove(last_name)
            for n in party_split_name_list:
                if len(n) <= 2:
                    party_split_name_list.remove(n)
            # add BkNameMatch to correct list
            if len(party_split_name_list) == 0:
                exact_match_names.append(party)
            else:
                variation_match_names.append(party)
        ordered_name_matches = exact_match_names + variation_match_names
        return ordered_name_matches

class NameAliasType(Enum):
    SURNAME = 'surname'
    MALE = 'male'
    FEMALE = 'female'

class NameAliasUtils:
    @staticmethod
    def load_scored_names(name_select, name_type):
        """
        Return a list of names ordered by descending score
        :param name_select: a name to use for the alias lookup routine
        :param name_type: one of 'surname' or 'forename'
        :return:
        """
        from django.conf import settings
        from orders.models import Surname, Forename

        if name_type == 'surname':
            return Surname.objects.using(settings.NAMESEARCH_DB).filter(name=name_select).order_by('-score')
        else:
            return Forename.objects.using(settings.NAMESEARCH_DB).filter(name=name_select).order_by('-score')

    @staticmethod
    def add_new_alias(name_type, name_select, new_name_alias):
        """
        Add a new alias to the name dictionary
        :param name_type: the type of name to add = one of 'surname' or 'forename'
        :param name_select: the base name to use when adding the new alias
        :param new_name_alias: the new alias to add to the name lookup dictionary
        :return:
        """
        from orders.models import Surname, Forename
        from django.conf import settings

        name_select = name_select.lower()
        new_name_alias = new_name_alias.lower()
        new_name_score = 200
        defaults = {'score': new_name_score, 'deleted': 'N', 'nickname': 'N' }
        if name_type == 'surname':
            name_alias, created = Surname.objects.using(settings.NAMESEARCH_DB).get_or_create(name=name_select,
                                                                                     name_match=new_name_alias,
                                                                                     defaults = defaults)
            if not created:
                sql = "update surnames set score = {}, deleted = 'N' where name = %s and name_match = %s".format(new_name_score)
                from django.db import connections
                with connections[settings.NAMESEARCH_DB].cursor() as cursor:
                    cursor.execute(sql, [name_select, new_name_alias])
        else:
            # # name_alias = Forename.objects.using(settings.NAMESEARCH_DB).update_or_create(name=name_select,
            # #                                                                           name_match=new_name_alias,
            # #                                                                           defaults= defaults)
            #
            # try:
            #     name_alias = Forename(name=name_select,
            #                           name_match=new_name_alias,
            #                           score=defaults['score'],
            #                           deleted=defaults['deleted'],
            #                           nickname=defaults['nickname'])
            #     name_alias.save(using=settings.NAMESEARCH_DB)
            # except:
            #     # already in db - using pre-existing
            #     name_alias = Forename.objects.using(settings.NAMESEARCH_DB).filter(name=name_select, name_match=new_name_alias).first()
            name_alias, created = Forename.objects.using(settings.NAMESEARCH_DB).get_or_create(name=name_select,
                                                                                     name_match=new_name_alias,
                                                                                     defaults = defaults)
            if not created:
                sql = "update forenames set score = {}, deleted = 'N' where name = %s and name_match = %s".format(new_name_score)
                from django.db import connections
                with connections[settings.NAMESEARCH_DB].cursor() as cursor:
                    cursor.execute(sql, [name_select, new_name_alias])

        return name_alias

    @staticmethod
    def load_common_names(name_type, name_select):
        """
        Load a list of names from the corresponding file and return the top 250
        :param name_type: type of name file to open
        :return: list of names
        """
        import os
        from django.conf import settings

        # load common names
        names_limit = 250
        names_file = None
        name_list = None

        if name_type == 'surname':
            names_file = 'common-surnames.txt'
        if name_type == 'male':
            names_file = 'common-male.txt'
        if name_type == 'female':
            names_file = 'common-female.txt'
        if name_type == 'surname-asian':
            names_file = 'common-surnames-asian.txt'
        if name_type == 'surname-hispanic':
            names_file = 'common-hispanic-last-names.txt'

        if not names_file:
            return
        with open(os.path.join(settings.MEDIA_ROOT,names_file), 'r') as f:
            names_list = f.readlines()
        # f = open(os.path.join(settings.MEDIA_ROOT,names_file))
        # names_list = f.read().decode("utf-8-sig").encode("utf-8")
        names_list = [x.strip() for x in names_list]
        # names_list[0] = names_list[0].decode("utf-8-sig").encode("utf-8")  # get rid of UTF-8 BOM

        # retrieve scored names
        if name_select:
            name_list = NameAliasUtils.load_scored_names(name_select, name_type)

        return names_list[:names_limit], name_list


class DOBScraperResults:

    @staticmethod
    def merge_scraped_judgment_dobs(searchname):
        """
        Pull DOB results from the database that were scraped from PDFs
        :param searchname: a name search object containing first and last names
        :return: dictionary of judgment numbers without dashes and matching DOB
        """
        from pdftools.models import SCDobDocument
        dob_matches = SCDobDocument.objects.filter(party_name__contains=searchname.first_name)\
            .filter(party_name__contains=searchname.last_name)
        dob_dict = {}
        for match in dob_matches:
            jnum = match.judgment_num
            jnum = jnum.replace('-','')
            jnum_last_4 = jnum[-4:]
            jnum = jnum[:-4] + jnum_last_4[-2:]
            dob = match.party_dob
            dob_dict[jnum] = dob
        return dob_dict

    @staticmethod
    def _is_valid_case(case, judgment_dobs):
        """
        Determine if a case's judgment number is in the list of judgment_dobs
        :param case: a SCNJ case
        :param judgment_dobs: dict of judgment numbers, possibly scraped from PDFs
        :return: boolean indicating whether case is already in dob dict
        """
        is_valid = False
        judgment_num = case.docketed_judgment_number
        if judgment_dobs.get(judgment_num, None):
            is_valid = True
        return is_valid

    @staticmethod
    def exclude_scraped_judgment_dobs(cases, judgment_dobs):
        """
        Remove cases with DOBs that have already been found
        :param judgment_dobs:
        :return:
        """
        filtered_cases = [x for x in cases if not DOBScraperResults._is_valid_case(x, judgment_dobs)]
        return filtered_cases
