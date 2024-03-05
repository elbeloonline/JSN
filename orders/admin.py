from django.contrib import admin
from django.http import HttpResponseForbidden

from .models import Client, Order, SearchName, Forename, Surname, UserClient


class ClientAdmin(admin.ModelAdmin):
    fields = ['client_name', 'email', 'phone', 'client_id', 'addr1', 'addr2', 'city', 'state', 'zip']


class OrderAdmin(admin.ModelAdmin):
    list_display = ('title_number', 'date_ordered', 'order_method')
    list_filter = ['created']
    search_fields = ['title_number']
    list_per_page = 20


class ForenameAdmin(admin.ModelAdmin):
    """
    Hide change attributes to make this table read-only in the admin screen
    http://stackoverflow.com/questions/1618728/disable-link-to-edit-object-in-djangos-admin-display-list-only
    """
    actions = None

    list_display = ('name', 'name_match', 'score')
    search_fields = ['name', 'name_match']
    list_per_page = 20

    def __init__(self, *args, **kwargs):
        super(ForenameAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SurnameAdmin(admin.ModelAdmin):
    actions = None

    list_display = ('name', 'name_match', 'score')
    search_fields = ['name', 'name_match']
    list_per_page = 20

    def __init__(self, *args, **kwargs):
        super(SurnameAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserClientAdmin(admin.ModelAdmin):
    pass


# Register your models here.
admin.site.register(Client, ClientAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(SearchName)
admin.site.register(Forename, ForenameAdmin)
admin.site.register(Surname, SurnameAdmin)
admin.site.register(UserClient, UserClientAdmin)
# admin.site.register(UserClient)
