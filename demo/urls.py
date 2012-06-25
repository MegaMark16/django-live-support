from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('', 
    url('^admin/', include(admin.site.urls)), 
    url('^chat/$', direct_to_template, {
        'template': 'chat.html'
    }),
    url('^', include('live_support.urls')),
)

