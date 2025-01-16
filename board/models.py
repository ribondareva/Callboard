from django.contrib.auth.models import User
from django.db import models


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.authorUser.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('TA', 'Танки'),
        ('HI', 'Хилы'),
        ('DD', 'ДД'),
        ('TO', 'Торговцы'),
        ('GI', 'Гилдмастеры'),
        ('KV', 'Квестгиверы'),
        ('KU', 'Кузнецы'),
        ('KO', 'Кожевники'),
        ('ZE', 'Зельевары'),
        ('MZ', 'Мастера заклинаний'),
    ]
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default='TA')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='ann')
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Response(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='responses')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Response by {self.author} to {self.announcement.title}"

    def get_responses_count(self):
        return self.responses.count()


