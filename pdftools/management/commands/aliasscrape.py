
import os

from django.core.management.base import BaseCommand, CommandError

from pdftools.utils import AliasesExtractor, JudgmentsFileHash

class Command(BaseCommand):
    help = 'Compares two judgment files'

    def add_arguments(self, parser):
        parser.add_argument('--cj_pdf_file',type=str)

    def handle(self, *args, **options):
        pdf_dir = os.path.join('pdftools', 'test_docs')
        # cj_pdf_filename = os.path.join(pdf_dir, '5041487B CJ.pdf')
        # cj_pdf_filename = os.path.join(pdf_dir, '20ST532.pdf')
        # cj_pdf_filename = os.path.join(pdf_dir, 'copy of 100107 CJ 100125.pdf')
        cj_pdf_filename = os.path.join(pdf_dir, '20ST528.pdf')

        judgment_file_hash = JudgmentsFileHash.generate_file_hash(cj_pdf_filename)
        print('Generated file hash: {}'.format(judgment_file_hash))

        if not JudgmentsFileHash.file_already_processed(judgment_file_hash):
            cj_parser = AliasesExtractor(cj_pdf_filename, ptype="CJ")
            cj_judgments = cj_parser.parse_pdf_aliases()
            # jsn_parser = JudgmentsExtractor(jsn_pdf_filename, ptype="JSN")
            # jsn_judgments = jsn_parser.parse_pdf_judgments()

            # print('Extracted CJ judgments: {}'.format(cj_judgments))
            # print('Extracted JSN judgments: {}'.format(jsn_judgments))
            print('Extracted aliases: {}'.format(cj_judgments))
        else:
            print('File already processed, skipping.')

        self.stdout.write(self.style.SUCCESS("Command completed"))
