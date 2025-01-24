from django.utils.timezone import now
from django.utils.html import strip_tags
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Subscription, Announcement
from config import settings
from datetime import timedelta
from django.urls import reverse

@shared_task
def send_daily_newsletter():
    subscriptions = Subscription.objects.filter(is_active=True)

    for subscription in subscriptions:
        category = subscription.category
        user = subscription.user

        # Фильтруем объявления, созданные за последние сутки
        last_day = now() - timedelta(days=1)
        new_announcements = Announcement.objects.filter(category=category, created_at__gte=last_day)

        if not new_announcements.exists():
            continue

        # Генерация HTML-контента письма
        subject = f"Новые объявления в категории {category.name}"

        # Формируем данные для шаблона
        announcements_with_links = [
            {
                'title': announcement.title,
                'text': strip_tags(announcement.text)[:200],  # Очищаем текст от HTML
                'link': f"{settings.SITE_URL}{reverse('announcement_detail', args=[announcement.id])}"
            }
            for announcement in new_announcements
        ]

        html_content = render_to_string('daily_newsletter.html', {
            'category': category,
            'user': user,
            'announcements': announcements_with_links,
        })

        # Генерация текстового контента письма
        text_content = f"Здравствуйте, {user.username}!\n\n"
        text_content += f"Новые объявления в категории {category.name}:\n\n"
        for announcement in announcements_with_links:
            text_content += f"- {announcement['title']}\n{announcement['text']}...\n"
            text_content += f"Подробнее: {announcement['link']}\n\n"
        text_content += "С уважением,\nКоманда нашего сайта."

        # Создаем объект письма
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")

        # Отправляем письмо
        email.send()
