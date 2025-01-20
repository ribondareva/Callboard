from board.models import Author, Announcement, Response, Category
from django.contrib import admin
from django import forms


admin.site.register(Author)
admin.site.register(Response)
admin.site.register(Category)
admin.site.register(Announcement)

