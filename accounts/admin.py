from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User    
# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets =UserAdmin.fieldsets + (
       ('Additional Information', {
            "fields": ('phone',),
        }),
    )
add_fieldsets = UserAdmin.add_fieldsets + (
    ('Additional Information', {
        "fields": ('phone',),
    }),
)
    