

import collections

from django.db import models
from enum import Enum


class ReportBatch(models.Model):
    """
        Store data about when a file was loaded
    """
    date_processed = models.DateTimeField()
    file_name = models.CharField(max_length=50)


class StateClosingsReport(models.Model):
    """
        Model for JDC0501S state closing report
    """
    report_batch = models.ForeignKey(ReportBatch, on_delete=models.CASCADE)
    century_year = models.CharField(max_length=50)
    dckt_jdg_num_yr = models.CharField(max_length=50)
    dckt_jdg_seq_num = models.CharField(max_length=50)
    dckt_jdg_type_code = models.CharField(max_length=50)
    debt_num = models.CharField(max_length=50)
    party_num = models.CharField(max_length=50)
    ptydbt_status_code = models.CharField(max_length=50)
    ptydbt_status_date = models.CharField(max_length=50)
    case_title = models.CharField(max_length=50)
    party_last_name = models.CharField(max_length=50, db_index=True)
    party_first_name = models.CharField(max_length=50, db_index=True)
    party_mid_intl = models.CharField(max_length=50, db_index=True)
    party_cnt = models.CharField(max_length=50)
    party_dbt_cnt = models.CharField(max_length=50)
    partical_close_indicator = models.CharField(max_length=50)
    warrent_of_sat_indicator = models.CharField(max_length=50)
    closing_document_code = models.CharField(max_length=50)
    jptydoc_target = models.CharField(max_length=50)
    venue_id = models.CharField(max_length=50)
    dckt_type_code = models.CharField(max_length=50)
    dckt_seq_num = models.CharField(max_length=50)
    dckt_crt_year = models.CharField(max_length=50)
    nonacms_venue_id = models.CharField(max_length=50)
    nonacms_key_frst = models.CharField(max_length=50)
    nonacms_key_mid = models.CharField(max_length=50)
    nonacms_key_last = models.CharField(max_length=50)
    extract_start_date = models.CharField(max_length=50)
    extract_end_date = models.CharField(max_length=50)
    report_batch = models.ForeignKey(ReportBatch, on_delete=models.CASCADE) # link to relevant import data
    data_layout_dict = None

    @classmethod
    def get_model_layout_dict(cls):
        """
        Returns a dictionary with the field character lengths for each field defined for the model.
        Ordered dict specifies the order of the fields, and number specifies the length
        :return: dict containing model layout to use for translation
        """
        if cls.data_layout_dict is None:
            d = collections.OrderedDict()
            d['century_year'] = 4
            d['dckt_jdg_num_yr'] = 2
            d['dckt_jdg_seq_num'] = 6
            d['dckt_jdg_type_code'] = 2
            d['debt_num'] = 3
            d['party_num'] = 3
            d['ptydbt_status_code'] = 2
            d['ptydbt_status_date'] = 8
            d['case_title'] = 50
            d['party_last_name'] = 20
            d['party_first_name'] = 9
            d['party_mid_intl'] = 1
            d['party_cnt'] = 3
            d['party_dbt_cnt'] = 3
            d['filler'] = 8
            d['partical_close_indicator'] = 1
            d['warrent_of_sat_indicator'] = 1
            d['closing_document_code'] = 3  #
            d['jptydoc_target'] = 1
            d['venue_id'] = 3
            d['dckt_type_code'] = 2
            d['dckt_seq_num'] = 6
            d['dckt_crt_year'] = 2
            d['nonacms_venue_id'] = 2
            d['nonacms_key_frst'] = 2
            d['nonacms_key_mid'] = 6
            d['nonacms_key_last'] = 2
            d['extract_start_date'] = 8  #
            d['extract_end_date'] = 8
            d['filler2'] = 29
            cls.data_layout_dict = d
        return cls.data_layout_dict

    @classmethod
    def extract_data_from_line(self, line):  # @TODO: move this function in both report types to base class
        """
        Test function - translate the line data into key value pairs based on the dictionary definition above
        :param line: the line to parse
        :return:
        """
        d = StateClosingsReport.get_model_layout_dict()
        pos = 0
        i = 0
        l = line
        for k, v in list(d.items()):
            last_pos = pos
            pos += v
            # data_extract = line[last_pos:pos]
            data_extract = str(line[last_pos:pos]).strip()
            print(("{}: {}".format(k, data_extract)))
        # parsed = True  # stupid
        # return parsed
# ----------------------------


class Jdc0503(Enum):
    """
    Definition for judgment record types
    """
    JCASEHEADER = 'A'
    JDGMNT = 'B'
    JDGDEBT = 'C'
    JPARTY = 'D'
    JDGMCOM = 'E'

class Jdc0503Party(Enum):
    """
    Definition for party types
    """
    PARTYCREDITOR = '0'
    PARTYDEBTOR = '1'
    PARTYALT = '2'
    PARTYGUARDIAN = '3'

class DatabaseExtractBase(models.Model):
    '''
    d = dict from class specifying layout of data line, provided by implementing class
    e.g. d = Case.get_model_layout_dict()
    :return collections.OrderedDict
    '''
    @classmethod
    def extract_data_from_line(self, line, d):
        """
        Translate the line data into key value pairs based on the dictionary definition above
        :param line: line to parse
        :param d: dictionary to use for data translation lookups
        :return:
        """
        extracted_data = collections.OrderedDict()
        pos = 0
        i = 0
        l = line
        for k, v in list(d.items()):
            last_pos = pos
            pos += v
            data_extract = line[last_pos:pos]
            extracted_data[k] = data_extract
        return extracted_data

    class Meta:
        abstract = True


class Case(DatabaseExtractBase):
    # JDC0503A-HEADER
    report_number = models.CharField(max_length=50)
    venue_id = models.CharField(max_length=50)
    court_code = models.CharField(max_length=50)
    report_request_number = models.CharField(max_length=50)
    docketed_judgment_cc = models.CharField(max_length=50)
    docketed_judgment_yy = models.CharField(max_length=50)
    docketed_judgment_seq_num = models.CharField(max_length=50)
    docketed_judgment_type_code = models.CharField(max_length=50)
    debt_number = models.CharField(max_length=50)
    record_type_code = models.CharField(max_length=50)
    # JDC0503A-DATA
    report_request_date = models.CharField(max_length=50)
    report_from_date = models.CharField(max_length=50)
    report_to_date = models.CharField(max_length=50)
    record_type_code_data = models.CharField(max_length=50)
    docketed_judgment_number = models.CharField(max_length=50, db_index=True)
    nonacms_docket_number = models.CharField(max_length=50)
    nonacms_venue_id = models.CharField(max_length=50)
    nonacms_docket_type = models.CharField(max_length=50)
    case_type_code = models.CharField(max_length=50)
    case_title = models.CharField(max_length=55)
    case_filed_date = models.CharField(max_length=50)
    acms_docket_number = models.CharField(max_length=50)
    acms_venue_id = models.CharField(max_length=50)
    acms_court_code = models.CharField(max_length=50)

    data_layout_dict = collections.OrderedDict()

    @classmethod
    def get_model_layout_dict(cls):
        """
        Returns a dictionary with the field character lengths for each field defined for the model.
        Ordered dict specifies the order of the fields, and number specifies the length
        :return: dict containing model layout to use for translation
        """
        if not cls.data_layout_dict:
            d = cls.data_layout_dict
            d['report_number'] = 7
            d['venue_id'] = 3
            d['court_code'] = 3
            d['report_request_number'] = 2
            d['docketed_judgment_cc'] = 2
            d['docketed_judgment_yy'] = 2
            d['docketed_judgment_seq_num'] = 6
            d['docketed_judgment_type_code'] = 2
            d['debt_number'] = 3
            d['record_type_code'] = 1
            d['filler'] = 29
            # JDC0503A-DATA
            d['report_request_date'] = 8
            d['report_from_date'] = 8
            d['report_to_date'] = 8
            d['record_type_code_data'] = 1
            d['docketed_judgment_number'] = 10
            d['nonacms_docket_number'] = 12
            d['nonacms_venui_id'] = 3
            d['nonacms_docket_type'] = 2
            d['filler2'] = 35
            d['case_type_code'] = 3
            d['case_title'] = 55
            d['case_filed_date'] = 8
            d['acms_docket_number'] = 10
            d['acms_venue_id'] = 3
            d['acms_court_code'] = 3
            d['filler3'] = 71
            cls.data_layout_dict = d
        return cls.data_layout_dict

    def __unicode__(self):
        """
        Use case title field for tostring function
        :return:
        """
        return self.case_title

    @property
    def first_judgment_amt(self):
        """
        Convenience function to return the first amount in a set of judgments
        :return:
        """
        return repr(self.judgment_set.all()[0])


