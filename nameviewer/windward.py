import os
import os.path
from xml.etree.ElementTree import Comment

from django.conf import settings
from enum import Enum

from nameviewer.csvwriter import JSNCSVWriter
from nameviewer.printfactory import PrintFactory

from nameviewer.restfulengine import Report, OutputFormat, XmlDataSource


class ReportTypes:
    FULL = 'full'
    STATE = 'state_report'
    STATE_HIGH_VALUE = 'hv_state_report'
    STATEDOB = 'state_dob'
    BANKRUPTCY = 'bankruptcy'
    USDC = 'usdc'
    COVER = 'cover_page'
    DOCKETLIST = 'docket_list'
    PATRIOT = 'patriot'
    GENERATEFINALREPORT = 'generate_final_report'
    XLSX = 'xlsx_report'
    BKCY_XLSX = 'bkcy_xlsx_report'
    USDC_XLSX = 'usdc_xlsx_report'


class JSNReportFileManager:

    @staticmethod
    def pdf_archive(report_name, case_xml_filename):
        """
        Copies the generated pdf
        :param report_name: pdf file to copy
        :param case_xml_filename: xml file pdf was generated from. will be used for new pdf name
        :return:
        """
        import os.path
        import shutil

        # @TODO: make this thread safe - original PDF can be overwritten b/c filename isn't unique
        if os.path.exists(report_name):
            # pdfs_loc = os.path.join('.', 'jsnetwork_project', 'media', 'generatedpdfs')
            pdfs_loc = os.path.join(settings.MEDIA_ROOT, 'generatedpdfs')
            if not os.path.exists(pdfs_loc):
                os.makedirs(pdfs_loc)
            # new_report_name = os.path.join(pdfs_loc, case_xml_filename[:-3] + 'pdf')
            new_report_name = case_xml_filename[:-3] + 'pdf'
            new_report_location = os.path.join(pdfs_loc, new_report_name)
            print(('Copying file from {} to {}'.format(report_name, new_report_location)))
            shutil.copy(report_name, new_report_location)
            print(('Using name {} to store to generated reports table'.format(new_report_name)))
        return new_report_name


class WindwardRestEngine:
    _report = None

    def __init__(self, base_uri, template_filename, xml_filenames, pdf_filename, data_source_names):
        """
        Templates are stored in C:\Windows\System32\inetsrv\jsnetwork_project on server - enforced by IIS
        :param base_uri:
        :param template_filename:
        :param xml_filenames:
        :param pdf_filename:
        :param data_source_names:
        """
        self._report = Report(base_uri, OutputFormat.pdf, template_filename, pdf_filename)
        self._xml_filenames = xml_filenames
        self._data_source_names = data_source_names

    def make_report(self):
        """
        Send a request to the windward report server to create a report
        """
        import os.path

        data_sources = []
        print(("Using the following xml filenames: {}".format(self._xml_filenames)))
        print(("Using the following data sources: {}".format(self._data_source_names)))

        for xml_filename, ds_name in zip(self._xml_filenames, self._data_source_names):
            xml_filename_data = None
            if os.path.exists(xml_filename):
                with open(xml_filename) as f:
                    try:
                        xml_filename_data = f.read()
                    except IOError:
                        print('Could not open XML data file')
            xml_data_bytes = bytearray(xml_filename_data, 'utf-8')
            print("Read XML file successfully")

            xds = XmlDataSource(name=ds_name, data=xml_data_bytes)
            data_sources.append(xds)
            print(("Attaching data source with name {}".format(ds_name)))

        # finally process the report
        self._report.process(data_sources)


class WindwardReportEngine2:
    def make_report(self):
        """
        Send a request to the windward reporting engine to generate a word report
        :return:
        """
        # @TODO: move this into the settings config file
        base_uri = 'https://jsntest.com/pdftools/make_pdf/'
        template = os.path.join('.', 'jsnetwork_project', 'media', 'Case Report Template.docx')
        xml_filename = os.path.join('.', 'jsnetwork_project', 'media', 'case_report_template.xml')
        pdf_filename = os.path.join('.', 'jsnetwork_project', 'media', 'casereport')

        report = Report(base_uri, OutputFormat.pdf, template, pdf_filename)

        xml_filename_data = None
        if os.path.exists(xml_filename):
            with open(xml_filename) as f:
                try:
                    xml_filename_data = f.read()
                except IOError:
                    print('Could not open XML data file')
        xml_data_bytes = bytearray(xml_filename_data, 'utf-8')
        data_sources = [
            XmlDataSource(
                name="CaseReport",
                data=xml_data_bytes  # string??
            )
        ]

        report.process(data_sources)


