# Generated by Django 4.2.6 on 2023-11-07 15:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('runner', '0012_remove_event_event_datetime_event_date_event_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='end_point_lat',
            field=models.DecimalField(decimal_places=8, default=-1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='end_point_lng',
            field=models.DecimalField(decimal_places=8, default=-1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='start_point_lat',
            field=models.DecimalField(decimal_places=8, default=-1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='start_point_lng',
            field=models.DecimalField(decimal_places=8, default=-1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.time(15, 7, 26, 459684)),
        ),
    ]
