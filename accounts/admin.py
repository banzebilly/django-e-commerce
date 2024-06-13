
from django.contrib import admin
from .models import Account
#in order to change the way password is showing in the admin panal 
from  django.contrib.auth.admin import UserAdmin
# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)
    
    
    list_filter = ('is_active',)  # Keep only is_active in list_filter
    filter_horizontal = ()  # Remove filter_horizontal completely
    fieldsets = ()
   
    

admin.site.register(Account, AccountAdmin)