class Judgment(DatabaseExtractBase):
    # JDC0503B-RECORD
    report_number = models.CharField(max_length=50)
    venue_id = models.CharField(max_length=50)
    court_code = models.CharField(max_length=50)
    report_request_number = models.CharField(max_length=50)
    docketed_judgment_cc = models.CharField(max_length=50)
    docketed_judgment_yy = models.CharField(max_length=50)
    docketed_judgment_seq_num = models.CharField(max_length=50)
    docketed_judgment_type_code = models.CharField(max_length=50)
    debt_number = models.CharField(max_length=50)
    record_type_code_data = models.CharField(max_length=50)
    # JDC0503B-DATA
    record_type_code_debt_data = models.CharField(max_length=50)
    docketed_judgment_number_debt_data = models.CharField(max_length=50)
    judgment_number = models.CharField(max_length=50)
    judgment_status_code = models.CharField(max_length=50)
    judgment_status_date = models.CharField(max_length=50)
    judgment_orig_amt = models.CharField(max_length=50)
    judgment_orig_taxed_cost_amt = models.CharField(max_length=50)
    judgment_orig_interest_amt = models.CharField(max_length=50)
    judgment_orig_atty_fee_amt = models.CharField(max_length=50)
    judgment_other_awd_orig_amt = models.CharField(max_length=50)
    judgment_due_amt = models.CharField(max_length=50)
    judgment_due_taxed_cost_amt = models.CharField(max_length=50)
    judgment_due_interest_amt = models.CharField(max_length=50)
    judgment_due_atty_fee_amt = models.CharField(max_length=50)
    judgment_due_other_award_due_amt = models.CharField(max_length=50)
    judgment_time = models.CharField(max_length=50)
    judgment_docketed_date = models.CharField(max_length=50)
    judgment_entered_date = models.CharField(max_length=50)
    judgment_issued_date = models.CharField(max_length=50)
    case = models.ForeignKey(Case, null=False, on_delete=models.CASCADE)

    data_layout_dict = collections.OrderedDict()

    @classmethod
    def get_model_layout_dict(cls):
        """
        Returns a dictionary with the field character lengths for each field defined for the model.
        Ordered dict specifies the order of the fields, and number specifies the length
        :return: dict containing model layout to use for translation
        """

        if not cls.data_layout_dict:
            d = cls.data_layout_dict
            d['report_number'] = 7
            d['venue_id'] = 3
            d['court_code'] = 3
            d['report_request_number'] = 2
            d['docketed_judgment_cc'] = 2
            d['docketed_judgment_yy'] = 2
            d['docketed_judgment_seq_num'] = 6
            d['docketed_judgment_type_code'] = 2
            d['docketed_judgment_type_code'] = 2
            d['debt_number'] = 3
            d['record_type_code_data'] = 1
            d['filler'] = 29
            d['record_type_code_debt_data'] = 1
            d['docketed_judgment_number_debt_data'] = 10
            d['judgment_number'] = 10
            d['judgment_status_code'] = 1
            d['judgment_status_date'] = 8
            d['judgment_orig_amt'] = 11
            d['judgment_orig_taxed_cost_amt'] = 11
            d['judgment_orig_interest_amt'] = 11
            d['judgment_orig_atty_fee_amt'] = 11
            d['judgment_other_awd_orig_amt'] = 11
            d['judgment_due_amt'] = 11
            d['judgment_due_taxed_cost_amt'] = 11
            d['judgment_due_interest_amt'] = 11
            d['judgment_due_atty_fee_amt'] = 11
            d['judgment_due_other_award_due_amt'] = 11
            d['judgment_time'] = 4
            d['judgment_docketed_date'] = 8
            d['judgment_entered_date'] = 8
            d['judgment_issued_date'] = 8
            d['filler2'] = 72
            cls.data_layout_dict = d
        return cls.data_layout_dict

    def __repr__(self):
        """
        Convenience method to return a dollar amount for the judgment
        :return: amount translated from cobol encoded format
        """
        amt = self.judgment_orig_amt
        return '${}.{}'.format(amt[:9].lstrip('0'), amt[9])

class Debt(DatabaseExtractBase):

    report_number = models.CharField(max_length=50)
    venue_id = models.CharField(max_length=50)
    court_code = models.CharField(max_length=50)
    report_request_number = models.CharField(max_length=50)
    docketed_judgment_number_cc = models.CharField(max_length=50)
    docketed_judgment_number_year = models.CharField(max_length=50)
    docketed_judgment_seq_num = models.CharField(max_length=50, db_index=True)
    docketed_judgment_type_code = models.CharField(max_length=50)
    debt_number = models.CharField(max_length=50)
    record_type_code = models.CharField(max_length=50)
    # JDC0503C - DATA
    record_type_code = models.CharField(max_length=50)
    docketed_judgment_number = models.CharField(max_length=50)
    debt_number = models.CharField(max_length=50)
    debt_status_code = models.CharField(max_length=50, db_index=True)
    debt_status_date = models.CharField(max_length=50)
    entered_date = models.CharField(max_length=50)
    party_orig_amt = models.CharField(max_length=50)
    party_orig_taxed_cost_amt = models.CharField(max_length=50)
    party_orig_interest_amt = models.CharField(max_length=50)
    party_orig_atty_fee_amt = models.CharField(max_length=50)
    party_other_award_orig_amt = models.CharField(max_length=50)
    party_due_amt = models.CharField(max_length=50)
    party_due_taxed_cost_amt = models.CharField(max_length=50)
    party_due_interest_amt = models.CharField(max_length=50)
    party_due_atty_fee_amt = models.CharField(max_length=50)
    party_other_awd_due_amt = models.CharField(max_length=50)
    debt_comments = models.CharField(max_length=55)
    case = models.ForeignKey(Case, null=False, on_delete=models.CASCADE)

    _data_layout_dict = collections.OrderedDict()

    @classmethod
    def get_model_layout_dict(cls):
        """
        Returns a dictionary with the field character lengths for each field defined for the model.
        Ordered dict specifies the order of the fields, and number specifies the length
        :return: dict containing model layout to use for translation
        """

        if not cls._data_layout_dict:
            d = cls._data_layout_dict
            # JDC0503C-RECORD
            d['report_number'] = 7
            d['venue_id'] = 3
            d['court_code'] = 3
            d['report_request_number'] = 2
            d['docketed_judgment_number_cc'] = 2
            d['docketed_judgment_number_year'] = 2
            d['docketed_judgment_seq_num'] = 6
            d['docketed_judgment_type_code'] = 2
            d['debt_number'] = 3
            d['record_type_code'] = 1
            d['filler'] = 29
            # JDC0503C - DATA
            d['record_type_code_data'] = 1
            d['docketed_judgment_number'] = 10
            d['debt_number_data'] = 3
            d['debt_status_code'] = 1
            d['debt_status_date'] = 8
            d['entered_date'] = 8
            d['party_orig_amt'] = 11
            d['party_orig_taxed_cost_amt'] = 11
            d['party_orig_interest_amt'] = 11
            d['party_orig_atty_fee_amt'] = 11
            d['party_other_award_orig_amt'] = 11
            d['party_due_amt'] = 11
            d['party_due_taxed_cost_amt'] = 11
            d['party_due_interest_amt'] = 11
            d['party_due_atty_fee_amt'] = 11
            d['party_other_awd_due_amt'] = 11
            d['debt_comments'] = 55
            d['filler2'] = 44
            cls._data_layout_dict = d
        return cls._data_layout_dict


class PartyBase(DatabaseExtractBase):
    """
    This is a base class shared by all judgment records
    Note this is an abstract class and cannot be instantiated
    """
    # DC0503D-RECORD - PARTY
    report_number = models.CharField(max_length=50)
    venue_id = models.CharField(max_length=50)
    court_code = models.CharField(max_length=50)
    report_request_number = models.CharField(max_length=50)
    docketed_judgment_cc = models.CharField(max_length=50)
    docketed_judgment_year = models.CharField(max_length=50)
    docketed_judgment_seq_num = models.CharField(max_length=50)
    docketed_judgment_type_code = models.CharField(max_length=50)
    debt_number = models.CharField(max_length=50)
    record_type_code = models.CharField(max_length=50) # @TODO: change field name to record_type_code_data, also for comments class
    party_type_indicator = models.CharField(max_length=50)
    case = models.ForeignKey(Case, null=False, on_delete=models.CASCADE)

    data_layout_dict = collections.OrderedDict()

    @classmethod
    def get_model_layout_dict(cls):
        """
        Returns a dictionary with the field character lengths for each field defined for the model.
        Ordered dict specifies the order of the fields, and number specifies the length
        :return: dict containing model layout to use for translation
        """

        if not cls.data_layout_dict:
            d = cls.data_layout_dict
            d['report_number'] = 7
            d['venue_id'] = 3
            d['court_code'] = 3
            d['report_request_number'] = 2
            d['docketed_judgment_cc'] = 2
            d['docketed_judgment_year'] = 2
            d['docketed_judgment_seq_num'] = 6
            d['docketed_judgment_type_code'] = 2
            d['debt_number'] = 3
            d['record_type_code_data'] = 1
            d['party_type_indicator'] = 1
            d['filler'] = 28
            cls.data_layout_dict = d
        return cls.data_layout_dict

    class Meta:
        abstract = True


