from typing import List
from fastapi import APIRouter
from asgiref.sync import sync_to_async
from ranking.models import Rank, UserRank
from fastapi_app.schemas import RankOut, LeaderboardEntryOut

router = APIRouter(prefix="/api/ranking", tags=["Ranking & Leaderboard"])


@router.get("/ranks", response_model=List[RankOut])
async def list_ranks():
    """List all athlete ranking tiers (Novice, Bronze, Silver, Gold, Apex Master)."""
    def _fetch():
        ranks = Rank.objects.all().order_by("order")
        return [
            RankOut(
                id=r.id,
                name=r.name,
                order=r.order,
                badge_color=r.badge_color,
                min_xp=r.min_xp
            ) for r in ranks
        ]
    return await sync_to_async(_fetch)()


@router.get("/leaderboard", response_model=List[LeaderboardEntryOut])
async def get_leaderboard():
    """Retrieve top global calisthenics athletes ordered by XP and verified skills."""
    def _fetch():
        top_ranks = UserRank.objects.select_related("user", "current_rank").order_by("-cached_xp")[:50]
        results = []
        for ur in top_ranks:
            results.append(LeaderboardEntryOut(
                username=ur.user.username,
                rank_name=ur.current_rank.name if ur.current_rank else "Novice",
                badge_color=ur.current_rank.badge_color if ur.current_rank else "#6b7280",
                xp=ur.cached_xp,
                verified_skills=ur.cached_verified_skill_count
            ))
        return results

    return await sync_to_async(_fetch)()
