# from django.conf import settings
from django.test import TestCase, SimpleTestCase

from .utils import PacerScraperUtils as psutils
# Create your tests here.


class UsdcPacerJudgmentTestCase(TestCase):

    def test_check_stop_file_terminates_execution(self):
        """
        This is the main function for the general workflow
        :return:
        """
        import logging
        logger = logging.getLogger(__name__)
        import os

        from_date_str = '1/4/2017'
        to_date_str = '1/4/2017'
        # psutils.remove_stop_files()
        if not os.path.exists(psutils.stop_file):
            open(psutils.stop_file, 'a').close()  # touch file
        usdc_report_contents = psutils.query_and_archive_judgment_report(from_date_str, to_date_str)
        logger.info("Judgment file generated: {}".format(usdc_report_contents.archive_file))
        row_count = psutils.build_judgment_index_report_from_local_file(usdc_report_contents.archive_file)
        self.assertEqual(row_count, 0)
        print("Done!")
