from django import forms
from .models import Announcement, Response

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['category', 'title', 'text']


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['content']
