from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden

from .models import Announcement, Response, Author, Category, Subscription
from .forms import AnnouncementForm, ResponseForm, EmailVerificationForm
from .filters import AnnouncementFilter, ResponseFilter
from config import settings

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
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
                        subject='Код подтверждения',
                        message=f'Ваш код подтверждения: {verification_code}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
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
    announcement_filter = AnnouncementFilter(request.GET, queryset=Announcement.objects.all().order_by('-created_at'))
    filtered_announcements = announcement_filter.qs
    paginator = Paginator(filtered_announcements, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    next_page = page_obj.number + 1 if page_obj.has_next() else None
    return render(request, 'index.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'next_page': next_page,
        'filter': announcement_filter,
    })


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
@permission_required('board.can_add_response', raise_exception=True)
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
            #     subject='Новый отклик на ваше объявление',
            #     message=f'Вы получили новый отклик: "{response.content}" от {response.author}',
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[announcement.author.authorUser.email],
            # )

            return redirect('announcement_detail', pk=pk)
    else:
        form = ResponseForm()

    return render(request, 'create_response.html', {'form': form, 'announcement': announcement})


# Просмотр откликов на объявления пользователя
@login_required
def my_responses(request):
    announcements = Announcement.objects.filter(author__authorUser=request.user)
    responses = Response.objects.filter(announcement__in=announcements)
    response_filter = ResponseFilter(request.GET, queryset=responses)
    filtered_responses = response_filter.qs
    return render(request, 'my_responses.html', {
        'announcements': announcements,
        'filter': response_filter,  # Передаём фильтр в шаблон
        'responses': filtered_responses,  # Отфильтрованные отклики
    })


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
            #     subject='Ваш отклик был принят!',
            #     message=f'Ваш отклик на объявление "{response.announcement.title}" был принят.',
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[response.author.email],
            # )
        elif action == 'delete':
            response.delete()

    return redirect('my_responses')


def category_list(request):
    categories = Category.objects.all()

    # Проверяем подписку для текущего пользователя на каждую категорию
    for category in categories:
        category.is_subscribed = False
        # Проверяем, есть ли активная подписка на эту категорию
        subscription = Subscription.objects.filter(user=request.user, category=category, is_active=True).first()
        if subscription:
            category.is_subscribed = True

    return render(request, 'category_list.html', {'categories': categories})


def category_announcements(request, pk):
    category = get_object_or_404(Category, id=pk)  # Ищем категорию по ID
    announcements = Announcement.objects.filter(category=category)  # Фильтруем по объекту категории
    paginator = Paginator(announcements, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'category_announcements.html', {
        'category': category,
        'page_obj': page_obj,
    })


# Подписка на категорию
def subscribe_to_category(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)

    category = get_object_or_404(Category, pk=pk)

    # Проверяем, есть ли уже подписка на эту категорию
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        category=category,
        is_active=True
    )
    return redirect('category_list')


# Отписка от категории
def unsubscribe_from_category(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)

    category = get_object_or_404(Category, pk=pk)

    # Получаем подписку, если она есть
    subscription = get_object_or_404(Subscription, user=request.user, category=category)

    subscription.is_active = False  # Делаем подписку неактивной
    subscription.save()

    return redirect('category_list')