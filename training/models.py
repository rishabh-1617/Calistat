from django.db import models
from django.conf import settings
from skills.models import Skill


class Exercise(models.Model):
    """Reusable exercise library block used inside workouts (section 36)."""
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    related_skill = models.ForeignKey(
        Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name="exercises"
    )

    def __str__(self):
        return self.name


class Program(models.Model):
    """A multi-week training program, e.g. '8-week First Muscle-up' (section 12)."""
    GOAL_SKILL = "skill"

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    target_skill = models.ForeignKey(
        Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name="programs"
    )
    experience_level = models.CharField(max_length=20, blank=True)
    duration_weeks = models.PositiveIntegerField(default=4)
    days_per_week = models.PositiveIntegerField(default=3)

    def __str__(self):
        return self.name


class Workout(models.Model):
    """A single workout template (section 13)."""
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="workouts", null=True, blank=True
    )
    title = models.CharField(max_length=150)
    estimated_duration_minutes = models.PositiveIntegerField(default=30)
    order_in_program = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["program", "order_in_program"]

    def __str__(self):
        return self.title


class WorkoutExercise(models.Model):
    """Sets/reps prescription for an exercise inside a workout."""
    SECTION_CHOICES = [
        ("warmup", "Warm-up"),
        ("skill", "Skill / Technique"),
        ("strength", "Strength"),
        ("accessory", "Accessory"),
        ("core", "Core / Conditioning"),
        ("cooldown", "Cool down"),
    ]

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="workout_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default="strength")
    sets = models.PositiveIntegerField(default=3)
    reps = models.CharField(max_length=50, help_text="e.g. '10' or '30s hold'")
    rest_seconds = models.PositiveIntegerField(default=60)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["section", "order"]

    def __str__(self):
        return f"{self.workout} - {self.exercise}"


class WorkoutSession(models.Model):
    """A user's attempt at a workout (section 14)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workout_sessions"
    )
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.workout} ({self.started_at:%Y-%m-%d})"


class ExerciseLog(models.Model):
    """Actual sets/reps performed during a session, feeding the progression system (section 15)."""
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name="exercise_logs")
    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE)
    sets_completed = models.PositiveIntegerField(default=0)
    reps_completed = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.session} - {self.workout_exercise.exercise}"


class Challenge(models.Model):
    """Calisthenics bounties, daily & weekly challenges (spec sections 22/37)."""
    CADENCE_CHOICES = [
        ("daily", "Daily Challenge"),
        ("weekly", "Weekly Bounty"),
        ("special", "Milestone Challenge"),
    ]
    CATEGORY_CHOICES = [
        ("push", "Push Power"),
        ("pull", "Pull Strength"),
        ("core", "Iron Core"),
        ("legs", "Legs & Explosiveness"),
        ("skill", "Static & Skill"),
        ("endurance", "Work Capacity"),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="push")
    cadence = models.CharField(max_length=20, choices=CADENCE_CHOICES, default="daily")
    target_metric = models.CharField(max_length=50, help_text="e.g. '100 push-ups' or '3 min plank'")
    target_value = models.PositiveIntegerField(default=100)
    xp_reward = models.PositiveIntegerField(default=75)
    badge_icon = models.CharField(max_length=10, default="🎯")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cadence", "-xp_reward"]

    def __str__(self):
        return f"[{self.get_cadence_display()}] {self.title} (+{self.xp_reward}XP)"


class UserChallenge(models.Model):
    """Tracks athlete completion/progress on challenges."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_challenges"
    )
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="user_records")
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    xp_claimed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "challenge")

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.progress}/{self.challenge.target_value})"

