from functools import reduce
class StateReportNameSearchUtils:

    @staticmethod
    def split_date_for_sql(date_to_split):
        """
        Splits a date on dashes '-' and returns the last two numbers of the year
        :param date_to_split: date separated by dashes
        :return: last two digits of the year
        """
        d = str(date_to_split).split('-')
        # return d[2][-2:]  # last two digits of year
        return d[0][-2:]  # last two digits of year

    @staticmethod
    def split_names_from_searchname(searchname):
        """
        Takes a search name and makes a string with first middle last names.
        Convert that name into a list
        Then the name is further split if an asian name is detected and the final result is returned
        :param searchname:
        :return:
        """
        import re
        from nameviewer.helpers import asian_name_check
        searchname = searchname  # type: orders.model.Searchname
        full_name = "{} {} {}".format(searchname.first_name, searchname.middle_name, searchname.last_name)
        # split_name = full_name.split(' ')
        split_name = re.split('\s+', full_name)
        asian_split_name = asian_name_check(split_name[0])
        final_split_name = asian_split_name + split_name[1:]
        return final_split_name

    @staticmethod
    def is_three_name_search(split_names):
        """
        Determines if the search name was specified with three names
        :param split_names: list of name parts provided for search
        :return: boolean indicating whether 3 names or more were detected
        """
        three_names_or_more = False
        if len(split_names) > 2:
            three_names_or_more = True
        return three_names_or_more

    @staticmethod
    def exclude_closed_judgments(party_match):
        """
        Return a queryset of party matches with closed judgments found in closed reports table excluded from match set
        :param party_match: django queryset of Party matches
        :return: django queryset of matches excluding closed judgments
        """
        from django.conf import settings
        from statereport.models import StateClosingsReport

        matched_judgments = [x for x in party_match.values_list('case__docketed_judgment_number', flat=True).distinct()]

        from django.db.models import Q
        closed_query = reduce(lambda x, y: x | y, [Q(dckt_jdg_seq_num=judg[2:8]) & Q(dckt_jdg_num_yr=judg[-2:]) for judg in matched_judgments])
        closed_filtered = StateClosingsReport.objects.using(settings.NAMESEARCH_DB).filter(closed_query).values_list('dckt_jdg_seq_num','dckt_jdg_type_code','dckt_jdg_num_yr')
        closed_judgments_list = [x[1] + x[0] + x[2] for x in closed_filtered]
        party_match_closed_excluded = party_match.exclude(case__docketed_judgment_number__in=(closed_judgments_list))
        return party_match_closed_excluded

    @staticmethod
    def search_company_entities(searchname):
        """
        Find party and party_alt matches for a given searchname that's a company name
        :param searchname: an Orders.models.searchname instance
        :return: a tuple of django querysets corresponding to party matches and party alt matches
        """
        from django.db.models import Q
        from django.conf import settings
        from .models import Party, PartyAlt

        sql = 'select statereport_party.* from statereport_party, statereport_case where statereport_party.case_id = statereport_case.id and '
        co_name_elements = searchname.company_name.split()
        i = 0
        sql2 = ''
        #
        for c_name in co_name_elements:
            s = "merged_party_name like '%%{}%%'".format(c_name)
            if i > 0:
                s = " and " + s
            i += 1
            sql2 += s
        final_sql = sql + sql2
        # only match debtors!
        sql3 = " AND statereport_party.party_role_type_code = 'D'"
        final_sql += sql3
        if searchname.search_from and searchname.search_to:
            date_from = StateReportNameSearchUtils.split_date_for_sql(searchname.search_from)
            date_to = StateReportNameSearchUtils.split_date_for_sql(searchname.search_to)
            date_filter_sql = " and docketed_judgment_yy >= {} and docketed_judgment_yy <= {}".format(date_from,
                                                                                                      date_to)
            final_sql += date_filter_sql

        party_match = Party.objects.using(settings.NAMESEARCH_DB).raw(final_sql)

        # @TODO: company name needs alt party match objects too
        q_alt_objs = Q()
        party_alt_match = PartyAlt.objects.using(settings.NAMESEARCH_DB)
        for n in co_name_elements:
            q_alt_objs &= Q(full_search_party_name__icontains=' ' + n + ' ')
        party_alt_match = party_alt_match.filter(q_alt_objs)
        if searchname.search_from and searchname.search_to:
            party_alt_match = party_alt_match.filter(case__case_filed_date__gte=searchname.search_from)
            party_alt_match = party_alt_match.filter(case__case_filed_date__lte=searchname.search_to)
            party_alt_match = party_alt_match.filter(party_type_indicator='1')  # only match debtors
        # sorting
        party_alt_match = party_alt_match.order_by('-case__debt__party_orig_amt')

        return party_match, party_alt_match

    @staticmethod
    def query_high_value_judgments(searchname):
        """
        Build query set for high value judgments
        :param searchname: Name to search by
        :return: django query set of matches
        """
        import logging
        from django.conf import settings
        from django.db.models import Q
        from .models import DebtAmountLookup, Party

        logger = logging.getLogger(__name__)

        from nameviewer.helpers import generate_forenames, generate_surnames
        logger.debug("Running high value judgment search...")
        searchname_first_name = searchname.first_name
        searchname_last_name = searchname.last_name

        lowest_name_match_score = 80
        # first names
        first_name_list = generate_forenames(searchname_first_name, lowest_name_match_score)
        print_fname_list = [searchname_first_name.lower().decode('utf-8')]
        for forename in first_name_list:
            print_fname_list.append(forename.name_match)
        # print_fname_list = tuple(print_fname_list)
        # last names
        last_name_list = generate_surnames(searchname_last_name, lowest_name_match_score)
        print_lname_list = [searchname_last_name.lower().decode('utf-8')]
        for surname in last_name_list:
            print_lname_list.append(surname.name_match)
        # print_lname_list = tuple(print_lname_list)

        high_value_threshold = settings.HIGH_VALUE_DEFAULT_THRESHOLD

        dals = DebtAmountLookup.objects.using(settings.NAMESEARCH_DB).filter(party_orig_amt__gte=high_value_threshold)\
            .filter(case__party__record_type_code_party='D')

        q_objs = Q()
        for n in print_lname_list:
            q_objs |= Q(case__party__party_last_name=n)
        dals = dals.filter(q_objs)
        q_objs = Q()
        for n in print_fname_list:
            q_objs |= Q(case__party__party_first_name=n)
        dals = dals.filter(q_objs)

        dals = dals.values_list('case__party__id', flat=True)
        dals = list(dals)
        high_value_party_ids = set(dals)
        party_match_high_value = Party.objects.using(settings.NAMESEARCH_DB).filter(id__in=high_value_party_ids)

        # addition: doing filtering and sorting here
        party_match = StateReportNameSearchUtils.remove_party_duplicates(party_match_high_value)
        print(('Size of party match set: {}'.format(len(party_match))))

        from orders.utils import CaseMatchSortType
        merged_names_match = None
        party_alt_match = None
        matching_cases_sort_type = CaseMatchSortType.CASE_FILED_DATE_ASC
        all_cases = StateReportNameSearchUtils.filter_and_sort_party_matches(party_match, party_alt_match,
                                                                             merged_names_match, searchname,
                                                                             matching_cases_sort_type)

        # return party_match_high_value
        return all_cases

    @staticmethod
    def build_party_match_continuations(searchname_first_name, searchname_last_name):
        """
        Find continuation judgments for a provided first and last name
        :param searchname_first_name: first_name to use for high value search
        :param searchname_last_name: last_name to use for high value search
        :return: django query set of matches
        """
        import logging
        from django.conf import settings
        from .models import Party, StateReportQueryManager

        logger = logging.getLogger(__name__)

        # BEGIN - second attempt - build party match continuations using aliases
        logger.debug("Running continuation search...")
        # @TODO: the upper year isn't calculated correctly - fix this work like the other years in the state lookups
        continuation_sql = """
            select statereport_party.id
            from statereport_comment, statereport_debt, statereport_party
              where
                    statereport_comment.docketed_judgment_year <= 99 and statereport_comment.docketed_judgment_year >=88
                and statereport_comment.case_id = statereport_debt.case_id
                and debt_status_code = 'O'
                and statereport_comment.case_id = statereport_party.case_id
                and party_role_type_code = 'D'
                and {}
                group by statereport_comment.case_id
                having count(statereport_comment.case_id) >= 2"""

        party_first_name_list = StateReportQueryManager._build_first_name_list(searchname_first_name)
        party_last_name_list = StateReportQueryManager._build_last_name_list(searchname_last_name)
        sql2 = ''
        i = 0
        # first name aliases
        for fname in party_first_name_list:
            s = "full_search_party_name like '%%{}%%'".format(fname)
            if i > 0:
                s = " or " + s
            i += 1
            sql2 += s
        if i == 1:  # hack
            sql2 = s
        sql2 = '(' + sql2 + ')'
        # last name aliases
        i = 0
        sql3 = ''
        for lname in party_last_name_list:
            if "'" in lname:
                pass
            else:
                s = "full_search_party_name like '%%{}%%'".format(lname)
                if i > 0:
                    s = " or " + s
                i += 1
                sql3 += s
        if i == 1:  # hack
            sql3 = s
        sql3 = '(' + sql3 + ')'
        final_sql = sql2 + ' and ' + sql3

        from django.db import connection, connections
        cursor_sql = continuation_sql.format(final_sql)
        cursor = connections[settings.NAMESEARCH_DB].cursor()
        logger.info("Querying database for continuations...")
        cursor.execute(cursor_sql)
        continuations_party_ids = cursor.fetchall()

        party_match_continuations = Party.objects.none()
        if continuations_party_ids:
            continuation_party_id_list = continuations_party_ids[0]
            party_ids_list = [x for x in continuation_party_id_list]
            party_match_continuations = Party.objects.using(settings.NAMESEARCH_DB).filter(
                id__in=party_ids_list).filter(case__party__party_role_type_code='D')
        # END - build party match continuations
        return party_match_continuations

    @staticmethod
    def search_name_entities(searchname, use_namelist_db, seq_num, matching_cases_sort_type):
        """
        Run a SCNJ search on the provided search name
        :param searchname: the name to search. Uses the first and last names
        :param use_namelist_db: Whether to the name alias database or not
        :param seq_num: optional seq number if looking for something specific
        :param matching_cases_sort_type: specifies how to sort the matched results
        :return: sorted list of parties matching first and last name.
        """
        import logging
        from django.conf import settings
        from .models import Party, StateReportQueryManager
        from orders.utils import CaseMatchSortType

        logger = logging.getLogger(__name__)

        debtor_code_type = 'D'
        party_match = None
        party_alt_match = None

        split_names = StateReportNameSearchUtils.split_names_from_searchname(searchname)
        if len(split_names) > 1:
            split_middle_name = split_names[1]
            # @TODO: may need to filter on this after search results come back if too many results are returned
        # treat name searches with 3 names or more differently than typical 2 name search
        # for 3 names or more, take the first and last name and search the db with this
        # then post-filter results (for db query efficiency) based on remaining matches
        # @TODO: generate name variations using first name db variations
        if not StateReportNameSearchUtils.is_three_name_search(split_names):
            searchname_first_name = searchname.first_name
            searchname_last_name = searchname.last_name
        else:
            searchname_first_name = split_names[0]
            searchname_last_name = split_names[-1]

        # use the elasticsearch database for lookups or just the mysql database
        if not settings.USE_ELASTICSEARCH_SCNJ:
            if searchname_first_name:
                party_match, party_alt_match = StateReportQueryManager._first_name_filter_build(
                    searchname_first_name,
                    use_namelist_db,
                    extra_name=searchname.first_name,
                    middle_name=searchname.middle_name)
            if searchname_last_name:
                party_match, party_alt_match = \
                    StateReportQueryManager._last_name_filter_build(searchname_last_name, use_namelist_db,
                                                                    party_match,
                                                                    party_alt_match)
        else:  # use elasticsearch DB
            if searchname_first_name and searchname_last_name:
                party_match, party_alt_match = StateReportQueryManager._full_name_filter_build(
                    searchname_first_name,
                    searchname_last_name,
                    extra_name=searchname.first_name,
                    middle_name=searchname.middle_name)

        if searchname.search_from and searchname.search_to:
            party_match, party_alt_match = \
                StateReportQueryManager._date_from_to_filter_build(searchname, party_match, party_alt_match)
        if seq_num:
            logger.debug("Using supplied sequence number: {}".format(seq_num))
            # making this work only on docket numbers minus other info
            party_match = Party.objects.using(settings.NAMESEARCH_DB).filter(
                docketed_judgment_number__exact=seq_num)

        if 1 == 2:  # OLD_QUERY_FOR_CONTINUATIONS:
            party_match = party_match.using(settings.NAMESEARCH_DB).filter(party_role_type_code__exact=debtor_code_type)
            party_alt_match = party_alt_match.using(settings.NAMESEARCH_DB)

            party_match_continuations = StateReportNameSearchUtils.build_party_match_continuations(
                searchname.first_name,
                searchname.last_name)

            # prefetching
            party_match.prefetch_related('case').prefetch_related('debt_set')

            # combine querysets
            # party_match = party_match | party_match_continuations | party_match_high_value
            party_match = party_match | party_match_continuations

        # remove closed judgments
        # party_match = StateReportNameSearchUtils.exclude_closed_judgments(party_match)

        # sorting
        if matching_cases_sort_type == CaseMatchSortType.CHILD_SUPPORT_AMT_DESC:
            party_match = party_match.order_by('-case__debt__party_orig_amt')
        elif matching_cases_sort_type == CaseMatchSortType.CASE_FILED_DATE_ASC:
            party_match = party_match.order_by('-case__case_filed_date')
            party_alt_match = party_alt_match.order_by('-case__case_filed_date')
        # logger.debug(party_match.query)
        return party_match, party_alt_match

    @staticmethod
    def remove_party_duplicates(party_match):
        """
        Remove duplicates from a list of party matches. Works for parties & alt_parties
        :param party_match: iterable of parties to remove duplicates from
        :return: list of de-duped parties
        """
        pm_dict = {}
        for pm in party_match:
            pm_dict[pm.id] = pm
        party_match = list(pm_dict.values())
        del(pm_dict)
        return party_match

    @staticmethod
    def filter_and_sort_party_matches(party_match, party_alt_match, merged_names_match, searchname, matching_cases_sort_type):
        """
        Runs a final check on a list of party matches to filter out matches that are too far apart from the original list of aliases.
        This routine is needed because the name search algorithm returns matches that are fuzzier than one may like
        :param party_match: List of party match results to filter and sort
        :param party_alt_match: List of alt party matches to filter and sort
        :param merged_names_match:
        :param searchname: the original search name supplied with the order
        :param matching_cases_sort_type: how to sort the final results
        :return: combined final list of sorted and filtered cases
        """
        from orders.utils import CaseMatchSortType
        from .models import StateReportQueryManager
        import time
        start_time = time.time()
        cases, child_support_cases = StateReportQueryManager. \
            filter_and_sort_scnj_cases(party_match, party_alt_match, merged_names_match, searchname)
        all_cases = []
        if matching_cases_sort_type == CaseMatchSortType.CHILD_SUPPORT_AMT_DESC:
            all_cases = child_support_cases + cases
        elif matching_cases_sort_type == CaseMatchSortType.CASE_FILED_DATE_ASC:
            all_cases = sorted(child_support_cases + cases, key=lambda case: case.id)

        execution_time = time.time() - start_time
        print(("Sorting routine total time: {}".format(execution_time)))

        return all_cases

    @staticmethod
    def get_party_extra_identifying_details(party_instance):
        """
        Fetches any partial drivers license or SSN info to
        :param party_instance: Party object
        :return: string containing extra party details scraped from PDF
        """
        merged_party_details = ""
        x = party_instance.docketed_judgment_number
        # converted_judg_num = x[:-8] + '-' + x[-8:-2] + '-' + x[-2:]  # now has format XX-XXXXXX-XX
        converted_judg_num = x[:-8] + '-' + x[-8:-2] + '-' + party_instance.docketed_judgment_cc + x[-2:]  # now has format XX-XXXXXX-YYYY
        converted_judg_num = converted_judg_num.replace(' ', '')
        scraped_judg = StateReportNameSearchUtils.get_scraped_judgment_data(converted_judg_num)
        # make sure the scraped data matches the correct party in cases where multiple parties are associated with a judgment
        if scraped_judg:
            is_matched_party = StateReportNameSearchUtils.match_scraped_data_to_party(party_instance, scraped_judg)
            if is_matched_party:
                ssn = scraped_judg.party_ssn
                dlicense = scraped_judg.party_dlicense
                if ssn:
                    merged_party_details += ', ' + ssn
                if dlicense:
                    # if merged_party_details:
                    #     merged_party_details += ', '
                    merged_party_details += ', ' + dlicense

                # scdob = SCDobDocument(file_hash=file_hash,
                #                       judgment_num=parsed_judgment_num,
                #                       party_name=d['name'],
                #                       party_dob=d.get('dob', None),
                #                       party_ssn=d.get('ssn', None),
                #                       party_dlicense=d.get('dlicense', None))

        return merged_party_details
        # party_dob = merge_extra_party_info(party_instance, party_dob_xml)

    @staticmethod
    def get_scraped_judgment_data(docket_num_ccyy):
        """
        Convenience method to get pdf scraped judgment data using a docket num as the lookup key
        :param docket_num_ccyy: docket number in the form of XX-XXXXX-XXXX
        :return: SCDobDocument
        """
        from django.conf import settings
        from pdftools.models import SCDobDocument

        return SCDobDocument.objects.using(settings.NAMESEARCH_DB).filter(judgment_num=docket_num_ccyy).first()

    @staticmethod
    def match_scraped_data_to_party(party_instance, scraped_judg):
        """
        Determine whether a party instance matches the pdf scraped judgment details by checking party against known aliases
        :param party_instance: instance of statereport.models.Party
        :param scraped_judg: name found in the scraped judgment
        :return: true if a match is found
        """
        from statereport.models import Party
        from orders.tasks import first_name_variations_from_db, last_name_variations_from_db
        i = 0
        first_name = party_instance.party_first_name
        last_name = party_instance.party_last_name

        fname_vars = first_name_variations_from_db(first_name)
        fname_vars = [x.lower() for x in fname_vars]
        lname_vars = last_name_variations_from_db(last_name)
        lname_vars = [x.lower() for x in lname_vars]

        split_scraped_party_names = scraped_judg.party_name.split(' ')
        split_scraped_fname = split_scraped_party_names[0].lower()
        split_scraped_lname = split_scraped_party_names[-1].lower()

        name_match = False
        if split_scraped_fname in fname_vars and split_scraped_lname in lname_vars:
            name_match = True
        return name_match
