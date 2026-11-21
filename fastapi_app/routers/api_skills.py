from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from asgiref.sync import sync_to_async
from skills.models import Skill, SkillCategory
from fastapi_app.schemas import SkillOut, SkillDetailOut, CategoryOut

router = APIRouter(prefix="/api/skills", tags=["Skills"])


@router.get("/categories", response_model=List[CategoryOut])
async def list_categories():
    """Retrieve all calisthenics skill categories in sequence order."""
    def _fetch():
        return list(SkillCategory.objects.all().order_by("order"))
    return await sync_to_async(_fetch)()


@router.get("", response_model=List[SkillOut])
async def list_skills(
    category: Optional[str] = Query(None, description="Category slug"),
    difficulty: Optional[str] = Query(None, description="Difficulty level code (e.g. beginner, intermediate, advanced)"),
    search: Optional[str] = Query(None, description="Search skill name or muscles")
):
    """List calisthenics skills with optional filtering."""
    def _fetch():
        qs = Skill.objects.filter(is_active=True).select_related("category")
        if category:
            qs = qs.filter(category__slug=category)
        if difficulty:
            qs = qs.filter(difficulty_level=difficulty)
        if search:
            qs = qs.filter(name__icontains=search)
        
        result = []
        for s in qs.order_by("category__order", "difficulty_score"):
            result.append(SkillOut(
                id=s.id,
                name=s.name,
                slug=s.slug,
                category_id=s.category_id,
                category_name=s.category.name if s.category else "General",
                difficulty_level=s.difficulty_level,
                difficulty_score=s.difficulty_score,
                target_muscles=s.get_target_muscles(),
                video_url=s.get_embed_url()
            ))
        return result
    return await sync_to_async(_fetch)()


@router.get("/{slug}", response_model=SkillDetailOut)
async def get_skill_detail(slug: str):
    """Retrieve in-depth skill instructions, prerequisites, and video tutorial."""
    def _fetch():
        try:
            s = Skill.objects.select_related("category").get(slug=slug)
        except Skill.DoesNotExist:
            return None
        
        prereqs = [p.name for p in s.prerequisites.all()]
        progresses = [p.name for p in s.progresses_to.all()]

        return SkillDetailOut(
            id=s.id,
            name=s.name,
            slug=s.slug,
            category_id=s.category_id,
            category_name=s.category.name if s.category else "General",
            difficulty_level=s.difficulty_level,
            difficulty_score=s.difficulty_score,
            target_muscles=s.get_target_muscles(),
            video_url=s.get_embed_url(),
            description=s.description,
            technique_instructions=s.technique_instructions,
            common_mistakes=s.common_mistakes,
            prerequisites=prereqs,
            progresses_to=progresses
        )

    res = await sync_to_async(_fetch)()
    if not res:
        raise HTTPException(status_code=404, detail="Skill not found")
    return res
