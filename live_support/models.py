from datetime import datetime
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache


class SupportGroup(models.Model):
    name = models.CharField(_("name"), max_length=255)
    agents = models.ManyToManyField(
        User, blank=True, related_name='agent_support_groups'
    )
    supervisors = models.ManyToManyField(
        User, blank=True, related_name='supervisor_support_groups'
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Support group')
        verbose_name_plural = _('Support groups')


class ChatManager(models.Manager):
    def get_query_set(self):
        return super(ChatManager, self).get_query_set().filter(ended=None)


class Chat(models.Model):
    name = models.CharField(_("name"), max_length=255)
    hash_key = models.CharField(unique=True, max_length=64, null=True,
                                editable=False, blank=True, default=uuid4)
    details = models.TextField(_("question"), blank=True)
    started = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField(null=True, blank=True)
    agents = models.ManyToManyField(User, blank=True, related_name='chats')
    objects = models.Manager()
    active = ChatManager()
    support_group = models.ForeignKey(SupportGroup, null=True, blank=True)

    def __unicode__(self):
        return '%s: %s' % (self.started, self.name)

    def end(self):
        self.ended = datetime.now()
        self.save()

    def is_active(self):
        return cache.get('chat_%s' % self.id, 'inactive')

    class Meta:
        permissions = (
            ("chat_admin", "Chat Admin"),
        )
        verbose_name = _('Chat')
        verbose_name_plural = _('Chats')


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages')
    name = models.CharField(max_length=255, blank=True)
    agent = models.ForeignKey(User, blank=True, null=True)
    message = models.TextField()
    sent = models.DateTimeField(auto_now_add=True)

    def get_name(self):
        if self.agent:
            return self.agent.first_name or self.agent.username
        else:
            return self.name

    def __unicode__(self):
        return '%s: %s' % (self.sent, self.message)

    class Meta:
        verbose_name = _('Chat message')
        verbose_name_plural = _('Chat messages')
