# Generated by Django 4.2.6 on 2023-12-12 14:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('runner', '0025_alter_event_date_alter_event_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='date',
        ),
        migrations.RemoveField(
            model_name='event',
            name='time',
        ),
        migrations.AlterField(
            model_name='event',
            name='date_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]