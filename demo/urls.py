from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('', 
    url('^admin/', include(admin.site.urls)), 
    url('^', include('live_support.urls')),
)

