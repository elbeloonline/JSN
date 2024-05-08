import os

from django.conf import settings

from nameviewer.windward import ReportTypes

PDF_DIR = os.path.join(settings.MEDIA_ROOT, 'generatedpdfs') + '/'


class ReportMunger:

    @staticmethod
    def merge_pdfs(pdf_path, pdf_files):
        """
        Merge pdf files into a single pdf
        :param pdf_path: path containing files in pdf_files list
        :param pdf_files: list of pdf files to merge in dir pdf_path
        :return: filename of new pdf
        """
        # type: (str, List) -> str
        # https://stackoverflow.com/questions/48894311/merging-many-pdfs-into-one-pdf
        from PyPDF2 import PdfFileMerger
        import uuid

        merger = PdfFileMerger()
        for pdf_file in pdf_files:
            merger.append(pdf_path + pdf_file)
        new_pdf_report = uuid.uuid4().hex + '.pdf'
        merger.write(pdf_path + new_pdf_report)
        merger.close()

        return new_pdf_report


class PdfMerger:

    @classmethod
    def merge_report_list_external(cls, pdf_list):
        """
        Wrapper function to allow for merging a list of PDFs outside of the class
        :param pdf_list: list of pdf names to merge
        :return: filename of merged pdf
        """
        p = PdfMerger()
        merged_pdf = p._merge_report_list(pdf_list, add_page_nums=False)
        return merged_pdf

    def _merge_report_list(self, pdf_list, add_page_nums=True):
        """
        Merges a list of pdfs into one final pdf and adds page numbers
        :param pdf_list: list of pdf names to merge
        :return: filename of merged pdf
        """
        print(('Merging together the following PDFs: {}'.format(pdf_list)))
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'generatedpdfs') + '/'
        rm = ReportMunger()
        merged_pdf = rm.merge_pdfs(pdf_dir, pdf_list)
        if add_page_nums:
            self._add_page_numbers_to_pdf(pdf_dir, merged_pdf)
        return merged_pdf

    def merge_reports(self, order_id):
        """
        Generates a master merged PDF from an order ID containing multiple pdf files from searches completed
        :param order_id: The order id to use for the pdf merge operation
        :return: filename of merged pdf
        """
        import os
        from django.conf import settings
        from orders.models import GeneratedReport

        generated_reports = GeneratedReport.objects.get(order_id=order_id)
        pdf_list = []
        # @TODO: add cover page
        if generated_reports.cover_filename:
            x = generated_reports.cover_filename.split(',')
            for e in x:
                pdf_list.append(e)
            # pdf_list.append(e for e in x)
        if generated_reports.docket_list_filename:
            if int(generated_reports.num_state_matches or 0) > 0 or int(generated_reports.num_bankruptcy_matches or 0) > 0 or int(generated_reports.num_usdc_matches or 0) > 0:
                pdf_list.append(generated_reports.docket_list_filename)
        if generated_reports.state_filename and int(generated_reports.num_state_matches or 0) > 0:
            x = generated_reports.state_filename.split(',')
            for e in x:
                pdf_list.append(e)
        if generated_reports.bankruptcy_filename and int(generated_reports.num_bankruptcy_matches or 0) > 0:
            x = generated_reports.bankruptcy_filename.split(',')
            for e in x:
                pdf_list.append(e)
        if generated_reports.usdc_filename and int(generated_reports.num_usdc_matches or 0) > 0:
            x = generated_reports.usdc_filename.split(',')
            for e in x:
                pdf_list.append(e)
        if generated_reports.patriot_filename:
            x = generated_reports.patriot_filename.split(',')
            for e in x:
                pdf_list.append(e)

        print(('Using the following for the pdf_list of files to merge together: {}'.format(pdf_list)))
        return self._merge_report_list(pdf_list)

    def merge_reports_by_type(self, order_id, report_type):
        """
        Merge a series of PDFs into a single PDF.
        This function handles returning the LAST report generated for a report type.
        This can happen if an order is requested to be generated multiple times
        :param order_id: the id of the order to work with
        :param report_type: one of enum selected from ReportTypes
        :return: filename of the merged pdf
        """
        from orders.models import Order
        order = Order.objects.get(id=order_id)
        generated_reports = order.generatedreport_set.order_by('-id')
        final_pdf_list = []
        show_single_report = False
        if report_type == ReportTypes.STATE:
            pdf_type_attribute = 'state_filename'
            show_single_report = True
        elif report_type == ReportTypes.BANKRUPTCY:
            pdf_type_attribute = 'bankruptcy_filename'
            show_single_report = True
        elif report_type == ReportTypes.USDC:
            pdf_type_attribute = 'usdc_filename'
            show_single_report = True

        if len(generated_reports) > 0:
            print(("Merging '{}' report into a single file".format(report_type)))
            generated_report = generated_reports[0]
            # pdf_names = generated_report.state_filename
            pdf_names = getattr(generated_report, pdf_type_attribute)
            if show_single_report:
                pdf_names = pdf_names.split(',')[-1]
            print(("Got this list of pdf names from the database: {}".format(pdf_names)))
            pdf_names_list = pdf_names.split(",")
            final_pdf_list = final_pdf_list + pdf_names_list
        return self._merge_report_list(final_pdf_list)

    def _add_page_numbers_to_pdf(self, pdf_dir, pdf_name):
        """
        Add page numbers to the final PDF since the original is created from multiple PDFs
        https://stackoverflow.com/questions/53864602/python-numbering-pages-in-a-pdf-using-pypdf2-and-io
        :param merged_pdf: name of pdf
        :return: None
        """
        from PyPDF2 import PdfFileWriter, PdfFileReader
        import io
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import LETTER

        pdf = PdfFileReader(pdf_dir + pdf_name)
        pdf_writer = PdfFileWriter()

        for page in range(pdf.getNumPages()):
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=LETTER)

            can.drawString(10, 10, "Page " + str(page + 1))
            can.save()
            packet.seek(0)
            watermark = PdfFileReader(packet)
            watermark_page = watermark.getPage(0)

            pdf_page = pdf.getPage(page)
            pdf_page.mergePage(watermark_page)
            pdf_writer.addPage(pdf_page)

        with open(pdf_dir + pdf_name, 'wb') as fh:
            pdf_writer.write(fh)

    @classmethod
    def get_state_report_from_order_id(cls, order_id, high_value=False):
        """
        Convenience method to fetch the merged report from an order
        :param order_id: order id to use to lookup the merged report name
        :return: name of the stored file/pdf
        """
        from orders.models import GeneratedReport

        report_name = None
        order_report = GeneratedReport.objects.filter(order_id=order_id)
        if order_report and len(order_report) > 0:
            generated_report = order_report[0]
            if not high_value:
                report_name = generated_report.state_filename
            else:
                report_name = generated_report.state_hv_filename

        return report_name

    @classmethod
    def get_bkcy_report_from_order_id(cls, order_id):
        """
        Convenience method to fetch the merged report from an order
        :param order_id: order id to use to lookup the merged report name
        :return:
        """
        from orders.models import GeneratedReport

        report_name = None
        order_report = GeneratedReport.objects.filter(order_id=order_id)
        if order_report and len(order_report) > 0:
            generated_report = order_report[0]
            report_name = generated_report.bankruptcy_filename

        return report_name

    @classmethod
    def get_usdc_report_from_order_id(cls, order_id):
        """
        Convenience method to fetch the merged report from an order
        :param order_id: order id to use to lookup the merged report name
        :return:
        """
        from orders.models import GeneratedReport

        report_name = None
        order_report = GeneratedReport.objects.filter(order_id=order_id)
        if order_report and len(order_report) > 0:
            generated_report = order_report[0]
            report_name = generated_report.usdc_filename

        return report_name

