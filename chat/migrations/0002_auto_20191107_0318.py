# Generated by Django 2.0.7 on 2019-11-07 03:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='thread',
            old_name='timestamp',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='thread',
            old_name='updated',
            new_name='updated_at',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='first',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='second',
        ),
        migrations.AddField(
            model_name='thread',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='thread',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='thread',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='chat_owner', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='thread',
            name='password',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='thread',
            name='users',
            field=models.ManyToManyField(related_name='chat_users', to=settings.AUTH_USER_MODEL),
        ),
    ]