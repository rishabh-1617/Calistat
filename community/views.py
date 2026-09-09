from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Post, Comment, Like, Report, Notification
from .forms import PostForm, CommentForm


def feed(request):
    """Section 28 -- community feed."""
    posts = Post.objects.filter(is_hidden=False).select_related("user").prefetch_related("likes", "comments")
    form = PostForm() if request.user.is_authenticated else None
    
    # Pre-check liked status for active user
    liked_post_ids = set()
    if request.user.is_authenticated:
        liked_post_ids = set(
            Like.objects.filter(user=request.user, post__in=posts).values_list("post_id", flat=True)
        )

    return render(request, "community/feed.html", {
        "posts": posts,
        "form": form,
        "liked_post_ids": liked_post_ids,
    })


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Post shared with the Calisfy community!")
    return redirect("community:feed")


@login_required
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    else:
        if post.user != request.user:
            Notification.objects.create(
                user=post.user,
                notif_type="like",
                message=f"@{request.user.username} liked your post: '{post.content[:35]}...'"
            )
    return redirect("community:feed")


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            if post.user != request.user:
                Notification.objects.create(
                    user=post.user,
                    notif_type="comment",
                    message=f"@{request.user.username} commented: '{comment.content[:35]}...'"
                )
            messages.success(request, "Comment added.")
    return redirect("community:feed")


@login_required
def report_post(request, pk):
    """Section 46 -- content moderation reporting."""
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        Report.objects.create(
            reporter=request.user, post=post, reason=request.POST.get("reason", "Reported by user")
        )
        post.is_reported = True
        post.save()
        messages.info(request, "Report submitted. Thank you for keeping the community safe.")
    return redirect("community:feed")


@login_required
def notifications_list(request):
    """Section 34 -- In-app notification center."""
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    unread_count = notifications.filter(is_read=False).count()
    return render(
        request,
        "community/notifications.html",
        {"notifications": notifications, "unread_count": unread_count},
    )


@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect("community:notifications_list")


@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("community:notifications_list")
