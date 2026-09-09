from django.contrib import admin
from .models import SkillCategory, Skill, VerificationRequirement, UserSkill, SkillVerification


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    prepopulated_fields = {"slug": ("name",)}


class VerificationRequirementInline(admin.StackedInline):
    model = VerificationRequirement
    extra = 0


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "difficulty_level", "difficulty_score", "is_active")
    list_filter = ("category", "difficulty_level", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("prerequisites", "progresses_to")
    inlines = [VerificationRequirementInline]


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ("user", "skill", "status", "started_at", "verified_at")
    list_filter = ("status", "skill__category")
    search_fields = ("user__username", "skill__name")


@admin.register(SkillVerification)
class SkillVerificationAdmin(admin.ModelAdmin):
    """
    Section 17/35 -- the human-review workbench: admins watch the uploaded
    video and flip state to approved/rejected here. Approving does NOT
    happen automatically -- see save_model below, which also syncs the
    related UserSkill status.
    """
    list_display = ("user", "skill", "state", "submitted_at", "reviewer")
    list_filter = ("state", "skill")
    readonly_fields = ("submitted_at",)

    def save_model(self, request, obj, form, change):
        from django.utils import timezone
        from skills.models import UserSkill
        from ranking.services import award_xp

        if change and "state" in form.changed_data:
            obj.reviewer = request.user
            obj.reviewed_at = timezone.now()

        super().save_model(request, obj, form, change)

        user_skill, _ = UserSkill.objects.get_or_create(user=obj.user, skill=obj.skill)
        if obj.state == "approved":
            user_skill.status = "verified"
            user_skill.verified_at = timezone.now()
            user_skill.save()
            award_xp(obj.user, "skill_verified", 200 + obj.skill.difficulty_score * 10, reference_id=obj.skill_id)
        elif obj.state == "rejected":
            user_skill.status = "self_recorded"
            user_skill.save()
