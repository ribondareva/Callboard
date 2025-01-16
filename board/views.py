from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from .models import Announcement, Response, Author, Category
from .forms import AnnouncementForm, ResponseForm
from allauth.account.forms import SignupForm
from django import forms


# Главная страница
def index(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'announcements': announcements})


# Просмотр одного объявления
def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    responses = announcement.responses.all()
    return render(request, 'announcement_detail.html', {
        'announcement': announcement,
        'responses': responses
    })


# Создание объявления
@login_required
def create_announcement(request):
    if not hasattr(request.user, 'author'):
        Author.objects.create(authorUser=request.user)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user.author
            announcement.save()
            return redirect('index')
    else:
        form = AnnouncementForm()

    return render(request, 'create_announcement.html', {'form': form})


# Редактирование объявления
@login_required
def edit_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.user != announcement.author.authorUser:
        return HttpResponseForbidden("Вы не можете редактировать это объявление.")

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            return redirect('announcement_detail', pk=pk)
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, 'edit_announcement.html', {'form': form, 'announcement': announcement})


# Удаление объявления
@login_required
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.user != announcement.author.authorUser:
        return HttpResponseForbidden("Вы не можете удалить это объявление.")

    announcement.delete()
    return redirect('index')


# Создание отклика
@login_required
def create_response(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.author = request.user
            response.announcement = announcement
            response.save()

            # Отправка уведомления о новом отклике
            # send_mail(
            #     'Новый отклик на ваше объявление',
            #     f'Вы получили новый отклик: {response.content}',
            #     'from@example.com',
            #     [announcement.author.authorUser.email],
            # )

            return redirect('announcement_detail', pk=pk)
    else:
        form = ResponseForm()

    return render(request, 'create_response.html', {'form': form, 'announcement': announcement})


# Просмотр откликов на объявления пользователя
@login_required
def my_responses(request):
    announcements = Announcement.objects.filter(author__authorUser=request.user)
    return render(request, 'my_responses.html', {'announcements': announcements})


# Управление статусом отклика
@login_required
def manage_response(request, pk):
    response = get_object_or_404(Response, pk=pk)

    if request.user != response.announcement.author.authorUser:
        return HttpResponseForbidden("Вы не можете управлять этим откликом.")

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            response.accepted = True
            response.save()

            # Уведомление автору отклика
            # send_mail(
            #     'Ваш отклик был принят!',
            #     f'Ваш отклик на объявление "{response.announcement.title}" был принят.',
            #     'from@example.com',
            #     [response.author.email],
            # )
        elif action == 'delete':
            response.delete()

    return redirect('my_responses')


