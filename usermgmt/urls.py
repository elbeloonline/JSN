from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^client_edit/(?P<client_id>[0-9]+)$', views.index, name='client_edit'),
    url(r'^client_add/(?P<client_id>[0-9]+)/(?P<add_id>[0-9]+)$', views.index, name='client_add'),
    url(r'^new_user/$', views.new_user, name='new_user'),
]
