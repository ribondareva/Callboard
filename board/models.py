from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django_ckeditor_5.fields import CKEditor5Field


@receiver(user_signed_up)
def set_inactive_user(sender, request, user, **kwargs):
    user.is_active = True
    user.save()


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.authorUser.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories', blank=True)

    def __str__(self):
        return self.name


class Announcement(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='ann')
    title = models.CharField(max_length=255)
    text = CKEditor5Field(
        'Content',
        config_name='default',  # Ссылка на конфигурацию в settings.py
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ('can_add_announcement', 'Can add announcement'),
            ('can_change_announcement', 'Can change announcement'),
            ('can_delete_announcement', 'Can delete announcement'),
        ]

    def __str__(self):
        return self.title


class Response(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='responses')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ('can_add_response', 'Can add response'),
            ('can_delete_response', 'Can delete response'),
        ]

    def __str__(self):
        return f"Response by {self.author} to {self.announcement.title}"

    def get_responses_count(self):
        return self.responses.count()


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"