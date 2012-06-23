from django import forms

from live_support.models import Chat, ChatMessage


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ('name','details',)

class ChatMessageForm(forms.ModelForm):
    message = forms.CharField()
    class Meta:
        model = ChatMessage
        fields = ('message',)
