# Generated by Django 2.0.7 on 2019-11-07 04:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20191107_0318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='users',
            field=models.ManyToManyField(blank=True, null=True, related_name='chat_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
