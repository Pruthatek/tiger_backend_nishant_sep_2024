import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from datetime import timedelta

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

    REQUIRED_FIELDS = ['name', 'mobile_no']

    def __str__(self):
        return self.email


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'OTP for {self.user.email}'

    def send_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
        # Send OTP via email (or SMS)
        send_mail(
            'Your OTP Code',
            f'Your OTP is {self.otp}',
            settings.EMAIL_HOST_USER,
            [self.user.email],
            fail_silently=False,
        )

    def is_otp_expired(self):
        """Check if OTP is expired after 1 minute"""
        expiration_time = self.created_at + timedelta(minutes=1)
        return timezone.now() > expiration_time


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


class StoreMaster(models.Model):
    GSTIN_CHOICES = [
        ('I Have GSTIN Number', 'I Have GSTIN Number'),
        ('I Want To Sell Products That Exempt GSTIN', 'I Want To Sell Products That Exempt GSTIN'),
        ('I Don\'t Have GSTIN Number OR I Have Applied For GSTIN', 'I Don\'t Have GSTIN Number OR I Have Applied For GSTIN'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming you are using Django's built-in User model
    business_name = models.CharField(max_length=100, null=True)
    store_name = models.CharField(max_length=100, null=True)
    store_description = models.CharField(max_length=500, null=True)
    store_email = models.EmailField(max_length=100, null=True)
    store_phone = models.CharField(max_length=10, null=True)
    business_type = models.CharField(max_length=200, null=True)
    signature_hash = models.CharField(max_length=255, null=True)
    bill_image_hash = models.CharField(max_length=255, null=True)
    address_line_1 = models.CharField(max_length=150, null=True)
    address_line_2 = models.CharField(max_length=150, blank=True, null=True)
    pin_code = models.IntegerField(null=True)
    city = models.ForeignKey(CityMaster, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(StateMaster, on_delete=models.SET_NULL, null=True)
    bank_name = models.CharField(max_length=100, null=True)
    bank_account_number = models.BigIntegerField(null=True)
    bank_account_holder_name = models.CharField(max_length=100, null=True)
    bank_ifsc_code = models.CharField(max_length=20, null=True)
    bank_account_type = models.CharField(max_length=50, null=True)
    is_gst = models.CharField(max_length=100, choices=GSTIN_CHOICES, null=True)
    pan_no = models.CharField(max_length=20, null=True)
    gst_no = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.store_name
