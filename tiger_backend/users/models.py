# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone

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
