# Generated by Django 4.2.6 on 2023-12-12 14:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('runner', '0024_alter_event_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(default=datetime.date(2023, 12, 12)),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.time(14, 8, 51, 273613)),
        ),
    ]