class Party(PartyBase):
    # DC0503D-RECORD - PARTY
    # JDC0503D-PARTY-DATA
    record_type_code_party = models.CharField(max_length=50)
    party_type_indicator_party = models.CharField(max_length=50)
    docketed_judgment_number = models.CharField(max_length=50, db_index=True)
    debt_number_party = models.CharField(max_length=50)
    party_last_name = models.CharField(max_length=50, db_index=True)
    party_first_name = models.CharField(max_length=50, db_index=True)
    party_initial = models.CharField(max_length=50, db_index=True)
    party_role_type_code = models.CharField(max_length=50, db_index=True)
    ptydebt_status_date = models.CharField(max_length=50, db_index=True)
    ptydebt_status_code = models.CharField(max_length=50, db_index=True)
    atty_firm_last_name = models.CharField(max_length=50)
    atty_firm_first_name = models.CharField(max_length=50)
    atty_firm_middle_init = models.CharField(max_length=50)
    nonatty_comments = models.CharField(max_length=50)
    party_initials = models.CharField(max_length=50, db_index=True)
    party_street_name = models.CharField(max_length=50, db_index=True)
    party_addt_street_name = models.CharField(max_length=50, db_index=True)
    party_city_name = models.CharField(max_length=50, db_index=True)
    party_state_code = models.CharField(max_length=50)
    party_zip_5 = models.CharField(max_length=50)
    party_zip_4 = models.CharField(max_length=50)
    party_affiliation_code = models.CharField(max_length=50)
    party_number = models.CharField(max_length=50)
    merged_party_name = models.CharField(max_length=100, db_index=True, blank=True)
    full_search_party_name = models.CharField(max_length=255, db_index=True, blank=True)

    @classmethod
    def get_model_layout_dict(cls):
        """
        Returns a dictionary with the field character lengths for each field defined for the model.
        Ordered dict specifies the order of the fields, and number specifies the length
        :return: dict containing model layout to use for translation
        """

        if not cls.data_layout_dict:
            d = super(Party, cls).get_model_layout_dict()
            # JDC0503D-PARTY-DATA
            # # d = cls.data_layout_dict
            # d = Party.get_model_layout_dict()
            d['record_type_code_party'] = 1
            d['party_type_indicator_party'] = 1
            d['docketed_judgment_number'] = 10
            d['debt_number_party'] = 3
            d['party_last_name'] = 20
            d['party_first_name'] = 9
            d['party_initial'] = 1
            d['party_role_type_code'] = 2
            d['ptydebt_status_date'] = 8
            d['ptydebt_status_code'] = 2
            d['atty_firm_last_name'] = 20
            d['atty_firm_first_name'] = 9
            d['atty_firm_middle_init'] = 1
            d['nonatty_comments'] = 35
            d['party_initials'] = 10
            d['party_street_name'] = 36
            d['party_addt_street_name'] = 36
            d['party_city_name'] = 16
            d['party_state_code'] = 2
            d['party_zip_5'] = 5
            d['party_zip_4'] = 4
            d['party_affiliation_code'] = 3
            d['party_number'] = 3
            d['filler2'] = 3
            cls.data_layout_dict = d
            # print("building dict...")
        return cls.data_layout_dict


class PartyAlt(PartyBase):
    # JDC0503D-PRTYALT-DATA REDEFINES JDC0503D-PARTY-DATA
    record_type_code_partyalt = models.CharField(max_length=50)
    party_type_indicator_partyalt = models.CharField(max_length=50)
    docketed_judgment_number = models.CharField(max_length=50)
    debt_number_partyalt = models.CharField(max_length=50)
    party_alternate_name = models.CharField(max_length=50, db_index=True)
    party_last_name = models.CharField(max_length=50, db_index=True)
    party_first_name = models.CharField(max_length=50, db_index=True)
    party_initial = models.CharField(max_length=50, db_index=True)
    alternate_name_type_code = models.CharField(max_length=50)
    party_number = models.CharField(max_length=50)
    full_search_party_name = models.CharField(max_length=255, db_index=True, blank=True)

    @classmethod
    def get_model_layout_dict(cls):
        """
        Returns a dictionary with the field character lengths for each field defined for the model.
        Ordered dict specifies the order of the fields, and number specifies the length
        :return: dict containing model layout to use for translation
        """

        if not cls.data_layout_dict:
            super(PartyAlt, cls).get_model_layout_dict()
            d = cls.data_layout_dict
            d['record_type_code_partyalt'] = 1
            d['party_type_indicator_partyalt'] = 1
            d['docketed_judgment_number'] = 10
            d['debt_number_partyalt'] = 3
            d['party_alternate_name'] = 3
            d['party_last_name'] = 20
            d['party_first_name'] = 9
            d['party_initial'] = 1
            d['alternate_name_type_code'] = 2
            d['party_number'] = 3
            d['filler'] = 125
            cls.data_layout_dict = d
        return cls.data_layout_dict


class PartyGuardian(PartyBase):
    # JDC0503D-GARDIAN-DATA  REDEFINES  JDC0503D-PARTY-DATA
    record_type_code_guardian = models.CharField(max_length=50)
    party_type_indicator_guardian = models.CharField(max_length=50)
    docketed_judgment_number = models.CharField(max_length=50)
    debt_number_guardian = models.CharField(max_length=50)
    guardian_last_name = models.CharField(max_length=50, db_index=True)
    guardian_first_name = models.CharField(max_length=50, db_index=True)
    guardian_initial = models.CharField(max_length=50, db_index=True)
    party_last_name = models.CharField(max_length=50, db_index=True)
    party_first_name = models.CharField(max_length=50, db_index=True)
    party_initial = models.CharField(max_length=50, db_index=True)
    guardian_affiliation_code = models.CharField(max_length=50)
    party_number = models.CharField(max_length=50)

    @classmethod
    def get_model_layout_dict(cls):
        """
        Returns a dictionary with the field character lengths for each field defined for the model.
        Ordered dict specifies the order of the fields, and number specifies the length
        :return: dict containing model layout to use for translation
        """

        if not cls.data_layout_dict:
            super(PartyGuardian, cls).get_model_layout_dict()
            d = cls.data_layout_dict
            d['record_type_code_guardian'] = 1
            d['party_type_indicator_guardian'] = 1
            d['docketed_judgment_number'] = 10
            d['debt_number_guardian'] = 3
            d['guardian_last_name'] = 20
            d['guardian_first_name'] = 9
            d['guardian_initial'] = 1
            d['party_last_name'] = 20
            d['party_first_name'] = 9
            d['party_initial'] = 1
            d['guardian_affiliation_code'] = 3
            d['party_number'] = 3
            d['filler2'] = 159
            cls.data_layout_dict = d
        return cls.data_layout_dict


class Comment(DatabaseExtractBase):
    # JDC0503E-RECORD comments record
    report_number = models.CharField(max_length=50)
    venue_id = models.CharField(max_length=50)
    court_code = models.CharField(max_length=50)
    report_request_number = models.CharField(max_length=50)
    docketed_judgment_cc = models.CharField(max_length=50)
    docketed_judgment_year = models.CharField(max_length=50)
    docketed_judgment_seq_num = models.CharField(max_length=50)
    docketed_judgment_type_code = models.CharField(max_length=50)
    debt_number = models.CharField(max_length=50)
    record_type_code = models.CharField(max_length=50)
    entered_date = models.CharField(max_length=50)
    # JDC0503E-DATA.
    record_type_code_data = models.CharField(max_length=50)
    docketed_judgment_number = models.CharField(max_length=50)
    jdgcomm_comments = models.CharField(max_length=75)
    entered_date = models.CharField(max_length=50)
    case = models.ForeignKey(Case, null=False, on_delete=models.CASCADE)

    data_layout_dict = collections.OrderedDict()

    @classmethod
    def get_model_layout_dict(cls):
        """
        Returns a dictionary with the field character lengths for each field defined for the model.
        Ordered dict specifies the order of the fields, and number specifies the length
        :return: dict containing model layout to use for translation
        """

        if not cls.data_layout_dict:
            d = cls.data_layout_dict
            d['report_number'] = 7
            d['venue_id'] = 3
            d['court_code'] = 3
            d['report_request_number'] = 2
            d['docketed_judgment_cc'] = 2
            d['docketed_judgment_year'] = 2
            d['docketed_judgment_seq_num'] = 6
            d['docketed_judgment_type_code'] = 2
            d['debt_number'] = 3
            d['record_type_code'] = 1
            d['entered_date'] = 8
            d['filler'] = 21
            # JDC0503E-DATA.
            d['record_type_code_data'] = 1
            d['docketed_judgment_number'] = 10
            d['jdgcomm_comments'] = 75
            d['entered_date'] = 8
            d['filler2'] = 146
            cls.data_layout_dict = d
        return cls.data_layout_dict


