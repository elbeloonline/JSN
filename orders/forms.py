from datetime import datetime

from django import forms
from .models import SearchName, Order, Client

class SearchNameForm(forms.ModelForm):
    def clean(self):
        ''' Validation method for form'''

        import logging
        import re
        logger = logging.getLogger(__name__)

        cleaned_data = super(SearchNameForm, self).clean()
        from_date = cleaned_data.get('search_from', None)
        to_date = cleaned_data.get('search_to', None)
        todays_date = datetime.now()
        right_now_datetime = datetime.combine(todays_date, datetime.min.time())
        if from_date is None:
            raise forms.ValidationError("Search from date is required.")
        search_to_date_datetime = datetime.combine(to_date, datetime.min.time())
        if to_date is None or search_to_date_datetime > right_now_datetime:
            raise forms.ValidationError("Search to date is required.")

        first_name = cleaned_data.get('first_name', None)
        last_name = cleaned_data.get('last_name', None)
        company_name = cleaned_data.get('company_name', None)
        high_value_search = cleaned_data.get('high_value_search', False)
        cleaned_data['company_name'] = re.sub('[,\-]', '', company_name)
        self.cleaned_data = cleaned_data

        if len(first_name) == 2 and any(elem in first_name for elem in ".,"):
            raise forms.ValidationError("{} is not a valid search name. Please contact your client to obtain a longer name.")
        if not first_name and not company_name:
            raise forms.ValidationError("First name is required.")
        if not last_name and first_name:
            raise forms.ValidationError("Last name is required.")

        print(('Names entered [f,l,c]: {} - {} - {}'.format(first_name, last_name, company_name)))
        if first_name.strip() != '':
            logger.info('first name: {}'.format(first_name))
            if last_name.strip() == '':
                msg = "First and last name required for search."
                self.add_error('last_name', msg)
            else:
                logger.warning('last name: {}'.format(last_name))
        # elif company_name.strip() == '':
        #         msg = "A company name is required."
        #         logger.warning(msg)
        #         self.add_error('company_name', msg)

        return cleaned_data # only return this if you wish

    class Meta:
        model = SearchName
        fields = ('first_name', 'middle_name', 'last_name', 'suffix', 'is_company', 'company_name',\
                  'company_type', 'address1', 'address2', 'city', 'zip', 'search_from', 'search_to',\
                  'name_qualifier', 'exact_name_match', 'additional_notes', 'high_value_search')
        widgets = {
            'search_from': forms.DateInput(attrs={'class': 'datepicker'}),
            'search_to': forms.DateInput(attrs={'class': 'datepicker'}),
        }


class ClientForm(forms.ModelForm):
    client_name = forms.ModelChoiceField(queryset=Client.objects.all().order_by('client_name'),
                                         empty_label="Please select")

    def clean(self):
        ''' Validation method for form'''

        import logging
        logger = logging.getLogger(__name__)

        cleaned_data = super(ClientForm, self).clean()
        client_id = cleaned_data.get('client_name', -1)
        if client_id == -1:
            raise forms.ValidationError("Please select a valid client.")

    class Meta:
        model = Client
        fields = ('client_name',)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('title_number', 'internal_tracking_num', 'order_method')


class QuickSearchForm(forms.Form):
    first_name = forms.CharField(max_length=50, label='First name')
    last_name = forms.CharField(max_length=50)

class SessionSettingsForm(forms.Form):
    name_match_score = forms.IntegerField(max_value=100, min_value=80, label='Name match score')
