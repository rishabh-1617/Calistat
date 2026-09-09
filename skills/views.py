from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages

from .models import Skill, SkillCategory, UserSkill, SkillVerification


def skill_list(request):
    """Section 9/10 -- browsable skill tree grouped by category."""
    categories = SkillCategory.objects.prefetch_related("skills")
    user_status = {}
    if request.user.is_authenticated:
        user_status = {
            us.skill_id: us.status
            for us in UserSkill.objects.filter(user=request.user)
        }
    return render(
        request, "skills/skill_list.html",
        {"categories": categories, "user_status": user_status},
    )


def skill_detail(request, slug):
    """Section 10 -- dedicated skill page with progression/prerequisites."""
    skill = get_object_or_404(Skill, slug=slug, is_active=True)
    user_skill = None
    if request.user.is_authenticated:
        user_skill, _ = UserSkill.objects.get_or_create(user=request.user, skill=skill)
    context = {
        "skill": skill,
        "user_skill": user_skill,
        "prerequisites": skill.prerequisites.all(),
        "progresses_to": skill.progresses_to.all(),
    }
    return render(request, "skills/skill_detail.html", context)


@login_required
def start_learning(request, slug):
    """Move a skill from NOT_STARTED -> LEARNING (section 11)."""
    skill = get_object_or_404(Skill, slug=slug)
    user_skill, _ = UserSkill.objects.get_or_create(user=request.user, skill=skill)
    if user_skill.status == "not_started":
        user_skill.status = "learning"
        user_skill.started_at = timezone.now()
        user_skill.save()
    return redirect("skills:skill_detail", slug=slug)


@login_required
def submit_verification(request, slug):
    """
    Section 17/18 -- video verification request.
    Selecting a skill NEVER auto-verifies it; this only creates a PENDING
    request for admin/moderator review.
    """
    skill = get_object_or_404(Skill, slug=slug)
    requirement = getattr(skill, "verification_requirement", None)

    if request.method == "POST" and request.FILES.get("video"):
        verification = SkillVerification.objects.create(
            user=request.user, skill=skill, video=request.FILES["video"], state="pending"
        )
        user_skill, _ = UserSkill.objects.get_or_create(user=request.user, skill=skill)
        user_skill.status = "verification_pending"
        user_skill.save()
        messages.success(request, "Verification submitted. A moderator will review your video soon.")
        return redirect("skills:skill_detail", slug=slug)

    return render(
        request, "skills/submit_verification.html",
        {"skill": skill, "requirement": requirement},
    )
