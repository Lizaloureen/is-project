# Generated by Django 5.0.6 on 2024-06-30 16:30

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendorapp', '0002_vendorprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='firearm',
            name='date_of_manufacture',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='firearm',
            name='description',
            field=models.TextField(default='n/a'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='firearm',
            name='image',
            field=models.FileField(default='None', upload_to='firearm_images/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='firearm',
            name='manufacturer',
            field=models.CharField(choices=[('kofc', 'kofc'), ('Kenya Bunduki', 'Kenya Bunduki'), ('Nsi', 'Nsi')], default='na', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='firearm',
            name='serial_number',
            field=models.CharField(default='na', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='firearm',
            name='status',
            field=models.CharField(choices=[('Available', 'Available'), ('Issued', 'Issued'), ('Destroyed', 'Destroyed')], default='Available', max_length=50),
        ),
        migrations.AddField(
            model_name='firearm',
            name='vendor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='vendor_firearm', to='vendorapp.vendorprofile'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='firearm',
            name='firearm_type',
            field=models.CharField(choices=[('PISTOL', 'PISTOL'), ('RIFLE', 'Rifle'), ('SHOTGUN', 'Shotgun'), ('SEMIAUTO', 'Semi-Automatic'), ('BOLT_ACTION', 'Bolt Action'), ('REVOLVER', 'Revolver'), ('SUBMACHINE_GUN', 'Submachine Gun'), ('ASSAULT_RIFLE', 'Assault Rifle'), ('SNIPER_RIFLE', 'Sniper Rifle'), ('OTHER', 'Other')], max_length=50),
        ),
    ]