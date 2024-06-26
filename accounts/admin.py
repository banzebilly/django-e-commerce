
from django.contrib import admin
from .models import Account, UserProfile
from django.utils.html import format_html

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
   
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="30" style="border-radius: 50%;">', obj.profile_picture.url)
        return "(No Image)"

    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Account, AccountAdmin)  #