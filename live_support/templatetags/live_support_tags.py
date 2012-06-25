from datetime import timedelta, datetime
from django import template
from django.core.urlresolvers import reverse

from live_support.models import Chat

register = template.Library()

def chat_iframe(context):
    request = context['request']
    iframe_url = reverse('live_support.views.start_chat')
    if request.session.get('chat_hash_key'):
        chat = Chat.objects.filter(hash_key=request.session['chat_hash_key'])
        if chat:
            iframe_url = reverse('live_support.views.client_chat', args=[chat[0].hash_key,])

    return {
        'url': iframe_url,
    }

register.inclusion_tag('live_support/chat_iframe.html', takes_context=True)(chat_iframe)

