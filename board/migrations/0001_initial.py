# Generated by Django 5.1.5 on 2025-01-19 20:13

import django.db.models.deletion
import django_ckeditor_5.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorUser', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('TA', 'Танки'), ('HI', 'Хилы'), ('DD', 'ДД'), ('TO', 'Торговцы'), ('GI', 'Гилдмастеры'), ('KV', 'Квестгиверы'), ('KU', 'Кузнецы'), ('KO', 'Кожевники'), ('ZE', 'Зельевары'), ('MZ', 'Мастера заклинаний')], default='TA', max_length=2)),
                ('title', models.CharField(max_length=255)),
                ('text', django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True, verbose_name='Content')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ann', to='board.author')),
            ],
            options={
                'permissions': [('can_add_announcement', 'Can add announcement'), ('can_change_announcement', 'Can change announcement'), ('can_delete_announcement', 'Can delete announcement')],
            },
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('accepted', models.BooleanField(default=False)),
                ('announcement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='board.announcement')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
