from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory

from .views import order_new


def add_middleware_to_request(request, middleware_class):
    middleware = middleware_class
    middleware.process_request(request)
    return request


def add_middleware_to_response(response, middleware_class):
    middleware = middleware_class
    middleware.process_response(response)
    return response


class SecuredFormTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_no_anonymous_add_order(self):
        request = self.factory.get('/orders/order_new/')
        request.user = AnonymousUser()
        # annotate the request with a session
        midware = SessionMiddleware()
        request = add_middleware_to_request(request, midware)
        request.session.save()
        # process and test the request
        response = self.client.get('/orders/order_new/', follow=True)
        self.assertContains(response, "Sign In", status_code=200)

