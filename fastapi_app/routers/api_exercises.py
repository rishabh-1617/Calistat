from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from asgiref.sync import sync_to_async
from training.models import Exercise
from fastapi_app.schemas import ExerciseOut

router = APIRouter(prefix="/api/exercises", tags=["Exercises"])


@router.get("", response_model=List[ExerciseOut])
async def list_exercises(
    search: Optional[str] = Query(None, description="Search exercise name or description"),
    muscle: Optional[str] = Query(None, description="Filter by target muscle")
):
    """Retrieve all 115+ calisthenics exercises with video demonstration URLs."""
    def _fetch():
        qs = Exercise.objects.all().order_by("name")
        if search:
            qs = qs.filter(name__icontains=search)
        
        results = []
        for ex in qs:
            muscles = ex.get_target_muscles()
            if muscle and not any(muscle.lower() in m.lower() for m in muscles):
                continue
            results.append(ExerciseOut(
                id=ex.id,
                name=ex.name,
                description=ex.description,
                video_url=ex.get_embed_url(),
                target_muscles=muscles,
                related_skill_id=ex.related_skill_id
            ))
        return results

    return await sync_to_async(_fetch)()


@router.get("/{exercise_id}", response_model=ExerciseOut)
async def get_exercise(exercise_id: int):
    """Retrieve single exercise details and video tutorial."""
    def _fetch():
        try:
            ex = Exercise.objects.get(id=exercise_id)
            return ExerciseOut(
                id=ex.id,
                name=ex.name,
                description=ex.description,
                video_url=ex.get_embed_url(),
                target_muscles=ex.get_target_muscles(),
                related_skill_id=ex.related_skill_id
            )
        except Exercise.DoesNotExist:
            return None

    res = await sync_to_async(_fetch)()
    if not res:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return res
