

from django.db import models
from functools import reduce

# Create your models here.
class JudgmentIndexReport(models.Model):
    date_from = models.DateField()
    date_to = models.DateField()
    archive_file = models.CharField(max_length=255)


class PacerJudgmentIndexCase(models.Model):
    case_number = models.CharField(max_length=255, db_index=True)
    in_favor = models.CharField(max_length=255)
    against = models.CharField(max_length=100)
    amount = models.CharField(max_length=255)
    judgment_date = models.DateField()
    document = models.IntegerField()
    interest = models.FloatField()
    court_cost = models.FloatField()
    case_status = models.CharField(max_length=50)
    satisfication_date = models.DateField()
    judgment_index_report = models.ForeignKey(JudgmentIndexReport, on_delete=models.CASCADE)
    alias_file = models.CharField(max_length=255, db_index=True)
    case_summary_file = models.CharField(max_length=255, db_index=True)
    party_file = models.CharField(max_length=255, db_index=True)
    alias_file_processed = models.CharField(max_length=1, db_index=True, default='N')
    party_file_processed = models.CharField(max_length=1, db_index=True, default='N')

    def __str__(self):
        return "Case number: {}; Case status: {}; Amount: {}".format(self.case_number, self.case_status, self.amount)


class BankruptcyIndexReport(models.Model):
    date_from = models.DateField()
    date_to = models.DateField()
    archive_file = models.CharField(max_length=255)


class PacerBankruptcyIndexCase(models.Model):
    case_number = models.CharField(max_length=255, db_index=True, unique=True)
    case_title = models.CharField(max_length=255)
    chapter_lead_bk_case = models.CharField(max_length=255)
    date_filed = models.DateField()
    date_closed = models.DateField(null=True, blank=True)
    bankruptcy_index_report = models.ForeignKey(BankruptcyIndexReport, on_delete=models.CASCADE)
    alias_file = models.CharField(max_length=255, db_index=True)
    case_summary_file = models.CharField(max_length=255, db_index=True)
    party_file = models.CharField(max_length=255, db_index=True)
    alias_file_processed = models.CharField(max_length=1, db_index=True, default='N')
    party_file_processed = models.CharField(max_length=1, db_index=True, default='N')

    def __str__(self):
        return "Case number: {}; Date filed: {}; Date closed: {}".format(self.case_number, self.date_filed, self.date_closed)


class PacerBankruptcyParty(models.Model):
    bankruptcy_index_case = models.ForeignKey(PacerBankruptcyIndexCase, on_delete=models.CASCADE)
    party_name = models.CharField(max_length=255, db_index=True)
    party_type = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return "Party name: {}".format(self.party_name)

    # class Meta:
    #     db_table = 'pacerscraper_bankruptcyindexreport_1'


class BankruptcyIndexReportBase(models.Model):
    date_from = models.DateField()
    date_to = models.DateField()
    archive_file = models.CharField(max_length=255)

    class Meta:
        abstract = True

class BankruptcyIndexReport_1(BankruptcyIndexReportBase):
    class Meta:
        db_table = 'pacerscraper_bankruptcyindexreport_1'

class BankruptcyIndexReport_2(BankruptcyIndexReportBase):
    class Meta:
        db_table = 'pacerscraper_bankruptcyindexreport_2'

class BankruptcyIndexReport_3(BankruptcyIndexReportBase):
    class Meta:
        db_table = 'pacerscraper_bankruptcyindexreport_3'

class BankruptcyIndexReport_4(BankruptcyIndexReportBase):
    class Meta:
        db_table = 'pacerscraper_bankruptcyindexreport_4'

class BankruptcyIndexReport_5(BankruptcyIndexReportBase):
    class Meta:
        db_table = 'pacerscraper_bankruptcyindexreport_5'



class PacerBankruptcyIndexCaseBase(models.Model):
    case_number = models.CharField(max_length=255, db_index=True, unique=True)
    case_title = models.CharField(max_length=255)
    chapter_lead_bk_case = models.CharField(max_length=255)
    date_filed = models.DateField()
    date_closed = models.DateField(null=True, blank=True)
    # bankruptcy_index_report = models.ForeignKey(BankruptcyIndexReport_1, on_delete=models.CASCADE)
    alias_file = models.CharField(max_length=255, db_index=True)
    case_summary_file = models.CharField(max_length=255, db_index=True)
    party_file = models.CharField(max_length=255, db_index=True)
    alias_file_processed = models.CharField(max_length=1, db_index=True, default='N')
    party_file_processed = models.CharField(max_length=1, db_index=True, default='N')

    def __str__(self):
        return "Case number: {}; Date filed: {}; Date closed: {}".format(self.case_number, self.date_filed, self.date_closed)

    class Meta:
        abstract = True

