# Generated by Django 4.0.2 on 2022-04-16 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, help_text='Введите текст комментария', verbose_name='Дата публикации комментария'),
        ),
    ]