class StateJudgmentReport:
    """
        Model for JDC0503S report
    """
    d = collections.OrderedDict()

    record_type = 'X' #  set this by parsing the correct portion of the string
    if record_type == 'A':
        m = Case()
    elif record_type == 'B':
        # m = Judgment()
        pass
    elif record_type == 'C':
        # m = Debt()
        pass
    elif record_type == 'D':
        # m = Party()
        # m = PartyAlt()
        # m = Guardian()
        pass
    elif record_type == 'E':
        # m = Comment()
        pass
    else:
        pass # @TODO: throw an exception

    # def build_report_dict(self):
    #     # d['century_year'] = 4
    #     self.report_dict = None # d


class StateReportDataLoader():
    """
    Manages the data received from a state data file. Typically this file is received via email
    """

    def __init__(self, filename):
        self.filename = filename
        content = self._load_503_data()
        self.content = content
        self.test_line_num = 0
        self.last_content_line_num = 0
        self.rec_type_location = 30  # @TODO: create and move to base class in model
        self.party_type_location = 31

    def _get_single_line(self, line_num):
        """
        Return a single line from the content loaded by this class
        :param line_num: the number of the line to return from the internal data structure
        :return: string representing returned line
        """
        line = self.content[line_num]
        return line

    def _load_503_data(self):
        """
        Open the data file provided when the class was initialized and make accessible via an internal variable
        :return: list of lines containing content
        """
        import os.path
        from django.conf import settings

        # filename = settings.MEDIA_ROOT + '/padjdc0503.txt'
        # filename = settings.MEDIA_ROOT + '/' + self.filename
        content = None
        if os.path.isfile(self.filename):
            with open(self.filename) as f:
                content = f.readlines()
        return content

    def _save_line_contents_to_db(self, unparsed_line, rec_type, model_type, parent_case_model = None):
        """
        Take an unparsed data content line and store the resulting record in the database
        :param unparsed_line: unparsed data line from file
        :param rec_type: judgment record type
        :param model_type: model to use for mapping the record type
        :param parent_case_model: optional parent case model, useful for e.g. alt party type records
        :return: model type that the unparsed_line data maps to
        """
        d = model_type.get_model_layout_dict()
        m = model_type()
        pos = 0
        for k, v in list(d.items()):
            last_pos = pos
            pos += v
            data_extract = unparsed_line[last_pos:pos]
            # print("{}: {}".format(k, data_extract))
            # m[k] = data_extract
            setattr(m, k, str(data_extract).strip())
        if parent_case_model is not None:
            setattr(m, 'case', parent_case_model)
            m.save()
        else:
            # check if the case already exists in the db before saving it again
            saved_case = model_type
            dj_num = getattr(m, 'docketed_judgment_number')
            if not saved_case.objects.filter(docketed_judgment_number=dj_num).exists():
                m.save()
            return m
        # m.save(force_insert=True)
        # print('Created {} model with id {} and sequence number {}'.format(rec_type, m.id, m.docketed_judgment_seq_num))
        # if parent_case_model is None:
        #     return m
        # else
        #     return None

    def _map_rec_type_to_model(self, rec_type, line):
        """
        Figures out what model to use for the underlying record type specified in the line
        :param rec_type: judgment record type. i.e A, B, C from data record layout specs
        :param line: data line to parse
        :return: Enum of model type and the corresponding model class
        """
        model_type = None
        model_class = None
        if rec_type == Jdc0503.JDGMNT.value:
            model_type = Jdc0503.JDGDEBT
            model_class = Judgment
        elif rec_type == Jdc0503.JDGDEBT.value:
            model_type = Jdc0503.JDGDEBT
            model_class = Debt
        elif rec_type == Jdc0503.JPARTY.value:
            # set based on sub_type
            party_type = line[self.party_type_location]
            if party_type == Jdc0503Party.PARTYCREDITOR.value:
                model_type = Jdc0503.JPARTY
                model_class = Party
            elif party_type == Jdc0503Party.PARTYDEBTOR.value:
                model_type = Jdc0503.JPARTY
                model_class = Party
            elif party_type == Jdc0503Party.PARTYALT.value:
                model_type = Jdc0503Party.PARTYALT
                model_class = PartyAlt
            elif party_type == Jdc0503Party.PARTYGUARDIAN.value:
                model_type = Jdc0503Party.PARTYGUARDIAN
                model_class = PartyGuardian
        elif rec_type == Jdc0503.JDGMCOM.value:
            model_type = Jdc0503.JDGMCOM
            model_class = Comment
        return model_type, model_class

    def import_file_to_db(self, num_lines = 1000):
        """
        Takes the entire contents of the file and loads each line into the database
        :param num_lines: optional number of lines to parse. Default is 1000
        """
        import logging

        logger = logging.getLogger(__name__)
        content = self.content
        file_len = len(content)
        # debug_lines_to_parse = 200000
        debug_lines_to_parse = num_lines
        num_cases_added = 0
        parent_case = None
        parent_case_model = None

        from django.db import transaction
        with transaction.atomic():
            for i in range(file_len):
                line = self._get_single_line(i)
                rec_type = line[self.rec_type_location]
                if rec_type == Jdc0503.JCASEHEADER.value:
                    # store the pk for child records
                    parent_case_model = self._save_line_contents_to_db(line, Jdc0503.JCASEHEADER, Case)
                    # print('Stored Case model with primary key: {}'.format(parent_case_model.id))
                    num_cases_added += 1
                    if num_cases_added % 2000 == 0:
                        logger.debug('Total cases added: {}'.format(num_cases_added))
                else:
                    if parent_case_model.pk:
                        rec_type, model_class = self._map_rec_type_to_model(rec_type, line)
                        if rec_type is None:
                            raise ValueError('Oh no problem with line: {}'.format(line))
                        else:
                            # print(model_type)
                            if model_class is not None:
                                self._save_line_contents_to_db(line, rec_type, model_class, parent_case_model)
                                # print('Added {} record type to parent case {}'.format(rec_type, parent_case_model.id))
                            else:
                                raise ValueError('Got a model class of None - (likely due to an unknown party type): {}'.format(line))
                if i > debug_lines_to_parse:
                    break


class StateClosingsDataLoader():
    """
    Handles processing of the closings data file
    """
    def __init__(self, filename):
        self.filename = filename
        content = self._load_501_data()
        self.content = content
        self.test_line_num = 0
        self.last_content_line_num = 0
        # self.rec_type_location = 30  # @TODO: create and move to base class in model
        # self.party_type_location = 31

    def _get_single_line(self, line_num):
        """
        Return a single line from the content loaded by this class
        :param line_num: the number of the line to return from the internal data structure
        :return: string representing returned line
        """
        line = self.content[line_num]
        return line

    def _load_501_data(self):
        """
        Open the data file provided when the class was initialized and make accessible via an internal variable
        :return: list of lines containing content
        """
        import os.path
        content = None
        if os.path.isfile(self.filename):
            with open(self.filename) as f:
                content = f.readlines()
        return content

    def _save_line_contents_to_db(self, unparsed_line, report_batch):
        """
        Take an unparsed data content line and store the resulting record in the database
        :param unparsed_line: unparsed data line from file
        :param report_batch: the batch number to assign to the saved model
        """
        d = StateClosingsReport.get_model_layout_dict()
        m = StateClosingsReport()
        pos = 0
        for k, v in list(d.items()):
            last_pos = pos
            pos += v
            data_extract = unparsed_line[last_pos:pos]
            # print("{}: {}".format(k, data_extract))
            # m[k] = data_extract
            setattr(m, k, str(data_extract).strip())
        # if parent_case_model is not None:
        #     setattr(m, 'case', parent_case_model)
        # m.save(force_insert=True)
        m.report_batch = report_batch
        m.save()
        # print('Created {} model with id {} and sequence number {}'.format(rec_type, m.id, m.docketed_judgment_seq_num))
        # if parent_case_model is None:
        #     return m
        # else
        #     return None

    def import_file_to_db(self, num_lines = 1000):
        """
        Takes the entire contents of the file and loads each line into the database
        :param num_lines: optional number of lines to parse. Default is 1000
        """

        import dateparser
        import logging

        logger = logging.getLogger(__name__)
        content = self.content
        file_len = len(content)
        # debug_lines_to_parse = 200000
        debug_lines_to_parse = num_lines
        num_cases_added = 0
        parent_case = None
        parent_case_model = None

        from django.db import transaction
        with transaction.atomic():
            report_batch = ReportBatch()
            report_batch.file_name = '-'  # self.filename
            report_batch.date_processed = dateparser.parse('now')
            report_batch.save()
            for i in range(file_len):
                line = self._get_single_line(i)
                self._save_line_contents_to_db(line, report_batch)
                # print('Stored Case model with primary key: {}'.format(parent_case_model.id))
                num_cases_added += 1
                if num_cases_added % 2000 == 0:
                    logger.debug('Total cases added: {}'.format(num_cases_added))
                if i > debug_lines_to_parse:
                    break