class PacerBankruptcyIndexCase_1(PacerBankruptcyIndexCaseBase):
    bankruptcy_index_report = models.ForeignKey(BankruptcyIndexReport_1, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyindexcase_1'

class PacerBankruptcyIndexCase_2(PacerBankruptcyIndexCaseBase):
    bankruptcy_index_report = models.ForeignKey(BankruptcyIndexReport_2, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyindexcase_2'

class PacerBankruptcyIndexCase_3(PacerBankruptcyIndexCaseBase):
    bankruptcy_index_report = models.ForeignKey(BankruptcyIndexReport_3, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyindexcase_3'

class PacerBankruptcyIndexCase_4(PacerBankruptcyIndexCaseBase):
    bankruptcy_index_report = models.ForeignKey(BankruptcyIndexReport_4, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyindexcase_4'

class PacerBankruptcyIndexCase_5(PacerBankruptcyIndexCaseBase):
    bankruptcy_index_report = models.ForeignKey(BankruptcyIndexReport_5, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyindexcase_5'



class PacerBankruptcyPartyBase(models.Model):
    bankruptcy_index_case = models.ForeignKey(PacerBankruptcyIndexCase, on_delete=models.CASCADE)
    party_name = models.CharField(max_length=255, db_index=True)
    party_type = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return "Party name: {}".format(self.party_name)

    class Meta:
        abstract = True

class PacerBankruptcyParty_1(PacerBankruptcyPartyBase):
    bankruptcy_index_case = models.ForeignKey(PacerBankruptcyIndexCase_1, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyparty_1'

class PacerBankruptcyParty_2(PacerBankruptcyPartyBase):
    bankruptcy_index_case = models.ForeignKey(PacerBankruptcyIndexCase_2, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyparty_2'

class PacerBankruptcyParty_3(PacerBankruptcyPartyBase):
    bankruptcy_index_case = models.ForeignKey(PacerBankruptcyIndexCase_3, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyparty_3'

class PacerBankruptcyParty_4(PacerBankruptcyPartyBase):
    bankruptcy_index_case = models.ForeignKey(PacerBankruptcyIndexCase_4, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyparty_4'

class PacerBankruptcyParty_5(PacerBankruptcyPartyBase):
    bankruptcy_index_case = models.ForeignKey(PacerBankruptcyIndexCase_5, on_delete=models.CASCADE)
    class Meta:
        db_table = 'pacerscraper_pacerbankruptcyparty_5'


class PacerJudgmentParty(models.Model):
    judgment_index_case = models.ForeignKey(PacerJudgmentIndexCase, on_delete=models.CASCADE)
    party_name = models.CharField(max_length=255, db_index=True)
    party_type = models.CharField(max_length=255)

    def __str__(self):
        return "Party name: {}".format(self.party_name)

import threading
class ParallelThread(threading.Thread):
    def __init__(self, db, fn_list, ln_list):
        threading.Thread.__init__(self)
        self.db = db
        self.fn_list = fn_list
        self.ln_list = ln_list
        self.result = []
        self.search_from = None
        self.search_to = None

    def run(self):
        from django.db.models import Q
        self.result = PacerBankruptcyParty.objects.using(self.db)\
            .filter(Q(party_type__icontains='debtor') | Q(party_type__icontains='defendant')) \
            .filter(party_name__iregex=r'{}'.format(self.fn_list)).prefetch_related() \
            .filter(party_name__iregex=r'{}'.format(self.ln_list)) \
            .filter(bankruptcy_index_case__date_filed__gte=self.search_from) \
            .filter(bankruptcy_index_case__date_filed__lte=self.search_to)

            # .filter(reduce(lambda x, y: x | y, [Q(party_type__icontains=word) for word in ['debtor','defendant']]))
        print(("Matches found in database {}: {}".format(self.db, len(self.result))))


class PacerBankruptcyAlias(models.Model):
    bankruptcy_index_case = models.ForeignKey(PacerBankruptcyIndexCase, on_delete=models.CASCADE)
    alias_name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return "Alias name: {}".format(self.alias_name)


class PacerJudgmentAlias(models.Model):
    judgment_index_case = models.ForeignKey(PacerJudgmentIndexCase, on_delete=models.CASCADE)
    alias_name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return "Alias name: {}".format(self.alias_name)


class UsdcReportQueryManager:
    @staticmethod
    def query_database_by_searchname_details3(searchname):
        """
        Query the usdc database using the provided searchname
        :param searchname: the name to use for the search
        :return: a queryset containing matching cases
        """
        def list_to_regex_str(the_list):  # @TODO remove dupe
            return '|'.join(the_list)

        import logging
        import re
        from django.conf import settings
        from nameviewer.helpers import first_name_variations_from_db, last_name_variations_from_db
        from pacerscraper.models import PacerJudgmentIndexCase

        cases = []
        case_dict = {}
        logger = logging.getLogger(__name__)
        match_first_name_list = first_name_variations_from_db(searchname.first_name)
        logger.info(match_first_name_list)
        match_last_name_list = last_name_variations_from_db(searchname.last_name)
        logger.info(match_last_name_list)

        fn_list = list_to_regex_str(match_first_name_list)
        ln_list = list_to_regex_str(match_last_name_list)

        db_matches = []
        db = settings.USDCSEARCH_DB
        cm = PacerJudgmentParty.objects.using(db) \
            .filter(party_name__iregex=r'{}'.format(fn_list))\
            .filter(party_name__iregex=r'{}'.format(ln_list))\
            .filter(judgment_index_case__judgment_date__gte=searchname.search_from) \
            .filter(judgment_index_case__judgment_date__lte=searchname.search_to) \
            .exclude(party_type__icontains='plaintiff') \
            .prefetch_related()

        all_search_names = match_first_name_list + match_last_name_list
        for party in cm:  # type: PacerJudgmentParty
            party_partial_names = party.party_name.lower().split()
            print(("-----> Pre Split party name: {}".format(party_partial_names)))
            party_partial_names = [x for x in party_partial_names if x in all_search_names]
            party_partial_names = [re.sub(r"[^A-Za-z0-9'\-]+", '', x) for x in party_partial_names]
            print(("-----> Post Split party name: {}".format(party_partial_names)))
            if len(party_partial_names) >= 2 and set(party_partial_names).issubset(set(all_search_names)):
                usdc_case = party.judgment_index_case
                usdc_case.pacerjudgmentparty_set.all()  # prefetch for later
                print(("corresponding case for party: {}".format(usdc_case)))
                case_dict[usdc_case.case_number] = usdc_case  # need the db for reporting party info
                db_matches.append(party)

        # cast case_match and equivs to list type
        case_match_list = [x for x in db_matches]
        # for db_match in db_matches[1:]:
        #     for cm in db_match:
        #         case_match_list.append(cm)
        # print("Matches found across {} dbs: {}".format(len(db_matches), len(case_match_list)))
        print(("Matches found: {} parties, {} cases".format(len(db_matches), len(case_match_list))))

        return case_match_list, case_dict


class BankruptcyReportQueryManager:
    @staticmethod
    def query_database_by_searchname_details2(searchname):
        """
        Returns a list of PacerBankruptcyParty and a dict of PacerBankruptcyIndexCase
        :param searchname: orders.models.SearchName to be searched
        :return: a tuple of matching cases and a dict indexed by case number
        """
        # type: (str) -> pacerscraper.models.PacerBankruptcyParty[], dict
        def _make_party_name_query(name_match_list):
            from django.db.models import Q
            query = reduce(lambda x, y: x | y, [Q(party_name__icontains=name) for name in name_match_list])
            # logger.info(query)
            return query

        def distinct_cases_and_filter(cases):
            # make dataset contain unique results
            distinct_matches = {}
            for e in cases:
                distinct_matches[e.bankruptcy_index_case_id] = e
            cases = list(distinct_matches.values())

            # filter out partial matches, like mar matching mark when maria was the original search
            final_cases = []
            for party_match in cases:
                l_party_match = party_match.party_name.lower()
                for f_name_match in match_first_name_list:
                    f_name_match = f_name_match.lower()
                    if "{} ".format(f_name_match) in l_party_match or " {}".format(f_name_match) in l_party_match:
                        final_cases.append(party_match)
                        for l_name_match in match_last_name_list:
                            l_name_match = l_name_match.lower()
                            if "{} ".format(l_name_match) in l_party_match or " {}".format(
                                l_name_match) in l_party_match:
                                final_cases.append(party_match)
            return final_cases

        import logging
        from django.conf import settings
        from nameviewer.helpers import first_name_variations_from_db, last_name_variations_from_db

        logger = logging.getLogger(__name__)
        cases = []
        case_match = None
        case_dict = {}
        match_last_name_list = last_name_variations_from_db(searchname.last_name)
        if searchname.last_name:
            # https://stackoverflow.com/questions/7088173/how-to-query-model-where-name-contains-any-word-in-python-list
            query = _make_party_name_query(match_last_name_list)
            # query every bankruptcy database for its results
            db_list = ['default', settings.NAMESEARCH_DB]
            db_matches = []
            # for i, db in enumerate(db_list):
            #     # prefetch_related gets the case info that will be needed later for generating the report
            #     cm = PacerBankruptcyParty.objects.using(db).filter(query).prefetch_related()
            #     print("Matches found in database {}: {}".format(i, len(cm)))
            #     # [begin] grab the actual case for generating the report later
            #     for party in cm:
            #         bk_case = party.bankruptcy_index_case
            #         # bk_case.prefetch_related()
            #         bk_case.pacerbankruptcyparty_set.all() # prefetch for later
            #         print("corresponding case for party: {}".format(bk_case))
            #         case_dict[bk_case.case_number] = {'db_ref':db, 'case_model':bk_case}  # need the db for reporting party info
            #     # [end] grab the actual case for generating the report later
            #     db_matches.append(cm)
            # case_match = db_matches[0]
            # case_match2 = db_matches[1]
        # @TODO: else generate company name matches here

        # cast case_match and equivs to list type
        case_match = [x for x in case_match]
        for cm in case_match2:
            case_match.append(cm)

        # further filter these results by matching last names
        if searchname.first_name:
            match_first_name_list = first_name_variations_from_db(searchname.first_name)
            # print(match_last_name_list)
            for cm in case_match:
                party_name = cm.party_name.lower()
                for nm in match_first_name_list:
                    if nm in party_name: # and cm.party_type == 'Defendant':
                        cases.append(cm)

        # filter out partial matches and make distinct
        cases = distinct_cases_and_filter(cases)

        # @TODO: downselect case_dict to get rid of un-needed matched
        # new_case_dict = {}

        # case_match = case_match.filter(party_type='Defendant')
        for c in cases:
            print(("found match: {}".format(c)))
        return cases, case_dict

    @staticmethod
    def query_database_by_searchname_details3(searchname):
        """
        This is the original BKCY search function that leverages (several) mysql databases
        :param searchname: the name to search on
        :return: a tuple of matching cases and a dict indexed by case number
        """
        def list_to_regex_str(the_list):  # @TODO remove dupe
            return '|'.join(the_list)

        def flatten(foo):
            for x in foo:
                if hasattr(x, '__iter__'):
                    for y in flatten(x):
                        yield y
                else:
                    yield x

        import logging
        import re
        from django.conf import settings
        from nameviewer.helpers import first_name_variations_from_db, last_name_variations_from_db
        from pacerscraper.models import PacerBankruptcyIndexCase

        cases = []
        case_dict = {}
        logger = logging.getLogger(__name__)
        match_first_name_list = first_name_variations_from_db(searchname.first_name)
        logger.info(match_first_name_list)
        match_last_name_list = last_name_variations_from_db(searchname.last_name)
        logger.info(match_last_name_list)

        fn_list = list_to_regex_str(match_first_name_list)
        ln_list = list_to_regex_str(match_last_name_list)

        db_list = [settings.NAMESEARCH_DB, settings.BKSEARCH_DB2, settings.BKSEARCH_DB3, settings.BKSEARCH_DB4]
        db_matches = []

        # begin run in parallel
        threads = []
        for db in db_list:
            t = ParallelThread(db, fn_list, ln_list)
            t.search_from = searchname.search_from
            t.search_to = searchname.search_to
            # t.setDaemon(True)
            t.start()
            threads.append(t)

        all_search_names = match_first_name_list + match_last_name_list
        for thread in threads:  # type: ParallelThread
            thread.join()
            cm = thread.result
            # [begin] grab the actual case for generating the report later
            for party in cm:
                party_partial_names = party.party_name.lower().split()
                print(("-----> Pre Split party name: {}".format(party_partial_names)))
                party_partial_names = [x for x in party_partial_names if x in all_search_names]
                party_partial_names = [re.sub(r"[^A-Za-z0-9'\-]+", '', x) for x in party_partial_names]
                print(("-----> Post Split party name: {}".format(party_partial_names)))
                if len(party_partial_names) >= 2 and set(party_partial_names).issubset(set(all_search_names)):
                    bk_case = party.bankruptcy_index_case
                    # bk_case.prefetch_related()
                    bk_case.pacerbankruptcyparty_set.all()  # prefetch for later
                    print(("corresponding case for party: {}".format(bk_case)))
                    case_dict[bk_case.case_number] = {'db_ref': thread.db,
                                                      'case_model': bk_case}  # need the db for reporting party info
            # [end] grab the actual case for generating the report later
            db_matches.append(cm)  # list[thread.result]
        # end run in parallel


        # cast case_match and equivs to list type
        case_match_list = []
        for db_match in db_matches:
        # case_match_list = [x for x in db_matches[0]]  # list[Party]
        # for db_match in db_matches[1:]:
            for cm in db_match:
                party = cm
                party_partial_names = party.party_name.lower().split()
                print(("-----> Pre Split party name: {}".format(party_partial_names)))
                party_partial_names = [re.sub(r"[^A-Za-z0-9'\-]+", '', x) for x in party_partial_names]
                party_partial_names = [x for x in party_partial_names if x in all_search_names]
                print(("-----> Post Split party name: {}".format(party_partial_names)))
                if len(party_partial_names) >= 2 and set(party_partial_names).issubset(set(all_search_names)):
                    case_match_list.append(cm)
        print(("Matches found across {} dbs: {}".format(len(db_matches), len(case_match_list))))

        return case_match_list, case_dict

# ---
    @staticmethod
    def _get_bkcy_party_case_matches(case_id_list, es_idx):
        """
        Get details about cases based on a list of case ids
        :param case_id_list: the list of cases to fetch details for
        :param es_idx: the index/shard where the original bkcy cases are located
        :return:
        """
        from django.conf import settings
        case_match = None
        if es_idx == 'bkcy':
            case_match = PacerBankruptcyIndexCase_1.objects.using(settings.BKSEARCH_DB_COMB).filter(id__in=case_id_list)
        if es_idx == 'bkcy2':
            case_match = PacerBankruptcyIndexCase_2.objects.using(settings.BKSEARCH_DB_COMB).filter(id__in=case_id_list)
        if es_idx == 'bkcy3':
            case_match = PacerBankruptcyIndexCase_3.objects.using(settings.BKSEARCH_DB_COMB).filter(id__in=case_id_list)
        if es_idx == 'bkcy4':
            case_match = PacerBankruptcyIndexCase_4.objects.using(settings.BKSEARCH_DB_COMB).filter(id__in=case_id_list)
        if es_idx == 'bkcy5':
            case_match = PacerBankruptcyIndexCase_5.objects.using(settings.BKSEARCH_DB_COMB).filter(id__in=case_id_list)
        else:
            case_match = PacerBankruptcyIndexCase.objects.using(settings.BKSEARCH_DB_COMB).filter(id__in=case_id_list)
        return case_match


    @staticmethod
    def query_database_by_searchname_details4(searchname):
        """
        This version uses an elasticsearch database for the initial lookup
        Then the cases are matched by ID
        :param searchname: the name to search on
        :return: a tuple of matching cases and a dict indexed by case number
        """
        def list_to_regex_str(the_list):  # @TODO remove dupe
            return '|'.join(the_list)

        def flatten(foo):
            for x in foo:
                if hasattr(x, '__iter__'):
                    for y in flatten(x):
                        yield y
                else:
                    yield x

        import logging
        import re
        from django.conf import settings
        from nameviewer.helpers import first_name_variations_from_db, last_name_variations_from_db
        from pacerscraper.models import PacerBankruptcyIndexCase

        cases = []
        case_dict = {}
        logger = logging.getLogger(__name__)
        match_first_name_list = first_name_variations_from_db(searchname.first_name)
        logger.info(match_first_name_list)
        match_last_name_list = last_name_variations_from_db(searchname.last_name)
        logger.info(match_last_name_list)

        # fn_list = list_to_regex_str(match_first_name_list)
        # ln_list = list_to_regex_str(match_last_name_list)
        fn_list = match_first_name_list
        ln_list = match_last_name_list

        db_list = [settings.NAMESEARCH_DB, settings.BKSEARCH_DB2, settings.BKSEARCH_DB3, settings.BKSEARCH_DB4]
        db_matches = []

        # begin run in parallel
        # threads = []
        # for db in db_list:
        #     t = ParallelThread(db, fn_list, ln_list)
        #     t.search_from = searchname.search_from
        #     t.search_to = searchname.search_to
        #     t.start()
        #     threads.append(t)
        #
        # all_search_names = match_first_name_list + match_last_name_list
        # for thread in threads:  # type: ParallelThread
        #     thread.join()
        #     cm = thread.result
        #     # [begin] grab the actual case for generating the report later
        #     for party in cm:
        #         party_partial_names = party.party_name.lower().split()
        #         print("-----> Pre Split party name: {}".format(party_partial_names))
        #         party_partial_names = [x for x in party_partial_names if x in all_search_names]
        #         party_partial_names = [re.sub(r"[^A-Za-z0-9'\-]+", '', x) for x in party_partial_names]
        #         print("-----> Post Split party name: {}".format(party_partial_names))
        #         if len(party_partial_names) >= 2 and set(party_partial_names).issubset(set(all_search_names)):
        #             bk_case = party.bankruptcy_index_case
        #             bk_case.pacerbankruptcyparty_set.all()  # prefetch for later
        #             print("corresponding case for party: {}".format(bk_case))
        #             case_dict[bk_case.case_number] = {'db_ref': thread.db,
        #                                               'case_model': bk_case}  # need the db for reporting party info
        #     db_matches.append(cm)  # list[thread.result]
        # # end run in parallel
        #
        #
        # # cast case_match and equivs to list type
        # case_match_list = []
        # for db_match in db_matches:
        #     for cm in db_match:
        #         party = cm
        #         party_partial_names = party.party_name.lower().split()
        #         print("-----> Pre Split party name: {}".format(party_partial_names))
        #         party_partial_names = [re.sub(r"[^A-Za-z0-9'\-]+", '', x) for x in party_partial_names]
        #         party_partial_names = [x for x in party_partial_names if x in all_search_names]
        #         print("-----> Post Split party name: {}".format(party_partial_names))
        #         if len(party_partial_names) >= 2 and set(party_partial_names).issubset(set(all_search_names)):
        #             case_match_list.append(cm)
        # print("Matches found across {} dbs: {}".format(len(db_matches), len(case_match_list)))

        from statereport.elasticsearch_utils import ElasticSearchUtils

        esu = ElasticSearchUtils()
        party_match = PacerBankruptcyParty.objects
        es_bkcy_index_list = ['all', 'bkcy', 'bkcy2', 'bkcy3', 'bkcy4']
        all_search_names = fn_list + ln_list
        case_match_list = []

        for es_idx in es_bkcy_index_list:
            party_case_id_list = esu.case_list_from_name_list(fn_list, ln_list, es_idx)
            # party_match = party_match.filter(id__in=party_case_id_list)
            party_match = BankruptcyReportQueryManager._get_bkcy_party_case_matches(party_case_id_list, es_idx)

            db_match = party_match
            for cm in db_match:
                party = cm
                party_partial_names = party.party_name.lower().split()
                print(("-----> Pre Split party name: {}".format(party_partial_names)))
                party_partial_names = [re.sub(r"[^A-Za-z0-9'\-]+", '', x) for x in party_partial_names]
                party_partial_names = [x for x in party_partial_names if x in all_search_names]
                print(("-----> Post Split party name: {}".format(party_partial_names)))
                if len(party_partial_names) >= 2 and set(party_partial_names).issubset(set(all_search_names)):
                    case_match_list.append(cm)

                # old code merged into here
                party_partial_names = party.party_name.lower().split()
                print(("-----> Pre Split party name: {}".format(party_partial_names)))
                party_partial_names = [x for x in party_partial_names if x in all_search_names]
                party_partial_names = [re.sub(r"[^A-Za-z0-9'\-]+", '', x) for x in party_partial_names]
                print(("-----> Post Split party name: {}".format(party_partial_names)))
                if len(party_partial_names) >= 2 and set(party_partial_names).issubset(set(all_search_names)):
                    bk_case = party.bankruptcy_index_case
                    bk_case.pacerbankruptcyparty_set.all()  # prefetch for later
                    print(("corresponding case for party: {}".format(bk_case)))
                    case_dict[bk_case.case_number] = {'db_ref': es_idx,
                                                      'case_model': bk_case}  # need the db for reporting party info
        # db_matches.append(cm)  # list[thread.result]

        return case_match_list, case_dict

# ---

    @staticmethod
    def query_database_by_searchname_details(searchname):
        """
        Search the database for matching bankruptcy cases based on the searchname provided
        :param searchname: the name to search on
        :return: a tuple of matching cases and a dict indexed by case number
        """
        #  @TODO: assumes first name or first and last name are supplied
        def _make_party_name_query(name_match_list):
            from django.db.models import Q
            query = reduce(lambda x, y: x | y, [Q(party_name__icontains=name) for name in match_first_name_list])
            # logger.info(query)
            return query

        import logging
        from nameviewer.helpers import first_name_variations_from_db, last_name_variations_from_db

        logger = logging.getLogger(__name__)

        cases = []
        case_match = None
        if searchname.first_name:
            match_first_name_list = first_name_variations_from_db(searchname.first_name)
            # https://stackoverflow.com/questions/7088173/how-to-query-model-where-name-contains-any-word-in-python-list
            query = _make_party_name_query(match_first_name_list)
            # print(query)
            case_match = PacerBankruptcyParty.objects.filter(query)
            # for c in case_match:
            #     print("found match: {}".format(c))
        if searchname.last_name:
            #     party_last_name_list = last_name_variations_from_db(searchname.last_name)
            #     # logger.warning('Generated last name list from db, {} matches found'.format(len(party_last_name_list)))
            #     party_match = party_match.filter(party_last_name__in=party_last_name_list)
            match_last_name_list = last_name_variations_from_db(searchname.last_name)
            # print(match_last_name_list)
            query = _make_party_name_query(match_last_name_list)
            case_match = case_match.filter(query)
            print((case_match.query))
            # for c in case_match:
            #     print("found match: {}".format(c))

        # if searchname.middle_name:
        #     party_match = party_match.filter(party_initial__in=searchname.middle_name)
        # if searchname.search_from:
        #     d = str(searchname.search_from).split('/')
        #     yy = d[2][-2:] # last two digits of year
        #     # from_date = '{:04}{:02}{:02}'.format(int(d[2]),int(d[0]),int(d[1]))
        #     # party_match = party_match.filter(case__case_filed_date__gte=from_date)
        #     party_match = party_match.filter(case__docketed_judgment_yy__gte =yy)
        # if searchname.search_to:
        #     d = str(searchname.search_to).split('/')
        #     yy = d[2][-2:] # last two digits of year
        #     # to_date = '{:04}{:02}{:02}'.format(int(d[2]),int(d[0]),int(d[1]))
        #     # party_match = party_match.filter(case__case_filed_date__lte=to_date)
        #     party_match = party_match.filter(case__docketed_judgment_yy__lte=yy)
        # if not seq_num is '':
        #     print("Using supplied sequence number: {}".format(seq_num))
        #     party_match = party_match.filter(docketed_judgment_seq_num__exact=seq_num)
        # # only search debtors
        # debtor_code_type = 'D'
        # party_match = party_match.filter(record_type_code_party__exact=debtor_code_type)

        # build the case list
        # if not party_match is None:
        #     for pm in party_match:
        #         c = None
        #         c = pm.case
        #         cases.append(c)
        #         # logger.warning('Generated a case with judgment number {}'.format(pm.case.docketed_judgment_number))
        #         print('Generated a case with judgment number {}'.format(pm.case.docketed_judgment_number))

        case_match = case_match.filter(party_type='Defendant')
        # make dataset contain unique results
        # distinct_matches = {}
        # for e in case_match:
        #     distinct_matches[e.bankruptcy_index_case_id] = e
        # case_match = distinct_matches.values()
        # logger.info(case_match)
        print(case_match)

        if not case_match is None:
            for cm in case_match:
                c = None
                c = cm.bankruptcy_index_case
                cases.append(c)
                logger.info('Generated a case match with case number {}'
                            .format(c.case_number))
        return cases

