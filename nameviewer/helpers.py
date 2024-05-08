

from xml.etree.ElementTree import tostring

from nameviewer.filters import ForenameFilter, SurnameFilter
from nameviewer.windward import ReportTypes, ReportFactory
from orders.models import Forename, Surname

from django.conf import settings


import os


### BEGIN NAME SEARCH STUFF


def get_forename_results(request, name_to_search):
    """
    Generate a list of aliases from the name database for a given forename
    :param request: the http request associated with the view accessed by the user
    :param name_to_search: first name to generate aliases for
    :return: a name ForenameFilter object
    """
    name_list = Forename.objects.filter(name=name_to_search)
    name_filter = ForenameFilter(request.GET, queryset=name_list)
    return name_filter


def get_surname_results(request, name_to_search):
    """
    Generate a list of aliases from the name database for a given surname
    :param request: the http request associated with the view accessed by the user
    :param name_to_search: last name to generate aliases for
    :return: a name SurnameFilter object
    """
    # name_list = Surname.objects.filter(name=name_to_search, deleted='N')
    name_list = Surname.objects.filter(name=name_to_search)
    name_filter = SurnameFilter(request.GET, queryset=name_list)


def make_name_combinations(fn_list, sn_list):
    """
    Generate a list of all possible combinations of fn_list and sn_list
    :param fn_list: a list of forenames
    :param sn_list: a list of surnames
    :return:
    """
    name_combinations = []
    print(fn_list)
    # print
    for fn in fn_list:
        for sn in sn_list:
            # name_combinations.append({'forename':fn, 'surname':sn})
            name_combinations.append([fn, sn])
    return name_combinations

def generate_forenames(name_to_search, name_score):
    """
    Return a list of names equal to or greater than name_score
    :param name_to_search: the forename to search on
    :param name_score: a score cutoff to use when looking up names
    :return: a list of first names greater than or equal to the name_score threshold
    """
    name_list = Forename.objects.using(settings.NAMESEARCH_DB).filter(name=name_to_search).filter(score__gte=name_score)\
        .filter(deleted='N')
    return name_list

def generate_surnames(name_to_search, name_score):
    """
    Return a list of names equal to or greater than name_score
    :param name_to_search: the surname to search on
    :param name_score: a score cutoff to use when looking up names
    :return: a list of last names greater than or equal to the name_score threshold
    """
    name_list = Surname.objects.using(settings.NAMESEARCH_DB).filter(name=name_to_search).filter(score__gte=name_score).\
        filter(deleted='')
    return name_list

def get_name_match_score(score_type=None, search_name=None):
    """
    Convenience function for getting the score threshold for first or last names
    :param score_type: the type of score to return (first name or last name)
    :param search_name: optional first name to use for generating score. the returned score is adjusted for common names
    :return: a corresponding score threshold
    """
    from django.conf import settings
    if score_type == 'FIRST_NAME':
        score = settings.FIRST_NAME_MATCH_SCORE
        return score
    else:
        score = settings.NAME_MATCH_SCORE_DEFAULT
        # dolores long name override
        if search_name and len(search_name) >= 8 and not _name_is_common(search_name):
            score = 94
        return score

def _unpack_and_append(name_list):
    """
    Unpack the first index of a list of lists into a flat list
    :param name_list: a list containing sub-lists
    :return: a flatten list of elements from the first index of the original list
    """
    new_list = [x for x in name_list[0]]
    return new_list

def _name_is_common(search_name):  # type: (str) -> bool
    """
    Determines if a name is considered to be a common name
    :param search_name: the name to examine
    :return: True or False depending on whether the name is considered to be common or not
    """
    from django.core.cache import cache
    from nameviewer.utils import NameAliasUtils
    COMMON_NAMES_KEY = 'common_names'
    common_names_list = cache.get(COMMON_NAMES_KEY)
    if not common_names_list:
        common_names_list = []
        common_names_list.extend(_unpack_and_append(NameAliasUtils.load_common_names('surname', False)))
        common_names_list.extend(_unpack_and_append(NameAliasUtils.load_common_names('male', False)))
        common_names_list.extend(_unpack_and_append(NameAliasUtils.load_common_names('female', False)))
        cache.set(COMMON_NAMES_KEY, common_names_list, None)
    return search_name.upper() in common_names_list

def _name_is_latin(search_name):  # type: (str) -> bool
    """
    Determines whether a name is latin/hispanic
    :param search_name: the name to search
    :return: True or False depending on whether the name is considered to be hispanic or not
    """
    from django.core.cache import cache
    from nameviewer.utils import NameAliasUtils
    HISPANIC_NAMES_KEY = 'hispanic_names'
    cache.delete(HISPANIC_NAMES_KEY)
    hispanic_names_list = cache.get(HISPANIC_NAMES_KEY)
    if not hispanic_names_list:
        hispanic_names_list = []
        hispanic_names_list.extend(_unpack_and_append(NameAliasUtils.load_common_names('surname-hispanic', False)))
        cache.set(HISPANIC_NAMES_KEY, hispanic_names_list, None)
    return search_name.upper() in hispanic_names_list

