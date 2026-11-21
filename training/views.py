from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages

from .models import Workout, Program, WorkoutSession, WorkoutExercise, ExerciseLog, Challenge, UserChallenge
from ranking.services import award_xp
from community.models import Notification

WORKOUT_COMPLETION_XP = 50
PROGRAM_COMPLETION_XP = 300


def program_list(request):
    """Section 12 -- browsable training programs."""
    programs = Program.objects.select_related("target_skill").prefetch_related("workouts")
    return render(request, "training/program_list.html", {"programs": programs})


def program_detail(request, pk):
    program = get_object_or_404(Program, pk=pk)
    workouts = program.workouts.all().prefetch_related("workout_exercises__exercise")
    return render(request, "training/program_detail.html", {"program": program, "workouts": workouts})


@login_required
def workout_player(request, pk):
    """Section 13 -- the actual workout screen: exercise, sets, reps, interactive rest timer."""
    workout = get_object_or_404(Workout, pk=pk)
    exercises = workout.workout_exercises.select_related("exercise", "exercise__related_skill").order_by("order")
    context = {"workout": workout, "exercises": exercises}
    return render(request, "training/workout_player.html", context)


@login_required
def start_workout(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    session = WorkoutSession.objects.create(user=request.user, workout=workout)
    return redirect("training:workout_player", pk=workout.pk)


@login_required
def complete_workout(request, pk):
    """
    Section 14/22 -- record completion and award XP.
    XP is granted through the Rank Engine's single award_xp() entry point,
    never written directly onto the user, to avoid spammable side-channels.
    """
    workout = get_object_or_404(Workout, pk=pk)
    session, created = WorkoutSession.objects.get_or_create(
        user=request.user, workout=workout, is_completed=False,
        defaults={},
    )
    session.is_completed = True
    session.completed_at = timezone.now()
    session.save()
    award_xp(request.user, "workout_completed", WORKOUT_COMPLETION_XP, reference_id=session.pk)

    Notification.objects.create(
        user=request.user,
        notif_type="achievement_unlocked",
        message=f"Workout completed: '{workout.title}'! +{WORKOUT_COMPLETION_XP} XP earned."
    )
    messages.success(request, f"Crushed it! You completed '{workout.title}' and earned +{WORKOUT_COMPLETION_XP} XP!")
    return redirect("training:history")


@login_required
def history(request):
    """Section 14 -- workout history."""
    sessions = (
        WorkoutSession.objects.filter(user=request.user)
        .select_related("workout")
        .order_by("-started_at")
    )
    total_workouts = sessions.filter(is_completed=True).count()
    return render(request, "training/history.html", {
        "sessions": sessions,
        "total_workouts": total_workouts,
    })


@login_required
def challenge_list(request):
    """Section 22/37 -- Daily & Weekly Calisthenics Challenges."""
    cadence = request.GET.get("cadence", "all")
    challenges = Challenge.objects.filter(is_active=True)
    if cadence in ["daily", "weekly", "special"]:
        challenges = challenges.filter(cadence=cadence)

    user_challenges = {
        uc.challenge_id: uc
        for uc in UserChallenge.objects.filter(user=request.user)
    }

    challenge_items = []
    for c in challenges:
        uc = user_challenges.get(c.id)
        progress = uc.progress if uc else 0
        is_completed = uc.is_completed if uc else False
        xp_claimed = uc.xp_claimed if uc else False
        pct = min(100, int((progress / max(1, c.target_value)) * 100))
        challenge_items.append({
            "challenge": c,
            "progress": progress,
            "is_completed": is_completed,
            "xp_claimed": xp_claimed,
            "pct": pct,
        })

    return render(request, "training/challenges.html", {
        "challenges": challenge_items,
        "selected_cadence": cadence,
    })


@login_required
def update_challenge_progress(request, pk):
    """Log progress towards a challenge."""
    challenge = get_object_or_404(Challenge, pk=pk)
    uc, _ = UserChallenge.objects.get_or_create(user=request.user, challenge=challenge)

    if request.method == "POST":
        step = int(request.POST.get("increment", 10))
        uc.progress = min(challenge.target_value, uc.progress + step)
        if uc.progress >= challenge.target_value:
            uc.is_completed = True
            if not uc.completed_at:
                uc.completed_at = timezone.now()
        uc.save()
        messages.success(request, f"Progress updated: {uc.progress}/{challenge.target_value} for '{challenge.title}'")

    return redirect("training:challenge_list")


@login_required
def claim_challenge_xp(request, pk):
    """Claim XP reward for completed challenge."""
    challenge = get_object_or_404(Challenge, pk=pk)
    uc = get_object_or_404(UserChallenge, user=request.user, challenge=challenge)

    if uc.is_completed and not uc.xp_claimed:
        uc.xp_claimed = True
        uc.save()
        award_xp(request.user, "challenge_completed", challenge.xp_reward, reference_id=challenge.pk)
        Notification.objects.create(
            user=request.user,
            notif_type="achievement_unlocked",
            message=f"Challenge Reward Claimed: '{challenge.title}'! +{challenge.xp_reward} XP added to your rank score."
        )
        messages.success(request, f"Claimed +{challenge.xp_reward} XP for '{challenge.title}'!")
    elif uc.xp_claimed:
        messages.info(request, "You have already claimed this reward.")

    return redirect("training:challenge_list")
