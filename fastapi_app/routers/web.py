from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.template.loader import render_to_string

from accounts.models import User
from skills.models import Skill, SkillCategory, UserSkill
from training.models import Program, Workout, WorkoutSession
from ranking.models import UserRank
from ranking.services import next_rank_progress
from community.models import Post

router = APIRouter(include_in_schema=False)
rf = RequestFactory()


def _get_django_request(fastapi_req: Request, user=None):
    req = rf.get(str(fastapi_req.url.path))
    req.session = {}
    req.user = user if user is not None else AnonymousUser()
    return req


@router.get("/", response_class=HTMLResponse)
async def web_dashboard(request: Request):
    def _render():
        user = User.objects.first()
        d_req = _get_django_request(request, user)

        if user is None:
            context = {
                "request": d_req,
                "user": None,
                "user_rank": None,
                "next_rank": None,
                "xp_needed": 0,
                "current_skills": [],
                "recent_sessions": [],
                "community_feed": Post.objects.filter(
                    is_hidden=False
                ).select_related("user")[:5],
            }
        else:
            user_rank, _ = UserRank.objects.get_or_create(user=user)
            next_rank, xp_needed = next_rank_progress(user_rank)
            context = {
                "request": d_req,
                "user": user,
                "user_rank": user_rank,
                "next_rank": next_rank,
                "xp_needed": xp_needed,
                "current_skills": (
                    UserSkill.objects.filter(user=user, status="learning")
                    .select_related("skill")[:5]
                ),
                "recent_sessions": (
                    WorkoutSession.objects.filter(user=user)
                    .order_by("-started_at")[:3]
                ),
                "community_feed": (
                    Post.objects.filter(is_hidden=False)
                    .select_related("user")[:5]
                ),
            }

        return render_to_string("core/dashboard.html", context, request=d_req)

    html = await sync_to_async(_render)()
    return HTMLResponse(content=html)


@router.get("/skills/", response_class=HTMLResponse)
async def web_skill_list(request: Request):
    def _render():
        user = User.objects.first()
        categories = SkillCategory.objects.prefetch_related("skills").order_by("order")
        user_status = {}
        if user:
            user_status = {
                us.skill_id: us.status
                for us in UserSkill.objects.filter(user=user)
            }
        d_req = _get_django_request(request, user)
        context = {
            "request": d_req,
            "user": user,
            "categories": categories,
            "user_status": user_status,
        }
        return render_to_string("skills/skill_list.html", context, request=d_req)

    html = await sync_to_async(_render)()
    return HTMLResponse(content=html)


@router.get("/skills/{slug}/", response_class=HTMLResponse)
async def web_skill_detail(request: Request, slug: str):
    def _render():
        try:
            skill = Skill.objects.select_related("category").get(slug=slug, is_active=True)
        except Skill.DoesNotExist:
            return None
        user = User.objects.first()
        user_skill = None
        if user:
            user_skill, _ = UserSkill.objects.get_or_create(user=user, skill=skill)
        d_req = _get_django_request(request, user)
        context = {
            "request": d_req,
            "user": user,
            "skill": skill,
            "user_skill": user_skill,
            "prerequisites": skill.prerequisites.all(),
            "progresses_to": skill.progresses_to.all(),
        }
        return render_to_string("skills/skill_detail.html", context, request=d_req)

    html = await sync_to_async(_render)()
    if not html:
        raise HTTPException(status_code=404, detail="Skill not found")
    return HTMLResponse(content=html)


@router.get("/training/", response_class=HTMLResponse)
@router.get("/training/programs/", response_class=HTMLResponse)
async def web_program_list(request: Request):
    def _render():
        user = User.objects.first()
        programs = Program.objects.select_related("target_skill").prefetch_related("workouts").order_by("id")
        d_req = _get_django_request(request, user)
        context = {
            "request": d_req,
            "user": user,
            "programs": programs,
        }
        return render_to_string("training/program_list.html", context, request=d_req)

    html = await sync_to_async(_render)()
    return HTMLResponse(content=html)


@router.get("/training/programs/{pk}/", response_class=HTMLResponse)
async def web_program_detail(request: Request, pk: int):
    def _render():
        try:
            program = Program.objects.get(pk=pk)
        except Program.DoesNotExist:
            return None
        user = User.objects.first()
        workouts = program.workouts.all().prefetch_related("workout_exercises__exercise").order_by("order_in_program")
        d_req = _get_django_request(request, user)
        context = {
            "request": d_req,
            "user": user,
            "program": program,
            "workouts": workouts,
        }
        return render_to_string("training/program_detail.html", context, request=d_req)

    html = await sync_to_async(_render)()
    if not html:
        raise HTTPException(status_code=404, detail="Program not found")
    return HTMLResponse(content=html)


@router.get("/training/workout/{pk}/player/", response_class=HTMLResponse)
@router.get("/training/workouts/{pk}/player/", response_class=HTMLResponse)
async def web_workout_player(request: Request, pk: int):
    def _render():
        try:
            workout = Workout.objects.get(pk=pk)
        except Workout.DoesNotExist:
            return None
        user = User.objects.first()
        exercises = workout.workout_exercises.select_related("exercise", "exercise__related_skill").order_by("order")
        d_req = _get_django_request(request, user)
        context = {
            "request": d_req,
            "user": user,
            "workout": workout,
            "exercises": exercises,
        }
        return render_to_string("training/workout_player.html", context, request=d_req)

    html = await sync_to_async(_render)()
    if not html:
        raise HTTPException(status_code=404, detail="Workout not found")
    return HTMLResponse(content=html)


@router.get("/ranking/", response_class=HTMLResponse)
async def web_ranking(request: Request):
    def _render():
        user = User.objects.first()
        user_ranks = UserRank.objects.select_related("user", "current_rank").order_by("-cached_xp")[:30]
        d_req = _get_django_request(request, user)
        context = {
            "request": d_req,
            "user": user,
            "user_ranks": user_ranks,
        }
        return render_to_string("ranking/leaderboard.html", context, request=d_req)

    html = await sync_to_async(_render)()
    return HTMLResponse(content=html)


@router.get("/community/", response_class=HTMLResponse)
async def web_community(request: Request):
    def _render():
        user = User.objects.first()
        posts = Post.objects.filter(is_hidden=False).select_related("user").order_by("-created_at")[:20]
        d_req = _get_django_request(request, user)
        context = {
            "request": d_req,
            "user": user,
            "posts": posts,
        }
        return render_to_string("community/feed.html", context, request=d_req)

    html = await sync_to_async(_render)()
    return HTMLResponse(content=html)
