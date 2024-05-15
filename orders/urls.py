from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^order_new/', views.order_new, name='order_new'),
    url(r'^(?P<order_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^quick_search/', views.quick_search, name='quick_search'),
    url(r'^quick_order/', views.quick_order, name='quick_order'),
    url(r'^run_search/(?P<order_id>[0-9]+)/(?P<report_type>\w+)/$', views.run_search, name='run_search'),
    url(r'^settings/', views.settings, name='settings'),
    url(r'^view_pdf/(?P<filename>.+)$', views.view_report, name="view_report"),
    url(r'^xml-to-base64/$', views.xml_to_base64, name="xml_to_base64"),
    url(r'^csv_report/(?P<order_id>.+)$', views.csv_report, name="csv_report"),
    url(r'^csv_report_high_value/(?P<order_id>.+)$', views.csv_report_high_value, name="csv_report_high_value"),
    url(r'^merge_and_view/(?P<order_id>[0-9]+)/(?P<report_type>\w+)$', views.merge_and_view_pdf, name="merge_and_view"),
    url(r'^order_status/(?P<order_id>[0-9]+)/(?P<report_type>\w+)$', views.order_status, name='order_status'),
    url(r'^reorder/(?P<order_id>[0-9]+)$', views.reorder, name='reorder'),
    url(r'^name_select/(?P<order_id>[0-9]+)$', views.select_names, name='name_select'),
    url(r'^name_select_view_pdf/', views.name_select_view_pdf, name='name_select_view_pdf'),
    url(r'^search_prev/', views.search_prev, name='search_prev'),
]