class StateReportQueryManager():
    """
    Convenience class for handling various queries related to state report data in the database
    """

    short_search_name_length = 4

    @staticmethod
    def make_first_name_variations(first_name):  # @TODO: replace with live query against DB
        """
        Test function to return a list of aliases for a given name
        :param first_name: either luis or leroy
        :return: a list of name aliases
        """
        name_list = []
        first_name = first_name.lower()
        if first_name == 'leroy':
            name_list = ['learoy', 'lerroy', 'leyroy', 'leroye', 'luroy', 'liroy', 'leroya', 'laroy',
                         'leeroy', 'leoroy', 'leroys', 'leroi', 'louroy', 'laroye', 'leigh', 'lee', 'roy',
                         'leighroy', 'leray', 'laroya', 'lawroy', 'lereoy', 'leroyd', 'leroiya', 'laroyee',
                         'laroi', 'learoyd', 'leraye', 'lereo', 'leeray', 'leroyce', 'leroa', 'leroh',
                         'lerray', 'lueroy', 'lereya', 'leroy']
        elif first_name.lower() == 'luis':
            name_list = ['luis']
        return name_list

    @staticmethod
    def make_last_name_variations(last_name): # @TODO: replace with live query against DB
        """
        Test function to return a list of aliases for a given name
        :param last_name: either banks or enriquez or wallace
        :return: a list of name aliases
        """
        name_list = []
        last_name  = last_name.lower()
        if last_name == 'banks':
            name_list = ['banks', 'bankszz']
        elif last_name.lower() == 'enriquez':
            name_list = ['enriquez']
        elif last_name.lower() == 'wallace':
            name_list = ['wallace']
        return name_list

    @staticmethod
    def query_database_for_order(party_first_name_list = None):
        """
        Returns a case list object based on a list of provided names
        :param party_first_name_list: list of first names
        :return: list of cases
        :rtype: list
        """
        party_match = Party.objects.filter(party_first_name__in=party_first_name_list)
        cases = None
        party_cases = []
        if not party_match is None:
            for pm in party_match:
                party_cases.append(pm.case)
            cases = party_cases
        return cases

    @staticmethod
    def _filter_close_matches(searchname_str, name_list, is_first_name=False):
        """
        Only include names with lengths that are equal to n+2 and where the first three characters match
        Exclude common names from this filter and return name_list
        @TODO: apply only to non-common name matches
        :param searchname_str: name supplied for search
        :param name_list: list of name variations
        :return: List[str] filtered name list
        """
        from nameviewer.helpers import _name_is_common as is_common_name
        filtered_name_list = []
        searchname_str = searchname_str.replace('-','').replace("'",'')
        if is_common_name(searchname_str):
            filtered_name_list = name_list
        else:
            search_name_length = len(searchname_str)
            search_name_first_chars = searchname_str[:3].upper()
            for name in name_list:
                # compare name to any common name and skip if in list
                if len(name) >= search_name_length and len(name) <= search_name_length + 2:
                    if is_first_name:  # only apply first 3 letter filter to last names
                        filtered_name_list.append(name)
                    # this doesn't work for Vazquez and Vasquez
                    else:
                        match_name_first_chars = name[:3].upper()
                        if match_name_first_chars == search_name_first_chars:
                            filtered_name_list.append(name)
                        else:
                            zs_match_name_first_chars = match_name_first_chars.replace('z','s')
                            if zs_match_name_first_chars == search_name_first_chars:
                                filtered_name_list.append(name)

        return filtered_name_list

    @staticmethod
    def _short_name_filter_build(search_first_name, search_last_name):
        """
        Use a different name filter for very short names
        :param search_name:
        :param is_first_name:
        :return: Party Queryset, AltParty Queryset
        """
        party_match = Party.objects
        party_alt_match = PartyAlt.objects

        party_match = party_match.filter(party_first_name__iexact=search_first_name)
        party_alt_match = party_alt_match.filter(party_first_name__iexact=search_first_name)
        party_match = party_match.filter(party_last_name__iexact=search_last_name)
        party_alt_match = party_alt_match.filter(party_last_name__iexact=search_last_name)

        return party_match, party_alt_match

    @staticmethod
    def _append_middle_initial(party_first_name_list, middle_name):
        """
        appends a middle initial to a list of names
        :param party_first_name_list: list of first names
        :param middle_name: middle initial to append to first names
        :return: list strings of first name SPACE middle initial
        :rtype: list
        """
        x = []
        if middle_name is None:
            return party_first_name_list
        middle_initial = middle_name.strip()
        for first_name in party_first_name_list:
            x.append("{} {}".format(first_name, middle_initial))
        return x

    @staticmethod
    def _first_name_filter_build0(searchname_first_name, use_namelist_db, extra_name=None):
        """
        This is the original relational database lookup function.
        Build filter objects for first name party and alt party search
        :param searchname_first_name: user supplied first name to search on
        :param use_namelist_db: boolean for whether to use name db variations while searching
        :return: Party Queryset, AltParty Queryset
        """
        from django.db.models import Q
        from nameviewer.helpers import first_name_variations_from_db

        if not use_namelist_db:
            party_first_name_list = StateReportQueryManager.make_first_name_variations(searchname_first_name)
        else:
            party_first_name_list = first_name_variations_from_db(searchname_first_name)
            if extra_name:  # for asian names like youngjung, pre-splitting routine
                party_first_name_list.append(extra_name)
        party_first_name_list = StateReportQueryManager._filter_close_matches(searchname_first_name, party_first_name_list, is_first_name=True)
        party_match = Party.objects
        party_alt_match = PartyAlt.objects
        q_objs = Q()
        for n in party_first_name_list:
            q_objs |= Q(full_search_party_name__icontains=' ' + n + ' ')
        party_match = party_match.filter(q_objs)
        # alt party
        q_alt_objs = Q()
        for n in party_first_name_list:
            q_alt_objs |= Q(full_search_party_name__icontains=' ' + n + ' ')
        party_alt_match = party_alt_match.filter(q_alt_objs)
        return party_match, party_alt_match

    @staticmethod
    def _first_name_filter_build(searchname_first_name, use_namelist_db, extra_name=None, middle_name=None):
        """
        Build filter objects for first name party and alt party search
        :param searchname_first_name: user supplied first name to search on
        :param use_namelist_db: boolean for whether to use name db variations while searching
        :return: Party Queryset, AltParty Queryset
        """
        from django.db.models import Q
        from nameviewer.helpers import first_name_variations_from_db

        if not use_namelist_db:
            party_first_name_list = StateReportQueryManager.make_first_name_variations(searchname_first_name)
        else:
            party_first_name_list = first_name_variations_from_db(searchname_first_name)
            # if str(middle_name):
            #     party_first_name_list = StateReportQueryManager._append_middle_initial(party_first_name_list, middle_name)

            if extra_name:  # for asian names like youngjung, pre-splitting routine
                party_first_name_list.append(extra_name)
            # elif extra_name and str(middle_name):
            #     party_first_name_list.append("{} {}".format(extra_name, middle_name).strip())
        party_first_name_list = StateReportQueryManager._filter_close_matches(searchname_first_name, party_first_name_list, is_first_name=True)
        party_match = Party.objects
        party_alt_match = PartyAlt.objects
        q_obj_middle_name = ""
        if middle_name.strip():
            q_obj_middle_name = middle_name
        q_objs = Q()
        for n in party_first_name_list:
            q_objs |= Q(full_search_party_name__icontains=' ' + n + ' ' + q_obj_middle_name)
        party_match = party_match.filter(q_objs)
        # alt party
        q_alt_objs = Q()
        for n in party_first_name_list:
            q_alt_objs |= Q(full_search_party_name__icontains=' ' + n + ' ')
        party_alt_match = party_alt_match.filter(q_alt_objs)
        return party_match, party_alt_match


    @staticmethod
    def _build_first_name_list(searchname_first_name, extra_name=None):
        """
        Helper method to build a list of first names from the alias dictionary
        :param searchname_first_name: seed first name to use
        :param extra_name: an optional extra name to include
        :return: list of first name aliases
        """
        from nameviewer.helpers import first_name_variations_from_db
        party_first_name_list = first_name_variations_from_db(searchname_first_name)
        if extra_name:  # for asian names like youngjung, pre-splitting routine
            party_first_name_list.append(extra_name)
        ap_mod_first_names = StateReportQueryManager._replace_apostrophes_in_name_list(party_first_name_list)
        return ap_mod_first_names

    @staticmethod
    def _replace_apostrophes_in_name_list(name_list):
        """
        Helper method to remove apostrophes from a list of strings
        SCNJ database strips 's from names
        :param name_list: list of names
        :return: list of names with apostrophes removed
        """
        # ap_mod_names = [x.replace("'", " ") for x in name_list if "'" in x]  # for apostrophes
        ap_mod_names = []
        for x in name_list:
            tmp_name = x
            if "'" in x:
                tmp_name = x.replace("'", " ")
            ap_mod_names.append(tmp_name)
        return ap_mod_names

    @staticmethod
    def _build_last_name_list(searchname_last_name):
        """
        Helper method to build a list of last names from the alias dictionary
        :param searchname_last_name: seed last name to use
        :return: list of last name aliases
        """
        import logging
        from nameviewer.helpers import last_name_variations_from_db, make_latin_last_name_variations, clean_hyphenated_names

        logger = logging.getLogger(__name__)

        split_last_name_1 = clean_hyphenated_names(searchname_last_name)
        # searchname_last_name = split_last_name_1
        party_last_name_list_part_1 = last_name_variations_from_db(split_last_name_1)

        is_hyphenated_name = len(searchname_last_name.split('-')) > 1
        party_last_name_list = party_last_name_list_part_1
        if is_hyphenated_name:
            split_last_name_2 = clean_hyphenated_names(searchname_last_name, 1)
            party_last_name_list_part_2 = last_name_variations_from_db(split_last_name_2)
            party_last_name_list = party_last_name_list_part_1 + party_last_name_list_part_2

        logger.debug("Party last name: {}".format(party_last_name_list))
        ap_mod_names = StateReportQueryManager._replace_apostrophes_in_name_list(party_last_name_list)
        party_last_name_list = party_last_name_list + ap_mod_names
        # logger.warning('Generated last name list from db, {} matches found'.format(len(party_last_name_list)))
        party_last_name_list_part_1 = StateReportQueryManager._filter_close_matches(split_last_name_1, party_last_name_list)
        if is_hyphenated_name:
            party_last_name_list_part_2 = StateReportQueryManager._filter_close_matches(split_last_name_2, party_last_name_list)
            party_last_name_list = party_last_name_list_part_1 + party_last_name_list_part_2
        else:
            party_last_name_list = party_last_name_list_part_1

        extra_latin_surnames = make_latin_last_name_variations(split_last_name_1, party_last_name_list)
        if is_hyphenated_name:
            extra_latin_surnames_2 = make_latin_last_name_variations(split_last_name_2, party_last_name_list)
            extra_latin_surnames = extra_latin_surnames + extra_latin_surnames_2
        party_last_name_list = party_last_name_list + extra_latin_surnames

        return party_last_name_list

    @staticmethod
    def _full_name_filter_build(searchname_first_name, searchname_last_name, extra_name=None, middle_name=None):
        """
        Build filter objects for first name party and alt party search
        :param searchname_first_name: user supplied first name to search on
        :param use_namelist_db: boolean for whether to use name db variations while searching
        :return: Party Queryset, AltParty Queryset
        """
        from nameviewer.helpers import make_latin_last_name_variations
        import logging
        from django.conf import settings

        logger = logging.getLogger(__name__)
        # first names
        party_first_name_list = StateReportQueryManager._build_first_name_list(searchname_first_name, extra_name)
        party_first_name_list = StateReportQueryManager._filter_close_matches(searchname_first_name, party_first_name_list, is_first_name=True)
        party_match = Party.objects.using(settings.NAMESEARCH_DB)
        party_alt_match = PartyAlt.objects.using(settings.NAMESEARCH_DB)
        q_obj_middle_name = ""
        if middle_name.strip():
            q_obj_middle_name = middle_name

        # last names
        party_last_name_list = StateReportQueryManager._build_last_name_list(searchname_last_name)

        # middle name variations
        # add ok lee as the first and last name for a name like soon ok lee
        party_first_name_list = party_first_name_list + [middle_name]  # no variations on middle name @TODO: add for non ES searches as well
        # party_last_name_list = party_last_name_list + searchname_last_name  # already added to list in code above

        from statereport.elasticsearch_utils import ElasticSearchUtils
        esu = ElasticSearchUtils()
        print(("Party last name list before sending to elasticsearch: {}".format(party_last_name_list)))
        party_case_id_list = esu.scnj_case_list_from_name_list(party_first_name_list, party_last_name_list, 'scnj')
        party_match = party_match.filter(case_id__in=party_case_id_list)
        # alt party
        party_alt_case_id_list = esu.scnj_case_list_from_name_list(party_first_name_list, party_last_name_list, 'scnjalt')
        party_alt_match = party_alt_match.filter(case_id__in=party_alt_case_id_list)
        return party_match, party_alt_match


    @staticmethod
    def _last_name_filter_build(searchname_last_name, use_namelist_db, party_match, party_alt_match):
        """
        Build filter objects for last name party and alt party search
        :param searchname_last_name: user supplied last name to search on
        :param use_namelist_db: boolean for whether to use name db variations while searching
        :param party_match: Party Queryset containing first name filter
        :param party_alt_match: AltParty Queryset containing first name filter
        :return: Party Queryset, AltParty Queryset
        """
        import logging
        from nameviewer.helpers import last_name_variations_from_db, make_latin_last_name_variations
        from django.db.models import Q

        logger = logging.getLogger(__name__)
        if not use_namelist_db:
            party_last_name_list = StateReportQueryManager.make_last_name_variations(searchname_last_name)
        else:
            party_last_name_list = last_name_variations_from_db(searchname_last_name)
            logger.debug("Party last name: {}".format(party_last_name_list))
            ap_mod_names = [x.replace("'", " ") for x in party_last_name_list if "'" in x]
            party_last_name_list = party_last_name_list + ap_mod_names
            # logger.warning('Generated last name list from db, {} matches found'.format(len(party_last_name_list)))
            party_last_name_list = StateReportQueryManager._filter_close_matches(searchname_last_name, party_last_name_list)
            extra_latin_surnames = make_latin_last_name_variations(searchname_last_name, party_last_name_list)
            party_last_name_list = party_last_name_list + extra_latin_surnames
        q_objs = Q()
        for n in party_last_name_list:
            q_objs |= Q(full_search_party_name__icontains=' ' + n + ' ')
        party_match = party_match.filter(q_objs)
        # alt party
        q_alt_objs = Q()
        for n in party_last_name_list:
            q_alt_objs |= Q(full_search_party_name__icontains=' ' + n + ' ')
        party_alt_match = party_alt_match.filter(q_alt_objs)
        return party_match, party_alt_match

    @staticmethod
    def _date_from_to_filter_build(searchname, party_match, party_alt_match):
        """
        Build Queryset objects for date from and date to party search
        :param searchname: search name object containing valid to and from date
        :param party_match: Party Queryset containing first name filter
        :param party_alt_match: AltParty Queryset containing first name filter
        :return: Party Queryset, AltParty Queryset
        """
        from django.db.models import Q
        case_from_date = str(searchname.search_from).replace('-', '')
        case_to_date = str(searchname.search_to).replace('-', '')
        case_from_year = case_from_date[2:4]

        # party_debt_code_exclusions = ['17', '16', '15', '13', '12', '07']
        party_debt_code_inclusions = ['99', '14', '11', '08', '06', '05', '04', '03', '02', '01']
        # can't do ptydebt_status_date b/c this may have been updated years after the docketed judgment cc
        party_match = party_match.filter(
            ((Q(case__debt__entered_date__gte=case_from_date) & Q(case__debt__entered_date__lte=case_to_date)) |
            (Q(case__party__ptydebt_status_date__gte=case_from_date) & Q(case__party__ptydebt_status_date__lte=case_to_date))
             ) &  # revived cases - technically should check ptydebt_status_date also ~20 years
            (Q(case__party__ptydebt_status_code__in=party_debt_code_inclusions))
        )
        # party_match = party_match.filter(
        #     ((Q(case__debt__entered_date__gte=case_from_date) & Q(case__debt__entered_date__lte=case_to_date)) |
        #     (Q(case__party__ptydebt_status_date__gte=case_from_date) & Q(case__party__ptydebt_status_date__lte=case_to_date)) |
        #      (Q(case__party__ptydebt_status_code='03'))) &  # revived cases - technically should check ptydebt_status_date also ~20 years
        #     (Q(case__party__ptydebt_status_code__in=party_debt_code_inclusions))
        # )
        # party_alt_match = party_alt_match.filter(case__case_filed_date__gte=case_from_date)
        # party_alt_match = party_alt_match.filter(case__case_filed_date__lte=case_to_date)
        party_alt_match = party_alt_match.filter(
            (((Q(case__debt__entered_date__gte=case_from_date) & Q(case__debt__entered_date__lte=case_to_date)) |
            Q(case__case_filed_date__exact='00000000')) |
             Q(case__party__ptydebt_status_code='03')) &
            (Q(case__party__ptydebt_status_code__in=party_debt_code_inclusions))
        )
        return party_match, party_alt_match

    @staticmethod
    def query_database_by_searchname_details(searchname, use_namelist_db=False, seq_num=''):
        """
        Return a set of cases based on the provided searchname object
        :param searchname: a orders.model.Searchname object
        :param use_namelist_db: whether to use the name search database or not
        :param seq_num: whether to optonally filter on docketed_judgment_num. default '' means to skip this, provided through UI call otherwise
        :type searchname: orders.models.Searchname
        :return: list of ordered cases
        """

        import logging
        from django.conf import settings
        from django.db.models import Q
        from orders.utils import CaseMatchSortType
        from statereport.utils import StateReportNameSearchUtils

        merged_names_match = None

        matching_cases_sort_type = CaseMatchSortType.CASE_FILED_DATE_ASC
        if not searchname.company_name:
            debtor_code_type = 'D'

            party_match, party_alt_match = StateReportNameSearchUtils.search_name_entities(searchname, use_namelist_db, seq_num, matching_cases_sort_type)

            logger = logging.getLogger(__name__)
            #
            # matching_cases_sort_type = CaseMatchSortType.CASE_FILED_DATE_ASC
            # party_match = None
            # party_alt_match = None

            # split_names = StateReportNameSearchUtils.split_names_from_searchname(searchname)
            # if len(split_names) > 1:
            #     split_middle_name = split_names[1]
            #     # @TODO: may need to filter on this after search results come back if too many results are returned
            # # treat name searches with 3 names or more differently than typical 2 name search
            # # for 3 names or more, take the first and last name and search the db with this
            # # then post-filter results (for db query efficiency) based on remaining matches
            # # @TODO: generate name variations using first name db variations
            # if not StateReportNameSearchUtils.is_three_name_search(split_names):
            #     searchname_first_name = searchname.first_name
            #     searchname_last_name = searchname.last_name
            # else:
            #     searchname_first_name = split_names[0]
            #     searchname_last_name = split_names[-1]
            #
            # # use the elasticsearch database for lookups or just the mysql database
            # if not settings.USE_ELASTICSEARCH_SCNJ:
            #     if searchname_first_name:
            #         party_match, party_alt_match = StateReportQueryManager._first_name_filter_build(
            #             searchname_first_name,
            #             use_namelist_db,
            #             extra_name=searchname.first_name,
            #             middle_name=searchname.middle_name)
            #     if searchname_last_name:
            #         party_match, party_alt_match = \
            #             StateReportQueryManager._last_name_filter_build(searchname_last_name, use_namelist_db,
            #                                                             party_match,
            #                                                             party_alt_match)
            # else:  # use elasticsearch DB
            #     if searchname_first_name and searchname_last_name:
            #         party_match, party_alt_match = StateReportQueryManager._full_name_filter_build(
            #             searchname_first_name,
            #             searchname_last_name,
            #             extra_name=searchname.first_name,
            #             middle_name=searchname.middle_name)

            # if searchname.search_from and searchname.search_to:
            #     party_match, party_alt_match = \
            #         StateReportQueryManager._date_from_to_filter_build(searchname, party_match, party_alt_match)
            # if not seq_num is '':
            #     logger.debug("Using supplied sequence number: {}".format(seq_num))
            #     # making this work only on docket numbers minus other info
            #     party_match = Party.objects.using(settings.NAMESEARCH_DB).filter(
            #         docketed_judgment_number__exact=seq_num)

            # party_match = party_match.using(settings.NAMESEARCH_DB).filter(party_role_type_code__exact=debtor_code_type)
            # party_alt_match = party_alt_match.using(settings.NAMESEARCH_DB)
            #
            # party_match_continuations = StateReportNameSearchUtils.build_party_match_continuations(
            #     searchname.first_name,
            #     searchname.last_name)

            # # BEGIN build high value judgments
            # # party_match_high_value = StateReportNameSearchUtils.query_high_value_judgments(searchname_first_name, searchname_last_name)
            # # END build high value judgments

            # # prefetching
            # party_match.prefetch_related('case').prefetch_related('debt_set')
            #
            # # combine querysets
            # # party_match = party_match | party_match_continuations | party_match_high_value
            # party_match = party_match | party_match_continuations

            # # remove closed judgments
            # party_match = StateReportNameSearchUtils.exclude_closed_judgments(party_match)
            #
            # # sorting
            # if matching_cases_sort_type == CaseMatchSortType.CHILD_SUPPORT_AMT_DESC:
            #     party_match = party_match.order_by('-case__debt__party_orig_amt')
            # elif matching_cases_sort_type == CaseMatchSortType.CASE_FILED_DATE_ASC:
            #     party_match = party_match.order_by('-case__case_filed_date')
            #     party_alt_match = party_alt_match.order_by('-case__case_filed_date')
            # # logger.debug(party_match.query)

        else: # if searchname.company_name:
            party_match, party_alt_match = StateReportNameSearchUtils.search_company_entities(searchname)

        # trim the party match list to remove duplicates; db backend doesn't support distinct on field operations
        # pm_dict = {}
        # for pm in party_match:
        #     pm_dict[pm.id] = pm
        # party_match = pm_dict.values()
        # del(pm_dict)
        party_match = StateReportNameSearchUtils.remove_party_duplicates(party_match)
        print(('Size of party match set: {}'.format(len(party_match))))

        # pm_alt_dict = {}
        # for pm in party_alt_match:
        #     pm_alt_dict[pm.id] = pm
        # party_alt_match = pm_alt_dict.values()
        # del(pm_alt_dict)
        party_alt_match = StateReportNameSearchUtils.remove_party_duplicates(party_alt_match)
        print(('Size of party alt match set: {}'.format(len(party_alt_match))))
        # end trim

        # build the case list
        # need to parse out exact matches first, then namve variations next
        # call function with each list or handle each list in function
        # import time
        # start_time = time.time()
        # cases, child_support_cases = StateReportQueryManager. \
        #     filter_and_sort_scnj_cases(party_match, party_alt_match, merged_names_match, searchname)
        # all_cases = []
        # if matching_cases_sort_type == CaseMatchSortType.CHILD_SUPPORT_AMT_DESC:
        #     all_cases = child_support_cases + cases
        # elif matching_cases_sort_type == CaseMatchSortType.CASE_FILED_DATE_ASC:
        #     all_cases = sorted(child_support_cases + cases, key=lambda case: case.id)
        #
        # execution_time = time.time() - start_time
        # print("Sorting routine total time: {}".format(execution_time))
        all_cases = StateReportNameSearchUtils.filter_and_sort_party_matches(party_match, party_alt_match, merged_names_match, searchname, matching_cases_sort_type)

        return all_cases

    @staticmethod
    def filter_and_sort_scnj_cases(party_match, party_alt_match, merged_names_match, searchname):
        """
        This routine orders the matched cases for the final report based on pre-defined criteria.
        Some filtering is also done on cases to make sure the returned matches are closely related to the original query.
        Essentially we want both of a matching first name alias and a matching last name alias in the matched result
        :param party_match: list of matched parties
        :param party_alt_match: list of matched alt parties
        :param merged_names_match: always None
        :param searchname: orders.model.searchname object provided by user for search
        :return: list of ordered cases
        """
        def partition_cases(party_match, cases, child_support_cases, search_to_yy, searchname=None):

            def add_exact_match_only(cases_list, party_match, searchname):
                """
                Returns a list of exact match only results from a list of cases
                :param cases_list: list of cases to search through
                :param party_match: the party name to match on
                :param searchname: the original search name object
                :return:
                """
                if not isinstance(party_match, Party):
                    return
                party_name_match_list = party_match.full_search_party_name.split()
                if len(searchname.first_name) > 0:
                    searchname_first_name = searchname.first_name.upper().split()[0]
                else:
                    searchname_first_name = ''
                if len(searchname.last_name) > 0:
                    searchname_last_name = searchname.last_name.upper().split()[-1]
                else:
                    searchname_last_name = ''

                if searchname_first_name in party_name_match_list:
                    party_name_match_list = [y for y in party_name_match_list if y != searchname_first_name]
                if searchname_last_name in party_name_match_list:
                    party_name_match_list = [y for y in party_name_match_list if y != searchname_last_name]
                party_name_match_list = [y for y in party_name_match_list if len(y) > 1]  # remove initials
                full_name_length = len(searchname_first_name + searchname_last_name)
                party_name_match_list = [y for y in party_name_match_list if len(y) < full_name_length]  # remove merged names
                if len(party_name_match_list) == 0:
                    cases_list.append(pm.case)

            def pd_year_in_range(yy, search_to_yy):
                """
                Determine whether or not a PD- type case is within 10 years of the present date
                :param yy: the original case year
                :param search_to_yy: the current year
                :return:
                """
                import datetime
                yy_diff = int(search_to_yy) - int(yy) < 10
                return yy_diff < 10 and yy_diff > 0  # avoid negative numbers passing through

            # if names are supplied filter list on exact match only
            import time
            start_time = time.time()
            cases_processed = {}  # don't process
            if not party_match is None:
                for pm in party_match:
                    skip_case = True
                    c = pm.case
                    if not cases_processed.get(c.id, None):
                        print(("partition: {}".format(c)))
                        for d in c.debt_set.all():
                            if d.debt_status_code in ['A','O','R']:
                                skip_case = skip_case & False
                                if (d.docketed_judgment_type_code.strip() == 'PD') and (not pd_year_in_range(d.docketed_judgment_number_year, search_to_yy)):
                                    skip_case = True
                        if not skip_case:
                            # child support cases
                            if c.case_type_code == 232 and not c in child_support_cases:
                                if not searchname:  # just add the case
                                    child_support_cases.append(c)
                                else:  # check if this is an exact name match
                                    add_exact_match_only(child_support_cases, pm, searchname)
                            # non-child support cases
                            elif not c in cases:
                                if not searchname:  # just add the case
                                    cases.append(c)
                                else:
                                    add_exact_match_only(cases, pm, searchname)
                            # logger.warning('Generated a case with judgment number {}'.format(pm.case.docketed_judgment_number))
                            logger.debug('Generated a case with judgment number {}'.format(pm.case.docketed_judgment_number))
                        cases_processed[c.id] = True
            execution_time = time.time() - start_time
            print(("Total time elapsed for partition function: {}".format(execution_time)))

        import logging

        logger = logging.getLogger(__name__)
        cases = []
        child_support_cases = []  # requirement: child support cases all displayed first
        search_to_yy = searchname.search_to.strftime("%y")
        if party_match is not None or merged_names_match is not None or party_alt_match is not None:
            # exact name matches
            partition_cases(party_match, cases, child_support_cases, search_to_yy, searchname)
            # for now alt and guardian matches aren't treated as exact matches; logically this is ok
            # partition_cases(party_alt_match, cases, child_support_cases)
            # partition_cases(merged_names_match, cases, child_support_cases)
            # other name variation matches
            partition_cases(party_match, cases, child_support_cases, search_to_yy)
            partition_cases(party_alt_match, cases, child_support_cases, search_to_yy)
            # partition_cases(merged_names_match, cases, child_support_cases)
        else:
            logger.debug('No state report case matches found!')
        return cases, child_support_cases


