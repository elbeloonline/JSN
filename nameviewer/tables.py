import django_tables2 as tables

from orders.models import Forename, Surname

class ForenameTable(tables.Table):
    class Meta:
        model = Forename
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
        fields = {'name', 'name_match', 'score'} # fields to display
