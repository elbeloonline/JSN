import django_filters

from orders.models import Forename, Surname


class ForenameFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Forename
        fields = ['name']


class SurnameFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Surname
        fields = ['name']