class DebtAmountLookup(models.Model):
    debt = models.OneToOneField(Debt, null=False, on_delete=models.CASCADE, primary_key=True)
    party_orig_amt = models.PositiveIntegerField()
    case = models.OneToOneField(Case, null=False, on_delete=models.CASCADE)

    class Meta:
        db_table = "debt_amount_lookup"
        managed = False


class MissingJudgmentDetails(models.Model):
    """
    A group of classes that represents missing judgments pulled from the SCNJ database.
    These judgments weren't in the original data feed received by the state,
    but by looking for missing numbers in each year's sequence they were identified
    """
    JudgmentNum = models.CharField(max_length=255)
    JudgmentSummary = models.CharField(max_length=255)
    Name = models.CharField(max_length=255)
    RelatedJudgment = models.CharField(max_length=255, blank=True, default=None, null=True)
    DocketNumber = models.CharField(max_length=255, blank=True, default=None, null=True)
    VenueId = models.CharField(max_length=255, blank=True, default=None, null=True)
    FilingLocation = models.CharField(max_length=255, blank=True, default=None, null=True)
    Court = models.CharField(max_length=255, blank=True, default=None, null=True)
    JudgmentStatus = models.CharField(max_length=255, blank=True, default=None, null=True)
    StatusDate = models.CharField(max_length=255, blank=True, default=None, null=True)
    JudgmentAmount = models.CharField(max_length=255, blank=True, default=None, null=True)
    CourtCosts = models.CharField(max_length=255, blank=True, default=None, null=True)
    Interest = models.CharField(max_length=255, blank=True, default=None, null=True)
    AttorneyFee = models.CharField(max_length=255, blank=True, default=None, null=True)
    OtherAmount = models.CharField(max_length=255, blank=True, default=None, null=True)
    ProcessingLocation = models.CharField(max_length=255, blank=True, default=None, null=True)
    JudgmentEnterDate = models.CharField(max_length=255, blank=True, default=None, null=True)
    Time = models.CharField(max_length=255, blank=True, default=None, null=True)
    JudgmentFilingDate = models.CharField(max_length=255, blank=True, default=None, null=True)


