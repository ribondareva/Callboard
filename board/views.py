from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from .models import Announcement, Response, Author
from .forms import AnnouncementForm, ResponseForm, EmailVerificationForm

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import random


# Функция для генерации кода подтверждения
def generate_verification_code():
    return str(random.randint(100000, 999999))  # Генерация 6-значного кода


# Форма регистрации
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect('send_verification_email')  # Переход на страницу отправки email с кодом
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


# Функция для отправки кода подтверждения на email
def send_verification_email(request):
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                try:
                    # Генерация кода подтверждения
                    verification_code = generate_verification_code()

                    # Отправка кода на email
                    send_mail(
                        'Код подтверждения',
                        f'Ваш код подтверждения: {verification_code}',
                        'mnikitina2001@gmail.com',
                        [email],
                        fail_silently=False,
                    )

                    # Сохраняем код в сессии
                    request.session['verification_code'] = verification_code
                    request.session['email'] = email

                    messages.success(request, "Код подтверждения был отправлен на ваш email.")
                    return redirect('verify_code')  # Переход на страницу для ввода кода
                except Exception as e:
                    messages.error(request, f"Ошибка отправки email: {e}")
                    return redirect('send_verification_email')  # Переход на страницу отправки email
    else:
        form = EmailVerificationForm()

    return render(request, 'account/email/send_verification_email.html', {'form': form})


# Форма для ввода кода подтверждения
def verify_code(request):
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')

        # Получаем код из сессии
        stored_code = request.session.get('verification_code')

        if entered_code == stored_code:
            # Если коды совпадают, подтверждаем email
            email = request.session.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                user.is_active = True  # Активируем пользователя
                user.save()
                messages.success(request, "Ваш email успешно подтвержден!")
                return redirect('login')  # Переход на страницу логина
            else:
                messages.error(request, "Пользователь не найден.")
                return redirect('verify_code')
        else:
            messages.error(request, "Неверный код подтверждения.")
            return redirect('verify_code')  # Переход на страницу ввода кода

    return render(request, 'account/email/verify_code.html')


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
@permission_required('board.can_add_announcement', raise_exception=True)
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
@permission_required('board.can_change_announcement', raise_exception=True)
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
@permission_required('board.can_delete_announcement', raise_exception=True)
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
            #     'mnikitina2001@gmail.com',
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


