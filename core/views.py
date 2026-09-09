from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from skills.models import UserSkill
from training.models import WorkoutSession
from ranking.models import UserRank
from ranking.services import next_rank_progress
from community.models import Post


def landing(request):
    """Section 5 -- public marketing landing page."""
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return render(request, "core/landing.html")


@login_required
def dashboard(request):
    """Section 33 -- personalized home dashboard."""
    user = request.user
    user_rank, _ = UserRank.objects.get_or_create(user=user)
    next_rank, xp_needed = next_rank_progress(user_rank)

    current_skills = (
        UserSkill.objects.filter(user=user, status="learning").select_related("skill")[:5]
    )
    recent_sessions = WorkoutSession.objects.filter(user=user).order_by("-started_at")[:3]
    community_feed = Post.objects.filter(is_hidden=False).select_related("user")[:5]

    context = {
        "user_rank": user_rank,
        "next_rank": next_rank,
        "xp_needed": xp_needed,
        "current_skills": current_skills,
        "recent_sessions": recent_sessions,
        "community_feed": community_feed,
    }
    return render(request, "core/dashboard.html", context)