def asian_name_check(first_name):
    """
    Check if an asian name like youngjung can be broken up into two names
    Return the original name if not, the split name if so
    :param first_name: user supplied first name
    :return: the original name if it can't be split, the split name if so
    """
    import re
    from nameviewer.utils import NameAliasUtils

    surnames_list = []
    surnames_list.extend(_unpack_and_append(NameAliasUtils.load_common_names('surname-asian', False)))
    name_length = len(first_name)
    revised_asian_name = first_name
    for i in range(name_length, 2, -1):
        name_substr = first_name[:i]
        if name_substr in surnames_list:
            revised_asian_name = "{} {}".format(name_substr, first_name[i:])
            break
    return re.split('\s+', revised_asian_name)

def clean_hyphenated_names(searchname, name_idx = 0):
    """
    Split a potentially hyphenated name into parts
    :param searchname: name to split
    :param name_idx: index of split to return. default is to return only the first name before the hyphen
    :return: str of the split hyphenated name
    """
    return searchname.split('-')[name_idx]

def first_name_variations_from_db(first_name):
    """
    Return a list of first name variations from the name alias db. Also prepends the original name searched on
    :param first_name: the name to use for generating name variations
    :return: a list of name variations including the name supplied
    """
    # from nameviewer.helpers import generate_forenames
    name_match_score = get_name_match_score(score_type='FIRST_NAME')
    # first_name = asian_name_check(first_name)
    name_list = generate_forenames(first_name, name_match_score)
    print_name_list = [first_name.lower()]
    for forename in name_list:
        print_name_list.append(forename.name_match)
    print('Matched first name names list: {}'.format(print_name_list))
    return print_name_list

def last_name_variations_from_db(last_name):
    """
    Return a list of last name variations from the name alias db. Also prepends the original name searched on
    Special processing for hyphenated names and names with apostrophes
    :param first_name: the name to use for generating name variations
    :return: a list of name variations including the name supplied
    """
    special_chars = "'-"
    min_score = 80
    name_match_score = get_name_match_score(search_name=last_name)
    if True in [x in last_name for x in special_chars]:
        if "'" in last_name:
            name_match_score = min_score  # minimum value
            last_name = last_name.replace("'",'').replace('-','')
        else:
            name_match_score = min_score  # minimum value - may need tuning for hyphenated names
            # last_name = last_name.split('-')[0]
            last_name = clean_hyphenated_names(last_name)
    name_list = generate_surnames(last_name, name_match_score)
    print_name_list = [last_name.lower()]
    for surname in name_list:
        print_name_list.append(surname.name_match)
    print('Matched Last name names list: {}'.format(print_name_list))
    return print_name_list

def make_latin_last_name_variations(searchname_last_name, last_name_list):
    """
    Add some extra name variations including 'de' for a list of latin/hispanic last names
    :param searchname_last_name: the last name to generate variations for
    :param last_name_list: a list of names to generate extra variations for. only generates variations for the top 5 entries
    :return:
    """
    if _name_is_latin(searchname_last_name):
        new_list = ["de "+x for x in last_name_list[:5]]
    else:
        new_list = []
    return new_list



### END NAME SEARCH STUFF

### FILE MANAGEMENT STUFF ###


class StateReportManager:

    @staticmethod
    def remove_prior_case_updates(cases):
        from collections import Counter
        """
        Remove old cases from cases list based on matching Case Numbers
        @TODO: this is incomplete - the cases I was going to use for testing actually
        don't have the same case number.
        :param cases: list of statereport.models.Case
        :return: list of statereport.models.Case without older cases included
        """
        # print('---------------> This is the format of the cases object: {}'.format(cases))
        dupe_list = []
        for case in cases:
            case_number = case.nonacms_docket_number  # type: str
            case_number = case_number.strip()
            if not case_number:
                case_number = case.acms_docket_number  # type: str
            if case_number:
                dupe_list.append(case_number)
        dupe_case_numbers = Counter(dupe_list)
        print('Dupe case numbers collection contains: {}'.format(dupe_case_numbers))
        return cases


