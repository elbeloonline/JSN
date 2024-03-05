from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    # url(r'^common_names/$', views.common_names, name='common_names'),
    url(r'^common_names/(?P<name_type>\w+)$', views.common_names, name='common_names'),
    url(r'^common_names/(?P<name_type>\w+)/(?P<name_select>\w+)$', views.common_names, name='common_names'),
    url(r'^new_name_alias/(?P<name_type>\w+)$', views.new_name_alias, name='new_name_alias'),
    url(r'^new_name_alias/(?P<name_type>\w+)/(?P<name_select>\w+)/(?P<new_name_alias>\w+)$', views.new_name_alias, name='new_name_alias'),
]
