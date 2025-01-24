import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from board.models import Category

categories = [
    "Танки",
    "Хилы",
    "ДД",
    "Торговцы",
    "Гилдмастеры",
    "Квестгиверы",
    "Кузнецы",
    "Кожевники",
    "Зельевары",
    "Мастера заклинаний"
]

for category_name in categories:
    Category.objects.get_or_create(name=category_name)
    print(f"Category '{category_name}' создана.")