class NameMergerHelper:

    @staticmethod
    def name_parser_orchestrator(order_id):
        """
        Parse and aggregrate matched names from the three reports
        :param order_id the id of the order to process
        :return: list of unique search names filtered based on available name variations of search name
        """
        from orders.models import GeneratedReport
        from orders.models import NameReportHistory
        generated_report = GeneratedReport.objects.get(order_id=order_id)  # type orders.models.GeneratedReport

        # SCNJ
        # case_xml_file_list = generated_report.state_filename.split(',')[0]
        # case_xml_filename = generated_report.state_filename[:-3] + 'xml'  # @TODO: this should ref case_xml_file_list
        name_report_hist_obj =  NameReportHistory.objects.filter(order_id=order_id).\
            filter(report_type=ReportTypes.STATE).order_by('-order_id').first()
        case_xml_filename = name_report_hist_obj.xml_filename

        scnj_parsed_xml_tree, party_names = NameMergerHelper.parse_names_from_xml(case_xml_filename, ReportTypes.STATE)
        unique_searchname_list = NameMergerHelper._filter_xml_names_by_name_dict_matches(scnj_parsed_xml_tree, party_names)

        # BK
        # some matches like gerald rogers can have a multiline debtor. need to handle these instances
        # bk_report_hist_obj =  NameReportHistory.objects.filter(order_id=order_id).\
        #     filter(report_type=ReportTypes.BANKRUPTCY).order_by('-order_id').first()
        # bk_xml_filename = name_report_hist_obj.xml_filename
        #
        # bk_parsed_xml_tree, party_names = NameMergerHelper.parse_names_from_xml(bk_xml_filename, ReportTypes.BANKRUPTCY)
        # bk_searchname_list = NameMergerHelper._filter_xml_names_by_name_dict_matches(bk_parsed_xml_tree, party_names)
        # unique_searchname_list = unique_searchname_list + bk_searchname_list

        # USDC
        # usdc_xml_filename = generated_report.usdc_filename.split(',')[0]
        # usdc_xml_filename = usdc_xml_filename[:-3] + 'xml'
        # usdc_parsed_xml_tree, party_names = NameMergerHelper.parse_names_from_xml(usdc_xml_filename, ReportTypes.USDC)
        # usdc_searchname_list = NameMergerHelper._filter_xml_names_by_name_dict_matches(usdc_parsed_xml_tree, party_names)
        # unique_searchname_list = unique_searchname_list + usdc_searchname_list

        return list(set(unique_searchname_list))

    @staticmethod
    def parse_names_from_xml(xml_filename, report_type):
        """
        Parses names from XML files of report_type
        :param report_type: a valid report type from the ReportTypes class
        :param xml_filename:
        :return: XMLTree, list of matched and unfiltered party names
        """
        import xml.etree.ElementTree as ET
        from django.conf import settings

        name_list = []
        xml_fullpath = os.path.join(settings.MEDIA_ROOT, xml_filename)
        tree = ET.parse(xml_fullpath)

        if report_type == ReportTypes.STATE:
            xml_node_name = ".//PARTY_NAME"
        elif report_type == ReportTypes.BANKRUPTCY:
            xml_node_name = ".//DEBTOR"
        else:
            return tree, name_list

        for party_element in tree.findall(xml_node_name):
            party_match = party_element.text
            print(party_match)
            name_list.append(party_match.upper())
        return tree, name_list

    @staticmethod
    def _filter_xml_names_by_name_dict_matches(xml_tree, from_xml_name_list):
        """
        Takes a list of names gathered from XML file and filteres results down to matched names
        :param xml_tree: xml.etree.ElementTree
        :param from_xml_name_list List of names parsed from the xml file
        :return: list of unique search names filtered based on available name variations of search name
        """
        from statereport.models import StateReportQueryManager

        search_name_node_list = xml_tree.findall(".//SEARCHNAME")  # need to capture all names
        search_name_list = []
        unique_searchname_list = []
        for sn in search_name_node_list:
            search_name_list.append(sn.text)
        search_name_list = list(set(search_name_list))  # ...and then make the list unique
        for search_name in search_name_list:
            searchname_first_name, searchname_last_name = \
                NameMergerHelper._parse_first_last_name_from_searchname(search_name)
            StateReportQueryManager.make_first_name_variations(searchname_first_name)
            first_name_variations = first_name_variations_from_db(searchname_first_name)
            last_name_variations = last_name_variations_from_db(searchname_last_name)
            unique_searchname_list = NameMergerHelper._filter_name_list(first_name_variations,
                                                                       last_name_variations,
                                                                       from_xml_name_list)
        return unique_searchname_list

    @staticmethod
    def _filter_name_list(first_name_vars, last_name_vars, from_xml_name_list):
        """
        Filter a list of names based on the first and last name variations provided
        :param first_name_vars: list of first names to look for in the from_xml_name_list name list
        :param last_name_vars: list of last names to look for in the from_xml_name_list name list
        :param from_xml_name_list list of names parsed from the xml file
        :return: list of filtered names containing one of first and last name for each match
        """
        filtered_list = []
        final_filtered_list = []
        for fnv in first_name_vars:
            for search_name in from_xml_name_list:
                if fnv.upper() in search_name:
                    filtered_list.append(search_name)
        for lnv in last_name_vars:
            for search_name in filtered_list:
                if lnv.upper() in search_name:
                    final_filtered_list.append(search_name)
        final_filtered_list = list(set(final_filtered_list))
        return final_filtered_list

    @staticmethod
    def _parse_first_last_name_from_searchname(search_name):
        """
        Return the first and last name in a string of names by splitting the string on space characters
        :param search_name:
        :return:
        """
        names = search_name.split(None)  # can do this or call with () to split on whitespace chars
        f_name = names[0]
        l_name = names[-1]
        return f_name, l_name


