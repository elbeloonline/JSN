from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^results_comparison/(?P<order_id>.+)$', views.results_comparison, name="results_comparison"),
    url(r'^cj_comparison/', views.cj_comparison, name="cj_comparison"),
]
