from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Workout, Program, WorkoutSession, WorkoutExercise, ExerciseLog
from ranking.services import award_xp

WORKOUT_COMPLETION_XP = 50
PROGRAM_COMPLETION_XP = 300


def program_list(request):
    """Section 12 -- browsable training programs."""
    programs = Program.objects.select_related("target_skill").prefetch_related("workouts")
    return render(request, "training/program_list.html", {"programs": programs})


def program_detail(request, pk):
    program = get_object_or_404(Program, pk=pk)
    workouts = program.workouts.all()
    return render(request, "training/program_detail.html", {"program": program, "workouts": workouts})


@login_required
def workout_player(request, pk):
    """Section 13 -- the actual workout screen: exercise, sets, reps, rest timer."""
    workout = get_object_or_404(Workout, pk=pk)
    exercises = workout.workout_exercises.select_related("exercise")
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
    return redirect("training:history")


@login_required
def history(request):
    """Section 14 -- workout history."""
    sessions = (
        WorkoutSession.objects.filter(user=request.user)
        .select_related("workout")
        .order_by("-started_at")
    )
    return render(request, "training/history.html", {"sessions": sessions})
