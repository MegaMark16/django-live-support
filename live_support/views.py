import json
from django.db import models 
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core import serializers
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.core.cache import cache

from live_support.models import Chat, ChatMessage
from live_support.forms import ChatMessageForm, ChatForm

@permission_required('live_support.chat_admin')
def join_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user.is_authenticated():
        chat.agents.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@permission_required('live_support.chat_admin')
def post_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    last_message_id = request.POST.get('last_message_id')
    message_form = ChatMessageForm(request.POST or None)
    if message_form.is_valid():
        message = message_form.save(commit=False)
        message.chat = chat
        message.agent = request.user
        message.name = message.get_name()
        message.save()
    if request.is_ajax():
        if last_message_id:
            new_messages = chat.messages.filter(id__gt=last_message_id)
        else:
            new_messages = chat.messages.all()
        new_messages_json = serializers.serialize("json", new_messages)
        return HttpResponse(new_messages_json)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
    
@permission_required('live_support.chat_admin')
def end_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.POST.get('end_chat') == 'true':
        chat.end()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@permission_required('live_support.chat_admin')
def get_messages(request):
    chats = {}
    for k, v in request.GET.iteritems():
        alive = True
        messages = ChatMessage.objects.filter(chat_id=k)
        if v:
            messages = ChatMessage.objects.filter(chat_id=k, id__gt=v)

        if not cache.get('chat %s' % k):
            alive = False

        chats[k] = {
            'messages': json.loads(serializers.serialize('json', messages)),
            'alive': alive
        }

    pending_chats = list(Chat.objects.filter(ended=None).exclude(agents=request.user).order_by('-started'))
    pending_chats_list = [{
        'name': chat.name, 
        'url': reverse('live_support.views.join_chat', args=[chat.id]),
    } for chat in pending_chats ]

    output = {
        'chats': chats,
        'pending_chats': pending_chats_list,
    }

    return HttpResponse(json.dumps(output))

def client_get_messages(request, chat_uuid):
    chat = get_object_or_404(Chat, hash_key=chat_uuid)
    cache.set('chat %s' % chat.id, 'active', 20)
    last_message_id = request.GET.get(str(chat.id))
    if last_message_id:
        messages = chat.messages.filter(id__gt=last_message_id)
    else:
        messages = chat.messages.all()

    chats = { 
        chat.id: {
            'messages': json.loads(serializers.serialize('json', messages)), 
        }
    }
    output = {
        'chats': chats,
        'pending_chats': [],
    }
    return HttpResponse(json.dumps(output))

def client_post_message(request, chat_uuid):
    chat = get_object_or_404(Chat, hash_key=chat_uuid)
    last_message_id = request.POST.get('last_message_id')
    message_form = ChatMessageForm(request.POST or None)
    if message_form.is_valid():
        message = message_form.save(commit=False)
        message.chat = chat
        message.name = chat.name
        message.save()
    if last_message_id:
        new_messages = chat.messages.filter(id__gt=last_message_id)
    else:
        new_messages = chat.messages.all()
    new_messages_json = serializers.serialize("json", new_messages)
    return HttpResponse(new_messages_json)

def client_chat(request, chat_uuid):
    chat = get_object_or_404(Chat, hash_key=chat_uuid)
    message_form = ChatMessageForm(request.POST or None)
    if message_form.is_valid():
        message = message_form.save(commit=False)
        message.chat = chat
        message.name = chat.name
        message.save()
        message_form = ChatMessageForm()

    params = {
        'chat': chat,
        'message_form': message_form,
    }
    return render_to_response('live_support/live_support.html', params, context_instance=RequestContext(request))

def start_chat(request):
    chat_form = ChatForm(request.POST or None)
    if chat_form.is_valid():
        chat = chat_form.save()
        print chat.hash_key
        return HttpResponseRedirect(reverse('live_support.views.client_chat', args=[chat.hash_key,]))

    params = {
        'chat_form': chat_form,
    }
    return render_to_response('live_support/start_chat.html', params, context_instance=RequestContext(request))
