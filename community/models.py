from django.db import models
from django.conf import settings
from skills.models import SkillVerification


class Post(models.Model):
    """Section 28/29. Can optionally attach a skill verification/achievement."""
    POST_TYPE_CHOICES = [
        ("text", "Text"),
        ("achievement", "Achievement"),
        ("skill_milestone", "Skill Milestone"),
        ("training_update", "Training Update"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default="text")
    content = models.TextField(max_length=1000)
    image = models.ImageField(upload_to="post_images/%Y/%m/", blank=True, null=True)
    video = models.FileField(upload_to="post_videos/%Y/%m/", blank=True, null=True)
    linked_verification = models.ForeignKey(
        SkillVerification, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_reported = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False, help_text="Moderation: hide without deleting")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.content[:40]}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} on {self.post_id}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")


class Report(models.Model):
    """Section 46 moderation queue."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("under_review", "Under Review"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="filed_reports"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report #{self.id} ({self.status})"


class Notification(models.Model):
    """Section 34."""
    TYPE_CHOICES = [
        ("new_follower", "New Follower"),
        ("like", "Like"),
        ("comment", "Comment"),
        ("verification_result", "Verification Result"),
        ("achievement_unlocked", "Achievement Unlocked"),
        ("rank_upgrade", "Rank Upgrade"),
        ("training_reminder", "Training Reminder"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}: {self.message}"
