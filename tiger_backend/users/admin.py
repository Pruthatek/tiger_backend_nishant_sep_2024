from django.contrib import admin
from .models import *

# Register RoleMaster in Django Admin
@admin.register(RoleMaster)
class RoleMasterAdmin(admin.ModelAdmin):
    # Fields to be displayed in the list view
    list_display = ['id', 'role_name', 'role_description', 'is_active']
    

class OTPAdmin(admin.ModelAdmin):
    list_display = ('otp', 'user_email', 'created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'User Email'

admin.site.register(OTP, OTPAdmin)
