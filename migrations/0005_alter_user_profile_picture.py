# Generated by Django 4.2.6 on 2023-11-02 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('runner', '0004_alter_user_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, upload_to='profile_pics'),
        ),
    ]