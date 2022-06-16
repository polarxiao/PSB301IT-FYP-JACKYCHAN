from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('%s' % settings.URL_PREFIX, include('check_in.urls')),
    path('%s' % settings.URL_PREFIX, include('registration.urls')),
    path('%s' % settings.URL_PREFIX, include('core.urls')),
    
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
