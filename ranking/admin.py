from django.contrib import admin
from .models import XPTransaction, Rank, UserRank, Achievement, UserAchievement


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    """Section 24/35 -- configure rank thresholds without touching code."""
    list_display = ("name", "order", "min_xp", "min_verified_skills", "min_skill_score", "badge_color")
    ordering = ("order",)


@admin.register(XPTransaction)
class XPTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "source", "amount", "created_at")
    list_filter = ("source",)
    search_fields = ("user__username",)


@admin.register(UserRank)
class UserRankAdmin(admin.ModelAdmin):
    list_display = ("user", "current_rank", "cached_xp", "cached_verified_skill_count", "last_calculated")
    readonly_fields = ("last_calculated",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "xp_reward")


admin.site.register(UserAchievement)
