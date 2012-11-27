from django import template
from django.conf import settings
from django.core.cache import cache
from datetime import timedelta, datetime
from django.core.urlresolvers import reverse

from live_support.models import Chat

register = template.Library()

def chat_iframe(context, support_group_id=None):
    request = context['request']
    # The default url is the Start Chat page
    if support_group_id:
        iframe_url = reverse('live_support.views.start_chat', args=[support_group_id,])
        cache_key = 'admin_active_%s' % support_group_id
    else:
        iframe_url = reverse('live_support.views.start_chat')
        cache_key = 'admin_active'
    if request.session.get('chat_hash_key'):
        chat = Chat.objects.filter(hash_key=request.session['chat_hash_key'])
        if chat and not chat[0].ended:
            # If the user currently has an active chat session and it has not
            # ended, display that instead.
            iframe_url = reverse('live_support.views.client_chat', args=[chat[0].hash_key])

    return {
        'STATIC_URL': settings.STATIC_URL,
        'url': iframe_url,
        'admin_active': cache.get(cache_key, False),
        'request': request,
    }

register.inclusion_tag('live_support/chat_iframe.html', takes_context=True)(chat_iframe)

