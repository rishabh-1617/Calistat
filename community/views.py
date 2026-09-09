from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Post, Comment, Like, Report
from .forms import PostForm, CommentForm


def feed(request):
    """Section 28 -- community feed."""
    posts = Post.objects.filter(is_hidden=False).select_related("user")
    form = PostForm() if request.user.is_authenticated else None
    return render(request, "community/feed.html", {"posts": posts, "form": form})


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
    return redirect("community:feed")


@login_required
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
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
    return redirect("community:feed")


@login_required
def report_post(request, pk):
    """Section 46 -- content moderation reporting."""
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        Report.objects.create(
            reporter=request.user, post=post, reason=request.POST.get("reason", "")
        )
        post.is_reported = True
        post.save()
    return redirect("community:feed")
