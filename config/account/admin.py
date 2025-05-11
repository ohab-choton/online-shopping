from django.contrib import admin
from .models import UserAccount
from django.contrib.auth.admin import UserAdmin


class UserAccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_filter =('is_active', 'is_staff', 'is_superuser')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    fieldsets = ()

# Register your models here.
admin.site.register(UserAccount, UserAccountAdmin)
