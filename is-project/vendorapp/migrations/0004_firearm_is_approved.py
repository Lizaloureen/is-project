# Generated by Django 5.0.6 on 2024-07-03 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendorapp', '0003_firearm_date_of_manufacture_firearm_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='firearm',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]