def get_base_report_name(report_filename):
    """
    Return a base filename from a supplied filename that can be used to locate a pdf from an xml file or vice-a-versa
    :param report_filename: the name of the file to parse
    :return:
    """
    report_filename = report_filename.split(',')[-1]  # multiple report names can exist, separated by commas
    return report_filename[:-3]


class XMLNameFilterHelper:

    @staticmethod
    def xml_name_filter_orchestrator(order_id, selected_names):
        """
        Generates a new report for an order based on a list of full names which will be used for downselecting results
        :param order_id: the order id to work with
        :param selected_names: a list of names to use for determining which cases to retain
        :return:
        """
        from orders.models import GeneratedReport, Order
        from orders.utils import OrderUtils

        generated_report = GeneratedReport.objects.get(order_id=order_id)  # type orders.models.GeneratedReport

        # state report
        case_xml_filename = get_base_report_name(generated_report.state_filename) + 'xml'
        parsed_xml_tree, party_names = NameMergerHelper.parse_names_from_xml(case_xml_filename, ReportTypes.STATE)
        reduced_scnj_xml_tree = XMLNameFilterHelper.filter_scnj_xml_from_name_selection(parsed_xml_tree, selected_names)
        reduced_scnj_xml = tostring(reduced_scnj_xml_tree.getroot())  # covert to a printable string, see PrintFactory.dump_xml_to_file()

        rf = ReportFactory()
        # state report
        searchname = XMLNameFilterHelper.parse_searchname_from_xml(case_xml_filename)
        report_name = rf.gen_windward_state_report(None, None, searchname, reduced_scnj_xml)
        order = Order.objects.get(pk=order_id)
        report_type = ReportTypes.STATE
        cases_len = len(parsed_xml_tree.getroot()) - 1

        # Can't store the original generated report and the new report, need to clear out old one
        # @TODO: but store report in history table beforehand
        OrderUtils.clear_order_generated_reports(order_id, ReportTypes.STATE)
        rf.add_generated_report_to_order(order, report_name, report_type, cases_len)

        # update report with new xml name
        # @TODO: BK report

        # @TODO: USDC report

    @staticmethod
    def parse_searchname_from_xml(xml_filename):
        """
        Return the search name entered by the user for the order that is stored in the xml file
        :param xml_filename:
        :return:
        """
        import xml.etree.ElementTree as ET

        xml_fullpath = os.path.join(settings.MEDIA_ROOT, xml_filename)
        tree = ET.parse(xml_fullpath)
        xml_node_name = ".//SEARCHNAME"
        parsed_name = None
        for searchname in tree.findall(xml_node_name):
            parsed_name = searchname.text
        return parsed_name

    @staticmethod
    def filter_scnj_xml_from_name_selection(parsed_xml_tree, selected_names):
        """
        Remove unwanted names from an xml dom tree
        :param parsed_xml_tree: xml.etree.ElementTree containing all matched names from system
        :param selected_names: list of user selected names matching SEARCHNAME nodes in element tree
        :return: a parsed xml tree
        :rtype xml.etree.ElementTree:
        """
        client_ref_num_tag = 'CLIENT_REF_NUM'
        case_tag = 'case'
        client_ref_tag_retained = False
        nodes_to_remove = []

        root_node = parsed_xml_tree.getroot()  # type: xml.etree.ElementTree
        for node in root_node:
            name_match_found = False
            if node.tag == client_ref_num_tag:
                if client_ref_tag_retained:
                    root_node.remove(node)
                if not client_ref_tag_retained:
                    client_ref_num_tag = True
                continue
            if node.tag == case_tag:
                for party_element in node.findall(".//PARTY_NAME"):
                    party_match = party_element.text
                    if party_match in selected_names:
                        name_match_found = True
            if not name_match_found:
                # root_node.remove(node)
                nodes_to_remove.append(node)

        nodes_to_remove = reversed(nodes_to_remove)
        for node in nodes_to_remove:
            root_node.remove(node)

        root_node.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        return parsed_xml_tree
