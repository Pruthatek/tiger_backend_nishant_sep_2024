# models.py
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone

User = get_user_model()

class RoleMaster(models.Model):
    id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    role_description = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    name = models.CharField(max_length=100, default="")
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    role = models.ForeignKey(RoleMaster, on_delete=models.SET_NULL, null=True)  # Default role is 'user'
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=None, null=True)

     # Resolve reverse accessor clashes by adding related_name attributes
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Add this line
        blank=True,
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set",  # Add this line
        blank=True,
        help_text="Specific permissions for this user."
    )

    

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'mobile_no']

    def __str__(self):
        return self.email


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'OTP for {self.user.email}'

    def send_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
        # Here, integrate your OTP sending logic (Email/SMS)
        send_mail(
            'Your OTP Code',
            f'Your OTP is {self.otp}',
            settings.EMAIL_HOST_USER,
            [self.user.email],
            fail_silently=False,
        )



class StateMaster(models.Model):
    id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=100)

    def __str__(self):
        return self.state_name


class CityMaster(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.ForeignKey(StateMaster, related_name='cities', on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100)

    def __str__(self):
        return self.city_name
