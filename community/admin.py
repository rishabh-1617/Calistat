from django.contrib import admin
from .models import Post, Comment, Like, Report, Notification


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "post_type", "created_at", "is_reported", "is_hidden")
    list_filter = ("post_type", "is_reported", "is_hidden")
    search_fields = ("user__username", "content")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Section 46 -- moderation queue."""
    list_display = ("id", "reporter", "post", "status", "created_at")
    list_filter = ("status",)
    actions = ["mark_resolved", "mark_rejected"]

    def mark_resolved(self, request, queryset):
        queryset.update(status="resolved")

    def mark_rejected(self, request, queryset):
        queryset.update(status="rejected")


admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Notification)
