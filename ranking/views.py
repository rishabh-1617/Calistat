from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserRank, XPTransaction, Achievement, UserAchievement
from .services import next_rank_progress
from skills.models import SkillCategory, Skill, UserSkill
from training.models import WorkoutSession, UserChallenge


def leaderboard(request):
    """Section 31 -- multiple leaderboard views. NOT follower-based."""
    scope = request.GET.get("scope", "overall")
    query = UserRank.objects.select_related("user", "current_rank")

    if scope == "skills":
        ranks = query.order_by("-cached_skill_score", "-cached_verified_skill_count", "-cached_xp")[:100]
    elif scope == "verified":
        ranks = query.order_by("-cached_verified_skill_count", "-cached_skill_score", "-cached_xp")[:100]
    else:
        ranks = query.order_by("-cached_xp", "-cached_skill_score")[:100]

    return render(request, "ranking/leaderboard.html", {
        "ranks": ranks,
        "scope": scope,
    })


@login_required
def analytics_dashboard(request):
    """Athlete progress, category skill mastery, XP ledger, and training consistency."""
    user = request.user
    user_rank, _ = UserRank.objects.get_or_create(user=user)
    next_rank, xp_needed = next_rank_progress(user_rank)

    # Calculate category skill mastery
    categories = SkillCategory.objects.all()
    user_skills = UserSkill.objects.filter(user=user)
    user_verified_ids = set(user_skills.filter(status="verified").values_list("skill_id", flat=True))
    user_learning_ids = set(user_skills.filter(status="learning").values_list("skill_id", flat=True))

    category_stats = []
    total_platform_skills = 0
    total_user_verified = 0

    for cat in categories:
        cat_skills = cat.skills.filter(is_active=True)
        total_in_cat = cat_skills.count()
        total_platform_skills += total_in_cat
        verified_in_cat = cat_skills.filter(id__in=user_verified_ids).count()
        learning_in_cat = cat_skills.filter(id__in=user_learning_ids).count()
        total_user_verified += verified_in_cat
        pct = min(100, int((verified_in_cat / max(1, total_in_cat)) * 100))

        category_stats.append({
            "category": cat,
            "total": total_in_cat,
            "verified": verified_in_cat,
            "learning": learning_in_cat,
            "pct": pct,
        })

    # Overall skill mastery percentage
    overall_mastery_pct = min(100, int((total_user_verified / max(1, total_platform_skills)) * 100))

    # Workout stats
    completed_workouts = WorkoutSession.objects.filter(user=user, is_completed=True)
    total_workout_count = completed_workouts.count()
    recent_sessions = completed_workouts.select_related("workout").order_by("-started_at")[:5]

    # XP Transactions history
    xp_history = XPTransaction.objects.filter(user=user).order_by("-created_at")[:12]

    # Achievements
    total_achievements = Achievement.objects.count()
    earned_achievements = UserAchievement.objects.filter(user=user).count()

    # Challenges completed
    completed_challenges = UserChallenge.objects.filter(user=user, is_completed=True).count()

    return render(request, "ranking/analytics.html", {
        "user_rank": user_rank,
        "next_rank": next_rank,
        "xp_needed": xp_needed,
        "category_stats": category_stats,
        "overall_mastery_pct": overall_mastery_pct,
        "total_platform_skills": total_platform_skills,
        "total_user_verified": total_user_verified,
        "total_workout_count": total_workout_count,
        "recent_sessions": recent_sessions,
        "xp_history": xp_history,
        "total_achievements": total_achievements,
        "earned_achievements": earned_achievements,
        "completed_challenges": completed_challenges,
    })