class ReportFactory:

    def __init__(self):
        self.print_factory = PrintFactory()

    def gen_windward_state_report(self, cases, order, searchname, case_xml=None, judgment_dobs=None):
        """
        Generate a SCNJ report using the reporting server
        :param cases: Queryset of cases. Can be None if case_xml is provided
        :param order: Order object. Can be None if case_xml is provided
        :param searchname: the name that was submitted for the search
        :param case_xml: a string containing a formatted xml file with case info
        :param judgment_dobs: dictionary of judgment numbers without dashes and matching DOB
        :return:
        """
        import uuid

        # make XML output for report
        # p = PrintFactory()
        p = self.print_factory
        case_xml_filename = uuid.uuid4().hex + '.xml'
        if not case_xml:
            case_xml = p.make_xml(cases, order, searchname, judgment_dobs)
        xml_filepath = p.dump_xml_to_file(case_xml, case_xml_filename)

        # make report
        template_filename = 'Case Report Template.docx'
        pdf_filename = 'case_report.pdf'
        data_source_name = "CaseReport"
        report_name = self._call_report_engine(xml_filepath, [case_xml_filename], [data_source_name],
                                               template_filename, pdf_filename)
        new_report_name = JSNReportFileManager.pdf_archive(report_name, case_xml_filename)
        return new_report_name
        # return report_name

    def gen_windward_bankruptcy_report(self, cases, bk_cases_dict, order, searchname):
        """
        High level function to make a BKCY report from a list of BkNameMatches and PacerBankruptcyIndexCase models
        :param cases: matched cases as list of BkNameMatch
        :param bk_cases_dict: dictionary of PacerBankruptcyIndexCase with related records attached
        :param searchname: the name that was searched
        :return: name of report on file system
        """
        # type: (list(PacerSearchUtils.BkNameMatch), dict(PacerBankruptcyIndexCase)) -> str
        import uuid
        from nameviewer.utils import PacerSearchUtils
        from pacerscraper.models import PacerBankruptcyIndexCase

        # make XML output for report
        # p = PrintFactory()
        p = self.print_factory
        bankruptcy_xml_filename = uuid.uuid4().hex + '.xml'
        bankruptcy_xml = p.make_bankruptcy_xml(cases, bk_cases_dict, order, searchname)
        xml_filepath = p.dump_xml_to_file(bankruptcy_xml, bankruptcy_xml_filename)
        print(xml_filepath)

        # # write csv
        # try:
        #     JSNCSVWriter.write_bk_csv(p.top, searchname, order)
        # except Exception:
        #     print("Couldn't append BK data to CSV file. Continuing...")

        # make report
        template_filename = 'Bankruptcy Template.docx'
        pdf_filename = 'bankruptcy_report.pdf'
        data_source_name = "BankruptcyReport"  # @TODO: make sure this matches in word document!
        report_name = self._call_report_engine(xml_filepath, [bankruptcy_xml_filename], [data_source_name],
                                               template_filename, pdf_filename)
        new_report_name = JSNReportFileManager.pdf_archive(report_name, bankruptcy_xml_filename)
        return new_report_name, p.top

    def gen_windward_usdc_report(self, cases, matched_cases_dict, order, searchname):
        """
        High level function to make the report from a list of USDCNameMatches and PacerJudgmentIndexCase models
        :param cases: matched cases as list of BkNameMatch
        :param bk_cases_dict: dictionary of PacerBankruptcyIndexCase with related records attached
        :param searchname: the name that was searched
        :return: name of report on file system
        """
        # type: (list(PacerSearchUtils.BkNameMatch), dict(PacerBankruptcyIndexCase)) -> str
        import logging
        import uuid
        from nameviewer.utils import PacerSearchUtils
        from pacerscraper.models import PacerBankruptcyIndexCase

        logger = logging.getLogger(__name__)
        # make XML output for report
        # p = PrintFactory()
        p = self.print_factory
        usdc_xml_filename = uuid.uuid4().hex + '.xml'
        # bankruptcy_xml = p.make_bankruptcy_xml(cases, matched_cases_dict, order)
        usdc_xml = p.make_usdc_xml(cases, matched_cases_dict, order, searchname)
        xml_filepath = p.dump_xml_to_file(usdc_xml, usdc_xml_filename)
        logger.info('Generated xml file for usdc report at {}'.format(xml_filepath))
        # print(xml_filepath)

        # write csv
        # JSNCSVWriter.write_usdc_csv(p.top, searchname, order)

        # make report
        template_filename = 'USDC Template.docx'
        pdf_filename = 'usdc_report.pdf'
        data_source_name = "UsdcReport"  # @TODO: make sure this matches in word document!

        report_name = self._call_report_engine(xml_filepath, [usdc_xml_filename], [data_source_name],
                                               template_filename, pdf_filename)
        logger.info('Got report name from report engine: {}'.format(report_name))
        # return report_name
        new_report_name = JSNReportFileManager.pdf_archive(report_name, usdc_xml_filename)
        return new_report_name, p.top


    def _gen_docket_list_report_data(self, order_id, save_filename):
        """
        Generate a docket list in xml format for an order
        :param order_id: the id of the order to use for generating the report
        :param save_filename: the name to use for generating the xml file
        :return:
        """
        import logging
        import xml.etree.ElementTree as ET
        from xml.etree.ElementTree import tostring

        from orders.models import GeneratedReport
        from nameviewer.utils import DocketListTypes

        def update_master_docket_dict(mdict, search_name, docket_list, docket_list_type):
            """

            :param mdict: the master docket dict
            :param search_name: the search name for this operation
            :param docket_list: the list of dockets to use for updating the dictionary
            :param docket_list_type: the type of report this docket list is being associated with
            :return: the updated mdict structure
            :rtype: dict
            """
            print(("Got docket list of type {} containing {}".format(docket_list_type, docket_list)))
            t_dict = mdict.get(search_name, {})
            t_dict[docket_list_type] = docket_list
            print(("Temporary dict for {} now contains {}".format(search_name, t_dict)))
            mdict[search_name] = t_dict
            return mdict

        def build_docket_list_xml(docket_list_dict):
            """
            Generate an xml file from a docket list dict
            :param docket_list_dict: a dictionary containing a docket list. This dict can contain dockets for
            different report types
            :return:
            """
            # xml_filename = uuid.uuid4().hex + '.xml'
            import xml.etree.ElementTree as ET

            top = ET.Element('root', attrib={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
            comment = Comment('Generated for JSN')
            top.append(comment)
            for search_name, nm_docket_dict in docket_list_dict.items():
                search_results_xml = ET.SubElement(top, 'SEARCH_RESULTS')
                search_name_xml = ET.SubElement(search_results_xml, 'SEARCH_NAME')
                search_name_xml.text = search_name
                for search_type, docket_list_result in nm_docket_dict.items():
                    search_type_xml = ET.SubElement(search_results_xml, 'SEARCH_TYPE')
                    search_type_name_xml = ET.SubElement(search_type_xml, 'SEARCH_TYPE_NAME')
                    search_type_name_xml.text = search_type
                    docket_results_xml = ET.SubElement(search_type_xml, 'DOCKET_RESULTS')
                    for d in docket_list_result:
                        ET.SubElement(docket_results_xml, 'DOCKET_NUM').text = d
            print("Docket list XML generated:")  # ET.dump(top)
            print((tostring(top)))
            # xml_filepath = os.path.join(settings.MEDIA_ROOT, 'generatedpdfs', save_filename)
            xml_filepath = os.path.join(settings.MEDIA_ROOT, save_filename)
            with open (xml_filepath, "wb") as f:
                f.write(tostring(top))
            print(("Wrote docket list XML to {}".format(xml_filepath)))
            return xml_filepath

        logger = logging.getLogger(__name__)
        gr = GeneratedReport.objects.get_or_create(order_id=order_id)[0]

        docket_dict = {}
        master_docket_dict = {}

        if gr.state_filename:
            fn_list = gr.state_filename.replace(".pdf",".xml").split(",")
            for generated_file in fn_list:
                print(("Processing file {} for buildout of state sub-docket list".format(generated_file)))
                docket_list = []
                tree = ET.parse(os.path.join(settings.MEDIA_ROOT, generated_file))
                root = tree.getroot()
                if len(root) > 0:
                    print(("Number of child nodes under root node: {}".format(len(root))))
                    search_name = root.find('case').find('SEARCHNAME').text
                    for child_case in root.findall('case'):
                        judgment_number = child_case.find('JUDGMENT_NUMBER').text
                        docket_list.append(judgment_number)
                    master_docket_dict = update_master_docket_dict(master_docket_dict, search_name, docket_list, DocketListTypes.STATE)

        if gr.bankruptcy_filename:
            fn_list = gr.bankruptcy_filename.replace(".pdf",".xml").split(",")
            for generated_file in fn_list:
                print(("Processing file {} for buildout of bankruptcy sub-docket list".format(generated_file)))
                docket_list = []
                tree = ET.parse(os.path.join(settings.MEDIA_ROOT, generated_file))
                root = tree.getroot()
                if len(root) > 1:
                    # print("Number of child nodes under root node: {}".format(len(root)))
                    search_name = root.find('case').find('SEARCHNAME').text
                    for child_case in root.findall('case'):
                        try:
                            case_number = child_case.find('BANKRUPTCY_NUMBER').text
                        except:
                            case_number = "NOT PROVIDED"
                        print("Case number: {}".format(case_number))
                        docket_list.append(case_number)
                    master_docket_dict = update_master_docket_dict(master_docket_dict, search_name, docket_list, DocketListTypes.BANKRUPTCY)
                    # print("After BK build, master docket dict now contains {}".format(master_docket_dict))

        if gr.usdc_filename:
            fn_list = gr.usdc_filename.replace(".pdf",".xml").split(",")
            for generated_file in fn_list:
                print(("Processing file {} for buildout of usdc sub-docket list".format(generated_file)))
                docket_list = []
                tree = ET.parse(os.path.join(settings.MEDIA_ROOT, generated_file))
                root = tree.getroot()
                if len(root) > 1:
                    search_name = root.find('case').find('SEARCHNAME').text
                    for child_case in root.findall('case'):
                        case_number = child_case.find('USDC_CASE_NUMBER').text
                        docket_list.append(case_number)
                    master_docket_dict = update_master_docket_dict(master_docket_dict, search_name, docket_list, DocketListTypes.USDC)

        logger.info("><><><><><><><><><><><><This is the parsed docket dict from the report: \n{}".format(master_docket_dict))
        docket_list_xml = build_docket_list_xml(master_docket_dict)
        gr.docket_list_filename = docket_list_xml
        gr.save()
        return docket_list_xml

    def gen_windward_patriot_report(self, match_records, order, searchname):
        """
        High level function to make the report from a list of Patriot names
        :param match_records: dict containing patriot.helpers.PatriotResultsDict
        :param order: Orders.models.order
        :param searchname: str original name searched on
        :return:
        """
        import logging
        import uuid

        logger = logging.getLogger(__name__)
        # make XML output for report
        p = self.print_factory
        patriot_xml_filename = uuid.uuid4().hex + '.xml'
        patriot_xml = p.make_patriot_xml(match_records, order, searchname)
        xml_filepath = p.dump_xml_to_file(patriot_xml, patriot_xml_filename)
        logger.info('Generated xml file for patriot report at {}'.format(xml_filepath))

        # make report
        template_filename = 'Patriot Template.docx'
        pdf_filename = 'patriot_report.pdf'
        data_source_name = "PatriotReport"  # @TODO: make sure this matches in word document!

        report_name = self._call_report_engine(xml_filepath, [patriot_xml_filename], [data_source_name],
                                               template_filename, pdf_filename)
        logger.info('Got report name from report engine: {}'.format(report_name))
        # return report_name
        new_report_name = JSNReportFileManager.pdf_archive(report_name, patriot_xml_filename)
        return new_report_name


    def gen_docket_list_report(self, order_id):
        """
        Generate a docket list pdf report for an order id. This pdf appears at the beginning of the combined report
        :param order_id: the id of the order to use for this operation
        :return: the name of the report generated
        :rtype: str
        """
        import logging
        import uuid

        # from orders.models import GeneratedReport

        logger = logging.getLogger(__name__)
        pdf_filename = uuid.uuid4().hex + '.pdf'
        xml_filename = uuid.uuid4().hex + '.xml'
        # grs = GeneratedReport.objects.get(order_id=order_id)
        # xml_data_filenames = [a[:-3]+'xml' for a in [grs.state_filename, grs.bankruptcy_filename, grs.usdc_filename]]
        docket_list_data_file = self._gen_docket_list_report_data(order_id, xml_filename)

        template_filename = 'Docket List Template.docx'
        data_source_names = ["DocketReport"]

        xml_filepath = "NoXMLFilePath"
        # logger.info(">>>>>>>>>>>>>>>>>>>> Calling report engine function, using {} for pdf_filename var".format(pdf_filename))
        report_name = self._call_report_engine(xml_filepath, [xml_filename], data_source_names,
                                               template_filename, pdf_filename)
        new_report_name = JSNReportFileManager.pdf_archive(report_name, pdf_filename)
        logger.info("Generated a new docket list! Name is {}".format(pdf_filename))
        return new_report_name
        # return "59aee1b156d3406cb8abbea320c21895.pdf"
        # return None


    # i don't know what the other function is for, so...
    def gen_windward_coverpage_report2(self, order, is_highvalue_search=False):
        """
        Generate a pdf coverpage report
        :param order: the order object to use for generating the report
        :param is_highvalue_search: indicates whether a high value search was performed
        :return: the name of the new report
        """
        import uuid
        # p = PrintFactory()
        p = self.print_factory

        name_search_dict = self.coverpage_names_from_order(order)
        coverpage_xml = p.make_coverpage_xml3(name_search_dict, order, is_highvalue_search)
        coverpage_xml_filename = uuid.uuid4().hex + '.xml'
        xml_filepath = p.dump_xml_to_file(coverpage_xml, coverpage_xml_filename)

        # make report
        template_filename = 'Cover Page Template.docx'
        pdf_filename = coverpage_xml_filename.replace('.xml', '.pdf')
        data_source_name = "CoverPage"
        report_name = self._call_report_engine(xml_filepath, [coverpage_xml_filename], [data_source_name],
                                               template_filename, pdf_filename)
        new_report_name = JSNReportFileManager.pdf_archive(report_name, coverpage_xml_filename)
        return new_report_name

    def coverpage_names_from_order(self, order):
        """
        Build a name search dict for the cover page from an order's associated GeneratedReport
        :param order: the order that was placed orders.model.Order
        :return: dict
        """
        import xml.etree.ElementTree as ET
        from orders.models import GeneratedReport, SearchName
        order_reports = GeneratedReport.objects.get(order_id__exact=order.id)
        # generated_filenames = [order_reports.bankruptcy_filename, order_reports.state_filename, order_reports.usdc_filename]
        bankruptcy_filenames = order_reports.bankruptcy_filename.split(',')
        state_filenames = order_reports.state_filename.split(',')
        usdc_filenames =  order_reports.usdc_filename.split(',')
        patriot_filenames = order_reports.patriot_filename.split(',')
        # generated_filenames = [order_reports.cover_filename]
        generated_filenames = bankruptcy_filenames + state_filenames + usdc_filenames + patriot_filenames
        namesearch_dict = {}
        court_types = ['BKCY'] * len(bankruptcy_filenames)\
                      + ['STAE'] * len(state_filenames)\
                      + ['DSTR'] * len(usdc_filenames)\
                      + ['PTRT'] * len(patriot_filenames)
        print(("Generated filenames list: {}".format(generated_filenames)))
        for court_number, generated_file in enumerate(generated_filenames):
            if generated_file:
                generated_file = generated_file.replace('.pdf', '.xml')
                tree = ET.parse(os.path.join(settings.MEDIA_ROOT, generated_file))
                root = tree.getroot()  # Element
                if court_types[court_number] == 'PTRT':
                    for search_name_element in root.findall('SEARCH_NAME_ELEMENT'):
                        if len(search_name_element.find('MATCHES')) > 0:
                            searchname = search_name_element.find('SEARCHED_NAME').text
                            namesearch_court_list = namesearch_dict.get(searchname, [])
                            namesearch_court_list.append(court_types[court_number])
                            namesearch_dict[searchname] = namesearch_court_list
                else:
                    for case in root.findall('case'):
                        searchname = case.find('SEARCHNAME').text
                        namesearch_court_list = namesearch_dict.get(searchname, [])
                        namesearch_court_list.append(court_types[court_number])
                        namesearch_dict[searchname] = namesearch_court_list
        # make sure all names show, even if no results were found. return the all clear signal in this caes
        searchnames = SearchName.objects.filter(order_id=order.id)
        for searchname in searchnames:
            name = searchname.__str__()
            if not namesearch_dict.get(name, None):
                namesearch_dict[name] = None
        print(('----------> This is the namesearch dict built: {}'.format(namesearch_dict)))
        return namesearch_dict

    def _call_report_engine(self, xml_filepath, case_xml_filenames, data_source_names,
                            template_filename, pdf_filename):
        """
        High level function to make a call to the report engine with the supplied parameters.
        This function can generate reports for all of the various report types
        :param xml_filepath: filepath to the directory containing the xml files
        :param case_xml_filenames: name of the xml file with the case data
        :param data_source_names: name of the datasource to use
        :param template_filename: the name of the word document to use as a template to the windward engine
        :param pdf_filename: the name of the pdf file to use for the generated report
        :return:
        """
        import os.path
        from django.conf import settings

        base_uri = settings.WINDWARD_ENGINE_URL
        template = os.path.join('.', 'jsnetwork_project', 'media', template_filename)
        xml_data = []
        for x in case_xml_filenames:
            xml_data.append(os.path.join('.', 'jsnetwork_project', 'media', x))
        report_name = os.path.join('.', 'jsnetwork_project', 'media', pdf_filename)
        if os.path.isfile(template):
            pass
            # os.remove(template)
            # os.remove(report_name)
        report_engine = WindwardRestEngine(base_uri, template, xml_data,
                                           report_name, data_source_names)
        report_engine.make_report()
        # cleanup xml file
        if os.path.exists(xml_filepath):
            print(('Removing xml file: {}'.format(xml_filepath)))
            # os.remove(xml_filepath)
        # copy pdf to storage location
        if not template_filename == 'Docket List Template.docx':  # XXX test - doesn't actually generate anything
            for xml_filename in case_xml_filenames:
                JSNReportFileManager.pdf_archive(report_name, xml_filename)

        return report_name

    def set_generated_report_attributes(self, report_name, generated_report, report_type_attr, num_matches_attr, num_matches):
        """
        Function updating attributes related to the generated report. Includes the number of matches found for a given report type
        :param report_name: the name of the report to update
        :param generated_report: a GeneratedReport object type. Existing or created new
        :param report_type_attr: the report attribute to update. e.g. state_filename, usdc_filename
        :param num_matches_attr: the number of matches attribute to update
        :param num_matches: the number of matches
        :return: a copy of the updated GeneratedReport object
        """
        print(('set_genrated_report_attributes got {} matches for report type attribute {}'.format(num_matches, report_type_attr)))
        pdf_names = getattr(generated_report, report_type_attr, None)
        if pdf_names:
            pdf_names_list = pdf_names.split(",")
        else:
            pdf_names_list = []
        pdf_names_list.append(report_name)
        report_name = ",".join(pdf_names_list)
        setattr(generated_report, report_type_attr, report_name)
        num_existing_matches = getattr(generated_report, num_matches_attr)
        print(('<><><>Num existing matches: {}'.format(num_existing_matches)))
        if num_existing_matches == -1 or num_existing_matches is None:
            num_existing_matches = 0
        setattr(generated_report, num_matches_attr, num_matches+num_existing_matches)
        print(('<><><>Set new value for num_matches to: {}'.format(num_existing_matches+num_matches)))
        return generated_report

    @staticmethod
    def store_report_history_to_db(order_id, report_type, xml_filename):
        """
        Keep a log of the xml report files generated for an order future reference
        :param report_type: a valid ReportTypes report
        :param xml_filename: name of the xml file to save
        :return: instance of created NameReportHistory object
        """
        from datetime import datetime
        from orders.models import NameReportHistory

        nr = NameReportHistory()
        nr.xml_filename = xml_filename
        nr.order_id = order_id
        nr.report_type = report_type
        nr.date_created = datetime.now()
        nr.save()

        return nr

    # @TODO: condense down this section's repeated code
    def add_generated_report_to_order(self, order, report_name, report_type, num_matches):
        """
        Associate a GeneratedReport object with an order
        :param order: the order to use for this operation
        :param report_name: the name of the report
        :param report_type: the type of report. One of the ReportTypes enum
        :param num_matches: the number of matches found for the report of report_type
        :return:
        """
        import logging
        from orders.models import GeneratedReport

        if not report_name:
            return  # no results found, don't attach to order db
        xml_name = report_name[:-3] + 'xml'
        logger = logging.getLogger(__name__)
        logger.info('Attaching report name {} to order {} for report_type {}'.format(report_name, order.id, report_type))
        # generated_reports = order.generatedreport_set.order_by('-id')
        generated_report = GeneratedReport.objects.get_or_create(order_id=order.id)[0]
        if report_type == ReportTypes.BANKRUPTCY:
            report_type_attr = 'bankruptcy_filename'
            num_matches_attr = 'num_bankruptcy_matches'
            generated_report = self.set_generated_report_attributes(report_name,
                                                                    generated_report,
                                                                    report_type_attr,
                                                                    num_matches_attr,
                                                                    num_matches)
        elif report_type == ReportTypes.STATE:
            report_type_attr = 'state_filename'
            num_matches_attr = 'num_state_matches'
            generated_report = self.set_generated_report_attributes(report_name,
                                                                    generated_report,
                                                                    report_type_attr,
                                                                    num_matches_attr,
                                                                    num_matches)
            ReportFactory.store_report_history_to_db(order.id, report_type, xml_name)
        elif report_type == ReportTypes.STATE_HIGH_VALUE:
            report_type_attr = 'state_hv_filename'
            num_matches_attr = 'num_state_hv_matches'
            generated_report = self.set_generated_report_attributes(report_name,
                                                                    generated_report,
                                                                    report_type_attr,
                                                                    num_matches_attr,
                                                                    num_matches)
            ReportFactory.store_report_history_to_db(order.id, report_type, xml_name)
        elif report_type == ReportTypes.USDC:
            report_type_attr = 'usdc_filename'
            num_matches_attr = 'num_usdc_matches'
            generated_report = self.set_generated_report_attributes(report_name,
                                                                    generated_report,
                                                                    report_type_attr,
                                                                    num_matches_attr,
                                                                    num_matches)
            ReportFactory.store_report_history_to_db(order.id, report_type, xml_name)
        elif report_type == ReportTypes.PATRIOT:
            report_type_attr = 'patriot_filename'
            num_matches_attr = 'num_patriot_matches'
            generated_report = self.set_generated_report_attributes(report_name,
                                                                    generated_report,
                                                                    report_type_attr,
                                                                    num_matches_attr,
                                                                    num_matches)
            ReportFactory.store_report_history_to_db(order.id, report_type, xml_name)
        elif report_type == ReportTypes.COVER:
            generated_report.cover_filename = report_name
        elif report_type == ReportTypes.DOCKETLIST:
            generated_report.docket_list_filename = report_name
        elif report_type == ReportTypes.FULL:
            # print("[Fake] attaching {} as the report name to the merged report!!!!!!!!!!!!!".format(report_name))
            generated_report.merged_report_filename = report_name
            # generated_report.name_select_ready = 'Y'

        generated_report.order = order
        generated_report.save()
