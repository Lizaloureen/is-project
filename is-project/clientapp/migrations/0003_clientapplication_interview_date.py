# Generated by Django 5.0.6 on 2024-06-17 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientapp', '0002_clientprofile_user_clientapplication_clientfirearm'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientapplication',
            name='interview_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
