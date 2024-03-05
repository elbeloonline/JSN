from django.core.urlresolvers import reverse
from django.test import TestCase

from .forms import SearchNameForm, OrderForm, ClientForm


class HomePageTest(TestCase):
    def test_root_loads_index_html(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>\n<html lang="en">\n  <head>\n'))
        self.assertIn("Sign In", response.content.decode())


class OrderFormTest(TestCase):
    def _make_form_data(self):
        form_data = { 'form_client-client_name': 'Xmus Jackson Flaxon-Waxon',
                      'form_order-title_number': '12345a',
                      'form_search_name-first_name': 'Leroy',
                      'form_search_name-last_name': 'Jenkins' }
        return form_data

    def test_date_empty_fails(self):
        form_data = self._make_form_data()
        form_search_name = SearchNameForm(form_data, prefix="form_search_name")
        # form_client = ClientForm(form_data, prefix="form_client")
        # form_order = OrderForm(form_data, prefix="form_order")
        self.assertFalse(form_search_name.is_valid())

    def test_date_in_the_future_fails(self):
        form_data = self._make_form_data()
        form_data['form_search_name-search_to'] = '01/01/3127'
        form_search_name = SearchNameForm(form_data, prefix="form_search_name")
        self.assertFalse(form_search_name.is_valid())

    def test_set_dates_passes(self):
        form_data = self._make_form_data()
        form_data['form_search_name-search_from'] = '01/01/1997'
        form_data['form_search_name-search_to'] = '01/01/2017'
        form_search_name = SearchNameForm(form_data, prefix="form_search_name")
        self.assertTrue(form_search_name.is_valid())


