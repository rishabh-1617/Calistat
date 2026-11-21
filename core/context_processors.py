from community.models import Notification
from ranking.models import UserRank


def calisfy_context(request):
    """
    Global context processor providing data for the persistent Left Section navigation
    and mobile app bars (unread notifications count, rank badge, and profile).
    """
    if request.user is None or not request.user.is_authenticated:
        return {
            "unread_notifications_count": 0,
            "nav_user_rank": None,
            "nav_athlete_profile": None,
        }

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    user_rank = (
        UserRank.objects.filter(user=request.user)
        .select_related("current_rank")
        .first()
    )
    athlete_profile = getattr(request.user, "athlete_profile", None)

    return {
        "unread_notifications_count": unread_count,
        "nav_user_rank": user_rank,
        "nav_athlete_profile": athlete_profile,
    }
