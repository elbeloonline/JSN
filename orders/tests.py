from django.test import TestCase
from django.http import HttpRequest

from orders.views import index

# Create your tests here.


# class HomePageTest(TestCase):
#
#     def test_root_loads_index_html(self):
#         request = HttpRequest()
#         response = index(request)
#         self.assertTrue(response.content.startswith('<!DOCTYPE html>\n<html lang="en">\n<head>'))
#         self.assertIn("Use this document as a way")
