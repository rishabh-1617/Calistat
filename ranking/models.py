from django.db import models
from django.conf import settings


class XPTransaction(models.Model):
    """
    Ledger of every XP-earning event (section 22/37).
    We NEVER store a running total on the user -- XP is always derivable by
    summing this table, so the Rank Engine can be recalculated if rules change.
    """
    SOURCE_CHOICES = [
        ("workout_completed", "Workout Completed"),
        ("program_completed", "Program Completed"),
        ("skill_verified", "Skill Verified"),
        ("achievement_unlocked", "Achievement Unlocked"),
        ("challenge_completed", "Challenge Completed"),
        ("community", "Community Participation"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="xp_transactions"
    )
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    amount = models.IntegerField()
    reference_id = models.PositiveIntegerField(
        null=True, blank=True, help_text="ID of the related object (workout session, skill, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} +{self.amount}XP ({self.source})"


class Rank(models.Model):
    """
    Admin-configurable rank tier (section 21/24).
    Thresholds live here, NOT hard-coded, so ranks can be rebalanced without
    a deploy.
    """
    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveIntegerField(unique=True, help_text="Lower = earlier rank (Novice=1, Elite=7...)")
    badge_color = models.CharField(max_length=20, default="#888888")
    min_xp = models.PositiveIntegerField(default=0)
    min_verified_skills = models.PositiveIntegerField(default=0)
    min_skill_score = models.PositiveIntegerField(
        default=0, help_text="Sum of difficulty_score across verified skills"
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class UserRank(models.Model):
    """
    Cached CURRENT rank for fast profile reads. This is a derived value,
    recomputed by ranking.services.recalculate_rank() -- never edited by hand
    except by admins for support/debug purposes (section 37).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rank_state"
    )
    current_rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, blank=True)
    cached_xp = models.PositiveIntegerField(default=0)
    cached_skill_score = models.PositiveIntegerField(default=0)
    cached_verified_skill_count = models.PositiveIntegerField(default=0)
    last_calculated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} -> {self.current_rank}"


class Achievement(models.Model):
    """Badge definitions (section 26). Kept separate from rank per section 53."""
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default="🏆")
    xp_reward = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="achievements"
    )
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")

    def __str__(self):
        return f"{self.user} - {self.achievement}"
