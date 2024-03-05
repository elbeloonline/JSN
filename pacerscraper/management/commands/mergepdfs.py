

import logging
import time

from django.core.management.base import BaseCommand, CommandError

from nameviewer.pdfutils import PdfMerger


class Command(BaseCommand):
    help = 'Merge multiple report pdfs for each court into a single pdf'

    def add_arguments(self, parser):
        parser.add_argument('order_id', type=int)

    def handle(self, *args, **options):

        logger = logging.getLogger(__name__)
        start = time.time()
        # model operations

        if options['order_id']:
            order_id = options['order_id']
            logger.info('Generating merged pdf for order {}.'.format(order_id))
            doc_merger = PdfMerger()
            merged_pdf = doc_merger.merge_reports(order_id)
            logger.info('Generated merged pdf: {}'.format(merged_pdf))
        executiontime = time.time() - start
        self.stdout.write(self.style.SUCCESS("Done! Total elapsed time: {:.2f} seconds".format(executiontime)))

# --------


