# Generated by Django 4.2.6 on 2023-12-11 09:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('runner', '0020_alter_event_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.time(9, 14, 14, 302855)),
        ),
    ]
