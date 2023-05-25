from django.contrib import admin
from .models import User, UserProfile, SocialMediaAccount

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'date_of_birth']
    search_fields = ['username', 'email', 'phone_number']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__username']

@admin.register(SocialMediaAccount)
class SocialMediaAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'username']
    search_fields = ['user__username', 'platform', 'username']
