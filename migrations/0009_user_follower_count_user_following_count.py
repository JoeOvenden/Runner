# Generated by Django 4.2.6 on 2023-11-02 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('runner', '0008_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='follower_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='following_count',
            field=models.IntegerField(default=0),
        ),
    ]
