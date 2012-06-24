from django import forms

from live_support.models import Chat, ChatMessage


class ChatForm(forms.ModelForm):
    details = forms.CharField(widget=forms.Textarea, label='Question')
    class Meta:
        model = Chat
        fields = ('name','details',)

class ChatMessageForm(forms.ModelForm):
    message = forms.CharField()
    class Meta:
        model = ChatMessage
        fields = ('message',)
