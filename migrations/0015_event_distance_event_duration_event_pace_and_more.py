# Generated by Django 4.2.6 on 2023-11-08 10:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('runner', '0014_event_title_alter_event_end_point_lat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='distance',
            field=models.DecimalField(decimal_places=1, default=1000, max_digits=7),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='duration',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='pace',
            field=models.TimeField(default=datetime.time(0, 6)),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.time(10, 14, 59, 560185)),
        ),
    ]
