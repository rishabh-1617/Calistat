from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from .forms import SignUpForm, OnboardingForm, ProfileEditForm
from .models import User, AthleteProfile
from skills.models import UserSkill
from ranking.models import UserRank, UserAchievement
from ranking.services import recalculate_rank
from community.models import Post


class CalisfyLoginView(LoginView):
    """Section 6/7 -- login with 'remember me' handling."""
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        if not self.request.POST.get("remember_me"):
            self.request.session.set_expiry(0)
        return response


def signup(request):
    """Section 6/7 -- registration -> initial profile setup -> dashboard."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            AthleteProfile.objects.create(user=user, display_name=user.username)
            recalculate_rank(user)
            login(request, user)
            return redirect("accounts:onboarding")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def onboarding(request):
    """Short post-signup onboarding: experience level + goal (section 6/7)."""
    if request.method == "POST":
        form = OnboardingForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("core:dashboard")
    else:
        form = OnboardingForm(instance=request.user)
    return render(request, "accounts/onboarding.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("core:landing")


def profile_detail(request, username):
    """Section 8/27 -- public athlete profile."""
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(AthleteProfile, user=profile_user)
    user_rank, _ = UserRank.objects.get_or_create(user=profile_user)
    verified_skills = UserSkill.objects.filter(
        user=profile_user, status="verified"
    ).select_related("skill", "skill__category")
    achievements = UserAchievement.objects.filter(user=profile_user).select_related("achievement")
    posts = Post.objects.filter(user=profile_user, is_hidden=False)
    workout_count = profile_user.workout_sessions.filter(is_completed=True).count()

    is_following = False
    if request.user.is_authenticated and hasattr(request.user, "athlete_profile"):
        is_following = profile.followers.filter(pk=request.user.athlete_profile.pk).exists()

    context = {
        "profile_user": profile_user,
        "profile": profile,
        "user_rank": user_rank,
        "verified_skills": verified_skills,
        "achievements": achievements,
        "posts": posts,
        "workout_count": workout_count,
        "is_following": is_following,
    }
    return render(request, "accounts/profile_detail.html", context)


@login_required
def edit_profile(request):
    profile, _ = AthleteProfile.objects.get_or_create(
        user=request.user, defaults={"display_name": request.user.username}
    )
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile_detail", username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, "accounts/edit_profile.html", {"form": form})


@login_required
def toggle_follow(request, username):
    """Section 4/27 -- follow/unfollow another athlete."""
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(AthleteProfile, user=target_user)
    my_profile, _ = AthleteProfile.objects.get_or_create(
        user=request.user, defaults={"display_name": request.user.username}
    )
    if target_profile != my_profile:
        if target_profile.followers.filter(pk=my_profile.pk).exists():
            target_profile.followers.remove(my_profile)
        else:
            target_profile.followers.add(my_profile)
    return redirect("accounts:profile_detail", username=username)


@login_required
def discover_athletes(request):
    """Section 30 -- athlete discovery with basic filters."""
    profiles = AthleteProfile.objects.select_related("user").all()
    rank_filter = request.GET.get("rank")
    if rank_filter:
        profiles = profiles.filter(user__rank_state__current_rank__name__iexact=rank_filter)
    return render(request, "accounts/discover.html", {"profiles": profiles})
