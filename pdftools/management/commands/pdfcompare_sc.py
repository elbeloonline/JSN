
import os

from django.core.management.base import BaseCommand, CommandError

from pdftools.utils import JudgmentsExtractor

class Command(BaseCommand):
    help = 'Compares two judgment files'

    def add_arguments(self, parser):
        parser.add_argument('jsn_pdf_file',type=str)
        parser.add_argument('sc_pdf_file',type=str)

    def handle(self, *args, **options):
        pdf_dir = os.path.join('pdftools', 'test_docs')
        sc_pdf_filename = os.path.join(pdf_dir, options['sc_pdf_file'])
        jsn_pdf_filename = os.path.join(pdf_dir, options['jsn_pdf_file'])

        sc_parser = JudgmentsExtractor(sc_pdf_filename, ptype="SC")
        sc_judgments = sc_parser.parse_pdf_judgments()
        sc_judgments = JudgmentsExtractor.sc_judgments_to_jsn_judgments(sc_judgments)
        jsn_parser = JudgmentsExtractor(jsn_pdf_filename, ptype="JSN")
        jsn_judgments = jsn_parser.parse_pdf_judgments()

        print('Extracted CJ judgments: {}'.format(sc_judgments))
        print('Extracted JSN judgments: {}'.format(jsn_judgments))
        self.stdout.write(self.style.SUCCESS("Command completed"))
