from django.test import TestCase

from orders.forms import SearchNameForm, OrderForm, ClientForm


class StateSearchTest(TestCase):

    def test_john_sylvester(self):
        from .models import StateReportQueryManager
        from orders.models import SearchName

        name_to_search = SearchName(first_name='John', last_name='Sylvester')
        name_to_search.search_from = '1998-08-26'
        name_to_search.search_to = '2018-08-26'
        cases = StateReportQueryManager.query_database_by_searchname_details(name_to_search)
        num_cases = len(cases)
        print(("Num cases returned: {}".format(num_cases)))
        self.assertEqual(num_cases, 15)

    def test_gladys_doughtery(self):
        from .models import StateReportQueryManager
        from orders.models import SearchName

        name_to_search = SearchName(first_name='gladys', last_name='dougherty')
        name_to_search.search_from = '1998-08-26'
        name_to_search.search_to = '2018-08-26'
        cases = StateReportQueryManager.query_database_by_searchname_details(name_to_search)
        num_cases = len(cases)
        print(("Num cases returned: {}".format(num_cases)))
        self.assertEqual(num_cases, 1)


