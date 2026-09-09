from django.shortcuts import render
from .models import UserRank


def leaderboard(request):
    """Section 31 -- multiple leaderboard views. NOT follower-based."""
    scope = request.GET.get("scope", "overall")
    ranks = (
        UserRank.objects.select_related("user", "current_rank")
        .order_by("-cached_xp", "-cached_skill_score")[:100]
    )
    return render(request, "ranking/leaderboard.html", {"ranks": ranks, "scope": scope})
