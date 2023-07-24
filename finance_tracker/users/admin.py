from django.contrib import admin
from .models import User, UserProfile, SocialMediaAccount
from django.contrib.auth.admin import UserAdmin


admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__username']

@admin.register(SocialMediaAccount)
class SocialMediaAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'username']
    search_fields = ['user__username', 'platform', 'username']
