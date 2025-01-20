from django import forms
from django.contrib.auth.models import Group, Permission

from .models import Announcement, Response
from allauth.account.forms import SignupForm


authors, created = Group.objects.get_or_create(name="authors")
permissions = Permission.objects.filter(content_type__model='announcement')
authors.permissions.add(*permissions)


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        user.groups.add(authors)
        # permission_user = Permission.objects.get(codename='can_add_announcement')
        # user.user_permissions.add(permission_user)
        return user


class EmailVerificationForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['category', 'title', 'text']


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['content']

