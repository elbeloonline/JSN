from django.core.urlresolvers import reverse
from django.test import TestCase

from orders.models import Order, Client, SearchName, Forename

class ClientModelTests(TestCase):

    def setUp(self):
        Client.objects.get_or_create(client_name="Xmus Jackson Flaxon-Waxon", phone="555-443-2211", email="xfw@z.com")
        Client.objects.get_or_create(client_name="Jackmerius Tacktheritrix", email="jt@z.com")

    def test_list(self):
        self.assertTrue(Client.objects.count() == 2)

    def test_detail(self):
        c = Client.objects.get(client_name="Xmus Jackson Flaxon-Waxon")
        self.assertEqual(c.client_name, "Xmus Jackson Flaxon-Waxon")

    def test_create(self):
        Client.objects.create(client_name="Javaris Jamar Javarison-Lamar", email="jjl@eastabstracts.com")
        c = Client.objects.filter(client_name="Javaris Jamar Javarison-Lamar").first() # a list is returned!
        self.assertEqual(c.email, "jjl@eastabstracts.com")


class OrderModelTests(TestCase):

    def setUp(self):
        Client.objects.get_or_create(client_name="Jackmerius Tacktheritrix", email="jt@z.com")

    def test_create(self):
        c = Client.objects.get(client_name="Jackmerius Tacktheritrix")
        o = Order.objects.create(title_number="12345a", client=c)
        o2 = c.order_set.first()
        self.assertEqual(o2.title_number, "12345a")

    def test_list(self):
        c = Client.objects.get(client_name="Jackmerius Tacktheritrix")
        Order.objects.create(title_number="2329101", client=c)
        Order.objects.create(title_number="0291291", client=c)
        Order.objects.create(title_number="093ik2a", client=c)
        self.assertTrue(c.order_set.count() > 0)

    def test_detail(self):
        Client.objects.get_or_create(client_name="J'Dinkalage Morgoone")
        c = Client.objects.filter(client_name="J'Dinkalage Morgoone").first()
        o = Order.objects.create(title_number="54321a", client=c)
        sn = SearchName.objects.create(first_name="Jan", last_name="Iverson", search_from="2016-01-31",
                                       search_to="2017-01-31", order=o)
        order_search_from = c.order_set.first().searchname_set.first().search_from
        self.assertEqual(str(order_search_from), "2016-01-31")

    def test_sync_qb_client(self):
        from .utils import OrderUtils
        rows_processed = OrderUtils.sync_qb_clients()
        self.assertGreater(rows_processed, 0)


class SearchNameModelTests(TestCase):

    def setUp(self):
        Client.objects.get_or_create(client_name="J'Dinkalage Morgoone", email="jm@z.com")

    def test_create(self):
        c = Client.objects.get(client_name="J'Dinkalage Morgoone")
        o = Order.objects.create(title_number="54321a", client=c)
        sn = SearchName.objects.create(first_name="Jan", last_name="Iverson", search_from="2016-01-31",
                                       search_to="2017-01-31", order=o)
        order_search_from = c.order_set.first().searchname_set.first().search_from
        self.assertEqual(str(order_search_from), "2016-01-31")

