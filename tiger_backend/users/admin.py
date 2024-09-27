from django.contrib import admin
from .models import RoleMaster

# Register RoleMaster in Django Admin
@admin.register(RoleMaster)
class RoleMasterAdmin(admin.ModelAdmin):
    # Fields to be displayed in the list view
    list_display = ['id', 'role_name', 'role_description', 'is_active']
    