import django_filters
from django.contrib.auth.models import User
from django_filters import FilterSet
from .models import Announcement, Author, Response, Category
from django.forms import DateTimeInput, Select


class AnnouncementFilter(FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label="Название")
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        empty_label="Все категории",
        label="Категория"
    )

    author = django_filters.ModelChoiceFilter(
        queryset=Author.objects.all(),
        empty_label="Все авторы",
        label="Автор",
        to_field_name='authorUser',
    )
    created_at = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label="Дата создания",
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        )
    )
    class Meta:
        model = Announcement
        fields = ['title', 'category', 'author', 'created_at']


class ResponseFilter(FilterSet):
    announcement = django_filters.CharFilter(
        field_name='announcement__title',  # Фильтрация по названию объявления
        lookup_expr='icontains',
        label="Название объявления"
    )
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),  # Список всех пользователей
        empty_label="Все авторы",  # Опция для всех авторов
        label="Имя автора"
    )
    accepted = django_filters.BooleanFilter(
        field_name='accepted',
        label="Принят или нет",
        widget=Select(choices=[
            ('', 'Неизвестно'),  # значение "Неизвестно"
            (True, 'Да'),  # Значение для True
            (False, 'Нет'),  # Значение для False
        ]),
    )
    class Meta:
        model = Response
        fields = ['announcement', 'author', 'accepted']
