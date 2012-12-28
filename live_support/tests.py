import unittest

from django.test import TestCase
from django.test.client import Client, ClientHandler
from django.core.urlresolvers import reverse
from django.core.cache import cache
from models import Chat

class ClientTests(TestCase):
    urls = 'live_support.urls'
    fixtures = ['live_support/fixtures/users.json',]

    def setUp(self):
        pass

    def test_start_chat(self):
        # Login and call get_messages to set the admin_active cache
        login = self.client.login(username='test', password='test')
        self.client.get(reverse('get_messages'))

        resp = self.client.post(reverse('start_chat'), {
            'name': 'Test Name',
            'details': 'Test Details'
        })
        self.assertEqual(resp.status_code, 302)
        resp2 = self.client.get(resp['location'])
        self.assertEqual(resp2.status_code, 200)
        self.assertTrue(resp2.context['chat'].hash_key in resp['location'])

    def test_leave_message(self):
        # Make sure no admins are logged in
        cache.set('admin_active', None)
        # Because no admin is logged in calling start_chat just leaves
        # a message and returns a thank you response
        resp = self.client.post(reverse('start_chat'), {
            'name': 'Test Name',
            'details': 'Test Message'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, 'Thank you for contacting us')

    def test_get_messages_prompts_login(self):
        # If you aren't logged in you cannot call get_messages without
        # a chat hash_key or you will be directed to log in
        resp = self.client.get(reverse('get_messages'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp['location'])

    def test_get_messages_with_hash_key_returns_messages(self):
        chat = Chat.objects.create(name='Test Chat', details='Details')
        chat.messages.create(name=chat.name, message='new message text')
        resp = self.client.get(reverse('client_get_messages', args=[chat.hash_key]))
        self.assertTrue('new message text' in resp.content)

    def test_get_latest_message(self):
        chat = Chat.objects.create(name='Test Chat', details='Details')
        message1 = chat.messages.create(name=chat.name, message='message one')
        message2 = chat.messages.create(name=chat.name, message='message two')
        url = reverse('client_get_messages', args=[chat.hash_key])
        resp = self.client.get('%s?%s=%s' % (url, chat.id, message1.id))
        self.assertIn('two', resp.content)
        self.assertNotIn('one', resp.content)


class AdminTests(TestCase):
    urls = 'live_support.urls'
    fixtures = ['live_support/fixtures/users.json',]

    def setUp(self):
        pass

    def test_get_all_messages(self):
        login = self.client.login(username='test', password='test')
        chat = Chat.objects.create(name='Test Chat', details='Details')
        chat.messages.create(name=chat.name, message='new message text')
        url = reverse('get_messages')
        resp = self.client.get('%s?%s=0' % (url, chat.id))
        self.assertTrue('new message text' in resp.content)

    def test_getting_messages_with_invalid_args(self):
        login = self.client.login(username='test', password='test')
        chat = Chat.objects.create(name='Test Chat', details='Details')
        message1 = chat.messages.create(name=chat.name, message='message one')
        message2 = chat.messages.create(name=chat.name, message='message two')
        url = reverse('get_messages')
        resp = self.client.get('%s?bad=good&%s=%s' % (url, chat.id, message1.id))
        self.assertIn('two', resp.content)
        self.assertNotIn('one', resp.content)

    def test_send_admin_message(self):
        login = self.client.login(username='test', password='test')
        chat = Chat.objects.create(name='Test Chat', details='Details')
        resp = self.client.post(reverse('post_message', args=[chat.id]), 
                         { 'message': 'admin test message'},
                         **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertIn('admin test message', resp.content)