class JudgmentPageExtractor:

    @staticmethod
    def extractScnjPages(judgments, pdf_file_list):
        """
        Generate a dict of judgments with the page each judgment is found on using a pdf
        If multiple PDFs are provided the pdfs are merged and then processed
        :param judgments: a list of judgments to look for and generate page numbers for in the merged pdf
        :param pdf_file_list: a list of pdfs to parse
        :return: a dict of judgments and the page number associated with each
        """
        import PyPDF2

        if not pdf_file_list is list:
            pdf_file_list = pdf_file_list.split(',')
        merged_pdf_file = PdfMerger.merge_report_list_external(pdf_file_list)

        pdf_page_offset = 2
        final_judgment_dict = {}
        pdf_file_path = PDF_DIR + merged_pdf_file
        with open(pdf_file_path, mode='rb') as f:
            reader = PyPDF2.PdfFileReader(f)
            for i, page in enumerate(reader.pages):
                page_text = page.extractText()
                judgment_page_dict = JudgmentPageExtractor._find_judgments_on_page(judgments, page_text, i+pdf_page_offset)
                final_judgment_dict.update(judgment_page_dict)
        return final_judgment_dict

    @staticmethod
    def _find_judgments_on_page(judgments, page_text, page_number):
        """
        Look for judgments on a page and return a dict of judgments found within the page_text
        :param judgments: list of judgments
        :param page_text: str containing text extracted from pdf page
        :param page_number: page number from original document being processed
        :return: a dict of judgments with the associated page number
        """
        judgment_page_dict = {}
        for judgment in judgments:
            if judgment in page_text:
                judgment_page_dict[judgment] = page_number
        return judgment_page_dict

    @staticmethod
    def extractBkcyPages(judgments, pdf_filename, xlsx_filename):
        """
        Look for bkcy judgments in a pdf and update an excel file with the page numbers for the judgments located
        :param judgments: a list of judgments to process
        :param pdf_filename: the pdf file to use when searching for judgments
        :param xlsx_filename: the xlsx file to use for calculating the page number offset
        :return: a dict of judgments and their respective page numbers
        """
        import PyPDF2
        from .csvwriter import JSNCSVWriter
        #
        # get page_offset
        #
        page_offset = JSNCSVWriter.calc_xlsx_page_offset(xlsx_filename)

        final_judgment_dict = {}
        pdf_file_path = PDF_DIR + pdf_filename
        with open(pdf_file_path, mode='rb') as f:
            reader = PyPDF2.PdfFileReader(f)
            for i, page in enumerate(reader.pages):
                page_text = page.extractText()
                judgment_page_dict = JudgmentPageExtractor._find_judgments_on_page(judgments, page_text, i + 1)
                final_judgment_dict.update(judgment_page_dict)
        for jkey, jval in list(final_judgment_dict.items()):
            final_judgment_dict[jkey] = jval + page_offset
        return final_judgment_dict

    @staticmethod
    def extractUsdcPages(judgments, pdf_file, xlsx_filename):
        """
        Look for bkcy judgments in a pdf and update an excel file with the page numbers for the judgments located
        :param judgments: a list of judgments to process
        :param pdf_file: the pdf file to when for searching for judgments
        :param xlsx_filename: the xlsx file to use for calculating the page number offset
        :return:
        """
        import PyPDF2
        from nameviewer.printfactory import PrintFactory
        from .csvwriter import JSNCSVWriter

        # pdf_page_offset = 2
        page_offset = JSNCSVWriter.calc_xlsx_page_offset(xlsx_filename)

        final_judgment_dict = {}
        pdf_file_path = PDF_DIR + pdf_file
        # formatted_judgments = []
        # for judgment in judgments:
        #     formatted_judgment = PrintFactory.format_usdc_case_number(judgment)
        #     formatted_judgments.append(formatted_judgment)
        with open(pdf_file_path, mode='rb') as f:
            reader = PyPDF2.PdfFileReader(f)
            for i, page in enumerate(reader.pages):
                page_text = page.extractText()
                judgment_page_dict = JudgmentPageExtractor._find_judgments_on_page(judgments, page_text, i + 1)
                final_judgment_dict.update(judgment_page_dict)
        for jkey, jval in list(final_judgment_dict.items()):
            final_judgment_dict[jkey] = jval + page_offset
        return final_judgment_dict

    @staticmethod
    def countIndexPages(order_id):
        """
        Count the number of pages for the index using the index PDF associated with the order id
        :param order_id: The order id to work with for this operation
        :return: number of pages counted in the PDF
        """
        import PyPDF2
        from orders.models import GeneratedReport

        num_pages = 0
        generated_reports = GeneratedReport.objects.get(order_id=order_id)
        pdf_filename = generated_reports.docket_list_filename
        if pdf_filename:
            pdf_file_path = PDF_DIR + pdf_filename
            with open(pdf_file_path, mode='rb') as f:
                reader = PyPDF2.PdfFileReader(f)
                num_pages = len(reader.pages)

        return num_pages
