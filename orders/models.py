# noinspection PyPackageRequirements


from django.db import models

from core.models import TimeStampedModel


# Create your models here.
class Client(models.Model):
    """
    A class for representing a client model
    """
    client_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    client_id = models.CharField(max_length=50, blank=True)  # quickbooks number
    addr1 = models.CharField(max_length=100, blank=True, default=None, null=True)
    addr2 = models.CharField(max_length=100, blank=True, default=None, null=True)
    city = models.CharField(max_length=50, blank=True, default=None, null=True)
    state = models.CharField(max_length=2, blank=True, default=None, null=True)
    zip = models.CharField(max_length=10, blank=True, default=None, null=True)

    def __str__(self):
        return self.client_name


class Order(TimeStampedModel):
    """
    A simple class for representing an order in the system
    """
    EMAIL = 'EM'
    WEB_SERVICES = 'WB'
    TELEPHONE = 'TL'
    ORDER_SOURCE_CHOICES = (
        (EMAIL, 'Email'),
        (TELEPHONE, 'Telephone'),
        (WEB_SERVICES, 'Web Services'),
    )
    order_method = models.CharField(max_length=2, choices=ORDER_SOURCE_CHOICES, default=EMAIL)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # each order is reference to a single client
    title_number = models.CharField(max_length=20, verbose_name='Client file number')
    is_reorder = models.BooleanField(default=False)
    internal_tracking_num = models.CharField(max_length=100, blank=True, verbose_name='Internal number')
    date_invoiced = models.DateField(blank=True, default=None, null=True)


    def date_ordered(self):
        return self.created
    date_ordered.short_description = "Date ordered"

    def __str__(self):
        return self.title_number


class GeneratedReport(models.Model):
    """
    A simple class for representing generated reports in the system
    """
    bankruptcy_filename = models.CharField(max_length=255)
    usdc_filename = models.CharField(max_length=255)
    state_filename = models.CharField(max_length=255)
    state_hv_filename = models.CharField(max_length=255, default=None, null=True)
    cover_filename = models.CharField(max_length=255, blank=True, default=None, null=True)
    docket_list_filename = models.CharField(max_length=255, blank=True, default=None, null=True)
    patriot_filename = models.CharField(max_length=1000, blank=True, default=None, null=True)
    merged_report_filename = models.CharField(max_length=255, blank=True)
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE) # each generated report is references to a single order
    num_bankruptcy_matches = models.IntegerField(blank=True, default=None, null=True)
    num_usdc_matches = models.IntegerField(blank=True, default=None, null=True)
    num_state_matches = models.IntegerField(blank=True, default=None, null=True)
    num_state_hv_matches = models.IntegerField(blank=True, default=None, null=True)
    num_patriot_matches = models.IntegerField(blank=True, default=None, null=True)
    name_select_ready = models.CharField(max_length=1, blank=True, default=None, null=True)

    def __str__(self):
        return "Reports generated (b,u,s,p): {} - {} - {}".format(self.bankruptcy_filename, self.usdc_filename,
                                                                  self.state_filename, self.patriot_filename)


class SearchName(models.Model):
    """
    A class for representing the data supplied by a client for a judgment search
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE) # each search name is referenced to a single order
    first_name = models.CharField(max_length=100, blank=True, verbose_name='First Name')
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    suffix = models.CharField(max_length=20, blank=True)
    is_company = models.BooleanField(default=False)
    company_name = models.CharField(max_length=100, blank=True)
    company_type = models.CharField(max_length=20, blank=True) # make a choice
    address1 = models.CharField(max_length=100, blank=True)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip = models.CharField(max_length=10, blank=True)
    search_from = models.DateField()
    search_to = models.DateField()
    name_qualifier = models.CharField(max_length=20, blank=True)
    exact_name_match = models.BooleanField(default=False)
    additional_notes = models.TextField(blank=True)
    report_name = models.CharField(max_length=100, blank=True)
    high_value_search = models.BooleanField(default=False)
    
    def __unicode__(self):
        from collections import defaultdict
        if self.first_name != "":
            name = "{} {} {}".format(self.first_name, self.middle_name, self.last_name)
        elif self.company_name != "":
            name = self.company_name
        return name
    
    def __str__(self):
        from collections import defaultdict
        if self.first_name != "":
            name = "{} {} {}".format(self.first_name, self.middle_name, self.last_name)
        elif self.company_name != "":
            name = self.company_name
        return name

# namesearch models
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.


class NameBase(models.Model):
    """
    A class for representing a forename or surname as provided by IMage Partners
    Specifying an arbitrary column as a primary key since this is a readonly table
    """
    name = models.CharField(max_length=255)
    name_match = models.CharField(max_length=255, primary_key=True)
    score = models.DecimalField(max_digits=10, decimal_places=0)
    deleted = models.CharField(max_length=1)
    nickname = models.CharField(max_length=1)

    class Meta:
        managed = False
        abstract = True
        ordering = ['name']


class Forename(NameBase):
    """
    A class for representing forenames as provided by the name alias database
    """
    class Meta(NameBase.Meta):
        db_table = 'forenames'


class Surname(NameBase):
    """
    A class for representing surnames as provided by the name alias database
    """
    class Meta(NameBase.Meta):
        db_table = 'surnames'


class UserClient(models.Model):
    """
    A custom django user model which provides some additional flexibility not present in the base model
    Much easier to override this at the beginning of the app's development than trying to retrofit something in later on!
    """
    from config.settings.common import AUTH_USER_MODEL as user_model
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(user_model, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.username + " - " + self.client.client_name


class FilteredSearchNameList(models.Model):
    """
    Unused
    """
    name_list = models.TextField()
    date_created = models.DateField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # each filtered name list was generated based on an order
    name_search = models.CharField(max_length=255, db_index=True)  # this is the original name entered by the user


class NameReportHistory(models.Model):
    """
    A model for mapping the xml results created for a report to the xml file stored on the system
    """
    date_created = models.DateField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=255, db_index=True)
    xml_filename = models.CharField(max_length=255, db_index=True)
