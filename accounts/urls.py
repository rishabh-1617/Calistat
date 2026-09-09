from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.CalisfyLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("edit/", views.edit_profile, name="edit_profile"),
    path("discover/", views.discover_athletes, name="discover"),
    path("u/<str:username>/", views.profile_detail, name="profile_detail"),
    path("u/<str:username>/follow/", views.toggle_follow, name="toggle_follow"),
    path("password-reset/", PasswordResetView.as_view(template_name="accounts/password_reset.html"), name="password_reset"),
    path("password-reset/done/", PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
]
