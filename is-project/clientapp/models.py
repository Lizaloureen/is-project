from django.db import models
from clientapp.constants import APPLICATION_STATUS, ARMED_STATUS, FILETAGS, LICENCE_STATUS


class clientAppModel(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ClientProfile(clientAppModel):
    user = models.OneToOneField('Authapp.User', on_delete=models.CASCADE, related_name="client_profile")
    first_Name = models.CharField(max_length=30)
    last_Name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30,blank=True, null=True)
    ID_Number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)

    
class ClientDocuments(clientAppModel):
    client = models.ForeignKey('clientapp.ClientProfile', on_delete=models.CASCADE, related_name="Client_documents")
    file = models.FileField(upload_to="client/profile")
    tag = models.CharField(max_length=20, choices=FILETAGS)


class ClientApplication(clientAppModel):
    client = models.ForeignKey('clientapp.ClientProfile', on_delete=models.CASCADE, related_name="Client_application")
    next_of_kin_name = models.CharField(max_length=50)
    address = models.TextField()
    region = models.CharField(max_length=50)
    reason = models.TextField()
    type_of_firearm = models.CharField(max_length=50)
    interview_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending", choices=APPLICATION_STATUS)
    good_conduct = models.FileField(upload_to="client/good_conduct", blank=True, null=True)


class ClientLicence(clientAppModel):
    client = models.ForeignKey('clientapp.ClientProfile', on_delete=models.CASCADE, related_name="Client_licence")
    application = models.ForeignKey('clientapp.ClientApplication', on_delete=models.CASCADE, related_name="client_licence_application")
    license_number = models.CharField(max_length=100)
    issued_on = models.DateField()
    expiry_on = models.DateField()
    renewed_on = models.DateField(blank=True, null=True)
    revoked_on = models.DateField(blank=True, null=True)
    interview_on = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=60, default="Active", choices=LICENCE_STATUS)


class LicencePayment(clientAppModel):
    transaction_id = models.CharField(max_length=100, unique=True)
    confirmed = models.BooleanField(default=False)
    confirmed_on = models.DateField(blank=True, null=True)
    licence = models.ForeignKey('clientapp.ClientLicence', on_delete=models.CASCADE, related_name="licence_payment")


class ClientFirearm(clientAppModel):
    client = models.ForeignKey('clientapp.ClientProfile', on_delete=models.CASCADE, related_name="client_firearm")
    firearm = models.ForeignKey('vendorapp.Firearm', on_delete=models.CASCADE, related_name="client_assigned_firearm")
    status = models.CharField(max_length=20, choices=ARMED_STATUS)
    licence = models.ForeignKey('clientapp.ClientLicence', on_delete=models.CASCADE, related_name="client_firearm_licence")

    