class MissingJudgmentParty(models.Model):
    """
    A group of classes that represents missing judgments pulled from the SCNJ database.
    These judgments weren't in the original data feed received by the state,
    but by looking for missing numbers in each year's sequence they were identified
    """
    JudgmentNum = models.CharField(max_length=255)
    JudgmentSummary = models.CharField(max_length=255)
    DebtID = models.CharField(max_length=255)
    DebtStatus = models.CharField(max_length=255)
    DebtAmount = models.CharField(max_length=255)
    AttorneyFee = models.CharField(max_length=255, blank=True, default=None, null=True)
    Cost = models.CharField(max_length=255, blank=True, default=None, null=True)
    Interest = models.CharField(max_length=255, blank=True, default=None, null=True)
    OtherAmount = models.CharField(max_length=255, blank=True, default=None, null=True)
    DebtEnterDate = models.CharField(max_length=255, blank=True, default=None, null=True)


class MissingJudgmentDebtSummary(models.Model):
    """
    A group of classes that represents missing judgments pulled from the SCNJ database.
    These judgments weren't in the original data feed received by the state,
    but by looking for missing numbers in each year's sequence they were identified
    """
    JudgmentNum = models.CharField(max_length=255)
    JudgmentSummary = models.CharField(max_length=255)
    DebtID = models.CharField(max_length=255)
    Name = models.CharField(max_length=255, blank=True, default=None, null=True)
    Role = models.CharField(max_length=255, blank=True, default=None, null=True)
    AlternateNames = models.CharField(max_length=255, blank=True, default=None, null=True)
    DebtPartyStatus = models.CharField(max_length=255, blank=True, default=None, null=True)
    StatusDate = models.CharField(max_length=255, blank=True, default=None, null=True)


