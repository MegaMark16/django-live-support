from django.contrib import admin
from django.conf import settings

from live_support.models import Chat, ChatMessage

class ChatAdmin(admin.ModelAdmin):
    list_display = ('id','name','started',)
    list_display_links = ('id','name',)
    list_filter = ('started',)
    
    class Media:
        js = (
            "live_support/js/live_support_admin.js",
            "live_support/js/live_support.js",
        )
        css = {
            'all': ('live_support/css/live_support.css',),
        }
    
    def changelist_view(self, request, extra_context=None):
        pending_chats = Chat.objects.filter(ended=None, agents=None).order_by('-started')
        active_chats = Chat.objects.filter(ended=None).filter(agents=request.user)
        c = {
            'pending_chats': pending_chats,
            'active_chats': active_chats,
        }
        print "ACTIVE CHATS: %s" % active_chats
        return super(ChatAdmin, self).changelist_view(request, extra_context=c)


admin.site.register(Chat, ChatAdmin)
admin.site.register(ChatMessage)


