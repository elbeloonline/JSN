
import os

from django.core.management.base import BaseCommand, CommandError

from pdftools.utils import DobExtractor, JudgmentsFileHash, JudgmentsFileHashType, JudgmentsExtractor

class Command(BaseCommand):
    help = 'Scrapes the DOBs from a State Capital Judgment File'

    def add_arguments(self, parser):
        parser.add_argument('--cj_pdf_file',type=str)

    def _handle_pdf_parsing(self, sc_pdf_filename):
        judgment_file_hash = JudgmentsFileHash.generate_file_hash(sc_pdf_filename)
        # print('Generated file hash: {}'.format(judgment_file_hash))

        if not JudgmentsFileHash.file_already_processed(judgment_file_hash, processing_type=JudgmentsFileHashType.SCDOB):
            print("Sending PDF to parser: {}".format(sc_pdf_filename))
            sc_parser = DobExtractor(sc_pdf_filename, ptype="SC")
            ##
            # cj_judgments = cj_parser.parse_pdf_aliases()
            dob_dict_list = sc_parser.parse_pdf_dobs()
            JudgmentsExtractor.save_sc_dobs(dob_dict_list, judgment_file_hash)

            # print('Extracted aliases: {}'.format(cj_judgments))
        else:
            print('File already processed, skipping.')


    def handle(self, *args, **options):
        MAX_PDFS_TO_PROCESS = 10000000
        pdf_dir = os.path.join('pdftools', 'sc_test_docs','20201220-sc-downloads')
        # pdf_dir = os.path.join('pdftools', 'sc_test_docs', 'test')

        i = 0
        for filename in os.listdir(pdf_dir):
            # print('Examining file: {}'.format(filename))
            if filename.endswith(".pdf") and i < MAX_PDFS_TO_PROCESS:
                sc_pdf_filename = os.path.join(pdf_dir, filename)
                self._handle_pdf_parsing(sc_pdf_filename)
                i += 1
            else:
                pass


        self.stdout.write(self.style.SUCCESS("Command completed"))
