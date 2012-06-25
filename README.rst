django-live-support
=================
A live support chat app for django that lets you chat with visitors to your
site through the Django Admin interface.

Dependancies
============

- django (tested with 1.3)

Getting Started
=============

To get started simply install using ``pip``:
::
    pip install django-live-support

Add ``live_support`` to your installed apps and ``syncdb`` (or migrate, if 
you have south installed).

Your installed apps should look something like this:
::
	INSTALLED_APPS = (
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'django.contrib.messages',
	    'django.contrib.admin',
	    'live_support',
	)

Add ``live_support.urls`` to your urls.py, like so:
::
    from django.conf.urls.defaults import patterns, include, url

    from django.contrib import admin
    admin.autodiscover()

    urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^support/', include('live_support.urls')),
    )

	
Usage
=============

You can either override the template for the `start_chat` 
(live_support/start_chat.html) and `client_chat` 
(live_support/live_support.html) views and just point users to the root 
of the live_support app as defined in your urls.py file, or you can drop
the `{% chat_iframe %}` templatetag into your base template, which will
render the chat sidebar (which pops out into a chat window) on every
page.

