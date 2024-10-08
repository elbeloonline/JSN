from background_task import background
from django.contrib.auth.models import User
import logging
from nameviewer.helpers import first_name_variations_from_db, last_name_variations_from_db

# start the tasks server with the command `python manage.py process_tasks`

def add_xlsx_task(order_id, report_type):
    """
    Add a task to generate an excel file for the search type
    :param order_id: the order id to process
    :param report_type: the type of report to generate the xlsx for
    :return:
    """
    from nameviewer.windward import ReportTypes

    if report_type == ReportTypes.STATE:
        process_report(order_id, ReportTypes.XLSX)
    elif report_type == ReportTypes.BANKRUPTCY:
        process_report(order_id, ReportTypes.BKCY_XLSX)
    elif report_type == ReportTypes.USDC:
        process_report(order_id, ReportTypes.USDC_XLSX)


def add_high_value_search(order_id, is_high_value_search):
    """
    SCNJ tasks can have a high value search requested with the primary order. Check if this was requested with the main order
    :param order_id: the order id to process
    :param is_high_value_search: indicates whether a high value search was requested
    :return:
    """
    from . import tasks
    from nameviewer.windward import ReportTypes

    if is_high_value_search:
        tasks.process_report(order_id, ReportTypes.STATE_HIGH_VALUE)


