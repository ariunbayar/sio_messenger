# Generated by Django 2.0.7 on 2019-11-13 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_userchannel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userchannel',
            name='channel_name',
            field=models.CharField(db_index=True, max_length=64),
        ),
    ]
