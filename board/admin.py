from board.models import Author, Announcement, Response, Category, Subscription
from django.contrib import admin


admin.site.register(Author)
admin.site.register(Response)
admin.site.register(Category)
admin.site.register(Announcement)
admin.site.register(Subscription)