@background(schedule=1)
def process_report(order_id, report_type):
    """
    This is the main loop for generating a report based on a user request.
    Requests to generate reports are submitted to a queue where they will be processed.
    If the FULL report is generated, all sub reports are automatically added, otherwise the type of report requested is generated
    :param order_id: the order id to use for getting the names submitted by the user
    :param report_type: the type of report to generate
    :return: None
    """
    import logging
    from .models import Order
    from django.conf import settings
    from nameviewer.utils import PacerSearchUtils, SCNJSearchUtils, DOBScraperResults
    from nameviewer.windward import ReportFactory
    from nameviewer.windward import ReportTypes
    from orders.models import SearchName
    from orders.utils import OrderUtils
    from nameviewer.pdfutils import PdfMerger
    from pacerscraper.utils import ReportHelper

    logger = logging.getLogger(__name__)
    logger.info('Got a notification to generate a report for order {} (for report type {})'.format(order_id, report_type))

    # generate report
    # first_name, last_name, company_name = PacerSearchUtils.name_from_order_id(order_id)

    OrderUtils.clear_order_generated_reports(order_id, report_type)
    searchname_set = PacerSearchUtils.name_from_order_id(order_id)
    if report_type == ReportTypes.FULL:
        from . import tasks
        from orders.models import GeneratedReport
        from nameviewer.csvwriter import JSNCSVWriter

        # delete the old report to fix possible data consistency issues later
        gr = GeneratedReport.objects.filter(order_id=order_id)
        if gr:
            gr.delete()
            JSNCSVWriter.delete_csv(order_id) # also delete any associated csv files
        tasks.process_report(order_id, ReportTypes.STATE)
        tasks.process_report(order_id, ReportTypes.STATE_HIGH_VALUE)  # added explicitly here for cover page generation later
        tasks.process_report(order_id, ReportTypes.BANKRUPTCY)
        tasks.process_report(order_id, ReportTypes.USDC)
        tasks.process_report(order_id, ReportTypes.DOCKETLIST)
        tasks.process_report(order_id, ReportTypes.PATRIOT)
        tasks.process_report(order_id, ReportTypes.COVER)
        # tasks.process_report(order_id, ReportTypes.FULL)
    else:
        high_value_name_in_search = False
        for search_name_set_element in searchname_set.all():
            print(search_name_set_element)
            first_name = search_name_set_element.first_name
            middle_name = search_name_set_element.middle_name
            last_name = search_name_set_element.last_name
            company_name = search_name_set_element.company_name
            searchname = SearchName()
            searchname.first_name = first_name
            searchname.middle_name = middle_name
            searchname.last_name = last_name
            searchname.company_name = company_name
            searchname.search_from = search_name_set_element.search_from
            searchname.search_to = search_name_set_element.search_to
            searchname.order = search_name_set_element.order
            searchname.order_id = search_name_set_element.order_id
            is_highvalue_search = search_name_set_element.high_value_search
            if is_highvalue_search:
                high_value_name_in_search = True
            if not report_type == ReportTypes.COVER and not report_type == ReportTypes.DOCKETLIST:
                name_search_results, matched_cases_dict = PacerSearchUtils.run_name_search(searchname, report_type)  # bk_case_dict contains a dict of db_ref and case_model
                logger.info('Generated name search results')
                logger.info(name_search_results)
            debug_message = ''
            # @TODO: handle multiple search names
            order = Order.objects.get(pk=order_id)

            rf = ReportFactory()
            if report_type == ReportTypes.STATE:
                logger.info('Running search to generate state report for order {}'.format(order_id))
                cases = name_search_results['state_names']
                judgment_dobs =  _run_scnj_dob_search(logger, order_id, searchname, cases)
                logger.info('Generating state report for order {}'.format(order_id))
                report_name = rf.gen_windward_state_report(cases, order, searchname, judgment_dobs=judgment_dobs)
                if len(cases) > 0:
                    logger.info('Name of report stored to filesystem: {}'.format(report_name))
                    rf.add_generated_report_to_order(order, report_name, report_type, len(cases))
                    add_xlsx_task(order_id, ReportTypes.STATE)
                    # add_high_value_search(order_id, is_highvalue_search)
            elif report_type == ReportTypes.STATE_HIGH_VALUE:
                if is_highvalue_search:
                    logger.info('Processing High Value Search Report')
                    # # BEGIN build high value judgments
                    # # party_match_high_value = StateReportNameSearchUtils.query_high_value_judgments(searchname_first_name, searchname_last_name)
                    # # END build high value judgments
                    # parties = name_search_results['state_names_hv']
                    # cases = [party.case for party in parties]
                    cases = name_search_results['state_names_hv']
                    if len(cases) > 0:
                        judgment_dobs =  _run_scnj_dob_search(logger, order_id, searchname, cases)
                        logger.info('Generating high value search report for order {}'.format(order_id))
                        report_name = rf.gen_windward_state_report(cases, order, searchname, judgment_dobs=judgment_dobs)
                        logger.info('Name of report stored to filesystem: {}'.format(report_name))
                        # @TODO: re-enable the code below to attach the report to the order. filename is already unique
                        rf.add_generated_report_to_order(order, report_name, report_type, len(cases))
                        # write CSV report
                        from nameviewer.csvwriter import JSNCSVWriter
                        client_number = '{}-{}'.format(order.title_number, order_id)
                        JSNCSVWriter.write_scnj_csv(order_id, cases, searchname, '{}-hv.csv'.format(client_number),
                                                    judgment_dobs=judgment_dobs, is_high_value=True)

            elif report_type == ReportTypes.BANKRUPTCY:
                logger.info('Running search to generate bankruptcy report for order {}'.format(order_id))
                cases = name_search_results['bankruptcy_names']
                if settings.BKCY_REPORT_EXACT_MATCH_ONLY:
                    cases = ReportHelper.add_bkcy_exact_match_only(cases, searchname)
                if len(cases) > 0:
                    logger.info('Generating bankruptcy report for order {}'.format(order_id))
                    report_name, p_top = rf.gen_windward_bankruptcy_report(cases, matched_cases_dict, order, searchname)
                    logger.info('Name of report stored to filesystem: {}'.format(report_name))
                    rf.add_generated_report_to_order(order, report_name, report_type, len(matched_cases_dict))
                    # write CSV report
                    # from nameviewer.csvwriter import JSNCSVWriter
                    # client_number = order.title_number
                    try:
                        # JSNCSVWriter.write_bk_csv(rf.print_factory.top, searchname, order)
                        # JSNCSVWriter.write_bk_csv(p_top, searchname, order, matched_cases_dict)
                        add_xlsx_task(order_id, ReportTypes.BANKRUPTCY)
                    except Exception:
                        print("Couldn't append BK data to CSV file. Continuing...")

            elif report_type == ReportTypes.USDC:
                logger.info('Running search to generate usdc report for order {}'.format(order_id))
                cases = name_search_results['usdc_names']
                if len(cases) > 0:
                    logger.info('Generating usdc report for order {}'.format(order_id))
                    report_name, p_top = rf.gen_windward_usdc_report(cases, matched_cases_dict, order, searchname)
                    logger.info('Name of report stored to filesystem: {}'.format(report_name))
                    rf.add_generated_report_to_order(order, report_name, report_type, len(matched_cases_dict))
                    # write CSV report
                    from nameviewer.csvwriter import JSNCSVWriter
                    # client_number = order.title_number
                    try:
                        JSNCSVWriter.write_usdc_csv(p_top, searchname, order, matched_cases_dict)
                    except Exception:
                        print("Couldn't append USDC data to CSV file. Continuing...")
            elif report_type == ReportTypes.DOCKETLIST:
                logger.info('Generating docket list page for order {}'.format(order_id))
                report_name = rf.gen_docket_list_report(order_id)
                rf.add_generated_report_to_order(order, report_name, report_type, 0)
            elif report_type == ReportTypes.PATRIOT:
                from patriot.helpers import PatriotResultsDict as prd
                logger.info('Running search to generate patriot report for order {}'.format(order_id))
                match_names = name_search_results['patriot_names']
                patriot_match_dict = match_names[str(searchname)]
                num_patriot_matches = len(patriot_match_dict[prd.PRIM_MATCHES]) + len(patriot_match_dict[prd.ALT_MATCHES])
                report_name = rf.gen_windward_patriot_report(match_names, order, searchname)
                logger.info('Name of report stored to filesystem: {}'.format(report_name))
                rf.add_generated_report_to_order(order, report_name, report_type, num_patriot_matches)
            elif report_type == ReportTypes.XLSX:
                # write CSV report
                from nameviewer.csvwriter import JSNCSVWriter
                cases = name_search_results['state_names']
                if len(cases) > 0:
                    judgment_dobs =  _run_scnj_dob_search(logger, order_id, searchname, cases)
                    client_number = '{}-{}'.format(order.title_number, order_id)
                    JSNCSVWriter.write_scnj_csv(order_id, cases, searchname, '{}.csv'.format(client_number),
                                                judgment_dobs=judgment_dobs)
            elif report_type == ReportTypes.BKCY_XLSX:
                # write BKCY CSV report
                from nameviewer.csvwriter import JSNCSVWriter
                # cases = name_search_results['state_names']
                # if len(cases) > 0:
                #     judgment_dobs =  _run_scnj_dob_search(logger, order_id, searchname, cases)
                #     client_number = '{}-{}'.format(order.title_number, order_id)
                #     JSNCSVWriter.write_scnj_csv(order_id, cases, searchname, '{}.csv'.format(client_number),
                #                                 judgment_dobs=judgment_dobs)
                cases = name_search_results['bankruptcy_names']
                if settings.BKCY_REPORT_EXACT_MATCH_ONLY:
                    cases = ReportHelper.add_bkcy_exact_match_only(cases, searchname)
                if len(cases) > 0:
                    logger.info('Generating bankruptcy report for order {}'.format(order_id))
                    report_name, p_top = rf.gen_windward_bankruptcy_report(cases, matched_cases_dict, order, searchname)
                    logger.info('Name of report stored to filesystem: {}'.format(report_name))
                    rf.add_generated_report_to_order(order, report_name, report_type, len(matched_cases_dict))
                    # write CSV report
                    JSNCSVWriter.write_bk_csv(p_top, searchname, order, matched_cases_dict)

        if report_type == ReportTypes.COVER:
            report_name = rf.gen_windward_coverpage_report2(order, high_value_name_in_search)
            rf.add_generated_report_to_order(order, report_name, report_type, 0)
            # return _pdf_view(None, report_name)
            doc_merger = PdfMerger()
            logger.debug('Calling PdfMerger merge_reports method')
            merged_report_name = doc_merger.merge_reports(order_id)
            rf.add_generated_report_to_order(order, merged_report_name, ReportTypes.FULL, 0)

def _run_scnj_dob_search(logger, order_id, searchname, cases):
    """
    Run a DOB search which is part of the SCNJ search. This fills in the DOBs where available.
    :param logger: logger to use for logging information about the search process
    :param order_id: the order id for this search
    :param searchname: the searchname object for this search
    :param cases: the cases to lookup as part of the DOB search
    :return: a list of judgments with DOBs attached, can be mapped back to the original cases
    """
    from django.conf import settings
    from nameviewer.utils import PacerSearchUtils, SCNJSearchUtils, DOBScraperResults

    logger.info('Augmenting state report data with DOBs for order {}'.format(order_id))
    judgment_dobs = DOBScraperResults.merge_scraped_judgment_dobs(searchname)
    # disabled 1-14-2020 until docker instance is available
    if settings.RUN_DOB_SEARCH:
        scnj_search = SCNJSearchUtils()
        no_dob_cases = DOBScraperResults.exclude_scraped_judgment_dobs(cases, judgment_dobs)
        judgment_dobs = scnj_search.run_dob_search(no_dob_cases, order_id, judgment_dobs)
    # else:
    #     judgment_dobs = {}
    return judgment_dobs
