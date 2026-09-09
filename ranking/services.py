"""
Rank Engine (spec sections 24/37/53).

Rank is NEVER stored as ground truth -- it is always recalculated here from
raw signals (XP ledger, verified skills, skill difficulty, achievements).
This keeps the formula swappable without touching the frontend or migrating
historical data.
"""
from django.db.models import Sum
from django.utils import timezone

from .models import XPTransaction, Rank, UserRank


def get_total_xp(user) -> int:
    return XPTransaction.objects.filter(user=user).aggregate(total=Sum("amount"))["total"] or 0


def get_skill_score(user) -> int:
    """Sum of difficulty_score across the user's VERIFIED skills only."""
    from skills.models import UserSkill

    verified = UserSkill.objects.filter(user=user, status="verified").select_related("skill")
    return sum(us.skill.difficulty_score for us in verified)


def get_verified_skill_count(user) -> int:
    from skills.models import UserSkill

    return UserSkill.objects.filter(user=user, status="verified").count()


def award_xp(user, source: str, amount: int, reference_id: int | None = None) -> XPTransaction:
    """Single entry point for granting XP -- keeps the ledger consistent
    and is the natural place to add anti-farming rate limits later."""
    tx = XPTransaction.objects.create(
        user=user, source=source, amount=amount, reference_id=reference_id
    )
    recalculate_rank(user)
    return tx


def recalculate_rank(user) -> UserRank:
    """
    Recompute the user's rank from raw signals and refresh the UserRank cache.
    Deliberately requires multiple thresholds (XP AND verified skills AND
    skill score) so nobody reaches a high rank purely by grinding easy
    workouts (spec section 24).
    """
    xp = get_total_xp(user)
    skill_score = get_skill_score(user)
    verified_count = get_verified_skill_count(user)

    eligible_rank = None
    for rank in Rank.objects.order_by("order"):
        if (
            xp >= rank.min_xp
            and verified_count >= rank.min_verified_skills
            and skill_score >= rank.min_skill_score
        ):
            eligible_rank = rank  # keep the highest rank whose requirements are all met
        else:
            break

    user_rank, _ = UserRank.objects.get_or_create(user=user)
    user_rank.cached_xp = xp
    user_rank.cached_skill_score = skill_score
    user_rank.cached_verified_skill_count = verified_count
    user_rank.current_rank = eligible_rank
    user_rank.last_calculated = timezone.now()
    user_rank.save()
    return user_rank


def next_rank_progress(user_rank: UserRank):
    """Returns (next_rank, xp_needed) for progress-bar UI, or (None, 0) if maxed out."""
    next_rank = (
        Rank.objects.filter(order__gt=(user_rank.current_rank.order if user_rank.current_rank else 0))
        .order_by("order")
        .first()
    )
    if not next_rank:
        return None, 0
    xp_needed = max(next_rank.min_xp - user_rank.cached_xp, 0)
    return next_rank, xp_needed
