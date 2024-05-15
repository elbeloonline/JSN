# -*- coding: utf-8 -*-


from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from django.conf import settings # new
from  django.conf.urls.static import static #new

# fix problem with admin section being inacessible on production
# https://github.com/pydanny/cookiecutter-django/issues/162
admin.autodiscover()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include(('jsnetwork_project.users.urls','users'), namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^orders/', include(('orders.urls', 'orders'), namespace='orders')),
    url(r'^nameviewer/', include(('nameviewer.urls', 'nameviewer'), namespace='nameviewer')),
    url(r'^usermgmt/', include(('usermgmt.urls', 'usermgmt'), namespace='usermgmt')),
    url(r'^pdftools/', include(('pdftools.urls', 'pdftools'), namespace='pdftools')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)

# set properties on the admin site - no need to define a custom template any more
# http://stackoverflow.com/questions/4938491/django-admin-change-header-django-administration-text
admin.site.site_header = 'Judgment Search Network Administration'
admin.site.site_title = 'JSN Admin'
