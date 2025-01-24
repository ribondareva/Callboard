from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница с объявлениями
    path('announcement/<int:pk>/', views.announcement_detail, name='announcement_detail'),  # Детали объявления
    path('announcement/create/', views.create_announcement, name='create_announcement'),  # Создание объявления
    path('announcement/<int:pk>/edit/', views.edit_announcement, name='edit_announcement'),  # Редактирование объявления
    path('announcement/<int:pk>/delete/', views.delete_announcement, name='delete_announcement'),  # Удаление объявления
    path('announcement/<int:pk>/response/', views.create_response, name='create_response'),  # Создание отклика
    path('responses/', views.my_responses, name='my_responses'),  # Отклики на свои объявления
    path('response/<int:pk>/manage/', views.manage_response, name='manage_response'),  # Управление откликом
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_announcements, name='category_announcements'),
    path('categories/<int:pk>/subscribe/', views.subscribe_to_category, name='subscribe_to_category'),  # Подписка
    path('categories/<int:pk>/unsubscribe/', views.unsubscribe_from_category, name='unsubscribe_from_category'),
]
