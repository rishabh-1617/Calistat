from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AthleteProfile


@admin.register(User)
class CalisfyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Calisfy", {"fields": ("experience_level", "primary_goal", "email_verified")}),
    )
    list_display = ("username", "email", "experience_level", "is_active", "date_joined")


@admin.register(AthleteProfile)
class AthleteProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "country", "follower_count", "created_at")
    search_fields = ("user__username", "display_name")
