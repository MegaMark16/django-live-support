# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Chat'
        db.create_table('live_support_chat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('hash_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64, blank=True)),
            ('details', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('ended', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('live_support', ['Chat'])

        # Adding M2M table for field agents on 'Chat'
        db.create_table('live_support_chat_agents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('chat', models.ForeignKey(orm['live_support.chat'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('live_support_chat_agents', ['chat_id', 'user_id'])

        # Adding model 'ChatMessage'
        db.create_table('live_support_chatmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chat', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['live_support.Chat'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('live_support', ['ChatMessage'])


    def backwards(self, orm):
        # Deleting model 'Chat'
        db.delete_table('live_support_chat')

        # Removing M2M table for field agents on 'Chat'
        db.delete_table('live_support_chat_agents')

        # Deleting model 'ChatMessage'
        db.delete_table('live_support_chatmessage')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'live_support.chat': {
            'Meta': {'object_name': 'Chat'},
            'agents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'chats'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'details': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ended': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hash_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'live_support.chatmessage': {
            'Meta': {'object_name': 'ChatMessage'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'chat': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['live_support.Chat']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['live_support']
