try:
    from django.conf.urls.defaults import patterns, include, url
except ImportError:
    from django.conf.urls import patterns, include, url
from live_support import views

urlpatterns = patterns('', 
    url('^$', views.start_chat, name='start_chat'), 
    url('^(?P<support_group_id>\d+)/$', views.start_chat, name='start_chat_for_group'),
    url('^ajax/get_messages/$', views.get_messages, name='get_messages'), 
    url('^ajax/(?P<chat_id>\d+)/post_message/$', views.post_message, name='post_message'), 
    url('^ajax/(?P<chat_id>\d+)/end_chat/$', views.end_chat, name='end_chat'), 
    url('^ajax/(?P<chat_id>\d+)/join_chat/$', views.join_chat, name='join_chat'), 
    url('^(?P<chat_uuid>[\w-]+)/end_chat/$', views.client_end_chat, name='client_end_chat'), 
    url('^(?P<chat_uuid>[\w-]+)/get_messages/$', views.client_get_messages, name='client_get_messages'), 
    url('^(?P<chat_uuid>[\w-]+)/post_message/$', views.client_post_message, name='client_post_message'), 
    url('^(?P<chat_uuid>[\w-]+)/$', views.client_chat, name='client_chat'),
)

