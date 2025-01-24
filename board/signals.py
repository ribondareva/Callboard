from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Response


@receiver(post_save, sender=Response)
def notify_announcement_author(sender, instance, created, **kwargs):
    """
    Уведомление автору объявления о новом отклике.
    """
    if created:  # Проверяем, что отклик только что создан
        announcement = instance.announcement
        send_mail(
            subject='Новый отклик на ваше объявление',
            message=(
                f'Вы получили новый отклик на объявление "{announcement.title}".\n\n'
                f'Текст отклика: {instance.content}\n\n'
                f'Отправлено пользователем: {instance.author.username}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[announcement.author.authorUser.email],
            fail_silently=False,
        )


@receiver(post_save, sender=Response)
def notify_response_author_on_accept(sender, instance, **kwargs):
    """
    Уведомление автору отклика о его принятии.
    """
    if instance.accepted:  # Проверяем, что отклик был принят
        send_mail(
            subject='Ваш отклик был принят',
            message=(
                f'Ваш отклик на объявление "{instance.announcement.title}" был принят.\n\n'
                f'Поздравляем! Свяжитесь с автором объявления для дальнейших действий.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.author.email],
            fail_silently=False,
        )
