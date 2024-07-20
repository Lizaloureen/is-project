from django.db import models

from clientapp.models import ClientLicence
from vendorapp.constants import FIREARM_CHOICES, FIREARM_MANUFACTURERS, FIREARM_STATUS



class vendorAppModel(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VendorProfile(vendorAppModel):
    user = models.OneToOneField('Authapp.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    company_address = models.CharField(max_length=100)
    company_email = models.EmailField()
    company_phone = models.CharField(max_length=15)
    company_website = models.URLField(blank=True, null=True)
    company_logo = models.ImageField(upload_to='vendor_logo/')


class Firearm(vendorAppModel):
    name = models.CharField(max_length=100)
    firearm_type = models.CharField(max_length=50, choices=FIREARM_CHOICES)
    serial_number = models.CharField(max_length=50)
    date_of_manufacture = models.DateField()
    manufacturer = models.CharField(max_length=50, choices=FIREARM_MANUFACTURERS)
    vendor = models.ForeignKey('vendorapp.VendorProfile', on_delete=models.CASCADE, related_name="vendor_firearm")
    image = models.FileField(upload_to='firearm_images/')
    description = models.TextField()
    status = models.CharField(max_length=50, default='Available', choices=FIREARM_STATUS)
    is_approved = models.BooleanField(default=True)


def approve_firearms():
    fire = Firearm.objects.all()
    for f in fire:
        f.is_approved = True
        f.save()
        print(f.name)

    print('done')

def expire_all_licences():
    fire = ClientLicence.objects.all()
    for f in fire:
        f.status = 'Expired'
        f.save()
        print(f.client)

    print('done')