from typing import List
from fastapi import APIRouter, HTTPException
from asgiref.sync import sync_to_async
from community.models import Post
from fastapi_app.schemas import CommunityPostOut

router = APIRouter(prefix="/api/community", tags=["Community"])


@router.get("/posts", response_model=List[CommunityPostOut])
async def list_community_posts():
    """Retrieve recent trainee community posts and milestones."""
    def _fetch():
        posts = Post.objects.filter(is_hidden=False).select_related("user").order_by("-created_at")[:40]
        return [
            CommunityPostOut(
                id=p.id,
                username=p.user.username if p.user else "Athlete",
                content=p.content,
                post_type=p.post_type,
                created_at=p.created_at,
                likes_count=p.likes.count() if hasattr(p, "likes") else 0
            ) for p in posts
        ]
    return await sync_to_async(_fetch)()