class MissingJudgmentJudgmentSummary(models.Model):
    """
    A group of classes that represents missing judgments pulled from the SCNJ database.
    These judgments weren't in the original data feed received by the state,
    but by looking for missing numbers in each year's sequence they were identified
    """
    JudgmentNum = models.CharField(max_length=255)
    JudgmentSummary = models.CharField(max_length=255)
    DebtID = models.CharField(max_length=255)
    JudgmentAmount = models.CharField(max_length=255, blank=True, default=None, null=True)
    JudgmentStatus = models.CharField(max_length=255, blank=True, default=None, null=True)
    StatusDate = models.CharField(max_length=255, blank=True, default=None, null=True)
    DebtAmount = models.CharField(max_length=255, blank=True, default=None, null=True)
    DebtStatus = models.CharField(max_length=255, blank=True, default=None, null=True)
    PartyDebtStatus = models.CharField(max_length=255, blank=True, default=None, null=True)
    PartyDebtStatusDate = models.CharField(max_length=255, blank=True, default=None, null=True)
    PartyInformation = models.CharField(max_length=255, blank=True, default=None, null=True)
    Role = models.CharField(max_length=255, blank=True, default=None, null=True)
    AlternateNames = models.CharField(max_length=255, blank=True, default=None, null=True)
    SelfRepresented = models.CharField(max_length=255, blank=True, default=None, null=True)
    BirthDate = models.CharField(max_length=255, blank=True, default=None, null=True)
    Address1 = models.CharField(max_length=255, blank=True, default=None, null=True)
    Address2 = models.CharField(max_length=255, blank=True, default=None, null=True)
    Phone = models.CharField(max_length=255, blank=True, default=None, null=True)
    Attorney = models.CharField(max_length=255, blank=True, default=None, null=True)
    Name = models.CharField(max_length=255, blank=True, default=None, null=True)
    GuardianInformation = models.CharField(max_length=255, blank=True, default=None, null=True)
    GuardianAddress1 = models.CharField(max_length=255, blank=True, default=None, null=True)
    GuardianAddress2 = models.CharField(max_length=255, blank=True, default=None, null=True)
    AffiliationCode = models.CharField(max_length=255, blank=True, default=None, null=True)
    AppointmentDate = models.CharField(max_length=255, blank=True, default=None, null=True)
    ReqBondAmount = models.CharField(max_length=255, blank=True, default=None, null=True)
    BondReceivedIndicator = models.CharField(max_length=255, blank=True, default=None, null=True)


class MissingJudgmentDocumentSummary(models.Model):
    """
    A group of classes that represents missing judgments pulled from the SCNJ database.
    These judgments weren't in the original data feed received by the state,
    but by looking for missing numbers in each year's sequence they were identified
    """
    JudgmentNum = models.CharField(max_length=255)
    JudgmentSummary = models.CharField(max_length=255)
    DebtId = models.CharField(max_length=255)
    DocumentType = models.CharField(max_length=255, blank=True, default=None, null=True)
    DocumentFileDate = models.CharField(max_length=255, blank=True, default=None, null=True)
    DocumentStatus = models.CharField(max_length=255, blank=True, default=None, null=True)
    PartyNameRole1 = models.CharField(max_length=255, blank=True, default=None, null=True)
    PartyNameRole2 = models.CharField(max_length=255, blank=True, default=None, null=True)
    PartyNameRole3 = models.CharField(max_length=255, blank=True, default=None, null=True)
    PartyNameRole4 = models.CharField(max_length=255, blank=True, default=None, null=True)
