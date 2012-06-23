from django.conf.urls.defaults import patterns, include, url
from live_support import views

urlpatterns = patterns('', 
    url('^$', views.start_chat), 
    url('^ajax/get_messages/$', views.get_messages), 
    url('^ajax/(?P<chat_id>\d+)/post_message/$', views.post_message), 
    url('^ajax/(?P<chat_id>\d+)/end_chat/$', views.end_chat), 
    url('^ajax/(?P<chat_id>\d+)/join_chat/$', views.join_chat), 
    url('^(?P<chat_uuid>[\w-]+)/get_messages/$', views.client_get_messages), 
    url('^(?P<chat_uuid>[\w-]+)/post_message/$', views.client_post_message), 
    url('^(?P<chat_uuid>[\w-]+)/$', views.client_chat)
)

