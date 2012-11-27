try:
    import simplejson as json
except ImportError:
    import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.core.cache import cache
from django.utils.html import escape

from live_support.models import Chat, ChatMessage, SupportGroup
from live_support.forms import ChatMessageForm, ChatForm


@permission_required('live_support.chat_admin')
def join_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user.is_authenticated():
        chat.agents.add(request.user)
        message = ChatMessage()
        name = request.user.first_name or request.user.username
        message.message = '%s has joined the chat' % name
        chat.messages.add(message)
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
        new_message_list = []
        for message in new_messages:
            new_message_list.append({
                'name': escape(message.name),
                'message': escape(message.message),
                'pk': message.pk,
                'chat': chat.id,
            })
        return HttpResponse(json.dumps(new_message_list))
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@permission_required('live_support.chat_admin')
def end_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    message = ChatMessage()
    name = request.user.first_name or request.user.username
    message.message = '%s has left the chat.  This chat has ended.' % name
    chat.messages.add(message)
    if request.POST.get('end_chat') == 'true':
        chat.end()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@permission_required('live_support.chat_admin')
def get_messages(request):
    """
        For each chat id passed in via querystring, get the last message id and
        query for any new messages for that chat session. Also include all
        pending chat sessions.
    """
    user = request.user
    chats = {}
    for k, v in request.GET.iteritems():
        alive = True
        messages = ChatMessage.objects.filter(chat__id=k)
        if v:
            messages = ChatMessage.objects.filter(chat__id=k, id__gt=v)

        # Check to see if the end user has recently checked for new messages
        # for this chat session by checking for the cache entry using the
        # chat id.  If they haven't asked for new messages in the past 30
        # seconds they probably navigated away or closed the window.
        if not cache.get('chat_%s' % k):
            alive = False

        message_list = []
        for message in messages:
            message_list.append({
                'name': escape(message.name),
                'message': escape(message.message),
                'pk': message.pk,
            })
        chats[k] = {
            'messages': message_list,
            'alive': alive
        }

    # Get the list of pending chat sessions, and for each one get a url for
    # joining that chat session.
    pending_chats = Chat.objects.filter(ended=None)\
                         .exclude(agents=user)\
                         .order_by('-started')
    groups = SupportGroup.objects.filter(
        Q(supervisors=user) | 
        Q(agents=user)
    )
    if groups:
        pending_chats = pending_chats.filter(support_group__in=groups)

    pending_chats = list(pending_chats)
    pending_chats_list = [{
        'name': escape(chat.name),
        'url': reverse('live_support.views.join_chat', args=[chat.id]),
        'active': chat.is_active(),
    } for chat in pending_chats]

    output = {
        'chats': chats,
        'pending_chats': pending_chats_list,
    }
    if groups:
        for group in groups:
            cache.set('admin_active_%s' % group.id, True, 20)
    else:
        cache.set('admin_active', True, 20)
    # Dump the whole thing to json and return it to the browser.
    return HttpResponse(json.dumps(output))


def client_get_messages(request, chat_uuid):
    """
        Get any new chat messages for the chat current chat session (based on
        hash_key) and return them to the browser as json.
    """
    chat = get_object_or_404(Chat, hash_key=chat_uuid)
    cache.set('chat_%s' % chat.id, 'active', 20)
    last_message_id = request.GET.get(str(chat.id))
    if last_message_id:
        messages = chat.messages.filter(id__gt=last_message_id)
    else:
        messages = chat.messages.all()

    message_list = []
    for message in messages:
        message_list.append({
            'name': escape(message.name),
            'message': escape(message.message),
            'pk': message.pk,
        })
    chats = {
        chat.id: {
            'messages': message_list,
        }
    }
    output = {
        'chats': chats,
        'pending_chats': [],
    }
    return HttpResponse(json.dumps(output))


def client_end_chat(request, chat_uuid):
    chat = get_object_or_404(Chat, hash_key=chat_uuid)
    if request.POST.get('end_chat') == 'true':
        message = ChatMessage()
        name = request.POST.get('name', 'the user')
        message.message = '%s has left the chat.  This chat has ended.' % name
        chat.messages.add(message)
        chat.end()
    return HttpResponse('Thank you')


def client_post_message(request, chat_uuid):
    """
        Post the message from the end user and return a list of any
        new messages based on the last_messag_id specified.
    """
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
    new_message_list = []
    for message in new_messages:
        new_message_list.append({
            'name': escape(message.name),
            'message': escape(message.message),
            'pk': message.pk,
            'chat': chat.id,
        })
    return HttpResponse(json.dumps(new_message_list))


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
    return render_to_response('live_support/live_support.html', params,
                              context_instance=RequestContext(request))


def start_chat(request, support_group_id=None):
    chat_form = ChatForm(request.POST or None)
    admin_active = cache.get('admin_active', False)
    if support_group_id:
        admin_active = cache.get('admin_active_%s' % support_group_id, False)
    if chat_form.is_valid():
        chat = chat_form.save(commit=False)
        chat.support_group_id = support_group_id
        chat.save()
        if admin_active:
            request.session['chat_hash_key'] = chat.hash_key
            return HttpResponseRedirect(reverse(
                'live_support.views.client_chat',
                args=[chat.hash_key, ])
            )
        else:
            return HttpResponse('Thank you for contacting us')
    params = {
        'chat_form': chat_form,
        'admin_active': admin_active,
    }
    return render_to_response('live_support/start_chat.html', params,
                              context_instance=RequestContext(request))
