# from django.conf import settings
from django.test import TestCase

from .utils import PacerScraperUtils
# Create your tests here.


class ChromeDriverTestCase(TestCase):

    def setUp(self):
        self.file_to_parse = '5fd8e643-1742-4a07-a853-a2f3f91c333c.html'
        self.single_case_number = '1:13-cr-00167-JBS'

        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1024, 768))
        display.start()

    def tearDown(self):
        browser.close()
        display.stop()

    def test_generic_connect(self):
        """
        Get a web browser using Chrome as the driver
        :return: selenium.webdriver
        """
        from selenium import webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--dns-prefetch-disable')
        options.add_argument('--no-sandbox')
        service_log_path = "./log/chromedriver.log"
        service_args = ['--verbose']

        # driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options, service_args=service_args, service_log_path=service_log_path)
        driver = webdriver.Chrome(chrome_options=options, service_args=service_args, service_log_path=service_log_path)

        # driver = PacerScraperUtils.get_webdriver()
        driver.get("http://www.python.org")
        self.assertIn("Python", driver.title)
