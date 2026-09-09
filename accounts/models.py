from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """
    Private account layer.
    Extends Django's built-in auth (already gives us secure password hashing,
    sessions, login/logout, password reset tokens) with the private-profile
    fields from the spec (section 8).
    """
    EXPERIENCE_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    experience_level = models.CharField(
        max_length=20, choices=EXPERIENCE_CHOICES, blank=True
    )
    primary_goal = models.CharField(max_length=255, blank=True)
    email_verified = models.BooleanField(default=False)
    notification_preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.username


class AthleteProfile(models.Model):
    """
    Public athlete profile layer (section 8).
    Deliberately holds NO calculated rank/XP fields directly editable here --
    those live in the ranking app and are derived by the Rank Engine
    (see spec section 37/53: don't store calculated info as ground truth).
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="athlete_profile"
    )
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)

    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"@{self.user.username}"

    def get_absolute_url(self):
        return reverse("accounts:profile_detail", args=[self.user.username])

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()
