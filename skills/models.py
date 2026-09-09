from django.db import models
from django.conf import settings
from django.urls import reverse


class SkillCategory(models.Model):
    """PUSH / PULL / CORE / LEGS / BALANCE / STATIC / DYNAMIC (section 9)."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Skill categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    A single node in the skill tree. Difficulty and prerequisites are
    admin-configurable (section 9/23) -- nothing here is hard-coded in
    application logic, so new skills can be added without a code change.
    """
    DIFFICULTY_LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
        ("elite", "Elite"),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        SkillCategory, on_delete=models.PROTECT, related_name="skills"
    )
    description = models.TextField(blank=True)
    difficulty_level = models.CharField(
        max_length=20, choices=DIFFICULTY_LEVEL_CHOICES, default="beginner"
    )
    difficulty_score = models.PositiveIntegerField(
        default=1, help_text="Configurable numeric difficulty (e.g. 1-10). Drives XP/rank scoring."
    )
    muscle_groups = models.CharField(max_length=255, blank=True)
    technique_instructions = models.TextField(blank=True)
    common_mistakes = models.TextField(blank=True)
    tutorial_video_url = models.URLField(blank=True)

    prerequisites = models.ManyToManyField(
        "self", symmetrical=False, related_name="unlocks", blank=True
    )
    # e.g. Pull-up -> Chest-to-bar -> Muscle-up
    progresses_to = models.ManyToManyField(
        "self", symmetrical=False, related_name="regresses_from", blank=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "difficulty_score"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("skills:skill_detail", args=[self.slug])


class VerificationRequirement(models.Model):
    """
    Section 18 -- explicit, per-skill verification criteria so reviewers
    (and future AI analysis) have a checklist instead of vague judgement.
    """
    skill = models.OneToOneField(
        Skill, on_delete=models.CASCADE, related_name="verification_requirement"
    )
    instructions = models.TextField(
        help_text="What the video must show (full body, full bar, no cuts, etc.)"
    )
    requires_strict_review = models.BooleanField(
        default=False, help_text="Elevated scrutiny for advanced skills (Planche, Front Lever, etc.)"
    )
    min_hold_seconds = models.PositiveIntegerField(null=True, blank=True)
    min_reps = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Verification rules: {self.skill.name}"


class UserSkill(models.Model):
    """
    Per-user progress on a skill (section 11). Status can never jump straight
    to VERIFIED without going through the verification workflow.
    """
    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("learning", "Learning"),
        ("self_recorded", "Self Recorded"),
        ("verification_pending", "Verification Pending"),
        ("verified", "Verified"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_skills"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="user_skills")
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="not_started")
    started_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "skill")

    def __str__(self):
        return f"{self.user} - {self.skill} ({self.status})"


class SkillVerification(models.Model):
    """
    Section 17/19 -- the verification request lifecycle.
    CLAIMED status is intentionally never enough on its own to earn the
    verified badge; only APPROVED flips UserSkill.status to 'verified'.
    """
    STATE_CHOICES = [
        ("self_recorded", "Self Recorded"),
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("expired", "Expired / Reverify Required"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="verifications"
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="verifications")
    video = models.FileField(upload_to="verification_videos/%Y/%m/")
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="pending")
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_verifications",
    )
    reviewer_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.skill} [{self.state}]"
