from typing import List, Optional
from fastapi import APIRouter, HTTPException
from asgiref.sync import sync_to_async
from training.models import Program, Workout, WorkoutSession
from fastapi_app.schemas import ProgramOut, WorkoutOut, WorkoutExerciseOut, WorkoutLogCreate

router = APIRouter(prefix="/api/training", tags=["Training & Programs"])


@router.get("/programs", response_model=List[ProgramOut])
async def list_programs():
    """Retrieve all structured calisthenics programs and their workouts."""
    def _fetch():
        programs = Program.objects.all().prefetch_related("workouts__workout_exercises__exercise")
        out = []
        for p in programs:
            workouts = []
            for w in p.workouts.all().order_by("order_in_program"):
                exercises = []
                for we in w.workout_exercises.all().order_by("order"):
                    exercises.append(WorkoutExerciseOut(
                        id=we.id,
                        exercise_id=we.exercise_id,
                        exercise_name=we.exercise.name,
                        section=we.section,
                        sets=we.sets,
                        reps=we.reps,
                        rest_seconds=we.rest_seconds,
                        video_url=we.exercise.get_embed_url()
                    ))
                workouts.append(WorkoutOut(
                    id=w.id,
                    title=w.title,
                    estimated_duration_minutes=w.estimated_duration_minutes,
                    order_in_program=w.order_in_program,
                    exercises=exercises
                ))
            out.append(ProgramOut(
                id=p.id,
                name=p.name,
                description=p.description,
                experience_level=p.experience_level,
                duration_weeks=p.duration_weeks,
                days_per_week=p.days_per_week,
                workouts=workouts
            ))
        return out

    return await sync_to_async(_fetch)()


@router.get("/workouts/{workout_id}", response_model=WorkoutOut)
async def get_workout(workout_id: int):
    """Retrieve a workout session plan, exercises, sets, reps, and rest timers."""
    def _fetch():
        try:
            w = Workout.objects.prefetch_related("workout_exercises__exercise").get(id=workout_id)
            exercises = [
                WorkoutExerciseOut(
                    id=we.id,
                    exercise_id=we.exercise_id,
                    exercise_name=we.exercise.name,
                    section=we.section,
                    sets=we.sets,
                    reps=we.reps,
                    rest_seconds=we.rest_seconds,
                    video_url=we.exercise.get_embed_url()
                ) for we in w.workout_exercises.all().order_by("order")
            ]
            return WorkoutOut(
                id=w.id,
                title=w.title,
                estimated_duration_minutes=w.estimated_duration_minutes,
                order_in_program=w.order_in_program,
                exercises=exercises
            )
        except Workout.DoesNotExist:
            return None

    res = await sync_to_async(_fetch)()
    if not res:
        raise HTTPException(status_code=404, detail="Workout not found")
    return res


@router.post("/workouts/{workout_id}/log")
async def log_workout_session(workout_id: int, log_data: WorkoutLogCreate):
    """Log completion of a workout session with duration and sets."""
    def _log():
        try:
            workout = Workout.objects.get(id=workout_id)
            # Find first active user or anonymous demo session
            from accounts.models import User
            user = User.objects.first()
            if not user:
                return {"status": "ok", "message": "Logged (guest mode)"}

            session = WorkoutSession.objects.create(
                user=user,
                workout=workout,
                duration_minutes=log_data.duration_minutes or workout.estimated_duration_minutes,
                notes=log_data.notes or ""
            )
            return {"status": "success", "session_id": session.id, "message": "Workout session recorded!"}
        except Workout.DoesNotExist:
            return None

    res = await sync_to_async(_log)()
    if not res:
        raise HTTPException(status_code=404, detail="Workout not found")
    return res
