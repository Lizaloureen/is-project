"""
Handles project Authentications
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from clientapp.models import ClientProfile
# from fundiApp.models import FundiProfile

# from clientApp.models import UserProfile


USER_TYPE = (
    ("Client", "Client"),
    ("Vendor", "Vendor"),
    ("Admin", "Admin"),
)


# Create your models here.
class MyAccountManager(BaseUserManager):

    def create_user(self, email, user_type, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, user_type=user_type, phone=phone,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, user_type, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, user_type, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)

    phone = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    user_type = models.CharField(max_length=100, choices=USER_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["user_type"]

    objects = MyAccountManager()

    def __str__(self):
        return f"{self.email} | {self.phone}"
        # For checking permissions. to keep it simple all admin have ALL permissions

    def has_perm(self, perm, obj=None):
        return self.is_admin

        # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)

    def has_module_perms(self, app_label):
        return True
    

    def get_client(self):
        client = ClientProfile.objects.filter(user__id = self.id).first()
        if client:
            return client
        else:
            return None
    

    # def get_fundi(self):
    #     fundi = FundiProfile.objects.filter(user__id = self.id).first()
    #     if fundi:
    #         return fundi
    #     else:
    #         return None
    

class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_otp')
    otp = models.IntegerField()
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.otp)