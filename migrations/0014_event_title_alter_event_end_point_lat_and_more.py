# Generated by Django 4.2.6 on 2023-11-08 10:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('runner', '0013_event_end_point_lat_event_end_point_lng_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='title',
            field=models.CharField(default='BIG BUNGA UNGA CHUNGA BEEFCAKE SOUP', max_length=60),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='end_point_lat',
            field=models.DecimalField(decimal_places=5, max_digits=10),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_point_lng',
            field=models.DecimalField(decimal_places=5, max_digits=10),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_point_lat',
            field=models.DecimalField(decimal_places=5, max_digits=10),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_point_lng',
            field=models.DecimalField(decimal_places=5, max_digits=10),
        ),
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(default=datetime.time(10, 4, 42, 50933)),
        ),
    ]
