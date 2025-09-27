from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile, Meep

admin.site.unregister(User)

class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),  # Önce username, sonra password
        ('Permissions', {'fields': ('is_staff','is_superuser','groups')}),
        ('Important dates', {'fields': ('last_login','date_joined')}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Meep)
